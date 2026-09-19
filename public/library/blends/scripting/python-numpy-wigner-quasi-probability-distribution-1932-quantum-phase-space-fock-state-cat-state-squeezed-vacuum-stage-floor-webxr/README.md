# Wigner Quasi-Probability Distribution (1932) — Quantum Phase-Space Floor

**Topic**: Quantum Optics / Open Quantum Systems  
**Blender version**: 5.1  
**Licence**: CC0  
**Mesh**: 128×128 = 16 384 vertices, 16 129 quad faces  
**Colour attribute**: `WQP_Phase` (FLOAT_COLOR, POINT domain)

## What this is

Eugene Wigner introduced his quasi-probability distribution in 1932 as a way to
translate quantum mechanics into a phase-space language — a language borrowed from
classical statistical mechanics but fundamentally different from it.

The Wigner function W(q,p) assigns a real number to each point of phase space
(position q, momentum p). It satisfies both quantum marginals exactly:

```
∫ W(q,p) dp  = |ψ(q)|²      (position probability density)
∫ W(q,p) dq  = |φ(p)|²      (momentum probability density)
```

The catch — and the quantum secret — is that W can be **negative**. Classical
probability distributions are always ≥ 0. Wherever W < 0, there is no classical
interpretation; those regions are the fingerprints of quantum coherence.

R.L. Hudson (1974) proved the converse: W ≥ 0 everywhere *if and only if* ψ is a
Gaussian. Every other pure state has a negative region somewhere.

## The five quantum states

### Basis — Fock |0⟩ (harmonic oscillator ground state)
```
W_0(q,p) = (2/π) · exp(-2r²)
```
A simple Gaussian. Always positive. This is the "most quantum" state that never shows
negativity — it saturates the Heisenberg uncertainty relation as a minimum-uncertainty
state, just like coherent states.

### SK_Fock1 — Fock |1⟩ (first excited state)
```
W_1(q,p) = (1/π)(4r² - 1) · exp(-2r²)
```
Negative at the origin (r < 1/2), positive doughnut ring at r > 1/2. The amber pit
at the centre in the floor visualisation is a direct readout of W < 0.

### SK_Fock5 — Fock |5⟩ (fifth excited state)
```
W_5(q,p) = ((-1)^5/π) · L_5(4r²) · exp(-2r²)
```
Five concentric rings alternating between cobalt (+) and amber (−), separated by the
five zeros of the 5th Laguerre polynomial. The outermost ring is positive.

### SK_Cat — Schrödinger cat (|+α⟩ + |−α⟩) / N, α = 2
```
W_cat = N²[ W_{+α} + W_{-α} + (2/π) · exp(-2(r² + α²)) · 2·cos(4pα) ]
```
Two Gaussian peaks at q = ±2, p = 0 — the "classical" locations of the two coherent
components. Between them, a dense grid of oscillating fringes along p with spatial
frequency 4α/(2π) ≈ 1.27 per unit p. These fringes have *no classical analogue*;
they prove the superposition is quantum-coherent, not a classical mixture.

### SK_Squeezed — Squeezed vacuum, squeeze parameter r = 1.2
```
W_sq(q,p) = (2/π) · exp(-2e^{2r}·q² - 2e^{-2r}·p²)
```
An elliptical Gaussian: width in q reduced to e^{-1.2} ≈ 0.30 of vacuum, width in p
expanded to e^{1.2} ≈ 3.32. Still positive everywhere (Gaussian), but the anisotropy
means q-measurement uncertainty is squeezed below the vacuum level at the cost of
p-measurement uncertainty. Used in LIGO and quantum communication.

## Files

| File | Purpose |
|---|---|
| `blueprint.py` | Builds the Blender scene from NumPy — run in Scripting tab |
| `record.py` | Animates shape-key morphing and renders `viewport.mp4` |
| `SCREEN-RECORDING-NOTES.md` | OBS instructions for `screen.mp4` |
| `.expected-artefacts.json` | CI manifest for generated files |

## References

- Wigner EP (1932) "On the Quantum Correction For Thermodynamic Equilibrium"
  *Phys. Rev.* **40**:749–759. doi:10.1103/PhysRev.40.749
- Hudson RL (1974) "When is the Wigner quasi-probability density non-negative?"
  *Rep. Math. Phys.* **6**:249–252
- Schleich WP (2001) *Quantum Optics in Phase Space* Wiley-VCH ISBN 978-3-527-29435-0
- NumPy (BSD-3-Clause) · SciPy special.eval_genlaguerre (BSD-3-Clause)
