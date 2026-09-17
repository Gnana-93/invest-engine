"""
engine/exits.py — "when is it no longer wise to hold" alerts.

User chose WATCHLIST-only tracking (no cost basis), so exits here are
thesis-driven + reference-price-driven rather than tax-lot-driven:
  * thesis break: stock's score dropped >= thesis_break_score_drop vs when
    we last recommended/confirmed it
  * price break: closed below 200DMA after previously being a BUY
  * dead money: ~9 months flat (< +3%) while score keeps falling →
    "capital locked here earns nothing; opportunity cost elsewhere"
  * stop-loss zone: -20% from last-recommended reference price
Reference prices live in data/watchlist.json ("since_price" — user fills
the approximate price when they start tracking; it's not cost-basis
sensitive data, but it is OPTIONAL).
"""

from __future__ import annotations


def check_watchlist(cfg: dict, watchlist: list[dict], scored_by_sym: dict) -> list[dict]:
    alerts = []
    e = cfg["exits"]
    for w in watchlist:
        sym = w.get("symbol", "").upper()
        s = scored_by_sym.get(sym)
        if not s:
            alerts.append({"symbol": sym, "level": "INFO",
                           "msg": "no data tonight (fetch failed or not in universe)"})
            continue
        since_price = w.get("since_price")
        ret_since = None
        px = w.get("last_price")
        if since_price and px:
            ret_since = round((px / since_price - 1) * 100, 1)

        level, msgs = None, []
        if s["score"] < cfg["scoring"]["watch_score"]:
            level, msgs = "WARN", [f"score {s['score']:.0f} fell below watch-line {cfg['scoring']['watch_score']}"]

        if since_price and px:
            if ret_since <= -e["stop_loss_pct"]:
                level = "EXIT"
                msgs.append(f"-{abs(ret_since):.0f}% from tracked price {since_price} — stop zone")
            if 0 <= ret_since < 3 and w.get("days_tracked", 0) >= e["dead_money_days"]:
                if level is None:
                    level = "WARN"
                msgs.append(f"dead money: {w.get('days_tracked')}d at {ret_since:.0f}% while score sliding")

        if level:
            alerts.append({"symbol": sym, "level": level, "msg": "; ".join(msgs),
                           "ret_since": ret_since, "score": s["score"]})
    return alerts


def review_past_suggestions(cfg: dict, history: list[dict], scored_by_sym: dict,
                            prices: dict[str, dict]) -> list[dict]:
    """
    Check yesterday's/older BUY suggestions: did they work? Did anything break?
    This closes the learning loop on our OWN suggestions, not just market moves.
    """
    out = []
    for h in history[-60:]:                      # last ~2 months of reports
        sym = h.get("symbol")
        if not sym or sym in {o["symbol"] for o in out}:
            continue
        px = prices.get(sym)
        if not px:
            continue
        gain = round((px["last"] / h["ref_price"] - 1) * 100, 1) if h.get("ref_price") else None
        s = scored_by_sym.get(sym)
        if gain is not None and gain <= -e_stop(cfg):
            out.append({"symbol": sym, "level": "EXIT",
                        "msg": f"{gain:.0f}% since suggestion @{h['ref_price']} — stop zone"})
        elif s and h.get("score", 100) - s["score"] >= cfg["exits"]["thesis_break_score_drop"]:
            out.append({"symbol": sym, "level": "WARN",
                        "msg": f"thesis break: score {h['score']:.0f} → {s['score']:.0f}"})
    return out


def e_stop(cfg):
    return cfg["exits"]["stop_loss_pct"]
