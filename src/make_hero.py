"""
make_hero.py  —  Nota.Lawyer unifying hero graphic (v3, restrained).

Design rules:
  * ONE accent (CockroachDB gold) for the database; GREEN only means "memory on / it worked".
    Agents are neutral slate cards (five of the same kind of thing) -- no rainbow.
  * Every string measured to fit inside its container (no spill).
  * The OFF->ON panel is self-explanatory: each row says what it measures, and a
    footer defines OFF vs ON honestly (persistence for 4 agents; isolation for Hold Firewall).

Output: docs/hero.png  (3200x1800, downscales cleanly for README + video)
"""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.abspath(os.path.join(HERE, "..", "docs", "hero.png"))
HTML = os.path.join(HERE, "_hero.html")
CHROME = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

W, H = 1600, 900

BG0 = "#0a0e13"
INK, MUT, DIM = "#e9edf2", "#9aa4b0", "#6e7681"
SLATE_BORDER = "#333c47"
GOLD, GRN, RED = "#f0b429", "#3fb950", "#f85149"

AGENTS = [  # name, role
    ("Cold Case",     "blind investigator"),
    ("Chronicle",     "case timeline"),
    ("Witness",       "contradictions"),
    ("Gap Hunter",    "missing documents"),
    ("Hold Firewall", "spoliation guard"),
]

# agent, what-it-measures, OFF value, ON value   (ON is always the better/green number)
ABLATION = [
    ("Cold Case",     "real fraud suspects found", "0",    "4/18"),
    ("Chronicle",     "timeline accuracy",         "0.42", "0.98"),
    ("Witness",       "contradictions retained",   "3",    "12/12"),
    ("Gap Hunter",    "withheld documents found",  "37%",  "100%"),
    ("Hold Firewall", "held docs preserved",       "0",    "200"),
]

PILLS = ["C-SPANN vectors", "363K-edge graph", "SERIALIZABLE", "RLS", "multi-region"]

# layout
CARD_W, CARD_H, CARD_Y = 172, 92, 178
CARD_X = [56 + i * 194 for i in range(5)]
CARD_CX = [x + CARD_W / 2 for x in CARD_X]
CONV = (530, 332)
CORE_X, CORE_Y, CORE_W, CORE_H = 150, 362, 760, 150
CORE_CX = CORE_X + CORE_W / 2
CF_X, CF_Y, CF_W, CF_H = 176, 560, 708, 120
RP_X, RP_Y, RP_W, RP_H = 1046, 178, 498, 502


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def card(x, name, role):
    cx = x + CARD_W / 2
    return f"""
  <g filter="url(#soft)">
    <rect x="{x}" y="{CARD_Y}" width="{CARD_W}" height="{CARD_H}" rx="14"
          fill="url(#card)" stroke="{SLATE_BORDER}" stroke-width="1.5"/>
  </g>
  <text x="{cx}" y="{CARD_Y+48}" text-anchor="middle" font-family="Inter" font-weight="800"
        font-size="24" fill="{INK}">{esc(name)}</text>
  <text x="{cx}" y="{CARD_Y+72}" text-anchor="middle" font-family="Inter" font-weight="500"
        font-size="14.5" fill="{MUT}" letter-spacing="0.3">{esc(role)}</text>"""


def connector(cx):
    y0 = CARD_Y + CARD_H
    return (f'<path d="M {cx} {y0} C {cx} {y0+42}, {CONV[0]} {CONV[1]-34}, {CONV[0]} {CONV[1]}" '
            f'fill="none" stroke="{GOLD}" stroke-width="2.4" stroke-linecap="round" opacity="0.34"/>')


def build_pills():
    gap = 14
    widths = [22 + len(t) * 9.5 for t in PILLS]
    total = sum(widths) + gap * (len(PILLS) - 1)
    x = CORE_CX - total / 2
    y = CORE_Y + CORE_H - 50
    out = []
    for t, w in zip(PILLS, widths):
        out.append(f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="34" rx="17" '
                   f'fill="#0c1118" stroke="#3a4048" stroke-width="1.2"/>')
        out.append(f'<text x="{x+w/2:.0f}" y="{y+23}" text-anchor="middle" '
                   f'font-family="JetBrains Mono" font-weight="600" font-size="15" '
                   f'fill="#c9d1d9">{esc(t)}</text>')
        x += w + gap
    return "\n  ".join(out)


