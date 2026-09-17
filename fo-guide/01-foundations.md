# Guide 01 — F&O Foundations (Absolute Beginner → Ready to Paper Trade)

> Read time: ~45–60 min. Come back to the cheat sheet at the end whenever confused.
> All numbers use **current 2026 contract specs** — always re-verify before live trading (see §12).

---

## 1. What are Futures & Options?

Both are **derivatives**: contracts whose value is *derived* from an underlying asset
(Nifty index, a stock, etc.). You never buy the asset itself — you trade a contract about it.

| | **Futures** | **Options** |
|---|---|---|
| What you get | An *obligation* to buy/sell at a fixed price on expiry | A *right* (buyer) or *obligation* (seller) |
| Profit potential | Unlimited both ways | Buyer: unlimited (call) / large (put). Seller: limited to premium |
| Loss potential | Unlimited both ways | Buyer: only premium paid. **Seller: can be huge** |
| Capital needed | Margin (~10–15% of contract value) | Buyer: premium only. Seller: margin (~1.5–4 lakh per index lot) |
| Best for beginners | ❌ Avoid entirely for now | ✅ Defined-risk strategies (as buyer or in spreads) |

**Your starting rule:** You will not touch naked futures or naked option selling for a long
time. Everything in this course is built on **defined-risk** positions.

---

## 2. Calls and Puts — with Indian examples

Throughout, assume **Nifty spot = 25,000** (illustrative). Nifty lot size = **65**, so
one lot controls ₹25,000 × 65 = **₹16,25,000** of index value.

### Call option = right to BUY at strike
- **Buy Nifty 25,200 CE at ₹120** → you pay ₹120 × 65 = **₹7,800**.
  - If Nifty rises to 25,500, the option is worth ~₹300 → ₹19,500. Profit ≈ ₹11,700.
  - If Nifty stays below 25,200 at expiry, option expires worthless. You lose ₹7,800. That's the max loss.
- **Sell (write) the same call** → you *receive* ₹7,800, but if Nifty rockets to 26,000 you
  must pay the difference. Losses are theoretically unlimited.

### Put option = right to SELL at strike
- **Buy Nifty 24,800 PE at ₹110** → pay ₹7,150.
  - If Nifty crashes to 24,000, the put is worth ~₹800 → ₹52,000. Big profit.
  - If Nifty stays above 24,800, max loss = ₹7,150.
- This is exactly how you'd **hedge a stock portfolio** (Guide 05).

**Mnemonic:** CE = Charge up (bullish). PE = Price exits (bearish).

---

## 3. Moneyness: ITM / ATM / OTM

For Nifty at 25,000:

| Strike (CE) | Type | Premium (typical) | Why |
|---|---|---|---|
| 24,500 | ITM (In The Money) | ₹650+ | Has ₹500 intrinsic value already |
| 24,950–25,050 | ATM (At The Money) | ₹150–180 | Pure time value, highest theta burn |
| 25,500 | OTM (Out of The Money) | ₹40–60 | Needs a big move to be worth anything |

For puts it flips: strikes **below** spot are ITM.

- **Intrinsic value** (CE) = max(0, Spot − Strike). Real money, never negative.
- **Time value** = Premium − Intrinsic. This is what option *sellers* collect and what
  *melts to zero* as expiry approaches (**theta decay**).

> **Income-strategy core idea:** sellers earn time value; buyers pay it. Weekly ATM options
> lose time value fastest in the last 2–3 days before expiry. This is the engine behind
> covered calls and credit spreads you'll learn in Guide 05.

---

## 4. The four building-block positions

| Position | View | Max profit | Max loss | Capital |
|---|---|---|---|---|
| Long Call | Bullish | Unlimited | Premium paid | Premium only |
| Long Put | Bearish | Large (till zero) | Premium paid | Premium only |
| Short Call | Bearish/neutral | Premium received | **Unlimited** | Big margin |
| Short Put | Bullish/neutral | Premium received | **Large** (strike×65 − premium) | Big margin |

Beginner-safe combos (from these four): **spreads** — buy one option, sell another, so the
short's risk is capped by the long. Covered call = short call backed by shares you own.

---

## 5. The Greeks — plain-language survival kit

You don't need to *compute* Greeks; Sensibull shows them. You need to *understand* them:

- **Delta (Δ):** How much option price moves per 1 point of Nifty. Nifty 25,100 CE at ₹160
  with delta 0.50 → Nifty rises 100 points → premium ≈ 160 + (100×0.50) = ₹210.
  Delta also ≈ probability of expiring ITM (rough rule).
- **Theta (Θ):** Daily time-value decay. If theta = −45 and you *own* the option, you lose
  ~₹45×65 = ₹2,925 per day *if nothing else changes*. If you *sold* it, that's your daily
  income — until the market moves against you.
- **Vega:** Sensitivity to implied volatility (IV). IV spikes on fear (elections, budgets,
  crashes). Buying options when IV is high = buying expensive insurance. Sellers love high IV
  but get hurt when IV spikes *after* they sell.
- **Gamma:** How fast delta changes. Highest for ATM options near expiry — why expiry-day
  short options are dangerous (and why SEBI added the extra expiry-day margin).

**Beginner intuition to carry forward:** *Option buyers fight theta; option sellers fight
movement.* Spreads try to make both risks small.

---

## 6. Margins — what money you actually need

- **Buying options:** pay full premium. A ₹150 Nifty option = ₹9,750/lot. Done.
- **Selling options:** broker blocks margin = **SPAN + Exposure** (roughly 12–18% of
  notional). Selling one Nifty lot can block **₹1.5–2.5 lakh** depending on strike/expiry.
