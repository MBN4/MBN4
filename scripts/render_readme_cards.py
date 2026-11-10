#!/usr/bin/env python3
import base64, datetime, json, os, re
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
DATA = os.path.join(ROOT, "data", "contributions.json")
OUT = os.path.join(ROOT, "cards")
FONTS = os.path.join(ROOT, "fonts")

TECH = "#2f55ff"
STUDIO = "#ef3b2d"
LEARN = "#ffc81a"
W = 880

SERIF = "'Instrument Serif', Georgia, serif"
SANS = "Geist, system-ui, -apple-system, sans-serif"
MONO = "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, monospace"

FONT_FILES = {
    "serif": ("Instrument Serif", "normal", 400, "serif-400.woff"),
    "serif-i": ("Instrument Serif", "italic", 400, "serif-italic.woff"),
    "sans": ("Geist", "normal", 400, "geist-400.woff"),
    "sans-b": ("Geist", "normal", 600, "geist-600.woff"),
    "mono": ("Geist Mono", "normal", 400, "geistmono-400.woff"),
}

BASE_CSS = """
@keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes pop{0%{opacity:0;transform:scale(.3)}70%{opacity:1;transform:scale(1.15)}100%{opacity:1;transform:none}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}
@keyframes nudge{0%,100%{transform:none}50%{transform:translateX(4px)}}
@keyframes nudgeup{0%,100%{transform:none}50%{transform:translate(3px,-3px)}}
.r{opacity:0;animation:rise .8s cubic-bezier(.2,.7,.2,1) both;transform-box:fill-box}
.f{opacity:0;animation:fade .9s ease-out both}
.g{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:grow .8s cubic-bezier(.2,.7,.2,1) both}
.p{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .4s ease-out both}
.live{animation:pulse 1.6s ease-in-out infinite}
.n{transform-box:fill-box;animation:nudge 1.8s ease-in-out infinite}
.nu{transform-box:fill-box;animation:nudgeup 1.8s ease-in-out infinite}
@keyframes tilein{0%{opacity:0;transform:translateY(90px) scale(.6) rotate(-9deg)}55%{opacity:1;transform:translateY(-10px) scale(1.05) rotate(2deg)}75%{transform:translateY(3px) scale(.98) rotate(-.8deg)}90%{transform:translateY(-1px) scale(1.01) rotate(.2deg)}100%{opacity:1;transform:none}}
@keyframes slidein{from{opacity:0;transform:translateX(-26px)}to{opacity:1;transform:none}}
@keyframes arrowin{0%{opacity:0;transform:translateX(-30px)}60%{opacity:1;transform:translateX(6px)}100%{opacity:1;transform:none}}
@keyframes roll{from{transform:translateY(60px)}to{transform:none}}
@keyframes sheen{0%{transform:translateX(-260px) skewX(-20deg)}22%,100%{transform:translateX(420px) skewX(-20deg)}}
@keyframes ring{0%{opacity:.7;transform:scale(.2)}100%{opacity:0;transform:scale(2.4)}}
.ti{opacity:0;transform-box:fill-box;transform-origin:50% 60%;animation:tilein 1.1s cubic-bezier(.2,.8,.2,1) both}
.sl{opacity:0;transform-box:fill-box;animation:slidein .6s cubic-bezier(.2,.7,.2,1) both}
.ai{opacity:0;transform-box:fill-box;animation:arrowin .7s cubic-bezier(.2,.7,.2,1) both}
.ro{transform-box:fill-box;animation:roll .8s cubic-bezier(.15,.8,.2,1) both}
.sh{animation:sheen 5s ease-in-out infinite}
.rg{opacity:0;transform-box:fill-box;transform-origin:center;animation:ring 1s ease-out both}

/* Theme Adaptive Tokens */
.bg { fill: #f3f3f1; stroke: #e2e2de; stroke-width: 1px; }
.ink { fill: #111111; }
.soft { fill: #3a3a3c; }
.muted { fill: #6e6e73; }
.rule { fill: #dcdcd7; }
.bar-default { fill: #111111; }
.bar-partial { fill: #c9c9c4; }
.grad-base { stop-color: #111111; }

.c-0 { fill: #e2e2de; }
.c-1 { fill: #c8d3ff; }
.c-2 { fill: #94a8ff; }
.c-3 { fill: #6280ff; }
.c-4 { fill: #2f55ff; }
.c-5 { fill: #1a3be0; }

@media (prefers-color-scheme: dark) {
  .bg { fill: #161b22; stroke: #30363d; stroke-width: 1px; }
  .ink { fill: #f0f6fc; }
  .soft { fill: #c9d1d9; }
  .muted { fill: #8b949e; }
  .rule { fill: #30363d; }
  .bar-default { fill: #8b949e; }
  .bar-partial { fill: #30363d; }
  .grad-base { stop-color: #f0f6fc; }

  .c-0 { fill: #21262d; }
  .c-1 { fill: #162c64; }
  .c-2 { fill: #1f4299; }
  .c-3 { fill: #2b5cd9; }
  .c-4 { fill: #487fff; }
  .c-5 { fill: #79a6ff; }
}

@media (prefers-reduced-motion: reduce){.r,.f,.g,.p,.live,.n,.nu,.ti,.sl,.ai,.ro,.rg{animation:none!important;opacity:1!important;transform:none!important}.sh,.rg{display:none}}
"""