def ablation_rows():
    # width-aware value placement so OFF / arrow / ON can never overlap.
    ON_FS, OFF_FS, AR_FS = 30, 23, 22
    GAP = 16
    right = RP_X + RP_W - 34          # right edge of the ON column
    rows = []
    n = len(ABLATION)
    top = RP_Y + 150
    bottom = RP_Y + RP_H - 66
    row_h = (bottom - top) / n
    for i, (name, metric, off, on) in enumerate(ABLATION):
        ry = top + i * row_h
        vy = ry + 34
        rows.append(f'<text x="{RP_X+34}" y="{ry+20:.0f}" font-family="Inter" font-weight="800" '
                    f'font-size="18" fill="{INK}">{esc(name)}</text>')
        rows.append(f'<text x="{RP_X+34}" y="{ry+41:.0f}" font-family="Inter" font-weight="500" '
                    f'font-size="14.5" fill="{MUT}">{esc(metric)}</text>')
        # fixed 3-column grid: OFF right-aligned | arrow centered | ON left-aligned
        arrow_cx = right - 120
        rows.append(f'<text x="{arrow_cx-24:.0f}" y="{vy:.0f}" text-anchor="end" '
                    f'font-family="JetBrains Mono" font-weight="700" font-size="{OFF_FS}" '
                    f'fill="{DIM}">{esc(off)}</text>')
        rows.append(f'<text x="{arrow_cx:.0f}" y="{vy-2:.0f}" text-anchor="middle" '
                    f'font-family="Inter" font-weight="700" font-size="{AR_FS}" '
                    f'fill="{MUT}">&#8594;</text>')
        rows.append(f'<text x="{arrow_cx+24:.0f}" y="{vy:.0f}" text-anchor="start" '
                    f'font-family="JetBrains Mono" font-weight="800" font-size="{ON_FS}" '
                    f'fill="{GRN}">{esc(on)}</text>')
        if i < n - 1:
            ly = top + (i + 1) * row_h
            rows.append(f'<line x1="{RP_X+34}" y1="{ly:.0f}" x2="{RP_X+RP_W-34}" y2="{ly:.0f}" '
                        f'stroke="#1c222a" stroke-width="1"/>')
    return "\n  ".join(rows)


svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<defs>
  <radialGradient id="bg" cx="28%" cy="14%" r="95%">
    <stop offset="0%" stop-color="#131c2b"/><stop offset="60%" stop-color="#0d1117"/>
    <stop offset="100%" stop-color="{BG0}"/>
  </radialGradient>
  <linearGradient id="card" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#151b23"/><stop offset="100%" stop-color="#0f141b"/>
  </linearGradient>
  <linearGradient id="corestroke" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#f7c948"/><stop offset="100%" stop-color="#c98a12"/>
  </linearGradient>
  <radialGradient id="coreglow" cx="50%" cy="50%" r="60%">
    <stop offset="0%" stop-color="#f0b429" stop-opacity="0.16"/>
    <stop offset="100%" stop-color="#f0b429" stop-opacity="0"/>
  </radialGradient>
  <filter id="soft" x="-40%" y="-40%" width="180%" height="180%">
    <feDropShadow dx="0" dy="5" stdDeviation="8" flood-color="#000" flood-opacity="0.42"/>
  </filter>
  <filter id="coreshadow" x="-30%" y="-30%" width="160%" height="160%">
    <feDropShadow dx="0" dy="9" stdDeviation="20" flood-color="#f0b429" flood-opacity="0.18"/>
  </filter>
</defs>

<rect width="{W}" height="{H}" fill="url(#bg)"/>

<text x="56" y="70" font-family="Inter" font-weight="800" font-size="19" fill="{GOLD}"
      letter-spacing="4">COCKROACHDB  E-DISCOVERY  SUITE</text>
<text x="54" y="119" font-family="Inter" font-weight="900" font-size="52" fill="{INK}"
      letter-spacing="-1.5">Nota<tspan fill="{GOLD}">.Lawyer</tspan></text>
<text x="56" y="151" font-family="Inter" font-weight="500" font-size="20" fill="{MUT}">Five specialized agents &#183; one transactional memory &#183; one unified case file</text>

{''.join(card(CARD_X[i], *AGENTS[i]) for i in range(5))}

  {chr(10).join(connector(CARD_CX[i]) for i in range(5))}
<circle cx="{CONV[0]}" cy="{CONV[1]}" r="5" fill="{GOLD}"/>
<path d="M {CONV[0]-8} {CONV[1]+3} L {CONV[0]+8} {CONV[1]+3} L {CONV[0]} {CONV[1]+15} Z" fill="{GOLD}"/>

<ellipse cx="{CORE_CX}" cy="{CORE_Y+CORE_H/2}" rx="450" ry="140" fill="url(#coreglow)"/>
<g filter="url(#coreshadow)">
  <rect x="{CORE_X}" y="{CORE_Y}" width="{CORE_W}" height="{CORE_H}" rx="22"
        fill="#12171e" stroke="url(#corestroke)" stroke-width="2.5"/>
