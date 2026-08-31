"""
Time-slice: same seed, three epochs.

A generator that only fires once is a one-off. Time-slice holds identity in
the seed and replays it across under construction / operational / relic so
the Plygon MCP loop can prove the system holds.

Public surface:

    from time_slice import slice_seed, build_playbook, write_preview, to_apply_script

    slices = slice_seed(1234)
    playbook = build_playbook(1234)
    write_preview(1234, "screenshots")
"""

from __future__ import annotations

from time_slice.cli import main
from time_slice.epochs import (
    EPOCH_LABELS,
    EPOCHS,
    SCREENSHOT_FOLDERS,
    DecayPass,
    SignalField,
    Slice,
    SliceSet,
    make_slice,
    slice_seed,
)
from time_slice.identity import Identity, Rig, generate_identity
from time_slice.playbook import Playbook, build_playbook, to_apply_script, write_playbook
from time_slice.preview import write_preview

__all__ = [
    "EPOCHS",
    "EPOCH_LABELS",
    "SCREENSHOT_FOLDERS",
    "DecayPass",
    "Identity",
    "Playbook",
    "Rig",
    "SignalField",
    "Slice",
    "SliceSet",
    "build_playbook",
    "generate_identity",
    "main",
    "make_slice",
    "slice_seed",
    "to_apply_script",
    "write_playbook",
    "write_preview",
]
