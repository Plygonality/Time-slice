"""One playbook, three folders. The bpy script is self-contained."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from time_slice.epochs import EPOCHS
from time_slice.playbook import (
    FORMAT,
    HOOK,
    LOOP,
    build_playbook,
    epoch_records,
    expected_screenshot_path,
    iter_playbook_paths,
    load_playbook,
    screenshot_folder_for,
    to_apply_script,
    validate_playbook,
)

REPO = Path(__file__).resolve().parents[1]
PLAYBOOKS = REPO / "playbooks"


def test_playbook_is_one_file_three_folders() -> None:
    book = build_playbook(1234).to_dict()
    assert book["format"] == FORMAT
    assert book["hook"] == HOOK
    assert book["seed"] == 1234
    assert list(book["folders"]) == list(EPOCHS)
    assert [item["epoch"] for item in book["epochs"]] == list(EPOCHS)
    for epoch, item in zip(EPOCHS, book["epochs"], strict=True):
        assert item["seed"] == 1234
        assert item["epoch"] == epoch
        assert book["folders"][epoch] == f"screenshots/{epoch}"
        assert item["folder"] == f"screenshots/{epoch}"
        assert item["expected_screenshot"] == expected_screenshot_path(epoch)
        assert item["generator"]["decay"] == item["decay"]
        assert item["generator"]["signal"] == item["signal"]
        assert "identity" not in item["generator"]


def test_loop_names_the_mcp_passes() -> None:
    joined = " ".join(LOOP)
    assert "decay-pass" in joined
    assert "signal-field" in joined
    assert "screenshot" in joined
    assert "identity" in joined


def test_playbook_json_roundtrip() -> None:
    raw = build_playbook(99).dumps()
    data = json.loads(raw)
    validate_playbook(data)
    assert data["identity"]["seed"] == 99
    assert len(data["epochs"]) == 3
    assert {item["seed"] for item in data["epochs"]} == {99}


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
    assert 'spec.get("generator")' in script


def test_every_playbook_has_matching_screenshot_folder_and_shared_seed() -> None:
    paths = iter_playbook_paths(PLAYBOOKS)
    assert paths, "playbooks/ must contain at least one JSON set"

    for path in paths:
        data = load_playbook(path)
        records = epoch_records(data)
        seeds = [item["seed"] for item in records]
        assert len(records) == 3
        assert len(set(seeds)) == 1, f"{path.name}: seeds must match across epochs"
        assert seeds[0] == data["seed"]
        assert {item["epoch"] for item in records} == set(EPOCHS)

        for item in records:
            relative = screenshot_folder_for(item["expected_screenshot"])
            folder = relative if relative.is_absolute() else REPO / relative
            assert folder.is_dir(), (
                f"{path.name} epoch {item['epoch']!r} expected screenshot "
                f"{item['expected_screenshot']!r} has no folder {folder}"
            )
            assert folder.name == item["epoch"]
            assert folder.parent.name == "screenshots"


def test_committed_playbooks_match_builder() -> None:
    for path in iter_playbook_paths(PLAYBOOKS):
        data = load_playbook(path)
        built = build_playbook(data["seed"]).to_dict()
        assert data == built


def test_validate_playbook_rejects_divergent_epoch_seeds() -> None:
    data = build_playbook(1234).to_dict()
    data["epochs"][1]["seed"] = 9999
    with pytest.raises(ValueError, match="seed"):
        validate_playbook(data)
