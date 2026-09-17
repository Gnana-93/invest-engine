"""
engine/learning.py — the learning loop (v3: multi-horizon, direction-aware, PEAD).

User requirement: "learn from daily/large movements, find what indicated them
earlier, use it next time with a confidence factor."

v2 insight (user's critique): a 70→120 move in ONE WEEK and a 70→200 move over
a YEAR are DIFFERENT lessons. v3 adds a third lesson family backed by the
academic canon, and makes every statistic direction-aware:

  SPIKE regime (event/price-driven)     TREND regime (sustained re-rating)
  ----------------------------------    ----------------------------------
  trigger: |1-day move| >= 4%           trigger: |5d| >= 12% or |21d| >= 25%
  question: "after cause X, did the     question: "when cause X accompanied a
  pop continue (30d) or was it a        grind higher, did the trend KEEP going
  chase trap?"                          (90d)?"
  success: fwd_30d >= +5%               success: fwd_90d >= +15%

  RESULT regime — post-earnings-announcement drift (PEAD)
  -------------------------------------------------------
  trigger: results-day detected (headline matches results keywords for the
           symbol) — no price threshold needed; drift can follow quiet days.
  question: "after quarterly results, does the market keep drifting in the
             direction of the surprise?"
  direction: sign of the results-day move (the market's verdict on the print)
  success: fwd_30d >= +5%  (config success_threshold_result_pct)
  canon:   Ball & Brown (1968); Bernard & Thomas (1989): abnormal returns
           drift in the surprise direction for ~60 days; drift is STRONGEST
           in illiquid, low-coverage names — precisely this engine's <Rs1000
           territory. Bernard & Thomas 1990: ~25-30% of drift clusters around
           the NEXT three earnings announcements.
  dedup:   one result event per symbol per 90 days (= one per quarter).

  HIGH52 regime — 52-week-high proximity (George & Hwang, JF 2004)
  ----------------------------------------------------------------
  trigger: price within X% of its 52-week high (default 2%), no other filter.
  question: "do stocks sitting at/near their 52w high keep drifting up?"
  direction: sign of ret_1d that night (short-horizon verdict)
  success: fwd_30d >= +5% (up) / <= -5% (down)
  canon:   George & Hwang (Journal of Finance 2004): nearness to the 52-week
           high predicts continuation; argued to be anchored underreaction.
           NOT yet India-verified — the backtest decides whether we trust it.
  dedup:   one event per symbol per 45 days (proximity is a state, not a news
           event — without dedup one long uptrend fabricates n).

  MOM63_1 regime — canonical 3-1 momentum (Jegadeesh & Titman, JF 1993)
  ---------------------------------------------------------------------
  trigger: 3-month return EXCLUDING the most recent week >= +15% (the last
           week is excluded so short-term reversal does not contaminate the
           momentum signal — this is the canonical 3-1 construction).
  question: "do 3-1 momentum winners keep winning for another month?"
  direction: sign of the 3-1 return
  success: fwd_30d >= +5% (up) / <= -5% (down)
  canon:   Jegadeesh & Titman (JF 1993): winners outperform by ~1%/month over
           3-12 months; effect documented to fade after ~12 months. Also NOT
           yet India-verified — backtest decides.
  dedup:   one event per symbol per 45 days.

VALIDATION RULE (user's instruction): international papers only HYPOTHESIZE;
engine/backtest.py measures each regime's real NSE success + consistency
rates, and a regime whose measured rate underperforms its base rate gets
dropped or down-weighted. Rates shown to the user are always our measured
ones, never the papers' quoted numbers.

Direction-awareness: every stat key is "tag:up" or "tag:down". Rationale:
"order win" before an up-move and "regulatory" before a down-move are
different lessons — mixing directions corrupted the hit-rate.

Consistency metric (per key): with evaluable events sorted by date, take the
most recent half; consistency = |2*hits - n| / n  (0 = coin-flip over time,
1 = perfectly one-sided). Reported alongside hit-rate so the user sees not
just "does it work" but "has it been working consistently".

Base rates: stats[regime]["__base__"] aggregates ALL evaluable events of that
regime regardless of cause — so a cause tag can be judged as "beats base rate
or not". Evidence scoring ignores "__base__" (it is context, not a tag).

Pipeline per night:
  1. DETECT  results-day (via news keywords) + multi-horizon price scan.
  2. EXPLAIN tag causes from that day's headlines.
  3. RECORD  one KB event per lesson: {kind, regime, direction, causes, ...}.
  4. BACKFILL rolling slice fills fwd_30d / fwd_90d from cached prices.
  5. LEARN   per (regime, tag:direction): hit-rate + consistency (n>=min to trust).
  6. EVIDENCE for tonight's candidate: detect which regime it is in NOW, use
     that regime+direction stats; cap evidence on parabolic charts.

The knowledge base (data/knowledge_base.json) is committed to the repo — it is
the system's memory. Price caches are not.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from . import data

ROOT = Path(__file__).resolve().parent.parent
KB_FILE = ROOT / "data" / "knowledge_base.json"

REGIMES = ("spike", "trend", "result", "high52", "mom63_1")


# ------------------------------------------------------------- knowledge base
def _load_kb() -> dict:
    if KB_FILE.exists():
        try:
            kb = json.loads(KB_FILE.read_text(encoding="utf-8"))
            kb.setdefault("events", [])
            kb.setdefault("signals", {})   # v3 shape: {regime: {"tag:dir": stats}}
            return kb
        except Exception:
            pass
    return {"events": [], "signals": {r: {} for r in REGIMES}, "updated": None}


def _save_kb(kb: dict) -> None:
    kb["updated"] = datetime.utcnow().isoformat()
    KB_FILE.parent.mkdir(parents=True, exist_ok=True)
    KB_FILE.write_text(json.dumps(kb, indent=1), encoding="utf-8")


# ------------------------------------------------------------- move detection
def _classify_move(cfg: dict, px: dict) -> dict | None:
    """
    Multi-horizon classification of tonight's PRICE action into ONE event kind
    (priority: freshest horizon wins). Result-regime detection happens in
    harvest() before this — a results day is a cause, not a price shape.
    """
    u = cfg["universe"]
    r1, r5, r21 = px.get("ret_1d"), px.get("ret_5d"), px.get("ret_21d")

    kind = regime = None
    trigger_ret = None
    if r1 is not None and abs(r1) >= u.get("move_abs_pct", 4.0):
        kind, regime, trigger_ret = "spike", "spike", r1
    elif r5 is not None and abs(r5) >= u.get("move_5d_pct", 12.0):
        kind, regime, trigger_ret = "weekly", "trend", r5
    elif r21 is not None and abs(r21) >= u.get("move_21d_pct", 25.0):
        kind, regime, trigger_ret = "monthly", "trend", r21
    if kind is None:
        return None

    vol_x = None
    if px.get("volume") and len(px["volume"]) >= 21:
        v_last = px["volume"][-1]
        v_avg = (sum(px["volume"][-21:-1]) / 20) or 1
        vol_x = round(v_last / v_avg, 2)

    return {
        "kind": kind,
        "regime": regime,                       # "spike" | "trend"
        "direction": "up" if (trigger_ret or 0) > 0 else "down",
        "ret_1d": r1,
        "ret_5d": r5,
        "ret_21d": r21,
        "trigger_ret": round(trigger_ret, 2),
        "violent": kind == "spike" and abs(r1) >= u.get("spike_regime_1d_pct", 8.0),
        "volume_x": vol_x,
        "confirmed": bool(vol_x and vol_x >= u.get("move_volume_x", 2.0)),
    }


def detect_moves(cfg: dict, universe: list[dict]) -> list[dict]:
    """Tonight's price events across the whole universe (multi-horizon)."""
    ucfg = cfg["universe"]
    moves = []
    for rec in universe:
        px = data.cache_read(
            f"prices_{rec['symbol']}_{ucfg.get('prices_lookback_days', 400)}", 1.0)
        if not px:
            continue
        ev = _classify_move(cfg, px)
        if not ev:
            continue
        ev["symbol"] = rec["symbol"]
        ev["date"] = px["dates"][-1]
        moves.append(ev)
    return moves


