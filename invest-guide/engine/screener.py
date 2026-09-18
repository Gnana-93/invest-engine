"""
engine/screener.py — cross-check theories against REAL historical fundamentals.

User instruction: "if you have theories, why don't you try using screener for
old stock details or similar websites instead of only papers."

Screener.in exposes 10-year ANNUAL tables (Sales, Net Profit, OPM, ROCE...)
and ~5 years of QUARTERLY results per company. That gives us two honest
cross-checks the papers alone cannot provide:

  1. QUALITY-SCREEN VALIDATION (are OUR filters predictive in India?)
     For each company-year reconstruct the quality screen's fundamental legs
     from history (ROCE, 3y sales CAGR, 3y profit CAGR, OPM) and measure the
     forward ~1-year price return from the engine's cached Yahoo prices.
     Compare passing years vs the base (all years). If the screen's edge is
     real, passing years must beat the base — measured, not assumed.
     Scope honesty: PE/PB/debt legs are NOT point-in-time reconstructable
     from screener pages, so this validates the quality core, not the whole
     composite strategy.

  2. PEAD PROXY (does the earnings-surprise drift exist in OUR universe?)
     Quarterly Net Profit YoY >= +20% = up-surprise, <= -20% = down-surprise.
     Measure forward 63-day (one quarter, matching Bernard & Thomas' ~60d
     drift window) price move. PEAD says BOTH directions drift onward.
     Event date is approximated as quarter-end + 45 days (Indian listing
     deadline); the report states this approximation.

Stdlib only. Politeness: per-run request budget + sleep + 30d page cache.
All numbers in the output are MEASURED on real data, never quoted.
"""

from __future__ import annotations

import json
import re
import time
from datetime import datetime, timedelta
from html.parser import HTMLParser
from pathlib import Path

from . import data

ROOT = Path(__file__).resolve().parent.parent
CURSOR_FILE = ROOT / "data" / "screener_cursor.json"
ACCUM_FILE = ROOT / "data" / "screener_accum.json"   # accumulated eval rows (committed)

_MONTHS = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun",
     "jul", "aug", "sep", "oct", "nov", "dec"])}


# ------------------------------------------------------------ HTML parsing --
class _Tables(HTMLParser):
    """Capture every <table> as {headers[], rows[{label, values[]}], attrs}."""

    def __init__(self):
        super().__init__()
        self.tables: list[dict] = []
        self._t = None       # current table
        self._row = None
        self._cell = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "table":
            self._t = {"attrs": a, "headers": [], "rows": []}
        elif self._t is not None and tag == "tr":
            self._row = []
        elif self._row is not None and tag in ("td", "th"):
            self._cell = []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._cell is not None:
            txt = " ".join("".join(self._cell).split())
            self._row.append(txt)
            self._cell = None
        elif tag == "tr" and self._row is not None:
            if any(c.strip() for c in self._row):
                self._t["rows"].append(self._row)
            self._row = None
        elif tag == "table" and self._t is not None:
            self.tables.append(self._t)
            self._t = None

    def handle_data(self, d):
        if self._cell is not None:
            self._cell.append(d)


def _num(s: str) -> float | None:
    """'-1,234.5' -> -1234.5; '' / '-' / '--' -> None; keeps % off."""
    s = (s or "").strip().replace("%", "")
    if s in ("", "-", "--", "—"):
        return None
    try:
        return float(s.replace(",", ""))
    except ValueError:
        return None


def _period_key(s: str):
    """'Mar 2024' -> (2024, 3); None if not a period header."""
    m = re.match(r"^([A-Za-z]{3})\s*(\d{4})$", (s or "").strip())
    if not m or m.group(1).lower() not in _MONTHS:
        return None
    return (int(m.group(2)), _MONTHS[m.group(1).lower()])


def _find_table(tables: list[dict], must_contain: list[str]) -> dict | None:
    for t in tables:
        labels = [r[0].strip().lower() for r in t["rows"] if r]
        if all(any(m in lab for lab in labels) for m in must_contain):
            return t
    return None


