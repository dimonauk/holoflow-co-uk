# Haldane Model 1988 — Chern Insulator Berry Curvature Height Field

**Blender 5.1 · Python + NumPy · Stage Floor WebXR**

## What this is

A 128×128 quad stage floor whose height at each point is the Berry curvature
Ω(kx, ky) of the lower band of the Haldane honeycomb Hamiltonian.
In the topological phase (Chern number C = ±1) the curvature concentrates into
two sharp peaks at the K and K′ Dirac points of the hexagonal Brillouin zone;
as the staggered mass M passes through the critical value 3√3 t₂ sin φ the
peaks collapse, the Chern number jumps to zero, and the landscape flattens.

## Files

| File | Purpose |
|------|---------|
| `blueprint.py` | Creates mesh, shape keys, material, exports GLB |
| `record.py`    | Adds camera + lights, animates shape-key morphing, renders viewport.mp4 |
| `haldane_floor.blend` | Blender scene (generated) |
| `haldane_floor.glb`   | Draco-6 WebP GLB (generated) |
| `SCREEN-RECORDING-NOTES.md` | OBS instructions for screen.mp4 |

## Shape keys

| Key | φ | M | Chern C | Physics |
|-----|---|---|---------|---------|
| Basis | π/2 | 0 | +1 | Topological — equal peaks at K and K′ |
| SK_PhiPi4 | π/4 | 0 | +1 | Weaker curvature (sin(π/4) < sin(π/2)) |
| SK_NearCrit | π/2 | 0.95 M_c | +1 | Approaching phase boundary M_c ≈ 1.039 |
| SK_Trivial | π/2 | 1.5 M_c | 0 | Trivial — nearly flat Berry landscape |

## How to run

```bash
# Step 1: build the mesh
blender --background --python blueprint.py

# Step 2: render the animation
blender haldane_floor.blend --python record.py
```

## Outside sources

- Haldane FDM (1988) PRL 61(18):2015 — original model, public domain mathematics
- Thouless et al. (1982) PRL 49(6):405 — Chern number = Hall conductance, public domain
- Asbóth, Oroszlány, Pályi (2016) arXiv:1509.02295 — CC-BY 4.0 lecture notes
- NumPy (Harris et al. 2020) Nature 585:357 — BSD-3-Clause
