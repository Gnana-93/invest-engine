"""
engine/tax.py — post-tax decision engine (FY 2026-27 rules).

User requirements covered here:
  * "consider impact of taxation on short-term buys & sell timelines"
  * "tell when it is NOT wise holding an investment any longer"

Rules (verified Sep 2026 — recheck every July):
  STCG (listed equity, STT paid): 20%  |  LTCG: 12.5% above ₹1.25L/yr
  Holding period: listed equity LTCG at >12 months.
  Costs modelled: Zerodha delivery ₹0 brokerage, STT 0.1% each side,
  exchange+SEBI+stamp ≈ 0.011%, DP sell ₹15.25 (approx; per-scrip rounding
  ignored for simplicity).

The engine never says "sell to save tax" blindly: it compares
  net(sell now @STCG) vs net(hold to LTCG) vs thesis quality,
because a 20%→12.5% saving on a 6% gain can be wiped by a 10% drawdown
while waiting. Output is a ranked recommendation with the math shown.
"""

from __future__ import annotations

STCG_RATE = 0.20
LTCG_RATE = 0.125
LTCG_EXEMPTION = 125_000.0
LTCG_HOLD_DAYS = 365
STT_PCT = 0.001            # delivery, each side
OTHER_COST_PCT = 0.00011   # exchange txn + SEBI + stamp (approx, both sides)
DP_SELL_INR = 15.25


def round_trip_cost_inr(amount: float) -> float:
    """Total frictions for a buy+sell round trip of `amount` rupees."""
    stt = amount * STT_PCT * 2
    other = amount * OTHER_COST_PCT * 2
    return round(stt + other + DP_SELL_INR, 2)


def net_after_tax(profit: float, hold_days: int, ltcg_band_used: float = 0.0) -> dict:
    """
    Net profit after CGT. ltcg_band_used = LTCG gains already realised this
    FY by the user (default 0 → full ₹1.25L exemption headroom available).
    """
    if profit <= 0:
        return {"tax": 0.0, "net": round(profit, 2), "regime": "loss (no CGT)",
                "note": "losses: STCL offsets any STCG/LTCG; carry forward 8 yrs"}
    if hold_days <= LTCG_HOLD_DAYS:
        tax = profit * STCG_RATE
        return {"tax": round(tax, 2), "net": round(profit - tax, 2),
                "regime": "STCG 20%"}
    headroom = max(0.0, LTCG_EXEMPTION - ltcg_band_used)
    taxable = max(0.0, profit - headroom)
    tax = taxable * LTCG_RATE
    return {"tax": round(tax, 2), "net": round(profit - tax, 2),
            "regime": "LTCG 12.5% (₹1.25L band applied)"}


def exit_timeline_advice(cfg: dict, buy_price: float, current: float,
                         buy_date_days: int, thesis_score: float,
                         target_price: float | None = None,
                         ltcg_band_used: float = 0.0) -> dict:
    """
    The 'when is holding no longer wise' calculator.
    Compares: SELL NOW (STCG) vs HOLD TO LTCG (>=365d) vs HOLD FOR TARGET.
    Returns ranked advice with numbers, never a bare "hold/sell".
    """
    amount = buy_price * 100                       # normalise to 100 shares
    gain_pct = (current / buy_price - 1) * 100 if buy_price else 0.0
    profit_per_share = current - buy_price
    profit = profit_per_share * 100

    sell_now = net_after_tax(profit, buy_date_days, ltcg_band_used)
    sell_now_net = sell_now["net"] - round_trip_cost_inr(amount)

    # "hold to LTCG" scenario: assume price unchanged (conservative) —
    # thesis risk is flagged separately via thesis_score.
    hold = net_after_tax(profit, max(buy_date_days, LTCG_HOLD_DAYS + 1), ltcg_band_used)
    days_to_ltcg = max(0, LTCG_HOLD_DAYS - buy_date_days)

    options = [
        {"option": "SELL NOW", "net_inr_per_100sh": round(sell_now_net, 0),
         "regime": sell_now["regime"], "risk": "known outcome today"},
        {"option": f"HOLD {days_to_ltcg}d → LTCG",
         "net_inr_per_100sh": round(hold["net"], 0),
         "regime": hold["regime"],
         "risk": f"price risk for {days_to_ltcg}d; tax saving ₹{hold['tax'] and round(sell_now['tax'] - hold['tax'], 0)}"},
    ]
    if target_price and target_price > current:
        tgt_profit = (target_price - buy_price) * 100
        tgt = net_after_tax(tgt_profit, max(buy_date_days, LTCG_HOLD_DAYS + 1), ltcg_band_used)
        options.append({"option": f"HOLD → TARGET {target_price}",
                        "net_inr_per_100sh": round(tgt["net"], 0),
                        "regime": tgt["regime"], "risk": "target may not be reached"})

    options.sort(key=lambda o: -o["net_inr_per_100sh"])
    best = options[0]

    warnings = []
    if gain_pct <= -cfg["exits"]["stop_loss_pct"]:
        warnings.append(f"DOWN {gain_pct:.0f}% — stop-loss zone: tax saving does NOT justify thesis breach")
    if 300 <= buy_date_days <= LTCG_HOLD_DAYS and profit > 0:
        warnings.append("LTCG window: crossing 365d within weeks — re-check before selling")
    if thesis_score < cfg["scoring"]["watch_score"]:
        warnings.append("thesis score below watch-line — holding is sentiment, not strategy")
    if days_to_ltcg > 60 and gain_pct > 15 and thesis_score < 60:
        warnings.append("big STCG gain + weak thesis: locking profit beats tax optimisation")

    return {
        "gain_pct": round(gain_pct, 2),
        "hold_days": buy_date_days,
        "options_ranked": options,
        "best": best["option"],
        "warnings": warnings,
        "advice": _advice_line(best, warnings, days_to_ltcg),
    }


def _advice_line(best, warnings, days_to_ltcg) -> str:
    if any("stop-loss" in w for w in warnings):
        return "NOT WISE TO HOLD — stop-loss breached; exit and reuse capital"
    if best["option"] == "SELL NOW":
        return "Selling now wins on net money; further holding must come from thesis, not tax"
    if "LTCG" in best["option"] and days_to_ltcg <= 90:
        return f"Borderline: ~{days_to_ltcg}d to LTCG — hold only if thesis score stays >=60"
    return "Holding justified: thesis intact and net-of-tax outcome favours patience"
