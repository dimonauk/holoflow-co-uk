import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-nlse-nonlinear-schrodinger-1972-zakharov-shabat-soliton-collision-akhmediev-breather-peregrine-rogue-wave-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — Nonlinear Schrödinger Equation, Zakharov–Shabat 1972 Integrability, Soliton Collision, Akhmediev Breather, Peregrine Rogue Wave, Strang Split-Step Fourier, Height-Field Stage Floor for WebXR (Blender 5.1)";

const LEDE =
  "The focusing nonlinear Schrödinger equation (i∂ψ/∂t + ∂²ψ/∂x² + 2|ψ|²ψ = 0) governs deep-water wave packets, single-mode optical fibres, Bose–Einstein condensates without trapping, and plasma Langmuir waves. Its integrability — established by Zakharov and Shabat via the inverse-scattering transform in 1972 — supplies an infinite tower of conserved quantities and exact multi-soliton solutions in which collisions are perfectly elastic. The same equation admits modulational instability of the plane-wave background: small perturbations grow into Akhmediev breathers (periodic in space, localised in time), Kuznetsov–Ma breathers (localised in space, periodic in time), and the doubly-localised Peregrine soliton whose peak amplitude is exactly three times the background — the mathematical archetype of the ocean rogue wave. This blueprint builds a 128×128 space-time |ψ(x,t)| height-field mesh in Blender 5.1 using a Strang split-step Fourier integrator, with four shape keys covering all four regimes.";

