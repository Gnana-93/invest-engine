"""
engine/report.py — builds the nightly brief (markdown) + returns the dict
used by dashboard.py. Sections are ordered by the user's reading priority:
1 market context, 2 BUY ideas (with confidence + tax timing), 3 WATCH,
4 EXIT/WARN alerts, 5 what the engine LEARNED tonight (moves+causes),
6 data-quality honesty note.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT / "reports"


def _ist_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def build_report(cfg: dict, ctx: dict) -> str:
    r = []
    r.append(f"# {cfg['report']['title']} — {ctx['date']}")
    r.append(f"_generated {_ist_now()} · engine v{ctx['version']}_\n")

    # ---- 1 market context
    r.append("## 1. Market context")
    if ctx.get("nifty"):
        n = ctx["nifty"]
        r.append(f"Nifty 50: {n.get('last', 'n/a')} ({n.get('ret_1d', 'n/a')}% 1d, "
                 f"{n.get('ret_1m', 'n/a')}% 1m, {n.get('ret_1y', 'n/a')}% 1y)")
    else:
        r.append("Nifty data unavailable tonight (fetch failed — see data note).")
    r.append(f"Universe scanned: {ctx['stats'].get('universe_size', '?')} · "
             f"deep-scanned: {ctx['stats'].get('deep_scan', '?')} · "
             f"big movers: {ctx['stats'].get('movers_tonight', '?')}\n")

    # ---- 2 BUY ideas
    r.append("## 2. BUY ideas (score-ordered, with confidence)")
    if ctx["buy"]:
        r.append("| # | Stock | ₹ | Score | Conf | Strategy | Budget fit | Evidence |")
        r.append("|---|-------|---|-------|------|----------|------------|----------|")
        for i, s in enumerate(ctx["buy"][:12], 1):
            rec = ctx["records"].get(s["symbol"], {})
            fit = _budget_fit(cfg, rec.get("price") or 0)
            r.append(
                f"| {i} | **{s['symbol']}** {rec.get('name', '')[:24]} | {rec.get('price', '?')} | "
                f"{s['score']:.0f} | {s['band']} | {', '.join(s['strategies'][:2])} | {fit} | "
                f"{_evline(s)} |")
        r.append("")
        r.append("**Entry plan (top pick):** stagger 50% now / 25% on 3% dip / 25% after next results, "
                 "unless earnings within 5 days — then wait for the print (see learning stats).")
        r.append("")
    else:
        r.append("_No stock crossed the BUY line tonight. Patience is a position._\n")

    # ---- 3 WATCH
    r.append("## 3. WATCH list (45-60 — what would upgrade them)")
    if ctx["watch"]:
        for s in ctx["watch"][:8]:
            need = _upgrade_hint(s)
            r.append(f"- **{s['symbol']}** score {s['score']:.0f} ({', '.join(s['strategies'][:1])}) — {need}")
    else:
        r.append("_empty tonight_")
    r.append("")

    # ---- 4 exits / warnings
    r.append("## 4. HOLD WARNINGS / EXITS")
    if ctx["alerts"]:
        for a in ctx["alerts"]:
            r.append(f"- **[{a['level']}] {a['symbol']}** — {a['msg']}")
    else:
        r.append("_nothing flagged tonight_")
    r.append("")

    # ---- 5 learning loop
    r.append("## 5. What the engine LEARNED tonight")
    r.append(f"New cause-tagged moves: {ctx['moves_learned']} (KB total: {ctx['kb_total']})")
    for m in ctx.get("move_digest", [])[:8]:
        r.append(f"- {m}")
    if ctx.get("signal_stats"):
        flat = []
        for regime in ("spike", "trend", "result"):
            for tag, st in (ctx["signal_stats"].get(regime) or {}).items():
                if tag == "__base__":
                    continue
                flat.append((regime, tag, st))
        flat.sort(key=lambda x: -x[2]["n"])
        r.append("\nTop learned signals (direction-aware · spike/result hit = +5%/30d · trend hit = +15%/90d):")
        for regime, tag, st in flat[:6]:
            line = (f"- `{regime}:{tag}`: {st['hit_rate']:.0%} over {st['n']} events"
                    + (f" · consistency {st['consistency']:.0%}" if st.get("consistency") is not None else "")
                    + (f" ({st['fades']} faded = chase traps)" if st.get("fades") else ""))
            b = (ctx["signal_stats"].get(regime) or {}).get("__base__") or {}
            if b.get("n"):
                line += f" · {regime} base rate {b['hit_rate']:.0%} over {b['n']} events"
            r.append(line)
    r.append("")

    # ---- 6 tax corner
    r.append("## 6. Tax corner (FY 2026-27)")
    r.append("STCG 20% · LTCG 12.5% above ₹1.25L/yr · LTCG needs >365d. "
             "Any BUY idea bought today becomes LTCG-eligible in ~365d — "
             "sell-timeline advice per holding appears in section 4 when triggered.")
    r.append("")

    # ---- 7 data honesty
    r.append("## 7. Data quality note")
    weak = [s for s, rec in ctx["records"].items() if (rec.get("data_quality") or 0) < 0.5]
    r.append(f"{len(weak)} deep-scanned stocks had <50% data completeness tonight: "
             f"{', '.join(sorted(weak)[:8]) or 'none'}")
    r.append("_Free data sources lag; never act on one report — cross-check on Screener/Zerodha Kite._")
    r.append("\n---\n_NOT investment advice. Educational engine; you own every decision._")

    text = "\n".join(r)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / f"{ctx['date']}.md").write_text(text, encoding="utf-8")
    _prune_old_reports(cfg)
    (ROOT / "data" / "last_report.json").write_text(
        json.dumps({"date": ctx["date"], "buy": ctx["buy"], "watch": ctx["watch"],
                    "alerts": ctx["alerts"]}, indent=1), encoding="utf-8")
    return text


def _prune_old_reports(cfg: dict) -> None:
    """Enforce config keep_days_of_history (default 90): delete daily report
    .md files older than that. Today's file is always kept."""
    days = int(cfg.get("report", {}).get("keep_days_of_history", 90))
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).date()
    for f in REPORTS_DIR.glob("*.md"):
        try:
            if datetime.strptime(f.stem, "%Y-%m-%d").date() < cutoff:
                f.unlink()
        except ValueError:
            continue  # not a date-named file; leave it alone


