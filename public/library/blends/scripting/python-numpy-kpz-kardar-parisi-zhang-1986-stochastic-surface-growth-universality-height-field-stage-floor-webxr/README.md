# KPZ (Kardar–Parisi–Zhang) Equation 1986
## Stochastic Surface Growth · Height-Field Stage Floor · Blender 5.1

**Equation:**  
`∂h/∂t = ν ∇²h + (λ/2)|∇h|² + σ η(x,y,t)`

**Universality class:** KPZ (distinct from Edwards–Wilkinson when λ ≠ 0)  
**Method:** Euler–Maruyama, 128×128 periodic grid  
**Source:** Kardar M, Parisi G, Zhang Y-C (1986) PRL 56:889  
**Licence:** CC0 (studio content) · PD equations

---

## What this builds

A 128×128 quad mesh (`KPZ_Floor.blend` / `kpz_floor.glb`) representing a
stochastically grown interface at four stages of the KPZ parameter space:

| Shape key | λ | σ | Steps | t | Character |
|-----------|---|---|-------|---|-----------|
| Basis     | 0 | 0.5 | 200 | 4 | EW limit — gentle correlated hills |
| SK_KPZ    | 2 | 0.5 | 200 | 4 | Nonlinear ridges, sharper crests   |
| SK_Strong | 2 | 2.0 | 200 | 4 | High-roughness noisy texture       |
| SK_Long   | 2 | 0.5 | 1000 | 20 | Well-developed KPZ morphology    |

All shape keys are σ-normalised before the ZSCALE multiplier, so every
state fills the same z-range — useful for direct visual comparison of
texture character rather than raw amplitude.

The `KPZ_Height` FLOAT_COLOR attribute runs cobalt (troughs) → amber (peaks).

---

## Running

1. Open Blender 5.1 → Scripting workspace → open `blueprint.py` → Run Script.  
   Produces `kpz_floor.blend` and `kpz_floor.glb` beside the script.

2. For the viewport recording, with `kpz_floor.blend` open, run `record.py`.  
   Produces `public/library/videos/scripting/<slug>/viewport.mp4`.

---

## Physics notes

**Why two universality classes?**  
The diffusion term ν∇²h is reversible — it does not prefer a growth direction.
The nonlinear term (λ/2)|∇h|² is an up–down symmetry breaker: it captures the
fact that a tilted surface grows faster in the direction of its tilt (think of
a ball rolling off a tilted plane depositing material). This irreversibility
places KPZ in a genuinely different universality class from EW.

**The Hopf–Cole transformation (1d exact solution)**  
Setting ψ = exp(λh/2ν), the 1d KPZ equation becomes the stochastic heat
equation: ∂ψ/∂t = ν ∂²ψ/∂x² + (λσ/2ν) ψ η. This linear SPDE is exactly
solvable, and the resulting Tracy–Widom distribution for the height
fluctuations has been confirmed experimentally in turbulent liquid crystals
(Takeuchi & Sano, PRL 2010).

**In 2+1 dimensions**  
The exact solution is not available, but extensive numerical and renormalisation
group work gives β_KPZ ≈ 0.24 and χ_KPZ ≈ 0.39. The KPZ fixed point in 2+1d
is under active rigorous investigation (Dauvergne–Ortmann–Virág 2022).

---

## Files

| File | Description |
|------|-------------|
| `blueprint.py` | Main Blender script — generates mesh + shape keys |
| `record.py` | Viewport animation renderer |
| `README.md` | This file |
| `SCREEN-RECORDING-NOTES.md` | OBS/Game Bar instructions for screen.mp4 |
| `.expected-artefacts.json` | CI manifest with cross-references |
| `kpz_floor.blend` | Generated Blender file |
| `kpz_floor.glb` | Draco-6 compressed GLB with morphs + vertex colours |

---

*Holoflow Studio · CC0 · Blender 5.1*
