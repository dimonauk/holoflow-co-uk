# Kane-Mele 2005 — Quantum Spin Hall / Z₂ Topological Insulator
## Spin-Hall Berry Curvature Height-Field Stage Floor (Blender 5.1, WebXR)

**Topic**: Condensed-matter topology — Z₂ topological insulator / Quantum Spin Hall effect  
**Series**: SSH (Z invariant, 1D) → Haldane (Chern number, 2D broken TRS) → **Kane-Mele (Z₂ invariant, 2D preserved TRS)**  
**Licence**: CC0 (blueprint + all outputs)  
**Blender**: 5.1 · Python scripting only · bpy + numpy

---

## What this builds

A 128 × 128 grid height-field mesh whose z-coordinate at each reciprocal-space
point (kx, ky) encodes the **spin Berry curvature density** Ω_s(k) = 2 Ω_↑(k)
of the Kane-Mele model. Four shape keys sweep the model through its phase diagram.

| Shape key | λ_SO | M | Phase | Visual |
|---|---|---|---|---|
| Basis | 0.20 | 0 | ν = 1 QSH | Two equal amber peaks at K and K′ |
| SK_StrongSOC | 0.40 | 0 | ν = 1 (stronger) | Sharper, taller peaks |
| SK_NearCrit | 0.20 | 0.95 Mc | ν = 1 → 0 | K′ peak shrinks |
| SK_Trivial | 0.20 | 1.50 Mc | ν = 0 trivial | Flat cobalt landscape |

Colour attribute **KM_SpinBC** (FLOAT_COLOR, per-vertex): cobalt at zero/negative
curvature, amber at positive. Both K and K′ amber in the topological phase — the
visual signature that topology is here preserved by time-reversal, not broken by it.

---

## Physics in two paragraphs

Kane and Mele (2005) noticed that graphene's spin-orbit coupling, however small,
turns both Dirac points into a Haldane insulator — spin-up electrons see a Haldane
model with flux phase φ = +π/2 (Chern number C_↑ = +1) and spin-down electrons see
the time-reversed partner with φ = −π/2 (C_↓ = −1). The total charge Chern number
is zero — no ordinary Hall conductance — but the **spin Chern number** C_s = C_↑ − C_↓ = 2
yields a quantised spin Hall conductance σ_xy^s = e/4π. The topological invariant
protecting it is Z₂ (ν = C_s/2 mod 2 ∈ {0,1}), robust against any perturbation that
preserves time-reversal.

The critical difference from Haldane: the amber peaks at K and K′ are **equal** (TRS
forces Ω_s(K) = Ω_s(K′)) whereas in the Haldane model with M ≠ 0 the two peaks
differ. When the on-site mass M exceeds the critical value M_c = 3√3 λ_SO, the gap
closes first at one valley, flipping its contribution, and the floor goes flat — the
trivial phase. Adding Rashba coupling λ_R mixes spin ↑ and ↓ (breaking Sz conservation)
but the Z₂ invariant survives until λ_R > λ_R^c ≈ 2λ_SO when the full gap closes.

---

## Files

| File | Purpose |
|---|---|
| `blueprint.py` | Run in Blender 5.1 → produces mesh, shape keys, .blend, .glb |
| `record.py` | Camera orbit + shape-key animation → viewport.mp4 |
| `SCREEN-RECORDING-NOTES.md` | OBS instructions for screen.mp4 |
| `.expected-artefacts.json` | CI manifest |

---

## Outside sources

1. **Kane CL, Mele EJ (2005)** — *Z₂ Topological Order and the Quantum Spin Hall Effect*,
   PRL 95:226801. doi:10.1103/PhysRevLett.95.226801. Original prediction.
   Public domain (mathematical content >20 years). Related org: APS Physics.

2. **Asbóth JK, Oroszlány L, Pályi A (2016)** — *A Short Course on Topological Insulators*,
   Lecture Notes in Physics 919. arXiv:1509.02295. Licence: CC-BY 4.0.
   Related: https://github.com/topocm/topocm_content (CC0).

3. **NumPy** — Harris et al. 2020 Nature 585:357–362. BSD-3-Clause.
   https://github.com/numpy/numpy.
