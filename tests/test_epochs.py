"""Same seed, three epochs. Decay-pass and signal-field move; identity does not."""

from __future__ import annotations

from time_slice.epochs import EPOCH_LABELS, EPOCHS, SCREENSHOT_FOLDERS, slice_seed


def test_three_named_epochs() -> None:
    assert EPOCHS == ("construction", "operational", "relic")
    assert EPOCH_LABELS["construction"] == "under construction"
    assert set(SCREENSHOT_FOLDERS) == set(EPOCHS)
    for epoch in EPOCHS:
        assert SCREENSHOT_FOLDERS[epoch] == f"screenshots/{epoch}"


def test_same_seed_shares_identity_across_epochs() -> None:
    slices = slice_seed(1234)
    identities = {item.identity.logline for item in slices.slices}
    rigs = {id(item.identity.rig) for item in slices.slices}
    assert len(slices.slices) == 3
    assert len(identities) == 1
    assert slices.identity.logline in identities
    assert len(rigs) == 1


def test_reproducible_dump() -> None:
    assert slice_seed(1234).to_dict() == slice_seed(1234).to_dict()


def test_construction_is_unfinished_not_ruined() -> None:
    item = slice_seed(1234).by_epoch("construction")
    assert item.decay.scaffold > 0.6
    assert item.decay.incomplete > 0.4
    assert item.decay.oxidation < 0.25
    assert item.decay.breach < 0.2
    assert "constructing" in item.tags
    assert "relic" not in item.tags


def test_operational_is_complete_and_live() -> None:
    item = slice_seed(1234).by_epoch("operational")
    assert item.decay.scaffold < 0.1
    assert item.decay.incomplete < 0.15
    assert item.signal.coherence > 0.6
    assert "complete" in item.tags
    assert "inhabited" in item.tags


def test_relic_is_decayed_and_ghosted() -> None:
    item = slice_seed(1234).by_epoch("relic")
    assert item.decay.oxidation > 0.7
    assert item.decay.breach > 0.5
    assert item.signal.ghost > 0.6
    assert item.signal.amplitude < 0.4
    assert {"derelict", "abandoned", "relic"} <= item.tags


def test_brief_tags_keep_identity_and_add_epoch() -> None:
    slices = slice_seed(7)
    identity_tags = slices.identity.tags
    for item in slices.slices:
        assert identity_tags <= item.tags


def test_palette_swatches_persist_across_epochs() -> None:
    slices = slice_seed(42)
    primary = slices.identity.swatches[0]
    construction = slices.by_epoch("construction").palette
    operational = slices.by_epoch("operational").palette
    relic = slices.by_epoch("relic").palette
    assert primary in construction
    assert primary in operational
    assert primary in relic
    assert construction != operational != relic


def test_decay_and_signal_diverge_by_epoch() -> None:
    slices = slice_seed(5)
    decays = [item.decay.to_dict() for item in slices.slices]
    signals = [item.signal.to_dict() for item in slices.slices]
    assert decays[0] != decays[1] != decays[2]
    assert signals[0] != signals[1] != signals[2]
