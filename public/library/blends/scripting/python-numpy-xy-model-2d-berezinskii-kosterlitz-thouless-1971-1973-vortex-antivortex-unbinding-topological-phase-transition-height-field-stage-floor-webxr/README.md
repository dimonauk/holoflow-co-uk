# 2D XY Model — Berezinskii-Kosterlitz-Thouless Transition

**Blender 5.1 · Python / NumPy · Scripting topic**  
**Licence: CC0**

---

## What this is

A 128 × 128 stage-floor mesh whose height and colour encode `cos(θ(x,y))`
— the cosine of the spin angle in a 2D classical XY ferromagnet.  Four
shape keys capture the model at four temperatures straddling the famous
Berezinskii-Kosterlitz-Thouless (BKT) transition at
T_BKT ≈ 0.8935 J/k_B.

The BKT transition was awarded the 2016 Nobel Prize in Physics
(Kosterlitz and Thouless; Haldane received it jointly for separate work).

---

## Files

| File | Purpose |
|---|---|
| `blueprint.py` | Run in Blender Scripting workspace to build the mesh |
| `record.py` | Run after blueprint.py to render `viewport.mp4` |
| `SCREEN-RECORDING-NOTES.md` | OBS / Game Bar instructions for `screen.mp4` |
| `xy_bkt_floor.blend` | Generated Blender file (produced by blueprint.py) |
| `xy_bkt_floor.glb` | Generated GLB for WebXR (Draco-6, WebP textures) |

---

## Physics in 90 seconds

The **2D XY model** places a unit-vector spin (cos θ, sin θ) on each
site of a square lattice:

```
H = −J Σ_{⟨ij⟩} cos(θᵢ − θⱼ)    θᵢ ∈ [0, 2π)
```

The Mermin-Wagner theorem (1966) proves that the continuous U(1) symmetry
**cannot be spontaneously broken** at any T > 0 in two dimensions — there
is no conventional ordered phase.

Yet the 2D XY universality class (superfluid helium films, Josephson
junction arrays, planar magnets) exhibits a sharp phase transition.  The
resolution is **topological**: the relevant excitations are *vortices*,
configurations in which θ winds by ±2π around a plaquette.

| Phase | T | G(r) | Free vortices |
|---|---|---|---|
| Quasi-LRO | T < T_BKT | ~ r^{−η(T)}, η ↗ ¼ | None (bound pairs) |
| BKT critical | T = T_BKT | ~ r^{−1/4} | Pairs just unbinding |
| Disordered | T > T_BKT | ~ exp(−r/ξ) | Free, proliferating |

The essential singularity in ξ ~ exp(b/√(T−T_BKT)) means *all* Landau
derivatives of the free energy are continuous at T_BKT — the transition
is of infinite order.

The **Nelson-Kosterlitz universal jump** (1977): just below T_BKT the
helicity modulus ρs (superfluid stiffness) satisfies ρs(T_BKT⁻)/T_BKT = 2/π,
a discontinuous jump with a universal value experimentally confirmed in
⁴He films by Bishop and Reppy (1978).

---

## Shape keys

| Key | T / T_BKT | T (J/k_B) | Physics |
|---|---|---|---|
| `Basis` | 0.40 | ≈ 0.357 | Quasi-LRO, spin waves, bound vortex pairs |
| `SK_BKT` | 1.00 | ≈ 0.893 | Critical, power-law correlations η = ¼ |
| `SK_Unbound` | 1.20 | ≈ 1.072 | Above BKT, free vortices proliferating |
| `SK_HighT` | 2.50 | ≈ 2.234 | Disordered, short-range order only |

---

## How to run

1. Open Blender 5.1 → Scripting workspace.
2. Open `blueprint.py`, click **Run Script**.
3. Switch to 3D Viewport; the floor object `xy_bkt_floor` appears.
4. Export GLB: File → Export → glTF 2.0 with settings in blueprint.py.
5. (Optional) Open `record.py` and **Run Script** to render the animation.

---

## Outside sources

- Berezinskii VL 1971 *JETP* 32:493-500 — original BKT paper (PD > 50 yr)
- Kosterlitz JM, Thouless DJ 1973 *J Phys C* 6:1181-1203 — topological phase transition (PD > 50 yr)
- Nelson DR, Kosterlitz JM 1977 *PRL* 39:1201 — universal superfluid stiffness jump (PD > 40 yr)
- Hasenbusch M 2005 *PRB* 71:184420 — T_BKT = 0.8935 Monte Carlo (CC0 equations)
- NumPy — BSD-3-Clause — https://numpy.org
