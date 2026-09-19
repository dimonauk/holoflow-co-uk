# N-Body Gravitational Dynamics — Leapfrog Integration — Poi Orbital Dance (Blender 5.1)

**Topic:** Direct-sum N-body gravity with Plummer softening, integrated via
the leapfrog (Störmer–Verlet) symplectic scheme. Eight point masses orbit and
interact, each leaving a neon trail tube. Poi-head spheres track each body's
tip in real time. EEVEE Next bloom on a black world produces a long-exposure
light-painting aesthetic.

**Blender version:** 5.1  
**Category:** Geometry Nodes / Scripting hybrid  
**Licence:** CC0 (public domain — you may use, modify, and redistribute freely)

## Files

| File | Purpose |
|---|---|
| `blueprint.py` | Full Python scene builder: integration + curve trails + poi heads + GLB export |
| `record.py` | EEVEE animation render → viewport.mp4 |
| `SCREEN-RECORDING-NOTES.md` | OBS / Game Bar instructions for screen.mp4 |

## Expected artefacts

After running `blueprint.py`:
- `nbody_orbital.glb` — exported to `public/library/glbs/…/`
- `viewport.mp4` — rendered by `record.py`
- `screen.mp4` — captured manually per SCREEN-RECORDING-NOTES.md

## Physics reference

- Newton's law of universal gravitation: F = G·m₁·m₂/r²
- Plummer softening (1911): replaces r³ denominator with (r²+ε²)^(3/2)
- Leapfrog integration: kicks velocity at half-steps → symplectic, second-order, zero secular energy drift

## Key parameters (blueprint.py top of file)

| Constant | Default | Effect |
|---|---|---|
| `N_BODIES` | 8 | Number of bodies (up to ~32 before performance drops) |
| `G` | 2.0 | Gravitational constant (scene units) |
| `SOFT_EPS` | 0.05 | Plummer softening — set to 0 for exact gravity (risk: singularities) |
| `DT` | 0.012 | Timestep — halve for more accurate long-term orbits |
| `N_FRAMES` | 300 | Animation length in Blender frames (30 fps → 10 s) |

## Tutorial

`/tutorials/blender-tutorial-gn-simulation-zone-n-body-gravity-leapfrog-orbital-dance-poi-webxr`
