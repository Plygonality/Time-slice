"""CLI entry points."""

from __future__ import annotations

import json
from pathlib import Path

from time_slice.cli import main


def test_default_prints_three_epochs(capsys) -> None:
    assert main(["--seed", "1234"]) == 0
    out = capsys.readouterr().out
    assert "under construction" in out
    assert "operational" in out
    assert "relic" in out
    assert "DECAY-PASS" in out
    assert "SIGNAL-FIELD" in out
    assert "BRIEF TAGS" in out
    assert "seed 1234" in out


def test_plain_is_three_lines(capsys) -> None:
    assert main(["--seed", "1", "--plain"]) == 0
    lines = [line for line in capsys.readouterr().out.strip().splitlines() if line]
    assert len(lines) == 3


def test_seed_after_subcommand(capsys) -> None:
    assert main(["dump", "--seed", "1234"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["seed"] == 1234
    assert len(data["epochs"]) == 3


def test_list_epochs(capsys) -> None:
    assert main(["list-epochs"]) == 0
    assert capsys.readouterr().out.split() == ["construction", "operational", "relic"]


def test_preview_and_playbook(tmp_path: Path, capsys) -> None:
    play = tmp_path / "playbook.json"
    assert main(["playbook", "--seed", "1234", "-o", str(play)]) == 0
    data = json.loads(play.read_text(encoding="utf-8"))
    assert data["hook"] == "generators not one-offs"
    assert data["format"] == "time-slice-playbook"

    out = tmp_path / "shots"
    assert main(["preview", "--seed", "1234", "--out", str(out)]) == 0
    assert (out / "gallery.html").is_file()
    assert (out / "construction" / "preview.svg").is_file()
    assert (out / "operational" / "preview.svg").is_file()
    assert (out / "relic" / "preview.svg").is_file()


def test_apply_script_writes(tmp_path: Path) -> None:
    path = tmp_path / "apply.py"
    assert main(["apply-script", "--seed", "1234", "-o", str(path)]) == 0
    text = path.read_text(encoding="utf-8")
    compile(text, str(path), "exec")
    assert "def apply_epoch" in text
