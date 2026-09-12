# GPE BEC Vortex Lattice — Rotating BEC Abrikosov Lattice via Imaginary-Time Propagation

**Slug**: `python-numpy-gross-pitaevskii-bec-rotating-vortex-lattice-abrikosov-imaginary-time-stage-floor-webxr`  
**Blender**: 5.1 · **Licence**: CC0 · **Grid**: 128×128 = 16 384 verts, 16 129 quads

## What this makes

A 128×128 height-field stage floor where the vertex height and colour encode the
superfluid density |ψ|² of a rotating Bose-Einstein condensate. The four shape
keys step through four angular-momentum sectors: smooth ground state (Ω=0),
single central vortex, seven-vortex hexagonal Abrikosov lattice, and nineteen-vortex
two-shell lattice. Vortex cores appear as deep cobalt wells; the surrounding
Thomas-Fermi condensate plateau glows amber.

## Physics

The Gross-Pitaevskii equation in dimensionless trap units (ℏ = m = ω = 1,
length in oscillator units ℓ = √(ℏ/mω)):

```
i ∂ψ/∂t = [−½∇² + ½r² + G|ψ|² − ΩLz] ψ
```

- `−½∇²` : kinetic energy  
- `½r²`  : harmonic trap  
- `G|ψ|²` : mean-field interaction (G = 500 ≫ 1 → Thomas-Fermi regime)  
- `ΩLz`  : rotation, Lz = −i(x∂_y − y∂_x)

**Thomas-Fermi radius**: R_TF = (2μ_TF)^½ where μ_TF = √(G/π) ≈ 12.6 → R_TF ≈ 5.0.

**Vortex count** scales linearly with rotation rate: N_v ≈ Ω × R_TF² in our units.
Seven vortices correspond to Ω ≈ 0.28, nineteen to Ω ≈ 0.76.

## Numerical method: imaginary-time split-operator

Replace t → −iτ (imaginary time). The GPE becomes a steepest-descent equation:

```
∂ψ/∂τ = [½∇² − ½r² − G|ψ|² + μ] ψ
```

The field is renormalised to ∫|ψ|² = 1 after each step; the chemical potential
μ is tracked implicitly. Strang splitting (2nd-order) separates kinetic (K) and
potential (V) operators:

```
ψ(τ+dτ) ∝  exp(−V·dτ/2) · IFFT[exp(−K·dτ)·FFT] · exp(−V·dτ/2) · ψ(τ)
```

with `exp(−K·dτ) = exp(−½k²·dτ)` precomputed. The result converges to the
lowest-energy state in the topological sector defined by the initial vortex seeds.

## Shape keys

| Name       | Vortices | Ω (effective) | Description                          |
|------------|----------|---------------|--------------------------------------|
| Basis      | 0        | 0             | Smooth Thomas-Fermi plateau          |
| SK_Single  | 1        | ≈ 0.04        | Single vortex at trap centre         |
| SK_Hex7    | 7        | ≈ 0.28        | Hexagonal Abrikosov lattice (1+6)    |
| SK_Hex19   | 19       | ≈ 0.76        | Two-shell lattice (1+6+12)           |

## Files

| File                        | Purpose                              |
|-----------------------------|--------------------------------------|
| `blueprint.py`              | Full bpy + NumPy build script        |
| `record.py`                 | Viewport animation recorder          |
| `SCREEN-RECORDING-NOTES.md` | OBS screen-recording instructions    |
| `.expected-artefacts.json`  | Build manifest + cross-references    |
| `gpe_bec_vortex.blend`      | *(created by blueprint.py)*          |
| `gpe_bec_vortex.glb`        | *(created by blueprint.py)*          |

## Run

Open Blender 5.1 → Scripting workspace → load `blueprint.py` → Run Script.
Estimated time: 10–15 s on a modern CPU (4 × 3000 imaginary-time steps).

## Outside sources

- **Gross 1961** — *Structure of a quantised vortex in boson systems*, Il Nuovo Cimento 20:454.  
  DOI: [10.1007/BF02731494](https://doi.org/10.1007/BF02731494) — PD (>65 yr)
- **Pitaevskii 1961** — *Vortex lines in an imperfect Bose gas*, JETP 13:451.  
  PD (>65 yr)
- **Dalfovo et al. 1999** — *Theory of Bose-Einstein condensation in trapped gases*,  
  Rev Mod Phys 71:463 — arXiv [cond-mat/9806038](https://arxiv.org/abs/cond-mat/9806038)  
  (open access, CC BY-compatible)
- **NumPy** — BSD-3-Clause — [numpy.org](https://numpy.org)
