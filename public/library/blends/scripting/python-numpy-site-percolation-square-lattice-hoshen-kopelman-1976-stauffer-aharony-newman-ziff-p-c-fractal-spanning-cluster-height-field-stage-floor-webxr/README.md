# Site Percolation on Z² — Hoshen–Kopelman 1976  (Blender 5.1)

**Source**: Hoshen & Kopelman (1976) Phys. Rev. B 14, 3438 (union-find algorithm).
Critical exponents: Nienhuis (1982) PRL 49, 1062; Cardy (1987) exact CFT results.
Threshold: Stauffer & Aharony (1994) *Introduction to Percolation Theory*, 2nd ed.

---

## What this is

A 128 × 128 site-percolation simulation on the square lattice, rendered as a
height-field stage floor for WebXR.  Each vertex sits on one lattice site;
its height encodes `log(1 + cluster_size) / log(N²)`.

Four shape keys sweep the phase diagram:

| Shape Key   | p      | Physics                                           |
|-------------|--------|---------------------------------------------------|
| Basis       | 0.40   | Sub-critical — small, isolated clusters           |
| SK_Critical | 0.5927 | Critical — fractal spanning cluster, D_f = 91/48 |
| SK_Above    | 0.70   | Super-critical — giant component dominates        |
| SK_Bond     | 0.50   | Bond percolation at threshold (exact, self-dual)  |

Colour attribute `Perc_Cluster`: cobalt (empty / small) → amber (giant component).

---

## Critical exponents (exact, conformal field theory)

| Exponent | Value    | Meaning                                         |
|----------|----------|-------------------------------------------------|
| τ        | 187/91   | Cluster-size distribution P(s) ~ s^{-τ}         |
| ν        | 4/3      | Correlation length ξ ~ |p − p_c|^{−ν}           |
| β        | 5/36     | P_∞ ~ (p − p_c)^β  for p > p_c                 |
| γ        | 43/18    | Mean cluster size S ~ |p − p_c|^{−γ}            |
| D_f      | 91/48    | Fractal dimension of spanning cluster at p_c     |

Bond percolation on Z² has p_c = 1/2 exactly (self-duality of the square lattice).
Site percolation on Z² has p_c ≈ 0.59274621(13) (Newman & Ziff 2001).

---

## Files

| File                        | Purpose                                     |
|-----------------------------|---------------------------------------------|
| `blueprint.py`              | Main Blender script — run once to build .blend + .glb |
| `record.py`                 | Keyframe animation bake + viewport render   |
| `SCREEN-RECORDING-NOTES.md` | OBS / Game Bar capture instructions         |
| `.expected-artefacts.json`  | CI artefact manifest                        |

---

## Usage

```bash
# From the Blender scripting workspace:
# 1. Open blueprint.py and run it → creates the mesh, shape keys, and exports GLB
# 2. Open record.py and run it → bakes animation, renders viewport.mp4
# 3. Follow SCREEN-RECORDING-NOTES.md to capture screen.mp4
```

---

## Licence

All code in this directory is released under **CC0 1.0 Universal** (Public Domain Dedication).
Outside sources credited: Hoshen & Kopelman 1976 (Phys Rev B, APS); Stauffer & Aharony 1994 (Taylor & Francis); Newman & Ziff 2001 (arXiv:cond-mat/0101295).