# ------------------------------------------------------------- cause tagging
def tag_causes(cfg: dict, symbol: str, news: list[dict]) -> list[str]:
    """Tag which cause-keywords appear in today's headlines for this symbol."""
    tags = set()
    kw = cfg["news"]["keyword_tags"]
    sym_clean = symbol.lower().replace("&", "and")
    for item in news:
        title = item.get("title", "").lower()
        if sym_clean not in title and symbol.lower() not in title:
            continue
        for tag, words in kw.items():
            if any(w in title for w in words):
                tags.add(tag)
    return sorted(tags)


# ------------------------------------------------------------- harvest -------
def harvest(cfg: dict, universe: list[dict], news: list[dict], max_stocks: int = 20) -> int:
    """
    Nightly harvest:
      (a) result-day events (PEAD regime) — one per symbol per 90 days;
      (b) fresh price events (spike/trend) with today's news causes — trends
          de-duplicated on a 45-day window so one leg is recorded once;
      (c) rolling backfill slice (20 stocks/night) fills fwd_30d / fwd_90d.
    Returns number of NEW KB events written.
    """
    kb = _load_kb()
    written = 0
    today = datetime.utcnow()
    today_s = today.strftime("%Y-%m-%d")
    seen_exact = {(e["symbol"], e["move_date"]) for e in kb["events"]}

    # trend de-dup: same symbol+kind within 45 days = same leg, skip
    recent_legs = set()
    # result de-dup: same symbol within 90 days = same quarter, skip
    recent_results = set()
    # high52/mom63_1 de-dup: state-like signals, one event per 45d window
    recent_high52 = set()
    recent_mom = set()
    for e in kb["events"]:
        try:
            age = (today - datetime.strptime(e["move_date"], "%Y-%m-%d")).days
        except (ValueError, TypeError):
            continue
        if age <= 45 and e.get("regime") == "trend":
            recent_legs.add((e["symbol"], e.get("kind")))
        if age <= 90 and e.get("regime") == "result":
            recent_results.add(e["symbol"])
        if age <= 45 and e.get("regime") == "high52":
            recent_high52.add(e["symbol"])
        if age <= 45 and e.get("regime") == "mom63_1":
            recent_mom.add(e["symbol"])

    for rec in universe:
        sym = rec["symbol"]
        px = data.cache_read(
            f"prices_{sym}_{cfg['universe'].get('prices_lookback_days', 400)}", 1.0)
        if not px:
            continue
        causes = tag_causes(cfg, sym, news)

        # ---- RESULT regime (PEAD): results-day headline, any price reaction
        if "results" in causes and sym not in recent_results and (sym, px["dates"][-1]) not in seen_exact:
            r1 = px.get("ret_1d") or 0.0
            kb["events"].append({
                "symbol": sym, "move_date": px["dates"][-1],
                "kind": "result", "regime": "result",
                "direction": "up" if r1 >= 0 else "down",   # market verdict on the print
                "ret_1d": px.get("ret_1d"), "ret_5d": px.get("ret_5d"),
                "ret_21d": px.get("ret_21d"),
                "trigger_ret": round(r1, 2),
                "violent": False, "volume_x": None, "confirmed": None,
                "causes": causes,
                "fwd_30d": None, "fwd_90d": None, "faded": None,
                "recorded": today_s,
            })
            written += 1
            continue    # a results day teaches the PEAD lesson, not the spike lesson

        # ---- HIGH52 regime (George & Hwang 2004): 52w-high proximity
        near = px.get("near_52w_high_pct")
        if (near is not None
                and near >= -cfg["learning"].get("near_52w_within_pct", 2.0)
                and sym not in recent_high52
                and (sym, px["dates"][-1]) not in seen_exact):
            kb["events"].append({
                "symbol": sym, "move_date": px["dates"][-1],
                "kind": "high52", "regime": "high52",
                "direction": "up" if (px.get("ret_1d") or 0) >= 0 else "down",
                "ret_1d": px.get("ret_1d"), "ret_5d": px.get("ret_5d"),
                "ret_21d": px.get("ret_21d"),
                "trigger_ret": near,          # for high52, trigger = proximity %
                "violent": False, "volume_x": None, "confirmed": None,
                "causes": causes,
                "fwd_30d": None, "fwd_90d": None, "faded": None,
                "recorded": today_s,
            })
            written += 1
            continue

        # ---- MOM63_1 regime (Jegadeesh & Titman 1993): 3-1 momentum
        m631 = px.get("ret_63_1")
        if (m631 is not None
                and m631 >= cfg["learning"].get("mom63_1_min_pct", 15.0)
                and sym not in recent_mom
                and (sym, px["dates"][-1]) not in seen_exact):
            kb["events"].append({
                "symbol": sym, "move_date": px["dates"][-1],
                "kind": "mom63_1", "regime": "mom63_1",
                "direction": "up" if m631 >= 0 else "down",
                "ret_1d": px.get("ret_1d"), "ret_5d": px.get("ret_5d"),
                "ret_21d": px.get("ret_21d"),
                "trigger_ret": m631,
                "violent": False, "volume_x": None, "confirmed": None,
                "causes": causes,
                "fwd_30d": None, "fwd_90d": None, "faded": None,
                "recorded": today_s,
            })
            written += 1
            continue

        # ---- SPIKE / TREND regimes (price-shaped)
        ev = _classify_move(cfg, px)
        if not ev:
            continue
        if (sym, px["dates"][-1]) in seen_exact:
            continue
        if ev["regime"] == "trend" and (sym, ev["kind"]) in recent_legs:
            continue
        kb["events"].append({
            "symbol": sym, "move_date": px["dates"][-1],
            "kind": ev["kind"], "regime": ev["regime"],
            "direction": ev["direction"], "violent": ev["violent"],
            "ret_1d": ev["ret_1d"], "ret_5d": ev["ret_5d"], "ret_21d": ev["ret_21d"],
            "trigger_ret": ev["trigger_ret"],
            "volume_x": ev["volume_x"], "confirmed": ev["confirmed"],
            "causes": causes,
            "fwd_30d": None, "fwd_90d": None,
            "faded": None,
            "recorded": today_s,
        })
        written += 1

    # rolling backfill: 20 stocks/night, fill forward returns for old events
    symbols = [r["symbol"] for r in universe]
    start = kb.get("backfill_cursor", 0)
    for sym in symbols[start:start + max_stocks]:
        px = data.cache_read(
            f"prices_{sym}_{cfg['universe'].get('prices_lookback_days', 400)}", 30.0)
        if not px:
            continue
        closes, dates = px["close"], px["dates"]
        for e in kb["events"]:
            if e["symbol"] != sym or e["fwd_30d"] is not None:
                continue
            try:
                i = dates.index(e["move_date"])
            except ValueError:
                continue
            if len(closes) > i + 30:
                e["fwd_30d"] = round((closes[i + 30] / closes[i] - 1) * 100, 2)
            if len(closes) > i + 90:
                e["fwd_90d"] = round((closes[i + 90] / closes[i] - 1) * 100, 2)
        kb["backfill_cursor"] = (start + max_stocks) % max(1, len(symbols))

    if written or kb.get("backfill_cursor") != start:
        _save_kb(kb)
    return written


