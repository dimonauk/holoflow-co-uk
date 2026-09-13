# FitzHugh-Nagumo Excitable Media
**Blender 5.1 | Python + numpy | CC0 | Holoflow Studio**

Produces a 128 × 128 displacement mesh from the FitzHugh-Nagumo (FHN) activator
field, with four shape keys encoding distinct excitable-media regimes:
trigger waves, two-armed spirals, concentric target rings, and single reentrant
spirals.  ETD1 (Cox-Matthews 2002) makes the stiff diffusion operator
unconditionally stable at dt = 0.10.

## Quick Start

```
blender --python blueprint.py
```

Output: `fhn_excitable.glb` (WebXR-ready, Draco-compressed)

## Equations

```
∂u/∂t = DU ∇²u + u − u³/3 − v + I_ext      (fast activator / voltage)
∂v/∂t = ε(u + A − B·v)                       (slow recovery variable)
```

ETD1 integration:  
```
û(n+1) = exp(L_u·dt)·û(n) + φ₁(L_u·dt)·N̂_u·dt
L_u(k) = −DU·|k|²       (spectral diffusion operator)
φ₁(z)  = expm1(z)/z     (Taylor-safe)
```

The recovery variable v has no spatial diffusion; it uses the scalar
exact exponential `exp(ε·B·dt)` with explicit coupling.

## Parameter Cheat-Sheet

| Variant | IC | Steps | Pattern |
|---|---|---|---|
| Basis | Edge pulse | 600 | Trigger wave front propagating left → right |
| SK_Spiral | S1+S2 cross-field | 1200 | Two-armed rotating spiral |
| SK_Target | Central pacemaker disc | 1400 | Concentric target rings |
| SK_Reentry | Half-plane + refractory quarter | 900 | Single reentrant spiral |

## Default Parameters

| Parameter | Value | Meaning |
|---|---|---|
| N | 128 | Grid side (128 × 128 = 16 384 vertices) |
| DU | 1.0 | Voltage diffusivity |
| DT | 0.10 | Time step (ETD1 unconditionally stable for diffusion) |
| EPS | 0.08 | Slow-fast ratio — small = fast wave, slow recovery |
| A_KIN | 0.70 | Recovery nullcline offset |
| B_KIN | 0.80 | Recovery damping |
| IEXT | 0.50 | Applied current (sub-threshold) |
| Z_SCALE | 0.50 | Height amplitude (Blender metres) |

## Files

| File | Purpose |
|---|---|
| `blueprint.py` | Expert bpy script — ETD1 FHN simulation + mesh + GLB export |
| `record.py` | Viewport animation rendering (8-snapshot S1+S2 spiral, 12 s) |
| `SCREEN-RECORDING-NOTES.md` | OBS instructions for screen.mp4 |
| `.expected-artefacts.json` | CI artefact manifest |

## Why ETD1?

Explicit Euler requires dt < (dx)² / (4·DU) ≈ 0.0005 at N = 128 (CFL).
ETD1 exact-exponentiates the stiff diffusion operator, removing that CFL
constraint entirely; the only stability requirement is on the explicit
kinetics and recovery, which comfortably allow dt = 0.10 — a 200× speedup.

## References

- FitzHugh R. (1961). *Impulses and physiological states in theoretical
  models of nerve membrane.* Biophys. J. 1(6):445–466.
  DOI: [10.1016/S0006-3495(61)86902-6](https://doi.org/10.1016/S0006-3495(61)86902-6)
- Barkley D. (1991). *A model for fast computer simulation of waves in
  excitable media.* Physica D 49:61–70.
  DOI: [10.1016/0167-2789(91)90194-E](https://doi.org/10.1016/0167-2789(91)90194-E)
- Cox S. M., Matthews P. C. (2002). *Exponential time differencing for stiff
  systems.* J. Comput. Phys. 176(2):430–455.
