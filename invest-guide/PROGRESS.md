# Investment Engine — Progress Tracker & Flow Map

> **Purpose:** If this session stops (token shortage / disconnect), restart by reading
> this file. It maps the ENTIRE system, marks what is built, and tells the next
> session exactly where to resume. Pattern copied from `fo-guide/PROGRESS.md`
> (which already survived one connection drop successfully).

> **STATUS (2026-09-19): LIVE IN PRODUCTION.** All Status Board rows ✅.
> Engine v1.5.0 runs nightly on GitHub Actions (`Gnana-93/invest-engine`,
> public) — 6/6 workflow runs green, cron 21:15 UTC firing, bot commits
> landing (2026-09-17, 2026-09-18), learning KB accumulating nightly.
> **Nothing pending in code.** New sessions: read §5 + last §7 rows, do the
> work, then APPEND a §7 row — don't let this file go stale again.

---

## 1. What We Are Building (one paragraph)

A ₹0/month **nightly research engine** for Indian equities. Every night a GitHub
Actions cron (public repo, free) runs a stdlib-only Python pipeline that: pulls
prices/fundamentals/news for a curated universe, runs 4 strategy screeners
(quality compounders, deep value, smallcap quality-momentum, turnaround),
scores every stock, computes post-tax return timelines (STCG 20% vs LTCG 12.5%
+ ₹1.25L exemption), flags "not wise to hold" situations, learns from big
stock moves (records what indicated them: news/results/orders → hit-rates →
confidence factor per suggestion), and delivers a morning Telegram message +
HTML dashboard. Investor context: under ₹1 lakh capital, prefers <₹1000 stocks,
watchlist-only tracking (no cost basis), Zerodha.

## 2. Architecture (files and what they do)

```
invest-guide/
├── PROGRESS.md            ← THIS FILE (resume map — keep updated!)
├── config.yaml            ← all knobs: universe, screens, scoring, tax, telegram
├── run.py                 ← CLI entrypoint: nightly | backfill | selftest |
│                            backtest | screenerbt
├── engine/
│   ├── __init__.py        ← version string
│   ├── data.py            ← fetchers: Yahoo prices, fundamentals, NSE universe,
│   │                        RSS news; disk cache (data/cache/*.json)
│   ├── universe.py        ← builds ~200-stock universe; rotation slices
│   ├── financials.py      ← derived metrics: ROCE, growth, OPM, D/E, FCF, pledge
│   ├── strategies.py      ← 4 screeners from config thresholds
│   ├── scoring.py         ← composite score + data-quality + liquidity
│   ├── learning.py        ← big-move detector, cause tags, hit-rate KB,
│   │                        confidence per suggestion (6 regimes incl. corpact)
│   ├── backtest.py        ← real-data regime backtest (no lookahead, evicting
│   │                        detectors) → data/backtest_report.json
│   ├── screener.py        ← screener.in scraper: fundamentals (PRIMARY source),
│   │                        point-in-time screen validation, PEAD proxy,
│   │                        quarterly tables → data/screener_backtest_report.json
│   ├── tax.py             ← STCG/LTCG engine, exit-timeline advice
│   ├── exits.py           ← stop-loss, thesis-break, dead-money warnings
│   ├── report.py          ← daily report builder (dict → markdown/dict)
│   ├── dashboard.py       ← HTML dashboard generator (index.html)
│   └── notify.py          ← Telegram sender (secrets from env; skip if unset)
├── data/                  ← gitignored cache + knowledge base snapshots
├── reports/YYYY-MM-DD.md  ← daily report archive (90 days kept)
└── .github/workflows/nightly.yml  ← cron 21:15 UTC (= 02:45 IST) + selftest
```

## 3. Data Flow (nightly)

```
cron 21:15 UTC (02:45 IST)
  → run.py nightly
  → universe.py: load universe.json (committed); pick deep-scan set
      (fresh movers + rotation slice + watchlist)
  → data.py: prices (Yahoo .NS) → cache; fundamentals (screener.in scrape /
      Yahoo key-stats fallback) → cache (21d TTL); news RSS → tags
  → financials.py: derive ROCE/CAGR/OPM/D/E/FCF per stock
  → strategies.py: screen all 4 → candidate list
  → learning.py: ① detect big moves (|Δ|≥4%) in last 24h ② tag causes from
      news/filings ③ update knowledge base hit-rates ④ backfill harvest
      (rolling 20 stocks/night over 5y history)
  → scoring.py: composite = quality*.60 + evidence*.25 + data-quality*.10
      + liquidity*.05 → confidence band A/B/C/D
  → tax.py: per candidate: STCG vs LTCG net-return table, hold-timeline advice
  → exits.py: watchlist checks → HOLD/WARN/EXIT flags
  → report.py: build daily report; write reports/YYYY-MM-DD.md
  → dashboard.py: regenerate index.html
  → notify.py: Telegram summary (if secrets present, else console)
  → git commit+push reports/dashboard (Actions does this)
```

