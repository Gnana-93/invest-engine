"""
engine/backtest.py — backtest the learned signals against REAL market data.

User requirement: "whatever you learn has to be backtested with real evidence
... add the success rate / consistency rate for the same."

Honesty rules (non-negotiable):
  1. REAL DATA ONLY. Every event is reconstructed from actual NSE daily
     history (Yahoo .NS) cached by the nightly engine. No synthetic series
     ever enters a backtest.
  2. NO LOOKAHEAD. A detector at date i sees only the series slice up to i.
  3. EVICTING DETECTORS. Each date hosts at most one event per symbol, and
     after an event of a regime the same regime waits out its evaluation
     window (spike/result: 30d, trend: 90d) — matching live harvest dedup.
     Without this, one long trend or one volatile fortnight would generate
     dozens of overlapping "events" and fabricate an n that does not exist.
  4. EVALUABLE ONLY. Events whose evaluation window extends past the last
     bar are excluded from hit-rates (their truth is simply not known yet).
  5. PUBLISHED PRIORS DO NOT FILL HOLES. The academic canon (Ball & Brown
     1968, Bernard & Thomas 1989, Jegadeesh & Titman 1993) motivates the
     detectors; the rates below are OUR OWN measured rates on real data.
     Small-n keys are reported as small-n, never padded.

Output: data/backtest_report.json + a console/printable summary.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from . import data, learning

ROOT = Path(__file__).resolve().parent.parent
OUT_FILE = ROOT / "data" / "backtest_report.json"


# ----------------------------------------------------------------- series ---
def _load_series(symbol: str, lb: int) -> dict | None:
    px = data.cache_read(f"prices_{symbol}_{lb}", 3650.0)
    return px if px and len(px.get("close", [])) >= 120 else None


def _returns(closes: list[float], i: int, horizon: int) -> float | None:
    """Return % from bar i to bar i+horizon, or None if not enough bars."""
    if i + horizon < len(closes):
        base = closes[i]
        return round((closes[i + horizon] / base - 1) * 100, 2) if base else None
    return None


def _ret_pct(closes: list[float], i: int, back: int) -> float | None:
    """Return % over the `back` bars ending at i (i-back -> i)."""
    if i - back < 0:
        return None
    base = closes[i - back]
    return round((closes[i] / base - 1) * 100, 2) if base else None


# ----------------------------------------------------------------- events ---
def _build_events(cfg: dict, symbol: str, px: dict) -> list[dict]:
    """
    Reconstruct history for one symbol with evicting, no-lookahead detectors.
    Priority per date: result > spike > weekly > monthly (matching harvest).
    """
    u = cfg["universe"]
    lcfg = cfg["learning"]
    closes, dates = px["close"], px["dates"]
    vol = px.get("volume") or []
    events: list[dict] = []

    # per-regime eviction: earliest index where the regime may fire again
    free_at = {"spike": 0, "trend": 0, "result": 0, "high52": 0, "mom63_1": 0}
    spike_wait = 30
    trend_wait = 90
    state_wait = 45          # high52 / mom63_1 are states -> 45d dedup
    near_min = -cfg["learning"].get("near_52w_within_pct", 2.0)  # 0 = AT the high
    mom_min = cfg["learning"].get("mom63_1_min_pct", 15.0)

    for i in range(70, len(closes) - 1):          # need 63+6d lookback behind
        r1 = _ret_pct(closes, i, 1)
        r5 = _ret_pct(closes, i, 5)
        r21 = _ret_pct(closes, i, 21)
        if r1 is None:
            continue

        # paper-signal states first (they are conditions, not events)
        m631 = _ret_pct(closes, i - 5, 63)        # 3-1 momentum: ends 5 bars back
        near = None
        if i >= 249:
            hi = max(closes[i - 249:i + 1])
            near = round((closes[i] / hi - 1) * 100, 2) if hi else None

        kind = regime = None
        if near is not None and near >= near_min and i >= free_at["high52"]:
            kind, regime = "high52", "high52"
        elif m631 is not None and m631 >= mom_min and i >= free_at["mom63_1"]:
            kind, regime = "mom63_1", "mom63_1"
        elif abs(r1) >= u.get("move_abs_pct", 4.0) and i >= free_at["spike"]:
            kind, regime = "spike", "spike"
        elif r5 is not None and abs(r5) >= u.get("move_5d_pct", 12.0) and i >= free_at["trend"]:
            kind, regime = "weekly", "trend"
        elif r21 is not None and abs(r21) >= u.get("move_21d_pct", 25.0) and i >= free_at["trend"]:
            kind, regime = "monthly", "trend"
        if regime is None:
            continue

        trig = (near if kind == "high52" else m631 if kind == "mom63_1"
                else r1 if kind == "spike" else r5 if kind == "weekly" else r21)
        ev = {
            "symbol": symbol, "move_date": dates[i], "idx": i,
            "kind": kind, "regime": regime,
            # direction follows the TRIGGER's sign (up-state vs down-state)
            "direction": "up" if (trig or 0) >= 0 else "down",
            "ret_1d": r1, "ret_5d": r5, "ret_21d": r21,
            "confirmed": None,
        }
        if vol and len(vol) > i and i >= 21:
            window = vol[max(0, i - 20):i]
            avg = (sum(window) / len(window)) or 1
            vx = vol[i] / avg
            ev["volume_x"] = round(vx, 2)
            ev["confirmed"] = bool(vx >= u.get("move_volume_x", 2.0))
        events.append(ev)
        if regime == "spike":
            free_at["spike"] = i + spike_wait
            free_at["trend"] = max(free_at["trend"], i + 5)   # let trends breathe
        elif regime == "trend":
            free_at["trend"] = i + trend_wait
            free_at["spike"] = max(free_at["spike"], i + 5)
        elif regime == "high52":
            free_at["high52"] = i + state_wait
        elif regime == "mom63_1":
            free_at["mom63_1"] = i + state_wait
    return events


def _evaluate(cfg: dict, events: list[dict], closes: list[float]) -> list[dict]:
    """Attach forward returns; keep only evaluable events (window completed)."""
    out = []
    for ev in events:
        i = ev.pop("idx")
        f30 = _returns(closes, i, 30)
        f90 = _returns(closes, i, 90)
        if ev["regime"] == "trend":
            ok = None if f90 is None else (
                f90 <= -cfg["learning"].get("success_threshold_90d_pct", 15.0)
                if ev["direction"] == "down"
                else f90 >= cfg["learning"].get("success_threshold_90d_pct", 15.0))
            if ok is None:
                continue
            ev.update(fwd_90d=f90, success=bool(ok))
        elif ev["regime"] in ("high52", "mom63_1"):
            thr = cfg["learning"].get("success_threshold_paper_pct", 5.0)
            ok = None if f30 is None else (
                f30 <= -thr if ev["direction"] == "down" else f30 >= thr)
            if ok is None:
                continue
            ev.update(fwd_30d=f30, success=bool(ok))
        else:
            thr = (cfg["learning"].get("success_threshold_result_pct", 5.0)
                   if ev["regime"] == "result"
                   else cfg["learning"].get("success_threshold_pct", 5.0))
            ok = None if f30 is None else (
                f30 <= -thr if ev["direction"] == "down" else f30 >= thr)
            if ok is None:
                continue
            ev.update(fwd_30d=f30, success=bool(ok))
            ev["faded"] = bool(ev["regime"] == "spike" and ev["direction"] == "up"
                               and f30 <= cfg["learning"].get("fade_threshold_pct", -10.0))
        out.append(ev)
    return out


def _stat_block(rows: list[dict], prior: float) -> dict | None:
    n = len(rows)
    if not n:
        return None
    hits = sum(1 for r in rows if r["success"])
    block = {
        "n": n,
        "hit_rate": round((hits + prior * 8) / (n + 8), 3),
        "raw_hits": hits,
        "raw_rate": round(hits / n, 3),
        "avg_fwd": round(sum((r.get("fwd_90d") if r["regime"] == "trend"
                              else r.get("fwd_30d")) or 0 for r in rows) / n, 2),
    }
    dates = sorted(r["move_date"] for r in rows)
    half = dates[len(dates) // 2:]
    recent = [r for r in rows if r["move_date"] in set(half)]
    rh = sum(1 for r in recent if r["success"])
    block["consistency"] = round(abs(2 * rh - len(recent)) / len(recent), 3) if recent else None
    return block


# ----------------------------------------------------------------- main -----
def run_backtest(cfg: dict, max_symbols: int = 150) -> dict:
    lb = cfg["universe"].get("prices_lookback_days", 400)
    prior = cfg["learning"].get("prior_hit_rate", 0.5)

    # universe: every symbol with a cached price series (real fetches only)
    symbols = []
    for p in sorted(data.CACHE_DIR.glob("prices_*_*.json")):
        m = re.match(r"^prices_(.+)_(\d+)\.json$", p.name)
        if m and m.group(1) and not m.group(1).startswith("^"):
            symbols.append(m.group(1))
    symbols = symbols[:max_symbols]

    all_rows: list[dict] = []
    per_symbol: dict = {}
    for sym in symbols:
        px = _load_series(sym, lb)
        if not px:
            continue
        rows = _evaluate(cfg, _build_events(cfg, sym, px), px["close"])
        if rows:
            per_symbol[sym] = len(rows)
            all_rows.extend(rows)

    report: dict = {
        "generated": datetime.utcnow().isoformat(),
        "universe_symbols": len(symbols),
        "symbols_with_events": len(per_symbol),
        "total_evaluable_events": len(all_rows),
        "method": "evicting detectors, no lookahead, real cached NSE data",
        "regimes": {},
        "signals": {},
        "examples": [],
    }

    # per-regime base rates
    for regime in learning.REGIMES:
        rows = [r for r in all_rows if r["regime"] == regime]
        st = _stat_block(rows, prior)
        if st:
            report["regimes"][regime] = st

    # per-signal (regime, kind/cause:direction) rates.
    # Without historical news we cannot tag causes retroactively, so the
    # backtest keys signals by event KIND + volume confirmation — exactly the
    # features the live engine knows at event time.
    keys: dict = {}
    for r in all_rows:
        d = r["direction"]
        keys.setdefault((r["regime"], r["kind"]), []).append(r)
        if r.get("confirmed") is not None:
            ck = f"{r['kind']}+vol" if r["confirmed"] else f"{r['kind']}-vol"
            keys.setdefault((r["regime"], ck), []).append(r)
        if r["regime"] == "spike" and r.get("ret_1d") is not None and abs(r["ret_1d"]) >= cfg["universe"].get("spike_regime_1d_pct", 8.0):
            keys.setdefault((r["regime"], "violent"), []).append(r)
    for (regime, key), rows in sorted(keys.items()):
        st = _stat_block(rows, prior)
        if st:
            report["signals"][f"{regime}:{key}"] = st

    # worked / failed examples (real, auditable)
    for r in all_rows:
        if len(report["examples"]) >= 12:
            break
        if r["regime"] == "trend":
            report["examples"].append(
                f"{r['symbol']} {r['move_date']} {r['kind']} {r['direction']} "
                f"({r['ret_5d']:+.1f}%/5d) → 90d {r.get('fwd_90d'):+.1f}% "
                f"= {'HIT' if r['success'] else 'MISS'}")
        else:
            report["examples"].append(
                f"{r['symbol']} {r['move_date']} {r['kind']} {r['direction']} "
                f"({r['ret_1d']:+.1f}%/1d) → 30d {r.get('fwd_30d'):+.1f}% "
                f"= {'HIT' if r['success'] else 'MISS'}"
                + (" [chase-trap fade]" if r.get("faded") else ""))

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(report, indent=1), encoding="utf-8")
    return report


def summarize(report: dict) -> list[str]:
    lines = [
        f"Backtest {report['generated'][:10]} · {report['universe_symbols']} symbols · "
        f"{report['total_evaluable_events']} evaluable events (real data, no lookahead)"]
    for regime, st in report["regimes"].items():
        lines.append(f"  {regime:6s}: {st['raw_hits']}/{st['n']} = {st['raw_rate']:.0%} "
                     f"raw · smoothed {st['hit_rate']:.0%} · consistency "
                     f"{(st['consistency'] or 0):.0%} · avg fwd {st['avg_fwd']:+.1f}%")
    top = sorted(report["signals"].items(), key=lambda kv: -kv[1]["n"])[:10]
    if top:
        lines.append("  Top signals (by n):")
        for key, st in top:
            lines.append(f"    {key:22s} {st['raw_hits']}/{st['n']} = {st['raw_rate']:.0%}"
                         + (f" · consistency {st['consistency']:.0%}" if st.get("consistency") is not None else ""))
    if report["examples"]:
        lines.append("  Sample outcomes:")
        lines.extend(f"    {e}" for e in report["examples"][:6])
    return lines
