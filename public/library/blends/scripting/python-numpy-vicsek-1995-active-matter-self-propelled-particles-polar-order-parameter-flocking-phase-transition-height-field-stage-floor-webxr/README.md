# Vicsek Model (1995) — Active Matter Flocking Phase Transition

**Topic**: Active matter · Self-propelled particles · Flocking · Phase transition  
**Blender version**: 5.1  
**Licence**: CC0 (studio-authored; outside sources cited in tutorial)  
**Tags**: scripting, python, numpy, physics, active-matter, stat-mech, webxr

## What this is

6 144 self-propelled point particles move at constant speed in a periodic 2-D
box at density ρ = 6.0 (matching Vicsek et al. 1995).  Each particle aligns
its heading to the mean direction of neighbours within radius R = 1.0, then
adds bounded uniform noise η.  The resulting 128 × 128 stage-floor mesh
encodes the time-averaged **local polar order parameter** Φ_local as vertex
height and Cobalt–Amber colour, with four shape keys spanning the full
phase diagram.

## Shape keys

| Key | η | Description |
|---|---|---|
| Basis | 0.10 | Ordered flocking — Φ ≈ 0.88, near-uniform amber plateau |
| SK_Bands | 0.28 | Travelling density bands (Chaté–Grégoire 2008 regime) |
| SK_Crit | 0.36 | Near-critical — large fluctuations, patchy mosaic |
| SK_Dis | 0.70 | Disordered — Φ ≈ 0.03, flat cobalt floor |

## Files

| File | Purpose |
|---|---|
| `blueprint.py` | Run in Blender 5.1 Scripting workspace; outputs `.blend` + `.glb` |
| `record.py` | Viewport animation render (run headless after blueprint) |
| `SCREEN-RECORDING-NOTES.md` | OBS / Game Bar instructions for `screen.mp4` |
| `vicsek_floor.blend` | Generated .blend (run blueprint to produce) |
| `vicsek_floor.glb` | Draco-6 WebP GLB for WebXR (run blueprint to produce) |

## Running

```bash
blender --background --python blueprint.py
# then (after .blend exists):
blender --background vicsek_floor.blend --python record.py
```

## Key parameters

```python
N_PARTICLES = 6144   # ρ = N / L² = 6.0 (Vicsek 1995)
L           = 32.0   # box side
R           = 1.0    # interaction radius
V0          = 0.03   # speed per step
η_c         ≈ 0.35   # estimated critical noise at this density
```

## Cross-references

- Tutorial page: `/tutorials/blender-tutorial-python-numpy-vicsek-1995-active-matter-...`
- Related: Kuramoto oscillators, Frank–Oseen nematic LC, FitzHugh–Nagumo excitable media

## Outside sources

1. Vicsek T et al. (1995) Phys Rev Lett 75(6):1226 — original model  
   arXiv:cond-mat/9507131 · Public Domain > 30 yr
2. Chaté H, Ginelli F, Grégoire G, Raynaud F (2008) Phys Rev E 77:046113 — bands  
   arXiv:0712.2062 · Free academic access
