"""Preview writes one gallery and three screenshot folders."""

from __future__ import annotations

from pathlib import Path

from time_slice.epochs import EPOCHS, slice_seed
from time_slice.preview import render_svg, write_preview


def test_svg_carries_seed_epoch_and_passes(tmp_path: Path) -> None:
    slices = slice_seed(1234)
    construction = render_svg(slices.by_epoch("construction"))
    operational = render_svg(slices.by_epoch("operational"))
    relic = render_svg(slices.by_epoch("relic"))

    assert 'data-seed="1234"' in construction
    assert 'data-epoch="construction"' in construction
    assert "DECAY-PASS" in construction
    assert "SIGNAL-FIELD" in construction
    assert "BRIEF TAGS" in construction
    assert 'class="scaffold"' in construction
    assert "under construction" in construction.lower() or "UNDER CONSTRUCTION" in construction

    assert 'class="scaffold"' not in operational
    assert 'class="signal-lane"' in operational or 'class="signal"' in operational

    assert 'class="debris"' in relic or 'class="ghost-signal"' in relic
    assert "relic" in relic.lower()

    # Same silhouette: identical spoke/module counts in the rig group.
    for svg in (construction, operational, relic):
        assert 'data-rings="' in svg
        assert 'data-spokes="' in svg
        assert 'data-modules="' in svg
        assert f'data-rings="{slices.identity.rig.rings}"' in svg
        assert f'data-spokes="{slices.identity.rig.spokes}"' in svg
        assert f'data-modules="{slices.identity.rig.modules}"' in svg


def test_write_preview_makes_three_folders(tmp_path: Path) -> None:
    written = write_preview(1234, tmp_path)
    assert (tmp_path / "gallery.html").is_file()
    for epoch in EPOCHS:
        svg = tmp_path / epoch / "preview.svg"
        assert svg.is_file()
        assert written[epoch] == svg
        text = svg.read_text(encoding="utf-8")
        assert "DECAY-PASS" in text
        assert "SIGNAL-FIELD" in text
    gallery = (tmp_path / "gallery.html").read_text(encoding="utf-8")
    assert "Same seed, three epochs" in gallery
    assert "construction/preview.svg" in gallery
    assert "operational/preview.svg" in gallery
    assert "relic/preview.svg" in gallery
    assert "1234" in gallery