def font_face(keys):
    out = []
    for k in keys:
        fam, style, weight, fn = FONT_FILES[k]
        path = os.path.join(FONTS, fn)
        if os.path.exists(path):
            b64 = base64.b64encode(open(path, "rb").read()).decode()
            out.append(f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:{weight};src:url(data:font/woff;base64,{b64}) format('woff')}}")
    return "".join(out)

def svg(w, h, body, fonts, label, left=0, right=0, bottom=12):
    if left: body = f'<g transform="translate({left:.3f} 0)">{body}</g>'
    w, h = w + left + right, h + bottom
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.3f}" height="{h}" viewBox="0 0 {w:.3f} {h}" role="img" aria-label="{escape(label)}"><title>{escape(label)}</title><style>{font_face(fonts) + BASE_CSS}</style>{body}</svg>'

def write(name, content):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f: f.write(content)

def d(s): return f'style="animation-delay:{s:.2f}s"'
def wrap(text, n):
    lines, line = [], ""
    for w in text.split():
        if line and len(line) + 1 + len(w) > n: lines.append(line); line = w
        else: line = f"{line} {w}".strip()
    return lines + [line] if line else lines

def text_lines(x, y, lines, lh, attrs):
    return "".join(f'<text x="{x}" y="{y + i * lh}" {attrs}>{escape(l)}</text>' for i, l in enumerate(lines))

def hero():
    h = 420
    portrait_svg = ""
    photo = os.path.join(ROOT, "portrait.jpg")
    if os.path.exists(photo):
        img_b64 = base64.b64encode(open(photo, "rb").read()).decode()
        portrait_svg = f"""
        <defs><clipPath id="circle-photo"><circle cx="680" cy="210" r="130"/></clipPath></defs>
        <circle cx="680" cy="210" r="135" fill="none" stroke="{TECH}" stroke-width="2.5" class="live"/>
        <image href="data:image/jpeg;base64,{img_b64}" x="550" y="80" width="260" height="260" clip-path="url(#circle-photo)" preserveAspectRatio="xMidYMid slice" class="f" {d(0.3)}/>
        """
    body = f"""
<defs>
  <linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="600" y2="0">
    <stop offset="0" class="grad-base"/><stop offset=".42" class="grad-base"/>
    <stop offset=".5" stop-color="{TECH}"/><stop offset=".58" class="grad-base"/>
    <stop offset="1" class="grad-base"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="-600 0;600 0;600 0" keyTimes="0;.45;1" dur="7s" begin="1.6s" repeatCount="indefinite"/>
  </linearGradient>
</defs>
<rect width="{W}" height="{h}" rx="14" class="bg"/>
<g class="f" {d(0)}>
  <rect class="live" x="48" y="49" width="8" height="8" rx="2" fill="{TECH}"/>
  <text x="66" y="57" font-family="{MONO}" font-size="12" letter-spacing="1" class="muted">FULL-STACK ARCHITECT &amp; AI SPECIALIST</text>
</g>
<text class="r ink" {d(0.15)} x="44" y="190" font-family="{SERIF}" font-size="116" letter-spacing="-2.5">Bilal</text>
<text class="r" {d(0.3)} x="44" y="290" font-family="{SERIF}" font-style="italic" font-size="116" letter-spacing="-2.5" fill="url(#shine)">Nadeem</text>
<g class="r" {d(0.55)}>
  {text_lines(48, 338, ["Building scalable web applications, intelligent automation,", "and modern cloud systems."], 27, f'font-family="{SANS}" font-size="18" class="soft"')}
</g>
<g class="f" {d(0.8)}>
  <text x="48" y="396" font-family="{MONO}" font-size="13" class="ink">github.com/MBN4</text>
  <text class="nu" x="186" y="396" font-family="{MONO}" font-size="13" fill="{TECH}">&#8599;</text>
</g>
{portrait_svg}
"""
    write("hero.svg", svg(W, h, body, ["serif", "serif-i", "sans", "mono"], "Bilal Nadeem"))

