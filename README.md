# Time-slice

Same seed, three epochs. One playbook, three screenshot folders.

A generator that only fires once is a prompt. Time-slice holds identity in the seed and replays it across **under construction**, **operational**, and **relic** so the MCP loop can prove the system holds.

```
seed  →  identity (brief tags)
      →  decay-pass + signal-field  per epoch
      →  one playbook
      →  screenshots/construction
         screenshots/operational
         screenshots/relic
```

[Plygon-mcp](https://github.com/Plygonality/Plygon-mcp) is the loop: inspect → apply → screenshot. This repo is the generator that loop is allowed to run more than once.

| Role | Job |
|---|---|
| **This library** | Seed → identity. Epoch overlay. Decay-pass. Signal-field. Playbook. |
| **[Plygon-mcp](https://github.com/Plygonality/Plygon-mcp)** | Apply the playbook in Blender and write the three folders. |
| **[Hard Sci-Fi Idea Generator](https://github.com/Plygonality/Hard-SciFi-idea-generator)** | Sibling: a concept seed you can reuse as a Time-slice seed. |
| **The `.blend`** | Working cache, never the source of truth. |

## Why this repo exists

Look-dev that starts from a fresh prompt every time cannot tell you whether the generator is a system. Time-slice can:

- The **seed** is the identity (structure, function, purpose, occupants, palette DNA, silhouette).
- The **epoch** is a parameter. It does not redesign the hull.
- **Brief tags** stay on the identity and pick up epoch state (`constructing` / `complete` / `relic`).
- **Decay-pass** is the geometry/material weathering (incomplete, scaffold, oxidation, breach, debris).
- **Signal-field** is the activity field on the *same emitter sites* (density, coherence, amplitude, wavelength, ghost).
- **One playbook** drives the MCP loop. **Three screenshot folders** catch the proof.

Same camera. Same rig. Time changed.

## Install

Python 3.10+. No third-party packages at runtime.

```bash
pip install -e ".[dev]"
```

## Usage

Canonical invoke (from a clone, or after `pip install .`):

```bash
python -m time_slice --seed 1234
```

After install, the same entry point is the console script:

```bash
time-slice --seed 1234
```

```
==============================================================
TIME-SLICE 1/3                                   seed 1234
==============================================================

[ IDENTITY ]
  a Dyson Swarm of collector petals, siphoning plasma as
  structural feedstock, governed as a foundry-state for a
  machine ecology.

[ EPOCH ] under construction

[ BRIEF TAGS ] constructing, foundry, incomplete, orbital, organic, ...

[ DECAY-PASS ]
  amount 0.14   incomplete 0.57   scaffold 0.87
  oxidation 0.08   breach 0.01   debris 0.16

[ SIGNAL-FIELD ]
  density 0.83   coherence 0.19   amplitude 0.90
  wavelength 0.29   ghost 0.00
```

### Commands

| Command | Meaning |
| --- | --- |
| `time-slice --seed N` | Print all three epoch briefs |
| `time-slice --seed N --epoch relic` | One epoch |
| `time-slice dump --seed N` | JSON of identity + slices |
| `time-slice playbook --seed N -o playbooks/seed_N.json` | Write the MCP playbook |
| `time-slice preview --seed N --out screenshots` | SVG triptych into the three folders |
| `time-slice apply-script --seed N` | Self-contained `bpy` for Plygon-mcp |
| `time-slice list-tags` | Identity tags the pools can produce |
| `time-slice list-epochs` | `construction` `operational` `relic` |

Reproduce any printed set with the same `--seed`. The preview and the playbook use that seed; they do not invent a new one.

```bash
python -m time_slice --seed 1234
python -m time_slice preview --seed 1234 --out screenshots
python -m time_slice playbook --seed 1234 -o playbooks/seed_1234.json
python -m time_slice apply-script --seed 1234 -o /tmp/time_slice_apply.py
```

## MCP loop

One playbook. The agent does not author a new scene per epoch.

1. `time-slice playbook --seed 1234 -o playbooks/seed_1234.json`
2. `time-slice apply-script --seed 1234` → Plygon-mcp `execute_blender_code`
3. The script loads identity once, then for each epoch: **decay-pass** → **signal-field** → same camera → `screenshots/<epoch>/viewport.png`

The SVG preview is the no-DCC stand-in. When Blender is listening, `viewport.png` lands next to `preview.svg` in each folder.

```
screenshots/
  gallery.html
  construction/preview.svg   (+ viewport.png from MCP)
  operational/preview.svg
  relic/preview.svg
```

Open `screenshots/gallery.html`. Three columns, one seed.

## Decay-pass / signal-field

Bind these as Geometry Node or shader inputs. Do not bake them into the identity mesh.

**Decay-pass** — `amount`, `incomplete`, `scaffold`, `oxidation`, `breach`, `debris`

| Epoch | Reads as |
|---|---|
| under construction | High scaffold, high incomplete, almost no oxidation |
| operational | Lived-in wear, no scaffold, hull complete |
| relic | Oxidation, breach, debris. Scaffold gone. |

**Signal-field** — `density`, `coherence`, `amplitude`, `wavelength`, `ghost`

| Epoch | Reads as |
|---|---|
| under construction | Chaotic, hot, work-lights and arcs |
| operational | Structured lanes, running lights |
| relic | Sparse survivors, ghost traces on dead channels |

Emitter sites are seed-locked. Epoch only weights which sites are live.

## Tests

```bash
pytest -q
UPDATE_GOLDENS=1 pytest tests/test_golden.py   # rewrite the seed-1234 fixture after an intentional dump change
```

Goldens live in `tests/goldens/`. If a generator change is intentional, update them. If it is not, the test failed for a reason.

## Layout

```
src/time_slice/     library
examples/           canonical seed as Python
playbooks/          MCP playbook JSON
screenshots/        three epoch folders + gallery
tests/goldens/      canonical dump for seed 1234
```
