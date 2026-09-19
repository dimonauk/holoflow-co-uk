# Hofstadter Butterfly — 1976 Fractal Energy Spectrum

**Blender 5.1 · Python + NumPy · CC0**

A 128 × 128 height-field stage floor whose landscape *is* the Hofstadter butterfly:
the fractal energy spectrum of 2D Bloch electrons in a uniform transverse magnetic field,
first computed by Douglas Hofstadter (1976, *Phys. Rev. B* 14:2239).

---

## Physics

The tight-binding Hamiltonian on a square lattice with transverse flux α
(in units of h/e per plaquette) admits, for rational α = p/q, exactly q Bloch
bands. Their positions in energy trace out a self-similar fractal when α sweeps
[0, 1]: the Hofstadter butterfly. Every gap in the butterfly carries an integer
TKNN Chern number (Thouless–Kohmoto–Nightingale–den Nijs 1982) equal to the
quantised Hall conductance σ_xy = C × e²/h.

The fractal is exact: the sub-butterfly centred at (α = 1/3, E = 0) is a perfect
Hofstadter butterfly at 1/9 the scale.

**Harper equation:** ψ_{n+1} + ψ_{n-1} + 2 cos(2π α n + k_y) ψ_n = E ψ_n

**Bandwidth:** E ∈ [−4, 4] for nearest-neighbour hopping t = 1.

---

## Files

| File | Purpose |
|------|---------|
| `blueprint.py` | Builds the Blender scene; exports `hofstadter_floor.glb` |
| `record.py` | Viewport animation render (run after blueprint.py) |
| `SCREEN-RECORDING-NOTES.md` | OBS/Game Bar instructions for `screen.mp4` |
| `.expected-artefacts.json` | CI manifest |

---

## Shape keys

| Key | Description |
|-----|-------------|
| **Basis** | Full butterfly α ∈ [0, 1], E ∈ [−4, 4] |
| **SK_Half** | Left half α ∈ [0, 0.5] zoomed — every sub-butterfly visible |
| **SK_Zoom** | α ∈ [0.25, 0.50] — the 1/3-sub-butterfly at full resolution |
| **SK_NNN** | Next-nearest-neighbour t₂ = 0.3 — particle-hole symmetry broken |

---

## Outside sources

- Hofstadter DR 1976 *Phys. Rev. B* 14:2239–2249 — original butterfly paper; PD > 40 yr.
- Thouless DJ, Kohmoto M, Nightingale MP, den Nijs M 1982 *PRL* 49:405 — TKNN integers / QHE; PD > 40 yr.
- NumPy — BSD-3-Clause — https://numpy.org

---

## Licence

CC0 — all original code.  Hofstadter (1976) and TKNN (1982) equations are public domain.
