# 🌙 Nightly Indian Stock Investment Engine (₹0/month)

A rules-based nightly research engine for long-term investing on NSE/BSE.
Runs on GitHub Actions (free for public repos), learns from big stock moves,
scores every idea with a **confidence factor**, computes **post-tax sell
timelines**, and pings you on **Telegram** before your morning.

> **Not investment advice.** Educational tool. You own every decision.

---

## What it does every night (02:45 IST)

1. **Universe**: Nifty 500 (NSE CSV) + your extras (`data/universe_extra.json`).
2. **Rotation, not re-research**: full fundamentals only for ~35 names/night
   (fresh movers + your watchlist + a rotating slice). Everything else uses
   ≤21-day cached fundamentals. Cost stays flat forever.
3. **Screens** (all thresholds in `config.yaml`):
   | Strategy | Core rules |
   |---|---|
   | Quality compounder | ROCE≥15, D/E≤0.75, sales≥10%, profit≥12% CAGR, OPM≥12, FCF+ |
   | Deep value | PE≤14, PB≤1.8, D/E≤1.0, earnings not collapsing |
   | Smallcap quality-momentum | >200DMA, +5% RS/3M, ROCE≥14, mcap≤₹5,000cr, delivery-quality proxy |
   | Turnaround | margin inflection + earnings turned positive; debt always flagged |
4. **Learning loop**: every ≥4% move is recorded with cause tags (order win,
   results, management change, pledge, capex, regulatory, ratings) from free
   news RSS. Each signal accumulates a hit-rate — P(+5% within 30d) — with
   Laplace smoothing. Hit-rates need n≥8 events before they influence scores.
   This is the **evidence/confidence factor** shown next to every suggestion.
5. **Scoring**: `quality(0.60) + evidence(0.25) + data-quality(0.10) + liquidity(0.05)`
   → A ≥75, B ≥60, C ≥45, else D. Only A/B go to the BUY table.
6. **Tax engine** (FY 2026-27): STCG 20%, LTCG 12.5% above ₹1.25L/yr, >365d
   holding. Every tracked position gets a ranked comparison: sell now (STCG)
   vs hold to LTCG vs hold to target — with frictions (STT both sides, DP ₹15.25).
7. **"Not wise to hold" alerts**: stop-loss zone (-20%), thesis break (score
   drop ≥15), dead money (~9 months flat while score slides), LTCG-window notes.
8. **Delivery**: Telegram message + `invest-guide/index.html` dashboard +
   `invest-guide/reports/YYYY-MM-DD.md` archive (90 days kept).

## Price preference

- Preferred: **< ₹1,000** (more quantity, smallcap zone) — enforced softly via
  `investor.max_price_pref` in budget-fit guidance.
- Hard ceiling: **₹3,000** (`max_price_hard`) — exceptional businesses above
  ₹1,000 still qualify; anything higher is excluded from BUY lists.
- Liquidity floor: ₹25 lakh daily turnover, price ≥ ₹12 (penny/SME filter).

## One-time setup (15 minutes)

1. **Create the repo**: push this folder to a **public** GitHub repo
   (public = Actions cron is free; private needs GitHub Pro for schedules).
2. **Telegram bot** (free):
   - In Telegram, message **@BotFather** → `/newbot` → copy the token.
   - Message your new bot once (any text), then open
     `https://api.telegram.org/bot<TOKEN>/getUpdates` → find `"chat":{"id": ...}`.
   - Repo → Settings → Secrets and variables → Actions → New repository secret:
     `TELEGRAM_BOT_TOKEN` = token, `TELEGRAM_CHAT_ID` = chat id.
   - Skip this and the engine still runs — it prints the message to the log.
3. **Actions tab** → enable workflows if asked → run **nightly-investment-brief**
   once manually (workflow_dispatch) to validate.
4. Done. Reports arrive ~02:45 IST daily; commits appear in the repo.

## Track your holdings (watchlist mode)

Edit `invest-guide/data/watchlist.json`:

```json
[
  {"symbol": "SUZLON", "since_date": "2026-09-01", "since_price": 58},
  {"symbol": "BEL",    "since_date": "2026-08-15"}
]
```

