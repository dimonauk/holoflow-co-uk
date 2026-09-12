# Oregonator BZ Reaction-Diffusion — Height-Field Stage Floor

**Blender 5.1 · Python + numpy · CC0**  
Source: Field, Körös, Noyes (1972) JACS 94 8649–8664  
Tyson & Fife (1980) J Chem Phys 73 2224–2237

---

## What is this?

The Belousov-Zhabotinsky (BZ) reaction is one of nature's most photogenic
self-organising chemical oscillators. Bromate oxidises malonic acid in the
presence of a cerium catalyst — the famous experiment that fills a Petri dish
with rotating blue-and-gold spirals visible to the naked eye.

This blueprint integrates the **Oregonator** kinetics (Field-Körös-Noyes 1972,
reduced to two variables by Tyson-Fife 1980) on a periodic 128×128 grid using
explicit Forward Euler, then maps the activator concentration `u` to vertex
height and colour (cobalt = resting, amber = excited front).

The result is a 16384-vertex, 16129-quad stage floor with four shape keys
capturing different dynamical regimes of the same equations.

---

## Equations

```
ε ∂u/∂t = u(1 − u) − f·v·(u − q)/(u + q)  +  Du ∇²u
     ∂v/∂t = u − v

ε = 0.04   (fast/slow timescale ratio — the smaller, the sharper the pulse)
f = 1.4    (stoichiometric factor — controls wave spacing)
q = 0.002  (rate constant ratio — sets pulse-front threshold sharpness)
Du = 1.0   (activator diffuses; inhibitor v is immobile in gel experiments)
```

---

## Shape keys

| Key         | ε    | f   | IC            | t    | Dynamics                 |
|-------------|------|-----|---------------|------|--------------------------|
| Basis       | 0.04 | 1.4 | broken wave   | t=40 | 4-armed spiral           |
| SK_Fast     | 0.02 | 1.4 | broken wave   | t=40 | narrower, faster arms    |
| SK_Rings    | 0.04 | 1.4 | pacemaker disk| t=40 | concentric target rings  |
| SK_Meander  | 0.04 | 1.6 | random noise  | t=60 | spiral breakup/turbulence|

---

## How to run

1. Open Blender 5.1, create or open a blank `.blend` in this directory.
2. Open `blueprint.py` in the Scripting editor.
3. Click **Run Script**. Computation: ~20–40 seconds for all four shape keys.
4. Save as `bz_oregonator_floor.blend`.
5. To record: open `record.py`, run. Requires a camera scene.

---

## File artefacts

| File                          | Description                              |
|-------------------------------|------------------------------------------|
| `bz_oregonator_floor.blend`   | Blender scene (created by blueprint.py)  |
| `bz_oregonator_floor.glb`     | WebXR export (Draco-6, WebP, morph targets) |
| `blueprint.py`                | Authoritative build script               |
| `record.py`                   | Viewport animation recording             |
| `SCREEN-RECORDING-NOTES.md`   | OBS/screen-capture instructions          |

---

## Numerical notes

Explicit Euler with `dt = 0.002` stays within the stability bound for the
stiffest region of the limit cycle (near `u ≈ q`, where `|λ_max| ≈ 850`).
`dt × 850 = 1.70 < 2` satisfies the Euler condition. Clipping to `[0, 1]`
after each step absorbs any remaining overshoot.

---

## Related tutorials

- `/tutorials/blender-tutorial-python-numpy-barkley-excitable-medium-spiral-wave-uv-sphere-poi-head-webxr`
- `/tutorials/blender-tutorial-python-numpy-gray-scott-reaction-diffusion-turing-pattern-height-field-webxr`
- `/tutorials/blender-tutorial-python-numpy-complex-ginzburg-landau-pde-spiral-turbulence-benjamin-feir-defect-height-field-stage-floor-webxr`
