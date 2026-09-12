import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-gross-pitaevskii-bec-rotating-vortex-lattice-abrikosov-imaginary-time-stage-floor-webxr";

const TITLE =
  "Python numpy — Gross-Pitaevskii Equation: Rotating BEC Abrikosov Vortex Lattice, Imaginary-Time Split-Operator, Height-Field Stage Floor for WebXR (Blender 5.1)";

const LEDE =
  "Cool a cloud of bosons to a billionth of a degree above absolute zero, spin the magnetic trap, and the superfluid spontaneously threads itself with a triangular lattice of quantised vortices — each a pinhole of zero density around which the phase winds by exactly 2π. This blueprint finds that Abrikosov ground state using imaginary-time Strang splitting of the Gross-Pitaevskii equation, plants four topological sectors as shape keys, and maps the superfluid density to a cobalt-and-amber stage-floor mesh for WebXR.";

function Body() {
  return (
    <>
      <p>
        The{" "}
        <a className={lk} href="https://doi.org/10.1007/BF02731494" target="_blank" rel="noreferrer">
          Gross-Pitaevskii equation
        </a>
        {" "}(Gross 1961, Pitaevskii 1961) is the mean-field theory of a
        zero-temperature Bose-Einstein condensate. It describes the macroscopic
        wavefunction ψ whose squared modulus is the superfluid density: the atoms
        all occupy the same quantum state and behave collectively as a single
        coherent object. When Cornell, Wieman, and Ketterle achieved BEC in 1995 —
        earning the{" "}
        <a className={lk} href="https://www.nobelprize.org/prizes/physics/2001/summary/" target="_blank" rel="noreferrer">
          2001 Nobel Prize in Physics
        </a>
        {" "}— the GPE immediately became the workhorse for predicting vortex
        dynamics, sound modes, and interference patterns in those experiments.
      </p>

      <p>
        In a rotating trap, the condensate hosts quantised vortices: topological
        defects where |ψ|=0 and the superfluid phase winds by 2π. The vortices
        repel one another via a logarithmic potential, and the energy minimum is
        the triangular Abrikosov lattice — the same geometry that flux lines adopt
        in type-II superconductors. This blueprint finds that lattice without
        simulating the real-time rotation; instead it plants phase singularities at
        desired positions and uses imaginary time to relax the wavefunction to the
        ground state within that topological sector.
      </p>

      <h2>Equation</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Gross-Pitaevskii (dimensionless, oscillator units  ℏ=m=ω=1):

  i ∂ψ/∂t = [−½∇² + ½r² + G|ψ|²] ψ

  −½∇²   kinetic energy (Laplacian)
  ½r²    harmonic trap potential (isotropic, 2D cross-section)
  G|ψ|²  mean-field repulsion  (G = 4πaN ≫ 1 → Thomas-Fermi regime)

Thomas-Fermi ground state (G→∞):
  |ψ_TF|² = max(0, μ_TF − ½r²) / G
  μ_TF   = √(G/π) ≈ 12.6   (from ∫|ψ|² d²r = 1)
  R_TF   = (2μ_TF)^½ ≈ 5.0  (condensate radius in oscillator units)`}
      </pre>

      <h2>Imaginary-time projection</h2>
      <p>
        Replace real time t by imaginary time τ = it. The Schrödinger equation
        becomes a steepest-descent equation in the L² metric: every eigenvector
        of H decays as exp(−E_n τ), so the ground state dominates for large τ.
        Renormalising ψ after each step keeps the norm equal to 1 and implicitly
        tracks the chemical potential μ = −d(log ‖ψ‖)/dτ. The{" "}
        <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-tdse-split-operator-fft-double-slit-quantum-interference-webxr">
          TDSE split-operator tutorial
        </Link>
        {" "}uses the same splitting idea for real-time quantum propagation.
      </p>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Strang splitting (2nd-order, one FFT pair per step):

  ψ₁ = exp(−V·dτ/2) ψ          half potential  V = ½r² + G|ψ|²
  ψ₂ = IFFT[exp(−½k²·dτ)·FFT[ψ₁]]  full kinetic (exact in k-space)
  ψ₃ = exp(−V·dτ/2) ψ₂         second half potential (updated V)
  ψ₄ = ψ₃ / ‖ψ₃‖               renormalise

WHY Strang and not Lie:  Strang is O(dτ²) vs O(dτ) — same cost, half the error.
WHY full FFT (not rfft2): ψ is complex; rfft2 would discard the
  imaginary part of the Fourier modes and corrupt the vortex phase.`}
      </pre>

      <h2>Vortex seeding</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`def _plant_vortices(positions):
    phase = np.zeros((N, N))
    for cx, cy in positions:
        phase += np.arctan2(Y - cy, X - cx)
    return phase

# Initial wavefunction: Thomas-Fermi amplitude × phase singularities
psi = TF_AMP * np.exp(1j * phase)

Winding number theorem: the integral of ∇θ around any closed curve equals
2π × (number of enclosed vortices). Imaginary time conserves this topological
invariant — it cannot annihilate a vortex without crossing a density zero,
which costs energy proportional to G. In the strongly interacting limit
(G=500), the wavefunction settles to the energy-minimum arrangement within
the seeded topological sector in < 3 000 steps.`}
      </pre>

      <h2>Shape keys</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Basis      0 vortices   Ω≈0      Smooth Thomas-Fermi hill; peak ≈ 0.50 m
