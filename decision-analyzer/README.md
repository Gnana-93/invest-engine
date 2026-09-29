# Scenario Decision Analyzer

Analyze big life decisions with scenario analysis and Expected Value (EV). A zero-cost, client-side web app: no backend, no accounts, no API keys. All data stays in your browser (localStorage autosave).

Built with Next.js (App Router), TypeScript strict, Tailwind v4, shadcn/ui, zustand, recharts, react-hook-form + zod, lucide-react.

## How it works

1. **Landing** — pick one of 4 pre-filled decision templates, or build your own:
   - Should I proceed with arranged marriage now or wait?
   - Should I change careers now?
   - Should I buy a house now?
   - Should I start my own business?
2. **Analyze (wizard)** — edit the decision title/description, compare 2–5 options, and give each option 2–8 scenarios. Every scenario has:
   - a **probability** (0–100%, sliders with validation — each option's probabilities should sum to 100%, with a one-click **Normalize** fix)
   - a **value** (−100 to +100 — how good/bad that outcome is for you)
   - an optional explanation
3. **Results** — the app computes each option's EV = Σ (probability × value):
   - EV comparison bar chart with the best option highlighted
   - 3 tabs: **Breakdown** (per-scenario contributions), **Risk** (best/worst case, upside, downside, volatility), **Compare** (side-by-side table)
   - Plain-language insights
   - **Copy to Clipboard** export, plus **Start New** to reset everything

Mid-edit autosave: refresh or close the tab and your work is restored (storage key `decision-storage`). Mobile-first layout designed for less scrolling and 44px touch targets.

## Getting started

```bash
npm install
npm run dev     # http://localhost:3000
```

Other scripts: `npm run build`, `npm run start`, `npm run lint`.

Type safety check: `npx tsc --noEmit` (passes with 0 errors).

## Deploy (zero cost, ~5 min)

The app is fully static/client-side, so any Next.js host works. Recommended: Vercel Hobby (free):

1. Push this repo to GitHub
2. [vercel.com](https://vercel.com) → Sign up free → **Add New Project** → import the repo → Framework auto-detected → Deploy
3. Done — free `*.vercel.app` URL, auto-redeploys on every git push

## Project structure

```
app/
  page.tsx           Landing page
  analyze/page.tsx   Wizard (template select → editor)
  results/page.tsx   Results (EV chart, tabs, insights, export)
components/
  landing/           Hero, HowItWorks, TemplatePreview, Features, Footer
  wizard/            TemplateSelector, DecisionEditor, sliders, validation UI
  results/           EVComparison, ScenarioTable, RiskAnalysis, ComparisonTable,
                     InsightsPanel, ExportButtons
lib/
  types.ts           Domain types (Decision, Option, Scenario)
  templates.ts       4 pre-filled decision templates
  calculations.ts    EV, risk profile, volatility, export text
  validation.ts      zod schemas + cross-field probability rules
  store.ts           zustand store with localStorage persistence
```
