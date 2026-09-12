# KP-II Web Soliton — Exact Hirota τ-Function Height-Field Stage Floor

**Blender 5.1 · Python + NumPy · CC0 · WebXR stage floor**

---

## What this is

The **Kadomtsev–Petviashvili (KP-II)** equation is a 2+1-dimensional integrable
partial differential equation that governs weakly nonlinear, weakly dispersive,
nearly-unidirectional waves on a plane.  It is the canonical extension of the
Korteweg–de Vries equation (KdV) to two spatial dimensions:

```
∂/∂x [ u_t + 6u u_x + u_xxx ] + 3 u_yy = 0
```

The `+3 u_yy` term (KP-**II** sign) makes line solitons **transversely stable** —
they persist under small y-perturbations — and allows them to form resonant
Y-junctions (Mach stems) when two solitons collide at the critical angle.

Unlike KdV, which requires a numerical pseudospectral scheme, KP-II has **exact
analytic multi-soliton solutions** via Hirota's bilinear (τ-function) formalism.
This blueprint computes them directly in NumPy with zero truncation error.

---

## Files

| File | Purpose |
|------|---------|
| `blueprint.py` | Full Blender 5.1 Python script → mesh + .blend + .glb |
| `record.py` | Viewport animation render → `viewport.mp4` |
| `SCREEN-RECORDING-NOTES.md` | OBS instructions for `screen.mp4` |
| `.expected-artefacts.json` | CI artefact manifest |

---

## Shape keys

| Key | Physics | Parameters |
|-----|---------|------------|
| **Basis** | 2-soliton oblique crossing | k=(1.2, 1.0), ell=(0.8, −1.0), t=0 |
| **SK_YJunction** | Resonant Y-junction (Mach stem) | k=(1,1), ell=(1,−1) — satisfies ell²=k⁴ resonance |
| **SK_Web4** | 4-soliton web lattice (Gr(2,4)) | Two crossing resonant pairs |
| **SK_Temporal** | 2-soliton at t=8 (post-collision) | Same SOL_2 pair, crests separated |

---

## Key physics: the resonance condition

For two symmetric solitons with wavenumbers (k, ell) and (k, −ell), the Mach
stem resonance requires:

```
ω₁ + ω₂ = ω₃     (frequencies sum)
k₁ + k₂ = k₃     (wavenumbers sum)
l₁ + l₂ = l₃     (y-wavenumbers sum)
```

This constrains `ell = k²`.  With k=1, ell=1: the two ±45° solitons resonate
to produce a horizontal stem soliton of double amplitude (k₃=2).  The Hirota
interaction coefficient for this pair is A₁₂ = 12/16 = 3/4.

---

## Cross-references

- [KdV Pseudospectral Stage Floor](/tutorials/blender-tutorial-python-numpy-korteweg-de-vries-1895-soliton-collision-pseudospectral-rk4-space-time-height-field-stage-floor-webxr) — 1D parent equation
- [Complex Ginzburg–Landau Stage Floor](/tutorials/blender-tutorial-python-numpy-complex-ginzburg-landau-pde-spiral-turbulence-benjamin-feir-defect-height-field-stage-floor-webxr) — related 2D wave PDE
- [Cahn–Hilliard Spinodal Decomposition](/tutorials/blender-tutorial-python-numpy-cahn-hilliard-phase-field-spinodal-decomposition-ostwald-ripening-stage-floor-webxr) — FFT semi-implicit PDE technique

---

## Outside sources

1. **Kadomtsev BN & Petviashvili VI 1970** — "On the stability of solitary waves in
   weakly dispersive media" *Sov. Phys. JETP Lett.* 15:539.
   Public domain (>50 years). Original derivation of the equation.

2. **Hirota R 1971** — "Exact solution of the Korteweg-de Vries equation for multiple
   collisions of solitons" *Phys. Rev. Lett.* 27:1192.
   Public domain (>50 years). τ-function and bilinear formalism.

3. **Kodama Y & Williams LK 2011** — "KP solitons and total positivity for the Grassmannian"
   arXiv:1108.4984. *Inventiones Mathematicae* 198:637.
   Mathematical classification of web-soliton types via totally non-negative Grassmannian.
