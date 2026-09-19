# Drossel–Schwabl Forest Fire Model (1992)
### Self-Organised Criticality — Fire Cluster Power Law — 128 × 128 Stage Floor — WebXR

**Source paper**: Drossel B, Schwabl F (1992) "Self-Organized Critical Forest-Fire Model."  
*Physical Review Letters* 69(11):1629–1632. DOI [10.1103/PhysRevLett.69.1629](https://doi.org/10.1103/PhysRevLett.69.1629) — Public Domain (>30 yr)

---

## What this is

A three-state stochastic cellular automaton on a 128 × 128 square lattice.  
Sites are EMPTY (ash), TREE (living), or BURNING (fire; persists one step only).

The synchronous update rule:
```
1. BURNING  → EMPTY
2. TREE + BURNING neighbour  → BURNING
3. TREE + no BURNING neighbour → BURNING with prob f  (lightning)
4. EMPTY → TREE with prob p
```

When `p ≪ 1`, `f ≪ 1`, and `p/f ≫ 1` the system self-organises to a critical
state where fire-cluster sizes follow a power law **P(S) ∼ S^{−1.5}** across
decades — without tuning any coupling constant.

---

## Files

| File | Purpose |
|---|---|
| `blueprint.py` | Full bpy simulation + mesh + shape keys + GLB export |
| `record.py` | Viewport animation render → `viewport.mp4` |
| `SCREEN-RECORDING-NOTES.md` | OBS procedure for `screen.mp4` |
| `drossel_schwabl_forest_floor.blend` | *Generated* — run blueprint.py |
| `drossel_schwabl_forest_floor.glb` | *Generated* — Draco-6, WebP, +Y-up |

---

## Shape keys

| Key | Parameters | Forest character |
|---|---|---|
| **Basis** | p=0.010, f=5×10⁻⁵, 3 000 steps | SOC steady state; mixed ash / forest / active fire |
| **SK_LowP** | p=0.003, f=5×10⁻⁵, 2 000 steps | Sparse savanna; fire clusters below percolation threshold |
| **SK_HighP** | p=0.050, f=5×10⁻⁵, 4 000 steps | Dense forest; infrequent but large system-spanning fires |
| **SK_AllTrees** | All TREE | Theoretical saturation before first lightning strike |

---

## Mesh

- **Vertices**: 128 × 128 = 16 384
- **Quad faces**: 127 × 127 = 16 129
- **Colour attribute**: `FF_State` (FLOAT_COLOR, POINT domain)
  - 0.0 → cobalt (EMPTY / ash)
  - 0.5 → green (TREE / living forest)
  - 1.0 → amber (BURNING / active fire)
- **Vertex Z**: `state * Z_SCALE / 2` — ash flat, trees mid-height, fire peaks
- **Export**: Draco compression level 6, WebP textures, +Y up, morph targets on

---

## How it differs from the BTW Sandpile

Both are SOC models with no tuning, but:
- **BTW**: Integer heights + toppling rule + conservation → τ ≈ 1.11, D_f ≈ 2.75
- **DS forest fire**: Three states + stochastic regrowth/ignition → τ ≈ 1.5

The DS mechanism is *dissipative*: grains (trees) are created and destroyed,
not conserved. This makes it closer to ecological and epidemiological spreading
processes than to the sandpile's chip-firing.

---

## Run order

```bash
# 1. Generate the blend and GLB
blender --background --python blueprint.py

# 2. Render the viewport animation
blender drossel_schwabl_forest_floor.blend --python record.py

# 3. Record screen.mp4 manually — see SCREEN-RECORDING-NOTES.md
```
