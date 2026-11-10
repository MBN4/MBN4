#!/usr/bin/env python3
"""scripts/extras2.py - five more animated sections (needs scripts/extras.py next to it)."""
import datetime
import json
import math
import re

from extras import END, PALETTE, README, ROOT, THEMES, esc, pic, svg, write

START2, END2 = "<!-- extras2:start -->", "<!-- extras2:end -->"
BOTTOM = 12  # transparent breathing room under every card


def S(w, h, body):
    return svg(w, h + BOTTOM, body)


def kt(*v):
    return ";".join(f"{min(max(x, 0), 1):.4f}" for x in v)


def reveal(x0, y, n, start, cyc, ch, step, bg, W):
    """Typewriter reveal: a bg-coloured cover slides right (plain x/width animation)."""
    kts = [0.0, start / cyc] + [(start + k * step) / cyc for k in range(1, n + 1)]
    xs = [x0, x0] + [x0 + k * ch for k in range(1, n + 1)]
    k_s = ";".join(f"{k:.5f}" for k in kts)
    return (f'<rect x="{x0}" y="{y-17}" width="{W-12-x0}" height="25" fill="{bg}">'
            f'<animate attributeName="x" calcMode="discrete" values="{";".join(f"{v:.1f}" for v in xs)}" keyTimes="{k_s}" dur="{cyc}s" repeatCount="indefinite"/>'
            f'<animate attributeName="width" calcMode="discrete" values="{";".join(f"{W-12-v:.1f}" for v in xs)}" keyTimes="{k_s}" dur="{cyc}s" repeatCount="indefinite"/></rect>')


def cursor(events, cyc, color):
    ev_t = ";".join(f"{e[0]:.5f}" for e in events)
    return (f'<rect width="2" height="17" fill="{color}"><animate attributeName="x" calcMode="discrete" values="{";".join(f"{e[1]:.1f}" for e in events)}" keyTimes="{ev_t}" dur="{cyc}s" repeatCount="indefinite"/>'
            f'<animate attributeName="y" calcMode="discrete" values="{";".join(f"{e[2]:.1f}" for e in events)}" keyTimes="{ev_t}" dur="{cyc}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="1;0" calcMode="discrete" dur="1s" repeatCount="indefinite"/></rect>')


# ───────────────────────── 0. TERMINAL (fixed typing; overrides extras.py's) ─────────────────────────
def terminal_card2(t):
    from extras import TERMINAL
    W, X0, CH, STEP = 960, 58, 7.8, 0.045
    rows = []
    for cmd, out in TERMINAL:
        rows += [("cmd", cmd), ("out", out)]
    clock, sched = 0.6, []
    for kind, text in rows:
        sched.append((clock, kind, text))
        clock += len(text) * STEP + (0.35 if kind == "cmd" else 0.7)
    cyc = round(clock + 3.5, 2)
    H = 84 + len(rows) * 30 + 26
    o = [f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="{t["term"]}" stroke="{t["border"]}"/>',
         f'<path d="M1 14.5A13.5 13.5 0 0 1 14.5 1h{W-29}A13.5 13.5 0 0 1 {W-1} 14.5V44H1z" fill="{t["chip"]}"/>',
         f'<line x1="1" y1="44.5" x2="{W-1}" y2="44.5" stroke="{t["border"]}"/>']
    for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        o.append(f'<circle cx="{26+i*20}" cy="23" r="6" fill="{c}"/>')
    o.append(f'<text x="{W/2}" y="27" text-anchor="middle" class="mono" font-size="11" letter-spacing="1.2" fill="{t["mute"]}">~/MBN4 \u2014 ZSH</text>')
    events = [(0.0, X0, 84 - 13)]
    for i, (start, kind, text) in enumerate(sched):
        y, n = 84 + i * 30, len(text)
        if kind == "cmd":
            o.append(f'<text x="34" y="{y}" class="mono" font-size="13" fill="{t["accent"]}">$</text>')
        mark = "" if kind == "cmd" else f'<tspan fill="{t["accent"]}">\u2192 </tspan>'
        fill = t["ink"] if kind == "cmd" else t["mute"]
        o.append(f'<text x="{X0}" y="{y}" class="mono" font-size="13" fill="{fill}" xml:space="preserve">{mark}{esc(text)}</text>')
        o.append(reveal(X0, y, n + (2 if kind == "out" else 0), start, cyc, CH, STEP if kind == "cmd" else STEP * n / max(n + 2, 1), t["term"], W))
        events.append((start / cyc, X0, y - 13))
        for k in range(1, n + (2 if kind == "out" else 0) + 1):
            events.append(((start + k * (STEP if kind == "cmd" else STEP * n / max(n + 2, 1))) / cyc, X0 + k * CH, y - 13))
    o.append(cursor(events, cyc, t["accent"]))
    return S(W, H, "".join(o))


