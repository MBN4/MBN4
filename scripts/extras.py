#!/usr/bin/env python3
import base64, html, json, math, os, re, textwrap, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CARDS, FONTS, README = ROOT / "cards", ROOT / "fonts", ROOT / "README.md"
USER = "MBN4"

# ==============================================================================
# EDIT HERE: pick ANY projects, in ANY order (1-9). 4 = 2x2 grid, 6 = 2 rows of 3.
# desc/lang are optional: if you leave them out they are pulled from GitHub.
# ==============================================================================
SHOWCASE = [
    {"name": "Ai-Business-Analyst", "color": "#3fb950", "lang": "JavaScript",
     "desc": "AI-powered automated business analytics and data processing insights."},
    {"name": "circle-the-ai-universe", "color": "#ef3b2d", "lang": "TypeScript",
     "desc": "Curated interactive universe platform exploring AI models & tools."},
    {"name": "ReelBite", "color": "#ffc81a", "lang": "JavaScript",
     "desc": "Interactive full-stack media platform with modern UX and APIs."},
    {"name": "Kitchens", "color": "#3fb950", "lang": "JavaScript",
     "desc": "Full-stack kitchen order & inventory management cloud system."},
    # {"name": "npm", "color": "#ef3b2d"},
    # {"name": "clipforge", "color": "#ffc81a"},
]

TERMINAL = [  # (command, output)
    ("whoami",         "bilal nadeem - full-stack architect & ai specialist"),
    ("cat stack.txt",  "typescript . python . next.js . node . llm agents"),
    ("./status --now", "shipping daily - open to interesting problems"),
]
TECH_ROW_1 = ["TypeScript", "Next.js", "React", "Node.js", "Python", "FastAPI", "PostgreSQL", "Redis"]
TECH_ROW_2 = ["LLM Agents", "RAG", "Docker", "AWS", "GitHub Actions", "Tailwind", "Prisma", "Microservices"]
ORBITS = [  # (radius, direction, seconds per turn, labels)
    (82,  1,  26, ["Python", "TypeScript"]),
    (140, -1, 40, ["Next.js", "Node.js", "FastAPI"]),
    (198, 1,  58, ["LLM Agents", "Docker", "AWS", "PostgreSQL"]),
]
# ==============================================================================

THEMES = {
    "light": dict(bg="#f3f3f1", border="#e2e2de", ink="#111111", mute="#6b6b66", accent="#2ea043", chip="#ebebe7", term="#fafaf8"),
    "dark":  dict(bg="#161b22", border="#30363d", ink="#f0f6fc", mute="#8b949e", accent="#3fb950", chip="#21262d", term="#0d1117"),
}
PALETTE = ["#3fb950", "#ef3b2d", "#ffc81a"]
esc = html.escape
slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def _font_css():
    faces = [("Instrument Serif", "serif-400.woff", 400, "normal"), ("Instrument Serif", "serif-italic.woff", 400, "italic"),
             ("Geist", "geist-400.woff", 400, "normal"), ("Geist", "geist-600.woff", 600, "normal"),
             ("Geist Mono", "geistmono-400.woff", 400, "normal")]
    css = ""
    for fam, f, w, st in faces:
        p = FONTS / f
        if p.exists():
            b = base64.b64encode(p.read_bytes()).decode()
            css += f"@font-face{{font-family:'{fam}';font-weight:{w};font-style:{st};src:url(data:font/woff;base64,{b}) format('woff');}}"
    return css

FONT_CSS = _font_css()
BASE_CSS = (".serif{font-family:'Instrument Serif',Georgia,serif}.sans{font-family:'Geist',-apple-system,Segoe UI,sans-serif}"
            ".mono{font-family:'Geist Mono',ui-monospace,Menlo,monospace}")

def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none">'
            f'<style>{FONT_CSS}{BASE_CSS}</style>{body}</svg>')

def write(name, mode, content):
    CARDS.mkdir(exist_ok=True)
    (CARDS / f"{name}-{mode}.svg").write_text(content, encoding="utf-8")

