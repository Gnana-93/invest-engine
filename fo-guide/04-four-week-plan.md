# Guide 04 — The 4-Week Paper Trading Plan

> Designed for: 10–15 min during market hours + ~1 hour evening.
> **Rule of the plan: milestones, not dates.** Repeat any week until you pass its exit
> checklist. Moving slow here is the fastest path to lasting live.

---

## 0. Standing rules (every day, every week)

1. **Evening plans, market executes.** All orders decided the previous evening; place at
   9:20–9:35 or 14:45–15:15 only. Mid-day window = look, log, don't touch.
2. Max loss per trade: **₹10,000 (2% of ₹5L paper capital)**. Max open positions: 2.
3. Every order must state, *before placing*: strategy, strikes, expiry, max profit,
   max loss, breakeven, and the reason (one line).
4. Journal entry same evening (07-trade-journal.md). Miss it → Mistake Counter.
5. Costs: log every trade with the Zerodha cost formula from Guide 01 §7 as if real.
6. If Nifty moves >1.5% intraday on news (RBI, budget, elections) → no new positions that day.

---

## Week 1 — Observation & first long trades (mechanics week)

**Study:** Varsity options ch. 1–6. **No selling yet.** Only buying = capped risk.

| Day | Market window (10–15 min) | Evening (~1 hr) |
|---|---|---|
| Mon | Read Nifty chain; note ATM strike, CE/PE premiums, bid-ask spread. No trades. | Varsity ch.1–2 + journal setup + notes |
| Tue | Log premiums of 25,000 CE and 25,500 CE at 13:00. | Varsity ch.3–4 + notes |
| Wed | **Trade 1 (paper):** Buy 1 lot Nifty weekly ATM CE (e.g., 25,000 CE @ ~₹150 = ₹9,750). Plan exit: either +40% premium or −50%. | Varsity ch.5 + journal Trade 1 (max loss ₹9,750 written) |
| Thu | 13:00 check Trade 1: premium vs entry. Note delta in Sensibull. Log. | Varsity ch.6 + decide Trade 1 exit for tomorrow |
| Fri | Execute planned exit of Trade 1 (whatever it is — follow the plan!). | Journal review + Varsity quiz + Weekly Review tab |

**Example — Trade 1 journal row:**
`Nifty 25,000 CE (weekly) · Entry ₹150 · Qty 65 · Max loss ₹9,750 · Reason: "learning mechanics, ATM delta ~0.5" · Exit plan: +40%/-50% · Result: +₹1,300 (7% of premium) after costs ₹64 · Emotion: itched to exit early, didn't ✔`

**Week 1 exit checklist:** [ ] 5 journal entries [ ] can explain ITM/ATM/OTM + bid-ask [ ] 1 trade entered & exited exactly per plan [ ] quiz ≥70%.
Fail any → repeat week 1 next week (fine!).

---

## Week 2 — Theta & delta in your face (engine room)

**Study:** Greeks + volatility chapters. Trades: 2–3 long options, *different expiries*, to feel decay.

| Day | Market window | Evening |
|---|---|---|
| Mon | **Trade 2:** Buy 1 lot Nifty **weekly** ATM CE. **Trade 3:** Buy 1 lot Nifty **monthly** ATM CE. Same spot, two clocks. | Greeks chapters + journal both trades |
| Tue–Thu | Daily 13:00: log both premiums side by side. Weekly should decay visibly faster. | 1 Greeks chapter/day + notes on which Greek dominated each day |
| Fri | Close both per plan (exits decided Thursday evening). | Compare: weekly vs monthly P&L. Write 3 lines on theta. Weekly Review. |

**Mini-lesson embedded:** if both trades lose money but the monthly loses less,
you've *personally discovered* why income sellers prefer selling short-dated and
buyers prefer longer-dated. That insight is worth more than any video.

**Week 2 exit checklist:** [ ] can define delta/theta/vega in one sentence each [ ] decay table completed all 5 days [ ] both trades per plan [ ] quiz ≥70%.

---

