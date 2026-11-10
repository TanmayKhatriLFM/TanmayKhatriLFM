#!/usr/bin/env python3
"""Render animated SVG cards for the GitHub profile README.

GitHub shows README images through <img>, which blocks scripts and external
requests but still runs inline CSS keyframes and SMIL. So every card is a
self-contained SVG. Data comes from data/contributions.json (refreshed daily
by the workflow); with no data file it falls back to sample values.

Usage: python3 scripts/render_cards.py   (STATIC=1 renders final states)
"""
import json, os, datetime, random, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "cards")
STATIC = os.environ.get("STATIC") == "1"
NAME = "Tanmay Khatri"
USER = "TanmayKhatriLFM"

BG, FG, MUTED, LINE, ACCENT = "#0d1117", "#e6edf3", "#7d8590", "#21262d", "#2f81f7"
FONT = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,monospace"

REDUCE = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"


def svg(w, h, body, css=""):
    if STATIC:
        css = ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img">'
            f'<style>text{{font-family:{FONT}}}.m{{font-family:{MONO}}}{css}{REDUCE}</style>'
            f'<rect width="{w}" height="{h}" rx="14" fill="{BG}" stroke="{LINE}"/>{body}</svg>')


def write(name, content):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w") as f:
        f.write(content)


def load():
    p = os.path.join(ROOT, "data", "contributions.json")
    if os.path.exists(p):
        return json.load(open(p))  # {"days":[{"date":"YYYY-MM-DD","count":n},...]}
    random.seed(7)
    today = datetime.date.today()
    days = [{"date": str(today - datetime.timedelta(d)),
             "count": max(0, int(random.gauss(3, 3)))} for d in range(364, -1, -1)]
    return {"days": days, "sample": True}


def stats(days):
    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: d["count"])
    streak = cur = 0
    for d in days:
        cur = cur + 1 if d["count"] else 0
        streak = max(streak, cur)
    months = {}
    for d in days:
        months.setdefault(d["date"][:7], 0)
        months[d["date"][:7]] += d["count"]
    return total, best, streak, list(months.items())[-12:]


# ---------- hero ----------
def hero():
    css = """
    .l{opacity:0;animation:rise .8s cubic-bezier(.2,.8,.2,1) forwards}
    .l2{animation-delay:.25s}.l3{animation-delay:.5s}
    @keyframes rise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
    .cur{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}
    """
    first, last = NAME.split(" ", 1)
    body = f'''
    <defs><linearGradient id="g" gradientUnits="userSpaceOnUse" x1="-300" x2="0">
      <stop offset="0" stop-color="{FG}"/><stop offset=".5" stop-color="{ACCENT}"/><stop offset="1" stop-color="{FG}"/>
      <animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="900 0" dur="3.5s" begin="1s" repeatCount="indefinite"/>
    </linearGradient></defs>
    <text class="l" x="48" y="92" font-size="52" font-weight="700" fill="{FG}">{html.escape(first)}</text>
    <text class="l l2" x="48" y="152" font-size="52" font-weight="700" fill="url(#g)">{html.escape(last)}</text>
    <text class="l l3 m" x="48" y="192" font-size="14" fill="{MUTED}">Building healthcare software that runs a hospital<tspan class="cur" fill="{ACCENT}">_</tspan></text>
    <text class="l l3 m" x="48" y="216" font-size="13" fill="{MUTED}">Next.js · TypeScript · Postgres · WhatsApp automation</text>
    '''
    # ascii-style code rows on the right, printing row by row
    rows = ["const hospital = new Altrus();", "await hospital.admit(patient);", "await hospital.discharge();",
            "bot.on('whatsapp', book);", "fms.run('facility-round');"]
    for i, r in enumerate(rows):
        body += (f'<text class="l m" style="animation-delay:{0.6 + i * 0.18:.2f}s" x="330" y="{50 + i * 26}" '
                 f'font-size="13" fill="{ACCENT if i % 2 == 0 else MUTED}">{html.escape(r)}</text>')
    import base64
    img = os.path.join(ROOT, "assets", "me.jpg")
    if os.path.exists(img):
        b64 = base64.b64encode(open(img, "rb").read()).decode()
        body += (f'<defs><clipPath id="av"><circle cx="705" cy="125" r="84"/></clipPath></defs>'
                 f'<g class="l l3"><circle cx="705" cy="125" r="90" fill="none" stroke="{ACCENT}" stroke-width="2" stroke-dasharray="6 6">'
                 f'<animateTransform attributeName="transform" type="rotate" from="0 705 125" to="360 705 125" dur="30s" repeatCount="indefinite"/></circle>'
                 f'<image href="data:image/jpeg;base64,{b64}" x="621" y="41" width="168" height="168" clip-path="url(#av)" preserveAspectRatio="xMidYMid slice"/></g>')
    write("hero.svg", svg(820, 250, body, css))


