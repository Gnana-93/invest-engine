"""
engine/dashboard.py — regenerates index.html (self-contained, no CDN).
Reads data/last_report.json + knowledge_base.json; safe to open locally.
"""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def build(cfg: dict) -> None:
    last = {}
    p = ROOT / "data" / "last_report.json"
    if p.exists():
        try:
            last = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            last = {}
    kb = {}
    kp = ROOT / "data" / "knowledge_base.json"
    if kp.exists():
        try:
            kb = json.loads(kp.read_text(encoding="utf-8"))
        except Exception:
            kb = {}

    rows = _buy_rows(last.get("buy", [])) + _watch_rows(last.get("watch", []))
    alerts = "".join(
        f"<tr><td><b>{html.escape(a['level'])}</b></td><td>{html.escape(a['symbol'])}</td>"
        f"<td>{html.escape(a['msg'])}</td></tr>"
        for a in last.get("alerts", [])) or "<tr><td colspan=3><i>none tonight</i></td></tr>"

    _flat = []
    for _regime in ("spike", "trend", "result"):
        for _t, _st in (kb.get("signals", {}).get(_regime) or {}).items():
            _flat.append((_regime, _t, _st))
    _flat.sort(key=lambda x: -x[2]["n"])
    sig_rows = "".join(
        f"<tr><td>{html.escape(r + ':' + t)}</td><td>{st['n']}</td>"
        f"<td>{st['hit_rate']:.0%}"
        + (f" · cons {st['consistency']:.0%}" if st.get("consistency") is not None else "")
        + (f" · {st['fades']} faded" if st.get("fades") else "")
        + "</td></tr>"
        for r, t, st in _flat[:14]) \
        or "<tr><td colspan=3><i>learning in progress…</i></td></tr>"

    page = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Nightly Investment Brief</title><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{{font-family:system-ui,sans-serif;margin:24px;max-width:900px;background:#0d1117;color:#e6edf3}}
h1{{color:#58a6ff}} table{{border-collapse:collapse;width:100%;margin:12px 0}}
th,td{{border:1px solid #30363d;padding:8px;text-align:left}}
th{{background:#161b22}} .A{{color:#3fb950;font-weight:700}} .B{{color:#d29922;font-weight:700}}
.C,.D{{color:#f85149}} .muted{{color:#8b949e}} a{{color:#58a6ff}}
</style></head><body>
<h1>Nightly Investment Brief</h1>
<p class="muted">Date: {html.escape(str(last.get('date', 'n/a')))} · Rules-engine confidence: score 0-100 + learned hit-rates</p>
<h2>Buy ideas (A/B bands)</h2><table><tr><th>#</th><th>Stock</th><th>Score</th><th>Band</th><th>Strategies</th><th>Evidence</th></tr>{rows}</table>
<h2>Hold warnings / exits</h2><table><tr><th>Level</th><th>Stock</th><th>Why</th></tr>{alerts}</table>
<h2>Learned signals (direction-aware · spike/result: +5%/30d · trend: +15%/90d)</h2><table><tr><th>Signal</th><th>Events</th><th>Hit-rate</th></tr>{sig_rows}</table>
<p class="muted">KB events: {len(kb.get('events', []))} · Not investment advice.</p>
</body></html>"""
    (ROOT / "index.html").write_text(page, encoding="utf-8")


def _buy_rows(buys):
    out = []
    for i, s in enumerate(buys[:12], 1):
        out.append(f"<tr><td>{i}</td><td><b>{html.escape(s['symbol'])}</b></td>"
                   f"<td>{s['score']:.0f}</td><td class='{s['band']}'>{s['band']}</td>"
                   f"<td>{html.escape(', '.join(s['strategies'][:2]))}</td>"
                   f"<td>{s['parts']['evidence']:.0f}</td></tr>")
    return "".join(out) or "<tr><td colspan=6><i>none tonight — patience is a position</i></td></tr>"


def _watch_rows(watch):
    return "".join(
        f"<tr><td>{i + 13}</td><td>{html.escape(s['symbol'])}</td><td>{s['score']:.0f}</td>"
        f"<td class='{s['band']}'>{s['band']}</td><td>{html.escape(', '.join(s['strategies'][:1]))}</td>"
        f"<td>{s['parts']['evidence']:.0f}</td></tr>"
        for i, s in enumerate(watch[:6]))