SK_Single  1 vortex    Ω≈0.04   Deep central dimple; phase winds 2π around it
SK_Hex7    7 vortices  Ω≈0.28   Classic Abrikosov lattice: 1+6 hexagonal shell
SK_Hex19  19 vortices  Ω≈0.76   Two-shell lattice: 1+6+12; lattice spacing √(π/Ω)

Effective Ω = N_v / R_TF²  (vortex density × area);  R_TF ≈ 5.0.`}
      </pre>

      <h2>Vertex colouring</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`FLOAT_COLOR attribute "GPE_Density":
  t = |ψ|² / max(|ψ|²)           → [0, 1]
  colour = LERP(cobalt, amber, t)
  cobalt = (0.027, 0.159, 0.408)  ← vortex core (density = 0)
  amber  = (1.000, 0.702, 0.000)  ← condensate peak

Reading: cobalt wells are the vortex cores — each a quantum of superfluid
circulation ℏ/m. The amber plateau is the Thomas-Fermi bulk. The sharp
boundary at R_TF ≈ 5 oscillator units (≈ 4 m in mesh coordinates) is the
condensate edge — beyond it, density falls to zero.`}
      </pre>

      <h2>Troubleshooting</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Vortices merge or disappear during imaginary time:
  → Increase N_ITER from 3 000 to 5 000.  The imaginary-time gap between
    N-vortex state and (N-1)-vortex state shrinks with G — more steps needed.

Vortex cores not round (elliptical dimples):
  → The seeding positions were outside R_TF. Vortices near the condensate
    edge are not energetically stable and migrate to the boundary.  Reduce
    r7 (ring radius) from 2.2 to 1.8 to keep them inside the bulk.

Dense lattice (SK_Hex19) looks smeared:
  → 19 vortices in R_TF≈5 gives inter-vortex spacing ≈ 1.5 ξ — borderline
    resolved at 128×128.  Increase N to 256 and DT to 0.01 for cleaner cores.

Height field looks flat (no contrast):
  → density.max() ≈ 0: normalisation failed.  Check that TF_AMP is non-zero;
    if G is very large (>2000), TF_AMP may have been clipped to zero — reduce
    G or increase N to resolve the healing length ξ = 1/√G per grid cell.`}
      </pre>

      <h2>Codex and related tutorials</h2>
      <p>
        The imaginary-time technique is a PDE integration and uses the same FFT
        workflow as{" "}
        <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-tdse-split-operator-fft-double-slit-quantum-interference-webxr">
          TDSE split-operator (double slit)
        </Link>
        {" "}and{" "}
        <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-complex-ginzburg-landau-pde-spiral-turbulence-benjamin-feir-defect-height-field-stage-floor-webxr">
          Complex Ginzburg–Landau (spiral turbulence)
        </Link>
        . The GPE is the real-valued analogue of CGL when the imaginary dispersion
        coefficient c₁ → 0; phase defects in CGL and vortices in GPE are the same
        topological object. The conserved-order-parameter counterpart is the{" "}
        <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-cahn-hilliard-phase-field-spinodal-decomposition-ostwald-ripening-stage-floor-webxr">
          Cahn–Hilliard equation
        </Link>
        . For the height-field with toroidal symmetry driven by orbital angular
        momentum, see{" "}
        <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-laguerre-gaussian-optical-vortex-allen-1992-orbital-angular-momentum-height-field-stage-floor-webxr">
          Laguerre–Gaussian optical vortex beams
        </Link>
        . The bpy scripting pipeline is covered in{" "}
        <Link className={lk} href="/codex/blender-python-scripting">
          Blender Python Scripting
        </Link>
        {" "}and the FFT workflow in{" "}
        <Link className={lk} href="/codex/numpy-in-blender">
          NumPy in Blender
        </Link>
        .
      </p>

      <h2>Outside sources</h2>
      <p>
        Original equations:{" "}
        <a className={lk} href="https://doi.org/10.1007/BF02731494" target="_blank" rel="noreferrer">
          Gross EP (1961) Il Nuovo Cimento 20:454
        </a>
        {" "}and Pitaevskii LP (1961) JETP 13:451 — the GPE mean-field equation
        is mathematical content and public domain. Related: the{" "}
        <a className={lk} href="https://www.nobelprize.org/prizes/physics/2001/summary/" target="_blank" rel="noreferrer">
          Nobel Prize in Physics 2001 (Cornell, Wieman, Ketterle)
        </a>
        {" "}for achievement of BEC in dilute gases.
      </p>
      <p>
        Comprehensive review including imaginary-time numerics:{" "}
        <a className={lk} href="https://arxiv.org/abs/cond-mat/9806038" target="_blank" rel="noreferrer">
          Dalfovo S, Giorgini S, Pitaevskii LP, Stringari S (1999) Rev Mod Phys 71:463
        </a>
        {" "}— arXiv open access. §IV.B describes the imaginary-time method. Sibling
        BEC simulation projects:{" "}
        <a className={lk} href="https://github.com/scipy/scipy" target="_blank" rel="noreferrer">
          SciPy (BSD-3-Clause)
        </a>
        {" "}for sparse-matrix variants; the related Gross-Pitaevskii and
        Bogoliubov–de Gennes codebase at{" "}
        <a className={lk} href="https://github.com/qutip/qutip" target="_blank" rel="noreferrer">
          QuTiP (BSD-3-Clause)
        </a>
        .
      </p>
      <p>
        Array runtime:{" "}
        <a className={lk} href="https://numpy.org" target="_blank" rel="noreferrer">
          NumPy (BSD-3-Clause)
        </a>
        {" "}—{" "}
        <a className={lk} href="https://github.com/numpy/numpy" target="_blank" rel="noreferrer">
          github.com/numpy/numpy
        </a>
        .
      </p>
    </>
  );
}

export const entry: Entry = buildInstructable({
  slug: SLUG,
  title: TITLE,
  lede: LEDE,
  date: "2026-09-12",
  topics: [
    "blender",
    "python",
    "numpy",
    "gross-pitaevskii",
    "bec",
    "vortex-lattice",
    "imaginary-time",
    "abrikosov",
    "quantum",
    "stage-floor",
    "webxr",
    "5.1",
  ],
  body: Body,
});