# ───────────────────────── 1. DEPLOY PIPELINE ─────────────────────────
def pipeline_card(t):
    W, H, Y, CYC = 960, 320, 214, 9
    xs = [96 + i * 153.6 for i in range(6)]
    steps = [("IDEA", "scope"), ("DESIGN", "system"), ("BUILD", "ship"), ("TEST", "trust"), ("DEPLOY", "cloud"), ("SCALE", "grow")]
    x0, x1 = xs[0], xs[-1]
    o = [f'<defs><filter id="gl" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="4"/></filter></defs>',
         f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="{t["bg"]}" stroke="{t["border"]}"/>',
         f'<text x="40" y="74" class="serif" font-size="42" fill="{t["ink"]}">From idea to</text>',
         f'<text x="40" y="122" class="serif" font-size="42" font-style="italic" fill="{t["accent"]}">production.</text>',
         f'<text x="{W-40}" y="60" text-anchor="end" class="mono" font-size="10.5" letter-spacing="2" fill="{t["mute"]}">CI/CD · CLOUD · OBSERVABILITY</text>',
         f'<line x1="{x0}" y1="{Y}" x2="{x1}" y2="{Y}" stroke="{t["border"]}" stroke-width="2" stroke-dasharray="4 8">'
         f'<animate attributeName="stroke-dashoffset" values="0;-24" dur="1.2s" repeatCount="indefinite"/></line>',
         f'<rect x="{x0}" y="{Y-1}" width="0" height="2" rx="1" fill="{t["accent"]}">'
         f'<animate attributeName="width" values="0;{x1-x0};{x1-x0};0" keyTimes="{kt(0,.8,.96,1)}" dur="{CYC}s" repeatCount="indefinite"/></rect>']
    for i, (x, (lab, sub)) in enumerate(zip(xs, steps)):
        f = 0.8 * i / 5
        a, b, c = f, f + 0.02, f + 0.14
        o.append(
            f'<circle cx="{x}" cy="{Y}" r="25" fill="{t["accent"]}" fill-opacity=".06" stroke="{t["border"]}" stroke-width="1.5">'
            f'<animate attributeName="fill-opacity" values=".06;.06;.5;.12;.06" keyTimes="{kt(0,a,b,c,1)}" dur="{CYC}s" repeatCount="indefinite"/>'
            f'<animate attributeName="stroke" values="{t["border"]};{t["border"]};{t["accent"]};{t["accent"]};{t["border"]}" keyTimes="{kt(0,a,b,c,1)}" dur="{CYC}s" repeatCount="indefinite"/></circle>'
            f'<circle cx="{x}" cy="{Y}" r="25" fill="none" stroke="{t["accent"]}" opacity="0">'
            f'<animate attributeName="r" values="25;25;50;50;25" keyTimes="{kt(0,a,c+.06,c+.07,1)}" dur="{CYC}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;0;.8;0;0" keyTimes="{kt(0,a,b,c+.06,1)}" dur="{CYC}s" repeatCount="indefinite"/></circle>'
            f'<text x="{x}" y="{Y+5}" text-anchor="middle" class="mono" font-size="13" fill="{t["ink"]}">0{i+1}</text>'
            f'<text x="{x}" y="{Y+58}" text-anchor="middle" class="mono" font-size="11" letter-spacing="2" fill="{t["ink"]}">{lab}</text>'
            f'<text x="{x}" y="{Y+78}" text-anchor="middle" class="sans" font-size="12" fill="{t["mute"]}">{sub}</text>')
    o.append(
        f'<g><animateMotion path="M{x0},{Y} H{x1}" keyPoints="0;1;1" keyTimes="{kt(0,.8,1)}" calcMode="linear" dur="{CYC}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="{kt(0,.8,.82,1)}" dur="{CYC}s" repeatCount="indefinite"/>'
        f'<circle r="11" fill="{t["accent"]}" opacity=".55" filter="url(#gl)"/><circle r="5" fill="{t["accent"]}"/></g>')
    return S(W, H, "".join(o))


