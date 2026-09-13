# Swift-Hohenberg Equation (1977) — Stripe, Hexagon & Labyrinth Pattern Formation

**Blender 5.1 · Python bpy + numpy · CC0**

## What this builds

A 128 × 128 height-field stage floor whose topology is computed by integrating
the Swift-Hohenberg PDE using an ETD1 pseudo-spectral method.  Four GLTF morph
targets encode qualitatively distinct pattern regimes:

| Shape key | r | γ | Pattern | Steps |
|---|---|---|---|---|
| `Basis` | 0.30 | 0 | parallel stripes (rolls) | 300 |
| `SK_Hex` | 0.30 | +1.6 | hexagonal lattice | 400 |
| `SK_Labyrinth` | 0.05 | 0 | labyrinthine near onset | 600 |
| `SK_Inverted` | 0.30 | −1.6 | inverted hexagons / spots | 400 |

Vertex colour attribute `SH_Order` (FLOAT_COLOR, per-point domain) maps the
order parameter u linearly: cobalt (u ≈ minimum) → amber (u ≈ maximum).

## Running

```bash
# In Blender 5.1 Scripting workspace:
# 1. Open blueprint.py and press Run Script.
# 2. Open record.py and press Run Script for the viewport render.
```

Expected terminal output:
```
[SH] Basis: stripes (r=0.30, γ=0) …
[SH] SK_Hex: hexagons (r=0.30, γ=+1.6) …
[SH] SK_Labyrinth: near onset (r=0.05, γ=0) …
[SH] SK_Inverted: inverted hexagons/spots (r=0.30, γ=−1.6) …
[SH] Exported → //sh_pattern_floor.glb
```

## The equation

```
∂u/∂t = r · u  −  (1 + ∇²)² u  +  γ · u²  −  u³
```

The operator `(1+∇²)²` selects **exactly one spatial wavelength** λ_c = 2π,
regardless of the control parameter r.  This makes SHE the canonical model for
studying pattern selection: stripes vs hexagons, ordering kinetics, defect
proliferation — all without the wavelength changing.

The ETD1 scheme (Cox-Matthews 2002) integrates the linear part `L̂_k = r − (1−k²)²`
analytically in Fourier space, lifting the stiff CFL restriction that would
otherwise require dt ≈ 3×10⁻⁵ for N=128.

## Outputs (after running)

- `sh_pattern_floor.blend` — Blender file with object, material, shape keys
- `sh_pattern_floor.glb` — Draco-compressed GLTF with morph targets + vertex colours
- `../../videos/scripting/<slug>/viewport.mp4` — rendered animation (record.py)
- `../../videos/scripting/<slug>/screen.mp4` — OBS screen capture (SCREEN-RECORDING-NOTES.md)

## Tutorial

`/tutorials/blender-tutorial-python-numpy-swift-hohenberg-1977-stripe-hexagon-labyrinth-etd1-spectral-height-field-stage-floor-webxr`

## Licence

The mathematics is in the public domain.  `numpy` is BSD-3.  This file and
all generated artefacts are CC0.
