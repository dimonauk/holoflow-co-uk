import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-burgers-equation-1948-cole-hopf-exact-" +
  "shock-formation-viscous-regularisation-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — Burgers Equation (1948): " +
  "u_t + u u_x = ν u_xx " +
  "Cole-Hopf Exact Solution φ̂(k,t)=φ̂₀(k)·exp(−νk²t) " +
  "Shock Formation t_shock=1/π≈0.318 Rankine-Hugoniot s=0 " +
  "δ≈4ν/|Δu| Viscous Shock Width " +
  "128×128=16384V 16129Q " +
  "Basis(ν=0.010)/SK_HighNu(ν=0.100)/SK_LowNu(ν=0.005)/SK_NWave(−sin2πx) " +
  "Burgers_Vel FLOAT_COLOR Cobalt–Teal–Amber Space-Time Height-Field Stage Floor WebXR (Blender 5.1)";

const LEDE =
  "Burgers wrote down his equation in 1948 as the simplest model that combines " +
  "nonlinear wave steepening with viscous diffusion. " +
  "The extraordinary insight of Hopf and Cole, independently in 1950 and 1951, " +
  "was that a single substitution — u = −2ν ∂ ln φ/∂x — converts it exactly to the " +
  "heat equation, making it the first nonlinear PDE to be solved analytically for " +
  "arbitrary initial data. " +
  "This blueprint computes the exact Fourier solution and lays the space-time " +
  "diagram flat as a stage floor: space runs along the x-axis, time forward " +
  "along the y-axis, and velocity rises as height — so the shock front appears " +
  "as a sharp ridge that steepens with time before stabilising at finite viscous width.";

