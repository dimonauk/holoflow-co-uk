import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-korteweg-de-vries-1895-soliton-collision-" +
  "pseudospectral-rk4-space-time-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — KdV (Korteweg–de Vries 1895): " +
  "u_t + 6u u_x + u_xxx = 0 " +
  "Fourier Pseudospectral RK4 Soliton Collisions " +
  "2/3-Rule Dealiasing Phase Shift Δx=(2/κ)ln((κ₁+κ₂)/(κ₁−κ₂)) " +
  "128×128=16384V 16129Q " +
  "Basis(2-soliton κ=[1,0.5] t≈8)/SK_Single(1-soliton)/SK_Three(3-soliton)/SK_Slow(slow pair) " +
  "KdV_Height FLOAT_COLOR Cobalt–Amber Space-Time Height-Field Stage Floor WebXR (Blender 5.1)";

const LEDE =
  "Korteweg and de Vries derived their equation for shallow-water waves in 1895, " +
  "but the remarkable fact that its solutions pass through one another without change " +
  "of shape — the soliton — was not understood until Gardner, Greene, Kruskal, and Miura " +
  "invented the inverse-scattering transform in 1967. " +
  "This blueprint integrates KdV on a periodic grid using Fourier pseudospectral + RK4, " +
  "then lays the space-time diagram flat as a stage floor: time runs forward along the y-axis, " +
  "space along the x-axis, and soliton amplitude rises as height — so each soliton is " +
  "a diagonal ridge, and a collision is two ridges crossing with a visible kink.";

function Body() {
  return (
    <>
      <p>
        The KdV equation is the simplest model that combines nonlinear steepening
        (the 6u u_x term, which would cause wave-breaking on its own) with linear
        dispersion (u_xxx, which spreads a wave packet). The two effects balance
        to produce a soliton: a solitary wave whose shape is fixed by the exact
        cancellation of spreading and steepening at every instant.
      </p>

      <h2>The equation and its exact soliton</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`u_t + 6u u_x + u_xxx = 0

1-soliton (positive, right-moving):
  u₁(x,t) = 2κ² sech²(κ(x − 4κ²t − x₀))
  speed   c = 4κ²         (faster soliton is taller)
  amplitude A = c/2 = 2κ² (amplitude-speed lock)
  FWHM    ≈ 3.526/κ       (faster soliton is narrower)`}
      </pre>
      <p>
        The amplitude–speed relation A = c/2 means solitons are self-similar
        under rescaling: doubling the speed quadruples the wavenumber κ, doubles
        the amplitude, and halves the width. On the floor, faster solitons appear
        as steeper, taller, narrower ridges.
      </p>

      <h2>Soliton collisions and the phase shift</h2>
      <p>
        When a faster soliton (κ₁ &gt; κ₂) overtakes a slower one, the faster
        ridge bends forward and the slower one bends backward in the space-time
        diagram. The exact asymptotic phase shifts (Gardner–Greene–Kruskal–Miura
        1967 inverse-scattering solution) are:
      </p>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Δx₊ = (2/κ₁) · ln((κ₁+κ₂)/(κ₁−κ₂))   (faster ridge, forward shift)
Δx₋ = (2/κ₂) · ln((κ₁+κ₂)/(κ₁−κ₂))   (slower ridge, backward shift)

For κ₁=1, κ₂=0.5  (Basis shape key):
  Δx₊ ≈ 2.20 m on the floor   (visible kink in the faster ridge)
  Δx₋ ≈ 4.39 m on the floor   (larger kink in the slower ridge)`}
      </pre>
      <p>
        These bends are measurable from the rendered floor: place a ruler along
        each ridge before and after the crossing and the offset matches the formula
        to within numerical error. That is the defining test of integrability.
      </p>

      <h2>Conserved quantities</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`I₁ = ∫u dx            (mass — total area under the floor)
I₂ = ½∫u² dx          (L² norm — "momentum")
I₃ = ∫(u³ − ½u_x²) dx (energy — Hamiltonian)
⋮  (infinite tower for KdV; n-th conserved density ~ u^n + derivatives)`}
      </pre>
      <p>
        The blueprint prints I₂ before and after integration as a sanity check.
        The pseudospectral RK4 scheme conserves I₂ to within floating-point
        precision over 600 steps — no artificial dissipation, no spurious energy
        loss from spatial discretisation.
      </p>

      <h2>Fourier pseudospectral + RK4</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Periodic domain x ∈ [0, 64], N_X = 128, dx = 0.5
Wavenumber k_j = 2π/64 · j,  j = 0,1,…,63,−64,…,−1

Fourier formulation (exact spatial derivatives):
  û_t = ik³ û − 3ik · FFT(u²)
       ↑                 ↑
   dispersive (stiff)    nonlinear (pseudospectral)

2/3-rule dealiasing (Orszag 1971):
  Zero out |k| > (2/3)·k_Nyquist ≈ 4.19 rad/unit
  Prevents aliasing of u² → spurious high-k energy

Stability (RK4 on imaginary axis, dt_stable ≤ 2√2/k_max³):
  dt_stable ≈ 0.038   →   DT = 0.02 (factor 1.9 margin)`}
      </pre>
      <p>
        WHY RK4 here rather than ETDRK4: the linear operator ik³ is purely
        imaginary — it has no negative-real stiff part to integrate exactly.
        ETDRK4 gains its advantage by treating stiff real dissipation exactly;
        for a purely dispersive equation that advantage is absent, and RK4 is
        both simpler and sufficient.
      </p>

      <h2>Shape keys</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Basis     2-soliton  κ=[1.0, 0.5]         x₀=[8, 32]       collision t≈8
