#!/usr/bin/env python3
"""Render the animated SVG cards for the GitHub profile README.

Everything here comes from the real account: data/profile.json (repos, commits,
join date) and data/contributions.json (calendar), both refreshed daily by the
workflow. GitHub shows README images through <img>, which blocks scripts but
still runs inline CSS keyframes and SMIL, so each card is one self-contained SVG.

Usage: python3 scripts/render_cards.py        (STATIC=1 renders final frames)
"""
import json, os, datetime, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "cards")
STATIC = os.environ.get("STATIC") == "1"

PAPER, PAPER2, INK, MUTED, LINE = "#f4efe4", "#ece5d4", "#17150f", "#6b6558", "#d8d0bd"
BLUE, RED, YEL = "#2f5bea", "#e5484d", "#e8a800"
SERIF = "'Instrument Serif',Georgia,'Times New Roman',serif"
SANS = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
LANG = {"Python": "#3572A5", "HTML": "#e34c26", "JavaScript": "#f1e05a", "TypeScript": "#3178c6", None: "#9a9384"}
REDUCE = "@media (prefers-reduced-motion:reduce){*{animation:none!important;opacity:1!important;transform:none!important}}"


def svg(w, h, body, css=""):
    if STATIC:
        css = ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">'
            f'<style>text{{font-family:{SANS}}}.serif{{font-family:{SERIF}}}.m{{font-family:{MONO}}}{css}{REDUCE}</style>'
            f'<rect width="{w}" height="{h}" rx="16" fill="{PAPER}" stroke="{LINE}"/>{body}</svg>')


def write(name, content):
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, name), "w").write(content)


def esc(s):
    return html.escape(str(s))


def d(s):
    return datetime.date.fromisoformat(s[:10])


def load():
    days = json.load(open(os.path.join(ROOT, "data", "contributions.json")))["days"]
    prof = json.load(open(os.path.join(ROOT, "data", "profile.json")))
    return days, prof


# ---------------------------------------------------------------- hero
def hero(prof, days):
    css = """
    .l{opacity:0;animation:rise .9s cubic-bezier(.2,.8,.2,1) forwards}
    @keyframes rise{from{opacity:0;transform:translateY(22px)}to{opacity:1;transform:none}}
    .r{opacity:0;animation:fade .25s ease forwards}@keyframes fade{to{opacity:1}}
    .dot{animation:pulse 1.8s ease-out infinite;transform-box:fill-box;transform-origin:center}
    @keyframes pulse{0%{transform:scale(1);opacity:.9}100%{transform:scale(3);opacity:0}}
    """
    last = max(r["pushed_at"] for r in prof["repos"])
    langs = []
    for r in prof["repos"]:
        if r["language"] and r["language"] not in langs:
            langs.append(r["language"])
    body = f'''
    <defs><linearGradient id="sh" gradientUnits="userSpaceOnUse" x1="-260" x2="0">
      <stop offset="0" stop-color="{INK}"/><stop offset=".5" stop-color="{BLUE}"/><stop offset="1" stop-color="{INK}"/>
      <animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="700 0" dur="2.6s" begin="1.2s;sh2.end+3s" id="sh2"/>
    </linearGradient></defs>
    <text class="l serif" x="52" y="118" font-size="84" fill="{INK}">Tanmay</text>
    <text class="l serif" style="animation-delay:.2s" x="52" y="198" font-size="84" fill="url(#sh)">Khatri</text>
    <text class="l" style="animation-delay:.5s" x="54" y="244" font-size="17" fill="{MUTED}">Learning in public: test automation, scraping and APIs.</text>
    <text class="l m" style="animation-delay:.6s" x="54" y="272" font-size="13" fill="{BLUE}">@{esc(prof["login"])}  ·  joined {d(prof["created_at"]):%b %Y}</text>
    <g class="l" style="animation-delay:.8s">
      <circle class="dot" cx="60" cy="312" r="5" fill="{RED}"/><circle cx="60" cy="312" r="5" fill="{RED}"/>
      <text class="m" x="76" y="316" font-size="13" fill="{INK}">last push {d(last):%d %b %Y}  ·  {" · ".join(esc(l) for l in langs)}</text>
    </g>'''
    # ASCII portrait, printed row by row (18 ms apart)
    p = os.path.join(ROOT, "assets", "portrait.txt")
    if os.path.exists(p):
        rows = open(p).read().split("\n")
        cw, lh, fs = 4.2, 8.1, 6.9
        x0, y0 = 440, 40
        for i, row in enumerate(rows):
            if not row.strip():
                continue
            body += (f'<text class="r m" style="animation-delay:{.5 + i * .018:.3f}s" xml:space="preserve" '
                     f'x="{x0}" y="{y0 + i * lh:.1f}" font-size="{fs}" fill="{INK}" textLength="{len(row) * cw:.1f}" '
                     f'lengthAdjust="spacing">{esc(row)}</text>')
    write("hero.svg", svg(820, 400, body, css))