# ───────────────────────── 2. CODE EDITOR ─────────────────────────
SYN = {"dark": dict(kw="#ff7b72", fn="#d2a8ff", str="#a5d6ff", cmt="#8b949e", num="#79c0ff"),
       "light": dict(kw="#cf222e", fn="#8250df", str="#0a3069", cmt="#6e7781", num="#0550ae")}
CODE = [
    [("import", "kw"), (" { agent, tool } ", "txt"), ("from", "kw"), (' "@mbn4/core"', "str"), (";", "txt")],
    [],
    [("// an agent that plans, acts and verifies", "cmt")],
    [("export const", "kw"), (" ship = ", "txt"), ("agent", "fn"), ("({", "txt")],
    [("  goal: ", "txt"), ('"turn an idea into production"', "str"), (",", "txt")],
    [("  tools: [tool.design, tool.build, tool.test, tool.deploy],", "txt")],
    [("  retries: ", "txt"), ("3", "num"), (",", "txt")],
    [("});", "txt")],
    [],
    [("await", "kw"), (" ship.", "txt"), ("run", "fn"), ("();", "txt"), ("  // ship it", "cmt")],
]


def code_card(t, mode):
    W, X0, CH, STEP, LH, Y0 = 960, 70, 7.8, 0.035, 24, 92
    syn = SYN[mode]
    H = Y0 + len(CODE) * LH + 40
    sched, clock = [], 0.7
    for i, line in enumerate(CODE):
        n = sum(len(x) for x, _ in line)
        if n:
            sched.append((i, clock, n))
            clock += n * STEP + 0.3
    cyc = round(clock + 4, 2)
    o = [f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="{t["term"]}" stroke="{t["border"]}"/>',
         f'<path d="M1 14.5A13.5 13.5 0 0 1 14.5 1h{W-29}A13.5 13.5 0 0 1 {W-1} 14.5V46H1z" fill="{t["chip"]}"/>',
         f'<line x1="1" y1="46.5" x2="{W-1}" y2="46.5" stroke="{t["border"]}"/>']
    for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        o.append(f'<circle cx="{26+i*20}" cy="24" r="6" fill="{c}"/>')
    o.append(f'<rect x="100" y="12" width="132" height="34" rx="8" fill="{t["term"]}"/>'
             f'<circle cx="118" cy="29" r="3.5" fill="{t["accent"]}"/>'
             f'<text x="130" y="33" class="mono" font-size="12" fill="{t["ink"]}">agent.ts</text>')
    events = [(0.0, X0, Y0 - 13)]
    for i, line in enumerate(CODE):
        y = Y0 + i * LH
        o.append(f'<text x="38" y="{y}" text-anchor="end" class="mono" font-size="12" fill="{t["mute"]}" opacity=".6">{i+1}</text>')
    ital = ' font-style="italic"'
    for i, start, n in sched:
        y = Y0 + i * LH
        spans = "".join(f'<tspan fill="{t["ink"] if k == "txt" else syn[k]}"{ital if k == "cmt" else ""}>{esc(x)}</tspan>' for x, k in CODE[i])
        o.append(f'<text x="{X0}" y="{y}" class="mono" font-size="13" xml:space="preserve">{spans}</text>')
        o.append(reveal(X0, y, n, start, cyc, CH, STEP, t["term"], W))
        events.append((start / cyc, X0, y - 13))
        events += [((start + k * STEP) / cyc, X0 + k * CH, y - 13) for k in range(1, n + 1)]
    o.append(cursor(events, cyc, t["accent"]))
    sb = H - 30
    o.append(f'<path d="M1 {sb}H{W-1}V{H-14.5}A13.5 13.5 0 0 1 {W-14.5} {H-1}H14.5A13.5 13.5 0 0 1 1 {H-14.5}z" fill="{t["chip"]}"/>'
             f'<circle cx="26" cy="{sb+15}" r="3.5" fill="{t["accent"]}"><animate attributeName="opacity" values="1;.3;1" dur="1.6s" repeatCount="indefinite"/></circle>'
             f'<text x="40" y="{sb+19}" class="mono" font-size="10.5" letter-spacing="1.5" fill="{t["mute"]}">MAIN · TYPESCRIPT · UTF-8</text>'
             f'<text x="{W-26}" y="{sb+19}" text-anchor="end" class="mono" font-size="10.5" letter-spacing="1.5" fill="{t["mute"]}">0 ERRORS · READY TO SHIP</text>')
    return S(W, H, "".join(o))


