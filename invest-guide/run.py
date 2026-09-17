#!/usr/bin/env python3
"""
run.py — CLI entrypoint.

Modes:
  python run.py nightly    full pipeline (used by GitHub Actions cron)
  python run.py backfill   learning-loop harvest only (cheap, safe to run often)
  python run.py backtest   reconstruct events from REAL cached prices; measure
                           success + consistency rates per signal (no lookahead)
  python run.py screenerbt cross-check theory signals against screener.in's
                           REAL 10y fundamentals (budgeted, rotates nightly)
  python run.py selftest   offline assertions with synthetic data (CI gate)

Stdlib only. ₹0 stack. All secrets optional via env.
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from engine import data, financials, strategies, scoring, learning, tax, exits, report, dashboard, notify  # noqa: E402
from engine import backtest as btmod  # noqa: E402
from engine import screener as scrmod  # noqa: E402
from engine.universe import build_universe, pick_tier_a  # noqa: E402

CONFIG_PATH = ROOT / "config.yaml"
WATCHLIST_FILE = ROOT / "data" / "watchlist.json"


# ------------------------------------------------------------- config loader
def load_config(path: Path = CONFIG_PATH) -> dict:
    """Minimal YAML-subset parser: nested maps, block lists of dicts
    (with lookahead so `key:` followed by `- item` becomes a list),
    inline lists/objects, comments, quotes. Stdlib-only."""
    root: dict = {}
    stack: list[tuple[int, dict]] = [(-1, root)]
    lines = [_strip_comment(ln).rstrip()
             for ln in path.read_text(encoding="utf-8").splitlines()]
    sig = [(len(ln) - len(ln.lstrip()), ln.strip()) for ln in lines if ln.strip()]
    for i, (indent, body) in enumerate(sig):
        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if body.startswith("- "):
            if not isinstance(parent, list):
                # recover: nearest enclosing list above us
                for _lvl, cont in reversed(stack):
                    if isinstance(cont, list):
                        parent = cont
                        break
                else:
                    continue
            rest = body[2:].strip()
            if ":" in rest:
                k, _, v = rest.partition(":")
                item: dict = {k.strip(): _scalar(v) if v.strip() else None}
                parent.append(item)
                stack.append((indent, item))  # continuation keys join this dict
            else:
                parent.append(_scalar(rest))
            continue
        if ":" not in body:
            continue
        key, _, val = body.partition(":")
        key, val = key.strip(), val.strip()
        nxt = sig[i + 1] if i + 1 < len(sig) else None
        if val == "":
            if nxt and nxt[1].startswith("- "):
                lst: list = []
                parent[key] = lst
                stack.append((indent, lst))
            else:
                child: dict = {}
                parent[key] = child
                stack.append((indent, child))
        else:
            parent[key] = _scalar(val)
    return root


def _strip_comment(raw: str) -> str:
    """Cut at the first '#' that is OUTSIDE any quote. The old heuristic
    (skip stripping when the line contained 2+ quotes) broke on comments
    that themselves contain quotes — e.g. `move_abs_pct: 4.0  # a "move"`
    parsed the value as a string. A real scanner fixes it."""
    out = []
    quote = None
    for ch in raw:
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
        elif ch in ("\"", "'"):
            quote = ch
            out.append(ch)
        elif ch == "#":
            break
        else:
            out.append(ch)
    return "".join(out)


def _scalar(v: str):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        return [_scalar(x) for x in inner.split(",")] if inner else []
    if v.startswith("{") and v.endswith("}"):
        out = {}
        for part in v[1:-1].split(","):
            k, _, vv = part.partition(":")
            if k.strip():
                out[k.strip()] = _scalar(vv)
        return out
    low = v.lower()
    if low in ("true", "yes"):
        return True
    if low in ("false", "no"):
        return False
    try:
        return float(v) if ("." in v or "e" in low) else int(v)
    except ValueError:
        return v


# ------------------------------------------------------------- watchlist ----
def load_watchlist() -> list[dict]:
    if not WATCHLIST_FILE.exists():
        WATCHLIST_FILE.parent.mkdir(parents=True, exist_ok=True)
        WATCHLIST_FILE.write_text("[]", encoding="utf-8")
    try:
        rows = json.loads(WATCHLIST_FILE.read_text(encoding="utf-8"))
        return rows if isinstance(rows, list) else []
    except Exception:
        return []


def enrich_watchlist(watchlist: list[dict], records: dict) -> list[dict]:
    out = []
    for w in watchlist:
        w = dict(w)
        rec = records.get(w.get("symbol", "").upper())
        if rec:
            w["last_price"] = rec.get("price")
            if w.get("since_date"):
                try:
                    d0 = datetime.strptime(w["since_date"], "%Y-%m-%d")
                    w["days_tracked"] = (datetime.utcnow() - d0).days
                except ValueError:
                    pass
        out.append(w)
    return out


# ------------------------------------------------------------- selftest -----
def selftest() -> int:
    print("== selftest: offline assertions ==")
    fails = []
    ok = lambda name, cond: fails.append(name) if not cond else print(f"  PASS {name}")

    cfg = load_config()
    ok("config loads", cfg["investor"]["capital_inr"] == 100000 and cfg["scoring"]["min_suggest_score"] == 60)
    ok("yaml loader: rss_sources list-of-dicts",
       isinstance(cfg["news"]["rss_sources"], list) and len(cfg["news"]["rss_sources"]) == 3
       and all(isinstance(x, dict) and "url" in x for x in cfg["news"]["rss_sources"]))
    ok("yaml loader: keyword_tags dict-of-lists",
       isinstance(cfg["news"]["keyword_tags"], dict) and isinstance(cfg["news"]["keyword_tags"]["order_win"], list))
    ok("yaml loader: style_weights floats",
       abs(cfg["investor"]["style_weights"]["quality"] - 0.40) < 1e-9)

    px = data.synthetic_prices()
    fin = data.synthetic_fundamentals()
    rec = financials.derive(fin, px)
    ok("derive: price present", rec["price"] is not None)
    ok("derive: data_quality full", rec["data_quality"] >= 0.9)

    hits = strategies.screen_all(cfg, {"TEST": rec})
    ok("screens: TEST hits quality_compounder", any(h["strategy"] == "quality_compounder" for h in hits.get("TEST", [])))
    ok("screens: TEST hits deep_value", any(h["strategy"] == "deep_value" for h in hits.get("TEST", [])))

    # hermetic KB for all learning tests (never touches the real one)
    import tempfile
    tmpdir = tempfile.mkdtemp()
    orig_kb = learning.KB_FILE
    learning.KB_FILE = Path(tmpdir) / "kb.json"
    learning._save_kb({"events": [], "signals": {r: {} for r in learning.REGIMES}})

    ev = learning.evidence_for(cfg, "TEST", ["quality_compounder"], ["order_win"], {})
    ok("evidence: neutral 50", ev["evidence_score"] == 50.0)

    # --- learning v2: multi-horizon classification (spike vs trend) ---
    cfg2 = json.loads(json.dumps(cfg))
    px_spike = dict(px)
    px_spike["ret_1d"], px_spike["ret_5d"], px_spike["ret_21d"] = 6.0, 4.0, 8.0
    mv = learning._classify_move(cfg2, px_spike)
    ok("v2: +6% day classifies as spike", bool(mv) and mv["regime"] == "spike")
    px_trend = dict(px)
    px_trend["ret_1d"], px_trend["ret_5d"], px_trend["ret_21d"] = 0.5, 14.0, 30.0
    mv2 = learning._classify_move(cfg2, px_trend)
    ok("v2: +14%/5d classifies as trend(weekly)", bool(mv2) and mv2["regime"] == "trend" and mv2["kind"] == "weekly")
    ok("v2: quiet night detects nothing", learning._classify_move(cfg2, px) is None)

    # --- v2: dual-threshold hit-rates + fade/chase-trap accounting ---
    learning._save_kb({"events": [
        {"symbol": "A", "move_date": "2025-01-01", "regime": "spike", "direction": "up",
         "causes": ["order_win"], "fwd_30d": 7.0, "fwd_90d": None, "faded": None},
        {"symbol": "B", "move_date": "2025-02-01", "regime": "spike", "direction": "up",
         "causes": ["order_win"], "fwd_30d": -12.0, "fwd_90d": None, "faded": None},
        {"symbol": "C", "move_date": "2025-03-01", "regime": "trend", "direction": "up",
         "causes": ["order_win"], "fwd_30d": 6.0, "fwd_90d": 22.0, "faded": None},
        {"symbol": "D", "move_date": "2025-04-01", "regime": "trend", "direction": "up",
         "causes": ["order_win"], "fwd_30d": 5.0, "fwd_90d": None, "faded": None},
    ], "signals": {}})
    stats = learning.update_signal_stats(cfg)
    ok("v3: spike stats direction-aware (+5%/30d)", stats["spike"]["order_win:up"]["n"] == 2
       and stats["spike"]["order_win:up"]["raw_hits"] == 1)
    ok("v3: up-spike that faded counts as chase trap", stats["spike"]["order_win:up"]["fades"] == 1)
    ok("v3: trend stats use +15%/90d, pending events excluded", stats["trend"]["order_win:up"]["n"] == 1)
    ok("v3: per-regime __base__ rate computed", stats["spike"]["__base__"]["n"] == 2
       and stats["trend"]["__base__"]["n"] == 1)
    ok("v3: down-move succeeds when fall continues",
       learning._success(cfg, {"regime": "spike", "direction": "down", "fwd_30d": -6.0}) is True)
    ok("v3: down-move that bounces is a miss",
       learning._success(cfg, {"regime": "spike", "direction": "down", "fwd_30d": 3.0}) is False)
    ok("v3: consistency = 1.0 for one-sided recent half",
       learning._consistency([("2025-01-01", False), ("2025-02-01", True),
                              ("2025-03-01", True), ("2025-04-01", True)]) == 1.0)

    # --- v2: regime-aware evidence consumption ---
    stats_manual = {"spike": {"order_win:up": {"n": 12, "hit_rate": 0.71, "raw_hits": 8, "fades": 1}}}
    ev2 = learning.evidence_for(cfg2, "TEST", [], ["order_win"], stats_manual)
    ok("v3: evidence uses spike-regime direction stats", ev2["evidence_score"] == 71.0)
    ev3 = learning.evidence_for(cfg2, "TEST", [], ["results"],
                                {"trend": {"results:up": {"n": 10, "hit_rate": 0.62, "raw_hits": 6, "fades": 0}}})
    ok("v3: cross-regime evidence discounted", abs(ev3["evidence_score"] - 55.8) < 0.1)

    # --- v3: regime detection via hermetic cache injection + backtest smoke ---
    orig_cache, orig_bt = data.CACHE_DIR, btmod.OUT_FILE
    data.CACHE_DIR = Path(tmpdir) / "cache"
    data.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    btmod.OUT_FILE = Path(tmpdir) / "bt.json"
    px_h = dict(px)
    px_h["near_52w_high_pct"], px_h["ret_63_1"] = -1.2, 8.0
    data.cache_write("prices_TEST_400", px_h)
    reg, _notes = learning._current_regime(cfg2, "TEST", [])
    ok("v3: near-52w-high state detected as high52", reg == "high52")
    # 400-bar fixture so evicting high52 detector yields evaluable events
    data.cache_write("prices_TEST2_400", data.synthetic_prices("TEST2", days=400))
    bt = btmod.run_backtest(cfg2, max_symbols=5)
    ok("v3: backtest runs hermetically & finds high52 events",
       bt["regimes"].get("high52", {}).get("n", 0) >= 3)
    ok("v3: backtest consistency present", "consistency" in bt["regimes"]["high52"])

    # --- v3: screener.in table parser (offline fixture) ---
    from engine.screener import _Tables, _series_from_table, _find_period_table
    tp = _Tables()
    tp.feed("<table><tr><th></th><th>Mar 2023</th><th>Mar 2024</th></tr>"
            "<tr><td>Sales</td><td>1,000</td><td>1,200</td></tr>"
            "<tr><td>Net Profit</td><td>100</td><td>150</td></tr></table>")
    at = _find_period_table(tp.tables, "sales", annual=True)   # all-March → annual
    keys_p, vals_p = _series_from_table(at, "sales")
    ok("v3: screener table parsed (periods + series)",
       keys_p == [(2023, 3), (2024, 3)] and vals_p == [1000.0, 1200.0])

    learning.KB_FILE = orig_kb
    data.CACHE_DIR = orig_cache
    btmod.OUT_FILE = orig_bt

    scored = scoring.score_record(cfg, rec, hits.get("TEST", []), ev)
    ok("score in range", 0 <= scored["score"] <= 100)
    buckets = scoring.bucket_suggestions(cfg, [scored])
    ok("buckets: TEST lands somewhere", sum(len(v) for v in buckets.values()) == 1)

    # tax math (exact)
    st = tax.net_after_tax(100000, 30)
    ok("tax: STCG 20%", st["tax"] == 20000 and st["net"] == 80000)
    lt = tax.net_after_tax(200000, 400)
    ok("tax: LTCG 12.5% above 1.25L", lt["tax"] == 9375 and lt["net"] == 190625)
    adv = tax.exit_timeline_advice(cfg, 100, 115, 300, 70)
    ok("tax: advice has ranked options", len(adv["options_ranked"]) >= 2 and adv["best"])

    wl = [{"symbol": "TEST", "since_price": 130, "last_price": 100, "days_tracked": 30}]
    alerts = exits.check_watchlist(cfg, wl, {"TEST": scored})
    ok("exits: stop-zone fires", any(a["level"] == "EXIT" for a in alerts))

    rp = report.build_report(cfg, _selftest_ctx(cfg, rec, scored, hits, alerts))
    ok("report: written & non-empty", len(rp) > 500)
    ok("dashboard: no crash", (dashboard.build(cfg) or True))
    print(f"== selftest {'FAILED: ' + ', '.join(fails) if fails else 'ALL PASS'} ==")
    return 1 if fails else 0


def _selftest_ctx(cfg, rec, scored, hits, alerts):
    return {
        "date": "selftest", "version": "1.0.0-selftest", "nifty": None,
        "stats": {"universe_size": 1, "deep_scan": 1, "movers_tonight": 0},
        "buy": [scored], "watch": [], "alerts": alerts,
        "records": {"TEST": rec}, "moves_learned": 0, "kb_total": 0,
        "move_digest": [], "signal_stats": {},
    }


# ------------------------------------------------------------- nightly ------
def nightly() -> int:
    t0 = time.time()
    cfg = load_config()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"[nightly] {today} start")

    universe = build_universe(cfg)
    if not universe:
        print("[nightly] FATAL: universe empty (NSE CSV + seed both failed)")
        return 1
    watchlist = load_watchlist()

    tier = pick_tier_a(cfg, universe, [w.get("symbol", "") for w in watchlist])
    print(f"[nightly] universe={tier['stats']['universe_size']} deep={tier['stats']['deep_scan']} "
          f"movers={tier['stats']['movers_tonight']}")

    lb = cfg["universe"]["prices_lookback_days"]
    # prices for ALL (move detection needs tonight's data); sleep to be polite.
    # Progress prints every 25 symbols WITH elapsed time and ETA — the old
    # every-50 buffered loop was how a dead-network night looked 'stuck'.
    prices: dict[str, dict] = {}
    t_px = time.time()
    n_ok = 0
    for i, row in enumerate(universe, 1):
        px = data.fetch_prices(row["symbol"], lb)
        if px:
            prices[row["symbol"]] = px
            n_ok += 1
        elif i == 1:
            print("[nightly] WARNING: first price fetch failed — check network "
                  "(run will degrade to caches)", flush=True)
        if i % 25 == 0 or i == len(universe):
            el = time.time() - t_px
            rate = el / i
            print(f"[nightly] prices {i}/{len(universe)} ok={n_ok} "
                  f"({el:.0f}s elapsed, ~{rate * (len(universe) - i):.0f}s left)", flush=True)
        time.sleep(0.12)
    nifty = data.fetch_prices("^NSEI", lb, is_index=True)  # Yahoo index symbol

    # fundamentals only for deep set (cache TTL 21d keeps cost flat)
    fins: dict[str, dict] = {}
    for sym in tier["deep"]:
        fins[sym] = data.fetch_fundamentals(sym) or {}

    records = {}
    for row in universe:
        sym = row["symbol"]
        if sym in tier["deep"] or sym in {w.upper() for w in [x.get("symbol", "") for x in watchlist]}:
            records[sym] = financials.derive(fins.get(sym), prices.get(sym))
    for w in watchlist:
        sym = w.get("symbol", "").upper()
        if sym in prices and sym not in records:
            records[sym] = financials.derive(fins.get(sym), prices.get(sym))

    hits = strategies.screen_all(cfg, records)

    news = data.fetch_news(cfg["news"]["rss_sources"])
    signal_stats = learning.update_signal_stats(cfg)
    moves_learned = learning.harvest(cfg, universe, news)
    print(f"[nightly] KB events +{moves_learned}")

    # evidence + scoring for every candidate with hits (+ watchlist names)
    candidates = {sym for sym, h in hits.items()} | {w.get("symbol", "").upper() for w in watchlist}
    scored = []
    causes_by_sym = {}
    for sym in candidates:
        rec = records.get(sym)
        if not rec:
            continue
        causes = learning.tag_causes(cfg, sym, news)
        causes_by_sym[sym] = causes
        ev = learning.evidence_for(cfg, sym, [h["strategy"] for h in hits.get(sym, [])], causes, signal_stats)
        scored.append(scoring.score_record(cfg, rec, hits.get(sym, []), ev))
    buckets = scoring.bucket_suggestions(cfg, scored)
    scored_by_sym = {s["symbol"]: s for s in scored}

    # hard price ceiling: exceptional businesses above ₹1,000 allowed up to
    # ₹3,000 (config max_price_hard); anything higher never enters BUY.
    hard = float(cfg["investor"]["max_price_hard"])
    buckets["buy"] = [s for s in buckets["buy"]
                      if (records.get(s["symbol"], {}).get("price") or 0) <= hard]

    # watchlist enrich + exits
    watchlist = enrich_watchlist(watchlist, records)
    alerts = exits.check_watchlist(cfg, watchlist, scored_by_sym)

    # tax advice for previously suggested names still tracked via last_report
    last = _read_last_report()
    for h in last.get("buy", []):
        sym = h.get("symbol")
        rec = records.get(sym)
        if not rec or not h.get("ref_price") or not h.get("date"):
            continue
        days = (datetime.now(timezone.utc) - datetime.strptime(h["date"], "%Y-%m-%d")).days
        if days <= 0:
            continue
        adv = tax.exit_timeline_advice(cfg, h["ref_price"], rec.get("price") or h["ref_price"],
                                       days, (scored_by_sym.get(sym) or {}).get("score", 50))
        if adv["warnings"]:
            alerts.append({"symbol": sym, "level": "WARN" if "stop-loss" not in str(adv) else "EXIT",
                           "msg": adv["advice"], "tax": True})

    # attach budget fit + ref price into buys for report/archive
    for s in buckets["buy"]:
        rec = records.get(s["symbol"], {})
        s["ref_price"] = rec.get("price")
        s["date"] = today
        s["causes"] = causes_by_sym.get(s["symbol"], [])

    move_digest = [
        f"{m['symbol']} {m['ret_1d']:+.1f}% vol {m['volume_x'] or '?'}x — causes: "
        f"{', '.join(learning.tag_causes(cfg, m['symbol'], news)) or 'none found (watch next results)'}"
        for m in learning.detect_moves(cfg, universe)[:10]
    ]

    ctx = {
        "date": today,
        "version": _version(),
        "nifty": nifty,
        "stats": tier["stats"],
        "buy": buckets["buy"],
        "watch": buckets["watch"],
        "alerts": alerts,
        "records": records,
        "moves_learned": moves_learned,
        "kb_total": len(learning._load_kb()["events"]),
        "move_digest": move_digest,
        "signal_stats": signal_stats,
    }
    text = report.build_report(cfg, ctx)
    print("[nightly] report + last_report.json written", flush=True)
    dashboard.build(cfg)
    notify.send(cfg, _telegram_summary(cfg, ctx))
    print(f"[nightly] done in {time.time() - t0:.0f}s — buy:{len(buckets['buy'])} "
          f"watch:{len(buckets['watch'])} alerts:{len(alerts)}")
    return 0


def backtest() -> int:
    cfg = load_config()
    rep = btmod.run_backtest(cfg)
    for line in btmod.summarize(rep):
        print(line)
    print(f"[backtest] report written: data/backtest_report.json")
    return 0


def screenerbt() -> int:
    cfg = load_config()
    rep = scrmod.run_screener_backtest(cfg)
    for line in scrmod.summarize(rep):
        print(line)
    print("[screenerbt] report: data/screener_backtest_report.json")
    return 0


def backfill() -> int:
    cfg = load_config()
    universe = build_universe(cfg)
    news = data.fetch_news(cfg["news"]["rss_sources"])
    n = learning.harvest(cfg, universe, news, max_stocks=30)
    stats = learning.update_signal_stats(cfg)
    print(f"[backfill] +{n} events; signals: {json.dumps(stats, indent=1)}")
    return 0


def _read_last_report() -> dict:
    p = ROOT / "data" / "last_report.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _version() -> str:
    from engine import __version__
    return __version__


def _esc(s) -> str:
    """Telegram HTML mode: dynamic text (news-derived msgs) must be escaped."""
    import html
    return html.escape(str(s), quote=False)


def _telegram_summary(cfg, ctx) -> str:
    lines = [f"🌙 <b>{_esc(cfg['report']['title'])} — {_esc(ctx['date'])}</b>"]
    n = ctx.get("nifty") or {}
    lines.append(f"Nifty {_esc(n.get('last', 'n/a'))} ({_esc(n.get('ret_1d', 'n/a'))}%)\n")
    if ctx["buy"]:
        lines.append("<b>BUY ideas</b>")
        for s in ctx["buy"][:5]:
            rec = ctx["records"].get(s["symbol"], {})
            lines.append(f"• <b>{_esc(s['symbol'])}</b> ₹{_esc(rec.get('price', '?'))} · "
                         f"score {s['score']:.0f} [{s['band']}] · "
                         f"{_esc(', '.join(s['strategies'][:2]))}")
    else:
        lines.append("No BUY ideas tonight — patience is a position.")
    if ctx["watch"]:
        lines.append("\n<b>WATCH</b>: " + _esc(", ".join(s["symbol"] for s in ctx["watch"][:6])))
    if ctx["alerts"]:
        lines.append("\n<b>⚠ Alerts</b>")
        for a in ctx["alerts"][:5]:
            lines.append(f"• [{_esc(a['level'])}] {_esc(a['symbol'])}: {_esc(a['msg'][:90])}")
    lines.append(f"\nLearned tonight: {ctx['moves_learned']} moves · KB {ctx['kb_total']}")
    lines.append("<i>Educational tool. Not investment advice.</i>")
    return "\n".join(lines)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "nightly"
    code = {"nightly": nightly, "backfill": backfill, "backtest": backtest,
            "screenerbt": screenerbt, "selftest": selftest}.get(mode)
    if not code:
        print(__doc__)
        sys.exit(2)
    sys.exit(code())