# ---------------------------------------------------------------- tiles
def tile(name, color, title, number, label, sub, delay, tilt):
    css = f"""
    .t{{transform-box:fill-box;transform-origin:bottom left;opacity:0;animation:swing 1s cubic-bezier(.3,1.5,.5,1) {delay}s forwards}}
    @keyframes swing{{from{{opacity:0;transform:translateY(46px) rotate({tilt}deg)}}to{{opacity:1;transform:none}}}}
    .ring{{transform-box:fill-box;transform-origin:center;animation:ring 2.4s ease-out {delay + 1}s infinite;opacity:0}}
    @keyframes ring{{0%{{transform:scale(.4);opacity:.7}}100%{{transform:scale(2.6);opacity:0}}}}
    .ar{{animation:nudge 1.6s ease-in-out infinite}}@keyframes nudge{{50%{{transform:translate(4px,-4px)}}}}
    """
    steps = 20
    nums = ""
    for i in range(steps):
        v = round(number * (i + 1) / steps)
        t0 = delay + .35 + i * .045
        end = f'<set attributeName="visibility" to="hidden" begin="{t0 + .045:.3f}s" fill="freeze"/>' if i < steps - 1 else ""
        nums += (f'<text class="serif" x="28" y="112" font-size="68" fill="{INK}" visibility="hidden">{v}'
                 f'<set attributeName="visibility" to="visible" begin="{t0:.3f}s" fill="freeze"/>{end}</text>')
    if STATIC:
        nums = f'<text class="serif" x="28" y="112" font-size="68" fill="{INK}">{number}</text>'
    body = f'''<defs><linearGradient id="s{name[0]}" gradientUnits="userSpaceOnUse" x1="-120" x2="-40">
      <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
      <animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="420 0" dur="1.4s" begin="{delay + 1.5}s;0s" repeatCount="indefinite" additive="sum"/>
    </linearGradient></defs>
    <g class="t">
      <rect x="1" y="1" width="258" height="178" rx="16" fill="{PAPER2}" stroke="{color}" stroke-width="2"/>
      <rect x="1" y="1" width="258" height="178" rx="16" fill="url(#s{name[0]})"/>
      <circle class="ring" cx="226" cy="34" r="12" fill="none" stroke="{color}" stroke-width="2"/>
      <circle cx="226" cy="34" r="5" fill="{color}"/>
      <text class="m" x="28" y="42" font-size="12" letter-spacing="3" fill="{color}" font-weight="700">{title}</text>
      {nums}
      <text x="28" y="142" font-size="14" fill="{INK}" font-weight="600">{esc(label)}</text>
      <text x="28" y="162" font-size="12" fill="{MUTED}">{esc(sub)}</text>
      <text class="ar" x="228" y="162" font-size="20" fill="{color}">↗</text>
    </g>'''
    write(name, svg(260, 180, body, css))


