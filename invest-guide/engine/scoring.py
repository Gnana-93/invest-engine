"""
engine/scoring.py — composite score + confidence band.

score = quality(0.60) + evidence(0.25) + data_quality(0.10) + liquidity(0.05)
  * quality:   0-100 from fundamentals (growth, margins, balance sheet, value)
  * evidence:  0-100 from learning-loop hit-rates of the signals present
  * data_quality: 0-100 (completeness of tonight's record)
  * liquidity: 0-100 (turnover vs floor; microcaps can still score high
    if turnover is comfortably above the floor)

Confidence bands (config): A>=75, B>=60, C>=45, else D.
The confidence factor shown next to every suggestion comes from here plus
the learning-loop evidence breakdown (learning.explain()).
"""

from __future__ import annotations


def score_record(cfg: dict, rec: dict, strategy_hits: list[dict], evidence: dict) -> dict:
    q = _quality_score(rec, strategy_hits)
    e = evidence.get("evidence_score", 50.0)          # neutral until learned
    d = (rec.get("data_quality") or 0) * 100
    l = _liquidity_score(cfg, rec)
    w = cfg["scoring"]
    total = (
        q * w["quality_weight"]
        + e * w["signal_evidence_weight"]
        + d * w["data_quality_weight"]
        + l * w["liquidity_weight"]
    )
    total = round(max(0.0, min(100.0, total)), 1)
    return {
        "symbol": rec["symbol"],
        "score": total,
        "parts": {"quality": round(q, 1), "evidence": round(e, 1),
                  "data_quality": round(d, 1), "liquidity": round(l, 1)},
        "band": _band(cfg, total),
        "strategies": [h["strategy"] for h in strategy_hits],
        "hits": strategy_hits,
    }


def _quality_score(rec: dict, hits: list[dict]) -> float:
    """0-100. Fundamentals-first; strategy breadth adds a little."""
    pts = 0.0
    # Growth (0-25)
    rg, eg = rec.get("rev_growth"), rec.get("earn_growth")
    if rg is not None:
        pts += min(12.5, max(0, rg) / 20 * 12.5)
    if eg is not None:
        pts += min(12.5, max(0, eg) / 20 * 12.5)
    # Margins (0-20)
    opm = rec.get("opm")
    if opm is not None:
        pts += min(20, opm / 25 * 20)
    # Balance sheet (0-20)
    de = rec.get("debt_equity")
    if de is not None:
        pts += 20 if de <= 0.3 else 15 if de <= 0.75 else 8 if de <= 1.25 else 0
    # Valuation sanity (0-15): neither cheap junk nor crazy bubble
    pe, pb = rec.get("pe"), rec.get("pb")
    if pe is not None:
        pts += 10 if pe <= 20 else 6 if pe <= 35 else 0
    if pb is not None:
        pts += 5 if pb <= 4 else 2 if pb <= 8 else 0
    # Returns on capital (0-10)
    roce = rec.get("roce_est")
    if roce is not None:
        pts += min(10, roce / 25 * 10)
    # Strategy breadth (0-10): matched by multiple independent screens
    pts += min(10, 4 * len({h["strategy"] for h in hits}) + 2 * sum(h.get("bonus", 0) for h in hits) / 2)
    return min(100.0, pts)


def _liquidity_score(cfg: dict, rec: dict) -> float:
    to = rec.get("turnover_lacs")
    floor = cfg["universe"]["min_turnover_lacs"]
    if to is None:
        return 30.0                      # unknown liquidity = cautious
    if to < floor:
        return max(0.0, 40 * to / floor)  # below floor → heavily penalised
    return min(100.0, 60 + 40 * min(1.0, (to - floor) / (500 - floor + 1)))


def _band(cfg: dict, score: float) -> str:
    b = cfg["scoring"]["confidence_bands"]
    if score >= b["A"]:
        return "A"
    if score >= b["B"]:
        return "B"
    if score >= b["C"]:
        return "C"
    return "D"


def bucket_suggestions(cfg: dict, scored: list[dict]) -> dict[str, list[dict]]:
    """Split into BUY (>= min_suggest_score), WATCH, REJECT with reasons."""
    lo = cfg["scoring"]["min_suggest_score"]
    wl = cfg["scoring"]["watch_score"]
    buy, watch, reject = [], [], []
    for s in scored:
        if s["score"] >= lo:
            buy.append(s)
        elif s["score"] >= wl:
            watch.append(s)
        else:
            reject.append(s)
    for lst in (buy, watch, reject):
        lst.sort(key=lambda x: -x["score"])
    return {"buy": buy, "watch": watch, "reject": reject}
