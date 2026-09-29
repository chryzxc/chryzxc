# Generates the profile README SVGs into ./assets. Edit the data below and rerun:
#   pip install fonttools brotli && python3 make.py
# Each image has a wide version and a phone version (*-sm.svg); README.md switches between them.
import base64
import io
import urllib.request
from html import escape
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).parent
OUT = ROOT / "assets"
OUT.mkdir(exist_ok=True)

ROWS = [("Experience", "Since 2019"), ("Side quest", "Cybersecurity")]
BUILD = [("AI agents", "LLM features, MCP servers"),
         ("Web platforms", "SaaS, dashboards, tools"),
         ("Native apps", "macOS, Android, games"),
         ("Dev tools", "CLIs, IDE extensions"),
         ("Automation", "Bots, scrapers, workflows")]

# Portfolio fonts (src/app/layout.tsx), pinned to the weights used and cut to printable ASCII + a few symbols.
# GitHub blocks external requests from README images, so the fonts are embedded as data URIs.
FONTS = {
    "FD": ("funneldisplay/FunnelDisplay%5Bwght%5D.ttf", {"wght": 500}),
    "FS": ("funnelsans/FunnelSans%5Bwght%5D.ttf", {"wght": (400, 600)}),
    "GM": ("geistmono/GeistMono%5Bwght%5D.ttf", {"wght": 400}),
}
CHARS = "".join(map(chr, range(32, 127))) + "·↗–—"


def font_face(family, path, axes):
    cache = ROOT / ".cache" / path.replace("%5B", "[").replace("%5D", "]").replace("/", "_")
    if not cache.exists():
        cache.parent.mkdir(exist_ok=True)
        cache.write_bytes(urllib.request.urlopen(f"https://raw.githubusercontent.com/google/fonts/main/ofl/{path}").read())
    font = instancer.instantiateVariableFont(TTFont(cache), axes)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga"]
    sub = subset.Subsetter(opts)
    sub.populate(text=CHARS)
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    weight = f"{axes['wght'][0]} {axes['wght'][1]}" if isinstance(axes["wght"], tuple) else axes["wght"]
    return f"@font-face{{font-family:{family};font-weight:{weight};src:url(data:font/woff2;base64,{base64.b64encode(buf.getvalue()).decode()}) format('woff2')}}"


FACES = "".join(font_face(f, p, a) for f, (p, a) in FONTS.items())

# Portfolio tokens (src/styles/folio.css): dark first, light when the viewer's GitHub is light.
STYLE = f"""<style>{FACES}
  :root{{--bg:#0D0D0E;--card:#18181B;--edge:#34343A;--fg:#EDECE8;--mute:#9C9B96;--chip:#1F1F22;--live:#7DDB8A;--dot:#34343A}}
  @media (prefers-color-scheme: light){{:root{{--bg:#F5F4F0;--card:#FFFFFF;--edge:#D5D3CC;--fg:#161618;--mute:#6C6B66;--chip:#EFEEEA;--live:#1C8A3A;--dot:#D5D3CC}}}}
  text{{font-family:FS,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;fill:var(--fg)}}
  .disp{{font-family:FD,FS,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;font-weight:500;letter-spacing:-.04em}}
  .mono{{font-family:GM,ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
  .eyebrow{{letter-spacing:.16em}}
  .mute{{fill:var(--mute)}} .live{{fill:var(--live)}}
  .up{{opacity:0;animation:up .7s cubic-bezier(.2,.7,.2,1) forwards}}
  @keyframes up{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:none}}}}
  .pulse{{transform-origin:center;transform-box:fill-box;animation:pulse 2s ease-out infinite}}
  @keyframes pulse{{0%{{opacity:.6;transform:scale(1)}}100%{{opacity:0;transform:scale(3)}}}}
  @media (prefers-reduced-motion: reduce){{.up{{opacity:1;animation:none}}.pulse{{animation:none;opacity:0}}}}
</style>"""


def svg(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">'
            f'{STYLE}<rect width="{w}" height="{h}" rx="20" fill="var(--bg)"/>{body}</svg>')


def up(delay, inner):
    return f'<g class="up" style="animation-delay:{delay}s">{inner}</g>'


def eyebrow(x, y, text, size=14):
    return f'<text x="{x}" y="{y}" class="mono live eyebrow" font-size="{size}">{escape(text)}</text>'


def pill(x, y):
    return (f'<rect x="{x}" y="{y}" width="106" height="28" rx="14" fill="var(--chip)" stroke="var(--edge)"/>'
            f'<circle cx="{x + 18}" cy="{y + 14}" r="4" class="live"/><circle cx="{x + 18}" cy="{y + 14}" r="4" class="live pulse"/>'
            f'<text x="{x + 30}" y="{y + 19}" font-size="13">Available</text>')


def rows(x1, x2, y, size=15):
    return "".join(
        (f'<line x1="{x1}" x2="{x2}" y1="{y + i * 44}" y2="{y + i * 44}" stroke="var(--edge)"/>' if y is not None and i else "")
        + f'<text x="{x1}" y="{y + 28 + i * 44}" class="mono mute" font-size="13">{escape(k)}</text>'
        + f'<text x="{x2}" y="{y + 28 + i * 44}" font-size="{size}" text-anchor="end">{escape(v)}</text>'
        for i, (k, v) in enumerate(ROWS))