def fetch_meta(name):
    headers = {"User-Agent": "mbn4-profile", "Accept": "application/vnd.github+json"}
    tok = os.environ.get("GITHUB_TOKEN")
    if tok: headers["Authorization"] = f"Bearer {tok}"
    try:
        req = urllib.request.Request(f"https://api.github.com/repos/{USER}/{name}", headers=headers)
        with urllib.request.urlopen(req, timeout=15) as r: d = json.load(r)
        return {"desc": d.get("description") or "", "lang": d.get("language") or "", "stars": d.get("stargazers_count", 0)}
    except Exception as e:
        print(f"  ! meta for {name} unavailable ({e})")
        return {}

def title_card(t, lead, italic):
    body = (f'<text x="12" y="46" class="serif" font-size="40" fill="{t["ink"]}">{esc(lead)} '
            f'<tspan font-style="italic" fill="{t["accent"]}">{esc(italic)}</tspan></text>'
            f'<rect x="12" y="58" width="0" height="2" rx="1" fill="{t["accent"]}">'
            f'<animate attributeName="width" values="0;80;80" keyTimes="0;.35;1" dur="3s" fill="freeze"/></rect>')
    return svg(960, 70, body)

def repo_card(r, t, w, uid):
    M, H = 8, 150
    cw, ch = w - 2 * M, H - 2 * M
    col = r["color"]
    chars = max(24, int((cw - 44) / 6.9))
    full = textwrap.wrap(r["desc"] or "No description yet.", chars)
    lines = full[:2]
    if len(full) > 2: lines[1] = lines[1].rstrip(".,; ")[: chars - 1] + "…"
    desc = "".join(f'<text x="{M+22}" y="{M+64+i*20}" class="sans" font-size="13" fill="{t["mute"]}">{esc(l)}</text>' for i, l in enumerate(lines))
    meta = " · ".join(x for x in [r.get("lang", "").upper(), f'★ {r["stars"]}' if r.get("stars") else "", "PUBLIC"] if x)
    body = f"""
<defs>
  <clipPath id="c{uid}"><rect x="{M}" y="{M}" width="{cw}" height="{ch}" rx="12"/></clipPath>
  <linearGradient id="g{uid}" x1="0" x2="1"><stop offset="0" stop-color="{col}" stop-opacity="0"/>
    <stop offset=".5" stop-color="{col}"/><stop offset="1" stop-color="{col}" stop-opacity="0"/></linearGradient>
</defs>
<rect x="{M}.5" y="{M}.5" width="{cw-1}" height="{ch-1}" rx="12" fill="{t["bg"]}" stroke="{t["border"]}"/>
<g clip-path="url(#c{uid})">
  <rect x="{M}" y="{M+ch-2}" width="140" height="2" fill="url(#g{uid})"><animate attributeName="x" values="{M-140};{M+cw}" dur="4.2s" repeatCount="indefinite"/></rect>
  <circle cx="{M+cw-30}" cy="{M+30}" r="70" fill="{col}" opacity=".06"><animate attributeName="r" values="60;82;60" dur="6s" repeatCount="indefinite"/></circle>
</g>
<circle cx="{M+28}" cy="{M+30}" r="4" fill="{col}"/>
<circle cx="{M+28}" cy="{M+30}" r="4" fill="none" stroke="{col}">
  <animate attributeName="r" values="4;11" dur="2.4s" repeatCount="indefinite"/><animate attributeName="opacity" values=".8;0" dur="2.4s" repeatCount="indefinite"/></circle>
<text x="{M+44}" y="{M+35}" class="sans" font-size="17" font-weight="600" fill="{t["ink"]}">{esc(r["name"])}</text>
<text x="{M+cw-26}" y="{M+34}" text-anchor="end" class="mono" font-size="15" fill="{col}">↗
  <animateTransform attributeName="transform" type="translate" values="0 0;2 -2;0 0" dur="2.4s" repeatCount="indefinite"/></text>
{desc}
<text x="{M+22}" y="{M+ch-20}" class="mono" font-size="10.5" letter-spacing="1.2" fill="{t["mute"]}">{esc(meta)}</text>"""
    return svg(w, H, body)