</g>
<g transform="translate({CORE_X+54},{CORE_Y+50})" fill="none" stroke="{GOLD}" stroke-width="3">
  <ellipse cx="0" cy="0" rx="24" ry="9"/>
  <path d="M -24 0 V 30 A 24 9 0 0 0 24 30 V 0"/>
  <path d="M -24 15 A 24 9 0 0 0 24 15"/>
</g>
<text x="{CORE_X+102}" y="{CORE_Y+52}" font-family="Inter" font-weight="900" font-size="40"
      fill="{INK}" letter-spacing="-1">CockroachDB</text>
<text x="{CORE_X+104}" y="{CORE_Y+80}" font-family="Inter" font-weight="600" font-size="18.5"
      fill="{GOLD}">one transactional memory shared by all five agents</text>
{build_pills()}

<path d="M {CORE_CX} {CORE_Y+CORE_H} L {CORE_CX} {CF_Y-8}" stroke="{GOLD}" stroke-width="3"/>
<path d="M {CORE_CX-8} {CF_Y-14} L {CORE_CX+8} {CF_Y-14} L {CORE_CX} {CF_Y} Z" fill="{GOLD}"/>

<g filter="url(#soft)">
  <rect x="{CF_X}" y="{CF_Y}" width="{CF_W}" height="{CF_H}" rx="16"
        fill="#0f141b" stroke="#2f3743" stroke-width="1.5"/>
</g>
<text x="{CF_X+30}" y="{CF_Y+36}" font-family="Inter" font-weight="800" font-size="16"
      fill="{GOLD}" letter-spacing="2.5">UNIFIED CASE FILE &#183; ONE SQL STATEMENT</text>
<text x="{CF_X+30}" y="{CF_Y+70}" font-family="Inter" font-weight="800" font-size="23"
      fill="{INK}">Andrew Fastow &#8212; invisible in the email.</text>
<text x="{CF_X+30}" y="{CF_Y+99}" font-family="Inter" font-weight="500" font-size="19"
      fill="{MUT}">Cold Case flagged nothing. <tspan fill="{GRN}" font-weight="700">The other agents built his whole file.</tspan></text>

<g filter="url(#soft)">
  <rect x="{RP_X}" y="{RP_Y}" width="{RP_W}" height="{RP_H}" rx="20"
        fill="#0f141b" stroke="#2a3038" stroke-width="1.5"/>
</g>
<text x="{RP_X+34}" y="{RP_Y+50}" font-family="Inter" font-weight="900" font-size="27"
      fill="{INK}">Turn memory <tspan fill="{DIM}">off</tspan> <tspan fill="{MUT}">&#8594;</tspan> <tspan fill="{GRN}">on</tspan></text>
<text x="{RP_X+34}" y="{RP_Y+78}" font-family="Inter" font-weight="500" font-size="15.5"
      fill="{MUT}">same model &amp; data &#8212; the only variable is the database</text>
<line x1="{RP_X+34}" y1="{RP_Y+96}" x2="{RP_X+RP_W-34}" y2="{RP_Y+96}" stroke="#20262e" stroke-width="1"/>
<text x="{RP_X+34}" y="{RP_Y+126}" font-family="Inter" font-weight="700" font-size="13.5"
      fill="{DIM}" letter-spacing="1.5">AGENT &#183; WHAT IT MEASURES</text>
<text x="{RP_X+RP_W-34}" y="{RP_Y+126}" text-anchor="end" font-family="Inter" font-weight="700"
      font-size="13.5" fill="{DIM}" letter-spacing="1.5">OFF &#8594; ON</text>
{ablation_rows()}
<line x1="{RP_X+34}" y1="{RP_Y+RP_H-58}" x2="{RP_X+RP_W-34}" y2="{RP_Y+RP_H-58}" stroke="#20262e" stroke-width="1"/>
<text x="{RP_X+34}" y="{RP_Y+RP_H-34}" font-family="Inter" font-weight="500" font-size="13.5"
      fill="{DIM}">OFF = no persistent memory &#183; ON = CockroachDB memory</text>
<text x="{RP_X+34}" y="{RP_Y+RP_H-15}" font-family="Inter" font-weight="500" font-size="13.5"
      fill="{DIM}">Hold Firewall: READ COMMITTED &#8594; SERIALIZABLE isolation</text>
</svg>"""

html = f"""<!doctype html><html><head><meta charset=utf-8>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@600;700;800&display=swap');
*{{margin:0}} html,body{{width:{W}px;height:{H}px;overflow:hidden;background:{BG0}}}
</style></head><body>{svg}</body></html>"""

open(HTML, "w", encoding="utf-8").write(html)
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
    f"--window-size={W},{H}", "--force-device-scale-factor=2",
    "--default-background-color=00000000", "--virtual-time-budget=2500",
    f"--screenshot={OUT}", "file:///" + HTML.replace("\\", "/")], timeout=90)
print("wrote", OUT, os.path.getsize(OUT) // 1024, "KB")
