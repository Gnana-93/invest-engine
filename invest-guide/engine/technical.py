"""
engine/technical.py — technical analysis overlay (v2.0).

Pure computation on the price series ALREADY fetched by engine/data.py
(Yahoo 400-bar cache) — zero new network calls, stdlib only.

Outputs per symbol:
  ta               dict of indicator values (rsi, macd, ma stack, volume, pivots)
  ta_score         0-100 composite (feeds scoring.technical_weight)
  reasons[]        plain-language lines for the report's "why" column

Scoring philosophy (deliberate, defensible):
  - Trend (40): price vs 200DMA + MA stack alignment (50>100>200 = healthy).
  - Momentum (25): RSI zone + MACD histogram sign/rising. RSI 40-60 in an
    uptrend scores best; >75 (overbought) and <25 (falling knife) penalised.
  - Volume (20): price up on above-average volume = accumulation; up on thin
    volume = suspect; down on huge volume = distribution.
  - Position (15): drawdown from 52w high + pivot proximity (room to target).

Nothing here is a "signal" on its own — ta_score is ONE input to the composite,
and the learning loop can later measure whether technical states actually
precede successful moves on NSE (same evidence rule as every other channel).
"""

from __future__ import annotations


# ----------------------------------------------------------------- helpers --
def _ema(series: list[float], n: int) -> list[float]:
    """Exponential moving average series (seeded with SMA of first n)."""
    if len(series) < n:
        return []
    k = 2.0 / (n + 1)
    out = [sum(series[:n]) / n]
    for x in series[n:]:
        out.append(x * k + out[-1] * (1 - k))
    return out


def _rsi(closes: list[float], n: int = 14) -> float | None:
    """Wilder's RSI. Needs n+1 closes."""
    if len(closes) < n + 1:
        return None
    gains = losses = 0.0
    for i in range(1, n + 1):
        d = closes[i] - closes[i - 1]
        gains += max(0.0, d)
        losses += max(0.0, -d)
    avg_g, avg_l = gains / n, losses / n
    for i in range(n + 1, len(closes)):
        d = closes[i] - closes[i - 1]
        avg_g = (avg_g * (n - 1) + max(0.0, d)) / n
        avg_l = (avg_l * (n - 1) + max(0.0, -d)) / n
    if avg_l == 0:
        return 100.0
    rs = avg_g / avg_l
    return round(100 - 100 / (1 + rs), 1)


def _macd(closes: list[float]) -> dict | None:
    """MACD line (EMA12-EMA26), signal (EMA9 of MACD), histogram."""
    if len(closes) < 35:                       # 26 + 9 warm-up
        return None
    e12, e26 = _ema(closes, 12), _ema(closes, 26)
    if not e12 or not e26:
        return None
    m = [a - b for a, b in zip(e12[-len(e26):], e26)]
    sig = _ema(m, 9)
    if not sig:
        return None
    hist = m[-len(sig):][-1] - sig[-1]
    hist_prev = m[-len(sig):][-2] - sig[-2] if len(sig) >= 2 else None
    return {"macd": round(m[-1], 2), "signal": round(sig[-1], 2),
            "hist": round(hist, 2),
            "hist_rising": (hist > (hist_prev if hist_prev is not None else hist - 1))}


def _dma(closes: list[float], n: int) -> float | None:
    if len(closes) < n:
        return None
    return round(sum(closes[-n:]) / n, 2)


def _pivots(closes: list[float]) -> dict | None:
    """Classic floor-trader pivots from the last completed day's H/L/C.
    We don't store intraday H/L, so approximate with the last 5 closes
    (high/low of the recent week) — honest proxy, stated as such."""
    if len(closes) < 5:
        return None
    w = closes[-5:]
    h, l, c = max(w), min(w), closes[-1]
    p = (h + l + c) / 3
    return {"pivot": round(p, 1), "r1": round(2 * p - l, 1),
            "s1": round(2 * p - h, 1), "r2": round(p + (h - l), 1),
            "s2": round(p - (h - l), 1)}


