"""Look-dev preview: SVG triptych that does not need Blender.

Same silhouette, three epochs. Brief tags, decay-pass meters, signal-field
meters. Writes `screenshots/<epoch>/preview.svg` plus `screenshots/gallery.html`.
When Plygon-mcp is in the loop it drops `viewport.png` next to the SVG.
"""

from __future__ import annotations

import math
from pathlib import Path
from xml.sax.saxutils import escape

from time_slice.epochs import EPOCHS, Slice, SliceSet, slice_seed
from time_slice.identity import Rig
from time_slice.rng import derive_rng

WIDTH = 720
HEIGHT = 960
CX = 360.0
CY = 560.0
SCALE = 250.0

# Plygon-adjacent: construction amber, operational cyan, relic rust.
_THEME: dict[str, dict[str, str]] = {
    "construction": {
        "bg": "#0d0e10",
        "ink": "#e8dcc4",
        "accent": "#ffb020",
        "dim": "#6b5a32",
        "signal": "#ffd36a",
        "ghost": "#5a4a28",
        "hull": "#c4b089",
        "bar": "#ffb020",
    },
    "operational": {
        "bg": "#0b0e12",
        "ink": "#d7eef5",
        "accent": "#6ae0ff",
        "dim": "#3a5a66",
        "signal": "#7dffa3",
        "ghost": "#245055",
        "hull": "#c9d6dc",
        "bar": "#6ae0ff",
    },
    "relic": {
        "bg": "#100c0a",
        "ink": "#edd5c4",
        "accent": "#c45c26",
        "dim": "#6a3a28",
        "signal": "#e08a5a",
        "ghost": "#4a2a22",
        "hull": "#8a5a44",
        "bar": "#c45c26",
    },
}


def _r(value: float) -> str:
    return f"{value:.2f}"


def _module_hash(seed: int, index: int) -> float:
    rng = derive_rng(seed, "module", str(index))
    return rng.random()


def _hidden(slice_: Slice, index: int) -> bool:
    h = _module_hash(slice_.identity.seed, index)
    if slice_.epoch == "construction":
        return h < slice_.decay.incomplete
    if slice_.epoch == "relic":
        return h < slice_.decay.breach
    return h < slice_.decay.incomplete * 0.25


def _meters(slice_: Slice, theme: dict[str, str]) -> str:
    rows = [
        ("DECAY-PASS", [
            ("amount", slice_.decay.amount),
            ("incomplete", slice_.decay.incomplete),
            ("scaffold", slice_.decay.scaffold),
            ("oxidation", slice_.decay.oxidation),
            ("breach", slice_.decay.breach),
            ("debris", slice_.decay.debris),
        ]),
        ("SIGNAL-FIELD", [
            ("density", slice_.signal.density),
            ("coherence", slice_.signal.coherence),
            ("amplitude", slice_.signal.amplitude),
            ("wavelength", slice_.signal.wavelength),
            ("ghost", slice_.signal.ghost),
        ]),
    ]
    parts: list[str] = []
    y0 = 222
    for group_i, (title, items) in enumerate(rows):
        x0 = 36 + group_i * 348
        parts.append(
            f'<text x="{x0}" y="{y0}" class="kicker">{escape(title)}</text>'
        )
        for i, (name, value) in enumerate(items):
            y = y0 + 18 + i * 18
            w = 210 * value
            parts.append(
                f'<text x="{x0}" y="{y + 9}" class="meter-label">{escape(name)}</text>'
                f'<rect x="{x0 + 92}" y="{y}" width="210" height="8" rx="1" fill="#00000055"/>'
                f'<rect class="meter" data-pass="{escape(title.lower())}" data-key="{escape(name)}" '
                f'data-value="{value:.4f}" x="{x0 + 92}" y="{y}" width="{_r(w)}" height="8" '
                f'rx="1" fill="{theme["bar"]}"/>'
            )
    return "\n".join(parts)