- **Spread margin benefit:** if you buy and sell together (a spread), margin is much lower
  than the short leg alone — Sensibull/Kite show it when you place both legs.
- **Upfront premium rule (Feb 2025 onward):** premium must be in your account before the
  trade — you can't sell first and use the premium received.
- **Expiry-day rule (Nov 2024 onward):** short options carry an **extra 2% ELM on expiry
  day**; also the calendar-spread margin benefit was removed on expiry day. Practical
  meaning: don't hold short legs into expiry day unless your strategy accounts for it.
- **Peak margin:** intraday margin snapshots; you can't over-leverage intraday.

**Physical settlement warning:** stock options that expire ITM now settle in *shares*
(no cash). Selling calls on stocks without owning them, or short puts you can't take
delivery of, can create huge delivery obligations. As a beginner: stick to **index**
options, where settlement is always cash.

---

## 7. Costs — a real worked example

Zerodha (verify current rates at zerodha.com/charges; STT revised 1-Apr-2026):

You **buy 1 lot Nifty 25,200 CE @ ₹120 and sell @ ₹150** (65 qty):

| Charge | Amount (approx) |
|---|---|
| Brokerage | ₹20 + ₹20 = ₹40 |
| STT (0.1% sell-side premium → ₹9,750×0.001) | ~₹10 |
| Exchange txn charges + SEBI fees | ~₹7 |
| GST (18% on brokerage+txn) | ~₹8 |
| Stamp duty (0.003% buy side) | ~₹1 |
| **Total cost ≈ ₹66** on a gross profit of ₹30×65 = ₹1,950 | ~3.4% round trip |

Key lesson: costs bite hardest on *frequent small trades* and on *selling spreads where
net credit is small*. In paper trading, log every trade as if costs applied.

---

## 8. Expiry & liquidity structure you must know (2026)

| Index | Lot | Expiry | Notes |
|---|---|---|---|
| Nifty 50 (NSE) | 65 | **Weekly (Tue) + monthly** | Only NSE weekly product |
| Bank Nifty | 30 | Monthly only (last Tue) | No weeklies |
| FinNifty | 60 | Monthly only | |
| Midcap Nifty | 120 | Monthly only | |
| Sensex (BSE) | 20 | Weekly (Thu) + monthly | Smaller lot = smaller premium outgo |

- Holiday on expiry day → expiry shifts to **previous trading day**.
- Weekly expiries: cheap premiums, violent theta, beginner trap for naked selling.
- Monthly expiries: slower decay — friendlier for your 10–15 min/day routine.
- Liquidity is deep in Nifty weeklies and monthlies; check bid-ask spread before any trade
  (you'll practice this in paper trading).

---

## 9. How a position actually plays out (mini case study)

**Setup:** You own ₹10 lakh of HDFC Bank shares (relevant to covered calls later).
Today you're paper-trading index options instead.

**Trade (paper):** Buy 1 lot Nifty 25,200 CE @ ₹120 on 1-Sep, monthly expiry.
- Max risk: ₹7,800 (premium).
- 5-Sep: Nifty 25,380 → premium ₹260. Unrealized +₹9,100. Do you book or hold?
- 15-Sep: Nifty 25,450 → premium ₹310 but **theta now −60/day**: even if Nifty freezes,
  you lose ~₹3,900/lot per day.
- 23-Sep (expiry eve): Nifty 25,300 → premium ₹95. Delta did its job, theta ate the rest.

**The lesson:** direction was right all along, but *timing + theta* decided the P&L.
This exact experience, repeated in paper trades, is what Guide 04 makes you log.

---

## 10. Beginner mistakes this guide exists to prevent

1. Trading weekly options like a lottery ticket (near-zero knowledge + weekly expiry = 
   the exact profile SEBI's loss statistics are made of).
2. Naked selling "because theta always wins" — one gap-open can erase months of income.
3. Ignoring IV: buying expensive options before events, selling cheap ones in panic.
4. Over-sizing: one Nifty short lot margin (₹2 lakh) is not "small money".
5. Not logging trades — paper trading without a journal is just gambling with fake money.
6. Confusing stock-F&O settlement: stock options = physical delivery risk.

---

## 11. Self-check before Guide 02 (answer without looking)

1. You buy 1 lot Nifty 25,000 CE @ ₹100. What is your maximum possible loss? (₹6,500)
2. Nifty = 25,000. Which put strikes are ITM? (below 25,000)
3. Premium ₹180, intrinsic ₹120 → time value? (₹60 — this decays to zero by expiry)
4. Why is a spread safer than a naked short? (short leg's loss is capped by the long leg)
5. Why do sellers want expiry day margin rules to matter less? (position already closed 😄)

If you got 4/5, continue. If not, re-read §2–§5 — no shame, this is the hard 20%.

---

## 12. Verify-before-trading checklist (things that change!)

- [ ] Lot sizes: NSE circular / your broker's contract page (rebaselined Jan 2026; can change again)
- [ ] Expiry days: NSE/BSE circulars (NSE=Tue, BSE=Thu as of Sep 2026)
- [ ] Zerodha charges page: brokerage, STT (revised 1-Apr-2026), txn charges
- [ ] Margin requirements: Sensibull/Console margin calculator before EVERY sell order
- [ ] SEBI circulars for new rules (journalplus.co/regulations or Zerodha bulletin)

*Sources: NSE contract specifications (nseindia.com), NSE circular FAOP70616,
Zerodha charges/bulletins, SEBI Oct-2024 rationalisation measures, onetradejournal lot-size tables
(as of Sep 2026).*
