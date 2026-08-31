"""Identity is constant across epochs; the seed is the whole identity."""

from __future__ import annotations

from time_slice.identity import AXES, OCCUPANTS, PALETTES, STRUCTURES, generate_identity


def test_catalogs_are_nonempty_and_unique() -> None:
    for name, pool in AXES.items():
        assert pool, name
        texts = [frag.text for frag in pool]
        assert len(texts) == len(set(texts)), name


def test_fragments_are_trimmed_and_unpunctuated() -> None:
    for pool in AXES.values():
        for frag in pool:
            assert frag.text == frag.text.strip(), frag.text
            assert not frag.text.endswith("."), frag.text


def test_identity_tags_are_epoch_neutral() -> None:
    forbidden = {"constructing", "derelict", "abandoned", "relic", "incomplete"}
    for pool in AXES.values():
        for frag in pool:
            assert not (frag.tags & forbidden), frag.text


def test_same_seed_same_identity() -> None:
    first = generate_identity(1234)
    second = generate_identity(1234)
    assert first.to_dict() == second.to_dict()


def test_different_seeds_can_diverge() -> None:
    loglines = {generate_identity(seed).logline for seed in range(24)}
    assert len(loglines) > 1


def test_rig_is_locked_to_seed() -> None:
    a = generate_identity(99).rig
    b = generate_identity(99).rig
    assert (a.rings, a.spokes, a.modules, a.tether, a.petals) == (
        b.rings,
        b.spokes,
        b.modules,
        b.tether,
        b.petals,
    )


def test_occupants_and_palettes_are_short() -> None:
    assert len(OCCUPANTS) >= 3
    assert len(PALETTES) >= 6
    assert len(STRUCTURES) >= 12