def _tags(slice_: Slice) -> str:
    tags = sorted(slice_.tags)
    x, y = 36, 152
    parts = ['<text x="36" y="138" class="kicker">BRIEF TAGS</text>']
    for tag in tags:
        w = 8 * len(tag) + 16
        if x + w > WIDTH - 36:
            x = 36
            y += 22
        parts.append(
            f'<g class="tag" data-tag="{escape(tag)}">'
            f'<rect x="{x}" y="{y - 12}" width="{w}" height="18" rx="2" '
            f'fill="#ffffff10" stroke="currentColor" stroke-width="0.6"/>'
            f'<text x="{x + 8}" y="{y + 1}">{escape(tag)}</text></g>'
        )
        x += w + 8
    return "\n".join(parts)


def _polar(radius: float, angle: float) -> tuple[float, float]:
    return CX + radius * math.cos(angle), CY + radius * math.sin(angle)


def _structure(slice_: Slice, theme: dict[str, str]) -> str:
    rig: Rig = slice_.identity.rig
    seed = slice_.identity.seed
    parts: list[str] = [f'<g class="rig" data-seed="{seed}" data-rings="{rig.rings}" data-spokes="{rig.spokes}" data-modules="{rig.modules}">']
    r0 = rig.core_radius * SCALE
    r1 = rig.outer_radius * SCALE
    hull = theme["hull"]
    accent = theme["accent"]
    dim = theme["dim"]
    signal = theme["signal"]
    ghost = theme["ghost"]

    # Tether
    if rig.tether:
        parts.append(
            f'<line class="tether" x1="{CX}" y1="{CY}" x2="{CX}" y2="{CY + r1 * 1.25}" '
            f'stroke="{dim}" stroke-width="1.2"/>'
        )

    # Scaffold (construction)
    if slice_.decay.scaffold > 0.15:
        parts.append('<g class="scaffold">')
        for i in range(4):
            rr = r0 + (r1 - r0) * (i + 0.5) / 4.5
            parts.append(
                f'<circle cx="{CX}" cy="{CY}" r="{_r(rr)}" fill="none" stroke="{accent}" '
                f'stroke-width="0.6" stroke-dasharray="3 5" opacity="0.55"/>'
            )
        for i in range(rig.spokes):
            ang = 2 * math.pi * (i + 0.5) / rig.spokes
            x2, y2 = _polar(r1, ang)
            x1, y1 = _polar(r0, ang)
            parts.append(
                f'<line x1="{_r(x1)}" y1="{_r(y1)}" x2="{_r(x2)}" y2="{_r(y2)}" '
                f'stroke="{accent}" stroke-width="0.7" opacity="0.45"/>'
            )
        parts.append("</g>")

    # Rings
    dash = "8 6" if slice_.epoch == "construction" else ("2 10" if slice_.epoch == "relic" else "none")
    opacity = 0.55 if slice_.epoch == "relic" else 0.9
    for ring_i in range(rig.rings):
        t = (ring_i + 1) / rig.rings
        rr = r0 + (r1 - r0) * t
        extra = f' stroke-dasharray="{dash}"' if dash != "none" else ""
        parts.append(
            f'<circle class="ring" cx="{CX}" cy="{CY}" r="{_r(rr)}" fill="none" '
            f'stroke="{hull}" stroke-width="1.6" opacity="{opacity}"{extra}/>'
        )

    # Spokes
    for i in range(rig.spokes):
        ang = 2 * math.pi * i / rig.spokes
        x2, y2 = _polar(r1, ang)
        x1, y1 = _polar(r0, ang)
        parts.append(
            f'<line class="spoke" x1="{_r(x1)}" y1="{_r(y1)}" x2="{_r(x2)}" y2="{_r(y2)}" '
            f'stroke="{hull}" stroke-width="1.3" opacity="{opacity}"/>'
        )

    # Petals
    if rig.petals:
        for i in range(rig.petals):
            ang = 2 * math.pi * i / rig.petals
            x1, y1 = _polar(r1 * 0.92, ang - 0.12)
            x2, y2 = _polar(r1 * 1.18, ang)
            x3, y3 = _polar(r1 * 0.92, ang + 0.12)
            parts.append(
                f'<path class="petal" d="M{_r(x1)},{_r(y1)} L{_r(x2)},{_r(y2)} L{_r(x3)},{_r(y3)}" '
                f'fill="none" stroke="{dim}" stroke-width="1"/>'
            )

    # Modules + debris
    parts.append('<g class="modules">')
    for i in range(rig.modules):
        ang = 2 * math.pi * i / rig.modules
        x, y = _polar(r1, ang)
        hidden = _hidden(slice_, i)
        if hidden and slice_.epoch == "relic" and slice_.decay.debris > 0.4:
            dx = 14 * math.cos(ang + 0.5)
            dy = 14 * math.sin(ang + 0.5)
            parts.append(
                f'<rect class="debris" data-index="{i}" x="{_r(x + dx - 4)}" y="{_r(y + dy - 3)}" '
                f'width="7" height="5" transform="rotate({_r(math.degrees(ang))} {_r(x + dx)} {_r(y + dy)})" '
                f'fill="{ghost}" opacity="0.7"/>'
            )
        if hidden:
            continue
        w, h = 11, 7
        parts.append(
            f'<rect class="module" data-index="{i}" x="{_r(x - w / 2)}" y="{_r(y - h / 2)}" '
            f'width="{w}" height="{h}" transform="rotate({_r(math.degrees(ang))} {_r(x)} {_r(y)})" '
            f'fill="{accent}" opacity="0.85"/>'
        )
    parts.append("</g>")

    # Core
    parts.append(
        f'<circle class="core" cx="{CX}" cy="{CY}" r="{_r(r0 * 0.55)}" fill="#00000040" '
        f'stroke="{accent}" stroke-width="1.4"/>'
    )

    # Signal field — same sites, epoch-weighted
    emitters = max(rig.modules, rig.spokes * rig.rings)
    parts.append('<g class="signal-field">')
    for i in range(emitters):
        ang = 2 * math.pi * i / emitters
        lane = i % rig.rings
        t = (lane + 1) / rig.rings
        rr = r0 + (r1 - r0) * t
        x, y = _polar(rr, ang)
        density = slice_.signal.density
        coherence = slice_.signal.coherence
        ghost_amt = slice_.signal.ghost
        amp = slice_.signal.amplitude
        live = ((i * 17 + seed) % 100) / 100.0 < density
        if coherence > 0.6:
            live = live or (i % max(1, int(3 - 2 * density)) == 0)
        is_ghost = (not live) and ghost_amt > 0.5 and ((i + lane) % 5 == 0)
        if not live and not is_ghost:
            continue
        cls = "ghost-signal" if is_ghost else "signal"
        color = ghost if is_ghost else signal
        rad = 1.6 + 2.4 * amp
        parts.append(
            f'<circle class="{cls}" data-index="{i}" cx="{_r(x)}" cy="{_r(y)}" r="{_r(rad)}" '
            f'fill="{color}" opacity="{0.35 if is_ghost else 0.9}"/>'
        )
        if live and coherence > 0.7 and i % rig.spokes == 0:
            x2, y2 = _polar(r0, ang)
            parts.append(
                f'<line class="signal-lane" x1="{_r(x2)}" y1="{_r(y2)}" x2="{_r(x)}" y2="{_r(y)}" '
                f'stroke="{signal}" stroke-width="0.6" opacity="0.35"/>'
            )
    parts.append("</g>")
    parts.append("</g>")
    return "\n".join(parts)