def _table_period_keys(t: dict) -> list:
    """Extract all period keys from a table (headers or first data row)."""
    headers = t.get("headers") or []
    if not any(_period_key(h) for h in headers):
        for r in t["rows"]:
            if r and len(r) > 1 and all(_period_key(c) for c in r[1:]):
                return [k for k in (_period_key(c) for c in r[1:]) if k]
        return []
    return [k for k in (_period_key(h) for h in headers) if k]


def _find_period_table(tables: list[dict], label_match: str, annual: bool) -> dict | None:
    """Screener pages hold BOTH quarterly and annual tables with the same row
    labels. Annual tables use all-March periods (Indian FY ends March); the
    quarterly table mixes months. Discriminate by month pattern."""
    fallback = None
    for t in tables:
        labels = [r[0].strip().lower() for r in t["rows"] if r]
        if not any(label_match in lab for lab in labels):
            continue
        keys = _table_period_keys(t)
        if not keys:
            continue
        all_march = all(m == 3 for (_y, m) in keys)
        if annual and all_march:
            return t
        if not annual and not all_march:
            return t
        fallback = fallback or t
    return fallback


def _series_from_table(t: dict, label_match: str) -> tuple[list, list[float]]:
    """Return (sorted period keys, values) for the first row matching label."""
    if not t:
        return [], []
    headers = t.get("headers") or []
    # screener puts periods in the first data row when headers are empty —
    # promote it PERSISTENTLY (t["headers"] = r) so repeated calls on the same
    # table (sales, then net profit, ...) keep working.
    if not any(_period_key(h) for h in headers):
        for r in t["rows"]:
            if r and len(r) > 1 and all(_period_key(c) for c in r[1:]):
                headers = r
                t["headers"] = r
                break
    cols = [(i, _period_key(h)) for i, h in enumerate(headers)]
    cols = [(i, k) for i, k in cols if k]
    if not cols:
        return [], []
    cols.sort(key=lambda x: x[1])                      # oldest -> newest
    for r in t["rows"]:
        if r and r[0].strip() and label_match in r[0].strip().lower():
            vals = []
            for ci, _k in cols:               # ci = original column index
                v = _num(r[ci].strip()) if ci < len(r) else None
                vals.append(v)
            return [k for _ci, k in cols], vals
    return [], []


# ------------------------------------------------------------ fetch ---------
def fetch_company(symbol: str, cfg: dict) -> dict | None:
    """Fetch + parse one screener company page (cached screener.cache_days)."""
    key = f"screener_{symbol}"
    hit = data.cache_read(key, float(cfg["screener"].get("cache_days", 30)))
    if hit:
        return hit
    sym_q = symbol.replace("&", "%26")
    html_text = None
    for path in (f"/company/{sym_q}/consolidated/", f"/company/{sym_q}/"):
        raw = data.http_get(f"https://www.screener.in{path}", timeout=15)
        text = raw.decode("utf-8", "ignore") if raw else ""
        if "Quarterly" in text:          # validity marker on screener company pages
            html_text = text
            break
    if not html_text:
        return None
    p = _Tables()
    try:
        p.feed(html_text)
    except Exception:
        return None
    if not p.tables:
        return None
    tr = _TopRatios()
    try:
        tr.feed(html_text)
    except Exception:
        pass
    out = {"symbol": symbol, "tables": p.tables, "ratios": tr.ratios,
           "fetched_at": datetime.utcnow().isoformat()}
    data.cache_write(key, out)
    return out


# ---------------------------------------------- fundamentals from screener --
class _TopRatios(HTMLParser):
    """Parse the 'top ratios' widget on company pages (li > name span + value
    span): Market Cap, Current Price, Stock P/E, Book Value, Dividend Yield,
    ROCE, ROE, Debt to equity. Not a <table>, so it needs its own parser."""

    def __init__(self):
        super().__init__()
        self.ratios: dict[str, str] = {}
        self._in_ul = self._in_li = 0
        self._span: list[str] | None = None
        self._li_texts: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "ul" and "top-ratios" in (a.get("id", "") + " " + a.get("class", "")):
            self._in_ul += 1
        elif self._in_ul and tag == "li":
            self._in_li += 1
            self._li_texts = []
        elif self._in_li and tag in ("span", "b", "a"):
            self._span = []

    def handle_endtag(self, tag):
        if tag in ("span", "b", "a") and self._span is not None:
            txt = " ".join("".join(self._span).split())
            if txt and txt not in self._li_texts:
                self._li_texts.append(txt)
            self._span = None
        elif tag == "li" and self._in_li:
            if self._li_texts:
                name = self._li_texts[0].strip().lower()
                nums = [t for t in self._li_texts[1:] if any(c.isdigit() for c in t)]
                val = (nums[-1].strip() if nums
                       else self._li_texts[-1].strip() if len(self._li_texts) > 1 else "")
                if name and val:
                    self.ratios[name] = val
            self._in_li -= 1
        elif tag == "ul" and self._in_ul:
            self._in_ul -= 1

    def handle_data(self, d):
        if self._span is not None:
            self._span.append(d)