# ------------------------------------------------------------------ analyze --
def analyze(px: dict) -> dict | None:
    """Full TA read for one symbol from its cached price dict.
    Returns None when there isn't enough history (flagged upstream)."""
    if not px:
        return None
    closes: list[float] = px.get("close") or []
    vols: list[float] = px.get("volume") or []
    last = px.get("last") or (closes[-1] if closes else None)
    if not last or len(closes) < 30:
        return None

    rsi = _rsi(closes)
    macd = _macd(closes)
    d20 = px.get("dma20") or _dma(closes, 20)
    d50 = _dma(closes, 50)
    d100 = _dma(closes, 100)
    d200 = px.get("dma200") or _dma(closes, 200)

    # volume read
    avg20 = px.get("avg_vol20")
    vol_ratio = None
    if vols and avg20:
        vol_ratio = round((vols[-1] or 0) / max(1.0, avg20), 2)
    ret_1d = px.get("ret_1d") or 0.0

    pv = "neutral"
    if vol_ratio is not None:
        if ret_1d > 1 and vol_ratio >= 1.5:
            pv = "accumulation (price up on heavy volume)"
        elif ret_1d > 1 and vol_ratio < 0.7:
            pv = "suspect rally (thin volume)"
        elif ret_1d < -1 and vol_ratio >= 1.5:
            pv = "distribution (price down on heavy volume)"

    hi52 = max(closes[-min(250, len(closes)):])
    drawdown = round((last / hi52 - 1) * 100, 1)
    pivots = _pivots(closes)

    stack = None
    if d50 and d100 and d200:
        stack = ("bullish" if d50 > d100 > d200
                 else "bearish" if d50 < d100 < d200 else "mixed")

    ta = {
        "rsi14": rsi,
        "macd": macd,
        "dma20": d20, "dma50": d50, "dma100": d100, "dma200": d200,
        "ma_stack": stack,
        "above_200dma": (last > d200) if d200 else None,
        "above_50dma": (last > d50) if d50 else None,
        "vol_ratio_1d": vol_ratio,
        "price_volume": pv,
        "drawdown_from_52w_high_pct": drawdown,
        "pivots": pivots,
        "near_52w_high_pct": px.get("near_52w_high_pct"),
    }
    ta["ta_score"], ta["reasons"] = _score_and_reasons(ta, last, ret_1d)
    return ta


def _score_and_reasons(ta: dict, last: float, ret_1d: float) -> tuple[float, list[str]]:
    pts = 0.0
    reasons: list[str] = []

    # --- trend (40)
    above200 = ta.get("above_200dma")
    if above200 is True:
        pts += 20
        reasons.append("above 200-DMA (primary uptrend)")
    elif above200 is False:
        reasons.append("below 200-DMA (primary downtrend — entries need stronger evidence)")
    stack = ta.get("ma_stack")
    if stack == "bullish":
        pts += 20
        reasons.append("MA stack bullish (50>100>200)")
    elif stack == "bearish":
        reasons.append("MA stack bearish (50<100<200)")
    else:
        pts += 8  # mixed stack = neutral, not hostile

    # --- momentum (25)
    rsi = ta.get("rsi14")
    if rsi is not None:
        if 40 <= rsi <= 60:
            pts += 15
            reasons.append(f"RSI {rsi:.0f} (healthy zone)")
        elif 60 < rsi <= 75:
            pts += 10
            reasons.append(f"RSI {rsi:.0f} (strong — momentum with you)")
        elif rsi > 75:
            pts += 4
            reasons.append(f"RSI {rsi:.0f} OVERBOUGHT — chasing here is how chases trap")
        elif 25 <= rsi < 40:
            pts += 8
            reasons.append(f"RSI {rsi:.0f} (weak — wait for stabilisation)")
        else:
            reasons.append(f"RSI {rsi:.0f} OVERSOLD — falling knife until it turns")
    m = ta.get("macd")
    if m:
        if m["hist"] > 0:
            pts += 6 if m["hist_rising"] else 4
            if m["hist_rising"]:
                reasons.append("MACD histogram positive & rising")
        else:
            reasons.append("MACD below signal (momentum negative)")

    # --- volume (20)
    vr = ta.get("vol_ratio_1d")
    pv = ta.get("price_volume")
    if pv and "accumulation" in pv:
        pts += 20
        reasons.append("volume confirms price (accumulation)")
    elif pv and "distribution" in pv:
        reasons.append("heavy volume on a down day — distribution risk")
    elif pv and "suspect" in pv:
        pts += 5
        reasons.append("rally on thin volume — demand unconfirmed")
    elif vr is not None and vr >= 1.5:
        pts += 10
        reasons.append(f"volume {vr:.1f}x average today")

    # --- position (15)
    dd = ta.get("drawdown_from_52w_high_pct")
    if dd is not None:
        if dd >= -5:
            pts += 15
            reasons.append("sitting at/near 52-week high")
        elif dd >= -15:
            pts += 10
        elif dd >= -30:
            pts += 5
            reasons.append(f"{dd:.0f}% off its 52w high (value zone if thesis intact)")
        else:
            reasons.append(f"{dd:.0f}% below 52w high — deep drawdown, needs repair")

    return round(max(0.0, min(100.0, pts)), 1), reasons


# ------------------------------------------------------------- shadow mode --
def shadow_summary(symbol: str, records: dict) -> list[str]:
    """Nightly-report lines for the slice verification phase (shadow mode:
    TA is displayed but does NOT yet move scores)."""
    ta = (records.get(symbol) or {}).get("technical")
    if not ta:
        return []
    m = ta.get("macd") or {}
    return [
        f"RSI {ta.get('rsi14') or '?'} · MACD hist {m.get('hist', '?')} "
        f"{'↑' if m.get('hist_rising') else '↓'} · stack {ta.get('ma_stack') or '?'} · "
        f"{ta.get('drawdown_from_52w_high_pct', '?')}% off 52w-high · ta_score {ta.get('ta_score')}"
    ]
