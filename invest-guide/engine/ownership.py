"""
engine/ownership.py — ownership & smart-money flows (v2.0).

Two channels, both free:

1. QUARTERLY SHAREHOLDING (promoter / FII / DII / Government / public)
   Screener.in already shows the shareholding table on the company pages we
   fetch every night (engine/screener.py). Zero new requests: we parse the
   already-cached tables. The table has two blocks — "No. of Shares" (huge
   numbers) and "%" (percent-like). Rows repeat between blocks, so we take
   the LAST occurrence of each owner label and sanity-check which block
   we got (pct-like iff all values <= 100.5). Output:
     {promoters: {latest, prev, delta_pp}, fiis: {...}, diis: {...}, ...}
   delta_pp = percentage-point change latest vs previous quarter
   (in shares-mode we report relative % change instead and say so).

2. BULK & BLOCK DEALS (NSE archives CSV, same-day)
   Who transacted big (>₹5-10cr equivalent) and on which side. NSE often
   403s non-browser traffic — every failure degrades gracefully to "deals
   unavailable tonight" and the data-quality note flags it. Never
   nightly-critical.

Interpretation lines ("why it matters") are generated for the report so the
user sees not just numbers but the plain-language read.
"""

from __future__ import annotations

import csv
import io
import re

from . import data
from .screener import _find_period_table, _period_key, _table_period_keys

BULK_CSV = "https://archives.nseindia.com/content/equities/bulk.csv"
BLOCK_CSV = "https://archives.nseindia.com/content/equities/block_deals.csv"

_OWNER_LABELS = {"promoters": "promoters", "fiis": "fiis", "diis": "diis",
                 "government": "government", "public": "public",
                 "shareholders": "shareholders"}


# ------------------------------------------------- shareholding (screener) --
def ownership_from_screener(co: dict | None) -> dict | None:
    """Parse the shareholding table from an already-fetched screener company
    dict (engine/screener.fetch_company output). Returns None if absent."""
    if not co:
        return None
    # NOTE: _find_period_table needs annual=True/False and keys off period
    # headers; the shareholding table usually has NEITHER (quarters sit in the
    # first data row and "promoters" appears twice as row labels). So we scan
    # tables ourselves instead of trusting the generic helper.
    t = None
    for cand in co.get("tables") or []:
        labels = {(r[0] or "").strip().lower() for r in cand.get("rows", []) if r}
        if labels & {"promoters", "fiis", "diis"} and len(_table_period_keys(cand)) >= 2:
            t = cand
            break
    if not t:
        # some pages bury the table under a generic header — scan all tables
        for cand in co.get("tables") or []:
            labels = {(r[0] or "").strip().lower() for r in cand.get("rows", []) if r}
            if labels & {"promoters", "fiis", "diis"} and len(cand.get("headers") or []) >= 4:
                t = cand
                break
    if not t:
        return None

    headers = t.get("headers") or []
    periods = [_period_key(h) for h in headers]
    if not any(periods):
        # screener style: periods live in the first data row (headers empty)
        for r in t.get("rows", []):
            if r and len(r) > 2 and all(_period_key(c) for c in r[1:4]):
                periods = [None] + [_period_key(c) for c in r[1:]]
                break

    out: dict[str, dict] = {}
    seen_counts: dict[str, int] = {}
    for r in t.get("rows", []):
        if not r or not r[0]:
            continue
        label = r[0].strip().lower()
        owner = _OWNER_LABELS.get(label.split(" (")[0].strip())
        if not owner:
            continue
        vals = []
        for i, v in enumerate(r[1:], 1):
            try:
                vals.append(float(v))
            except (TypeError, ValueError):
                vals.append(None)
        seen_counts[owner] = seen_counts.get(owner, 0) + 1
        out[owner] = {"vals": vals, "occurrence": seen_counts[owner],
                      "periods": [p for p in periods[1:len(vals) + 1] if p]}

    cleaned = {}
    for owner, d in out.items():
        vals = [v for v in d["vals"]]
        pct_like = bool(vals) and all(v is None or v <= 100.5 for v in vals)
        if not pct_like and d["occurrence"] > 1:
            # previous occurrence was the % block — but we kept the last one;
            # keep shares-mode and mark it
            mode = "shares"
        else:
            mode = "pct" if pct_like else "shares"
        # compress to (period, value) pairs, newest last
        series = []
        ps = d["periods"]
        for i, v in enumerate(vals):
            p = ps[i] if i < len(ps) else None
            if v is not None:
                series.append({"period": p, "value": v})
        if len(series) < 2:
            continue
        newest, prev = series[-1], series[-2]
        if mode == "pct":
            delta = round(newest["value"] - prev["value"], 2)
        else:
            delta = (round((newest["value"] / prev["value"] - 1) * 100, 1)
                     if prev["value"] else None)
        cleaned[owner] = {"latest": newest["value"], "prev": prev["value"],
                          "latest_period": newest["period"], "prev_period": prev["period"],
                          "delta": delta, "mode": mode, "history": series[-6:]}

    return {"owners": cleaned, "source": "screener_in_shareholding",
            "symbol": co.get("symbol")} if cleaned else None


def _period_label(p) -> str:
    """(2026, 9) -> 'Sep 2026'; None-safe for display in alerts."""
    if isinstance(p, tuple) and len(p) == 2:
        months = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        return f"{months[p[1]]} {p[0]}"
    return str(p) if p else "?"


