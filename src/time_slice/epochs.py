"""Epoch overlay: under construction / operational / relic.

Identity is constant. Epoch rewrites state tags, decay-pass, signal-field,
lighting, occupancy, and the finished palette. That is the whole trick —
replay the seed, change epoch, the silhouette holds.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

from time_slice.identity import Identity, generate_identity
from time_slice.rng import derive_rng, jitter

EpochId = Literal["construction", "operational", "relic"]

EPOCHS: tuple[EpochId, ...] = ("construction", "operational", "relic")

EPOCH_LABELS: dict[EpochId, str] = {
    "construction": "under construction",
    "operational": "operational",
    "relic": "relic",
}

# Folder names match epoch ids so the playbook can be a dumb copy loop.
SCREENSHOT_FOLDERS: dict[EpochId, str] = {
    "construction": "screenshots/construction",
    "operational": "screenshots/operational",
    "relic": "screenshots/relic",
}


@dataclass(frozen=True)
class DecayPass:
    """Geometry / material weathering. Bind these as GN or shader inputs."""

    amount: float
    incomplete: float
    scaffold: float
    oxidation: float
    breach: float
    debris: float

    def to_dict(self) -> dict[str, float]:
        return {key: round(value, 4) for key, value in asdict(self).items()}


@dataclass(frozen=True)
class SignalField:
    """Activity / comms / energy field. Same emitter sites, epoch-weighted."""

    density: float
    coherence: float
    amplitude: float
    wavelength: float
    ghost: float

    def to_dict(self) -> dict[str, float]:
        return {key: round(value, 4) for key, value in asdict(self).items()}


# Bases before seed jitter. Construction is unfinished, not ruined.
# Operational is lived-in. Relic is the same hull after time.
_DECAY_BASE: dict[EpochId, DecayPass] = {
    "construction": DecayPass(
        amount=0.14,
        incomplete=0.62,
        scaffold=0.88,
        oxidation=0.06,
        breach=0.02,
        debris=0.16,
    ),
    "operational": DecayPass(
        amount=0.18,
        incomplete=0.02,
        scaffold=0.00,
        oxidation=0.14,
        breach=0.01,
        debris=0.05,
    ),
    "relic": DecayPass(
        amount=0.86,
        incomplete=0.22,
        scaffold=0.04,
        oxidation=0.90,
        breach=0.68,
        debris=0.78,
    ),
}

_SIGNAL_BASE: dict[EpochId, SignalField] = {
    "construction": SignalField(
        density=0.82,
        coherence=0.22,
        amplitude=0.92,
        wavelength=0.32,
        ghost=0.04,
    ),
    "operational": SignalField(
        density=0.70,
        coherence=0.86,
        amplitude=0.72,
        wavelength=0.54,
        ghost=0.06,
    ),
    "relic": SignalField(
        density=0.16,
        coherence=0.38,
        amplitude=0.22,
        wavelength=0.84,
        ghost=0.88,
    ),
}

_EPOCH_TAGS: dict[EpochId, frozenset[str]] = {
    "construction": frozenset({"constructing", "incomplete", "active"}),
    "operational": frozenset({"active", "complete", "inhabited"}),
    "relic": frozenset({"derelict", "abandoned", "relic"}),
}

_LIGHTING: dict[EpochId, str] = {
    "construction": (
        "warm amber worklights, welding arcs, and warning strobes "
        "against unfinished dark"
    ),
    "operational": (
        "designed running lights, cool corridor glow, controlled sun-side"
    ),
    "relic": (
        "harsh unfiltered starlight, failing emergency flicker, long shadows"
    ),
}

_OCCUPANCY: dict[EpochId, str] = {
    "construction": "work crews and assembly drones on the open hull",
    "operational": "full census, systems live, traffic in the lanes",
    "relic": "empty decks, scavenger traces, drones that forgot their purpose",
}


def remap_palette(swatches: tuple[str, ...], epoch: EpochId) -> str:
    """Finish, prime, or oxidize the same three metals. Do not pick a new set."""
    primary = swatches[0] if swatches else "metal"
    secondary = swatches[1] if len(swatches) > 1 else "carbon"
    accent = swatches[2] if len(swatches) > 2 else "warning-yellow"
    if epoch == "construction":
        return f"primer grey, hazard stripe, raw {primary}"
    if epoch == "operational":
        return f"{primary}, {secondary}, {accent}"
    return f"oxidized {primary}, faded {secondary}, deep shadow"


def _decay_for(seed: int, epoch: EpochId) -> DecayPass:
    rng = derive_rng(seed, "decay", epoch)
    base = _DECAY_BASE[epoch]
    return DecayPass(
        amount=jitter(rng, base.amount),
        incomplete=jitter(rng, base.incomplete, 0.06),
        scaffold=jitter(rng, base.scaffold, 0.04),
        oxidation=jitter(rng, base.oxidation),
        breach=jitter(rng, base.breach, 0.06),
        debris=jitter(rng, base.debris, 0.06),
    )


def _signal_for(seed: int, epoch: EpochId) -> SignalField:
    rng = derive_rng(seed, "signal", epoch)
    base = _SIGNAL_BASE[epoch]
    return SignalField(
        density=jitter(rng, base.density),
        coherence=jitter(rng, base.coherence),
        amplitude=jitter(rng, base.amplitude),
        wavelength=jitter(rng, base.wavelength),
        ghost=jitter(rng, base.ghost),
    )


@dataclass(frozen=True)
class Slice:
    """One epoch of one identity: brief tags + decay-pass + signal-field."""

    identity: Identity
    epoch: EpochId
    decay: DecayPass
    signal: SignalField
    lighting: str
    occupancy: str
    palette: str

    @property
    def label(self) -> str:
        return EPOCH_LABELS[self.epoch]

    @property
    def folder(self) -> str:
        return SCREENSHOT_FOLDERS[self.epoch]

    @property
    def tags(self) -> frozenset[str]:
        return self.identity.tags | _EPOCH_TAGS[self.epoch]

    @property
    def brief(self) -> str:
        return (
            f"A 3D scene depicting: {self.identity.logline}. "
            f"Epoch: {self.label}. Occupancy: {self.occupancy}."
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "epoch": self.epoch,
            "label": self.label,
            "folder": self.folder,
            "brief": self.brief,
            "tags": sorted(self.tags),
            "lighting": self.lighting,
            "occupancy": self.occupancy,
            "palette": self.palette,
            "decay": self.decay.to_dict(),
            "signal": self.signal.to_dict(),
        }


@dataclass(frozen=True)
class SliceSet:
    """Same seed, three epochs. The unit the playbook consumes."""

    identity: Identity
    slices: tuple[Slice, ...]

    @property
    def seed(self) -> int:
        return self.identity.seed

    def by_epoch(self, epoch: EpochId) -> Slice:
        for item in self.slices:
            if item.epoch == epoch:
                return item
        raise KeyError(epoch)

    def to_dict(self) -> dict[str, object]:
        return {
            "seed": self.seed,
            "identity": self.identity.to_dict(),
            "epochs": [item.to_dict() for item in self.slices],
        }


def make_slice(identity: Identity, epoch: EpochId) -> Slice:
    return Slice(
        identity=identity,
        epoch=epoch,
        decay=_decay_for(identity.seed, epoch),
        signal=_signal_for(identity.seed, epoch),
        lighting=_LIGHTING[epoch],
        occupancy=_OCCUPANCY[epoch],
        palette=remap_palette(identity.swatches, epoch),
    )


def slice_seed(seed: int) -> SliceSet:
    """The public generator: one seed in, three epoch slices out."""
    identity = generate_identity(seed)
    return SliceSet(
        identity=identity,
        slices=tuple(make_slice(identity, epoch) for epoch in EPOCHS),
    )
