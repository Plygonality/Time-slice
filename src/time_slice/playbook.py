"""One playbook, three screenshot folders.

The playbook is JSON Habitat-kit and Plygon-mcp already know how to apply.
It does not invent generator logic: seed → identity, then decay-pass +
signal-field per epoch. Load identity once, overlay each epoch, frame the
same camera, write the expected screenshot.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from time_slice.epochs import (
    EPOCHS,
    SCREENSHOT_FOLDERS,
    Slice,
    SliceSet,
    slice_seed,
)

FORMAT = "time-slice-playbook"
VERSION = 1
HOOK = "generators not one-offs"
VIEWPORT_NAME = "viewport.png"

LOOP: tuple[str, ...] = (
    "load identity from seed (once)",
    "apply decay-pass for epoch",
    "apply signal-field for epoch",
    "frame the same camera",
    "screenshot into screenshots/<epoch>/",
)

# Contract Habitat-kit / MCP read. Generator numbers come from slice_seed.
REQUIRED_PLAYBOOK_KEYS: tuple[str, ...] = (
    "format",
    "seed",
    "identity",
    "epochs",
)
REQUIRED_EPOCH_KEYS: tuple[str, ...] = (
    "seed",
    "epoch",
    "generator",
    "expected_screenshot",
)
REQUIRED_GENERATOR_KEYS: tuple[str, ...] = ("decay", "signal")


@dataclass(frozen=True)
class Playbook:
    slices: SliceSet

    @property
    def seed(self) -> int:
        return self.slices.seed

    def to_dict(self) -> dict[str, Any]:
        return {
            "format": FORMAT,
            "version": VERSION,
            "hook": HOOK,
            "seed": self.seed,
            "loop": list(LOOP),
            "folders": dict(SCREENSHOT_FOLDERS),
            "identity": self.slices.identity.to_dict(),
            "epochs": [_epoch_entry(item) for item in self.slices.slices],
        }

    def dumps(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=False) + "\n"


def expected_screenshot_path(epoch: str, output_root: str = "screenshots") -> str:
    """Repo-relative path Habitat-kit / MCP / Blend-ci should write."""
    return f"{output_root}/{epoch}/{VIEWPORT_NAME}"


def screenshot_folder_for(path: str | Path) -> Path:
    """Directory that must exist for a playbook's expected screenshot path."""
    target = Path(path)
    return target if target.suffix == "" else target.parent


def _epoch_entry(item: Slice) -> dict[str, Any]:
    dump = item.to_dict()
    generator = {
        "decay": dump["decay"],
        "signal": dump["signal"],
    }
    return {
        "seed": item.identity.seed,
        "epoch": dump["epoch"],
        "label": dump["label"],
        "folder": dump["folder"],
        "expected_screenshot": expected_screenshot_path(item.epoch),
        "generator": generator,
        "brief": dump["brief"],
        "tags": dump["tags"],
        "lighting": dump["lighting"],
        "occupancy": dump["occupancy"],
        "palette": dump["palette"],
        # Aliases so apply-script and Habitat-kit sockets keep reading the same keys.
        "decay": dump["decay"],
        "signal": dump["signal"],
    }


def build_playbook(seed: int) -> Playbook:
    return Playbook(slices=slice_seed(seed))


def dumps(playbook: Playbook) -> str:
    return playbook.dumps()


