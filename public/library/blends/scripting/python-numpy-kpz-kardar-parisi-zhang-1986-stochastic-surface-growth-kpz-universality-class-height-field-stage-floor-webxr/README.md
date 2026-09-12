# KPZ Equation — Stochastic Surface Growth

**Blender 5.1 · Python · NumPy · bpy data API**  
**Topic:** KPZ universality class, semi-implicit pseudo-spectral integration, Euler–Maruyama noise  
**Output:** `kpz_growth_floor.blend` + `kpz_growth_floor.glb` (128×128 height-field stage floor)

---

## What this is

The Kardar–Parisi–Zhang (KPZ) equation (1986) is three terms:

```
∂h/∂t = ν∇²h   +   (λ/2)|∇h|²   +   η(x,t)
          ↑               ↑              ↑
     surface tension   tilt/slope    white noise
     (smooths)         (KPZ term)    (roughens)
```

Remove the middle term (λ = 0) and you have the 1982 Edwards–Wilkinson
equation — a stochastic heat equation with Gaussian fluctuations.
Add it back and the universality class shifts: in 1D the interface
height fluctuations obey the Tracy–Widom GUE distribution (also appearing
in random matrix theory, TASEP particle flows, and the longest increasing
subsequence of a random permutation). In 2D the exponents are α ≈ 0.38,
β ≈ 0.24, z ≈ 1.58.

---

## Shape keys

| Key | Parameters | t | What you see |
|---|---|---|---|
| Basis | λ = 1.0, ν = 0.5, D = 0.3 | 3.0 | Early roughening — fine-scale noise structure |
| SK_Long | λ = 1.0, ν = 0.5, D = 0.3 | 12.0 | Developed KPZ surface — coarser, asymmetric |
| SK_EW | λ = 0.0, ν = 0.5, D = 0.3 | 12.0 | Edwards–Wilkinson — smoother, symmetric |
| SK_Strong | λ = 2.0, ν = 0.5, D = 0.3 | 12.0 | Strong KPZ coupling — pronounced ridges |

The same random seed (137) is used for all four runs. Differences are
physics, not random chance. Comparing SK_Long with SK_EW is the most
instructive pair: identical noise and t, but λ changed from 0 to 1.

---

## Method

- **Pseudo-spectral gradients:** `∂h/∂x = irfft2(i·kx·rfft2(h))`. No
  finite-difference artefacts. Physical-unit wavenumbers (rad/m) so ν has
  the correct dimensional role.
- **Semi-implicit linear part:** the stiff ν∇²h term is treated as
  `ĥ_new = (ĥ_old + dt·RHS) / (1 + ν|k|²·dt)`. Unconditionally stable
  for any `dt`.
- **Euler–Maruyama noise:** σ = sqrt(2D / (dx²·dt)) per grid point per step.
  The dx² factor reflects the physical noise density — omitting it would
  underestimate roughening on coarse grids.
- **Mean removal:** ⟨h⟩ → 0 every step. The (λ/2)|∇h|² term has a non-zero
  spatial average on a rough surface; without subtraction the mean height
  drifts monotonically upward.

---

## Mesh statistics

| Property | Value |
|---|---|
| Grid | 128 × 128 |
| Vertices | 16 384 |
| Quads | 16 129 |
| Shape keys | 4 |
| Vertex attribute | KPZ_Height (FLOAT_COLOR) |
| Export | Draco 6, WebP, +Y up |

---

## Files

- `blueprint.py` — simulation + mesh construction (run in Blender Text Editor)
- `record.py` — viewport animation for `viewport.mp4`
- `SCREEN-RECORDING-NOTES.md` — OBS setup and narration guide
- `.expected-artefacts.json` — artefact manifest with cross-references

---

## Outside sources

**Primary equation:**  
Kardar M, Parisi G, Zhang Y-C (1986) "Dynamic scaling of growing interfaces"  
*Physical Review Letters* 56: 889–892. doi:10.1103/PhysRevLett.56.889  
Mathematical content — public domain

**Edwards–Wilkinson baseline:**  
Edwards SF, Wilkinson DR (1982) "The surface statistics of a granular aggregate"  
*Proceedings of the Royal Society A* 381: 17–31. doi:10.1098/rspa.1982.0056  
Mathematical content — public domain

**NumPy (array computations):**  
Harris CR et al. (2020) *Nature* 585: 357–362. BSD-3-Clause.  
https://numpy.org · github.com/numpy/numpy
