"""Epoch-neutral identity: the thing that must not change when time does.

A generator that bakes 'derelict' into the noun is a one-off. Time-slice holds
structure, function, purpose, occupants, and palette DNA in an Identity, then
lets epoch overlay rewrite state. The seed is the whole identity.
"""

from __future__ import annotations

from dataclasses import dataclass

from time_slice.rng import derive_rng


@dataclass(frozen=True)
class Fragment:
    """One interchangeable line, plus the tags it contributes."""

    text: str
    tags: frozenset[str] = frozenset()
    weight: float = 1.0


def F(text: str, tags: str = "", weight: float = 1.0) -> Fragment:
    return Fragment(text=text, tags=frozenset(tags.split()), weight=weight)


# Tag conventions (epoch-neutral — no constructing / derelict / abandoned):
#   scale     : orbital | planetary | stellar | interstellar | black_hole
#   kind      : habitat | foundry | archive | weapon | thruster | compute
#   occupant  : organic | synthetic | posthuman
#   physics   : singularity | exotic_matter | anomaly
#   mood      : desolate | sublime | menacing | melancholy | uncanny

STRUCTURES: tuple[Fragment, ...] = (
    F("a Bishop Ring above a gas giant", "orbital planetary habitat"),
    F("a Ringworld segment spanning a temperate band", "orbital stellar habitat sublime"),
    F("a Dyson Swarm of collector petals", "orbital stellar foundry"),
    F("the lattice core of a Matrioshka Brain", "stellar compute synthetic sublime"),
    F("a space elevator anchored to a rogue planet", "planetary orbital"),
    F("a topopolis coiled around a dim orange star", "stellar habitat organic sublime"),
    F("a star-lifting rig around a red giant", "stellar foundry"),
    F("a Nicoll-Dyson beam emitter", "stellar weapon menacing"),
    F("a Jupiter Brain planetary supercomputer", "planetary compute synthetic"),
    F("an orbital habitat ring spun for gravity", "orbital habitat"),
    F("a comet-herding waystation at the Oort edge", "interstellar desolate"),
    F("a seed-vault moonlet", "planetary archive melancholy"),
    F("a Shkadov thruster around a neutron star", "stellar thruster black_hole sublime"),
    F("an Alderson Disk spanning a star", "stellar planetary habitat sublime"),
    F("a Kardashev-II swarm foundry", "stellar foundry synthetic exotic_matter"),
    F("a generation-ship drydock in deep interstellar space", "interstellar habitat"),
    F("a Penrose-process mine on a stellar-mass black hole", "black_hole stellar foundry"),
    F("an orbital elevator rising from a continental plate", "planetary orbital"),
)

FUNCTIONS: tuple[Fragment, ...] = (
    F("powered by a contained micro-singularity", "singularity"),
    F("sheathed in a self-repairing smart-matter skin", "synthetic"),
    F("that uses exotic matter as its primary structural material", "exotic_matter"),
    F("harvesting vacuum energy through kilometre-scale Casimir arrays", "exotic_matter"),
    F("using negative-mass exotic matter to hold open a traversable wormhole", "exotic_matter uncanny"),
    F("acting as a cradle for a nascent autonomous intelligence", "synthetic compute"),
    F("fed by a lattice of star-lifting mass drivers", "foundry"),
    F("cataloguing genomes of extinct biospheres", "archive organic melancholy"),
    F("siphoning plasma as structural feedstock", "foundry"),
    F("broadcasting a navigation beacon across a dead frequency", "uncanny"),
    F("whose hull is a programmable metamaterial", "synthetic exotic_matter"),
    F("tethered to a captured micro-singularity for spin and power", "singularity"),
)

PURPOSES: tuple[Fragment, ...] = (
    F("built to outlast its makers", "melancholy"),
    F("whose sole purpose is to witness the final moments of the universe", "sublime melancholy"),
    F("designed to seed an entirely new universe once this one ends", "sublime"),
    F("serving as a harbour against vacuum decay", "sublime menacing"),
    F("engineered as a doomsday ark", "melancholy"),
    F("that encodes forgotten engineering as ritual", "melancholy"),
    F("governed as a foundry-state for a machine ecology", "synthetic"),
    F("meant as a monument to a civilization's greatest work", "sublime"),
    F("holding one final, untranslatable message", "uncanny melancholy"),
    F("raised as a pilgrimage spine for scattered post-human sects", "posthuman"),
    F("chartered as a safe loft for organic crews between stars", "organic"),
    F("commissioned as a weapon the builders hoped never to fire", "weapon menacing"),
)