def _budget_fit(cfg, price: float) -> str:
    cap = cfg["investor"]["capital_inr"]
    lo, hi = cfg["investor"]["per_position_pct"]
    pref = cfg["investor"].get("max_price_pref", 1000)
    if not price:
        return "n/a"
    pos_lo, pos_hi = cap * lo / 100, cap * hi / 100
    q_lo, q_hi = int(pos_lo // price), int(pos_hi // price)
    note = " (above your ₹%s pref)" % pref if price > pref else ""
    if price > pos_hi:
        return f"₹{price} > max position ₹{pos_hi:.0f} — wait for size or skip{note}"
    if q_lo < 1:
        return f"min {int(pos_lo // price) + 1}sh (₹{price}){note}"
    return f"{q_lo}-{q_hi} shares fits ₹{pos_lo:.0f}-{pos_hi:.0f} band{note}"


def _evline(s) -> str:
    e = s["parts"]["evidence"]
    return f"{e:.0f} (learning)"


def _upgrade_hint(s) -> str:
    hints = []
    if "quality_compounder" not in s["strategies"]:
        hints.append("needs ROCE/growth strength")
    if "deep_value" not in s["strategies"]:
        hints.append("valuation rich for value screen")
    if not hints:
        hints.append("await trigger: results beat / volume confirmation")
    return "; ".join(hints[:2])
