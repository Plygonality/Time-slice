"""Human-readable briefs — the thing you paste into a look-dev note."""

from __future__ import annotations

import textwrap

from time_slice.epochs import Slice, SliceSet

WIDTH = 62


def render_slice(slice_: Slice, index: int = 1, total: int = 3) -> str:
    decay = slice_.decay.to_dict()
    signal = slice_.signal.to_dict()
    tags = ", ".join(sorted(slice_.tags))
    lines = [
        "=" * WIDTH,
        f"TIME-SLICE {index}/{total}".ljust(48) + f"seed {slice_.identity.seed}",
        "=" * WIDTH,
        "",
        "[ IDENTITY ]",
        textwrap.fill(
            slice_.identity.logline, width=WIDTH, initial_indent="  ", subsequent_indent="  "
        ),
        f"  Occupants  : {slice_.identity.occupants.text}",
        "",
        f"[ EPOCH ] {slice_.label}",
        "",
        "[ PROJECT PROMPT ]",
        textwrap.fill(slice_.brief, width=WIDTH, subsequent_indent="  "),
        "",
        "[ BRIEF TAGS ] " + tags,
        "",
        "[ DECAY-PASS ]",
        (
            f"  amount {decay['amount']:.2f}   incomplete {decay['incomplete']:.2f}   "
            f"scaffold {decay['scaffold']:.2f}"
        ),
        (
            f"  oxidation {decay['oxidation']:.2f}   breach {decay['breach']:.2f}   "
            f"debris {decay['debris']:.2f}"
        ),
        "",
        "[ SIGNAL-FIELD ]",
        (
            f"  density {signal['density']:.2f}   coherence {signal['coherence']:.2f}   "
            f"amplitude {signal['amplitude']:.2f}"
        ),
        (
            f"  wavelength {signal['wavelength']:.2f}   ghost {signal['ghost']:.2f}"
        ),
        "",
        "[ ART DIRECTION ]",
        f"  Lighting   : {slice_.lighting}",
        f"  Palette    : {slice_.palette}",
        f"  Occupancy  : {slice_.occupancy}",
        f"  Folder     : {slice_.folder}",
    ]
    return "\n".join(lines)


def render_set(slices: SliceSet) -> str:
    blocks = [
        render_slice(item, index=i, total=len(slices.slices))
        for i, item in enumerate(slices.slices, start=1)
    ]
    return "\n\n".join(blocks)


def render_plain(slices: SliceSet) -> str:
    return "\n".join(item.brief for item in slices.slices)
