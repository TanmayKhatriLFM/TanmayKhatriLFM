#!/usr/bin/env python3
"""Render the animated SVG cards for the GitHub profile README.

Every number on every card is computed from data/profile.json and
data/contributions.json (refreshed by the workflow). Nothing is typed in by hand.
Cards are single self-contained SVGs: GitHub shows README images through <img>,
which blocks scripts but still runs inline CSS keyframes and SMIL.

Usage: python3 scripts/render_cards.py        (STATIC=1 renders final frames)
"""
import json, os, datetime, html, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "cards")
STATIC = os.environ.get("STATIC") == "1"

INK, MUTED, LINE, CARD = "var(--ink)", "var(--muted)", "var(--line)", "var(--card)"
SERIF = "'Instrument Serif',Georgia,'Times New Roman',serif"
SANS = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
LANG = {"Python": "#3572A5", "HTML": "#e34c26", "JavaScript": "#f1e05a", "TypeScript": "#3178c6", None: "#8b8577"}
BLUE, RED, YEL = "#2f5bea", "#e5484d", "#f5b301"

THEME = (":root{--ink:#1f2328;--muted:#656d76;--line:#d0d7de;--card:#f6f8fa;--floor:#e3e7eb;"
         "--b1:#6f95ff;--b2:#2f5bea;--b3:#1e3fb0;--hi:#e5484d}"
         "@media (prefers-color-scheme:dark){:root{--ink:#e6edf3;--muted:#7d8590;--line:#30363d;--card:#161b22;--floor:#1d242d;"
         "--b1:#8fb0ff;--b2:#4a78f0;--b3:#2a4fc2;--hi:#ff7b72}}")
REDUCE = "@media (prefers-reduced-motion:reduce){*{animation:none!important;opacity:1!important;transform:none!important}}"


def svg(w, h, body, css=""):
    if STATIC:
        css = ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">'
            f'<style>{THEME}text{{font-family:{SANS}}}.serif{{font-family:{SERIF}}}.m{{font-family:{MONO}}}{css}{REDUCE}</style>'
            f'{body}</svg>')


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


def stats(days):
    active = [x for x in days if x["count"]]
    total = sum(x["count"] for x in days)
    best = max(active, key=lambda x: x["count"]) if active else {"count": 0, "date": days[-1]["date"]}
    streak = run = 0
    prev = None
    for x in active:
        dt = d(x["date"])
        run = run + 1 if prev and (dt - prev).days == 1 else 1
        streak, prev = max(streak, run), dt
    return total, len(active), streak, best


# ---------------------------------------------------------------- hero
def hero(prof, days):
    total, nactive, streak, best = stats(days)
    css = """
    .l{opacity:0;animation:rise .9s cubic-bezier(.2,.8,.2,1) forwards}
    @keyframes rise{from{opacity:0;transform:translateY(24px)}to{opacity:1;transform:none}}
    .r{opacity:0;animation:fade .25s ease forwards}@keyframes fade{to{opacity:1}}
    .rule{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:wipe 1s .5s cubic-bezier(.2,.8,.2,1) forwards}
    @keyframes wipe{to{transform:scaleX(1)}}
    """
    last = max(r["pushed_at"] for r in prof["repos"])
    body = f'''
    <text class="l serif" x="48" y="118" font-size="92" fill="{INK}">Tanmay</text>
    <text class="l serif" style="animation-delay:.18s" x="48" y="202" font-size="92" fill="{INK}">Khatri</text>
    <rect class="rule" x="52" y="232" width="360" height="2" fill="{INK}"/>'''
    for i, (n, lab) in enumerate([(total, "contributions"), (nactive, "active days"), (streak, "day streak")]):
        x = 52 + i * 128
        body += (f'<g class="l" style="animation-delay:{.5 + i * .12:.2f}s"><text class="serif" x="{x}" y="288" font-size="46" fill="{INK}">{n}</text>'
                 f'<text class="m" x="{x}" y="308" font-size="11" fill="{MUTED}">{lab}</text></g>')
    body += (f'<text class="l m" style="animation-delay:.9s" x="52" y="346" font-size="11" fill="{MUTED}">'
             f'@{esc(prof["login"])}  /  since {d(prof["created_at"]):%d %b %Y}  /  last push {d(last):%d %b %Y}</text>')
    # ASCII portrait, printed row by row (18 ms apart)
    p = os.path.join(ROOT, "assets", "portrait.txt")
    if os.path.exists(p):
        cw, lh, fs = 2.8, 5.65, 4.8
        x0, y0 = 458, 30
        for i, row in enumerate(open(p).read().split("\n")):
            if not row.strip():
                continue
            body += (f'<text class="r m" style="animation-delay:{.4 + i * .018:.3f}s" xml:space="preserve" '
                     f'x="{x0}" y="{y0 + i * lh:.1f}" font-size="{fs}" fill="{INK}" textLength="{len(row) * cw:.1f}" '
                     f'lengthAdjust="spacing">{esc(row)}</text>')
    write("hero.svg", svg(820, 380, body, css))


