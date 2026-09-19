# 2-D Navier-Stokes Turbulence — Pseudospectral Vorticity-Streamfunction
## Kraichnan-Batchelor-Leith (1967) Inverse Energy Cascade — Blender 5.1

A 128 × 128 height-field stage floor that encodes four snapshots of 2D
turbulence as shape keys. Run `blueprint.py` in Blender 5.1 Scripting to
generate `ns2d_turbulence_floor.blend` and `ns2d_turbulence_floor.glb`.

### Physics

| Quantity | Symbol | Value |
|---|---|---|
| Kinematic viscosity | ν | 8 × 10⁻⁴ |
| Time step | Δt | 0.004 |
| Grid | N² | 128² = 16 384 |
| Injection wavenumber | k_f | 6 |
| Energy cascade slope | E(k) | k⁻⁵/³ (k < k_f) |
| Enstrophy cascade slope | E(k) | k⁻³ (k > k_f) |

### Shape keys

| Key | Stage | Description |
|---|---|---|
| Basis | t ~ 300 Δt | Early turbulence, small eddies at forcing scale |
| SK_Cascade | t ~ 800 Δt | Inverse cascade developing, larger structures |
| SK_Condensed | t ~ 1600 Δt | Coherent vortex dipole condensation |
| SK_Forced | t ~ 2600 Δt | Saturated forced state, domain-scale vortex |

### Colour map
- Cobalt `(0.027, 0.159, 0.557)` — negative vorticity (clockwise / cyclonic)
- Amber `(0.980, 0.620, 0.050)` — positive vorticity (anticlockwise / anticyclonic)

### Files
- `blueprint.py` — bpy script; run in Blender 5.1 Scripting editor
- `record.py` — automated viewport render → `videos/…/viewport.mp4`
- `SCREEN-RECORDING-NOTES.md` — OBS manual recording guide
- `ns2d_turbulence_floor.blend` — Blender file (generated)
- `ns2d_turbulence_floor.glb` — WebXR-ready GLB (generated)

### Outside sources
- Kraichnan RH (1967) *Physics of Fluids* 10:1417–1423. PD.
- NumPy BSD-3-Clause — https://numpy.org

### Studio tutorial
`/tutorials/blender-tutorial-python-numpy-2d-navier-stokes-turbulence-kraichnan-batchelor-leith-1967-inverse-cascade-pseudospectral-rk4-height-field-stage-floor-webxr`