# ------------------------------------------------------------- hit-rates ----
def _success(cfg: dict, e: dict) -> bool | None:
    """
    Regime-specific, direction-aware success test. None = not yet evaluable.
    Up-events succeed when the drift CONTINUES up (fwd >= +threshold);
    down-events succeed when the fall CONTINUES (fwd <= -threshold).
    """
    lcfg = cfg["learning"]
    down = e.get("direction") == "down"
    if e.get("regime") == "trend":
        f = e.get("fwd_90d")
        if f is None:
            return None                      # trends need their 90d verdict
        thr = lcfg.get("success_threshold_90d_pct", 15.0)
        return f <= -thr if down else f >= thr
    if e.get("regime") == "result":
        f = e.get("fwd_30d")
        if f is None:
            return None                      # PEAD drift needs its 30d verdict
        thr = lcfg.get("success_threshold_result_pct", 5.0)
        return f <= -thr if down else f >= thr
    if e.get("regime") in ("high52", "mom63_1"):
        f = e.get("fwd_30d")
        if f is None:
            return None                      # paper-signal drift, 30d verdict
        thr = lcfg.get("success_threshold_paper_pct", 5.0)
        return f <= -thr if down else f >= thr
    f = e.get("fwd_30d")
    if f is None:
        return None
    thr = lcfg.get("success_threshold_pct", 5.0)
    return f <= -thr if down else f >= thr


