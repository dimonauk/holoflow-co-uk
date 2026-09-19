# NLSE — Nonlinear Schrödinger Equation: Solitons, Breathers, Rogue Waves

**Blender 5.1 · Python / numpy · Stage Floor · WebXR**

Focusing NLSE: `i∂ψ/∂t + ∂²ψ/∂x² + 2|ψ|²ψ = 0`

An integrable PDE (Zakharov & Shabat 1972) whose solutions span from perfectly
elastic soliton collisions to modulational instability breathers and the
Peregrine rogue wave — a doubly-localised spike three times the background
amplitude that appears from nowhere and disappears without a trace.

## Files

| File | Purpose |
|------|---------|
| `blueprint.py` | Blender 5.1 script: Strang split-step SSF integrator + exact Peregrine formula → 128×128 height-field mesh with 4 shape keys → GLB export |
| `record.py` | Viewport animation: shape-key morph → renders `viewport.mp4` |
| `SCREEN-RECORDING-NOTES.md` | OBS / Game Bar instructions for `screen.mp4` |
| `.expected-artefacts.json` | Artefact manifest and cross-references |

## Shape Keys

| Key | Initial condition | Physics |
|-----|------------------|---------|
| `Basis` | Two η=1 solitons, v=±0.5, at x=∓3 | Elastic collision, phase shift, integrability |
| `SK_Akhmediev` | Plane wave + 4% cosine perturbation | MI growth → Akhmediev breather → FPUT recurrence |
| `SK_KM` | Plane wave + 70% sech bump | KM-type localised breathing, periodic in t |
| `SK_Peregrine` | Exact formula on independent grid | Rogue wave prototype: peak amplitude = 3× background |

## Integration

- **Method**: Strang split-step Fourier (2nd-order, spectrally accurate in space)
- **Linear step**: `ψ̂ *= exp(−ik²dt)` (exact)
- **Nonlinear step**: `ψ *= exp(2i|ψ|²dt)` (exact, |ψ| conserved)
- **Grid**: N=128, L=12, DT=0.10, NT=127 → t ∈ [0, 12.7]
- **Peregrine**: exact rational formula, independent 128×128 grid, x∈[−5,5], t∈[−4,4]

## Licence

CC0 — blueprint and record scripts are original works.
Sources credited and linked in `.expected-artefacts.json` and the tutorial page.