# ───────────────────────── 3. NEURAL NETWORK ─────────────────────────
def neural_card(t):
    W, H = 960, 400
    layers, lx = [4, 6, 6, 3], [380, 560, 740, 900]
    names = ["INPUT", "REASON", "RETRIEVE", "ACT"]
    pos = []
    for n, x in zip(layers, lx):
        y0 = H / 2 - (n - 1) * 56 / 2 - 6
        pos.append([(x, y0 + i * 56) for i in range(n)])
    o = [f'<defs><filter id="gl" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="3.5"/></filter></defs>',
         f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="{t["bg"]}" stroke="{t["border"]}"/>',
         f'<text x="40" y="96" class="serif" font-size="46" fill="{t["ink"]}">Intelligence,</text>',
         f'<text x="40" y="146" class="serif" font-size="46" font-style="italic" fill="{t["accent"]}">wired in.</text>',
         f'<text x="42" y="186" class="sans" font-size="14" fill="{t["mute"]}">LLM agents, retrieval and automation,</text>',
         f'<text x="42" y="206" class="sans" font-size="14" fill="{t["mute"]}">connected end to end.</text>',
         f'<text x="42" y="{H-34}" class="mono" font-size="10.5" letter-spacing="2" fill="{t["mute"]}">AGENTS · RAG · PIPELINES</text>']
    for L in range(3):
        for a in pos[L]:
            for b in pos[L + 1]:
                o.append(f'<line x1="{a[0]}" y1="{a[1]:.1f}" x2="{b[0]}" y2="{b[1]:.1f}" stroke="{t["border"]}" stroke-width="1"/>')
    k = 0
    for L in range(3):
        for i, a in enumerate(pos[L]):
            for j, b in enumerate(pos[L + 1]):
                if (L * 5 + i * 7 + j * 3) % 4 == 0:
                    dur, beg, col = 2.2 + (k % 4) * 0.4, (k * 0.41) % 3.3, PALETTE[k % 3]
                    o.append(f'<g opacity="0"><animateMotion path="M{a[0]},{a[1]:.1f} L{b[0]},{b[1]:.1f}" dur="{dur}s" begin="{beg:.2f}s" repeatCount="indefinite"/>'
                             f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.15;.85;1" dur="{dur}s" begin="{beg:.2f}s" repeatCount="indefinite"/>'
                             f'<circle r="8" fill="{col}" opacity=".55" filter="url(#gl)"/><circle r="3" fill="{col}"/></g>')
                    k += 1
    for L, layer in enumerate(pos):
        for i, (x, y) in enumerate(layer):
            fill = t["accent"] if L == 3 else t["bg"]
            o.append(f'<circle cx="{x}" cy="{y:.1f}" r="7" fill="{fill}" stroke="{t["accent"]}" stroke-width="1.6">'
                     f'<animate attributeName="r" values="7;9.5;7" dur="3s" begin="{(L*.5+i*.23)%3:.2f}s" repeatCount="indefinite"/></circle>')
        o.append(f'<text x="{lx[L]}" y="{H-34}" text-anchor="middle" class="mono" font-size="10" letter-spacing="1.8" fill="{t["mute"]}">{names[L]}</text>')
    return S(W, H, "".join(o))