def _ratio_val(ratios: dict, name: str) -> float | None:
    v = str(ratios.get(name, "")).replace("₹", "").replace("Cr.", "").strip()
    return _num(v)


def fetch_fundamentals_from_company(co: dict) -> dict | None:
    """Build a fin dict (same shape as data.fetch_fundamentals) from a parsed
    screener company page: top-ratios widget + annual tables. Values arrive
    ALREADY IN PERCENT (screener convention). Pure function of `co` —
    offline-testable; never raises."""
    try:
        if not co or not co.get("tables"):
            return None
        r = co.get("ratios") or {}
        price = _ratio_val(r, "current price")
        pe = _ratio_val(r, "stock p/e")
        bv = _ratio_val(r, "book value")
        roce = _ratio_val(r, "roce")
        roe = _ratio_val(r, "roe")
        dy = _ratio_val(r, "dividend yield")
        de = _ratio_val(r, "debt to equity")
        mcap = _ratio_val(r, "market cap")

        at = _find_period_table(co["tables"], "sales", annual=True)
        _ky, sales = _series_from_table(at, "sales") if at else ([], [])
        _kp, profit = _series_from_table(at, "net profit") if at else ([], [])
        _ko, opm = _series_from_table(at, "opm") if at else ([], [])
        _kd, payout = _series_from_table(at, "dividend payout") if at else ([], [])

        def cagr(series, n=3):
            if len(series) > n and series[-1] and series[-1 - n]:
                try:
                    return round(((series[-1] / series[-1 - n]) ** (1 / n) - 1) * 100, 1)
                except (ZeroDivisionError, TypeError):
                    return None
            return None

        rev_g = cagr(sales)
        earn_g = cagr(profit)
        # deep_value "earnings stabilizing": a LAST-YEAR collapse must not
        # hide behind a good 3y average — surface the negative YoY.
        if (len(profit) > 1 and profit[-1] is not None
                and profit[-2] not in (None, 0)):
            latest_yoy = (profit[-1] / profit[-2] - 1) * 100
            if latest_yoy < 0:
                earn_g = round(latest_yoy, 1)
        pm = (profit[-1] / sales[-1] * 100
              if (sales and profit and sales[-1] and profit[-1] is not None) else None)

        # D/E fallback from balance sheet: Borrowings / (Equity + Reserves)
        if de is None:
            bt = _find_table(co["tables"], ["borrowings"])
            if bt:
                eq = bor = None
                for row in bt["rows"]:
                    lab = row[0].strip().lower()
                    if lab.startswith("equity capital"):
                        eq = _num(row[-1])
                    elif lab.startswith("reserves"):
                        eq = (eq or 0) + (_num(row[-1]) or 0)
                    elif lab.startswith("borrowings"):
                        bor = _num(row[-1])
                if bor is not None and eq:
                    de = round(bor / eq, 2)

        # FCF proxy: latest year "Cash from Operating Activity"
        fcf = None
        ct = _find_table(co["tables"], ["cash from operating activity"])
        if ct:
            for row in ct["rows"]:
                if row and "cash from operating activity" in row[0].strip().lower():
                    fcf = _num(row[-1])
                    break

        if all(v is None for v in (pe, roce, mcap, rev_g)):
            return None
        return {
            "symbol": co.get("symbol"),
            "name": co.get("name") or co.get("symbol"),
            "source": "screener_in",
            "market_cap_cr": mcap, "pe": pe,
            "pb": round(price / bv, 2) if (price and bv) else None,
            "roce": roce, "roe": roe,
            "opm": opm[-1] if opm else None,
            "profit_margin": round(pm, 1) if pm is not None else None,
            "debt_equity": de,
            "revenue_growth": rev_g, "earnings_growth": earn_g,
            "div_yield": dy, "payout_ratio": payout[-1] if payout else None,
            "fcf_cr": fcf, "book_value_ps": bv,
            "fetched_at": co.get("fetched_at"),
        }
    except Exception:
        return None