# ---------------------------------------------------------------- tiles
def tile(name, bg, fg, title, number, label, strip, delay, tilt):
    css = f"""
    .t{{transform-box:fill-box;transform-origin:bottom left;opacity:0;animation:swing 1s cubic-bezier(.3,1.5,.5,1) {delay}s forwards}}
    @keyframes swing{{from{{opacity:0;transform:translateY(46px) rotate({tilt}deg)}}to{{opacity:1;transform:none}}}}
    .sb{{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:up .6s ease forwards}}
    @keyframes up{{to{{transform:scaleY(1)}}}}"""
    steps = 20
    nums = ""
    for i in range(steps):
        v = round(number * (i + 1) / steps)
        t0 = delay + .35 + i * .045
        end = f'<set attributeName="visibility" to="hidden" begin="{t0 + .045:.3f}s" fill="freeze"/>' if i < steps - 1 else ""
        nums += (f'<text class="serif" x="24" y="104" font-size="70" fill="{fg}" visibility="hidden">{v}'
                 f'<set attributeName="visibility" to="visible" begin="{t0:.3f}s" fill="freeze"/>{end}</text>')
    if STATIC:
        nums = f'<text class="serif" x="24" y="104" font-size="70" fill="{fg}">{number}</text>'
    # strip: list of (value, active) bars drawn along the bottom
    sw, sx, sy, sh = 212, 24, 172, 30
    mx = max((v for v, _ in strip), default=1) or 1
    n = len(strip)
    bw = sw / n
    bars = ""
    for i, (v, on) in enumerate(strip):
        bh = max(2, sh * v / mx) if on else 2
        bars += (f'<rect class="sb" style="animation-delay:{delay + .5 + i * (0.6 / n):.3f}s" x="{sx + i * bw:.2f}" y="{sy - bh:.1f}" '
                 f'width="{max(.8, bw - (1.2 if bw > 4 else .3)):.2f}" height="{bh:.1f}" fill="{fg}" opacity="{1 if on else .35}"/>')
    body = f'''<g class="t">
      <rect width="260" height="190" rx="14" fill="{bg}"/>
      <text class="m" x="24" y="36" font-size="11" letter-spacing="3" fill="{fg}" font-weight="700">{title}</text>
      {nums}
      <text x="24" y="130" font-size="14" fill="{fg}" font-weight="600">{esc(label)}</text>
      {bars}
    </g>'''
    write(name, svg(260, 190, body, css))


