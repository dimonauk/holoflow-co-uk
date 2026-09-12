# φ⁴ Kink-Antikink Collision — Space-Time Height-Field Stage Floor

**Equation** | ∂²φ/∂t² = ∂²φ/∂x² + φ − φ³  ·  V(φ) = ¼(1−φ²)²  
**Technique** | Leapfrog (Störmer-Verlet) · NumPy · bpy direct-data API  
**Blender** | 5.1  
**Licence** | CC0  
**Source** | Campbell, Schonfeld & Wingate, *Physica D* 9 (1983) 1–32

---

## What this is

φ⁴ (phi-four) scalar field theory is the simplest relativistic field equation
that has *topological* kink solutions — field configurations that cannot be
continuously deformed back to the vacuum.  The kink connects the two degenerate
ground states φ = −1 and φ = +1, much like a domain wall in a ferromagnet.

Unlike the KdV or sine-Gordon equations (both integrable, solitons pass through
each other unchanged), φ⁴ is **non-integrable**: kink-antikink collisions
emit radiation and can temporarily trap the pair into an oscillating *bion*
bound state.  Whether the pair escapes or stays bound depends exquisitely on the
initial speed — giving rise to the famous **resonance windows**.

## Space-time carpet

The Blender floor maps:

| Axis | Field |
|------|-------|
| x (horizontal) | Space ∈ [−6, 6], world ±2 m |
| y (depth) | Time  ∈ [0, 30], world 0–3 m |
| z (height) | φ + 1, so vacuum floor level = 0 |

Cobalt = vacuum φ = −1.  Amber ridge = kink interior φ ≈ +1.
The two kink worldlines enter from the front corners and converge toward
the centre; what happens there depends on the shape key.

## Shape keys

| Name | Velocity | Physics |
|------|----------|---------|
| Basis | v = 0.10 | Below critical — bion capture, oscillating bound state |
| SK_TwoBounce | v = 0.193 | Two-bounce resonance window — two collisions then escape |
| SK_Critical | v = 0.26 | Near v_c ≈ 0.2598 — marginal escape + large radiation plume |
| SK_Escape | v = 0.40 | Well above v_c — single-pass, clean exit |

## Running

```
Blender 5.1 → Scripting workspace → open blueprint.py → Run Script
```

Output files created next to the script:
- `phi4_kink_floor.blend`
- `phi4_kink_floor.glb`

Then for the viewport animation:

```
Run record.py (in the same .blend file)
```

## Physics notes

The **critical velocity** v_c ≈ 0.2598 separates capture from escape.
Below v_c, within a fractal set of narrow "resonance windows", the pair
escapes after n bounces (n = 2, 3, 4, …).  Peyrard & Campbell (1983) showed
these windows arise because energy is temporarily stored in the kink's
*internal vibrational mode* at ω_int ≈ √3 ≈ 1.73 and then returned to
translational motion.  The window widths follow a Fibonacci-like recursion —
self-similar structure that foreshadowed later work on fractal basin boundaries.

## Solver notes

- **Leapfrog**: φⁿ⁺¹ = 2φⁿ − φⁿ⁻¹ + DT²·f(φⁿ)  where f = φ_xx + φ − φ³
- **CFL**: DT = 0.04, DX = 12/128 ≈ 0.094 → σ = DT/DX ≈ 0.43 < 1 ✓
- **Dirichlet BCs**: φ[ghost] = −1 (far-vacuum), justified because kinks
  never reach the domain walls within T_FINAL = 30

## Files

| File | Description |
|------|-------------|
| `blueprint.py` | Main Blender script, runs four integrations |
| `record.py` | Viewport animation recorder |
| `SCREEN-RECORDING-NOTES.md` | OBS instructions for screen.mp4 |
| `phi4_kink_floor.blend` | Generated Blender scene |
| `phi4_kink_floor.glb` | WebXR export, Draco-6 compressed |