def write_playbook(seed: int, path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(build_playbook(seed).dumps(), encoding="utf-8")
    return target


def epoch_records(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Epoch objects from a combined playbook or a single-epoch JSON file."""
    if "epochs" in data:
        records = data["epochs"]
        if not isinstance(records, list) or not records:
            raise ValueError("playbook.epochs must be a non-empty list")
        return records
    return [data]


def validate_playbook(data: dict[str, Any]) -> dict[str, Any]:
    """Check the Habitat-kit / MCP contract. Does not generate a new seed."""
    if not isinstance(data, dict):
        raise ValueError("playbook must be a JSON object")
    missing = [key for key in REQUIRED_PLAYBOOK_KEYS if key not in data]
    if missing:
        raise ValueError(f"playbook missing keys: {', '.join(missing)}")
    if data.get("format") != FORMAT:
        raise ValueError(f"playbook.format must be {FORMAT!r}")
    seed = data["seed"]
    if not isinstance(seed, int):
        raise ValueError("playbook.seed must be an int")
    identity = data.get("identity")
    if isinstance(identity, dict) and identity.get("seed") not in (None, seed):
        raise ValueError(
            f"identity.seed {identity.get('seed')!r} != playbook.seed {seed}"
        )

    records = epoch_records(data)
    seen: list[str] = []
    seeds: list[int] = []
    for item in records:
        if not isinstance(item, dict):
            raise ValueError("each playbook epoch must be a JSON object")
        absent = [key for key in REQUIRED_EPOCH_KEYS if key not in item]
        if absent:
            raise ValueError(f"epoch missing keys: {', '.join(absent)}")
        epoch = item["epoch"]
        if epoch not in EPOCHS:
            raise ValueError(
                f"epoch must be one of {list(EPOCHS)}; got {epoch!r}"
            )
        if epoch in seen:
            raise ValueError(f"duplicate epoch {epoch!r} in playbook set")
        seen.append(epoch)
        epoch_seed = item["seed"]
        if not isinstance(epoch_seed, int):
            raise ValueError("epoch.seed must be an int")
        if epoch_seed != seed:
            raise ValueError(
                f"epoch {epoch!r} seed {epoch_seed} != set seed {seed}"
            )
        seeds.append(epoch_seed)
        generator = item["generator"]
        if not isinstance(generator, dict):
            raise ValueError("epoch.generator must be a JSON object")
        gen_missing = [key for key in REQUIRED_GENERATOR_KEYS if key not in generator]
        if gen_missing:
            raise ValueError(f"epoch.generator missing keys: {', '.join(gen_missing)}")
        shot = item["expected_screenshot"]
        if not isinstance(shot, str) or not shot:
            raise ValueError("epoch.expected_screenshot must be a path string")

    if len(set(seeds)) != 1:
        raise ValueError("seeds must be identical across the three epochs for a set")
    if set(seen) != set(EPOCHS):
        raise ValueError(
            f"playbook set must include {list(EPOCHS)}; got {seen}"
        )
    return data


def load_playbook(path: str | Path) -> dict[str, Any]:
    """Read committed playbook JSON. Does not re-run the generator."""
    target = Path(path)
    data = json.loads(target.read_text(encoding="utf-8"))
    return validate_playbook(data)


def iter_playbook_paths(root: str | Path) -> list[Path]:
    directory = Path(root)
    return sorted(path for path in directory.glob("*.json") if path.is_file())


def to_apply_script(playbook: Playbook, output_root: str = "screenshots") -> str:
    """Self-contained bpy. Plygon-mcp runs this; Blender does not need this package."""
    payload = json.dumps(playbook.to_dict())
    return _APPLY_TEMPLATE.format(
        payload=payload,
        output_root=output_root,
        epochs=repr(list(EPOCHS)),
    )


_APPLY_TEMPLATE = '''\
# Time-slice apply script. Generated. Plygon-mcp: execute_blender_code(this).
# Same seed, three epochs. Identity mesh once; decay-pass + signal-field per epoch.
# Screenshots land in {output_root}/<epoch>/viewport.png

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

PLAYBOOK = json.loads({payload!r})
OUTPUT_ROOT = Path({output_root!r})
EPOCH_IDS = {epochs}

IDENTITY = PLAYBOOK["identity"]
RIG = IDENTITY["rig"]
SEED = PLAYBOOK["seed"]
EPOCHS = {{item["epoch"]: item for item in PLAYBOOK["epochs"]}}


def _clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in list(bpy.data.meshes):
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in list(bpy.data.materials):
        if block.users == 0:
            bpy.data.materials.remove(block)
    for block in list(bpy.data.collections):
        if block.name.startswith("TimeSlice"):
            bpy.data.collections.remove(block)


def _collection(name):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)
    return coll


def _link(obj, coll):
    for existing in list(obj.users_collection):
        existing.objects.unlink(obj)
    coll.objects.link(obj)


def _mesh(name, verts, edges, faces, coll):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, edges, faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    _link(obj, coll)
    return obj


def _material(name, color, roughness, metallic, emission=(0.0, 0.0, 0.0, 1.0), strength=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    emit = nodes.new("ShaderNodeEmission")
    mix = nodes.new("ShaderNodeAddShader")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    emit.inputs["Color"].default_value = emission
    emit.inputs["Strength"].default_value = strength
    links.new(bsdf.outputs["BSDF"], mix.inputs[0])
    links.new(emit.outputs["Emission"], mix.inputs[1])
    links.new(mix.outputs["Shader"], out.inputs["Surface"])
    return mat


def _ring_verts(radius, n=64, z=0.0):
    return [
        (
            radius * math.cos(2 * math.pi * i / n),
            radius * math.sin(2 * math.pi * i / n),
            z,
        )
        for i in range(n)
    ]


def _build_identity():
    hull = _collection("TimeSlice.Hull")
    scaffold = _collection("TimeSlice.Scaffold")
    signal = _collection("TimeSlice.Signal")
    debris = _collection("TimeSlice.Debris")

    rings = int(RIG["rings"])
    spokes = int(RIG["spokes"])
    modules = int(RIG["modules"])
    r0 = float(RIG["core_radius"]) * 8.0
    r1 = float(RIG["outer_radius"]) * 8.0

    hub = _mesh(
        "Hub",
        [
            (r0 * 0.6 * math.cos(i * math.pi / 3), r0 * 0.6 * math.sin(i * math.pi / 3), 0.0)
            for i in range(6)
        ],
        [],
        [(0, 1, 2, 3, 4, 5)],
        hull,
    )
    hub["ts.kind"] = "hub"

    for ring_i in range(rings):
        t = (ring_i + 1) / rings
        radius = r0 + (r1 - r0) * t
        n = 48 + ring_i * 16
        verts = _ring_verts(radius, n)
        edges = [(i, (i + 1) % n) for i in range(n)]
        obj = _mesh(f"Ring.{{ring_i:02d}}", verts, edges, [], hull)
        obj["ts.kind"] = "ring"

    for spoke_i in range(spokes):
        ang = 2 * math.pi * spoke_i / spokes
        verts = [
            (r0 * math.cos(ang), r0 * math.sin(ang), 0.0),
            (r1 * math.cos(ang), r1 * math.sin(ang), 0.0),
        ]
        obj = _mesh(f"Spoke.{{spoke_i:02d}}", verts, [(0, 1)], [], hull)
        obj["ts.kind"] = "spoke"

    rng_mod = (SEED * 1103515245 + 12345) & 0x7FFFFFFF
    for mod_i in range(modules):
        ang = 2 * math.pi * mod_i / modules
        radius = r1
        cx, cy = radius * math.cos(ang), radius * math.sin(ang)
        s = 0.22
        dx, dy = -math.sin(ang) * s, math.cos(ang) * s
        verts = [
            (cx - dx, cy - dy, -0.08),
            (cx + dx, cy + dy, -0.08),
            (cx + dx, cy + dy, 0.08),
            (cx - dx, cy - dy, 0.08),
        ]
        obj = _mesh(f"Module.{{mod_i:03d}}", verts, [], [(0, 1, 2, 3)], hull)
        obj["ts.kind"] = "module"
        obj["ts.index"] = mod_i
        rng_mod = (rng_mod * 1103515245 + 12345) & 0x7FFFFFFF
        obj["ts.hash"] = rng_mod / 0x7FFFFFFF

        # Debris copy, hidden until relic.
        dverts = [(x + 0.4 * math.cos(ang + 0.4), y + 0.4 * math.sin(ang + 0.4), z - 0.3) for x, y, z in verts]
        chunk = _mesh(f"Debris.{{mod_i:03d}}", dverts, [], [(0, 1, 2, 3)], debris)
        chunk["ts.kind"] = "debris"
        chunk["ts.index"] = mod_i
        chunk.hide_viewport = True
        chunk.hide_render = True

    # Scaffold: extra concentric rings + offset spokes.
    for sc_i in range(4):
        radius = r0 + (r1 - r0) * (sc_i + 0.5) / 4.5
        n = 36
        verts = _ring_verts(radius, n, z=0.15)
        edges = [(i, (i + 1) % n) for i in range(n)]
        obj = _mesh(f"Scaffold.Ring.{{sc_i}}", verts, edges, [], scaffold)
        obj["ts.kind"] = "scaffold"
    for spoke_i in range(spokes):
        ang = 2 * math.pi * (spoke_i + 0.5) / spokes
        verts = [
            (r0 * math.cos(ang), r0 * math.sin(ang), 0.15),
            (r1 * math.cos(ang), r1 * math.sin(ang), 0.15),
        ]
        obj = _mesh(f"Scaffold.Spoke.{{spoke_i:02d}}", verts, [(0, 1)], [], scaffold)
        obj["ts.kind"] = "scaffold"

    if RIG["tether"]:
        verts = [(0.0, 0.0, 0.0), (0.0, 0.0, -r1 * 1.4)]
        obj = _mesh("Tether", verts, [(0, 1)], [], hull)
        obj["ts.kind"] = "tether"

    # Signal emitters sit on the same sites every epoch.
    emitters = max(modules, spokes * rings)
    for i in range(emitters):
        ang = 2 * math.pi * i / emitters
        lane = i % rings
        t = (lane + 1) / rings
        radius = r0 + (r1 - r0) * t
        loc = Vector((radius * math.cos(ang), radius * math.sin(ang), 0.35))
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=4, radius=0.08, location=loc)
        obj = bpy.context.active_object
        obj.name = f"Signal.{{i:03d}}"
        obj["ts.kind"] = "signal"
        obj["ts.index"] = i
        obj["ts.lane"] = lane
        _link(obj, signal)

    return hull, scaffold, signal, debris


def _ensure_camera_and_light():
    cam_data = bpy.data.cameras.new("TimeSlice.Camera")
    cam = bpy.data.objects.new("TimeSlice.Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = (0.0, -18.0, 10.0)
    cam.rotation_euler = (math.radians(58), 0.0, 0.0)
    cam_data.lens = 35
    bpy.context.scene.camera = cam

    sun_data = bpy.data.lights.new("TimeSlice.Sun", "SUN")
    sun = bpy.data.objects.new("TimeSlice.Sun", sun_data)
    bpy.context.scene.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(40), math.radians(20), math.radians(30))
    sun_data.energy = 4.0

    key_data = bpy.data.lights.new("TimeSlice.Key", "AREA")
    key = bpy.data.objects.new("TimeSlice.Key", key_data)
    bpy.context.scene.collection.objects.link(key)
    key.location = (8.0, -6.0, 6.0)
    key_data.energy = 200.0
    key_data.size = 4.0

    world = bpy.context.scene.world or bpy.data.worlds.new("TimeSlice.World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.02, 0.022, 0.03, 1.0)
        bg.inputs["Strength"].default_value = 0.4


def apply_epoch(epoch_id):
    spec = EPOCHS[epoch_id]
    gen = spec.get("generator") or {{}}
    decay = gen.get("decay") or spec["decay"]
    signal = gen.get("signal") or spec["signal"]
    incomplete = float(decay["incomplete"])
    scaffold_amt = float(decay["scaffold"])
    breach = float(decay["breach"])
    oxidation = float(decay["oxidation"])
    debris_amt = float(decay["debris"])

    hull = _material(
        "TS.Hull",
        color=(0.18 + 0.2 * (1.0 - oxidation), 0.16, 0.14, 1.0),
        roughness=0.25 + 0.6 * oxidation,
        metallic=0.85 - 0.4 * oxidation,
    )
    scaf = _material(
        "TS.Scaffold",
        color=(0.85, 0.62, 0.12, 1.0),
        roughness=0.45,
        metallic=0.3,
        emission=(1.0, 0.7, 0.15, 1.0),
        strength=2.0 * scaffold_amt,
    )
    ghost = float(signal["ghost"])
    amp = float(signal["amplitude"])
    sig = _material(
        "TS.Signal",
        color=(0.2, 0.7, 1.0, 1.0),
        roughness=0.2,
        metallic=0.0,
        emission=(0.3 + 0.4 * ghost, 0.75, 1.0, 1.0),
        strength=8.0 * amp,
    )
    deb = _material(
        "TS.Debris",
        color=(0.12, 0.1, 0.08, 1.0),
        roughness=0.9,
        metallic=0.4,
    )

    for obj in bpy.data.objects:
        kind = obj.get("ts.kind")
        if kind in {{"hub", "ring", "spoke", "tether", "module"}}:
            obj.data.materials.clear()
            obj.data.materials.append(hull)
            if kind == "module":
                h = float(obj.get("ts.hash", 0.5))
                missing = h < incomplete or (epoch_id == "relic" and h < breach)
                obj.hide_viewport = missing
                obj.hide_render = missing
        elif kind == "scaffold":
            obj.data.materials.clear()
            obj.data.materials.append(scaf)
            visible = scaffold_amt > 0.15
            obj.hide_viewport = not visible
            obj.hide_render = not visible
        elif kind == "signal":
            obj.data.materials.clear()
            obj.data.materials.append(sig)
            idx = int(obj.get("ts.index", 0))
            lane = int(obj.get("ts.lane", 0))
            coherent = float(signal["coherence"])
            density = float(signal["density"])
            # Construction: chaotic (index hash). Operational: every Nth on a lane.
            # Relic: sparse + ghost (drawn dim even when "dead").
            live = ((idx * 17 + SEED) % 100) / 100.0 < density
            if coherent > 0.6:
                live = (idx % max(1, int(3 - 2 * density))) == 0 or live
            if epoch_id == "relic" and ghost > 0.5:
                live = live or ((idx + lane) % 7 == 0)
            obj.hide_viewport = not live
            obj.hide_render = not live
            obj.scale = (1.0 + amp, 1.0 + amp, 1.0 + amp)
        elif kind == "debris":
            obj.data.materials.clear()
            obj.data.materials.append(deb)

    for obj in bpy.data.objects:
        if obj.get("ts.kind") != "debris":
            continue
        idx = int(obj.get("ts.index", 0))
        partner = bpy.data.objects.get(f"Module.{{idx:03d}}")
        show = False
        if partner is not None and partner.hide_viewport and debris_amt > 0.4:
            show = True
        obj.hide_viewport = not show
        obj.hide_render = not show

    sun = bpy.data.objects.get("TimeSlice.Sun")
    if sun and sun.data:
        sun.data.energy = 2.2 if epoch_id == "relic" else 4.5 if epoch_id == "operational" else 3.0
    key = bpy.data.objects.get("TimeSlice.Key")
    if key and key.data:
        key.data.energy = 80.0 if epoch_id == "relic" else 260.0 if epoch_id == "construction" else 180.0


def shoot(epoch_id):
    apply_epoch(epoch_id)
    folder = OUTPUT_ROOT / epoch_id
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "viewport.png"
    scene = bpy.context.scene
    scene.render.filepath = str(path)
    scene.render.image_settings.file_format = "PNG"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    bpy.ops.render.opengl(write_still=True)
    return str(path)


def run():
    _clear()
    _build_identity()
    _ensure_camera_and_light()
    written = [shoot(epoch_id) for epoch_id in EPOCH_IDS]
    print("time-slice wrote:", ", ".join(written))
    return written


if __name__ == "__main__":
    run()
'''