def terminal_card(t):
    W, X0, CH, STEP = 960, 58, 7.8, 0.045
    rows = []
    for cmd, out in TERMINAL: rows += [("cmd", cmd), ("out", out)]
    clock, sched = 0.6, []
    for kind, text in rows:
        sched.append((clock, kind, text))
        clock += len(text) * STEP + (0.35 if kind == "cmd" else 0.7)
    cycle = round(clock + 3.5, 2)
    H = 84 + len(rows) * 30 + 26
    parts = [f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="{t["term"]}" stroke="{t["border"]}"/>',
             f'<path d="M1 14.5A13.5 13.5 0 0 1 14.5 1h{W-29}A13.5 13.5 0 0 1 {W-1} 14.5V44H1z" fill="{t["chip"]}"/>',
             f'<line x1="1" y1="44.5" x2="{W-1}" y2="44.5" stroke="{t["border"]}"/>']
    for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{26+i*20}" cy="23" r="6" fill="{c}"/>')
    parts.append(f'<text x="{W/2}" y="27" text-anchor="middle" class="mono" font-size="11" letter-spacing="1.2" fill="{t["mute"]}">~/MBN4 — ZSH</text>')
    defs, last_x, last_y = "", 0, 0
    for i, (start, kind, text) in enumerate(sched):
        y, n = 84 + i * 30, len(text)
        if kind == "cmd":
            parts.append(f'<text x="34" y="{y}" class="mono" font-size="13" fill="{t["accent"]}">$</text>')
        fill = t["ink"] if kind == "cmd" else t["mute"]
        kts = ";".join(f"{k:.5f}" for k in [0.0, start / cycle] + [(start + k * STEP) / cycle for k in range(1, n + 1)])
        vs = ";".join(str(v) for v in [0, 0] + [round(k * CH, 1) for k in range(1, n + 1)])
        defs += (f'<clipPath id="t{i}"><rect x="{X0}" y="{y-16}" width="0" height="24"><animate attributeName="width" calcMode="discrete" '
                 f'values="{vs}" keyTimes="{kts}" dur="{cycle}s" repeatCount="indefinite"/></rect></clipPath>')
        mark = "" if kind == "cmd" else f'<tspan fill="{t["accent"]}">→ </tspan>'
        parts.append(f'<g clip-path="url(#t{i})"><text x="{X0}" y="{y}" class="mono" font-size="13" fill="{fill}" xml:space="preserve">{mark}{esc(text)}</text></g>')
        last_x, last_y = X0 + (n + (2 if kind == "out" else 0)) * CH, y
    parts.append(f'<rect x="{last_x+4}" y="{last_y-12}" width="8" height="16" fill="{t["accent"]}">'
                 f'<animate attributeName="opacity" values="1;0" calcMode="discrete" dur="1s" repeatCount="indefinite"/></rect>')
    return svg(W, H, f"<defs>{defs}</defs>" + "".join(parts))

