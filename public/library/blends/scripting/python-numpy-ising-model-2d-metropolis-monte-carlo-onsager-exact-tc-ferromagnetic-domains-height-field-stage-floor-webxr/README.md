# 2D Ising Model — Metropolis Monte Carlo

**Topic:** Statistical mechanics · Phase transitions  
**Blender version:** 5.1  
**Licence:** CC0  
**Grid:** 128 × 128 = 16 384 spins · 16 129 quad faces  
**Tc (Onsager exact):** 2J / ln(1 + √2) ≈ 2.2692 J/k_B

---

## What this is

The 2D ferromagnetic Ising model places binary spins s_i ∈ {−1, +1} on a
square lattice:

```
H = −J Σ_{⟨ij⟩} s_i s_j
```

Lars Onsager solved it exactly in 1944 — one of the few exactly-solved models
in statistical mechanics — giving a critical temperature

```
Tc = 2J / ln(1 + √2)  ≈  2.2692 J/k_B
```

and a set of critical exponents (β = 1/8, γ = 7/4, ν = 1) that define the
**2D Ising universality class**, shared by every Z₂ order parameter model in
two dimensions.

---

## Files

| File | Purpose |
|---|---|
| `blueprint.py` | Full Blender script — runs MC, builds mesh, assigns colours, shape keys |
| `record.py` | Viewport animation script for `viewport.mp4` |
| `SCREEN-RECORDING-NOTES.md` | OBS instructions for `screen.mp4` |
| `.expected-artefacts.json` | Artefact manifest |

---

## Shape keys

| Key | Temperature | Physics |
|---|---|---|
| Basis | 0.50 Tc | Deep ferromagnet — large ordered domains |
| SK_Critical | 1.00 Tc | Onsager critical point — fractal percolation cluster |
| SK_Hot | 1.50 Tc | Paramagnet — disordered salt-and-pepper |
| SK_Quench | 0.25 Tc | Quench from T→∞ — coarsening domain walls visible |

---

## Algorithm

**Checkerboard Metropolis** (vectorised with NumPy):

1. Divide lattice into black/white sublattices (chess-board colouring).
2. For all sites of one colour simultaneously:
   - ΔE = 2J s_i Σ_nn s_j
   - Accept flip with probability min(1, exp(−ΔE / k_BT))
3. Alternate sublattice each half-sweep.

Sites of the same colour share no nearest neighbours, so all their acceptance
decisions are independent → fully vectorisable.  Full detailed balance is
maintained (identical equilibrium distribution to sequential Metropolis).

---

## Colour encoding

```
Cobalt (0.027, 0.159, 0.557) ← s = −1 (down-spin, at floor)
Amber  (0.980, 0.620, 0.050) ← s = +1 (up-spin, raised Z_SCALE)
```

Height: z = ((s + 1) / 2) × 0.35 m

---

## Running

Open Blender 5.1 → Scripting workspace → Open `blueprint.py` → Run.
Expect ~20–60 s depending on hardware.

Then run `record.py` for the viewport animation.

---

## External sources

- **Ising E (1925)** Beitrag zur Theorie des Ferro- und Paramagnetismus.
  Z. Physik 31:253–258. PD (>100 yr). Original 1D model.

- **Onsager L (1944)** Crystal statistics I. A two-dimensional model with an
  order-disorder transition. Phys. Rev. 65:117–149.
  doi:10.1103/PhysRev.65.117. PD (>80 yr). Exact 2D solution.

- **NumPy** BSD-3-Clause. https://numpy.org (Harris et al. 2020,
  Nature 585:357–362).