def ownership_alerts(own: dict | None) -> list[str]:
    """Plain-language flags on meaningful shifts. Thresholds deliberately
    conservative — noise here would train the user to ignore the section."""
    if not own:
        return []
    alerts = []
    for owner, d in own["owners"].items():
        delta, mode = d.get("delta"), d.get("mode")
        if delta is None:
            continue
        if owner == "promoters":
            if mode == "pct" and delta <= -1.0:
                alerts.append(f"Promoter holding DOWN {abs(delta):.1f} pp "
                              f"({_period_label(d['prev_period'])}→{_period_label(d['latest_period'])}) — find out why before buying")
            elif mode == "pct" and delta >= 1.0:
                alerts.append(f"Promoter holding UP {delta:.1f} pp — skin in the game increasing")
            elif mode == "shares" and delta <= -1.0:
                alerts.append(f"Promoter shares reduced {abs(delta):.1f}% QoQ")
        elif owner in ("fiis", "diis") and mode == "pct" and abs(delta) >= 1.5:
            who = "FII" if owner == "fiis" else "DII"
            direction = "UP" if delta > 0 else "DOWN"
            alerts.append(f"{who} holding {direction} {abs(delta):.1f} pp — institutional conviction shifting")
    return alerts


def ownership_lines(own: dict | None) -> list[str]:
    """One line per tracked owner for report display."""
    if not own:
        return []
    lines = []
    for owner, d in own["owners"].items():
        if owner == "shareholders":
            continue
        val = d.get("latest")
        delta, mode = d.get("delta"), d.get("mode")
        if val is None:
            continue
        if mode == "pct":
            unit = "%"
            ds = f"{delta:+.1f}pp" if delta is not None else "n/a"
        else:
            unit = ""
            ds = f"{delta:+.1f}%" if delta is not None else "n/a"
        lines.append(f"{owner.title()}: {val}{unit} ({ds} QoQ)")
    return lines


# ------------------------------------------------------- bulk/block deals --
def fetch_deals(symbols: set[str], force: bool = False) -> dict:
    """Today's bulk + block deals filtered to our symbols. Both feeds fail
    soft; the returned dict states availability honestly."""
    out = {"available": False, "deals": [], "note": ""}
    rows: list[dict] = []
    got_any = False
    for kind, url in (("bulk", BULK_CSV), ("block", BLOCK_CSV)):
        key = f"deals_{kind}"
        hit = data.cache_read(key, 0.5) if not force else None
        if hit is not None:
            rows.extend(hit)
            got_any = True
            continue
        raw = data.http_get(url, timeout=20)
        parsed = []
        if raw:
            try:
                text = raw.decode("utf-8", "ignore")
                reader = csv.DictReader(io.StringIO(text))
                for r in reader:
                    low = {(k or "").strip().lower(): (v or "").strip()
                           for k, v in r.items() if k is not None}
                    sym = low.get("symbol") or ""
                    if not sym:
                        continue
                    parsed.append({
                        "symbol": sym.upper(),
                        "client": low.get("client name") or low.get("name of the company/bank") or "",
                        "type": low.get("deal type") or low.get("buy/sell") or kind,
                        "qty": _f(low.get("quantity") or low.get("no. of shares")),
                        "price": _f(low.get("price")),
                        "kind": kind,
                    })
            except Exception:
                parsed = []
        if parsed:
            data.cache_write(key, parsed)
            rows.extend(parsed)
            got_any = True
        else:
            data.cache_write(key, [])  # negative cache so we don't hammer NSE

    if not got_any:
        out["note"] = "NSE deals feed unreachable tonight (not counted against any stock)"
        return out
    out["available"] = True
    symset = {s.upper() for s in symbols}
    out["deals"] = [d for d in rows if d["symbol"] in symset]
    return out


def deal_lines(deals: dict) -> list[str]:
    if not deals.get("available"):
        return [deals.get("note", "")] if deals.get("note") else []
    if not deals["deals"]:
        return []
    lines = []
    for d in deals["deals"][:6]:
        val_cr = (d["qty"] or 0) * (d["price"] or 0) / 1e7
        side = (d["type"] or "?").upper()[:4]
        lines.append(f"{d['symbol']}: {side} {d['qty'] or '?'}sh @ ₹{d['price'] or '?'} "
                     f"(≈₹{val_cr:.1f}cr) — {d['client'][:40]}")
    return lines


def _f(v):
    if v in (None, ""):
        return None
    try:
        return float(re.sub(r"[^0-9.\-]", "", str(v)))
    except ValueError:
        return None


# ---------------------------------------------------------------- summary --
def analyze(co: dict | None, deals: dict | None, symbol: str) -> dict | None:
    """Bundle for one symbol: shareholding read + today's deals in it."""
    own = ownership_from_screener(co)
    sym_deals = []
    if deals and deals.get("available"):
        sym_deals = [d for d in deals["deals"] if d["symbol"] == symbol.upper()]
    if not own and not sym_deals:
        return None
    return {
        "symbol": symbol,
        "shareholding": own,
        "alerts": ownership_alerts(own),
        "lines": ownership_lines(own),
        "deals_today": sym_deals,
        "source": "screener_in+nse_deals",
    }