SK_Single 1-soliton  κ=1.0                x₀=16            single ridge
SK_Three  3-soliton  κ=[1.0, 0.75, 0.5]  x₀=[5, 18, 32]   two collisions
SK_Slow   2-soliton  κ=[0.75, 0.5]       x₀=[5, 20]        slow pair`}
      </pre>

      <h2>Troubleshooting</h2>
      <ul className="list-disc pl-5 space-y-1">
        <li>
          <strong>Soliton disperses over time:</strong> DT too large — the RK4
          imaginary-axis stability criterion is violated at high k. Halve DT and
          double N_STEPS.
        </li>
        <li>
          <strong>Negative heights visible:</strong> numerical noise at the
          background level. The <code>clip(u/U_NORM, 0, 3)</code> call in
          _verts_faces removes them; adjust U_NORM if solitons are undersized.
        </li>
        <li>
          <strong>Aliasing spikes after long runs:</strong> increase dealiasing
          from 2/3 to 1/2 (Canuto et al. 2006) or add a tiny spectral viscosity
          ν_s ·|k|^8 ·û with ν_s = 1e-14.
        </li>
      </ul>

      <h2>Studio cross-references</h2>
      <ul className="list-disc pl-5 space-y-1">
        <li>
          <Link
            href="/tutorials/blender-tutorial-python-numpy-kpz-kardar-parisi-zhang-1986-stochastic-surface-growth-universality-height-field-stage-floor-webxr"
            className={lk}
          >
            KPZ equation 1986 — stochastic interface growth
          </Link>{" "}
          — another Fourier+ETD height-field floor; the Cole–Hopf substitution
          maps 1D KPZ directly to the stochastic heat equation, which is the
          Schrödinger equation in imaginary time — connecting KdV and KPZ
          through mathematical physics.
        </li>
        <li>
          <Link
            href="/tutorials/blender-tutorial-python-numpy-kuramoto-sivashinsky-pde-spatiotemporal-chaos-flame-front-height-field-stage-floor-webxr"
            className={lk}
          >
            Kuramoto–Sivashinsky — spatiotemporal chaos
          </Link>{" "}
          — another 1D PDE rendered as a space-time floor; contrast with KdV&apos;s
          clean soliton collisions — KS is chaotic because its fourth-order
          term inverts the stability of KdV&apos;s third-order dispersion.
        </li>
        <li>
          <Link
            href="/tutorials/blender-tutorial-python-numpy-complex-ginzburg-landau-pde-spiral-turbulence-benjamin-feir-defect-height-field-stage-floor-webxr"
            className={lk}
          >
            Complex Ginzburg–Landau — spiral turbulence
          </Link>{" "}
          — a 2D dissipative PDE floor; CGL in 1D contains the NLS (nonlinear
          Schrödinger) equation as a special case, which is the complex cousin
          of KdV with bright solitons instead of KdV&apos;s real ones.
        </li>
        <li>
          <Link
            href="/tutorials/blender-tutorial-python-numpy-allen-cahn-phase-field-mean-curvature-motion-allen-cahn-1979-stage-floor-webxr"
            className={lk}
          >
            Allen–Cahn phase field — mean-curvature motion
          </Link>{" "}
          — shows ETD1 integration for a stiff real-eigenvalue PDE; compare
          with KdV&apos;s RK4 to understand when ETD is worth the extra complexity.
        </li>
      </ul>

      <h2>Outside sources</h2>
      <ul className="list-disc pl-5 space-y-1">
        <li>
          Korteweg D J &amp; de Vries G (1895){" "}
          <a
            href="https://doi.org/10.1080/14786449508620739"
            className={lk}
            target="_blank"
            rel="noopener noreferrer"
          >
            On the change of form of long waves advancing in a rectangular canal,
            and on a new type of long stationary waves.{" "}
            <em>Philosophical Magazine</em> 39(240):422–443
          </a>{" "}
          — original derivation; equations are public domain. Related: Boussinesq
          J (1877) earlier shallow-water analysis, Stokes G G (1847) original wave
          dispersion relation.
        </li>
        <li>
          Gardner C S, Greene J M, Kruskal M D, Miura R M (1967){" "}
          <a
            href="https://doi.org/10.1103/PhysRevLett.19.1095"
            className={lk}
            target="_blank"
            rel="noopener noreferrer"
          >
            Method for solving the Korteweg–de Vries equation.{" "}
            <em>Phys Rev Lett</em> 19(19):1095–1097
          </a>{" "}
          — inverse scattering transform, N-soliton phase shifts; equations PD.
          Related: Ablowitz M J &amp; Segur H (1981){" "}
          <a
            href="https://epubs.siam.org/doi/book/10.1137/1.9781611970883"
            className={lk}
            target="_blank"
            rel="noopener noreferrer"
          >
            Solitons and the Inverse Scattering Transform
          </a>{" "}
          (SIAM, freely accessible to members); and the dysts Python library (MIT)
          at{" "}
          <a
            href="https://github.com/williamgilpin/dysts"
            className={lk}
            target="_blank"
            rel="noopener noreferrer"
          >
            github.com/williamgilpin/dysts
          </a>{" "}
          — open catalogue of chaotic systems and integrable maps.
        </li>
        <li>
          NumPy contributors —{" "}
          <a
            href="https://numpy.org/doc/stable/user/"
            className={lk}
            target="_blank"
            rel="noopener noreferrer"
          >
            NumPy User Guide
          </a>{" "}
          (BSD-3-Clause). Related: SciPy (BSD-3-Clause) at{" "}
          <a
            href="https://scipy.org"
            className={lk}
            target="_blank"
            rel="noopener noreferrer"
          >
            scipy.org
          </a>
          ; Dedalus Project (GPL-3 — excluded from blueprint, cited for
          comparison only) at{" "}
          <a
            href="https://dedalus-project.org"
            className={lk}
            target="_blank"
            rel="noopener noreferrer"
          >
            dedalus-project.org
          </a>
          .
        </li>
      </ul>
    </>
  );
}

export const entry: Entry = buildInstructable({
  slug:  SLUG,
  title: TITLE,
  lede:  LEDE,
  date:  "2026-09-12",
  body:  <Body />,
  tags:  [
    "blender",
    "python",
    "scripting",
    "numpy",
    "pde",
    "soliton",
    "dispersive-waves",
    "kdv",
    "pseudospectral",
    "height-field",
    "webxr",
    "integrable-systems",
  ],
  libraryPath: `blends/scripting/python-numpy-korteweg-de-vries-1895-soliton-collision-pseudospectral-rk4-space-time-height-field-stage-floor-webxr/`,
});