`since_price` is optional (used for stop-loss math); `since_date` powers the
LTCG clock and dead-money detection. These names are deep-scanned every night.

Add microcaps to the universe via `invest-guide/data/universe_extra.json`
(same format as the seed file).

## Daily/weekly maintenance (5 min)

- **Daily**: read Telegram. That's it.
- **Weekly**: skim `reports/` + learned-signal table on the dashboard;
  prune watchlist names that exited.
- **Every July** (new FY): verify tax constants at the top of
  `engine/tax.py` against current Finance Act. Two numbers: STCG rate,
  LTCG rate/exemption.
- If a source breaks (Yahoo/NSE/RSS change format): each fetcher degrades
  gracefully and the report's data-quality note tells you what's stale.

## Local run (optional)

```bash
python run.py selftest   # offline assertions, no network
python run.py backfill   # learning-loop harvest only
python run.py nightly    # full pipeline
```

Python 3.10+ · zero dependencies (stdlib only).

## How the engine validates itself (evidence, not trust)

The engine holds theories — its strategy screens and 5 learning regimes
(spike, trend, results-drift, 52-week-high, 3-1 momentum). Per your rule, no
theory is trusted because a paper or a guru says so: each is backtested
against REAL data, and only trusted if its measured rate beats the base rate.

| Check | Data source | What it measures | Output |
|---|---|---|---|
| Regime backtest | Cached Yahoo price history (grows nightly) | success rate + consistency per regime/signal — no lookahead, evicting detectors | `run.py backtest` → `data/backtest_report.json` |
| Quality-screen validation | Screener.in 10-yr annual tables | forward 1-yr return of years passing the ROCE/CAGR/OPM screen vs all years | `run.py screenerbt` → `data/screener_backtest_report.json` |
| PEAD drift proxy | Screener.in quarterly profits (YoY ±20%) | 63-day drift after up/down earnings surprises | same report |

Both run nightly in Actions (budgeted: 200 pages/run, universe rotates).
Reports commit to the repo — `n` is shown honestly, small samples say so.

International canon used (verification status honest):
- PEAD — Ball & Brown 1968, Bernard & Thomas 1989/90 ✅ fetched & verified
- Momentum 3-12m — Jegadeesh & Titman 1993 ✅ fetched & verified
- 52-week-high — George & Hwang 2004 ⚠ unverified this session — hypothesis
  only; our NSE backtest decides whether it earns trust.

## Cost breakdown (why this is ₹0)

| Component | Choice | Cost |
|---|---|---|
| Compute/schedule | GitHub Actions, public repo | ₹0 |
| Price data | Yahoo Finance chart API | ₹0 |
| Fundamentals | Yahoo quoteSummary (+ Screener.in 10-yr/quarterly cross-check, built in) | ₹0 |
| News | ET / Moneycontrol / Business-Standard RSS | ₹0 |
| Delivery | Telegram bot + committed HTML dashboard | ₹0 |
| LLM | none — deterministic rules engine | ₹0 |

**What paying would buy (if you ever want it):**
| ₹/month | Gain |
|---|---|
| ~350 (GitHub Pro) | Private repo: schedules + your data hidden from public view |
| ~1,500-4,000 (Screener.in API-level data / Tickertape) | Full multi-year financial statements (real 3y CAGRs, quarterly OPM trends, promoter pledge %) → sharper screens, fewer estimates |
| ~1,500+ (paid LLM API) | Narrative reasoning per stock: management-quality commentary from concalls/annual reports — beyond rule engines |

The current design is deliberately strong on **process discipline** (screens,
evidence, tax math, exits) and weak on **deep fundamental history** — the
first paid upgrade that matters is the financial-data one, not the LLM.

## Known limits (honesty section)

- ROCE is proxied by ROE (Yahoo lacks capital-employed); labelled `roce_est`.
- Growth screens use Yahoo point-in-time growth fields, not true 3y CAGRs —
  the Screener.in cross-check validates the quality core from real history,
  but live screens still run on Yahoo fields (report flags `data_quality`).
- Promoter pledge % and shareholding patterns aren't in free APIs — flagged
  as manual checks in reports for turnaround names.
- Free data occasionally lags a day for smallcaps; the data-quality note
  flags weak records every night.