def _wrap(text: str, width: int = 78) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        trial = " ".join([*current, word])
        if current and len(trial) > width:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines or [""]


def render_svg(slice_: Slice) -> str:
    theme = _THEME[slice_.epoch]
    identity = slice_.identity
    log_lines = _wrap(identity.logline, 78)
    logline = "\n".join(
        f'<text class="logline" x="36" y="{108 + i * 14}">{escape(line)}</text>'
        for i, line in enumerate(log_lines)
    )
    epoch_n = EPOCHS.index(slice_.epoch) + 1
    tags_block = _tags(slice_)
    meters = _meters(slice_, theme)
    rig = _structure(slice_, theme)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}"
     role="img" data-epoch="{slice_.epoch}" data-seed="{identity.seed}">
  <style>
    text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: {theme["ink"]}; }}
    .kicker {{ font-size: 10px; letter-spacing: 0.18em; fill: {theme["accent"]}; }}
    .title {{ font-size: 13px; letter-spacing: 0.28em; fill: {theme["accent"]}; }}
    .epoch {{ font-size: 22px; font-weight: 600; }}
    .seed {{ font-size: 12px; fill: {theme["dim"]}; }}
    .logline {{ font-size: 11px; }}
    .meter-label {{ font-size: 10px; fill: {theme["dim"]}; }}
    .tag text {{ font-size: 10px; fill: {theme["ink"]}; }}
    .foot {{ font-size: 10px; fill: {theme["dim"]}; letter-spacing: 0.08em; }}
  </style>
  <rect width="100%" height="100%" fill="{theme["bg"]}"/>
  <rect x="16" y="16" width="{WIDTH - 32}" height="{HEIGHT - 32}" fill="none"
        stroke="{theme["accent"]}" stroke-width="0.8" opacity="0.45"/>
  <text class="title" x="36" y="48">TIME-SLICE</text>
  <text class="seed" x="684" y="48" text-anchor="end">SEED {identity.seed}</text>
  <text class="epoch" x="36" y="82">{escape(slice_.label).upper()}</text>
  {logline}
  {tags_block}
  {meters}
  {rig}
  <text class="foot" x="36" y="910">{escape(slice_.palette)}</text>
  <text class="foot" x="36" y="932">PLAYBOOK {epoch_n}/3  ·  {escape(slice_.folder)}</text>
  <text class="foot" x="684" y="932" text-anchor="end">GENERATORS NOT ONE-OFFS</text>
