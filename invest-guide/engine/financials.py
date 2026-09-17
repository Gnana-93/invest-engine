"""
engine/financials.py — derive comparable metrics from Yahoo fundamentals.

Yahoo gives us point-in-time ratios; the rules engine needs canonical forms.
Where Yahoo lacks multi-year data (smallcaps), we degrade honestly:
data_quality drops, and CAGR-based screens use whatever growth fields exist.
This keeps the engine usable on the whole Nifty 500 + microcap tail instead
of silently excluding half the universe.
"""

from __future__ import annotations

def derive(fin: dict | None, px: dict | None) -> dict:
    """
    Merge fundamentals + price metrics into one canonical record.
    Never raises; missing fields become None and reduce data_quality.
    """
    out = {
        "symbol": (fin or px or {}).get("symbol", "UNKNOWN"),
        "name": None, "industry": None,
        "market_cap_cr": None, "price": None,
        "pe": None, "pb": None, "roe": None, "roce_est": None,
        "opm": None, "profit_margin": None,
        "debt_equity": None, "current_ratio": None,
        "fcf_cr": None, "cash_cr": None, "debt_cr": None,
        "rev_growth": None, "earn_growth": None,
        "div_yield": None, "payout": None,
        "ev_ebitda": None, "target_upside": None,
        "above_200dma": None, "ret_3m": None, "ret_1y": None,
        "turnover_lacs": None, "next_earnings": None,
        "data_quality": 0.0, "sources": [],
    }

    if fin:
        f = fin
        out["sources"].append(f.get("source", "fund"))
        out["name"] = f.get("name")
        out["industry"] = f.get("industry")
        out["market_cap_cr"] = f.get("market_cap_cr")
        out["pe"] = _pos(f.get("pe"))
        out["pb"] = _pos(f.get("pb"))
        out["roe"] = _ratio(f.get("roe"))
        out["opm"] = _ratio(f.get("opm"))
        out["profit_margin"] = _ratio(f.get("profit_margin"))
        out["debt_equity"] = _de(f.get("debt_equity"))   # Yahoo: x100, debt-only
        out["current_ratio"] = f.get("current_ratio")
        out["fcf_cr"] = f.get("fcf_cr")
        out["cash_cr"] = f.get("cash_cr")
        out["debt_cr"] = f.get("debt_cr")
        out["rev_growth"] = _ratio(f.get("revenue_growth"))
        out["earn_growth"] = _ratio(f.get("earnings_growth"))
        out["div_yield"] = _ratio(f.get("div_yield"))
        out["payout"] = _ratio(f.get("payout_ratio"))
        out["ev_ebitda"] = _pos(f.get("ev_ebitda"))
        out["next_earnings"] = f.get("next_earnings")
        out["target_mean"] = f.get("target_mean")  # upside computed post-merge

    if px:
        p = px
        out["sources"].append(p.get("source", "px"))
        out["price"] = p.get("last")
        out["above_200dma"] = p.get("above_200dma")
        out["ret_3m"] = p.get("ret_3m")
        out["ret_1y"] = p.get("ret_1y")
        out["turnover_lacs"] = p.get("turnover_lacs")
        if not out["market_cap_cr"]:
            out["market_cap_cr"] = None  # never fake it

    # ---- ROCE estimate: Yahoo gives ROA+ROE; ROE levered is the honest proxy.
    # True ROCE needs EBIT/capital-employed from annual reports (Screener.in
    # scrape is the planned upgrade; see README "Upgrade path").
    if out["roe"] is not None:
        out["roce_est"] = out["roe"]  # labelled "est" — screens treat as proxy

    # analyst target upside needs the LIVE price (from px), not fundamentals
    tp = out.pop("target_mean", None)
    if tp and out.get("price"):
        out["target_upside"] = round((tp / out["price"] - 1) * 100, 1)

    out["data_quality"] = _quality(out)
    return out


def _pos(v):
    if v is None:
        return None
    try:
        v = float(v)
        return v if v > 0 else None
    except (TypeError, ValueError):
        return None


def _ratio(v):
    """Yahoo returns fractions (0.18 = 18%). Normalize to percent."""
    if v is None:
        return None
    try:
        v = float(v)
    except (TypeError, ValueError):
        return None
    if abs(v) <= 1.5:          # fraction form
        return round(v * 100, 1)
    return round(v, 1)          # already percent-ish


def _de(v):
    """Yahoo debtToEquity is debt-only, scaled x100 (35 -> 0.35)."""
    if v is None:
        return None
    try:
        return round(float(v) / 100.0, 2)
    except (TypeError, ValueError):
        return None


def _quality(rec: dict) -> float:
    """0..1 — how complete is this record? Drives scoring.data_quality."""
    checks = [
        rec["price"] is not None,
        rec["pe"] is not None,
        rec["pb"] is not None,
        rec["roe"] is not None,
        rec["opm"] is not None,
        rec["debt_equity"] is not None,
        rec["rev_growth"] is not None,
        rec["market_cap_cr"] is not None,
        rec["turnover_lacs"] is not None,
        rec["above_200dma"] is not None,
    ]
    return round(sum(checks) / len(checks), 2)
