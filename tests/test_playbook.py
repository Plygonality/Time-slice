"""One playbook, three folders. The bpy script is self-contained."""

from __future__ import annotations

import ast
import json

from time_slice.epochs import EPOCHS
from time_slice.playbook import FORMAT, HOOK, LOOP, build_playbook, to_apply_script


def test_playbook_is_one_file_three_folders() -> None:
    book = build_playbook(1234).to_dict()
    assert book["format"] == FORMAT
    assert book["hook"] == HOOK
    assert book["seed"] == 1234
    assert list(book["folders"]) == list(EPOCHS)
    assert [item["epoch"] for item in book["epochs"]] == list(EPOCHS)
    for epoch in EPOCHS:
        assert book["folders"][epoch] == f"screenshots/{epoch}"
        assert any(item["folder"] == f"screenshots/{epoch}" for item in book["epochs"])


def test_loop_names_the_mcp_passes() -> None:
    joined = " ".join(LOOP)
    assert "decay-pass" in joined
    assert "signal-field" in joined
    assert "screenshot" in joined
    assert "identity" in joined


def test_playbook_json_roundtrip() -> None:
    raw = build_playbook(99).dumps()
    data = json.loads(raw)
    assert data["identity"]["seed"] == 99
    assert len(data["epochs"]) == 3


def test_apply_script_parses_and_names_the_folders() -> None:
    script = to_apply_script(build_playbook(1234), output_root="screenshots")
    ast.parse(script)
    assert "construction" in script
    assert "operational" in script
    assert "relic" in script
    assert "viewport.png" in script
    assert "apply_epoch" in script
    assert "TimeSlice" in script
    assert "decay-pass" in script or "decay" in script