</svg>
"""


def render_gallery(slices: SliceSet) -> str:
    cards = []
    for item in slices.slices:
        cards.append(
            f"""    <figure data-epoch="{item.epoch}">
      <figcaption>
        <span class="epoch">{escape(item.label)}</span>
        <span class="folder">{escape(item.folder)}</span>
      </figcaption>
      <object type="image/svg+xml" data="{item.epoch}/preview.svg"></object>
    </figure>"""
        )
    identity = slices.identity
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Time-slice · seed {identity.seed}</title>
  <style>
    :root {{ color-scheme: dark; }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; background: #08090b; color: #e8e4dc;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }}
    header {{
      padding: 28px 32px 12px; border-bottom: 1px solid #ffffff14;
    }}
    header .kicker {{ letter-spacing: 0.22em; color: #ff6a1a; font-size: 11px; }}
    h1 {{ font-size: 22px; font-weight: 600; margin: 8px 0 6px; letter-spacing: 0.04em; }}
    .logline {{ color: #9aa3a8; font-size: 13px; max-width: 72ch; line-height: 1.45; }}
    .meta {{ margin-top: 10px; color: #6d767c; font-size: 11px; letter-spacing: 0.08em; }}
    main {{
      display: grid; grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px; padding: 20px;
    }}
    figure {{ margin: 0; background: #0d0e10; border: 1px solid #ffffff12; }}
    figcaption {{
      display: flex; justify-content: space-between; padding: 10px 12px;
      font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase;
      border-bottom: 1px solid #ffffff10;
    }}
    figcaption .folder {{ color: #6d767c; letter-spacing: 0.04em; text-transform: none; }}
    object {{ width: 100%; height: auto; aspect-ratio: 720 / 960; display: block; }}
    @media (max-width: 1100px) {{ main {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <header>
    <div class="kicker">TIME-SLICE · ONE PLAYBOOK · THREE FOLDERS</div>
    <h1>Same seed, three epochs</h1>
    <p class="logline">{escape(identity.logline)}</p>
    <p class="meta">SEED {identity.seed}  ·  UNDER CONSTRUCTION / OPERATIONAL / RELIC  ·  GENERATORS NOT ONE-OFFS</p>
  </header>
  <main>
{chr(10).join(cards)}
  </main>
</body>
</html>
"""


def write_preview(seed: int, out_dir: str | Path = "screenshots") -> dict[str, Path]:
    """Write three epoch folders plus a gallery. Returns paths keyed by role."""
    slices = slice_seed(seed)
    root = Path(out_dir)
    written: dict[str, Path] = {}
    for item in slices.slices:
        folder = root / item.epoch
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / "preview.svg"
        path.write_text(render_svg(item), encoding="utf-8")
        written[item.epoch] = path
    gallery = root / "gallery.html"
    gallery.write_text(render_gallery(slices), encoding="utf-8")
    written["gallery"] = gallery
    return written
