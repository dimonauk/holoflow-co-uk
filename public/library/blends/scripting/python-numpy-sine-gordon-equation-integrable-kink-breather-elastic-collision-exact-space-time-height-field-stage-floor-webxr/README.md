# Sine-Gordon Equation — Integrable 1+1D PDE

**φ_tt − φ_xx + sin φ = 0**

A 128×128 space-time height-field stage floor for WebXR, with four shape keys
showing the exact multi-soliton solutions of the Sine-Gordon equation.

---

## The physics in two sentences

The Sine-Gordon equation is the simplest relativistic field theory with a
periodic potential V(φ) = 1 − cos φ. Its complete integrability — demonstrated
via the AKNS inverse scattering transform (Ablowitz, Kaup, Newell, Segur 1973)
— means every multi-soliton solution is given by an exact algebraic formula,
and collisions are perfectly elastic.

## Four shape keys

| Key | Solution | What you see |
|-----|----------|--------------|
| Basis | Single kink, v = 0.65 | One cobalt-to-amber ridge sweeping diagonally |
| SK_Breather | Stationary breather, ω = 0.50 | Symmetric butterfly: oscillating bound state |
| SK_Collision | Kink–antikink collision, v = 0.65 | Elastic "X" with phase shift visible |
| SK_TwoKink | Two co-propagating kinks, v₁ = 0.80, v₂ = 0.30 | Two ridges, one overtaking the other |

## Why exact solutions rather than numerical integration?

Because they exist. The Hirota τ-function gives every N-soliton solution
in closed form. Using them here:

1. Demonstrates integrability concretely — the elastic collision is exact,
   not approximate.
2. Avoids discretisation error and the CFL constraint.
3. Lets us choose parameter values freely without worrying about stability.

Compare with the φ⁴ blueprint, which *must* use leapfrog time-stepping because
φ⁴ is non-integrable and has no closed-form multi-soliton solutions.

## Mesh statistics

- **Vertices:** 128 × 128 = 16 384
- **Quads:** 127 × 127 = 16 129
- **Vertex attribute:** `SG_Field` — FLOAT_COLOR, POINT domain
- **Colour ramp:** Cobalt (0.03, 0.15, 0.58) → Amber (1.00, 0.65, 0.00) by φ/4π
- **Shape keys:** Basis / SK_Breather / SK_Collision / SK_TwoKink

## Key equations

```
Single kink (v, x₀):
  φ_K(x,t) = 4 arctan[exp(γ(x − vt − x₀))]    γ = 1/√(1−v²)
  Topological charge Q = +1

Breather (ω):
  φ_B(x,t) = 4 arctan[(β/ω) sin(ωt) / cosh(βx)]    β = √(1−ω²)
  Mass M_B = 16β < 2M_kink (bound state)

Kink–antikink collision (v):
  φ_{KĀ}(x,t) = 4 arctan[v sinh(γx) / cosh(γvt)]
  Phase shift Δ = (2/γ) log(2v)  (only trace of the meeting)
```

## Files

```
blueprint.py             — builds mesh, shape keys, exports GLB
record.py                — renders viewport.mp4 (camera orbit + SK morph)
SCREEN-RECORDING-NOTES.md — OBS instructions for screen.mp4
README.md                — this file
.expected-artefacts.json — manifest with cross-references
```

## Running

```bash
# Build the .blend and export GLB
blender --background --python blueprint.py

# Render the viewport animation
blender --background sine_gordon_floor.blend --python record.py
```

## Outside sources

- Scott AC, Chu FYF, McLaughlin DW (1973) "The soliton: A new concept in
  applied science" *Proc. IEEE* 61(10):1443–1483 — PD equations.
  <https://doi.org/10.1109/PROC.1973.9296>

- Ablowitz MJ, Kaup DJ, Newell AC, Segur H (1973) "Method for Solving
  the Sine-Gordon Equation" *Physical Review Letters* 30(25):1262 — PD.
  <https://doi.org/10.1103/PhysRevLett.30.1262>