OCCUPANTS: tuple[Fragment, ...] = (
    F("organic crews", "organic", weight=1.1),
    F("synthetic drones", "synthetic", weight=1.2),
    F("mixed organic and synthetic shifts", "organic synthetic"),
    F("posthuman uploads", "posthuman synthetic"),
)

# Three-swatch DNA. Epoch remap finishes, primers, or oxidizes the same metals.
PALETTES: tuple[Fragment, ...] = (
    F("titanium, carbon, warning-yellow", "industrial"),
    F("copper, glass, obsidian", "sublime"),
    F("gunmetal, ice-blue, sterile-white", "desolate"),
    F("bone-white, ash-grey, faded-ochre", "melancholy"),
    F("iridescent oil-slick, matte carbon, phosphor-green", "uncanny"),
    F("crimson, char, ember-orange", "menacing"),
    F("teal, violet, phosphor-green", "uncanny sublime"),
    F("silver, glass, pinpoint-gold", "sublime"),
    F("oxidizable copper, rust-primer, deep-shadow", "desolate melancholy"),
    F("obsidian, molten-gold, carbon", "sublime menacing"),
)

AXES: dict[str, tuple[Fragment, ...]] = {
    "structure": STRUCTURES,
    "function": FUNCTIONS,
    "purpose": PURPOSES,
    "occupants": OCCUPANTS,
    "palette": PALETTES,
}


@dataclass(frozen=True)
class Rig:
    """Seed-locked silhouette. Epoch may hide parts; it may not redesign this."""

    rings: int
    spokes: int
    modules: int
    core_radius: float
    outer_radius: float
    tether: bool
    petals: int


@dataclass(frozen=True)
class Identity:
    """The constant across under construction / operational / relic."""

    seed: int
    structure: Fragment
    function: Fragment
    purpose: Fragment
    occupants: Fragment
    palette: Fragment
    rig: Rig

    @property
    def tags(self) -> frozenset[str]:
        parts = (
            self.structure,
            self.function,
            self.purpose,
            self.occupants,
            self.palette,
        )
        return frozenset().union(*(frag.tags for frag in parts))

    @property
    def swatches(self) -> tuple[str, ...]:
        return tuple(part.strip() for part in self.palette.text.split(",") if part.strip())

    @property
    def logline(self) -> str:
        return (
            f"{self.structure.text}, {self.function.text}, {self.purpose.text}"
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "seed": self.seed,
            "structure": self.structure.text,
            "function": self.function.text,
            "purpose": self.purpose.text,
            "occupants": self.occupants.text,
            "palette": self.palette.text,
            "tags": sorted(self.tags),
            "rig": {
                "rings": self.rig.rings,
                "spokes": self.rig.spokes,
                "modules": self.rig.modules,
                "core_radius": round(self.rig.core_radius, 4),
                "outer_radius": round(self.rig.outer_radius, 4),
                "tether": self.rig.tether,
                "petals": self.rig.petals,
            },
        }


def _pick(pool: tuple[Fragment, ...], rng) -> Fragment:
    weights = [max(frag.weight, 1e-9) for frag in pool]
    return rng.choices(pool, weights=weights, k=1)[0]


def _build_rig(seed: int, tags: frozenset[str]) -> Rig:
    rng = derive_rng(seed, "rig")
    stellar = bool(tags & {"stellar", "black_hole"})
    habitat = "habitat" in tags
    foundry = "foundry" in tags
    rings = rng.randint(2, 4 if stellar else 3)
    spokes = rng.choice([6, 8, 10, 12, 16, 18])
    modules = rng.randint(18, 36 if habitat or foundry else 28)
    core = rng.uniform(0.12, 0.22)
    outer = rng.uniform(0.78, 0.96)
    tether = "planetary" in tags or rng.random() < 0.25
    petals = rng.choice([0, 0, 6, 8, 12]) if foundry or "stellar" in tags else 0
    return Rig(
        rings=rings,
        spokes=spokes,
        modules=modules,
        core_radius=core,
        outer_radius=outer,
        tether=tether,
        petals=petals,
    )


def generate_identity(seed: int) -> Identity:
    """Assemble one identity from `seed`. Same seed, same identity, every time."""
    rng = derive_rng(seed, "identity")
    structure = _pick(STRUCTURES, rng)
    function = _pick(FUNCTIONS, rng)
    purpose = _pick(PURPOSES, rng)
    occupants = _pick(OCCUPANTS, rng)
    palette = _pick(PALETTES, rng)
    tags = (
        structure.tags
        | function.tags
        | purpose.tags
        | occupants.tags
        | palette.tags
    )
    return Identity(
        seed=seed,
        structure=structure,
        function=function,
        purpose=purpose,
        occupants=occupants,
        palette=palette,
        rig=_build_rig(seed, tags),
    )
