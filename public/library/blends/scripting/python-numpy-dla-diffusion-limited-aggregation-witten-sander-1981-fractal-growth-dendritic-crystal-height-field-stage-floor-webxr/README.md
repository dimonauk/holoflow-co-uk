# DLA — Diffusion-Limited Aggregation
## Witten & Sander 1981 · Fractal Growth · Height-Field Stage Floor · WebXR

**Blender 5.1 · Python bpy + NumPy · CC0 output**

---

### What this is

Diffusion-Limited Aggregation generates fractal dendrites that look like
snowflakes, coral, lightning channels, and mineral deposits. A single seed
particle sits at the centre of a 128 × 128 lattice. Random walkers are
released one at a time from a launch circle; each sticks to the first
cluster-neighbour it touches. After 2 000 walkers the cluster has a
Hausdorff dimension D_f ≈ 1.71 — the universal DLA exponent measured
computationally by Meakin (1983) and confirmed analytically by
Turkevich & Scher (1985).

### Files

| File | Purpose |
|---|---|
| `blueprint.py` | Full Blender 5.1 script — runs DLA, builds mesh, exports GLB |
| `record.py` | EEVEE NEXT viewport render — 10 s animation (`viewport.mp4`) |
| `SCREEN-RECORDING-NOTES.md` | OBS instructions for the manual screen recording |
| `.expected-artefacts.json` | Machine-readable artefact manifest and cross-references |

### Running the blueprint

1. Open Blender 5.1 with a new scene.
2. Open the **Scripting** workspace.
3. Open `blueprint.py`.
4. Press **Run Script** (or Alt+P in the text editor).
5. Output: `dla_cluster_floor.blend` + `dla_cluster_floor.glb` in the same folder.

Run time: 20 – 40 seconds on a modern CPU for 2 000 particles.

### Shape keys

| Key | Description |
|---|---|
| Basis | Full 2 000-particle cluster; cobalt seed, amber tips |
| SK_Small | First 400 particles — early growth, sparse dendrites |
| SK_Mid | First 1 200 particles — intermediate branching |
| SK_Inverse | Inverted height: core = peak, tips taper down; coral silhouette |

### Physics background

**Witten & Sander 1981**: launch a Brownian walker far from a growing cluster.
It diffuses until it touches the cluster, then sticks permanently. Because
the walker explores space diffusively, it reaches exposed tips long before
it reaches screened interior fjords. Fjords grow slower. Tips grow faster.
This *screened growth instability* produces the fractal.

The fractal dimension D_f ≈ 1.71 is universal across lattice type, launch
radius, and even continuous off-lattice simulations. The scaling law
N ~ r^{D_f} holds for cluster mass N versus radius r over several decades.

### Physical applications

- Electrodeposition (zinc crystallisation on electrode)
- Snowflake and ice dendrite formation
- Mineral dendrite growth (pyrolusite, magnetite)
- Dielectric breakdown patterns (lightning channels)
- Viscous fingering in porous media (Hele-Shaw cells)

### Sources

- Witten & Sander 1981: DOI 10.1103/PhysRevLett.47.1400 (Public Domain)
- Meakin 1983 (fractal dimension): DOI 10.1103/PhysRevA.27.1495 (Public Domain)
- NumPy: https://github.com/numpy/numpy (BSD-3-Clause)