# ───────────────────────── 4. WEEKLY RHYTHM (real data) ─────────────────────────
def rhythm_card(t):
    p = ROOT / "data" / "contributions.json"
    if not p.exists():
        return None
    days = json.load(open(p)).get("days", [])
    if not days:
        return None
    tot = [0] * 7
    for d in days:
        tot[datetime.date.fromisoformat(d["date"]).weekday()] += d["count"]
    s, mx = sum(tot) or 1, max(tot) or 1
    ab = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    full = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    peak = tot.index(mx)
    wk = round((tot[5] + tot[6]) / s * 100)
    W, H, cx, cy, R0, RM = 960, 440, 640, 220, 48, 124
    o = [f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="{t["bg"]}" stroke="{t["border"]}"/>',
         f'<text x="40" y="100" class="serif" font-size="46" fill="{t["ink"]}">A week in</text>',
         f'<text x="40" y="150" class="serif" font-size="46" font-style="italic" fill="{t["accent"]}">commits.</text>',
         f'<text x="42" y="194" class="sans" font-size="14" fill="{t["mute"]}">{full[peak]} is the busiest day:</text>',
         f'<text x="42" y="214" class="sans" font-size="14" fill="{t["mute"]}">{round(mx/s*100)}% of everything I ship.</text>',
         f'<text x="42" y="244" class="sans" font-size="14" fill="{t["mute"]}">Weekends carry {wk}%.</text>',
         f'<text x="42" y="{H-34}" class="mono" font-size="10.5" letter-spacing="2" fill="{t["mute"]}">LIVE FROM MY CONTRIBUTION DATA</text>']
    for r in (R0 + RM * .33, R0 + RM * .66):
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{r:.0f}" stroke="{t["border"]}" stroke-dasharray="2 6"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{R0+RM+8}" stroke="{t["border"]}" stroke-width="1.2" stroke-dasharray="3 9">'
             f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="60s" repeatCount="indefinite"/></circle>')
    for i in range(7):
        ang = i * 360 / 7
        ln = max(6, tot[i] / mx * RM)
        col = t["accent"] if i == peak else t["mute"]
        op = "1" if i == peak else ".55"
        top = cy - R0 - ln
        o.append(f'<g transform="rotate({ang:.2f} {cx} {cy})"><rect x="{cx-11}" y="{cy-R0}" width="22" height="0" rx="11" fill="{col}" opacity="{op}">'
                 f'<animate attributeName="height" values="0;{ln:.1f};{ln:.1f};0" keyTimes="{kt(0,.22,.86,1)}" dur="9s" begin="{i*0.12:.2f}s" repeatCount="indefinite" calcMode="spline" keySplines=".2 .8 .2 1;0 0 1 1;.6 0 .8 .2"/>'
                 f'<animate attributeName="y" values="{cy-R0};{top:.1f};{top:.1f};{cy-R0}" keyTimes="{kt(0,.22,.86,1)}" dur="9s" begin="{i*0.12:.2f}s" repeatCount="indefinite" calcMode="spline" keySplines=".2 .8 .2 1;0 0 1 1;.6 0 .8 .2"/></rect></g>')
        a = math.radians(ang)
        lr = R0 + RM + 34
        lxp, lyp = cx + lr * math.sin(a), cy - lr * math.cos(a)
        o.append(f'<text x="{lxp:.1f}" y="{lyp:.1f}" text-anchor="middle" class="mono" font-size="11" letter-spacing="1.5" fill="{t["ink"] if i == peak else t["mute"]}">{ab[i].upper()}</text>'
                 f'<text x="{lxp:.1f}" y="{lyp+14:.1f}" text-anchor="middle" class="mono" font-size="10" fill="{t["mute"]}">{round(tot[i]/s*100)}%</text>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{R0-8}" fill="{t["accent"]}" fill-opacity=".08" stroke="{t["accent"]}"/>'
             f'<circle cx="{cx}" cy="{cy}" r="{R0-8}" fill="none" stroke="{t["accent"]}"><animate attributeName="r" values="{R0-8};{R0+22}" dur="3s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values=".7;0" dur="3s" repeatCount="indefinite"/></circle>'
             f'<text x="{cx}" y="{cy+8}" text-anchor="middle" class="serif" font-size="26" font-style="italic" fill="{t["ink"]}">{ab[peak]}</text>')
    return S(W, H, "".join(o))


# ───────────────────────── 5. AURORA CALL-TO-ACTION ─────────────────────────
def linkedin():
    try:
        m = re.search(r'LINKEDIN_URL\s*=\s*"([^"]+)"', (ROOT / "scripts" / "render_readme_cards.py").read_text())
        return m.group(1) if m else "https://github.com/MBN4"
    except Exception:
        return "https://github.com/MBN4"