def _consistency(events: list[tuple[str, bool]]) -> float | None:
    """
    Recency-stability of a signal: events sorted by date, take the most
    recent half; consistency = |2*hits - n| / n.
    0.0 = the recent half is a coin flip; 1.0 = perfectly one-sided lately.
    None when fewer than 2 evaluable events.
    """
    if len(events) < 2:
        return None
    evs = sorted(events, key=lambda x: x[0])
    half = evs[len(evs) // 2:]               # most recent half (ceil for odd)
    n = len(half)
    hits = sum(1 for _, ok in half if ok)
    return round(abs(2 * hits - n) / n, 3)


def update_signal_stats(cfg: dict) -> dict:
    """
    Recompute direction-aware hit-rates per (regime, tag:direction), plus a
    per-regime __base__ rate over ALL evaluable events (with or without
    causes) so tags can be compared against the unattributed base rate.
    Returns {regime: {key: stats}} for all REGIMES and persists
    it into kb["signals"]. Up-spikes that faded (gave back <= fade_threshold
    in 30d) count as failures AND increment the explicit fade counter.
    """
    kb = _load_kb()
    fade_cut = cfg["learning"].get("fade_threshold_pct", -10.0)

    # key -> list of (move_date, success, faded)
    bucket = {r: {} for r in REGIMES}
    base = {r: [] for r in REGIMES}

    for e in kb["events"]:
        regime = e.get("regime", "spike")
        if regime not in REGIMES:
            regime = "spike"
        ok = _success(cfg, e)
        if ok is None:
            continue
        faded = (regime == "spike" and e.get("direction") == "up"
                 and (e.get("fwd_30d") or 0) <= fade_cut)
        e["faded"] = bool(faded)
        base[regime].append((e.get("move_date", ""), ok))
        d = e.get("direction", "up")
        for tag in e.get("causes", []):
            bucket[regime].setdefault(f"{tag}:{d}", []).append(
                (e.get("move_date", ""), ok, bool(faded)))

    prior = cfg["learning"].get("prior_hit_rate", 0.5)
    min_n = cfg["scoring"].get("min_history_n", 8)
    stats: dict = {r: {} for r in REGIMES}
    for regime in REGIMES:
        # base rate: all evaluable events of this regime
        b = base[regime]
        if b:
            n = len(b)
            hits = sum(1 for _, ok in b if ok)
            stats[regime]["__base__"] = {
                "n": n,
                "hit_rate": round((hits + prior * 8) / (n + 8), 3),
                "raw_hits": hits,
                "consistency": _consistency([(d, ok) for d, ok in b]) if n >= min_n else None,
                "fades": 0,
                "base": True,
            }
        # cause tags, direction-aware
        for key, evs in bucket[regime].items():
            s = [(d, ok) for d, ok, _f in evs]
            n = len(evs)
            hits = sum(1 for _, ok in s if ok)
            stats[regime][key] = {
                "n": n,
                "hit_rate": round((hits + prior * 8) / (n + 8), 3),  # Laplace
                "raw_hits": hits,
                "consistency": _consistency(s) if n >= min_n else None,
                "fades": sum(1 for _d, _ok, f in evs if f),
            }
    kb["signals"] = stats
    _save_kb(kb)
    return stats


# ------------------------------------------------------------- evidence -----
def _current_regime(cfg: dict, symbol: str, causes_today: list[str]) -> tuple[str, list[str]]:
    """
    Which regime is this stock in RIGHT NOW?
    Results-day headline -> result regime (PEAD) regardless of move size.
    Otherwise paper-signal states (52w-high proximity, 3-1 momentum) take
    precedence — they are states, not events. Otherwise price-based:
    trend if 5d/21d thresholds fire, else spike.
    """
    notes: list[str] = []
    px = data.cache_read(
        f"prices_{symbol}_{cfg['universe'].get('prices_lookback_days', 400)}", 1.0)
    if "results" in causes_today:
        notes.append("results-day detected — PEAD drift stats used")
        return "result", notes
    if not px:
        return "spike", notes             # default: judge by event-day tags
    u = cfg["universe"]
    near = px.get("near_52w_high_pct")
    m631 = px.get("ret_63_1")
    if near is not None and near >= -cfg["learning"].get("near_52w_within_pct", 2.0):
        notes.append(f"within {near:.1f}% of 52w high — high52 regime stats used")
        return "high52", notes
    if m631 is not None and m631 >= cfg["learning"].get("mom63_1_min_pct", 15.0):
        notes.append(f"3-1 momentum {m631:+.0f}% — mom63_1 regime stats used")
        return "mom63_1", notes
    r5, r21 = px.get("ret_5d"), px.get("ret_21d")
    if r21 is not None and abs(r21) >= u.get("move_21d_pct", 25.0):
        notes.append(f"active 21d move {r21:+.0f}% — trend regime stats used")
        return "trend", notes
    if r5 is not None and abs(r5) >= u.get("move_5d_pct", 12.0):
        notes.append(f"active 5d move {r5:+.0f}% — trend regime stats used")
        return "trend", notes
    return "spike", notes


def _current_direction(cfg: dict, symbol: str, regime: str) -> str:
    """Tonight's direction for this stock: event regimes (result/spike) and
    state regimes (high52/mom63_1) use the 1-day sign — matching how harvest
    records them; trend uses the 5d/21d sign."""
    px = data.cache_read(
        f"prices_{symbol}_{cfg['universe'].get('prices_lookback_days', 400)}", 1.0)
    if not px:
        return "up"
    r1, r5, r21 = px.get("ret_1d"), px.get("ret_5d"), px.get("ret_21d")
    if regime in ("result", "spike", "high52", "mom63_1"):
        return "up" if (r1 or 0) >= 0 else "down"
    if r5 is not None and abs(r5) >= cfg["universe"].get("move_5d_pct", 12.0):
        return "up" if r5 >= 0 else "down"
    return "up" if (r21 or 0) >= 0 else "down"


def evidence_for(cfg: dict, symbol: str, strategies_hit: list[str],
                 causes_today: list[str], signal_stats: dict) -> dict:
    """
    Confidence evidence for tonight's suggestion, regime- AND direction-aware:
      - pick the regime the stock is in now (result / spike / trend);
      - key each tag with tonight's direction ("tag:up" / "tag:down");
      - cross-regime evidence counts at 0.9 weight, opposite-direction at 0.8;
      - PARABOLIC GUARD: +60%/21d or +35%/5d charts cap evidence at 55 —
        learned stats must not talk us into chasing a vertical move.
    Neutral 50 when nothing learned yet.
    """
    min_n = cfg["scoring"]["min_history_n"]
    primary, regime_notes = _current_regime(cfg, symbol, causes_today)
    parts, notes = [], list(regime_notes)
    others = [r for r in REGIMES if r != primary]
    direction = _current_direction(cfg, symbol, primary)

    for tag in causes_today:
        if tag == "results" and primary == "result":
            key = f"results:{direction}"      # PEAD lesson keyed by print verdict
        else:
            key = f"{tag}:{direction}"
        st = (signal_stats.get(primary) or {}).get(key)
        if st and st["n"] >= min_n:
            parts.append(st["hit_rate"])
            note = (f"{primary}:{key} {st['raw_hits']}/{st['n']} → {st['hit_rate']:.0%}"
                    + (f" · consistency {st['consistency']:.0%}" if st.get("consistency") is not None else "")
                    + (f" ({st['fades']} faded)" if st.get("fades") else ""))
            notes.append(note)
            continue
        # fallbacks: cross-regime same direction (0.9), same regime opposite direction (0.8)
        placed = False
        for o in others:
            xs = (signal_stats.get(o) or {}).get(key)
            if xs and xs["n"] >= min_n:
                parts.append(xs["hit_rate"] * 0.9)
                notes.append(f"{o}:{key} {xs['raw_hits']}/{xs['n']} → "
                             f"{xs['hit_rate']:.0%} (cross-regime)")
                placed = True
                break
        if placed:
            continue
        opp = (signal_stats.get(primary) or {}).get(
            f"{tag}:" + ("down" if direction == "up" else "up"))
        if opp and opp["n"] >= min_n:
            parts.append(opp["hit_rate"] * 0.8)
            notes.append(f"{primary}:{tag} opposite-direction "
                         f"{opp['raw_hits']}/{opp['n']} → {opp['hit_rate']:.0%} (discounted)")
        elif st or any((signal_stats.get(o) or {}).get(key) for o in others):
            have = (st or next(((signal_stats.get(o) or {}).get(key) for o in others
                                if (signal_stats.get(o) or {}).get(key)), None))["n"]
            notes.append(f"{key}: only {have} events yet — neutral prior")

    px = data.cache_read(
        f"prices_{symbol}_{cfg['universe'].get('prices_lookback_days', 400)}", 1.0)
    parabolic = bool(px and (
        (px.get("ret_21d") or 0) >= cfg["learning"].get("parabolic_21d_pct", 60.0)
        or (px.get("ret_5d") or 0) >= cfg["learning"].get("parabolic_5d_pct", 35.0)))
    if parabolic:
        notes.append(f"parabolic chart ({px.get('ret_21d', 0):+.0f}%/21d, "
                     f"{px.get('ret_5d', 0):+.0f}%/5d) — evidence capped at 55")

    if parts:
        score = round(100 * sum(parts) / len(parts), 1)
    else:
        score = 50.0
    if parabolic:
        score = min(score, 55.0)
    return {"evidence_score": score,
            "evidence_notes": notes or ["no learned signals yet — neutral"]}


def explain(cfg: dict, scored: dict, causes: list[str], signal_stats: dict) -> str:
    """One-line confidence explanation for the report."""
    band = scored["band"]
    ev = scored["parts"]["evidence"]
    if causes:
        return f"{band} · evidence {ev:.0f} · learned causes: {', '.join(causes)}"
    return f"{band} · evidence {ev:.0f} · no same-day cause tags"