TILE_W, TILE_H = 880 / 3 - 8, 210
def count_up(num, word, x, y, attrs, begin, dur=1.1, frames=18):
    m = re.match(r"([\d.]+)(.*)", num)
    val = float(m.group(1)) if m else 0
    suf = m.group(2) if m else ""
    dec = len(m.group(1).split(".")[1]) if m and "." in m.group(1) else 0
    tail = f' <tspan font-style="italic">{escape(word)}</tspan>'
    out = []
    for i in range(frames + 1):
        e = 1 - (1 - i / frames) ** 3
        txt = num if i == frames else f"{val * e:.{dec}f}{suf}"
        on = begin + dur * i / frames
        off = "" if i == frames else f'<set attributeName="opacity" to="0" begin="{begin + dur * (i + 1) / frames:.3f}s"/>'
        out.append(f'<text x="{x}" y="{y}" {attrs} opacity="0">{escape(txt)}{tail}<set attributeName="opacity" to="1" begin="{on:.3f}s"/>{off}</text>')
    return "".join(out)

def tile(name, label, color, on, num, word, blurb, delay, pos):
    lines = wrap(blurb, 34)
    blurb_svg = "".join(f'<text class="r" {d(delay + 0.75 + i * 0.1)} x="24" y="{150 + i * 20}" font-family="{SANS}" font-size="14" fill="{on}" opacity=".92">{escape(l)}</text>' for i, l in enumerate(lines))
    body = f"""
<defs>
  <clipPath id="card-{name}"><rect width="{TILE_W}" height="{TILE_H}" rx="14"/></clipPath>
  <clipPath id="slot-{name}"><rect x="0" y="62" width="{TILE_W}" height="62"/></clipPath>
  <linearGradient id="gl-{name}" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".35"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
</defs>
<g class="ti" {d(delay)}>
  <g clip-path="url(#card-{name})">
    <rect width="{TILE_W}" height="{TILE_H}" fill="{color}"/>
    <circle class="rg" {d(delay + 0.5)} cx="{TILE_W - 40}" cy="{TILE_H - 40}" r="60" fill="none" stroke="{on}" stroke-opacity=".5" stroke-width="2"/>
    <rect class="sh" style="animation-delay:{delay + 1.4:.2f}s" x="0" y="-20" width="90" height="{TILE_H + 40}" fill="url(#gl-{name})" transform="translate(-260 0)"/>
  </g>
  <text class="sl" {d(delay + 0.35)} x="24" y="38" font-family="{MONO}" font-size="12" letter-spacing="1.2" fill="{on}">{label}</text>
  <g class="ai" {d(delay + 0.5)}><text class="n" style="animation-delay:{delay + 1.3:.2f}s" x="250" y="38" font-family="{MONO}" font-size="14" fill="{on}">&#8594;</text></g>
  <g clip-path="url(#slot-{name})"><g class="ro" {d(delay + 0.45)}>{count_up(num, word, 22, 112, f'font-family="{SERIF}" font-size="44" fill="{on}"', delay + 0.45)}</g></g>
  {blurb_svg}
</g>
"""
    write(f"{name}.svg", svg(TILE_W, TILE_H, body, ["serif", "serif-i", "sans", "mono"], f"{label}: {num} {word}", left=4 * pos, right=8 - 4 * pos))

