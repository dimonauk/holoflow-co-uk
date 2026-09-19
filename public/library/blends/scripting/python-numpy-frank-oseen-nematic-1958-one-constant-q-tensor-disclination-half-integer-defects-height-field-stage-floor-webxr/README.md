# Frank-Oseen Nematic LC — Director Field, Disclination Defects

**Blender 5.1 · Python / numpy · Stage Floor · WebXR**

One-constant Frank elastic energy: `F = K/2 ∫|∇θ|² dA → ∇²θ = 0`

The nematic director field θ(x,y) satisfies Laplace's equation in the
one-constant approximation, admitting an exact superposition solution for
point disclinations. Four shape keys sweep through the principal defect
configurations found experimentally in confined nematic films.

## Files

| File | Purpose |
|------|---------|
| `blueprint.py` | Blender 5.1 script: analytic superposition director field → 128×128 order-parameter height-field with 4 shape keys → GLB export |
| `record.py` | Viewport animation: shape-key morph renders `viewport.mp4` |
| `SCREEN-RECORDING-NOTES.md` | OBS / Game Bar instructions for `screen.mp4` |
| `.expected-artefacts.json` | Artefact manifest and cross-references |

## Shape Keys

| Key | Defect config | Director pattern |
|-----|---------------|-----------------|
| `Basis` | +½,+½,−½,−½ quadrupole | Charge-neutral; most common in confined planar cells |
| `SK_Comet` | Single +½ at origin | Comet / radial: all director lines diverge from core |
| `SK_Hedgehog` | Single +1 at origin | Full radial escape; topologically unstable in 2D nematics |
| `SK_Anneal` | ±½ pair at ±0.15 | Pre-annihilation geometry; elastic attraction drives fusion |

## Key Physics

- **Charge**: Half-integer topological charge allowed because n̂ ≡ −n̂ (Z₂ symmetry).
- **Superposition**: θ = Σ sₐ arctan2(y−yₐ, x−xₐ) solves ∇²θ = 0 exactly.
- **Order parameter**: S = 1 − exp(−d²_min/ξ²), zero at the isotropic core, one in bulk.
- **Height field**: Z = S × Z_SCALE — defect cores appear as pits on the floor mesh.
- **Colour**: (θ mod π)/π → cobalt (0) … amber (1). Period = π because n̂ ≡ −n̂.

## Licence

CC0 — blueprint and record scripts are original works.
Sources credited and linked in `.expected-artefacts.json` and the tutorial page.
