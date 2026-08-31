"""Stable, salt-derived RNGs so identity, rig, and epoch jitter never share a stream."""

from __future__ import annotations

import hashlib
import random


def derive_rng(seed: int, *salts: str) -> random.Random:
    """Return a Random whose state is a SHA-256 of `seed` plus salt tokens.

    Separate salts keep the identity pick independent of the rig, and the rig
    independent of per-epoch decay/signal jitter. Re-running with the same
    seed always yields the same stream for a given salt.
    """
    material = f"{seed}:" + ":".join(salts)
    digest = hashlib.sha256(material.encode("utf-8")).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


def clamp01(value: float) -> float:
    return 0.0 if value < 0.0 else 1.0 if value > 1.0 else value


def jitter(rng: random.Random, base: float, spread: float = 0.05) -> float:
    """Symmetric noise around `base`, clamped to [0, 1]."""
    return clamp01(base + rng.uniform(-spread, spread))