## Week 3 — First defined-risk income trades (the real curriculum begins)

**Study:** strategy chapters (covered call, protective put, bull-put spread, bear-call spread).

| Day | Market window | Evening |
|---|---|---|
| Mon | **Trade 4 (paper): Bull Put Spread on Nifty monthly.** Sell 24,700 PE, buy 24,500 PE (both monthly). Net credit example: sell @ ₹120 (₹7,800) − buy @ ₹70 (₹4,550) = ₹3,250 credit. Max loss = (200×65) − 3,250 = ₹9,750 ✔ under cap. Margin blocked (simulated): far less than naked put — note the number Sensibull shows. | Journal Trade 4 with full math |
| Tue | 13:00: note spread value vs entry. No action. | Covered call chapter + plan Trade 5 |
| Wed | **Trade 5 (paper): Covered call on a stock you own.** Example: own 550 HDFC Bank shares (₹10L notional at ₹1,800). Sell 1 lot HDFC Bank monthly CE strike ~+4% (e.g., 1,880 @ ₹25 → ₹13,750 credit, lot 550). This is *your* end-goal strategy — paper it thoroughly. | Journal + note physical-settlement logic (you own shares, so ITM call = you deliver shares you have) |
| Thu | 13:00: check both spreads' MTM. If bull put spread hits −50% of credit (loss ≈ ₹1,625), plan exit for Friday 9:25. | Management chapter + write exit instructions |
| Fri | Execute exits per plan (or hold if within rules). | Full journal review + Weekly Review. |

**Week 3 exit checklist:** [ ] both trades have max profit/loss/breakeven written pre-entry [ ] can explain why spread margin < naked margin [ ] managed (not abandoned) one losing position per plan [ ] quiz ≥70%.

---

## Week 4 — Management, scaling decisions, go/no-go data

**Study:** position management, taxation, costs. Trades: repeat Week 3's two strategies
but with **half position size**, plus one deliberate "stress" exercise.

| Day | Market window | Evening |
|---|---|---|
| Mon | **Trade 6:** Repeat bull put spread (half size). **Trade 7:** Repeat covered call (or roll last week's if assignment logic clean). | Journal + tax chapter notes (F&O = business income; advance tax basics) |
| Tue | 13:00 routine check + log IV level on Sensibull (before vs after any news). | Volatility chapter recap |
| Wed | **Stress exercise:** manually write down what you'd do if Nifty gapped −2% tomorrow with your spread on. Compute the loss. *Then* actually place that hypothetical exit order tomorrow if the gap happens (it usually won't — the point is you now have a plan). | Journal the plan |
| Thu | Routine check; exits per plan. | Re-read Guide 01 §7 (costs) & §10 (mistakes); self-audit against your Mistake Counter |
| Fri | Close anything expiring; screenshot/final MTM. | **Grand review** → fill the scoring table below → go/no-go draft |

**Week 4 scoring table (fill honestly):**

| Metric | Your number | Target |
|---|---|---|
| Total paper trades completed | __ | 6–8 |
| Followed pre-planned exit % | __% | ≥ 80% |
| Trades with full journal entry | __% | 100% |
| Net P&L after simulated costs | ₹__ | Not the key metric — but log it |
| Biggest single loss (vs cap ₹10,000) | ₹__ | Never exceeded cap |
| Mistake Counter total | __ | ≤ 3 |

**Go-live gate (detailed in Guide 06):** all targets hit AND both exit checklists from
Weeks 1–3 passed → you may start Guide 06. Anything less → repeat Week 4 (or the weak
week) with fresh trades. The market will still be there next month.

---

## If you miss days (you will — job, life)

- Missed market window? Nothing breaks: place nothing; continue evening study. The plan
  heals because decisions are made evenings anyway.
- Missed 2+ days? Don't "catch up" with bigger trades. Resume at the last completed step.
- On vacation/leave? Just extend the week. There is no expiry on your learning.

*All premium/margin numbers are illustrative at Nifty ≈ 25,000, lot 65; recalculate with
live chain values on the day you trade.*