# ---------- three tiles ----------
def tile(name, title, number, label, delay):
    css = f"""
    .t{{transform-box:fill-box;opacity:0;animation:swing .9s cubic-bezier(.3,1.4,.5,1) {delay}s forwards}}
    @keyframes swing{{from{{opacity:0;transform:translateY(40px)}}to{{opacity:1;transform:none}}}}
    """
    steps = 18
    frames = ""
    for i in range(steps):
        v = round(number * (i + 1) / steps)
        frames += (f'<text x="28" y="108" font-size="44" font-weight="700" fill="{FG}" visibility="hidden">'
                   f'{v}<set attributeName="visibility" to="visible" begin="{delay + .3 + i * .05:.2f}s" fill="freeze"/>'
                   f'<set attributeName="visibility" to="hidden" begin="{delay + .3 + (i + 1) * .05:.2f}s" fill="freeze"/></text>'
                   ) if i < steps - 1 else (
                   f'<text x="28" y="108" font-size="44" font-weight="700" fill="{FG}" visibility="hidden">'
                   f'{v}<set attributeName="visibility" to="visible" begin="{delay + .3 + i * .05:.2f}s" fill="freeze"/></text>')
    if STATIC:
        frames = f'<text x="28" y="108" font-size="44" font-weight="700" fill="{FG}">{number}</text>'
    body = f'''<g class="t">
    <text x="28" y="44" font-size="12" letter-spacing="2" fill="{ACCENT}" class="m">{title}</text>
    {frames}
    <text x="28" y="136" font-size="14" fill="{MUTED}">{html.escape(label)}</text>
    <text x="238" y="44" font-size="16" fill="{MUTED}">↗</text></g>'''
    write(name, svg(260, 160, body, css))


# ---------- activity bars ----------
def activity(months):
    w, h, base = 820, 230, 180
    mx = max(c for _, c in months) or 1
    css = ".b{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:grow .7s cubic-bezier(.2,.8,.2,1) forwards}@keyframes grow{to{transform:scaleY(1)}}"
    body = f'<text x="32" y="38" font-size="14" fill="{FG}" font-weight="600">Contributions, last 12 months</text>'
    bw = (w - 64) / len(months)
    for i, (m, c) in enumerate(months):
        bh = max(3, 120 * c / mx)
        x = 32 + i * bw + 8
        best = c == mx
        col = ACCENT if best else "#1f6feb55"
        body += (f'<rect class="b" style="animation-delay:{i * .06:.2f}s" x="{x:.1f}" y="{base - bh:.1f}" '
                 f'width="{bw - 16:.1f}" height="{bh:.1f}" rx="4" fill="{col}"/>')
        body += f'<text x="{x + (bw - 16) / 2:.1f}" y="{base + 20}" text-anchor="middle" font-size="11" fill="{MUTED}">{datetime.date(int(m[:4]), int(m[5:]), 1):%b}</text>'
        if best:
            body += f'<text x="{x + (bw - 16) / 2:.1f}" y="{base - bh - 8:.1f}" text-anchor="middle" font-size="12" fill="{FG}" font-weight="600">{c}</text>'
    write("activity.svg", svg(w, h, body, css))


# ---------- contribution graph ----------
def graph(days):
    w, h = 820, 190
    css = ".c{opacity:0;animation:pop .35s ease forwards}@keyframes pop{to{opacity:1}}"
    body = f'<text x="32" y="36" font-size="14" fill="{FG}" font-weight="600">Contribution graph</text>'
    mx = max(d["count"] for d in days) or 1
    pal = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
    first = datetime.date.fromisoformat(days[0]["date"])
    off = (first.weekday() + 1) % 7
    for i, d in enumerate(days):
        col, row = (i + off) // 7, (i + off) % 7
        lvl = 0 if d["count"] == 0 else min(4, 1 + int(3 * d["count"] / mx))
        body += (f'<rect class="c" style="animation-delay:{col * .025:.3f}s" x="{32 + col * 14}" y="{56 + row * 17}" '
                 f'width="11" height="11" rx="2" fill="{pal[lvl]}"/>')
    write("graph.svg", svg(w, h, body, css))


# ---------- stats strip ----------
def strip(total, best, streak):
    items = [(str(total), "contributions this year"), (str(streak), "day best streak"),
             (str(best["count"]), f"busiest day · {best['date']}")]
    body = ""
    css = ".s{opacity:0;animation:rise .7s ease forwards}@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}"
    for i, (n, l) in enumerate(items):
        x = 40 + i * 260
        body += (f'<g class="s" style="animation-delay:{i * .2:.1f}s"><text x="{x}" y="58" font-size="36" font-weight="700" fill="{FG}">{n}</text>'
                 f'<text x="{x}" y="82" font-size="13" fill="{MUTED}">{html.escape(l)}</text></g>')
    write("stats.svg", svg(820, 110, body, css))


def main():
    data = load()
    days = data["days"]
    total, best, streak, months = stats(days)
    hero()
    tile("build.svg", "BUILD", 3, "live products shipped", 0.2)
    tile("work.svg", "WORK", 14, "facility modules built", 0.4)
    tile("learn.svg", "LEARN", 365, "days, one commit at a time", 0.6)
    activity(months)
    graph(days)
    strip(total, best, streak)
    print("rendered", "(sample data)" if data.get("sample") else "(live data)")


if __name__ == "__main__":
    main()
