"""
engine/notify.py — Telegram delivery.
Secrets: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID in repo Settings→Secrets.
Locally unset → print to console instead (never crashes the pipeline).
"""

from __future__ import annotations

import json
import os
import urllib.request

API = "https://api.telegram.org/bot{token}/sendMessage"


def send(cfg: dict, text: str) -> bool:
    token = os.environ.get(cfg["telegram"]["secret_env"], "")
    chat = os.environ.get(cfg["telegram"]["chat_env"], "")
    if not token or not chat:
        print("[notify] Telegram secrets unset — message follows:\n" + text)
        return False
    limit = cfg["telegram"]["max_message_chars"]
    chunks = [text[i:i + limit] for i in range(0, len(text), limit)]
    ok = True
    for chunk in chunks:
        payload = json.dumps({"chat_id": chat, "text": chunk,
                              "parse_mode": "HTML", "disable_web_page_preview": True}).encode()
        try:
            req = urllib.request.Request(
                API.format(token=token), data=payload,
                headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status != 200:
                    ok = False
        except Exception as exc:
            print(f"[notify] Telegram failed: {exc}")
            ok = False
    return ok