function Body() {
  return (
    <>
      <p>
        The nonlinear Schrödinger equation sits at the intersection of water
        waves, fibre optics, and quantum condensates. Like the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-korteweg-de-vries-1895-soliton-collision-pseudospectral-rk4-space-time-height-field-stage-floor-webxr"
        >
          Korteweg–de Vries equation
        </Link>
        , it is integrable — yet the NLSE is two-dimensional in the
        (space, time) sense and supports a far richer menagerie of exact
        solutions. Where KdV solitons travel at speeds set by amplitude,
        NLSE solitons travel at an independently tunable group velocity,
        and the plane-wave background spawns the entire breather hierarchy
        through modulational instability.
      </p>

      <h2>The equation and its physical contexts</h2>

      <p>
        In the focusing sign (positive nonlinearity) the NLSE reads:
      </p>

      <pre>{`i∂ψ/∂t + ∂²ψ/∂x² + 2|ψ|²ψ = 0`}</pre>

      <p>
        Physical contexts and their re-scalings:
      </p>

      <pre>{`Deep water (Zakharov 1968):  A_T + ½ω₀/k₀² A_XX − ½ω₀k₀²|A|²A = 0
Optical fibre (Hasegawa 1973): iE_z = β₂/2 E_tt − γ|E|²E
BEC (Gross–Pitaevskii):       iħ∂ψ/∂t = (−ħ²∇²/2m + V + g|ψ|²)ψ`}</pre>

      <p>
        The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-gross-pitaevskii-bec-rotating-vortex-lattice-abrikosov-imaginary-time-stage-floor-webxr"
        >
          Gross–Pitaevskii
        </Link>{" "}
        entry covers the BEC case with a trapping potential and rotation.
        Here we work in 1D without a trap, where the NLSE is exactly
        integrable by the Zakharov–Shabat (ZS) inverse-scattering transform —
        a non-linear analogue of the Fourier transform in which solitons are
        the &lsquo;modes&rsquo; and their eigenvalues are the conserved quantities.
      </p>

      <h2>Integrability and the ZS spectrum</h2>

      <p>
        Zakharov and Shabat (1972, Sov. Phys. JETP 34:62) showed that the NLSE
        is the compatibility condition for the ZS pair:
      </p>

      <pre>{`∂v₁/∂x = −iλv₁ + ψv₂
∂v₂/∂x =  iλv₂ + ψ*v₁`}</pre>

      <p>
        The discrete spectrum {"{λⱼ = ξⱼ + iηⱼ}"} gives the solitons:
        η_j sets the amplitude, ξ_j sets the velocity. The continuous spectrum
        encodes dispersive radiation. The conserved quantities include mass
        (‖ψ‖²), momentum (Im∫ψ*ψ_x dx), and Hamiltonian (∫(|ψ_x|² − |ψ|⁴)dx).
      </p>

      <h2>The four shape keys</h2>

      <h3>Basis — two-soliton head-on collision</h3>

      <p>
        Initial condition ψ₀ = sech(x+3)·e^{"{i(v/2)x}"}  +  sech(x−3)·e^{"{−i(v/2)x}"}
        with v = 0.5, so the ZS spectrum has two eigenvalues at
        λ₁ = 0.25+i (rightward soliton) and λ₂ = −0.25+i (leftward).
        The solitons collide near x=0, t≈6 and emerge with a phase shift
        Δφ = 2 arctan(2η/(ξ₁−ξ₂)) — the only trace of the interaction.
        Amplitude and shape are unchanged: NLSE elastic collision is exact,
        a consequence of integrability rather than an approximation.
      </p>

      <h3>SK_Akhmediev — modulational instability breather</h3>

      <p>
        The plane-wave ψ₀ = 1 is a solution (up to phase e^{"{2it}"}), but it is
        Benjamin–Feir unstable: a perturbation at wavenumber q satisfies the
        linearised growth rate σ = q√(4−q²)/2. For q = 2π/L ≈ 0.52,
        σ ≈ 0.51, and the perturbation grows exponentially over timescale 1/σ ≈ 2.
        The nonlinear saturation produces an Akhmediev breather — periodic in x,
        localised in t — which peaks, then returns to the plane-wave background
        in a near-perfect Fermi–Pasta–Ulam–Tsingou (FPUT) recurrence. Unlike the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-complex-ginzburg-landau-pde-spiral-turbulence-benjamin-feir-defect-height-field-stage-floor-webxr"
        >
          complex Ginzburg–Landau
        </Link>{" "}
        equation, the integrable NLSE sustains this recurrence indefinitely in
        the absence of noise.
      </p>

      <h3>SK_KM — Kuznetsov–Ma breathing soliton</h3>

      <p>
        A localised bump ψ₀ = 1 + 0.70 sech(0.7x) placed on the background
        evolves into a structure periodic in time and localised in space — the
        KM breather regime (Kuznetsov 1977, Ma 1979). In the exact solution the
        KM period is T = 2π/√(8a(2a−1)) for parameter a &gt; 1/2. The bump
        amplitude 0.70 corresponds to a ≈ 0.60, giving T ≈ 9 time units,
        consistent with the observed breathing frequency over the 12.7-unit
        window.
      </p>

      <h3>SK_Peregrine — rogue wave (exact formula)</h3>

      <p>
        The Peregrine soliton (Peregrine 1983) is the a → 1/2 limit of both
        the Akhmediev and KM families, doubly localised in x and t:
      </p>

      <pre>{`ψ_P(x,t) = e^{2it} · [1 − 4(1+2it) / (1 + 4x² + 4t²)]

At (x,t) = (0,0):   |ψ_P| = 3   (triple the background)
As x→∞ or t→∞:      |ψ_P| → 1   (returns to plane wave)`}</pre>

      <p>
        This formula is evaluated on an independent 128×128 grid (x ∈ [−5,5],
        t ∈ [−4,4]) — no PDE integration required, the shape key is exact.
        The dramatic spike at the mesh centre encodes the three-fold amplitude
        amplification that makes the Peregrine soliton the accepted model for
        oceanic rogue waves observed in the JONSWAP experiment and reproduced in
        water-tank experiments by Chabchoub et al. (2011,{" "}
        <a
          className={lk}
          href="https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.106.204502"
          target="_blank"
          rel="noopener noreferrer"
        >
          PRL 106:204502
        </a>
        ).
      </p>

      <h2>Strang split-step Fourier method</h2>

      <p>
        The NLSE splits cleanly into a linear part (dispersion) and a nonlinear
        part (self-phase modulation), each solvable exactly:
      </p>

      <pre>{`Linear:    ψ̂(k,t+dt) = ψ̂(k,t) · exp(−ik²dt)      (spectral, exact)
Nonlinear: ψ(x,t+dt)  = ψ(x,t) · exp(2i|ψ|²dt)    (pointwise, |ψ| conserved)`}</pre>

      <p>
        Strang (symmetric) splitting gives 2nd-order accuracy in dt:
        apply NL for dt/2, then Linear for dt, then NL for dt/2.
        Consecutive NL half-steps from adjacent time steps combine into a single
        full NL step at interior points, giving an efficient loop. At N=128
        spatial points, each step costs two FFTs plus pointwise multiplies —
        well within interactive speed in Blender&apos;s Python environment.
      </p>

      <h2>Failure modes and troubleshooting</h2>

      <pre>{`Aliasing blow-up:  If |ψ| grows without bound, reduce DT or
                   add 2/3 de-aliasing (zero kk > N/3 modes).
Phase recurrence:  The SSF is symplectic and conserves ‖ψ‖²
                   to machine precision; any drift signals a bug.
Peregrine centering: The formula uses an independent grid; if the
                   spike is off-centre, check meshgrid indexing.`}</pre>

      <h2>Outside sources</h2>

      <p>
        <strong>
          Zakharov, V.E. &amp; Shabat, A.B. (1972). &ldquo;Exact theory of
          two-dimensional self-focusing and one-dimensional self-modulation of
          waves in nonlinear media.&rdquo;
        </strong>{" "}
        <em>Sov. Phys. JETP</em> 34(1):62–69.{" "}
        <a
          className={lk}
          href="https://www.jetp.ac.ru/cgi-bin/dn/e_034_01_0062.pdf"
          target="_blank"
          rel="noopener noreferrer"
        >
          JETP direct link
        </a>
        . Public Domain (&gt;50 yr). The foundational paper establishing NLSE
        integrability via the inverse-scattering transform and giving the exact
        N-soliton solution. Related project: AKNS (Ablowitz–Kaup–Newell–Segur
        1974, also PD), which generalises the ZS framework to a wide class of
        integrable PDEs including the sine-Gordon equation.
      </p>

      <p>
        <strong>
          Peregrine, D.H. (1983). &ldquo;Water waves, nonlinear Schrödinger
          equations and their solutions.&rdquo;
        </strong>{" "}
        <em>J. Austral. Math. Soc. Ser. B</em> 25:16–43. Public Domain
        (&gt;30 yr). Derives the exact rational solution used in SK_Peregrine,
        including the proof that |ψ_P|_max = 3 and the asymptotic return to the
        plane-wave background. Related project: Chabchoub et al. (2011) PRL
        water-tank verification, available open-access at APS.
      </p>
    </>
  );
}

export const blenderTutorialPythonNumpyNlseNonlinearSchrodinger1972ZakharovShabatSolitonCollisionAkhmedievBreatherPeregrineRogueWaveHeightFieldStageFloorWebxrEntry: Entry = buildInstructable({
  slug: SLUG,
  title: TITLE,
  lede: LEDE,
  body: <Body />,
  topics: ["blender", "python", "scripting", "physics", "waves", "optics", "webxr"],
  blenderVersion: "5.1",
  publishedAt: "2026-09-19",
  libraryPath:
    "blends/scripting/python-numpy-nlse-nonlinear-schrodinger-1972-zakharov-shabat-soliton-collision-akhmediev-breather-peregrine-rogue-wave-height-field-stage-floor-webxr",
});