# ---------------------------------------------------------------- skyline
def skyline(days):
    W, base = 820, 236
    cw, bw, step, dep = 13, 11, 5, 4        # column pitch, bar width, row offset, bar depth
    css = """
    .bar{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:grow .7s cubic-bezier(.2,.9,.2,1) forwards}
    @keyframes grow{to{transform:scaleY(1)}}
    .fade{opacity:0;animation:fd .6s ease forwards}@keyframes fd{to{opacity:1}}"""
    mx = max(x["count"] for x in days) or 1
    off = (d(days[0]["date"]).weekday() + 1) % 7
    cells = []
    for i, x in enumerate(days):
        cells.append(((i + off) // 7, (i + off) % 7, x))
    ncols = max(c for c, _, _ in cells) + 1
    x00 = (W - (ncols * cw + 6 * step)) / 2
    total = sum(x["count"] for x in days)
    body = f'<text class="serif" x="36" y="46" font-size="34" fill="{INK}">Skyline</text>'
    body += f'<text class="m" x="36" y="66" font-size="11" fill="{MUTED}">one bar per day, height is contributions</text>'
    floor, bars = "", ""
    hi = None
    for r in range(6, -1, -1):                     # back rows first
        for c, rr, x in cells:
            if rr != r:
                continue
            X = x00 + c * cw + r * step
            Y = base - r * step
            if not x["count"]:
                floor += f'<path d="M{X:.1f} {Y:.1f}h{bw}l{dep} -{dep}h-{bw}z" fill="var(--floor)"/>'
                continue
            h = 4 + 100 * x["count"] / mx
            delay = c * .018 + (6 - r) * .01
            bars += (f'<g class="bar" style="animation-delay:{delay:.3f}s">'
                     f'<rect x="{X:.1f}" y="{Y - h:.1f}" width="{bw}" height="{h:.1f}" fill="var(--b2)"/>'
                     f'<path d="M{X:.1f} {Y - h:.1f}h{bw}l{dep} -{dep}h-{bw}z" fill="var(--b1)"/>'
                     f'<path d="M{X + bw:.1f} {Y - h:.1f}l{dep} -{dep}v{h:.1f}l-{dep} {dep}z" fill="var(--b3)"/></g>')
            if hi is None or x["count"] > hi[0]:
                hi = (x["count"], X + bw / 2 + dep / 2, Y - h - dep, x["date"])
    body += floor + bars
    # month ticks along the front edge
    seen = None
    for c, rr, x in cells:
        if rr == 0:
            m = d(x["date"]).month
            if m != seen:
                seen = m
                body += f'<text class="m" x="{x00 + c * cw:.1f}" y="{base + 22}" font-size="10" fill="{MUTED}">{d(x["date"]):%b}</text>'
    if hi:
        n, hx, hy, hd = hi
        body += (f'<g class="fade" style="animation-delay:1.6s"><path d="M{hx:.1f} {hy - 2:.1f}v-14" stroke="var(--hi)" stroke-width="1.5"/>'
                 f'<text class="m" x="{hx:.1f}" y="{hy - 22:.1f}" text-anchor="middle" font-size="11" font-weight="700" fill="var(--hi)">{n}</text>'
                 f'<text class="m" x="{hx:.1f}" y="{hy - 34:.1f}" text-anchor="middle" font-size="9" fill="{MUTED}">{d(hd):%d %b}</text></g>')
    stamp = datetime.datetime.utcnow()
    body += (f'<text class="m" x="{W - 36}" y="{base + 22 + 18}" text-anchor="end" font-size="10" fill="{MUTED}">'
             f'{total} in the last 12 months  /  updated {stamp:%d %b %H:%M} UTC</text>')
    write("skyline.svg", svg(W, base + 62, body, css))


# ---------------------------------------------------------------- rhythm
def rhythm(days, prof):
    W, H, base = 820, 270, 190
    css = f"""
    .b{{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:grow .8s cubic-bezier(.2,.9,.2,1) forwards}}
    @keyframes grow{{to{{transform:scaleY(1)}}}}
    .pop{{opacity:0;animation:pp .4s ease forwards}}@keyframes pp{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}"""
    months = collections.OrderedDict()
    for x in days:
        k = d(x["date"]).replace(day=1)
        months[k] = months.get(k, 0) + x["count"]
    keys = list(months)
    while keys and not months[keys[0]]:
        keys.pop(0)                                  # start at the first active month
    wd = [0] * 7                                     # Sun..Sat
    for x in days:
        wd[(d(x["date"]).weekday() + 1) % 7] += x["count"]
    body = f'<text class="serif" x="36" y="46" font-size="34" fill="{INK}">Rhythm</text>'
    body += f'<text class="m" x="36" y="66" font-size="11" fill="{MUTED}">by month, and by day of the week</text>'
    # months (left)
    mx = max(months[k] for k in keys) or 1
    area = 470
    bw = area / len(keys)
    for i, k in enumerate(keys):
        c = months[k]
        h = max(3, 100 * c / mx) if c else 3
        x = 36 + i * bw
        top = c == mx
        body += (f'<rect class="b" style="animation-delay:{i * .08:.2f}s" x="{x + 6:.1f}" y="{base - h:.1f}" width="{bw - 12:.1f}" height="{h:.1f}" '
                 f'rx="3" fill="{"var(--b2)" if top else INK}" opacity="{1 if top else (.85 if c else .25)}"/>')
        body += f'<text class="m" x="{x + bw / 2:.1f}" y="{base + 18}" text-anchor="middle" font-size="10" fill="{MUTED}">{k:%b}</text>'
        if c:
            body += (f'<text class="pop m" style="animation-delay:{.7 + i * .08:.2f}s" x="{x + bw / 2:.1f}" y="{base - h - 8:.1f}" text-anchor="middle" '
                     f'font-size="11" font-weight="700" fill="{"var(--b2)" if top else INK}">{c}</text>')
    # weekdays (right)
    wx0, wmax = 560, max(wd) or 1
    names = "SMTWTFS"
    best = wd.index(max(wd))
    for i, c in enumerate(wd):
        h = max(3, 100 * c / wmax)
        x = wx0 + i * 32
        top = i == best
        body += (f'<rect class="b" style="animation-delay:{.3 + i * .07:.2f}s" x="{x}" y="{base - h:.1f}" width="22" height="{h:.1f}" rx="3" '
                 f'fill="{"var(--hi)" if top else INK}" opacity="{1 if top else .85}"/>')
        body += f'<text class="m" x="{x + 11}" y="{base + 18}" text-anchor="middle" font-size="10" fill="{MUTED}">{names[i]}</text>'
        body += (f'<text class="pop m" style="animation-delay:{.9 + i * .07:.2f}s" x="{x + 11}" y="{base - h - 8:.1f}" text-anchor="middle" '
                 f'font-size="10" font-weight="700" fill="{"var(--hi)" if top else INK}">{c}</text>')
    full = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    body += f'<text class="m" x="{wx0}" y="{H - 14}" font-size="11" fill="{MUTED}">most active: {full[best]}s</text>'
    body += f'<line x1="520" y1="86" x2="520" y2="{base + 6}" stroke="{LINE}"/>'
    write("rhythm.svg", svg(W, H, body, css))


# ---------------------------------------------------------------- repos
def repos(prof):
    items = sorted(prof["repos"], key=lambda r: r["pushed_at"], reverse=True)
    W, row, top = 820, 40, 96
    H = top + len(items) * row + 24
    css = """
    .k{opacity:0;animation:in .5s ease forwards}@keyframes in{from{opacity:0;transform:translateX(-14px)}to{opacity:1;transform:none}}
    .cb{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:wx .8s cubic-bezier(.2,.9,.2,1) forwards}
    @keyframes wx{to{transform:scaleX(1)}}"""
    body = f'<text class="serif" x="36" y="46" font-size="34" fill="{INK}">Repositories</text>'
    body += f'<text class="m" x="36" y="66" font-size="11" fill="{MUTED}">{prof["public_repos"]} public (this profile repo not listed), newest push first</text>'
    mx = max((r["commits"] for r in items), default=1) or 1
    for i, r in enumerate(items):
        y = top + i * row
        col = LANG.get(r["language"], "#8b8577")
        lang = "fork" if r["fork"] else (r["language"] or "empty")
        body += f'<a href="https://github.com/{esc(prof["login"])}/{esc(r["name"])}"><g class="k" style="animation-delay:{.15 + i * .1:.2f}s">'
        body += f'<line x1="36" y1="{y}" x2="{W - 36}" y2="{y}" stroke="{LINE}"/>'
        body += f'<text class="m" x="36" y="{y + 25}" font-size="10" fill="{MUTED}">{i + 1:02d}</text>'
        body += f'<text class="m" x="70" y="{y + 25}" font-size="14" font-weight="700" fill="{INK}">{esc(r["name"])}</text>'
        body += f'<circle cx="400" cy="{y + 21}" r="4.5" fill="{col}"/><text x="412" y="{y + 25}" font-size="13" fill="{INK}">{esc(lang)}</text>'
        bwid = 130 * r["commits"] / mx
        body += f'<rect x="520" y="{y + 15}" width="130" height="8" rx="4" fill="var(--floor)"/>'
        if r["commits"]:
            body += f'<rect class="cb" style="animation-delay:{.4 + i * .1:.2f}s" x="520" y="{y + 15}" width="{bwid:.1f}" height="8" rx="4" fill="var(--b2)"/>'
        body += f'<text class="m" x="662" y="{y + 25}" font-size="12" fill="{INK}">{r["commits"]}</text>'
        body += f'<text class="m" x="{W - 36}" y="{y + 25}" text-anchor="end" font-size="11" fill="{MUTED}">{d(r["pushed_at"]):%d %b %Y}</text>'
        body += "</g></a>"
    body += f'<line x1="36" y1="{top + len(items) * row}" x2="{W - 36}" y2="{top + len(items) * row}" stroke="{LINE}"/>'
    write("repos.svg", svg(W, H, body, css))


def main():
    days, prof = load()
    rs = prof["repos"]
    total, nactive, streak, best = stats(days)
    since = (datetime.date.today() - d(prof["created_at"])).days
    hero(prof, days)
    # tile strips are real: commits per repo / weekly contributions / one cell per day since joining
    repo_strip = [(r["commits"], True) for r in sorted(rs, key=lambda r: r["pushed_at"])]
    weeks = [sum(x["count"] for x in days[i:i + 7]) for i in range(len(days) % 7, len(days), 7)][-26:]
    by_date = {x["date"]: x["count"] for x in days}
    join = d(prof["created_at"])
    day_strip = []
    for k in range(since + 1):
        c = by_date.get(str(join + datetime.timedelta(days=k)), 0)
        day_strip.append((c or 1, bool(c)))
    tile("build.svg", BLUE, "#ffffff", "BUILD", prof["public_repos"], "public repositories", repo_strip, .2, -5)
    tile("work.svg", RED, "#ffffff", "WORK", total, "contributions, last year", [(w, bool(w)) for w in weeks], .45, 4)
    tile("learn.svg", YEL, "#1a1400", "LEARN", since, f"days on GitHub, {nactive} active", day_strip, .7, -4)
    skyline(days)
    rhythm(days, prof)
    repos(prof)
    print("rendered:", total, "contributions,", nactive, "active days,", len(rs), "repos")


if __name__ == "__main__":
    main()