def marquee_card(t):
    W, H, GAP = 960, 176, 12
    def row(items, y, direction, speed, off):
        widths = [len(s) * 7.4 + 40 for s in items]
        total = sum(widths) + GAP * len(items)
        copies, chips, x = math.ceil(W / total) + 1, [], 0
        for _ in range(copies):
            for i, (s, w) in enumerate(zip(items, widths)):
                c = PALETTE[(i + off) % 3]
                chips.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="36" rx="18" fill="{t["chip"]}" stroke="{t["border"]}"/>'
                             f'<circle cx="{x+18:.1f}" cy="{y+18}" r="3.5" fill="{c}"/>'
                             f'<text x="{x+30:.1f}" y="{y+22.5}" class="mono" font-size="12" fill="{t["ink"]}">{esc(s)}</text>')
                x += w + GAP
        a, b = (0, -total) if direction < 0 else (-total, 0)
        return (f'<g><animateTransform attributeName="transform" type="translate" from="{a} 0" to="{b} 0" dur="{total/speed:.1f}s" repeatCount="indefinite"/>{"".join(chips)}</g>')
    body = f"""
<defs><clipPath id="mq"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14"/></clipPath>
<linearGradient id="fl"><stop offset="0" stop-color="{t["bg"]}"/><stop offset="1" stop-color="{t["bg"]}" stop-opacity="0"/></linearGradient>
<linearGradient id="fr"><stop offset="0" stop-color="{t["bg"]}" stop-opacity="0"/><stop offset="1" stop-color="{t["bg"]}"/></linearGradient></defs>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="{t["bg"]}" stroke="{t["border"]}"/>
<text x="28" y="34" class="mono" font-size="10.5" letter-spacing="2" fill="{t["mute"]}">TOOLBOX · ALWAYS IN MOTION</text>
<g clip-path="url(#mq)">{row(TECH_ROW_1, 52, -1, 38, 0)}{row(TECH_ROW_2, 106, 1, 30, 1)}
<rect x="0" y="40" width="110" height="{H-40}" fill="url(#fl)"/><rect x="{W-110}" y="40" width="110" height="{H-40}" fill="url(#fr)"/></g>"""
    return svg(W, H, body)

def orbit_card(t):
    W, H = 960, 440
    cx, cy = W / 2 + 120, H / 2 + 6
    out = [f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="{t["bg"]}" stroke="{t["border"]}"/>',
           f'<text x="40" y="82" class="serif" font-size="46" fill="{t["ink"]}">The stack,</text>',
           f'<text x="40" y="132" class="serif" font-size="46" font-style="italic" fill="{t["accent"]}">in orbit.</text>',
           f'<text x="42" y="170" class="sans" font-size="14" fill="{t["mute"]}">Languages, frameworks and infra I reach for</text>',
           f'<text x="42" y="190" class="sans" font-size="14" fill="{t["mute"]}">when an idea has to survive production.</text>',
           f'<text x="42" y="{H-34}" class="mono" font-size="10.5" letter-spacing="2" fill="{t["mute"]}">SCALE · AUTOMATE · BUILD</text>']
    for r, d, sec, labels in ORBITS:
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" stroke="{t["border"]}" stroke-width="1.2" stroke-dasharray="3 7">'
                   f'<animate attributeName="stroke-dashoffset" values="0;{-100*d}" dur="{sec/2}s" repeatCount="indefinite"/></circle>')
    for ri, (r, d, sec, labels) in enumerate(ORBITS):
        for i, lab in enumerate(labels):
            ang = 360 / len(labels) * i + ri * 47
            col, w = PALETTE[(ri + i) % 3], len(lab) * 7.2 + 26
            a0, a1 = (0, 360) if d > 0 else (360, 0)
            c0, c1 = (0, -360) if d > 0 else (-360, 0)
            out.append(
                f'<g transform="rotate({ang} {cx} {cy})"><g>'
                f'<animateTransform attributeName="transform" type="rotate" from="{a0} {cx} {cy}" to="{a1} {cx} {cy}" dur="{sec}s" repeatCount="indefinite"/>'
                f'<g transform="translate({cx+r} {cy})"><g>'
                f'<animateTransform attributeName="transform" type="rotate" from="{c0}" to="{c1}" dur="{sec}s" repeatCount="indefinite"/>'
                f'<g transform="rotate({-ang})">'
                f'<rect x="{-w/2:.1f}" y="-14" width="{w:.1f}" height="28" rx="14" fill="{t["bg"]}" stroke="{col}"/>'
                f'<circle cx="{-w/2+13:.1f}" cy="0" r="3" fill="{col}"/>'
                f'<text x="{-w/2+22:.1f}" y="4" class="mono" font-size="11" fill="{t["ink"]}">{esc(lab)}</text>'
                f'</g></g></g></g></g>')
    out.append(f"""<circle cx="{cx}" cy="{cy}" r="40" fill="{t["accent"]}" fill-opacity=".1" stroke="{t["accent"]}"/>
<circle cx="{cx}" cy="{cy}" r="40" stroke="{t["accent"]}"><animate attributeName="r" values="40;70" dur="3s" repeatCount="indefinite"/>
<animate attributeName="opacity" values=".7;0" dur="3s" repeatCount="indefinite"/></circle>
<text x="{cx}" y="{cy+10}" text-anchor="middle" class="serif" font-size="30" font-style="italic" fill="{t["ink"]}">B.N</text>""")
    return svg(W, H, "".join(out))

