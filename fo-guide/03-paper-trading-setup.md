# Guide 03 — Paper Trading Setup (Zerodha User Edition)

> Time to set up: ~30–45 min, one evening. Do this BEFORE Week 1 of the curriculum.

---

## 1. What paper trading will and won't teach you (read this honestly)

**It WILL teach you:** option chain reading, order types, strategy construction, Greeks
behaviour, premium decay in real time, discipline of journaling, strategy P&L patterns.

**It WON'T teach you:** fear when ₹10,000 of *real* money is on the line, slippage
(your virtual order fills at the price you see; real orders may not), margin rejection
errors, expiry-day chaos with real exposure, and the urge to overtrade.

That's why live trading (Guide 06) starts *small* even after 4 successful paper weeks.

---

## 2. Primary setup: Sensibull (free for Zerodha users)

Sensibull is Zerodha's official options platform partner — free tier covers option chain,
strategy builder, and virtual trading. This is your main simulator.

### Step-by-step (one evening)

1. **Log in:** Go to `web.sensibull.com` → Login → choose **Zerodha** → sign in with your
   Kite credentials. (Or from Kite web: apps → Sensibull.)
2. **Find virtual trading:** In Sensibull, open the **Virtual Trading / Draft Portfolio**
   section (may appear as "Draft Portfolios" or "Paper Trading" in the menu/app).
3. **Create your paper account:**
   - Virtual capital: **₹5,00,000** (see §4 for why this number).
   - Name it "FO-Training-R1" so you never confuse it with anything real.
4. **Learn the three screens you'll live in:**
   - **Option chain:** Nifty → current expiry. Identify: spot, ATM strike, OTM/ITM,
     bid-ask spread, volume/OI. (Guide 01 §3–§8 vocabulary applies here.)
   - **Strategy builder:** pick a strategy (e.g., bull put spread) → see max profit,
     max loss, breakeven, margin, and Greeks *before* placing. This preview is your
     pre-flight checklist for every paper trade.
   - **Positions page:** track open virtual positions, MTM, and expiry behaviour.
5. **Place one throwaway trade** (e.g., buy 1 lot Nifty ATM CE) just to learn the flow.
   Then close it. You're not trading yet — you're learning the buttons.

### Sensibull settings that matter
- Turn on **Greeks display** (delta/theta columns) in the option chain.
- Set Nifty as default underlying; add Bank Nifty and 2–3 stocks you own as watchlist.
- Explore the **free video course** tab (Guide 02) — same login works.

> If the UI has changed: search "virtual trading" inside Sensibull's help, or see their
> YouTube tutorial "Sensibull Virtual Trading for New Option Traders" (Booming Bulls
> video, ~15 min, shows the full flow).

---

## 3. Backup simulators (use if Sensibull feels limiting)

| Platform | Strengths | Watch-outs | Link |
|---|---|---|---|
| **Neostox** | Virtual money F&O sim with real-time NSE data; margin simulation; good for stock options too | Ads on free tier; fills are still idealized | neostox.com |
| **TradingView Paper Trading** | Best-in-class charts; simulate entries on charts | Generic broker sim — not India-margin aware; use for *chart skill*, not margin | tradingview.com |
| **StockGro / broker sims** | Mobile-first practice | Social/feed features can distract; ignore them | — |

**Recommended combo for you:** Sensibull (primary, margin+Greeks aware) +
TradingView (evening chart study). Don't run three sims — one journal, one primary sim.

---

## 4. Choose your paper capital — and size like it's real

Your live capital is undecided, so paper trade with a **realistic envelope**, not fantasy
millions. Use **₹5,00,000 notional**, but with these self-imposed caps:

- Never risk more than **2% of paper capital (₹10,000)** max loss on a single idea.
- Max **2 open positions** at a time in Weeks 1–3 (3 in Week 4 max).
- One "experiment slot" per week for a strategy you just learned; everything else repeats
  the previous week's strategy so you get repetition data.

Why this matters: if you paper trade with ₹1 crore, you'll learn nothing transferable —
your real decisions will happen at ₹5 lakh scale. Simulate the scale you'll actually face.

---

## 5. Set up your journal before your first trade

1. Copy the template in `07-trade-journal.md` into a Google Sheet (or use it as-is).
2. Create 4 tabs: **Trade Log · Daily Notes · Weekly Review · Mistake Counter**.
3. Pre-fill your rules at the top of Trade Log (max loss/trade, max positions, allowed
   strategies this week — from §4 and Guide 04).
4. Every virtual order gets a row *the same evening* — with entry reason, max profit/loss,
   and planned exit. No journal entry = the trade didn't happen (it goes to Mistake Counter).

---

## 6. Your pre-Week-1 checklist

- [ ] Sensibull login working via Zerodha; virtual portfolio "FO-Training-R1" created (₹5L)
- [ ] Greeks visible in option chain
- [ ] Watchlist: Nifty, Bank Nifty, 2–3 stocks you actually own
- [ ] One test trade placed and closed
- [ ] Journal sheet created with rules header
- [ ] TradingView account (optional, free) for chart study
- [ ] Calendar blocked: 45–50 min evening study + 10–15 min mid-day glance
- [ ] Read Guide 04 fully so Week 1 has no surprises

Once all boxes are ticked → start Guide 04's Week 1, Day 1 on the next trading day.

*Sources: Sensibull (web.sensibull.com — free for Zerodha customers per Zerodha z-connect
announcement), Neostox, TradingView paper trading docs (checked Sep 2026). UI labels may
vary by version — use in-app search if a screen isn't where described.*
