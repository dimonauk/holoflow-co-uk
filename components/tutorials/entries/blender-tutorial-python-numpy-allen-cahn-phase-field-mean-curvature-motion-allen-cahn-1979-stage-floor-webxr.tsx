import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-allen-cahn-phase-field-mean-curvature-motion-allen-cahn-1979-stage-floor-webxr";

const TITLE =
  "Python numpy — Allen–Cahn Phase-Field Equation: Non-Conserved Interface Motion by Mean Curvature, ETD1 Spectral Integration, Height-Field Stage Floor for WebXR (Blender 5.1)";

const LEDE =
  "Shake oil and water, then set it down: without the shaking the droplets merge — the smaller ones first, the larger ones last, until one phase wins entirely. The Allen–Cahn equation captures that directional coarsening in a single scalar field. This blueprint integrates it on a 128 × 128 periodic grid using ETD1 (Exponential Time Differencing), maps the phase order parameter to vertex height, and produces a stage-floor mesh whose amber peaks and cobalt valleys are the two stable phases of a Ginzburg–Landau double-well free energy.";

function Body() {
  return (
    <>
      <p>
        Phase-field models divide the world into two camps. In the conserved
        camp sits the{" "}
        <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-cahn-hilliard-phase-field-spinodal-decomposition-ostwald-ripening-stage-floor-webxr">
          Cahn–Hilliard equation
        </Link>
        {" "}— composition is locked; domains grow by Ostwald ripening with a
        characteristic length ⟨L⟩ ∼ t^(1/3). In the non-conserved camp sits
        Allen–Cahn: the total amount of each phase is free to change, and
        interfaces move by mean curvature at velocity v_n = ε · κ. Small
        circular islands shrink and vanish; the growth law is ⟨L⟩ ∼ t^(1/2).
        The same double-well free energy drives both equations, but the mobility
        operator differs: Allen–Cahn is an L² gradient flow, Cahn–Hilliard is
        an H⁻¹ gradient flow.
      </p>

      <p>
        The two equations are not merely cousins. Allen–Cahn is used to describe
        antiphase domain coarsening in metallic alloys, crystal grain boundaries,
        ferroelectric domain walls, and — in its vector form — the motion of
        bubbles in foam. When coupled with a temperature field it models
        solidification fronts.{" "}
        <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-complex-ginzburg-landau-pde-spiral-turbulence-benjamin-feir-defect-height-field-stage-floor-webxr">
          The Complex Ginzburg–Landau equation
        </Link>{" "}
        is a complex-valued generalisation of Allen–Cahn that admits spiral
        waves and phase turbulence — the simplest route to spatiotemporal chaos
        in an oscillatory medium.
      </p>

      <h2>Equation and free energy</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Allen–Cahn equation (Allen & Cahn 1979):

∂φ/∂t = ε²∇²φ − F′(φ)
F(φ)   = ¼(1 − φ²)²     (Ginzburg–Landau double-well)
F′(φ)  = φ³ − φ          (zero at φ = −1, 0, +1)

Equivalently, after splitting off the +φ linear term:
∂φ/∂t = (ε²∇² + 1)φ  −  φ³
       =      L̂φ      + N(φ)
L̂φ:   linear — stiff for large k, stabilising for small k
N(φ):  nonlinear — bounded (φ³ near ±1 resists blow-up)`}
      </pre>

      <h2>Sharp-interface limit</h2>
      <p>
        As ε → 0 (sharp interface), Allen–Cahn reduces to the <em>mean
        curvature flow</em>: every point on a domain boundary moves in the
        inward-normal direction at speed proportional to the local mean
        curvature κ. A circle of radius R shrinks as R(t)² = R₀² − 2ε²t and
        disappears in finite time. This is a purely geometric evolution — no
        diffusion, no mass transport — and it is the reason Allen–Cahn coarsens
        faster than Cahn–Hilliard.
      </p>
      <p>
        The interface thickness is proportional to ε. The shape keys
        SK_Fine (ε = 0.012) and SK_Broad (ε = 0.040) demonstrate the
        effect directly: halving ε halves the wall width and reveals finer
        internal structure in the same number of time steps.
      </p>

      <h2>ETD1 — Exponential Time Differencing</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Split: ∂φ/∂t = L̂φ + N(φ)   with L̂ = ε²∇² + 1

Fourier eigenvalue of L̂:  λ_k = 1 − ε²|k|²
  k² < 1/ε²  →  λ_k > 0  (slow modes: unstable, drive phase separation)
  k² > 1/ε²  →  λ_k < 0  (fast modes: stable, damp interface wiggles)

ETD1 step (exact for linear, Euler for nonlinear):

  φ̂(t+dt) = E_k · φ̂(t) + φ₁(λ_k dt) · dt · F̂{N(φ(t))}

  E_k    = exp(λ_k · dt)              exact linear propagator
  φ₁(z)  = expm1(z)/z  ≈  1 + z/2    ETD weight (via expm1 for z ≈ 0)

WHY not semi-implicit:
  Semi-implicit denominator = 1 − dt·λ_k.
  At k² = 1/ε² the eigenvalue λ_k = 0 → denominator = 1 (fine).
  But numerically, floating-point λ_k near 0 produces near-cancellation in
  1/(1 − dt·λ_k). ETD1 avoids this: for λ_k ≈ 0, expm1(z)/z → 1 stably.
  For large |λ_k dt|, E_k decays/grows exponentially — always bounded.`}
      </pre>

      <h2>Blueprint walkthrough</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`# 1. Wavenumber grid (rfft2 shape — half the columns)
kx = np.fft.fftfreq(N, d=1/N)[:, None]    # (N, 1) integer cycles/grid
ky = np.fft.rfftfreq(N, d=1/N)[None, :]   # (1, N//2+1)
k2 = kx**2 + ky**2                         # (N, N//2+1)

# 2. ETD1 coefficients (computed once per (ε, dt) pair)
lam    = 1.0 - eps**2 * k2    # linear Fourier eigenvalue
lam_dt = lam * dt
E_k    = np.exp(lam_dt)       # propagator
phi1   = expm1(lam_dt)/lam_dt # (Taylor fallback near zero)

# 3. Integration loop
for _ in range(steps):
    phi_hat = rfft2(phi)
    nl_hat  = rfft2(-phi**3)           # N(φ) = -φ³
    phi_hat = E_k * phi_hat + phi1 * dt * nl_hat
    phi     = irfft2(phi_hat, s=(N,N))
    phi     = np.clip(phi, -2, 2)      # safety guard

# 4. Mesh: φ → vertex height z = φ × HEIGHT_SCALE (0.40 m)`}
      </pre>

      <h2>Why rfft2 and not fft2</h2>
      <p>
        The order parameter φ is a real field. The full FFT of a real N × N
        array wastes exactly half its output on the conjugate-symmetric
        redundant modes. NumPy's <code>rfft2</code> returns only the
        (N, N//2+1) unique modes — roughly half the memory and about half the
        arithmetic. The inverse <code>irfft2</code> accepts an output size
        argument <code>s=(N,N)</code> that guarantees the correct even-length
        reconstruction. The savings are modest at 128 × 128 but become
        significant at 512 × 512 or above, which is why the habit is worth
        building from the start. See also{" "}
        <Link className={lk} href="/codex/numpy-in-blender">
          NumPy in Blender
        </Link>{" "}
        for a broader treatment of the FFT workflow.
      </p>

      <h2>Vertex colouring</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`FLOAT_COLOR attribute "AC_Phase":
  t = (φ + 1) / 2              → [0, 1]
  colour = LERP(cobalt, amber, t)
  cobalt  = (0.030, 0.200, 0.780)  ← φ = −1 (one phase)
  amber   = (0.980, 0.620, 0.050)  ← φ = +1 (other phase)
  interface (φ ≈ 0) → intermediate purple–green hue

FLOAT_COLOR, not BYTE_COLOR: preserves sub-integer precision needed to
distinguish the diffuse interface gradient from the flat bulk phases.`}
      </pre>

      <h2>Shape key programme</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Basis       ε=0.020  t=10   Fine blobs; many nucleation sites