START, END = "<!-- extras:start -->", "<!-- extras:end -->"
OLD = [re.compile(r'(?:<a\b[^>]*>\s*)?<picture>(?:(?!</picture>).)*?cards/(?:repo-|title-coding)(?:(?!</picture>).)*?</picture>(?:\s*</a>)?(?:<br>)?', re.S),
       re.compile(r'(?:<a\b[^>]*>\s*)?<img[^>]*cards/(?:repo-|title-coding)[^>]*>(?:\s*</a>)?', re.S)]

def pic(name, alt, width, href=None):
    p = (f'<picture><source media="(prefers-color-scheme: dark)" srcset="./cards/{name}-dark.svg">'
         f'<img src="./cards/{name}-light.svg" alt="{esc(alt)}" width="{width}"></picture>')
    return f'<a href="{href}">{p}</a>' if href else p

def inject(block):
    text = README.read_text(encoding="utf-8")
    new = f"{START}\n{block}\n{END}"
    if START in text and END in text:
        text = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda m: new, text, flags=re.S)
    else:
        pos = None
        for pat in OLD:
            m = pat.search(text)
            if m and (pos is None or m.start() < pos): pos = m.start()
            text = pat.sub("", text)
        if pos is None: pos = len(text)
        text = text[:pos] + new + "\n" + text[pos:]
    README.write_text(text, encoding="utf-8")

def main():
    n = len(SHOWCASE)
    cols = 3 if n % 3 == 0 else 2
    card_w = {3: 320, 2: 480, 1: 960}
    pct = {3: "32.5%", 2: "49%", 1: "99%"}
    repos = []
    for i, r in enumerate(SHOWCASE):
        need = not (r.get("desc") and r.get("lang"))
        m = fetch_meta(r["name"]) if need else {}
        repos.append({"name": r["name"], "color": r.get("color", PALETTE[i % 3]),
                      "desc": r.get("desc") or m.get("desc", ""), "lang": r.get("lang") or m.get("lang", ""), "stars": m.get("stars", 0)})
    html_rows = []
    for i in range(0, n, cols):
        row = repos[i:i + cols]
        per = 1 if len(row) == 1 else cols
        cells = []
        for r in row:
            name = f"proj-{slug(r['name'])}"
            for mode, t in THEMES.items():
                write(name, mode, repo_card(r, t, card_w[per], f"{slug(r['name'])}{mode[0]}"))
            cells.append(pic(name, r["name"], pct[per], f"https://github.com/{USER}/{r['name']}"))
        html_rows.append('<div align="center">\n' + "\n".join(cells) + "\n</div>")
    for mode, t in THEMES.items():
        write("sect-projects", mode, title_card(t, "What I'm", "coding"))
        write("sect-terminal", mode, terminal_card(t))
        write("sect-marquee", mode, marquee_card(t))
        write("sect-orbit", mode, orbit_card(t))
    block = "\n".join([
        '<div align="center">', pic("sect-projects", "What I'm coding", "100%"), "</div>", *html_rows,
        '<br>', '<div align="center">', pic("sect-terminal", "Terminal", "100%"), "</div>",
        '<div align="center">', pic("sect-marquee", "Toolbox", "100%"), "</div>",
        '<div align="center">', pic("sect-orbit", "The stack, in orbit", "100%"), "</div>"])
    inject(block)
    print(f"extras: {n} projects ({cols} per row) + terminal, marquee, orbit written; README updated.")

if __name__ == "__main__":
    main()
