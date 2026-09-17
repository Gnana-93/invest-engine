"""
engine/data.py — fetchers + cache.

Sources (all free, no API keys):
  1. Yahoo Finance chart API   -> daily OHLCV  (~1y history per symbol, .NS)
  2. Yahoo quoteSummary API    -> fundamentals (financialData, key stats)
  3. NSE archives CSV          -> Nifty 500 constituents (universe seed)
  4. RSS feeds (ET/MC/BS)      -> news headlines for cause-tagging

Rules:
  - Every fetch wrapped in try/except; failures degrade gracefully.
  - Disk cache in data/cache/ with per-source TTL (config: fundamentals 21d).
  - Returns dicts with "source" + "fetched_at" so scoring can rate data quality.
stdlib only: urllib + json + time + csv + xml.
"""

from __future__ import annotations

import csv
import io
import json
import os
import re
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / "data" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


# ----------------------------------------------------------------- cache ----
def _cache_path(key: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", key)
    return CACHE_DIR / f"{safe}.json"


def cache_read(key: str, ttl_days: float) -> dict | None:
    """Return cached payload if fresh enough, else None."""
    p = _cache_path(key)
    if not p.exists():
        return None
    try:
        blob = json.loads(p.read_text(encoding="utf-8"))
        age = time.time() - blob.get("fetched_at", 0)
        if age < ttl_days * 86400:
            return blob["payload"]
    except Exception:
        return None
    return None


def cache_write(key: str, payload) -> None:
    p = _cache_path(key)
    try:
        p.write_text(
            json.dumps({"fetched_at": time.time(), "payload": payload}),
            encoding="utf-8",
        )
    except Exception:
        pass


# ----------------------------------------------------------------- http -----
_fail_streak = 0          # consecutive http_get failures (circuit-breaker state)


def http_get(url: str, timeout: int = 15) -> bytes | None:
    """GET with UA + retries. Returns bytes or None (never raises).

    Circuit-breaker: when the network (or one source) is down, the old
    2-attempt x full-timeout pattern cost ~30s+ PER SYMBOL — a 500-stock
    night crawled for hours looking 'stuck'. After 8 consecutive failures
    we drop to a single short attempt (fast-fail) and pause once for a
    cool-down; the run then degrades to caches in minutes instead of hanging."""
    global _fail_streak
    hot = _fail_streak >= 8
    attempts = 1 if hot else 2
    tmo = min(timeout, 10) if hot else timeout
    for attempt in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=tmo) as resp:
                _fail_streak = 0
                return resp.read()
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
            _fail_streak += 1
            if _fail_streak == 8:
                print(f"[data] {8} consecutive fetch failures — network down or "
                      f"rate-limited; switching to fast-fail mode (run degrades to caches)", flush=True)
                time.sleep(15)                       # one-time cool-down, not per call
            elif _fail_streak > 8 and _fail_streak % 25 == 0:
                print(f"[data] still failing x{_fail_streak}", flush=True)
            elif not hot:
                time.sleep(1.2 * (attempt + 1))
    return None


def _get_json(url: str) -> dict | None:
    raw = http_get(url)
    if not raw:
        return None
    try:
        return json.loads(raw.decode("utf-8", errors="replace"))
    except Exception:
        return None


# ----------------------------------------------------------------- prices ---
def fetch_prices(symbol: str, lookback_days: int = 400, force: bool = False,
                 is_index: bool = False) -> dict | None:
    """
    Yahoo chart API. Returns:
    { symbol, dates[], close[], volume[], dma20, dma200, last, prev_close,
      ret_1d, ret_1m, ret_3m, ret_1y, avg_vol20, turnover_lacs, source }
    Indices (e.g. ^NSEI) must pass is_index=True — no .NS suffix is added.
    """
    key = f"prices_{symbol}_{lookback_days}"
    if not force:
        hit = cache_read(key, ttl_days=1.0)
        if hit:
            return hit
    ysym = symbol if is_index else f"{symbol}.NS"
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/"
        f"{urllib.request.quote(ysym)}?range=1y&interval=1d"
    )
    js = _get_json(url)
    out = None
    try:
        res = js["chart"]["result"][0]
        ts = res.get("timestamp", [])
        q = res["indicators"]["quote"][0]
        closes = q.get("close", [])
        vols = q.get("volume", [])
        rows = [
            (datetime.fromtimestamp(t).strftime("%Y-%m-%d"), c, v)
            for t, c, v in zip(ts, closes, vols)
            if c is not None and v is not None
        ]
        if len(rows) < 60:
            raise ValueError("insufficient history")
        dates = [r[0] for r in rows]
        close = [float(r[1]) for r in rows]
        vol = [float(r[2]) for r in rows]
        out = _price_metrics(symbol, dates, close, vol)
    except Exception:
        out = None
    if out:
        cache_write(key, out)
    return out or cache_read(key, ttl_days=3650.0)  # stale fallback better than none


