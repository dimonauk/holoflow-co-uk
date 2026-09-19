# 3-State Potts Model — Wu 1982 Self-Dual Exact Tc

**Blender 5.1 · Python / NumPy · Scripting topic**
**Licence: CC0**

---

## What this is

A 128 × 128 stage-floor mesh where each site carries one of three spin
states σ ∈ {0, 1, 2}.  Height and colour encode the normalised state
value σ/2, producing a terrace-style landscape that evolves from ordered
three-colour domains below Tc to a critical fractal mosaic exactly at Tc
to short-range disorder above.

---

## Files

| File | Purpose |
|---|---|
| `blueprint.py` | Run in Blender Scripting workspace to build the mesh |
| `record.py` | Run after blueprint.py to render `viewport.mp4` |
| `SCREEN-RECORDING-NOTES.md` | OBS / Game Bar instructions for `screen.mp4` |
| `potts3_floor.blend` | Generated Blender file (produced by blueprint.py) |
| `potts3_floor.glb` | Generated GLB for WebXR (Draco-6, WebP textures) |

---

## Physics in 90 seconds

The **q-state Potts model** (Potts 1952) generalises the Ising model:

```
H = −J Σ_{⟨ij⟩} δ(σᵢ, σⱼ)    σᵢ ∈ {0, 1, …, q−1}
```

For q = 2 this is identical to the Ising model.  For q = 3 and q = 4 the
2D transition remains second-order (continuous).  For q ≥ 5 the transition
becomes first-order (discontinuous latent heat).  This boundary is exact
and follows from conformal field theory (CFT): the c = 1 barrier.

The self-duality of the 2D square-lattice Potts model pins the exact
critical temperature (Wu 1982):

```
e^{J/Tc} = 1 + √q      →      Tc = J / ln(1 + √q)
```

For q = 3:  Tc ≈ 0.9950 J/k_B.

| Phase | T | Behaviour |
|---|---|---|
| Quasi-ordered | T < Tc | Large single-state domains; power-law M ~ (Tc − T)^{β} |
| Critical (c=4/5) | T = Tc | Fractal domain mosaic, G(r) ~ r^{−(d−2+η)} |
| Disordered | T > Tc | Short-range clusters, exponential G(r) |

Exact critical exponents (Nienhuis 1982 PRL, CFT):

| Exponent | Value | Meaning |
|---|---|---|
| β | 1/9 ≈ 0.111 | Magnetisation M ~ (Tc−T)^β |
| γ | 13/9 ≈ 1.444 | Susceptibility χ ~ |T−Tc|^{−γ} |
| ν | 5/6 ≈ 0.833 | Correlation length ξ ~ |T−Tc|^{−ν} |
| η | 4/15 ≈ 0.267 | G(r, Tc) ~ r^{−(d−2+η)} |

---

## Shape keys

| Key | T / Tc | T (J/k_B) | Physics |
|---|---|---|---|
| `Basis` | 0.50 | ≈ 0.498 | Large ordered domains, sharp walls |
| `SK_Critical` | 1.00 | ≈ 0.995 | Critical mosaic, β=1/9 |
| `SK_HotCrit` | 1.50 | ≈ 1.493 | Short-range order, dissolving domains |
| `SK_HighT` | 3.00 | ≈ 2.985 | Fully disordered, equal populations |

---

## How to run

1. Open Blender 5.1 → Scripting workspace.
2. Open `blueprint.py`, click **Run Script**.
3. Switch to 3D Viewport; the floor object `potts3_floor` appears.
4. Export GLB: File → Export → glTF 2.0 (Draco-6, WebP, +Y up).
5. (Optional) Open `record.py` and **Run Script** to render the animation.

---

## Outside sources

- Potts RB 1952 *Proc. Camb. Phil. Soc.* 48:106-109 — original q-state generalisation (PD > 70 yr)
- Wu FY 1982 *Rev. Mod. Phys.* 54:235-268 — canonical review; self-dual Tc derivation (equations CC0)
- Nienhuis B 1982 *PRL* 49:1062 — exact critical exponents from CFT for q = 2,3,4 (PD > 40 yr)
- NumPy — BSD-3-Clause — https://numpy.org