def cta_card(t, mode):
    W, H = 960, 270
    op = ".5" if mode == "dark" else ".38"
    blobs = [(180, 90, PALETTE[0], 120, 18), (520, 210, PALETTE[1], 100, 22), (820, 80, PALETTE[2], 110, 26)]
    o = [f'<defs><clipPath id="cl"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14"/></clipPath>'
         f'<filter id="bl" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="42"/></filter>'
         f'<linearGradient id="sw" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".18"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>',
         f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="{t["bg"]}" stroke="{t["border"]}"/>', '<g clip-path="url(#cl)">']
    for i, (x, y, c, r, d) in enumerate(blobs):
        o.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}" opacity="{op}" filter="url(#bl)">'
                 f'<animate attributeName="cx" values="{x};{x+(90 if i%2==0 else -90)};{x}" dur="{d}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="cy" values="{y};{y+(50 if i!=1 else -60)};{y}" dur="{d*.8:.1f}s" repeatCount="indefinite"/></circle>')
    o.append(f'<rect x="-200" y="0" width="160" height="{H}" fill="url(#sw)" transform="skewX(-20)"><animate attributeName="x" values="-200;1200" dur="6s" repeatCount="indefinite"/></rect></g>')
    o += [f'<circle cx="52" cy="54" r="4" fill="{t["accent"]}"><animate attributeName="opacity" values="1;.25;1" dur="1.6s" repeatCount="indefinite"/></circle>',
          f'<text x="68" y="58" class="mono" font-size="11" letter-spacing="2.5" fill="{t["ink"]}">OPEN TO COLLABORATION</text>',
          f'<text x="48" y="128" class="serif" font-size="58" fill="{t["ink"]}">Let\'s build something</text>',
          f'<text x="48" y="188" class="serif" font-size="58" font-style="italic" fill="{t["accent"]}">remarkable.</text>',
          f'<rect x="{W-300}" y="{H-92}" width="252" height="46" rx="23" fill="{t["bg"]}" fill-opacity=".75" stroke="{t["accent"]}" stroke-width="1.5"/>',
          f'<text x="{W-174}" y="{H-63}" text-anchor="middle" class="mono" font-size="13" letter-spacing="1" fill="{t["ink"]}">SAY HELLO</text>',
          f'<text x="{W-80}" y="{H-62}" class="mono" font-size="17" fill="{t["accent"]}">→<animateTransform attributeName="transform" type="translate" values="0 0;6 0;0 0" dur="1.6s" repeatCount="indefinite"/></text>']
    return S(W, H, "".join(o))


# ───────────────────────── README + MAIN ─────────────────────────
def inject(block):
    text = README.read_text(encoding="utf-8")
    new = f"{START2}\n{block}\n{END2}"
    if START2 in text and END2 in text:
        text = re.sub(re.escape(START2) + r".*?" + re.escape(END2), lambda m: new, text, flags=re.S)
    elif END in text:
        text = text.replace(END, END + "\n" + new, 1)
    else:
        text += "\n" + new + "\n"
    README.write_text(text, encoding="utf-8")


def main():
    made = []
    for mode, t in THEMES.items():
        cards = [("sect-terminal", terminal_card2(t)), ("sect-pipeline", pipeline_card(t)), ("sect-code", code_card(t, mode)), ("sect-neural", neural_card(t)),
                 ("sect-rhythm", rhythm_card(t)), ("sect-cta", cta_card(t, mode))]
        for name, content in cards:
            if content:
                write(name, mode, content)
                if name not in made and name != "sect-terminal":
                    made.append(name)
    alts = {"sect-pipeline": "From idea to production", "sect-code": "agent.ts", "sect-neural": "Intelligence, wired in",
            "sect-rhythm": "A week in commits", "sect-cta": "Let's build something remarkable"}
    parts = []
    for n in made:
        href = linkedin() if n == "sect-cta" else None
        parts.append('<div align="center">\n' + pic(n, alts[n], "100%", href) + "\n</div>")
    inject("\n".join(parts))
    print(f"extras2: {len(made)} extra sections written ({', '.join(made)})")


if __name__ == "__main__":
    main()
