import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-kuramoto-2d-phase-oscillators-synchronisation-spiral-wave-chimera-stage-floor-webxr";

const TITLE =
  "Python numpy — 2D Kuramoto Model: Coupled Phase Oscillators, Synchronisation Transition, Spiral Waves & Chimera States, Height-Field Stage Floor for WebXR (Blender 5.1)";

const LEDE =
  "Yoshiki Kuramoto asked in 1975 whether a population of oscillators with different natural rhythms could spontaneously lock to a common beat. The answer, embarrassingly tidy, is: yes, at a critical coupling K_c that depends only on the width of the frequency distribution. Below K_c the phases tumble independently and the cosine height-field churns like turbulence; above K_c a macroscopic fraction lock and the field resolves into smooth, slowly rotating spiral wave-fronts. This blueprint simulates the 2D nearest-neighbour Kuramoto model in NumPy inside Blender 5.1, bakes four coupling regimes into shape keys, colours the mesh by local order parameter, and exports a 128 × 128 quad-grid stage floor as a Draco-compressed GLB ready for WebXR.";

function Body() {
  return (
    <>
      <p>
        The Kuramoto model is the canonical model for synchronisation —
        the same phenomenon that makes fireflies flash in unison, cardiac
        pacemaker cells beat together, and power-grid generators stay
        in phase. It is the dynamical counterpart to the equilibrium{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-xy-model-2d-berezinskii-kosterlitz-thouless-1971-1973-vortex-antivortex-unbinding-topological-phase-transition-height-field-stage-floor-webxr"
        >
          2D XY model
        </Link>
        : both involve planar rotors interacting via a cosine-of-difference
        coupling, but the XY model is sampled at thermal equilibrium by
        Metropolis Monte Carlo, while the Kuramoto model evolves by
        deterministic ODE dynamics with each rotor driven by its own
        natural frequency ω.
      </p>

      <h2>The equations</h2>

      <pre>{`dθ_{i,j}/dt = ω_{i,j}  +  K Σ_{nn} sin(θ_nn − θ_{i,j})

ω_{i,j} ~ Lorentzian(0, κ):  F(ω) = κ / [π(ω² + κ²)]
θ_{i,j} ∈ [0, 2π),  periodic boundary conditions
Height field h_{i,j} = 0.5 + 0.5·cos(θ_{i,j})  ∈ [0, 1]`}</pre>

      <p>
        The four nearest neighbours (±i, ±j) contribute a restoring torque
        proportional to the sine of their phase lead over the local oscillator.
        When K is large, this torque wins over the spread in ω and phases lock.
        When K is small, each oscillator advances at its own pace and phases
        decorrelate.
      </p>

      <h2>Why Lorentzian frequencies</h2>

      <p>
        Kuramoto&apos;s 1975 derivation used a Lorentzian (Cauchy) distribution
        because it yields a closed-form solution for the order parameter in the
        all-to-all coupled thermodynamic limit. The mean-field critical coupling
        is K_c = 2κ for a Lorentzian of half-width κ. Gaussian distributions
        require numerical quadrature; the Lorentzian is the analytically
        tractable choice. On the square lattice with nearest-neighbour coupling
        the threshold shifts upward — the sparser graph needs stronger coupling
        to propagate synchrony — but the qualitative transition remains.
      </p>

      <p>
        The blueprint draws frequencies via the inverse CDF: if U ~ Uniform(0,1)
        then ω = κ·tan(π(U−0.5)) ~ Cauchy(0, κ). Tails beyond ±6κ are clamped
        to prevent the heavy Lorentzian tail from producing pathological outlier
        oscillators that refuse to lock at any K.
      </p>

      <h2>Numerical integration</h2>

      <p>
        Forward Euler with DT = 0.05 is stable for this system. The Kuramoto
        ODE is bounded: |dθ/dt| ≤ |ω| + 4K. With K = 3.5 and the clamped
        Lorentzian |ω_max| ≤ 6κ = 1.8, the maximum rate is 15.8 rad/s, giving
        a phase advance per step of at most 0.79 rad — well within the linear
        regime of the sin nonlinearity. Unconditionally stable methods (ETD1,
        Crank–Nicolson) offer no benefit here because the bottleneck is the
        four-simulation budget, not stiffness.
      </p>

      <p>
        Compare this to the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-complex-ginzburg-landau-equation-1950-dissipative-phase-defects-spiral-turbulence-etd1-spectral-stage-floor-webxr"
        >
          Complex Ginzburg–Landau equation
        </Link>
        , which requires ETD1 spectral integration because the diffusion term
        ∇²A has a stiff eigenvalue spectrum that makes Euler unstable for any
        useful DT at N=128.
      </p>

      <h2>Blueprint walkthrough</h2>

      <p>
        Open <code>blueprint.py</code> in Blender 5.1&apos;s Scripting workspace
        and press <strong>Run Script</strong>.
      </p>

      <h3>Step 1 — natural frequencies</h3>

      <pre>{`u    = rng.uniform(0.0, 1.0, (N, N)).astype(np.float32)
u    = np.clip(u, 0.001, 0.999)      # avoid tan(±π/2) = ±∞
omega = kappa * np.tan(np.pi * (u - 0.5))
omega = np.clip(omega, -6*kappa, 6*kappa)  # remove heavy-tail outliers`}</pre>

      <h3>Step 2 — simulate one snapshot</h3>

      <pre>{`theta = rng.uniform(0.0, 2π, (N, N)).astype(np.float32)
for _ in range(N_STEPS):
    coupling = (sin(roll(theta,-1,1)-theta) + sin(roll(theta,+1,1)-theta) +
                sin(roll(theta,-1,0)-theta) + sin(roll(theta,+1,0)-theta))
    theta += DT * (omega + K * coupling)
return 0.5 + 0.5 * cos(theta)   # height in [0, 1]`}</pre>

      <p>
        <code>np.roll</code> with periodic wrap gives nearest-neighbour
        coupling without conditionals or explicit index arithmetic. All four
        rolls are computed in one loop body, keeping the inner loop at 5
        NumPy array operations — fast enough at N=128 in Python.
      </p>

      <h3>Step 3 — local order parameter colour</h3>

      <pre>{`# 5×5 sliding window mean of cos(θ), padded with wrap
local_mean = sliding_window_view(padded_height, (5,5)).mean((-2,-1))
order      = clip(2 * abs(local_mean - 0.5), 0, 1)
# order ≈ 0 → cobalt (incoherent),  order ≈ 1 → amber (synchronised)`}</pre>

      <p>
        <code>|cos θ|</code> averaged over a 5×5 patch estimates the local
        order parameter without computing complex exponentials. Synchronised
        regions have cos(θ) close to a constant (≈ ±1), so the mean deviates
        strongly from 0.5. Incoherent regions have cos(θ) averaging toward 0.5
        (uniform phase). The factor of 2 rescales to [0, 1].
      </p>

      <h3>Step 4 — four shape keys</h3>

      <pre>{`Basis     K=1.2 κ=0.3  near-critical; spiral defects form
SK_LowK   K=0.3 κ=0.3  subcritical; turbulent incoherence
SK_HighK  K=3.5 κ=0.3  supercritical; nearly locked, smooth ripples
SK_BroadW K=1.2 κ=1.5  wide frequency spread; K same as Basis but harder to sync`}</pre>

      <p>
        Each shape key is a completely independent simulation run, not a time
        snapshot of the same trajectory. The Basis and SK_BroadW runs use the
        same K so the viewer can directly compare the effect of frequency
        disorder on synchronisation at fixed coupling.
      </p>

      <h2>Spiral wave defects</h2>

      <p>
        Near K_c the Basis shape key shows spiral wave-fronts radiating from
        topological defect cores — points where the phase θ winds by ±2π
        around a small loop. These are the same mathematical objects as
        vortex–antivortex pairs in the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-xy-model-2d-berezinskii-kosterlitz-thouless-1971-1973-vortex-antivortex-unbinding-topological-phase-transition-height-field-stage-floor-webxr"
        >
          BKT transition
        </Link>
        , and as spiral defects in the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-fitzhugh-nagumo-1961-excitable-media-trigger-wave-spiral-height-field-stage-floor-webxr"
        >
          FitzHugh–Nagumo excitable medium
        </Link>
        . In the Kuramoto case the defects are not thermally excited but
        dynamically nucleated by the competition between local coupling (which
        wants to align neighbours) and frequency disorder (which drives them
        apart). Defects of opposite winding number attract and annihilate;
        isolated defects drift under the influence of the coupling gradient.
      </p>

      <h2>Chimera states</h2>

      <p>
        In 2002 Kuramoto and Battogtokh discovered that with nonlocal coupling
        — each oscillator coupled to all others with a kernel K(x−x&apos;) =
        (2π)⁻¹exp(−κ|x−x&apos;|) — coherent and incoherent domains can coexist
        stably in the same system. Abrams & Strogatz named these
        &ldquo;chimera states&rdquo; in their 2004 PRL paper. The nearest-neighbour
        blueprint does not produce the classic stable chimera, but the
        local-order-parameter colour map reveals transient chimera-like patches
        during the initial approach to steady state: amber (locked) islands
        surrounded by cobalt (turbulent) seas. Compare the turbulent Navier–Stokes
        inverse cascade with coherent-vortex islands in the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-2d-navier-stokes-turbulence-kraichnan-batchelor-leith-1967-inverse-cascade-pseudospectral-rk4-height-field-stage-floor-webxr"
        >
          2D NS turbulence blueprint
        </Link>
        : both show emergent spatial heterogeneity from a nominally uniform
        initial condition.
      </p>

      <h2>Shape key visual guide</h2>

      <pre>{`Basis      K=1.2 κ=0.3  swirling spirals; cobalt cores, amber arms
SK_LowK    K=0.3 κ=0.3  all cobalt; turbulent with no coherent structure
SK_HighK   K=3.5 κ=0.3  mostly amber; smooth gentle rolling undulation
SK_BroadW  K=1.2 κ=1.5  patchier than Basis; wider ω makes locking harder`}</pre>

      <h2>Troubleshooting</h2>

      <pre>{`Height field looks flat / all same colour
  → K_HIGH is so large oscillators lock within ~20 steps; increase N_STEPS
    or reduce K_HIGH to 2.5 to retain more wave structure.

Script runs slowly (>3 minutes)
  → Normal on a single CPU core. The 4 × 300-step × N² loop is 20M
    floating-point additions. On M-series Mac or modern Intel this takes
    30–90 s. Consider reducing N to 64 for a fast preview.

Spiral defects not visible in Basis
  → The RNG seed may have landed near a near-synchronised initial condition.
    Change SEED to 7 or 123; each seed produces a different spiral topology.

GLB has no morph targets in the browser
  → Verify export_morph=True in the GLB export call; Draco level > 6
    can silently strip morph data in some gltf2 exporter versions.`}</pre>

      <h2>Outside sources</h2>

      <p>
        The original paper:{" "}
        <a
          className={lk}
          href="https://doi.org/10.1007/BFb0013365"
          target="_blank"
          rel="noopener noreferrer"
        >
          Kuramoto 1975, Lecture Notes in Physics vol. 39, Springer
        </a>{" "}
        (Public Domain). Chimera states:{" "}
        <a
          className={lk}
          href="https://doi.org/10.1103/PhysRevLett.93.174102"
          target="_blank"
          rel="noopener noreferrer"
        >
          Abrams & Strogatz 2004, Phys. Rev. Lett. 93:174102
        </a>{" "}
        (Public Domain — &gt;20 years). Numerical computing provided by{" "}
        <a
          className={lk}
          href="https://github.com/numpy/numpy"
          target="_blank"
          rel="noopener noreferrer"
        >
          NumPy (BSD-3-Clause)
        </a>
        .
      </p>
    </>
  );
}

export const blenderTutorialPythonNumpyKuramoto2dPhaseOscillatorsSynchronisationSpiralWaveChimeraStageFloorWebxrEntry: Entry =
  buildInstructable({
    slug: SLUG,
    date: "2026-09-19",
    title: TITLE,
    lede: LEDE,
    tags: [
      "scripting",
      "phase-oscillators",
      "synchronisation",
      "spiral-waves",
      "chimera",
      "nonlinear-dynamics",
      "webxr",
      "stage-floor",
    ],
    body: Body,
  });