def activity(data):
    h = 340
    monthly = data.get("monthly", [])[-12:]
    if not monthly: monthly = [{"month": "2024-01", "total": 1}]
    best = max(monthly, key=lambda m: m["total"])
    top = max(best["total"], 1)
    x0, x1, base, maxh, gap = 40, 600, 292, 140, 10
    bw = (x1 - x0 - gap * (len(monthly) - 1)) / len(monthly)
    bars = []
    for i, m in enumerate(monthly):
        partial = i == len(monthly) - 1
        is_best = m is best and m["total"] > 0
        bh = max(4, round(m["total"] / top * maxh))
        x = x0 + i * (bw + gap)
        fill_cls = 'fill="{}"'.format(TECH) if is_best else ('class="bar-partial"' if partial else 'class="bar-default"')
        label = datetime.date.fromisoformat(m["month"] + "-01").strftime("%b")
        bars.append(f'<rect class="g" {fill_cls} style="animation-delay:{2.2 + i * 0.07:.2f}s" x="{x:.1f}" y="{base - bh}" width="{bw:.1f}" height="{bh}" rx="4"><title>{label}: {m["total"]:,}</title></rect><text class="f muted" style="animation-delay:{2.2 + i * 0.07:.2f}s" x="{x + bw / 2:.1f}" y="{base + 22}" text-anchor="middle" font-family="{MONO}" font-size="11">{label}</text>')
        if is_best:
            bars.append(f'<text class="p" style="animation-delay:3.2s" x="{x + bw / 2:.1f}" y="{base - bh - 10}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{TECH}">{m["total"]:,}</text>')
    cs = data.get("current_streak", {}).get("length", 0)
    ls = data.get("longest_streak", {}).get("length", 0)
    streak_note = "current streak, and the longest" if cs >= ls else f"current streak, longest {ls}"
    total_days = len(data.get("days", [])) or 365
    stats = [
        (f'{cs} <tspan font-style="italic">days</tspan>', streak_note),
        (f'{data.get("active_days", 0)}<tspan class="muted"> / {total_days}</tspan>', "days with a commit"),
        (f'{data.get("best_day", {}).get("count", 0)}', "on the busiest day"),
    ]
    side = []
    for i, (big, small) in enumerate(stats):
        y = 104 + i * 92
        side.append(f'<g class="r" {d(2.6 + i * 0.15)}><text class="ink" x="650" y="{y}" font-family="{SERIF}" font-size="40">{big}</text><text class="muted" x="650" y="{y + 24}" font-family="{SANS}" font-size="13">{small}</text></g>')
        if i < 2: side.append(f'<rect class="f rule" {d(2.6)} x="650" y="{y + 44}" width="190" height="1"/>')
    body = f"""
<rect width="{W}" height="{h}" rx="14" class="bg"/>
<text class="f muted" {d(1.9)} x="40" y="58" font-family="{MONO}" font-size="12" letter-spacing="1">THE LAST 12 MONTHS ON GITHUB</text>
<text class="r ink" {d(2.0)} x="38" y="114" font-family="{SERIF}" font-size="52">{data.get("total_contributions", 0):,} <tspan font-style="italic">contributions</tspan></text>
{''.join(bars)}
{''.join(side)}
"""
    write("activity.svg", svg(W, h, body, ["serif", "serif-i", "sans", "mono"], "Activity"))

REPO_W, REPO_H = 880 / 3 - 8, 176
REPOS = [
    ("Ai-Business-Analyst", "AI-powered automated business analytics and data processing insights.", "JavaScript", TECH),
    ("circle-the-ai-universe", "Curated interactive universe platform exploring AI models & tools.", "TypeScript", STUDIO),
    ("ReelBite", "Interactive full-stack media platform with modern UX and APIs.", "JavaScript", LEARN),
]

def repo_card(i, name, desc, lang, color):
    delay = 4.6 + i * 0.12
    meta = f"{lang}  ·  public"
    body = f"""
<rect width="{REPO_W}" height="{REPO_H}" rx="14" class="bg"/>
<g class="r" {d(delay)}>
  <rect x="24" y="30" width="8" height="8" rx="2" fill="{color}"/>
  <text class="ink" x="40" y="39" font-family="{SANS}" font-weight="600" font-size="17">{escape(name)}</text>
  {text_lines(24, 72, wrap(desc, 34), 21, f'font-family="{SANS}" font-size="14" class="soft"')}
  <text class="muted" x="24" y="{REPO_H - 24}" font-family="{MONO}" font-size="12">{escape(meta)}</text>
</g>
"""
    write(f"repo-{name}.svg", svg(REPO_W, REPO_H, body, ["sans", "sans-b", "mono"], f"{name}: {desc}", left=4 * i, right=8 - 4 * i))