def fetch_fundamentals(symbol: str, cfg: dict) -> dict | None:
    """Screener.in fundamentals (top-ratios widget + annual tables),
    page-cached like all screener fetches."""
    co = fetch_company(symbol, cfg)
    return fetch_fundamentals_from_company(co) if co else None


# ------------------------------------------------------------ PEAD proxy ----
def pead_proxy_events(cfg: dict, tables: list[dict]) -> list[dict]:
    """Up/down earnings surprises from quarterly Net Profit YoY."""
    qt = _find_period_table(tables, "net profit", annual=False)
    if not qt:
        return []
    _keys, profits = _series_from_table(qt, "net profit")
    up_cut = float(cfg["screener"].get("surprise_yoy_pct", 20.0))
    down_cut = -up_cut
    evs = []
    for i in range(4, len(profits)):
        q, y = profits[i], profits[i - 4]
        if not q or not y or y <= 0:                 # YoY undefined on losses
            continue
        yoy = (q / y - 1) * 100
        if yoy >= up_cut:
            evs.append({"yoy": round(yoy, 1), "direction": "up", "pi": i})
        elif yoy <= down_cut:
            evs.append({"yoy": round(yoy, 1), "direction": "down", "pi": i})
    return evs


def _nearest_price_idx(dates: list[str], want: datetime) -> int | None:
    """Index of the first price date >= want (announcement approx)."""
    ws = want.strftime("%Y-%m-%d")
    for i, d in enumerate(dates):
        if d >= ws:
            return i
    return None


# ------------------------------------------------------------ quality -------
def quality_years(cfg: dict, tables: list[dict]) -> list[dict]:
    """Reconstruct per-year quality screen legs from the ANNUAL table."""
    at = _find_period_table(tables, "sales", annual=True)
    if not at:
        return []
    rt = _find_period_table(tables, "roce", annual=True) or _find_table(tables, ["roce"])
    years_k, sales = _series_from_table(at, "sales")
    _yk2, profit = _series_from_table(at, "net profit")
    _yk3, opm = _series_from_table(at, "opm")
    roce = _series_from_table(rt, "roce")[1] if rt else []
    scfg = cfg["strategies"]["quality_compounder"]
    out = []
    for i in range(3, len(years_k)):
        s3, s0 = sales[i], sales[i - 3]
        p3, p0 = profit[i] if i < len(profit) else None, \
            profit[i - 3] if i - 3 < len(profit) else None
        if not s3 or not s0 or s0 <= 0:
            continue
        sales_cagr = ((s3 / s0) ** (1 / 3) - 1) * 100
        prof_cagr = (((p3 / p0) ** (1 / 3) - 1) * 100
                     if p3 and p0 and p0 > 0 else None)
        yr, mon = years_k[i]
        rec = {
            "year": f"{yr}-{mon:02d}",
            "sales_cagr_3y": round(sales_cagr, 1),
            "profit_cagr_3y": round(prof_cagr, 1) if prof_cagr is not None else None,
            "opm": _num(opm[i]) if i < len(opm) else None,
            "roce": roce[i] if i < len(roce) else None,
        }
        rec["passes"] = bool(
            (rec["roce"] is not None and rec["roce"] >= scfg["roce_min"])
            and rec["sales_cagr_3y"] >= scfg["sales_cagr_3y_min"]
            and (rec["profit_cagr_3y"] is not None
                 and rec["profit_cagr_3y"] >= scfg["profit_cagr_3y_min"])
            and (rec["opm"] is not None and rec["opm"] >= scfg["opm_min"]))
        out.append(rec)
    return out