def _price_metrics(symbol: str, dates: list[str], close: list[float], vol: list[float]) -> dict:
    def dma(n):
        return round(sum(close[-n:]) / n, 2) if len(close) >= n else None

    def ret(days):
        if len(close) <= days:
            return None
        base = close[-1 - days]
        return round((close[-1] / base - 1) * 100, 2) if base else None

    avg_vol20 = sum(vol[-20:]) / min(20, len(vol)) or 1.0
    last = close[-1]
    prev = close[-2] if len(close) > 1 else last
    return {
        "symbol": symbol,
        "dates": dates,
        "close": close,
        "volume": vol,
        "last": round(last, 2),
        "prev_close": round(prev, 2),
        "ret_1d": round((last / prev - 1) * 100, 2) if prev else None,
        "ret_5d": ret(5),
        "ret_21d": ret(21),
        "ret_1m": ret(21),
        "ret_3m": ret(63),
        "ret_1y": ret(250),
        # v3 learning signals (international canon; validated by engine/backtest.py):
        # near_52w_high_pct — George & Hwang (JF 2004) hypothesis: stocks near
        #   their 52-week high drift higher. Semantics: 0 = AT the 52w high,
        #   -2 = within 2% of it, -30 = 30% below it. Trigger: >= -within_pct.
        # ret_63_1 — Jegadeesh & Titman (JF 1993) canonical momentum window:
        #   3-month return EXCLUDING the most recent week (avoids short-term
        #   reversal contaminating the momentum signal).
        "near_52w_high_pct": round((last / max(close[-min(250, len(close)):]) - 1) * 100, 2) if close else None,
        "ret_63_1": round((close[-6] / close[-6 - 63] - 1) * 100, 2)
                    if len(close) > 68 and close[-6 - 63] else None,
        "dma20": dma(20),
        "dma200": dma(200),
        "avg_vol20": round(avg_vol20, 0),
        "turnover_lacs": round(last * avg_vol20 / 1e5, 1),
        "above_200dma": bool(last > dma(200)) if dma(200) else None,
        "source": "yahoo_chart",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


# ------------------------------------------------------------ fundamentals --
_SUMMARY_MODULES = ",".join(
    ["financialData", "defaultKeyStatistics", "summaryDetail", "assetProfile", "calendarEvents"]
)


def fetch_fundamentals(symbol: str, force: bool = False) -> dict | None:
    """
    Yahoo quoteSummary (free, no key). Many fields may be missing on smallcaps;
    caller must tolerate None and score data-quality accordingly.
    """
    key = f"fund_{symbol}"
    if not force:
        hit = cache_read(key, ttl_days=21.0)
        if hit:
            return hit
    ysym = f"{symbol}.NS"
    url = (
        f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/"
        f"{urllib.request.quote(ysym)}?modules={_SUMMARY_MODULES}"
    )
    js = _get_json(url)
    out = None
    try:
        r = js["quoteSummary"]["result"][0]
        fd = r.get("financialData", {}) or {}
        ks = r.get("defaultKeyStatistics", {}) or {}
        sd = r.get("summaryDetail", {}) or {}
        ap = r.get("assetProfile", {}) or {}
        cal = r.get("calendarEvents", {}) or {}

        def g(d, *path):
            cur = d
            for p in path:
                cur = (cur or {}).get(p)
            if isinstance(cur, dict):
                cur = cur.get("raw")
            return cur

        out = {
            "symbol": symbol,
            "name": g(r, "assetProfile", "longName") or symbol,
            "industry": g(ap, "industry"),
            "market_cap_cr": round(g(sd, "marketCap") / 1e7, 1) if g(sd, "marketCap") else None,
            "pe": g(sd, "trailingPE") or g(ks, "trailingPegRatio"),
            "pb": g(ks, "priceToBook"),
            "roe": g(fd, "returnOnEquity"),
            "roa": g(fd, "returnOnAssets"),
            "opm": g(fd, "operatingMargins"),
            "profit_margin": g(fd, "profitMargins"),
            "debt_equity": g(fd, "debtToEquity"),
            "current_ratio": g(fd, "currentRatio"),
            "fcf_cr": round(g(fd, "freeCashflow") / 1e7, 1) if g(fd, "freeCashflow") else None,
            "cash_cr": round(g(fd, "totalCash") / 1e7, 1) if g(fd, "totalCash") else None,
            "debt_cr": round(g(fd, "totalDebt") / 1e7, 1) if g(fd, "totalDebt") else None,
            "revenue_growth": g(fd, "revenueGrowth"),
            "earnings_growth": g(fd, "earningsGrowth"),
            "ev_ebitda": g(sd, "enterpriseToEbitda"),
            "div_yield": g(sd, "dividendYield"),
            "payout_ratio": g(sd, "payoutRatio"),
            "recommendation": g(fd, "recommendationKey"),
            "target_mean": g(fd, "targetMeanPrice"),
            "earnings_dates": [
                e for e in (cal.get("earnings", {}) or {}).get("earningsDate", [])
                if isinstance(e, dict)
            ],
            "next_earnings": (
                datetime.fromtimestamp(cal["earnings"]["earningsDate"][0]["raw"]).strftime("%Y-%m-%d")
                if (cal.get("earnings", {}) or {}).get("earningsDate")
                else None
            ),
            "source": "yahoo_summary",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception:
        out = None
    if out:
        cache_write(key, out)
    return out or cache_read(key, ttl_days=3650.0)


# ---------------------------------------------------------------- universe --
NIFTY500_CSV = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"


def fetch_universe_symbols(force: bool = False) -> list[dict]:
    """Nifty 500 constituents (weekly refresh is plenty). Fallback: seed file."""
    key = "universe_nifty500"
    if not force:
        hit = cache_read(key, ttl_days=7.0)
        if hit:
            return hit
    out = []
    raw = http_get(NIFTY500_CSV, timeout=25)
    if raw:
        try:
            reader = csv.DictReader(io.StringIO(raw.decode("utf-8", errors="replace")))
            for row in reader:
                sym = (row.get("Symbol") or "").strip()
                if sym:
                    out.append(
                        {
                            "symbol": sym,
                            "name": (row.get("Company Name") or "").strip(),
                            "industry": (row.get("Industry") or "").strip(),
                        }
                    )
        except Exception:
            out = []
    if not out:
        seed = ROOT / "data" / "universe_seed.json"
        if seed.exists():
            try:
                out = json.loads(seed.read_text(encoding="utf-8"))
            except Exception:
                out = []
    if out:
        cache_write(key, out)
    return out


# ------------------------------------------------------------------- news ---
def fetch_news(rss_sources: list[dict], force: bool = False) -> list[dict]:
    """Parse RSS feeds -> [{title, link, source, pub}] for cause-tagging."""
    key = "news_rss"
    if not force:
        hit = cache_read(key, ttl_days=0.25)
        if hit:
            return hit
    items = []
    for src in rss_sources:
        raw = http_get(src["url"], timeout=12)
        if not raw:
            continue
        try:
            root = ET.fromstring(raw)
            for item in root.iter("item"):
                title = (item.findtext("title") or "").strip()
                link = (item.findtext("link") or "").strip()
                pub = (item.findtext("pubDate") or "").strip()
                if title:
                    items.append({"title": title, "link": link, "source": src["name"], "pub": pub})
        except Exception:
            continue
    if items:
        cache_write(key, items)
    return items or cache_read(key, ttl_days=3650.0) or []


# ------------------------------------------------------------ selftest data -
def synthetic_prices(symbol: str = "TEST", days: int = 260, base: float = 500.0) -> dict:
    """Deterministic fake series for --selftest (no network needed)."""
    import math

    dates, close, vol = [], [], []
    for i in range(days):
        d = datetime(2025, 1, 1).strftime("%Y-%m-%d")
        val = base * (1 + 0.002 * i + 0.02 * math.sin(i / 7))
        dates.append(f"d{i:03d}" or d)
        close.append(round(val, 2))
        vol.append(100000 + 1000 * (i % 13))
    return _price_metrics(symbol, dates, close, vol)


def synthetic_fundamentals(symbol: str = "TEST") -> dict:
    return {
        "symbol": symbol,
        "name": "Test Industries Ltd",
        "industry": "Manufacturing",
        "market_cap_cr": 1200.0,
        "pe": 11.0,
        "pb": 1.2,
        "roe": 0.18,
        "roa": 0.09,
        "opm": 0.15,
        "profit_margin": 0.09,
        "debt_equity": 0.35,
        "current_ratio": 1.8,
        "fcf_cr": 45.0,
        "cash_cr": 60.0,
        "debt_cr": 90.0,
        "revenue_growth": 0.14,
        "earnings_growth": 0.17,
        "ev_ebitda": 8.0,
        "div_yield": 0.012,
        "payout_ratio": 0.22,
        "recommendation": "buy",
        "target_mean": 600.0,
        "next_earnings": None,
        "source": "synthetic",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
