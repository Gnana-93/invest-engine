# 🚀 Going Live — Step-by-Step (from a fresh Windows PC)

Follow top to bottom. Nothing here needs money. Total time: ~30 minutes.

> After finishing, the engine runs itself at **02:45 IST every night** and the
> report arrives on Telegram before your morning. You never touch it again
> unless you want to.

---

## PART 1 — Install Git on your PC (10 min)

Git does two jobs here: it uploads your code to GitHub, and it installs
**Git Bash** (the terminal needed to run/test the engine locally).

1. Download: **https://git-scm.com/download/win** (file: `Git-...-64-bit.exe`).
2. Run the installer. Click **Next** through every screen — the defaults are
   all correct. The two screens below are pre-configured right already:
   - "Adjusting your PATH environment" → `Git from the command line and also from 3rd-party software`
   - "Choosing the default editor" → anything is fine
3. Click **Install**, then **Finish**.
4. Verify: press `Win` key → type **Git Bash** → open it → type:

   ```bash
   git --version
   python --version
   ```

   - `git --version` must print something like `git version 2.4x`.
   - If `python` is missing, install it: https://www.python.org/downloads/
     → run installer → **tick "Add python.exe to PATH"** → Next → Finish.
     Then **close and reopen Git Bash**.

> 💡 Bonus: once Git Bash exists, the AI assistant can run the engine's
> selftest on your machine in future sessions (`python run.py selftest`).

## PART 2 — Tell Git who you are (1 min, once)

In Git Bash:

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Use the same email you will register on GitHub with.

## PART 3 — Create the GitHub repo (5 min)

1. Go to **https://github.com** → **Sign up** (free) → verify email.
2. After login, click the **+** (top-right) → **New repository**.
3. Fill in exactly:
   - Repository name: `invest-engine` (any name works)
   - Visibility: **Public** ← mandatory (public = free scheduled runs;
     private repos need a paid plan for schedules)
   - Do **NOT** tick "Add a README" (the folder already has one)
4. Click **Create repository**. Leave this tab open.

## PART 4 — Push the project from your PC (5 min)

The folder to upload is the one that **contains** `invest-guide/`,
`fo-guide/` and `.github/` (the `.github` folder holds the nightly job).

In Git Bash (adjust the path to where your project folder actually is):

```bash
cd /c/path/to/your/project        # e.g. cd /c/Users/GNANASEKAR/projects/myrepo
ls                                # you must see: invest-guide  fo-guide  .github
```

Then run these five commands one by one:

```bash
git init
git add .
git commit -m "nightly investment engine — first version"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/invest-engine.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username (shown in the open tab).

- **Login popup:** on first push a GitHub sign-in window appears → choose
  "Sign in with your browser" → authorize. That's it (Windows stores it).
- If instead it asks for a password on the terminal: GitHub no longer accepts
  account passwords. Create a token: GitHub → top-right profile picture →
  **Settings → Developer settings → Personal access tokens → Tokens
  (classic)** → *Generate new token (classic)* → tick the **repo** checkbox →
  copy the token → paste it as the password.
- If `.github` was hidden in `ls`, run `ls -a` (dot-folders are hidden by
  default) — `git add .` includes it regardless.

**Verify the upload:** refresh the GitHub tab — you should see
`invest-guide/`, `fo-guide/`, and a folder `.github/workflows/` containing
`nightly.yml`.

## PART 5 — Create the Telegram bot (5 min)

1. In Telegram, search **@BotFather** → open → send `/newbot`.
2. Give it a name (e.g. `Nightly Stock Brief`) and a username ending in `bot`
   (e.g. `gnana_stocks_bot`).
3. BotFather replies with a **token** like
   `7123456789:AAH8x...`. Copy it. This is `TELEGRAM_BOT_TOKEN`.
4. **Start a chat with your new bot**: open it from the BotFather message and
   send any message (just "hi"). This step is required, or step 5 finds nothing.
5. Get your chat ID: open this URL in a browser (paste your token):

   ```
   https://api.telegram.org/bot7123456789:AAH8x.../getUpdates
   ```

   In the JSON, find `"chat":{"id": 123456789` — that number is
   `TELEGRAM_CHAT_ID`. (If `getUpdates` shows empty, send the bot another
   message and refresh.)

## PART 6 — Add the secrets to GitHub (2 min)

On your repo page:

**Settings → Secrets and variables → Actions → New repository secret** (green
button) — do this twice:

| Name | Value |
|---|---|
| `TELEGRAM_BOT_TOKEN` | the token from BotFather |
| `TELEGRAM_CHAT_ID` | the chat id number |

(Names must match exactly, including capitals/underscores.)

## PART 7 — First run & verification (3 min)

1. Repo page → **Actions** tab → if asked, click **"I understand my workflows,
   go ahead and enable them"**.
2. Left sidebar → **nightly-investment-brief** → right side →
   **Run workflow** → green **Run workflow** button.
3. The run appears in the list. Click it to watch live. It takes ~10–25 min
   (fetching ~500 stock prices politely). Two steps must both get ✅:
   - **Selftest (offline gate)** — all engine assertions
   - **Nightly pipeline** — the real data run
4. When done, verify all three:
   - ✅ Telegram received your first brief
   - ✅ A new commit "nightly brief 2026-09-16" appeared in the repo
   - ✅ `invest-guide/index.html` updated (open it via the repo, or
     `https://htmlpreview.github.io/?https://github.com/YOUR-USERNAME/invest-engine/blob/main/invest-guide/index.html`)

From tonight on, it runs itself at 02:45 IST. Nothing more to do.

---

## Troubleshooting

| Symptom | Cause → Fix |
|---|---|
| Selftest step red | Click the failed step, read the last lines (`FAIL name`) → note which assertion → tell the assistant the exact FAIL line |
| Nightly step red, log shows `FATAL: universe empty` | NSE CSV + seed both failed that night (network). Re-run once; it recovers |
| No Telegram message but run is green | Secrets missing/misspelled → re-check Part 6 names; also make sure you messaged your bot once (Part 5.4) |
| Workflow never runs at night | Actions disabled, or repo was made **private** (schedules need paid plan) → check Settings |
| Run skipped / delayed by hours | Normal: GitHub cron is best-effort, can lag 15–60 min. Report still arrives in the morning |
| `git push` says `rejected` | The online repo was created with a README → run `git pull origin main --allow-unrelated-histories` then `git push` again |
| Yahoo/NSE errors in log but report still made | Fine by design — fetchers degrade, the report's data-quality note says what was stale |

## Daily life after setup

- **Morning:** read Telegram. That's the whole routine.
- **Track buys:** add symbols to `invest-guide/data/watchlist.json`
  (format shown in README) — they get exit/tax monitoring every night.
- **Fix anything:** ask the assistant in a chat session; the progress map
  (`invest-guide/PROGRESS.md`) lets any session resume instantly.
