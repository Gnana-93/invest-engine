"""
engine/strategies.py — the 4 screeners (rules engine, config-driven).

Each screener returns a list of "hits" with per-criterion pass/fail detail,
so the report can explain WHY a stock matched (transparency requirement).
A stock can match multiple strategies; scoring.py handles dedup + ranking.

Threshold sources (industry-tested, documented in README):
  Compounder/GARP: ROCE>=15, D/E<=0.75, growth>=10/12, OPM>=12 (Basant
    Maheshwari / Motilal Oswal / Peter Lynch schools)
  Deep value: PE<=14, PB<=1.8 with earnings-stabilization trigger (Graham-
    inspired, adapted for India where PB<1 screens catch value traps)
  Quality momentum: 200DMA + 3M RS + ROCE + delivery% (anti pump-and-dump)
  Turnaround: margin inflection + promoter skin-in-the-game, debt watched
"""

from __future__ import annotations


def _get(rec, key):
    return rec.get(key)


def screen_all(cfg: dict, records: dict[str, dict]) -> dict[str, list[dict]]:
    """records: symbol -> canonical record (from financials.derive)."""
    hits: dict[str, list[dict]] = {}
    strat_cfg = cfg["strategies"]
    runners = {
        "quality_compounder": _quality_compounder,
        "deep_value": _deep_value,
        "smallcap_quality_momentum": _smallcap_momentum,
        "turnaround": _turnaround,
    }
    for name, fn in runners.items():
        if not strat_cfg.get(name, {}).get("enabled", False):
            continue
        for sym, rec in records.items():
            verdict = fn(strat_cfg[name], rec)
            if verdict:
                hits.setdefault(sym, []).append({"strategy": name, **verdict})
    return hits


def _quality_compounder(c: dict, r: dict) -> dict | None:
    tests = [
        ("roce_est >= min", _ge(r["roce_est"], c["roce_min"])),
        ("debt_equity <= max", _le(r["debt_equity"], c["debt_equity_max"])),
        ("rev_growth >= min", _ge(r["rev_growth"], c["sales_cagr_3y_min"])),
        ("earn_growth >= min", _ge(r["earn_growth"], c["profit_cagr_3y_min"])),
        ("opm >= min", _ge(r["opm"], c["opm_min"])),
        ("fcf positive", (r["fcf_cr"] or 0) > 0 if r["fcf_cr"] is not None else None),
    ]
    return _verdict("quality_compounder", tests, r,
                    bonus=_dividend_bonus(r) if c.get("dividend_ok") else 0)


def _deep_value(c: dict, r: dict) -> dict | None:
    stable = (r["earn_growth"] is not None and r["earn_growth"] >= 0) \
        if c.get("require") == "earnings_stabilizing" else True
    tests = [
        ("pe <= max", _le(r["pe"], c["pe_max"])),
        ("pb <= max", _le(r["pb"], c["pb_max"])),
        ("debt_equity <= max", _le(r["debt_equity"], c["debt_equity_max"])),
        ("earnings stabilizing", stable),
    ]
    return _verdict("deep_value", tests, r)


def _smallcap_momentum(c: dict, r: dict) -> dict | None:
    mcap_ok = r["market_cap_cr"] is not None and r["market_cap_cr"] <= c["market_cap_max_cr"]
    tests = [
        ("above 200DMA", r["above_200dma"] is True if c.get("price_above_200dma") else None),
        ("3M RS vs Nifty >= min", _ge(r["ret_3m"], c["rs_vs_nifty_3m_min"])),
        ("roce_est >= min", _ge(r["roce_est"], c["roce_min"])),
        ("market cap <= max", mcap_ok),
    ]
    return _verdict("smallcap_quality_momentum", tests, r)


def _turnaround(c: dict, r: dict) -> dict | None:
    # Margin inflection proxy with point-in-time data: positive OPM that is
    # below the sector norm + earnings turned positive. Full 2-quarter math
    # arrives with the Screener.in quarterly upgrade (README).
    improving = (r["opm"] or 0) > 0 and (r["earn_growth"] or -999) > 0
    tests = [
        ("margins improving", improving),
        ("not loss-making", (r["profit_margin"] or -999) > 0),
    ]
    verdict = _verdict("turnaround", tests, r)
    if verdict:
        verdict["risk_flag"] = "debt_watch: verify D/E and pledge before acting"
    return verdict


# ---------------------------------------------------------------- helpers ---
def _verdict(name, tests, r, bonus: int = 0) -> dict | None:
    passed = [t[0] for t in tests if t[1] is True]
    failed = [t[0] for t in tests if t[1] is False]
    unknown = [t[0] for t in tests if t[1] is None]
    # A strategy hit requires all known tests to pass, and <=1 unknown
    # (data gaps must not silently block good stocks with fresh other data).
    if failed:
        return None
    if len(unknown) > 1:
        return None
    if not passed:
        return None
    return {
        "criteria_passed": passed,
        "criteria_unknown": unknown,
        "bonus": bonus,
        "data_quality": r.get("data_quality", 0),
    }


def _dividend_bonus(r) -> int:
    y = r.get("div_yield")
    if y is None:
        return 0
    return 2 if y >= 2.0 else 1 if y >= 1.0 else 0


def _ge(v, floor) -> bool | None:
    return None if v is None else v >= floor


def _le(v, ceil) -> bool | None:
    return None if v is None else v <= ceil