DOTS = '<defs><pattern id="g" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="var(--dot)"/></pattern></defs>'
LABEL = "Christian Rey Villablanca, full-stack and AI developer"


def header():
    card_h = 112 + 44 * len(ROWS)  # card grows with its rows and stays vertically centered
    body = f"""{DOTS}<rect width="1200" height="360" rx="20" fill="url(#g)" opacity=".5"/>
{up(0, eyebrow(64, 92, "FULL-STACK & AI DEVELOPER"))}
{up(.1, '<text x="62" y="162" class="disp" font-size="66">Christian Rey</text>')}
{up(.2, '<text x="62" y="228" class="disp" font-size="66">Villablanca</text>')}
{up(.35, '<text x="64" y="284" font-size="20">I set the direction. <tspan class="mute">AI speeds it up. I ship it.</tspan></text>')}
{up(.45, '<text x="64" y="316" class="mono mute" font-size="13">Tacloban City, Philippines · open to remote full-time &amp; contract</text>')}
{up(.3, f'''<g transform="translate(0 {(360 - card_h) / 2 - 40})"><rect x="690" y="40" width="470" height="{card_h}" rx="16" fill="var(--card)" stroke="var(--edge)"/>
<rect x="720" y="70" width="44" height="44" rx="10" fill="var(--chip)" stroke="var(--edge)"/>
<text x="742" y="98" class="disp" font-size="17" text-anchor="middle">CR</text>
<text x="778" y="89" font-size="16" font-weight="600">Christian</text>
<text x="778" y="108" class="mono mute" font-size="12">christianvillablanca.is-a.dev</text>
{pill(1024, 78)}
<line x1="720" x2="1130" y1="150" y2="150" stroke="var(--edge)"/>
{rows(720, 1130, 150)}</g>''')}"""
    return svg(1200, 360, body, LABEL)


def header_sm():
    card_y, card_h = 304, 44 * len(ROWS) + 16
    h = card_y + card_h + 28
    body = f"""{DOTS}<rect width="400" height="{h}" rx="20" fill="url(#g)" opacity=".5"/>
{up(0, eyebrow(28, 50, "FULL-STACK & AI DEVELOPER", 12))}
{up(.1, '<text x="27" y="102" class="disp" font-size="46">Christian Rey</text>')}
{up(.2, '<text x="27" y="150" class="disp" font-size="46">Villablanca</text>')}
{up(.35, '<text x="28" y="190" font-size="17">I set the direction.</text><text x="28" y="214" class="mute" font-size="17">AI speeds it up. I ship it.</text>')}
{up(.45, '<text x="28" y="244" class="mono mute" font-size="12">Tacloban City, PH · open to remote</text>')}
{up(.5, pill(28, 260))}
{up(.55, f'<rect x="20" y="{card_y}" width="360" height="{card_h}" rx="14" fill="var(--card)" stroke="var(--edge)"/>{rows(40, 360, card_y + 8)}')}"""
    return svg(400, h, body, LABEL)


def build():
    gap, w = 16, (1200 - 128 - 16 * (len(BUILD) - 1)) / len(BUILD)
    tiles = "".join(up(.1 + i * .08, f'''<rect x="{64 + i * (w + gap)}" y="72" width="{w}" height="100" rx="14" fill="var(--card)" stroke="var(--edge)"/>
<text x="{84 + i * (w + gap)}" y="102" class="mono live" font-size="12">{i + 1:02}</text>
<text x="{84 + i * (w + gap)}" y="132" class="disp" font-size="19">{escape(name)}</text>
<text x="{84 + i * (w + gap)}" y="154" class="mute" font-size="13">{escape(what)}</text>''')
                    for i, (name, what) in enumerate(BUILD))
    return svg(1200, 200, up(0, eyebrow(64, 48, "WHAT I BUILD")) + tiles, "What I build: " + ", ".join(n for n, _ in BUILD))


def build_sm():
    h = 68 + 70 * len(BUILD) + 18
    tiles = "".join(up(.1 + i * .08, f'''<rect x="20" y="{68 + i * 70}" width="360" height="60" rx="12" fill="var(--card)" stroke="var(--edge)"/>
<text x="40" y="{103 + i * 70}" class="mono live" font-size="12">{i + 1:02}</text>
<text x="76" y="{94 + i * 70}" class="disp" font-size="18">{escape(name)}</text>
<text x="76" y="{114 + i * 70}" class="mute" font-size="13">{escape(what)}</text>''')
                    for i, (name, what) in enumerate(BUILD))
    return svg(400, h, up(0, eyebrow(28, 48, "WHAT I BUILD", 12)) + tiles, "What I build: " + ", ".join(n for n, _ in BUILD))


for name, make in {"header": header, "header-sm": header_sm, "build": build, "build-sm": build_sm}.items():
    (OUT / f"{name}.svg").write_text(make())
    print(f"wrote {name}.svg ({(OUT / f'{name}.svg').stat().st_size // 1024} KB)")