# ------------------------------------------------------------ main run ------
def _load_cursor() -> int:
    try:
        return int(json.loads(CURSOR_FILE.read_text())["next"])
    except Exception:
        return 0


def _save_cursor(i: int) -> None:
    CURSOR_FILE.parent.mkdir(parents=True, exist_ok=True)
    CURSOR_FILE.write_text(json.dumps({"next": i}))


def _fwd_stats(cfg, rows: list[dict], fwd_key: str, thr: float) -> dict | None:
    vals = [r[fwd_key] for r in rows if r.get(fwd_key) is not None]
    n = len(vals)
    if not n:
        return None
    hits = sum(1 for v in vals if v >= thr)
    vals_sorted = sorted(vals)
    half = vals_sorted[len(vals_sorted) // 2:]
    consistency = (sum(1 for v in half if v >= thr) / len(half)) if half else None
    return {"n": n, "avg_fwd_pct": round(sum(vals) / n, 2),
            "positive_rate": round(sum(1 for v in vals if v > 0) / n, 3),
            f"hit_rate(>={thr}%)": round(hits / n, 3),
            "consistency": round(consistency, 3) if consistency is not None else None}


def run_screener_backtest(cfg: dict, universe: list[dict] | None = None) -> dict:
    scfg = cfg["screener"]
    lb = cfg["universe"].get("prices_lookback_days", 400)
    if universe is None:
        from .universe import build_universe
        universe = build_universe(cfg)
    symbols = [r["symbol"] for r in universe
               if r.get("symbol") and not r["symbol"].startswith("^")]

    # rotate through the universe within the per-run budget
    start = _load_cursor() % max(1, len(symbols))
    order = symbols[start:] + symbols[:start]
    budget = int(scfg.get("max_requests_per_run", 200))
    sleep_s = float(scfg.get("request_sleep_s", 1.5))

    res_years: list[dict] = []      # {symbol, year, passes, fwd_250d}
    res_pead: list[dict] = []       # {symbol, yoy, direction, fwd_63d}
    fetched = failed = 0
    report = {"generated": datetime.utcnow().isoformat(),
              "fetched": 0, "failed": 0, "quality": {}, "pead": {}}

    for sym in order:
        if fetched >= budget:
            break
        fetched += 1
        co = fetch_company(sym, cfg)
        if not co:
            failed += 1
            time.sleep(sleep_s)
            continue
        px = data.cache_read(f"prices_{sym}_{lb}", 3650.0)
        if px and px.get("dates"):
            dates, closes = px["dates"], px["close"]
            # --- quality years -> fwd 250d price return
            for rec in quality_years(cfg, co["tables"]):
                yr, mon = int(rec["year"][:4]), int(rec["year"][5:7])
                anchor = _nearest_price_idx(dates, datetime(yr, mon, 1) + timedelta(days=40))
                if anchor is not None and anchor + 250 < len(closes) and closes[anchor]:
                    rec["symbol"] = sym
                    rec["fwd_250d"] = round((closes[anchor + 250] / closes[anchor] - 1) * 100, 2)
                    res_years.append(rec)
            # --- PEAD proxy -> fwd 63d price return
            qt = _find_period_table(co["tables"], "net profit", annual=False)
            keys, _vals = _series_from_table(qt, "net profit")
            for ev in pead_proxy_events(cfg, co["tables"]):
                # announcement approximated as quarter-end + 45d (listing deadline)
                if ev["pi"] < len(keys):
                    y, m = keys[ev["pi"]]
                    ev["quarter"] = f"{y}-{m:02d}"
                    anchor = _nearest_price_idx(dates, datetime(y, m, 1) + timedelta(days=45))
                    if anchor is not None and anchor + 63 < len(closes) and closes[anchor]:
                        ev["symbol"] = sym
                        ev["fwd_63d"] = round((closes[anchor + 63] / closes[anchor] - 1) * 100, 2)
                        res_pead.append(ev)
        time.sleep(sleep_s)

    _save_cursor((start + fetched) % max(1, len(symbols)))

    # accumulate eval rows across nights (small JSON, committed like the KB)
    # dedupe: quality by (symbol, year) · pead by (symbol, quarter, direction)
    acc = {"quality_rows": [], "pead_rows": []}
    if ACCUM_FILE.exists():
        try:
            acc = json.loads(ACCUM_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    q_seen = {(r.get("symbol"), r.get("year")) for r in acc["quality_rows"]}
    for r in res_years:
        if (r.get("symbol"), r.get("year")) not in q_seen:
            acc["quality_rows"].append(r)
            q_seen.add((r.get("symbol"), r.get("year")))
    p_seen = {(r.get("symbol"), r.get("quarter"), r.get("direction")) for r in acc["pead_rows"]}
    for r in res_pead:
        if (r.get("symbol"), r.get("quarter"), r.get("direction")) not in p_seen:
            acc["pead_rows"].append(r)
            p_seen.add((r.get("symbol"), r.get("quarter"), r.get("direction")))
    ACCUM_FILE.write_text(json.dumps(acc, indent=1), encoding="utf-8")

    # stats are computed over the FULL accumulated sample, not tonight's slice
    thr_q = 10.0     # fwd 1y vs a plain ~10% market drift baseline
    thr_p = 3.0      # one-quarter drift, smaller threshold
    all_years = acc["quality_rows"]
    all_pead = acc["pead_rows"]
    if all_years:
        passing = [r for r in all_years if r["passes"]]
        report["quality"] = {
            "screen": "ROCE>=15 & sales3y>=10% & profit3y>=12% & OPM>=12 (annual, point-in-time)",
            "passing_years": _fwd_stats(cfg, passing, "fwd_250d", thr_q) or {"n": 0},
            "base_all_years": _fwd_stats(cfg, all_years, "fwd_250d", thr_q) or {"n": 0},
        }
    up = [r for r in all_pead if r["direction"] == "up"]
    dn = [r for r in all_pead if r["direction"] == "down"]
    if up or dn:
        report["pead"] = {
            "proxy": "quarterly profit YoY >= +20% (up) / <= -20% (down), fwd 63d, announcement approx = quarter end + 45d",
            "up_surprise": _fwd_stats(cfg, up, "fwd_63d", thr_p) or {"n": 0},
            "down_surprise": _fwd_stats(cfg, dn, "fwd_63d", -thr_p) or {"n": 0},
        }
    report["fetched"], report["failed"] = fetched, failed
    report["accumulated"] = {"quality_rows": len(all_years), "pead_rows": len(all_pead)}
    out = ROOT / "data" / "screener_backtest_report.json"
    out.write_text(json.dumps(report, indent=1), encoding="utf-8")
    return report


def summarize(report: dict) -> list[str]:
    acc = report.get("accumulated") or {}
    lines = [f"Screener cross-check {report['generated'][:10]} · "
             f"fetched {report['fetched']} pages ({report['failed']} failed) · "
             f"accumulated sample: {acc.get('quality_rows', 0)} quality-years, "
             f"{acc.get('pead_rows', 0)} earnings-surprises"]
    q = report.get("quality") or {}
    if q.get("passing_years", {}).get("n"):
        p, b = q["passing_years"], q["base_all_years"]
        edge = round(p["avg_fwd_pct"] - b["avg_fwd_pct"], 2)
        verdict = "screen ADDS edge" if edge > 0 else "screen shows NO edge — review thresholds"
        lines += [f"  QUALITY screen: passing n={p['n']} avg fwd 1y {p['avg_fwd_pct']:+.1f}%"
                  f" · base n={b['n']} avg {b['avg_fwd_pct']:+.1f}% · edge {edge:+.1f}pp → {verdict}"]
    pe = report.get("pead") or {}
    if pe.get("up_surprise", {}).get("n"):
        u, d = pe["up_surprise"], pe["down_surprise"]
        lines += [f"  PEAD proxy: up-surprises n={u['n']} avg fwd 63d {u['avg_fwd_pct']:+.1f}%"
                  f" · down-surprises n={d['n']} avg {d['avg_fwd_pct']:+.1f}%"
                  " (drift in surprise direction = Bernard & Thomas pattern)"]
    if not lines[1:]:
        lines.append("  (no evaluable data yet — runs rotate through the universe nightly)")
    return lines