function Body() {
  return (
    <>
      <p>
        The Burgers equation balances two competing effects in a single term each.
        The nonlinear u&nbsp;∂u/∂x tends to steepen gradients: fluid elements moving
        faster catch up to slower ones, compressing the wave until it would break.
        The viscous ν&nbsp;∂²u/∂x² opposes that steepening: diffusion spreads
        whatever gradient forms. The competition produces a travelling shock layer
        of finite width — a feature that appears in gas dynamics, traffic flow,
        cosmological large-scale structure, and one-dimensional turbulence.
      </p>

      <h2>The Cole-Hopf transformation</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Burgers equation:      u_t + u u_x = ν u_xx

Substitution:          u = −2ν ∂ ln φ/∂x  =  −2ν φ_x / φ

Transformed equation:  φ_t = ν φ_xx        (heat equation — linear!)

Initial data:
  θ(x) = ∫u₀ dξ             (antiderivative; spectral: θ̂ = û₀/(ik))
  φ₀(x) = exp(−θ(x)/(2ν))   (Cole-Hopf initial condition)

Exact solution in Fourier space:
  φ̂(k,t) = φ̂₀(k) · exp(−νk²t)   (heat kernel — no time-stepping needed)

Recovery:
  u(x,t) = −2ν · IFFT(ik · φ̂(k,t)) / IFFT(φ̂(k,t))`}
      </pre>
      <p>
        The transformation is remarkable precisely because it is lossless:
        every solution of Burgers, including shocks, is captured exactly.
        There is no approximation, no stability criterion, and no accumulated
        round-off error from repeated time-stepping.
      </p>

      <h2>Shock formation and the Rankine-Hugoniot condition</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Initial condition:  u₀ = −sin(πx)  on x ∈ [−1, 1]  (periodic)

Shock time (inviscid, from method of characteristics):
  t_shock = 1 / max|∂u₀/∂x| = 1 / π ≈ 0.318  (at x = 0)

Rankine-Hugoniot jump condition:
  shock speed s = (u⁺ + u⁻) / 2

For u₀ = −sin(πx):  u⁺ = +1, u⁻ = −1  →  s = 0  (stationary shock)

Viscous shock width (balance between steepening and diffusion):
  δ ≈ 4ν / |u⁺ − u⁻|  =  2ν

  ν = 0.100  →  δ ≈ 0.20  (diffusion-dominated, no visible shock)
  ν = 0.010  →  δ ≈ 0.02  (moderate shock, several mesh cells wide)
  ν = 0.005  →  δ ≈ 0.01  (near-inviscid, near-vertical ridge)`}
      </pre>
      <p>
        On the floor, the shock appears as the near-vertical ridge at x&nbsp;=&nbsp;0
        that forms around y&nbsp;=&nbsp;0.318 (about one-fifth of the way along the
        y-axis) and persists through t&nbsp;=&nbsp;1.5.
        The ridge is stationary because the jump is symmetric: u⁺ = −u⁻.
      </p>

      <h2>Numerical precision of the exact method</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Grid:  N_X = 128 points on L = 2 (periodic)
       k_Nyquist = π N_X / L = 201 rad/unit
       dx = L / N_X = 0.015625 m

No stability criterion — the heat kernel damps all wavenumbers for ν > 0.
The only source of error is spatial aliasing of φ₀ = exp(−θ/(2ν)).

For small ν (ν = 0.005):  max|θ/(2ν)| = 1/(π·0.005) ≈ 63.7
  →  φ₀(0) ≈ exp(−63.7) ≈ 4×10⁻²⁸  (well within float64 range ≥ 10⁻³⁰⁸)

Blueprint subtracts θ.mean() before taking exp to keep φ₀ near 1,
then recovers the correct u via the logarithmic derivative u = −2ν φ_x/φ.`}
      </pre>

      <h2>Shape keys</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Basis     u₀=−sin(πx)   ν=0.010  moderate shock, δ≈0.020
SK_HighNu u₀=−sin(πx)   ν=0.100  over-damped: profile diffuses before shock
SK_LowNu  u₀=−sin(πx)   ν=0.005  sharp shock layer, δ≈0.010
SK_NWave  u₀=−sin(2πx)  ν=0.010  N-wave: two simultaneous shocks`}
      </pre>
      <p>
        Blending between Basis and SK_HighNu in the shape-key panel shows
        the smooth transition from shock-forming to diffusion-dominated
        regimes — equivalent to increasing the Reynolds number in reverse.
        SK_NWave demonstrates that the Cole-Hopf method handles multiple
        simultaneous shocks without any modification.
      </p>

      <h2>Colour map</h2>
      <p>
        The <code>Burgers_Vel</code> FLOAT_COLOR attribute uses a signed
        cobalt–teal–amber map: cobalt (u&nbsp;&lt;&nbsp;0, leftward flow),
        dark teal (u&nbsp;=&nbsp;0, stagnation), amber (u&nbsp;&gt;&nbsp;0,
        rightward flow). The shock at x&nbsp;=&nbsp;0 appears as a sharp
        transition from amber to cobalt — the visual marker of the jump
        discontinuity that viscosity regularises into a thin layer.
      </p>

      <h2>Studio cross-references</h2>
      <ul className="list-disc pl-5 space-y-1">
        <li>
          <Link
            href="/tutorials/blender-tutorial-python-numpy-kpz-kardar-parisi-zhang-1986-stochastic-surface-growth-universality-height-field-stage-floor-webxr"
            className={lk}
          >
            KPZ equation 1986 — stochastic interface growth
          </Link>{" "}
          — the 1D KPZ equation ∂h/∂t = ν∂²h/∂x² + (λ/2)(∂h/∂x)² + η maps
          exactly to Burgers via u = ∂h/∂x, then to the stochastic heat equation
          via Cole-Hopf: the same substitution that solves Burgers analytically
          converts KPZ to a linear equation driven by white noise.
        </li>
        <li>
          <Link
            href="/tutorials/blender-tutorial-python-numpy-korteweg-de-vries-1895-soliton-collision-pseudospectral-rk4-space-time-height-field-stage-floor-webxr"
            className={lk}
          >
            KdV equation 1895 — soliton collisions
          </Link>{" "}
          — another 1D space-time floor where the wave evolution is visible as
          height; contrast the KdV&apos;s dispersive solitons (ridges that pass
          through each other intact) with Burgers&apos; dissipative shocks (a
          ridge that forms irreversibly and persists).
        </li>
        <li>
          <Link
            href="/tutorials/blender-tutorial-python-numpy-kuramoto-sivashinsky-pde-spatiotemporal-chaos-flame-front-height-field-stage-floor-webxr"
            className={lk}
          >
            Kuramoto–Sivashinsky — spatiotemporal chaos
          </Link>{" "}
          — the KS equation contains Burgers&apos; nonlinear term (u&nbsp;u_x) plus a
          destabilising fourth-order term that prevents the shock from ever
          settling; where Burgers produces a clean stationary front, KS produces
          chaos.
        </li>
        <li>
          <Link
            href="/tutorials/blender-tutorial-python-numpy-allen-cahn-phase-field-mean-curvature-motion-allen-cahn-1979-stage-floor-webxr"
            className={lk}
          >
            Allen–Cahn phase field — mean-curvature motion
          </Link>{" "}
          — another equation whose solution involves an interface layer of finite
          width controlled by a diffusion coefficient; the Allen-Cahn interface
          width scales as √(κ/α), analogous to the Burgers shock width δ ≈ 4ν/|Δu|.
        </li>
      </ul>

      <h2>Outside sources</h2>
      <ul className="list-disc pl-5 space-y-1">
        <li>
          Burgers J M (1948){" "}
          <a
            href="https://doi.org/10.1016/S0065-2156(08)70100-5"
            className={lk}
            target="_blank"
            rel="noopener noreferrer"
          >
            A mathematical model illustrating the theory of turbulence.{" "}
            <em>Advances in Applied Mechanics</em> 1:171–199
          </a>{" "}
          — original derivation; equations are public domain.
          Burgers also introduced the model to describe turbulent channel flow;
          the one-dimensional version analysed here was identified as the minimal
          nonlinear wave equation.
        </li>
        <li>
          Hopf E (1950){" "}
          <a
            href="https://doi.org/10.1002/cpa.3160030302"
            className={lk}
            target="_blank"
            rel="noopener noreferrer"
          >
            The partial differential equation u_t + u&thinsp;u_x = μ&thinsp;u_xx.{" "}
            <em>Communications on Pure and Applied Mathematics</em> 3:201–230
          </a>{" "}
          — first publication of the Cole-Hopf linearisation; equations PD.
          Cole J D (1951){" "}
          <a
            href="https://doi.org/10.1090/qam/42889"
            className={lk}
            target="_blank"
            rel="noopener noreferrer"
          >
            On a quasi-linear parabolic equation occurring in aerodynamics.{" "}
            <em>Quarterly of Applied Mathematics</em> 9:225–236
          </a>{" "}
          — independent simultaneous discovery; both equations PD.
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
          (BSD-3-Clause). The <code>np.fft</code> module provides the FFT used
          for spectral integration and heat-kernel propagation.
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
    "burgers-equation",
    "cole-hopf",
    "shock-formation",
    "exact-solution",
    "height-field",
    "webxr",
  ],
  libraryPath: `blends/scripting/python-numpy-burgers-equation-1948-cole-hopf-exact-shock-formation-viscous-regularisation-height-field-stage-floor-webxr/`,
});