## 4. Key Decisions Locked (with user)

| Decision | Choice | Notes |
|---|---|---|
| Runner | Public GitHub repo | ₹0; cron works; secrets not needed except Telegram |
| Delivery | Telegram + HTML dashboard | Email dropped (not selected) |
| Strategies | Compounders, Deep value, Smallcap quality-momentum, Turnaround | Dividend/index fallback NOT selected |
| Universe | Everything incl. microcaps | Liquidity floor ₹25L turnover, price ≥ ₹12 |
| Brain | Rules engine only (no LLM) | ₹0; deterministic; confidence via hit-rates |
| Holdings | Watchlist only | No cost basis → tax engine works on hypothetical buys |
| Capital | Under ₹1 lakh | 8–12 positions, min ₹8k position |
| Learning loop | Statistical (no LLM) | move→cause tagging→hit-rates→confidence factor |
| Tax | FY26-27: STCG 20%, LTCG 12.5% over ₹1.25L | hardcoded in tax.py, easy to update |

## 5. Status Board

| # | Deliverable | File | Status |
|---|---|---|---|
| 0 | Progress tracker | `PROGRESS.md` | ✅ Done (this file) |
| 1 | Config | `config.yaml` | ✅ Done |
| 2 | Package init | `engine/__init__.py` | ✅ Done |
| 3 | Data fetchers + cache | `engine/data.py` | ✅ Done |
| 4 | Universe builder | `engine/universe.py` | ✅ Done |
| 5 | Financial metrics | `engine/financials.py` | ✅ Done |
| 6 | Strategy screeners | `engine/strategies.py` | ✅ Done |
| 7 | Scoring + confidence | `engine/scoring.py` | ✅ Done |
| 8 | Learning loop | `engine/learning.py` | ✅ Done |
| 9 | Tax engine | `engine/tax.py` | ✅ Done |
| 10 | Exit/hold warnings | `engine/exits.py` | ✅ Done |
| 11 | Report builder | `engine/report.py` | ✅ Done |
| 12 | Dashboard | `engine/dashboard.py` | ✅ Done |
| 13 | Telegram notifier | `engine/notify.py` | ✅ Done |
| 14 | CLI entrypoint | `run.py` | ✅ Done (+ YAML loader rewritten w/ lookahead) |
| 15 | GitHub workflow | `.github/workflows/nightly.yml` | ✅ Done |
| 16 | README (setup: Telegram secrets, cron, user guide) | `README.md` | ✅ Done |
| 17 | `.gitignore` for data/cache | `invest-guide/.gitignore` | ✅ Done |
| 18 | Smoke test pass (selftest) | — | ✅ Done (green in Actions since run #1; 6/6 runs passed) |
| 19 | Review fixes: index symbol, target-upside, price ceilings, TG escaping | various | ✅ Done |
| 20 | 90-day report pruning (keep_days_of_history enforced) | `engine/report.py` | ✅ Done |
| 21 | Static audit: loader vs config, workflow commit paths, dashboard output path | — | ✅ Done |
| 22 | Learning-loop v2: multi-horizon (spike vs trend — user's Stock A/B critique) | `engine/learning.py` | ✅ Done |
| 23 | v2 consumers: config keys, report/dashboard stats shape, selftest assertions, version bump | various | ✅ Done |
| 24 | Learning v3: +result(PEAD)/high52/mom63_1 regimes, direction-aware stats, consistency metric | `engine/learning.py`, `data.py`, config | ✅ Done |
| 25 | Real-data backtest harness (no lookahead, evicting detectors, success+consistency) | `engine/backtest.py`, run.py `backtest` mode | ✅ Done |
| 26 | Screener.in cross-check (quality-screen validation + PEAD proxy from real fundamentals) | `engine/screener.py`, run.py `screenerbt` mode | ✅ Done |
| 27 | Nightly workflow runs both backtests; accumulated sample committed (repo-safe) | `.github/workflows/nightly.yml` | ✅ Done |
| 28 | GO-LIVE: repo public + Actions cron live, nightly reports committing | — | ✅ Done (2026-09-17) |
| 29 | v1.3.0: fundamentals from screener.in PRIMARY (fix starved screens after Yahoo quoteSummary 401); report polish (real company names from page h1, Nifty 1y return via range=2y) | `engine/screener.py`, `engine/data.py`, `run.py` | ✅ Done |
| 30 | v1.4.0: numeric quarterly review — real 2-quarter OPM inflection for turnaround; deep-value earnings check prefers quarterly profit YoY | `engine/screener.py`, `financials.py`, `strategies.py`, `run.py` | ✅ Done |
| 31 | v1.5.0: corpact learning regime (6th) — measure bonus/dividend/split/buyback edge: announcement = event, direction = 1d reaction, success = 30d drift (success_threshold_corpact_pct) | `engine/learning.py`, `config.yaml`, `report.py`, `run.py` | ✅ Done |
| 32 | Docs sync: PROGRESS.md + README.md updated to production reality; stale status rows fixed | docs | ✅ Done (2026-09-19) |

## 6. Session Protocol (start AND end — non-skippable)

**Session START:**
1. `git pull --ff-only` FIRST. The bot commits nightly reports; a stale clone
   creates fake "pending work" (2026-09-19: stale selftest artifacts from a
   manual run looked like uncommitted work and blocked the pull).
2. Read this file top to bottom: banner → §5 Status Board → last §7 rows.
3. If a fresh morning: verify last night's run — `reports/YYYY-MM-DD.md`
   exists, latest Actions run green
   (`api.github.com/repos/Gnana-93/invest-engine/actions/runs?per_page=3`),
   bot commit on remote. Report missing → check §9 rows 2-3 (Telegram
   secrets) + run log before touching code.
4. Find first ⬜ row in Status Board → build that next. Build order MUST
   respect dependencies:
   `data.py → financials.py → universe.py → strategies.py → scoring.py →
   learning.py → tax.py → exits.py → report.py → dashboard.py → notify.py →
   run.py → workflow → README → selftest`.
5. Never rewrite already-✅ files from scratch — read first, patch if needed.

**Session END (this file went stale once — never again):**
1. `git pull --ff-only` (the bot may have committed while you worked).
2. Update §5 Status Board + append ONE §7 Checkpoint Log row: what changed,
   what's next. A session that skips this erases itself for the next one.
3. If engine behavior changed: sync §2 architecture tree, §3 data flow, and
   README.md to match.
4. Commit + push the docs. An unpulled progress map helps nobody.

## 7. Checkpoint Log

| Timestamp | Checkpoint | Notes |
|---|---|---|
| Session 3 | Learning v2 complete: `learning.py` rewritten (multi-horizon `_classify_move`, dual-threshold `_success`, fade/chase-trap counter, regime-aware `evidence_for` with parabolic cap), config extended, `report.py`+`dashboard.py` consume nested stats shape, selftest adds 9 v2 assertions with hermetic KB swap, `engine/__init__.py` → 1.1.0. Static verification done; execution happens in Actions. | Next: user go-live per §9 |
| Session 4 | Learning v3 per user instruction ("international papers OK, validate for India; backtest with real evidence; use screener.in for old data"): (1) canon anchored — PEAD Ball&Brown'68/Bernard&Thomas'89 (fetched), momentum Jegadeesh&Titman'93 (fetched); George&Hwang'04 + momentum-crash lit flagged unverified-this-session, used as hypotheses only. (2) `learning.py` → 5 regimes (spike/trend/result-PEAD/high52/mom63_1), direction-aware keys `tag:dir`, down-move success = fall continues, consistency metric, per-regime `__base__` rate. (3) `backtest.py` — real cached prices, no lookahead, evicting detectors, per-regime + per-signal success/consistency, worked/failed examples → `data/backtest_report.json`. (4) `screener.py` — stdlib HTML table parser, point-in-time quality-screen validation (fwd 250d, passing vs base years) + PEAD proxy (quarterly profit YoY ±20% → fwd 63d), budgeted 200 reqs/run, 30d page cache, accumulation file committed instead of page caches → `data/screener_backtest_report.json`. (5) Workflow runs both nightly and commits reports; selftest extended (direction-aware keys, high52 hermetic-cache detection, backtest smoke, parser fixture); version → 1.2.0. | Next: first Actions run executes selftest+backtests; regime trust decided by measured rates |
|---|---|---|
| Session start | Questions asked & answered | 7 decisions locked (see §4) |
| Session start | config.yaml written | Engine knobs + thresholds locked |
| T+0 | PROGRESS.md created | This file; resume protocol active |
| T+1 | __init__ + data.py done | Yahoo chart/summary, NSE CSV, RSS, cache w/ TTL, synthetic data for selftest |
| Session 2 (resumed after drop) | ALL engine files + workflow + README + seed built | 17 files verified on disk via glob |
| Session 2 | Review fixes applied | ^NSEI is_index, target_mean stored, hard/pref price ceilings, TG html escaping, YAML loader lookahead rewrite |
| Session 2 | Status Board synced to reality | rows 4-19 marked; only selftest run pending |
| Session 3 | Report pruning added (session 2 cut-off recovered) | `_prune_old_reports()` in report.py; timedelta import fixed |
| Session 3 | Static audit complete, no shell on this machine | loader/dashboard/workflow paths verified by reading code; selftest must run in Actions |
| Session 3 | ONLY PENDING: selftest + user GitHub/Telegram setup | see §9 First-Run Checklist |
| Session 3 (evening prep) | GITHUB-SETUP.md created | Step-by-step: Git install → repo → push → Telegram bot → secrets → first run → troubleshooting |
| Session 3 (evening prep) | PAUSED — user disconnecting till evening | Learning v2 half-done: config.yaml ✓ (move_5d_pct, move_21d_pct, spike_regime_1d_pct, success_threshold_90d_pct, fade_threshold_pct) + data.py ✓ (ret_5d, ret_21d in _price_metrics). NEXT ON RESUME: (1) learning.py overhaul — detect_moves multi-horizon, event.regime=spike/trend, update_signal_stats dual thresholds, evidence_for spike-vs-trend classification; (2) selftest additions for v2; (3) explain Stock A (spike) vs Stock B (trend) logic to user in plain language |
| Sessions 3.5–4.5 (logged late, 2026-09-19) | v1.3.0 / v1.4.0 / v1.5.0 shipped + engine went LIVE | (1) v1.3.0: Yahoo quoteSummary started 401-ing → fundamentals rebuilt on screener.in pages as PRIMARY (top-ratios widget = true ROCE/PB/D/E, annual + quarterly tables), Yahoo kept as fallback; report prints real company names from page h1; Yahoo chart range 1y→2y so ret_1y stops printing None. (2) v1.4.0: quarterly_fundamentals() reads screener.in quarterly tables → real last-2Q OPM trend for turnaround, quarterly profit YoY for deep value. (3) v1.5.0: corpact regime — corpaction headlines rarely move ≥4% so spike detector never caught them; now announcement IS the event (1d reaction = direction, 30d drift = success). All committed & pushed; nightly runs green on top. |
| Session 5 (2026-09-19) | Docs synced to production reality | Engine LIVE: 6/6 Actions runs green, cron verified via API, bot commits 09-17+09-18 on remote. Local repo had drifted 2 bot-commits behind with 3 stale selftest artifacts (from a manual 15:11 UTC run) — discarded + ff-pulled. Architecture tree fixed (+backtest.py, +screener.py, run.py modes), row 18 un-staled, §9 marked complete. NO PENDING WORK in code — docs were the only debt. Next session: work, then append a row here |

## 8. Standing Warnings (apply to every report the engine produces)

- Not investment advice; educational tool. User decides & bears risk.
- Microcaps: operator/pump risk real → liquidity + delivery% filters mandatory.
- Free data can lag/break: every fetcher needs try/except + fallback + data-quality score.
- SEBI FY26 context: ~88-93% retail F&O losers — user also does F&O (fo-guide); keep equity advice long-horizon.
- Tax numbers hardcoded for FY2026-27; recheck each July (new FY) — add to README maintenance section.

## 9. First-Run Checklist — COMPLETE (engine is live)

| # | Step | Status |
|---|---|---|
| 1 | Push repo to GitHub as **public** | ✅ `Gnana-93/invest-engine` |
| 2 | Create Telegram bot → get token + your chat ID | ✅ configured (if a morning brief ever stops arriving, re-check this + #3) |
| 3 | Add secrets `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` | ✅ (notify degrades silently to console if ever unset — runs stay green) |
| 4 | Enable Actions on the repo | ✅ scheduled runs firing |
| 5 | First run: Actions tab → nightly-investment-brief → Run workflow | ✅ runs #1–#6 all green |
| 6 | Verify: Actions log shows `[nightly] done`; Telegram message arrives; `invest-guide/index.html` updated in the commit | ✅ bot commits 2026-09-17 & 2026-09-18 on remote |
| 7 | Nightly cron 21:15 UTC = 02:45 IST → report ready each morning | ✅ LIVE — no intervention needed |
