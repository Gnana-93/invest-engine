# Guide 07 — Trade Journal Template

> Copy this into a Google Sheet with 4 tabs. Same journal from paper day 1 → live.
> The journal IS the system. No entry = trade didn't happen (and a Mistake Counter tick).

---

## Tab 1 — Trade Log (one row per order, incl. both legs of spreads)

**Header rules (rows 1–2, frozen):**
`Max loss/trade: ₹10,000 · Max open ideas: 2 · Strategies allowed this week: [fill] · Mid-day orders = mistake`

| Col | Field | Example |
|---|---|---|
| A | Date + time placed | 16-Sep-2026, 9:25 |
| B | ID (T1, T2…) | T4 |
| C | PAPER / LIVE / SHADOW | PAPER |
| D | Underlying + expiry | Nifty, 29-Sep monthly |
| E | Strategy | Bull put spread |
| F | Legs (strike/type/buy-sell/premium) | Sell 24,700 PE @120 / Buy 24,500 PE @70 |
| G | Qty (lots × lot size) | 1 × 65 |
| H | Net credit/debit (₹) | +3,250 |
| I | Max profit | 3,250 |
| J | Max loss | 9,750 |
| K | Breakeven | 24,650 |
| L | Reason (one line, written BEFORE entry) | "Neutral-bull week, IV 14%, support 24,650" |
| M | Exit plan (written BEFORE entry) | "Exit @ spread ≤35% of credit; hard exit if close < 24,700" |
| N | Exit date + price | 22-Sep, spread @ ₹22 |
| O | Result P&L (after simulated costs) | +1,950 |
| P | Followed plan? (Y/N + deviation note) | Y |
| Q | Emotion note (1 line) | "Wanted to hold for full credit — gamma fear was right" |
| R | Lesson (1 line, feeds Weekly Review) | "Early exit converted 60% max → 60% real, good trade" |

**Cost simulation (Col O):** use Guide 01 §7 formula — ≈₹66/round trip for 1 index lot
option spread; add ₹1–1.5k extra on expensing covered-call round trips (bigger premium STT).

---

## Tab 2 — Daily Notes (2 minutes/evening)

| Date | Market one-liner | My positions' MTM | Tomorrow's plan (orders, exact strikes) | Urges noticed | Followed windows? |
|---|---|---|---|---|---|
| 16-Sep | "Range-bound, RBI speech 10am" | T4 +₹800 | "No new trades; check T4 at 13:00 only" | "Wanted to buy CE on green candle" | Y |

The "Urges noticed" column is the highest-value column in the sheet. Trade your journal,
not your urges.

---

## Tab 3 — Weekly Review (Friday evening, 15 min)

1. **Scorecard:** trades this week __ · journaled 100%? __ · exits per plan __% · cap breached? __
2. **Best decision** (not best trade — best *decision*): ___
3. **Worst decision:** ___
4. **Mistake Counter this week:** __ (running total: __) — list them
5. **Next week's allowed strategies + size:** ___ (from Guide 04 schedule)
6. **Self-audit score (Guide 02 §5):** __/14

---

## Tab 4 — Mistake Counter (your behavioural P&L)

| # | Date | Mistake type | Cost (₹ or 0) | Root cause | Rule I'll install |
|---|---|---|---|---|---|
| 1 | 18-Sep | Mid-day unplanned order | 0 | Boredom | Phone away 12:30–13:30; only Sensibull MTM check |

**Recurring-mistake taxonomy (tick as they appear):** overtrading · early exit · late exit ·
size creep · no-plan entry · revenge trade · FOMO entry · ignored stop · journal skipped.

---

## The three questions (ask before EVERY order, 30 seconds)

1. What is my **max loss** in ₹, and is it within cap?
2. What exactly will make me **exit** (price rule + date rule)?
3. Am I entering because of my **evening plan** or because of something the market just did?

Any "I don't know" → no order. That's the whole discipline in 3 lines.
