# Guide 05 — Income Strategy Playbook (Your End-Goal Strategies)

> Your profile: own stocks + MFs, want long-run income, 10–15 min/day.
> Every strategy here is **defined-risk or asset-backed**. No naked selling, ever, in this guide.
> Numbers illustrative at **Nifty ≈ 25,000 (lot 65)** and HDFC Bank ≈ ₹1,800 (lot 550). Recompute live.

---

## 0. Reality calibration first

- SEBI Aug-2026 study: **88% of individual F&O traders lost money in FY26**; 93% across FY22–24 (₹1.8 lakh crore aggregate). The survivors share two traits: defined risk + position sizing. This guide hard-codes both.
- **Realistic income expectation:** well-run covered-call/spread programs historically target roughly **1–2% per month on deployed capital before costs and tax** — with real months of zero or negative return. Anyone promising more is selling something.
- **Tax:** F&O income = **non-speculative business income** (ITR-3, audit rules may apply at size). Premium income and costs both count.MF dividends vs this differ — plan with a CA once live.

---

## 1. Strategy A — Covered Call (on stocks you already own)

**When:** neutral-to-mildly-bullish view on a stock you're happy to hold.
**Mechanic:** you own shares (in lot multiples) → sell calls against them → keep premium.

### Worked example (paper this in Week 3, Trade 5)
- You own **550 HDFC Bank shares** (₹9.9 lakh). Lot size = 550 → exactly 1 lot ✔.
- Stock at ₹1,800. Sell **1,870 CE (monthly, ~4% OTM) @ ₹25** → credit = 25 × 550 = **₹13,750**.
- **Outcome map at expiry:**
  - Stock ≤ 1,870 → call expires worthless → you keep ₹13,750 (~1.4%/month on holding) and still own shares.
  - Stock = 1,900 → shares called away at 1,870: effective sale 1,870 + 25 = ₹1,895 (+5.3% incl. premium) — you sold at your planned price, not a loss.
  - Stock crashes to 1,600 → premium cushions only ₹25/share; you bear the fall (that's stock risk, not options risk).
- **Margin note:** short call against shares gets margin offset only if shares are pledged/collateralised at the broker. Unpledged shares → you still pay option margin (~₹1–1.5L). Zerodha margin calculator shows both cases. Alternatively use the **covered call identification** in Sensibull, which tracks stock + option as one position.
- **Physical settlement = safe here:** if ITM, you deliver shares you actually own. This is the *one* stock-option strategy a beginner with holdings can do safely.

### Rules
1. Never write calls before **results, budget, RBI policy** dates on that stock — premium is high because risk is high.
2. Strike ≥ +3–5% above cost basis you're content to sell at. Writing calls = agreeing to sell.
3. If stock runs hard through your strike mid-month: don't panic-buy-back by default. Pre-decide (journal): roll up-and-out vs let assignment happen.
4. Skip writing when your honest view is strongly bullish — upside forgone is a real cost.

---

## 2. Strategy B — Cash-Secured Put, Indian version

**When:** you'd *love* to buy a stock/index cheaper.
**Mechanic (textbook):** sell put at a strike where you'd happily buy; keep the "cash" aside to buy if assigned.

### India reality check
- No broker automatically "reserves" your cash — you post SPAN margin (~₹1.2–1.5L for 1 Nifty put; similar logic for stock puts) *and* you must keep the notional cash liquid on your own. **Stock put assignment = you must take delivery** (physical settlement) → keep the full cash ready or trade index only.
- Because full margin + full cash is capital-hungry, retail income traders usually substitute **Strategy C** (spread) for the same view at a fraction of the capital. Learn CSP mechanics, then usually execute as C.

### Index CSP example (if you do run it)
- Nifty 25,000. Sell **24,500 PE (monthly) @ ₹130** → credit ₹8,450. Margin ≈ ₹1.3–1.5L + keep ₹8L+ liquid as the "buy fund".
- If Nifty stays > 24,500 → keep ₹8,450 (~0.9% on the cash you hold, monthly).
- If Nifty falls to 24,300 → assigned long index-equivalent at effective 24,370 — that was the plan.
- Danger: you now hold a falling index. CSP is **not** a free-income machine; it's a paid limit-order.

---

## 3. Strategy C — Bull Put Spread (your capital-efficient workhorse)

**When:** neutral-to-mildly-bullish. **Mechanic:** sell higher put, buy lower put, same expiry.

### Worked example (paper this in Week 3, Trade 4; repeat Week 4 half-size)
- Nifty 25,000, monthly expiry.
- Sell 24,700 PE @ ₹120 → receive ₹7,800.
- Buy 24,500 PE @ ₹70 → pay ₹4,550.
- **Net credit = ₹3,250.** Margin ≈ ₹25–35k (spread margin — far less than naked's ₹1.3L+).
- **Max profit:** ₹3,250 (if Nifty ≥ 24,700 at expiry).
- **Max loss:** (200 × 65) − 3,250 = **₹9,750** (if Nifty ≤ 24,500) ✔ under your ₹10k cap.
- **Breakeven:** 24,700 − 3,250/65 = **24,650** (≈1.4% cushion).
- Risk:reward = 3:1 against you — which is why **win rate must be high**: this trade needs discipline in *entry selection* (only when trend/IV support it) and *early exit* (see management).

### Management rules (write these before entry)
- Exit (buy back) when spread value falls to **~30–35% of credit** → book ~65–70% of max profit early instead of waiting weeks for the last 30% with gamma risk.
- Exit **immediately-ish** if Nifty closes below short strike (24,700) — don't wait for max loss. Losing ₹3–4k beats losing ₹9,750.
- Never hold short legs into **expiry day** (+2% ELM, calendar-spread benefit removed — Guide 01 §6). Close spreads by expiry-eve.

---

## 4. Strategy D — Bear Call Spread (the mirror)

**When:** neutral-to-mildly-bearish or after big rallies.
- Sell 25,300 CE @ ₹100 (₹6,500), buy 25,500 CE @ ₹55 (₹3,575) → credit ₹2,925.
- Max loss = (200 × 65) − 2,925 = ₹10,075 → trim width to 150 points to stay under ₹10k cap.
- Same management as C, mirrored. C + D alternating = poor man's market-neutral income (graduation path, month 2+).

---

## 5. Strategy E — Protecting your portfolio (hedge, not income — but yours matters)

You have 5 years of stocks/MFs. When you eventually trade live, consider pairing income trades with protection:

- **Protective put:** buy 1 lot Nifty PE (~2–3% OTM, monthly) ≈ ₹150–200 × 65 = ₹10–13k per month — expensive insurance; typically only before known risk events.
- **Collar:** own stocks + sell OTM call + buy OTM put with the call's premium → near-zero-cost protection. The covered call you already learned becomes the funding leg.
- Paper-trade a collar once in month 2 — it converts "income strategies" into "income + insurance", which matches a 5-year investor's psychology far better.

---

## 6. Choosing on any given day (decision card)

| Your view | Capital light? | Trade |
|---|---|---|
| Own stock, neutral-mild bull | yes | Covered call (A) |
| Want to buy X cheaper | n/a | CSP (B) — usually execute as C |
| Neutral-mild bull, small capital | yes | **Bull put spread (C)** |
| Neutral-mild bear / post-rally | yes | Bear call spread (D) |
| Scared about portfolio | yes | Collar (E) |
| Strongly bullish / bearish | — | **No income trade.** Directional views = long options (Guide 04 Week 1–2 style), small |

**Event filter (always):** RBI policy, Union Budget, election results, major earnings weeks → halve size or skip. High IV *looks* attractive to sellers; that's exactly when gap risk eats months of premium.

---

## 7. Monthly income math — honest version (example, not promise)

Deployable: ₹10L (₹5L pledged collateral + ₹5L cash) in month 3+ of live trading:
- 2 × bull put spreads (₹3,000 credit each, exit at 65% → ~₹3,900 booked)
- 1 covered call on ₹10L stock (₹13,750, keep full if uncalled)
- Gross ≈ ₹17,600; costs ≈ ₹600–800; taxes per slab later.
- **On months when spreads fail** (Nifty −3% weeks happen ~2–4×/year): spread losses −₹6–10k can wipe the month. That's the deal. **Journal everything; judge on quarters, not weeks.**

*Sources: SEBI press release Sep-2024 & Aug-2026 studies, NSE contract specs, Zerodha margin/charges pages, OIC (optionseducation.org) strategy definitions. Illustrative premiums only.*
