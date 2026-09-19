# Hofstadter Butterfly — Bloch Electron in Rational Magnetic Flux

**Physics**: Douglas Hofstadter (1976). *Energy levels and wave functions of
Bloch electrons in rational and irrational magnetic fields.*
Physical Review B **14**(6):2239–2249. DOI 10.1103/PhysRevB.14.2239

**Blender version**: 5.1  
**Licence**: CC0 (code and generated assets)  
**Topic**: Condensed matter / quantum topology / scripting

---

## What this is

A 2D square lattice electron in a perpendicular magnetic field Φ obeys a
beautifully compact 1D equation — the Harper (1955) recurrence — when Φ is a
rational multiple of the flux quantum Φ₀. For Φ/Φ₀ = p/q, the q×q cyclic
Harper matrix has q eigenvalues, each one a point in the energy spectrum E(α).
Plotting E versus α over all rationals α = p/q with q ≤ Q_MAX produces the
Hofstadter butterfly: a fractal spectrum shaped like wings, with gaps indexed
by Chern numbers (TKNN 1982).

The height-field encodes a 2D density-of-states map: x = magnetic flux ratio
α ∈ [0, 1], y = energy E ∈ [−4.2, 4.2], height = log₁₀(1 + eigenvalue count).

## Shape keys

| Key | Q_MAX | α range | Shows |
|---|---|---|---|
| Basis | 100 | [0, 1] | Standard butterfly |
| SK_Coarse | 30 | [0, 1] | Main wings only |
| SK_Dense | 200 | [0, 1] | Fine sub-bands |
| SK_Central | 150 | [0.4, 0.6] | Zoomed self-similar core |

## Running

```bash
blender --background --python blueprint.py
# (from the directory containing this file)
```

Outputs: `hofstadter_butterfly_floor.blend`, `hofstadter_butterfly_floor.glb`

For the viewport recording:

```bash
blender hofstadter_butterfly_floor.blend --python record.py
```

## Cross references

- Studio tutorial: `/tutorials/blender-tutorial-python-numpy-hofstadter-butterfly-1976-bloch-electron-rational-flux-harper-equation-fractal-cantor-spectrum-stage-floor-webxr`
- Related: SSH Zak phase, Haldane Chern insulator, Kane-Mele Z₂ invariant, Anderson localisation, 2D tight-binding band

## Outside sources

- Hofstadter, D.R. (1976) *Phys. Rev. B* **14**(6):2239–2249. Public Domain (>50 yr).
- Thouless, D.J., Kohmoto, M., Nightingale, M.P. & den Nijs, M. (1982)
  "Quantised Hall conductance in a two-dimensional periodic potential."
  *Phys. Rev. Lett.* **49**(6):405–408. Public Domain (>40 yr).
- NumPy, BSD-3-Clause — <https://github.com/numpy/numpy>
- TopoCM (Delft) course content, CC0 — <https://github.com/topocm/topocm_content>
