# Scenario Decision Analyzer — Build Log

> Living document. Updated at every milestone. Last updated: 2026-09-29 — **goResults navigation bug fixed, browser-verified (commit 14c3309).**

## What this is
A zero-cost, client-side web app to analyze big life decisions via scenario analysis and Expected Value (EV). No backend, no accounts, no API keys. Data stays in your browser (localStorage, key `decision-storage`).

## Decisions locked with owner
| Decision | Choice |
|---|---|
| Location | `decision-analyzer/` inside this repo |
| Tech | Next.js (App Router) + TypeScript strict + Tailwind v4 + shadcn/ui |
| Scope v1 | Core flow: Landing → Wizard → Results (charts/tabs/insights) + validation + autosave |
| Export | Copy to Clipboard + Start New (PDF skipped in v1) |
| Deploy | Zero-cost: Vercel Hobby, clean `npm run build` passes |
| UX requirements | Mobile-first; works on phone + laptop; less scrolling; less visual fatigue |

## Steps & status — ALL 12 STEPS COMPLETE ✅
| # | Step | Status |
|---|------|--------|
| 1 | Scaffold Next.js app (create-next-app, TS, Tailwind, App Router) | ✅ Done |
| 2 | Install deps: zustand, recharts, react-hook-form, zod, lucide-react | ✅ Done |
| 3 | Init shadcn/ui + add UI components | ✅ Done |
| 4 | Foundation: types, calculations, validation (zod) | ✅ Done |
| 5 | Templates file: 4 decision templates (marriage, career, house, business) | ✅ Done |
| 6 | Zustand store with localStorage persistence (autosave) | ✅ Done |
| 7 | Landing page (Hero, How It Works, Templates, Features, Footer) | ✅ Done |
| 8 | Wizard: template select → edit decision/options/scenarios (sliders, probability validation, normalize) | ✅ Done |
| 9 | Results: EV bar chart, recommendation, 3 tabs (Scenario Breakdown / Risk / Comparison), insights, copy-to-clipboard | ✅ Done |
| 10 | Mobile & fatigue pass: sticky nav, tabs/accordions, 44px touch targets | ✅ Done |
| 11 | Verify: `tsc --noEmit` → **0 errors**; `npm run build` → **passes** (verified 2026-09-29) | ✅ Done |
| 12 | README + zero-cost deploy note (Vercel Hobby, 3 steps) | ✅ Done |

## What was verified on 2026-09-29
- `npx tsc --noEmit` — exits 0, no type errors
- `npm run build` — production build succeeds (`.next/BUILD_ID` present)
- Store persists via zustand `persist` middleware → localStorage key `decision-storage`

## Bug fix + verification session — 2026-09-29 (commit 14c3309)

**Bug:** `components/wizard/DecisionEditor.tsx` → `goResults()` called `calculateExpectedValues()` + `setStep(2)` but never navigated, so the **Calculate Results button did nothing**. Caught by owner testing (no CI existed to catch it).

**Fix (14c3309, 1 file, +3 lines):** added `useRouter` import, `const router = useRouter()`, `router.push("/results")`.

**Checks run — all pass, evidence is exit codes:**
| Check | Command | Result |
|---|---|---|
| Typecheck | `npx tsc --noEmit` | exit 0, no errors |
| Build | `npm run build` | pass — Next.js 16.3.7 (Turbopack), 6 static pages |
| Cleanup | `rm -rf e2e-tmp/` | stale puppeteer scaffolding deleted (was never git-tracked) |
| Regression test | throwaway puppeteer-core script vs system Chrome on `next dev --port 3210` | **19/19 assertions PASS, exit 0** |

**Browser test coverage (19 assertions):** landing renders → template selector → Start Custom Decision → all 6 accordion triggers expanded via `aria-expanded` (sliders hidden until expanded) → 12 `[role="slider"]` thumbs appear, 6 with `aria-label="Scenario probability"` → first probability = 30 → ArrowLeft ×10 → 20, banner "Probabilities sum to 90%", **Calculate Results correctly disabled** → "Normalize to 100%" → re-proportioned to 22.2/55.6/22.2, banner green → **Calculate Results navigates to `/results`** (URL, title, Breakdown tab verified) → state survives page reload (localStorage persist) → no console/page errors.

> Note: the test script was intentionally throwaway (deleted after the run; driver installed in a temp dir outside the repo). It is **not** yet a permanent part of the project — making it a permanent Playwright test is a proposed follow-up.

**Deploy status: not live anywhere.** `origin` = github.com/Gnana-93/invest-engine, but `main` is ahead 2 commits (31aeca6 app + 14c3309 fix) — **unpushed**. No Vercel/Netlify config exists in the repo. Deploy remains the owner's manual step (checklist at bottom).

## Owner's manual testing checklist
1. Open on phone-sized window — layout stacks, no horizontal scroll
2. Landing → pick a template (marriage / career / house / business) → wizard loads pre-filled
3. Edit probabilities with sliders; try sum ≠ 100% → warning + Normalize button
4. Calculate Results → chart renders, best option highlighted
5. Check 3 tabs: Breakdown / Risk / Compare
6. Copy to Clipboard → paste into a text file
7. Refresh page mid-edit → autosave restores state
8. Start New Analysis → resets everything

## How to run (local)
```bash
cd decision-analyzer
npm install   # already done during build
npm run dev   # http://localhost:3000
```

## Deploy (zero cost, ~5 min, owner does this at the end)

> Status 2026-09-29: **not started** — repo not yet pushed; no live URL exists.
1. Push this repo to GitHub
2. vercel.com → Sign up free → "Add New Project" → import the repo → Framework auto-detected → Deploy
3. Done — free `*.vercel.app` URL, auto-redeploys on every git push
