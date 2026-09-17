"""
engine/universe.py — universe construction + nightly rotation.

User decision: "everything incl. microcaps" — so we do NOT hard-limit to
Nifty 500. We start from the Nifty 500 seed (quality data coverage) and
allow an extension file (data/universe_extra.json) for microcaps the user
or the learning loop adds. Liquidity floors are enforced at screen time,
not at universe time, so movers can enter the pipeline and get rejected
with a visible reason.

Nightly cost control (the "don't re-research everything" rule):
  Tier A (deep scan): fresh movers (|ret_1d| >= 4%), watchlist names,
                      + a rotating slice of the base list.
  Everything else keeps 21d-cached fundamentals — cheap, still fresh.
"""

from __future__ import annotations

import json
import random
from datetime import datetime
from pathlib import Path

from . import data

ROOT = Path(__file__).resolve().parent.parent
EXTRA_FILE = ROOT / "data" / "universe_extra.json"


def load_extra_symbols() -> list[dict]:
    """User-maintained microcap additions. Format: [{"symbol":"XYZ","name":"..."}]"""
    if not EXTRA_FILE.exists():
        return []
    try:
        rows = json.loads(EXTRA_FILE.read_text(encoding="utf-8"))
        return [r for r in rows if isinstance(r, dict) and r.get("symbol")]
    except Exception:
        return []


def build_universe(cfg: dict) -> list[dict]:
    """Nifty 500 + user extras, deduped, price/liquidity floors applied later."""
    seen = {}
    for row in data.fetch_universe_symbols():
        seen[row["symbol"].upper()] = row
    for row in load_extra_symbols():
        sym = row["symbol"].upper()
        if sym not in seen:
            seen[sym] = {"symbol": sym, "name": row.get("name", sym), "industry": row.get("industry", "")}
    return list(seen.values())


def pick_tier_a(cfg: dict, universe: list[dict], watchlist: list[str]) -> dict:
    """
    Choose tonight's deep-scan set.
    Returns {deep: [symbols], rotated: [symbols], rest: [symbols], stats: {...}}
    """
    ucfg = cfg["universe"]
    n_deep = int(ucfg.get("deep_scan_per_night", 35))
    rot_share = float(ucfg.get("rotation_share", 0.35))
    move_abs = float(ucfg.get("move_abs_pct", 4.0))

    # 1) movers: stocks whose cached 1-day return cleared the threshold
    movers = []
    for rec in universe:
        px = data.cache_read(f"prices_{rec['symbol']}_{ucfg.get('prices_lookback_days', 400)}", 1.0)
        if px and px.get("ret_1d") is not None and abs(px["ret_1d"]) >= move_abs:
            movers.append(rec["symbol"])

    wl = [s.upper() for s in watchlist if s]

    # 2) rotation slice from the rest
    rest = [r["symbol"] for r in universe if r["symbol"] not in set(movers) | set(wl)]
    k = max(1, int(len(universe) * rot_share * n_deep / max(1, len(universe))))
    rng = random.Random(datetime.utcnow().strftime("%Y%m%d"))  # deterministic/night
    rotated = rng.sample(rest, min(k, len(rest)))

    deep = list(dict.fromkeys(wl + movers + rotated))[:n_deep]
    deep_set = set(deep)
    others = [r["symbol"] for r in universe if r["symbol"] not in deep_set]

    return {
        "deep": deep,
        "rotated": rotated,
        "movers": movers,
        "watchlist": wl,
        "rest": others,
        "stats": {
            "universe_size": len(universe),
            "deep_scan": len(deep),
            "movers_tonight": len(movers),
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
        },
    }
