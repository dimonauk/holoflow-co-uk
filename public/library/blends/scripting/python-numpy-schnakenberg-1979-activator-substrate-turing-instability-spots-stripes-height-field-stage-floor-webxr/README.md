# Schnakenberg Activator-Substrate — Turing Instability

**Blender 5.1 · Python + NumPy · ETD1 Spectral · CC0**

## What this is

The Schnakenberg (1979) reaction-diffusion system is the simplest two-component
model that exhibits Turing pattern formation with an exactly provable stability
boundary.  The activator `u` auto-catalytically produces itself via the `u²v`
cubic term; the substrate `v` is consumed by that same term.  Because the
nonlinearity is polynomial — not rational like Gierer–Meinhardt — the
dispersion relation and Turing conditions are closed-form.

```
∂u/∂t = Du ∇²u + γ(a − u + u²v)
∂v/∂t = Dv ∇²v + γ(b − u²v)
```

## Files

| File | Purpose |
|------|---------|
| `blueprint.py` | Full Blender script: runs PDEs, builds 128×128 mesh, exports GLB |
| `record.py` | Viewport animation renderer (run after blueprint.py) |
| `SCREEN-RECORDING-NOTES.md` | OBS instructions for `screen.mp4` |
| `.expected-artefacts.json` | Artefact manifest |

## Output artefacts

- `schnakenberg_turing_floor.blend` (saved manually after running blueprint.py)
- `schnakenberg_turing_floor.glb` — 16 384 vertices, 16 129 quads, Draco-6,
  four morph targets (Basis / SK_Coarse / SK_Fine / SK_Bloom)

## Shape keys

| Key | Parameters | Pattern |
|-----|-----------|---------|
| Basis | a=0.1268, b=0.7924, γ=1000 | Murray-textbook reference spots |
| SK_Coarse | a=0.10, b=0.90, γ=1000 | Larger u*, coarser spot array |
| SK_Fine | a=0.1268, b=0.7924, γ=3000 | Same chemistry, √3× finer λ |
| SK_Bloom | a=0.18, b=0.90, γ=1000 | Higher u*, dense spots |

## How to run

1. Open Blender 5.1; switch to **Scripting** workspace.
2. Open `blueprint.py`, press **Run Script**.
   Expected console output: "Turing verification" table then "Exported".
3. File → Save As `schnakenberg_turing_floor.blend`.
4. (Optional) Open `record.py`, press **Run Script** to render `viewport.mp4`.

## Turing condition quick-check

At steady state `(u*, v*) = (a+b,  b/(a+b)²)`:

```
det A = γ²(a+b)³ > 0  ← always
k_c²  = γ[(b−a)Dv/(a+b) − (a+b)²Du] / (2 Du Dv)  ← must be > 0
Turing:  k_c² > 0  AND  (f_u Dv + g_v Du)² > 4 Du Dv det A
```

All four regimes pass; the script prints verification before running.

## Licence

CC0 1.0 — public domain.
Equation system from Schnakenberg (1979) J. Theor. Biol. 81:389–400.