def section_title(text, italic, theme):
    fg = "#f0f6fc" if theme == "dark" else "#111111"
    body = f'<text class="r" {d(4.4)} x="2" y="46" font-family="{SERIF}" font-size="34" fill="{fg}">{escape(text)} <tspan font-style="italic">{escape(italic)}</tspan></text>'
    write(f"title-coding-{theme}.svg", svg(W, 64, body, ["serif", "serif-i"], f"{text} {italic}", bottom=0))

def level_for(c): return 0 if c == 0 else 1 if c <= 3 else 2 if c <= 8 else 3 if c <= 15 else 4 if c <= 25 else 5

def heatmap(data):
    days = data.get("days", [])
    if not days: return
    first = datetime.date.fromisoformat(days[0]["date"])
    lead = (first.weekday() + 1) % 7
    cell, step, gx, gy = 12, 15, 44, 96
    cells, months, seen = [], [], set()
    for i, day in enumerate(days):
        k = i + lead
        col, row = divmod(k, 7)
        date = datetime.date.fromisoformat(day["date"])
        if date.day <= 7 and (date.year, date.month) not in seen and row == 0:
            seen.add((date.year, date.month))
            months.append((col, date.strftime("%b")))
        c = day["count"]
        delay = 1.0 + col * 0.03 + row * 0.02
        cells.append(f'<rect class="p c-{level_for(c)}" style="animation-delay:{delay:.2f}s" x="{gx + col * step}" y="{gy + row * step}" width="{cell}" height="{cell}" rx="3"><title>{day["date"]}: {c} contributions</title></rect>')
    ncols = (len(days) + lead + 6) // 7
    right = gx + ncols * step - 3
    labels = "".join(f'<text class="muted" x="{gx + col * step}" y="{gy + 7 * step + 16}" font-family="{MONO}" font-size="11">{m}</text>' for col, m in months if col < ncols - 12)
    legend_x = right - 6 * 14
    legend = "".join(f'<rect class="c-{i}" x="{legend_x + i * 14}" y="{gy + 7 * step + 6}" width="11" height="11" rx="2.5"/>' for i in range(6))
    h = gy + 7 * step + 44
    body = f"""
<rect width="{W}" height="{h}" rx="14" class="bg"/>
<text class="r ink" {d(0.8)} x="42" y="62" font-family="{SERIF}" font-size="34">Every day, <tspan font-style="italic" fill="{TECH}">in blue</tspan></text>
<text class="f muted" {d(0.8)} x="{right}" y="60" text-anchor="end" font-family="{MONO}" font-size="12" letter-spacing="1">REFRESHED DAILY</text>
{''.join(cells)}
<g class="f" {d(2.4)}>{labels}
<text class="muted" x="{legend_x - 8}" y="{gy + 7 * step + 16}" text-anchor="end" font-family="{MONO}" font-size="11">less</text>
{legend}
<text class="muted" x="{legend_x + 6 * 14 + 2}" y="{gy + 7 * step + 16}" font-family="{MONO}" font-size="11">more</text></g>
"""
    write("heatmap.svg", svg(W, h, body, ["serif", "serif-i", "mono"], "Heatmap"))

if __name__ == "__main__":
    data = json.load(open(DATA)) if os.path.exists(DATA) else {}
    hero()
    tile("build", "BUILD", TECH, "#ffffff", "15+", "apps", "Production SaaS applications, modern full-stack web apps, and MVPs.", 3.1, 0)
    tile("brand", "AUTOMATE", STUDIO, "#ffffff", "50+", "workflows", "Autonomous AI pipelines, LLM agents, and business process automation.", 3.35, 1)
    tile("learn", "SCALE", LEARN, "#111111", "99.9%", "uptime", "Cloud-native microservices, database architecture, and resilient systems.", 3.6, 2)
    activity(data)
    for i, (name, desc, lang, color) in enumerate(REPOS):
        repo_card(i, name, desc, lang, color)
    section_title("What I'm", "coding", "dark")
    section_title("What I'm", "coding", "light")
    heatmap(data)