SK_Coarsened ε=0.020  t=70   Fewer, larger domains; smaller ones gone
SK_Fine      ε=0.012  t=25   Sharper walls; fractal-like fine texture
SK_Broad     ε=0.040  t=15   Diffuse walls; smooth domain morphology

All four start from the same random seed — the ε variants show the
interface-width effect; the Basis/Coarsened pair shows temporal evolution.`}
      </pre>

      <h2>Troubleshooting</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`φ stuck at near-zero after integration:
  → Initial noise amplitude too small. Increase rng scale from 0.05 to 0.2.

φ blows up beyond ±2 (clipped):
  → dt is too large for the nonlinear term. Reduce DT from 0.10 to 0.05.
  → ETD1 is only unconditionally stable for the linear part; the nonlinear
    φ³ term still has a stability requirement: dt × max(φ²) < O(1).

All shape keys look identical:
  → STEPS differences too small. Coarsen with STEPS_COARSE ≥ 5 × STEPS_BASIS.

SK_Fine looks same as Basis:
  → ε=0.012 with STEPS_FINE=250 (t=25) coarsens slower than ε=0.020 t=10.
    This is correct — smaller ε means a longer coarsening timescale.
    Increase STEPS_FINE to 600 for a more contrasted visual.`}
      </pre>

      <h2>Codex and related tutorials</h2>
      <p>
        The bpy scripting workflow is covered in{" "}
        <Link className={lk} href="/codex/blender-python-scripting">
          Blender Python Scripting
        </Link>
        {" "}and the array pipeline in{" "}
        <Link className={lk} href="/codex/numpy-in-blender">
          NumPy in Blender
        </Link>
        . For the conserved phase-field counterpart, see{" "}
        <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-cahn-hilliard-phase-field-spinodal-decomposition-ostwald-ripening-stage-floor-webxr">
          Cahn–Hilliard Spinodal Decomposition
        </Link>
        . For two-component reaction-diffusion with Turing patterns, see{" "}
        <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-gray-scott-reaction-diffusion-turing-pattern-height-field-webxr">
          Gray–Scott Reaction-Diffusion
        </Link>
        . For the complex-valued Ginzburg–Landau generalisation, see{" "}
        <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-complex-ginzburg-landau-pde-spiral-turbulence-benjamin-feir-defect-height-field-stage-floor-webxr">
          Complex Ginzburg–Landau PDE
        </Link>
        . Swift–Hohenberg (pattern-selecting 4th-order PDE) is at{" "}
        <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-swift-hohenberg-pde-hexagonal-rolls-benard-convection-stage-floor-webxr">
          Swift–Hohenberg
        </Link>
        .
      </p>

      <h2>Outside sources</h2>
      <p>
        The defining paper:{" "}
        <a
          className={lk}
          href="https://doi.org/10.1016/0001-6160(79)90196-2"
          target="_blank"
          rel="noreferrer"
        >
          Allen SM &amp; Cahn JW (1979) Acta Metallurgica 27:1085–1095
        </a>{" "}
        — antiphase boundary motion; equations are public domain as mathematical
        content. Related upstream work includes Cahn &amp; Hilliard (1958) and
        the broader phase-field community using{" "}
        <a
          className={lk}
          href="https://github.com/scipy/scipy"
          target="_blank"
          rel="noreferrer"
        >
          SciPy
        </a>{" "}
        for sparse-matrix phase-field solvers.
      </p>
      <p>
        The ETD1 time-integration scheme:{" "}
        <a
          className={lk}
          href="https://doi.org/10.1006/jcph.2002.6995"
          target="_blank"
          rel="noreferrer"
        >
          Cox SM &amp; Matthews PC (2002) J Comput Phys 176:430–455
        </a>{" "}
        — Exponential Time Differencing; the ETD1 and ETDRK4 algorithms are
        mathematical methods and their equations are public domain. Related
        spectral PDE tools include{" "}
        <a
          className={lk}
          href="https://github.com/spectralDNS/shenfun"
          target="_blank"
          rel="noreferrer"
        >
          shenfun (MIT)
        </a>
        {" "}for high-order Galerkin spectral methods.
      </p>
      <p>
        Array runtime:{" "}
        <a
          className={lk}
          href="https://numpy.org"
          target="_blank"
          rel="noreferrer"
        >
          NumPy
        </a>{" "}
        (BSD-3-Clause,{" "}
        <a
          className={lk}
          href="https://github.com/numpy/numpy"
          target="_blank"
          rel="noreferrer"
        >
          github.com/numpy/numpy
        </a>
        ). Related packages:{" "}
        <a
          className={lk}
          href="https://github.com/cupy/cupy"
          target="_blank"
          rel="noreferrer"
        >
          CuPy (MIT)
        </a>{" "}
        for GPU-accelerated rfft2 when grid sizes exceed 512 × 512.
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
    "phase-field",
    "allen-cahn",
    "pde",
    "etd1",
    "mean-curvature",
    "stage-floor",
    "webxr",
    "5.1",
  ],
  body: Body,
});