# ---------------------------------------------------------------- activity
def activity(days, prof):
    start = d(prof["created_at"]).replace(day=1)
    today = datetime.date.today()
    months, cur = [], start
    while cur <= today:
        months.append(cur)
        cur = (cur.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
    counts = {m: 0 for m in months}
    active = []
    for x in days:
        dt = d(x["date"])
        k = dt.replace(day=1)
        if k in counts and x["count"]:
            counts[k] += x["count"]
            active.append(x)
    total = sum(counts.values())
    best = max(active, key=lambda x: x["count"]) if active else {"count": 0, "date": today.isoformat()}
    streak = run = 0
    prev = None
    for x in sorted(active, key=lambda x: x["date"]):
        dt = d(x["date"])
        run = run + 1 if prev and (dt - prev).days == 1 else 1
        streak, prev = max(streak, run), dt
    mx = max(counts.values()) or 1
    w, h, base = 820, 300, 200
    css = f"""
    .b{{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:grow .8s cubic-bezier(.2,.9,.2,1) forwards}}
    @keyframes grow{{to{{transform:scaleY(1)}}}}
    .pop{{opacity:0;animation:pp .4s ease forwards}}@keyframes pp{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}"""
    body = f'<text class="serif" x="36" y="50" font-size="30" fill="{INK}">Activity</text>'
    body += f'<text class="m" x="36" y="70" font-size="12" fill="{MUTED}">commits and contributions per month since joining</text>'
    # stats on the right
    for i, (n, lab) in enumerate([(total, "contributions"), (len(active), "active days"), (streak, "day streak"), (best["count"], "busiest day")]):
        x = 470 + i * 88
        body += (f'<g class="pop" style="animation-delay:{.2 + i * .12:.2f}s"><text class="serif" x="{x}" y="52" font-size="36" fill="{INK}">{n}</text>'
                 f'<text x="{x}" y="70" font-size="11" fill="{MUTED}">{lab}</text></g>')
    area = w - 72
    bw = area / len(months)
    for i, m in enumerate(months):
        c = counts[m]
        bh = max(4, 110 * c / mx) if c else 4
        x = 36 + i * bw
        top = c == max(counts.values()) and c > 0
        col = BLUE if top else (INK if c else LINE)
        body += (f'<rect class="b" style="animation-delay:{i * .1:.2f}s" x="{x + 10:.1f}" y="{base - bh:.1f}" width="{bw - 20:.1f}" '
                 f'height="{bh:.1f}" rx="6" fill="{col}" opacity="{1 if c else .8}"/>')
        body += f'<text x="{x + bw / 2:.1f}" y="{base + 22}" text-anchor="middle" font-size="12" fill="{MUTED}">{m:%b}</text>'
        if c:
            body += (f'<text class="pop" style="animation-delay:{.8 + i * .1:.2f}s" x="{x + bw / 2:.1f}" y="{base - bh - 8:.1f}" '
                     f'text-anchor="middle" font-size="14" font-weight="700" fill="{BLUE if top else INK}">{c}</text>')
    body += f'<text class="m" x="36" y="{h - 18}" font-size="11" fill="{MUTED}">busiest day: {d(best["date"]):%d %b %Y}</text>'
    write("activity.svg", svg(w, h, body, css))


# ---------------------------------------------------------------- heatmap
def heatmap(days):
    w, h = 820, 200
    css = ".c{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .4s ease forwards}@keyframes pop{from{opacity:0;transform:scale(.2)}to{opacity:1;transform:none}}"
    mx = max(x["count"] for x in days) or 1
    pal = ["#e4dccb", "#c3d3ff", "#86a6ff", "#4f7af0", BLUE]
    body = f'<text class="serif" x="36" y="44" font-size="30" fill="{INK}">The last year</text>'
    off = (d(days[0]["date"]).weekday() + 1) % 7
    cols = (len(days) + off + 6) // 7
    cell = min(14.5, (w - 72) / cols)
    for i, x in enumerate(days):
        col, row = (i + off) // 7, (i + off) % 7
        lvl = 0 if not x["count"] else min(4, 1 + int(3 * x["count"] / mx))
        body += (f'<rect class="c" style="animation-delay:{col * .03:.3f}s" x="{36 + col * cell:.1f}" y="{66 + row * cell:.1f}" '
                 f'width="{cell - 3:.1f}" height="{cell - 3:.1f}" rx="3" fill="{pal[lvl]}"/>')
    write("heatmap.svg", svg(w, h, body, css))


# ---------------------------------------------------------------- repos
def repos(prof):
    items = prof["repos"]
    cols, cw, ch, gap = 3, 241, 112, 12
    rows = (len(items) + cols - 1) // cols
    w, h = 820, 90 + rows * (ch + gap)
    css = f"""
    .k{{opacity:0;transform-box:fill-box;transform-origin:center;animation:in .6s cubic-bezier(.3,1.4,.5,1) forwards}}
    @keyframes in{{from{{opacity:0;transform:translateY(24px) scale(.96)}}to{{opacity:1;transform:none}}}}
    .ty{{stroke-dasharray:60;stroke-dashoffset:60;animation:dr 1s ease forwards}}@keyframes dr{{to{{stroke-dashoffset:0}}}}"""
    body = f'<text class="serif" x="36" y="50" font-size="30" fill="{INK}">What I\'m coding</text>'
    body += f'<text class="m" x="36" y="70" font-size="12" fill="{MUTED}">every public repo, newest push first</text>'
    for i, r in enumerate(items):
        cx, cy = 36 + (i % cols) * (cw + gap), 88 + (i // cols) * (ch + gap)
        lang = r["language"]
        col = LANG.get(lang, "#9a9384")
        name = r["name"] if len(r["name"]) <= 22 else r["name"][:21] + "…"
        meta = f'{r["commits"]} commit{"s" if r["commits"] != 1 else ""}' if r["commits"] else "empty"
        meta += f' · {d(r["pushed_at"]):%d %b %Y}'
        tag = "fork" if r["fork"] else (lang or "no code yet")
        body += f'''<a href="https://github.com/{esc(prof["login"])}/{esc(r["name"])}"><g class="k" style="animation-delay:{.2 + i * .12:.2f}s">
          <rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="12" fill="{PAPER2}" stroke="{LINE}"/>
          <rect x="{cx}" y="{cy + 16}" width="4" height="30" rx="2" fill="{col}"/>
          <text class="m" x="{cx + 20}" y="{cy + 38}" font-size="14" font-weight="700" fill="{INK}">{esc(name)}</text>
          <path class="ty" style="animation-delay:{.6 + i * .12:.2f}s" d="M{cx + 20} {cy + 48} h60" stroke="{BLUE}" stroke-width="2" fill="none"/>
          <circle cx="{cx + 24}" cy="{cy + 76}" r="5" fill="{col}"/>
          <text x="{cx + 36}" y="{cy + 80}" font-size="13" fill="{INK}">{esc(tag)}</text>
          <text class="m" x="{cx + 20}" y="{cy + 100}" font-size="11" fill="{MUTED}">{esc(meta)}</text>
        </g></a>'''
    write("repos.svg", svg(w, h, body, css))


def main():
    days, prof = load()
    rs = prof["repos"]
    commits = sum(r["commits"] for r in rs)
    since = (datetime.date.today() - d(prof["created_at"])).days
    hero(prof, days)
    tile("build.svg", BLUE, "BUILD", len(rs), "public repositories", "automation, scraping, tests", .2, -5)
    tile("work.svg", RED, "WORK", commits, "commits across repos", "one small push at a time", .45, 4)
    tile("learn.svg", YEL, "LEARN", since, "days on GitHub", f"since {d(prof['created_at']):%d %b %Y}", .7, -4)
    activity(days, prof)
    heatmap(days)
    repos(prof)
    print("rendered", len(rs), "repos,", commits, "commits")


if __name__ == "__main__":
    main()
