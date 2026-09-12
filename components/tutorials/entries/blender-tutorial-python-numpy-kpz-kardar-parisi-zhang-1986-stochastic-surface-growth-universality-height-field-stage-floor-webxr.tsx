import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-kpz-kardar-parisi-zhang-1986-stochastic-surface-growth-universality-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — KPZ Equation 1986: " +
  "∂h/∂t=ν∇²h+(λ/2)|∇h|²+ση " +
  "Euler–Maruyama Stochastic Interface Growth " +
  "EW vs KPZ Universality β_KPZ≈0.24 χ_KPZ≈0.39 " +
  "128×128=16384V 16129Q " +
  "Basis(EW λ=0 t=4)/SK_KPZ(λ=2 t=4)/SK_Strong(σ=2 t=4)/SK_Long(t=20) " +
  "KPZ_Height FLOAT_COLOR Cobalt–Amber Height-Field Stage Floor WebXR (Blender 5.1)";

const LEDE =
  "Kardar, Parisi and Zhang introduced their eponymous equation in 1986 to " +
  "describe the growth of a rough interface under random deposition. " +
  "The nonlinear term (λ/2)|∇h|² — representing the fact that a tilted surface " +
  "grows faster in the direction of its slope — breaks up–down symmetry and " +
  "places the equation in a universality class distinct from the linear " +
  "Edwards–Wilkinson model. Four shape keys explore the EW baseline, the " +
  "full KPZ nonlinearity, strong noise, and long-time morphology, all " +
  "rendered as a stage floor with cobalt–amber vertex colouring.";

function Body() {
  return (
    <>
      <p>
        The KPZ equation is perhaps the most studied stochastic PDE in
        statistical physics, sitting at the intersection of interface growth,
        directed polymers, random matrices and turbulence. Its deceptively
        simple form hides a zoo of exact results in 1+1 dimensions, an open
        rigorous problem in 2+1 dimensions, and experimental confirmations in
        turbulent liquid crystals (Takeuchi &amp; Sano 2010).
      </p>

      <h2>The equation and its terms</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`∂h/∂t = ν ∇²h  +  (λ/2)|∇h|²  +  σ η(x,y,t)

ν > 0  : surface tension — penalises curvature, smooths the interface.
λ      : lateral-growth coefficient — a tilted interface element (tilt ∇h)
         has effective area (1 + |∇h|²)^{½} ≈ 1 + ½|∇h|² in the small-
         gradient limit; so material landing on it adds height at rate
         proportional to |∇h|².  This is the up–down symmetry breaker.
σ      : noise amplitude; η is spatiotemporal Gaussian white noise
         ⟨η(r,t) η(r′,t′)⟩ = δ²(r−r′) δ(t−t′).`}
      </pre>
      <p>
        Setting λ = 0 recovers the Edwards–Wilkinson (EW) equation — a linear
        Langevin model whose steady-state height correlations are Gaussian. The
        KPZ nonlinearity is relevant under the renormalisation group whenever
        the coupling g = λ²σ/(ν³) exceeds a critical value, driving the system
        to a KPZ fixed point with non-Gaussian fluctuations.
      </p>

      <h2>Universality class and scaling exponents</h2>
      <p>
        The Family–Vicsek scaling hypothesis (1985) asserts that the surface
        width W(L,t) = ⟨(h − ⟨h⟩)²⟩^(1/2) obeys:
      </p>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`W(L,t) ~ L^χ · f(t / L^z)

f(u) → u^β  as u → 0  (early time, W grows)
f(u) → const  as u → ∞  (saturated)

KPZ scaling relation:  χ + z = 2   (exact in all dimensions)

d = 1+1:  χ = 1/2, β = 1/3, z = 3/2  (exact, Kardar 1987)
d = 2+1:  χ ≈ 0.39, β ≈ 0.24, z ≈ 1.61  (numerical, Krug et al.)`}
      </pre>
      <p>
        The EW exponents are lower (β_EW ≈ 0.20 in 2+1d), so the two classes
        are distinguishable from a log-log plot of W(t) at early times — the
        subject of shape key SK_KPZ vs Basis in this blueprint.
      </p>

      <h2>Exact solution in 1+1 dimensions</h2>
      <p>
        The Hopf–Cole substitution ψ = exp(λh / 2ν) maps the 1d KPZ equation
        to the stochastic heat equation (SHE):
      </p>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`∂ψ/∂t = ν ∂²ψ/∂x²  +  (λσ/2ν) ψ η`}
      </pre>
      <p>
        The SHE is exactly solvable via Feynman–Kac. Its solution connects to
        directed polymers in random environments: ψ(x,t) is the partition
        function of a directed polymer from 0 to x in time t, with energy given
        by the noise field. The fluctuations of log ψ (= λh/2ν) follow the
        Tracy–Widom GUE distribution — the same law governing the largest
        eigenvalue of a random Gaussian unitary matrix (Prähofer &amp; Spohn
        2000).
      </p>
      <p>
        Martin Hairer&apos;s 2014 Fields Medal was awarded for his theory of
        regularity structures, which gives the first rigorous meaning to the
        KPZ equation in 1+1d as a properly renormalised stochastic PDE.
      </p>

      <h2>Numerical integration: Euler–Maruyama</h2>
      <p>
        The blueprint uses an explicit Euler–Maruyama scheme on a 128×128
        periodic grid with spatial step DX = 1.0 and time step DT = 0.02.
      </p>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`h ← h + DT · [ν ∇²h + ½λ|∇h|²]  +  σ√DT · ξ
ξ ~ N(0,1) per grid site per time step

Laplacian  (5-point stencil, periodic):
  ∇²h[i,j] = (N + E + S + W − 4C) / DX²
  via np.roll — no boundary cases needed

Gradient squared (central differences, periodic):
  ∂h/∂x = (h[i+1,j] − h[i−1,j]) / (2 DX)
  |∇h|² = (∂h/∂x)² + (∂h/∂y)²

Stability: DT ≤ DX²/(4ν) = 0.25  →  DT = 0.02 (safe factor 12.5)`}
      </pre>
      <p>
        Each of the four shape keys is generated from the same SEED = 1986, so
        the same initial flat surface h = 0 is subjected to the same random
        number stream — making visual differences attributable purely to the
        parameter change, not to different noise realisations.
      </p>

      <h2>Shape-key tour</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Basis      λ=0, σ=0.5, t=4  (200 steps)
  Edwards–Wilkinson limit. The Laplacian smooths correlated
  undulations; no sharp ridges form. This is the baseline.

SK_KPZ     λ=2, σ=0.5, t=4  (200 steps)
  Full KPZ. Ridges sharpen; the (λ/2)|∇h|² term amplifies
  existing slopes, creating asymmetric crest-trough profiles.
  Visually: compare crest width vs Basis — KPZ crests are narrower.

SK_Strong  λ=2, σ=2.0, t=4  (200 steps)
  Quadrupled noise variance. Rougher texture; the nonlinear term
  is still present but swamped by noise at early time — compare
  to SK_KPZ to see the noise-vs-nonlinearity balance.

SK_Long    λ=2, σ=0.5, t=20  (1000 steps)
  Full KPZ after 5× longer evolution. Channels deepen, lateral
  correlation length grows as ξ∥ ~ t^{1/z} ≈ t^{0.62} — the
  coarser texture of SK_Long compared to SK_KPZ is that scaling.`}
      </pre>

      <h2>Vertex attribute and material</h2>
      <p>
        The <code>KPZ_Height</code> FLOAT_COLOR attribute is set from the Basis
        (EW) height field, normalised linearly to [0,1]: cobalt (troughs) →
        amber (peaks). A MixShader blends Principled BSDF (metallic 0.30,
        roughness 0.25) with an Emission node at factor 0.35, giving a
        slightly iridescent surface that reads well in both Eevee and Cycles.
      </p>

      <h2>Studio cross-references</h2>
      <p>Other Holoflow stage floors using PDEs and statistical-physics models:</p>
      <ul className="list-disc pl-5 space-y-1">
        <li>
          <Link href="/tutorials/blender-tutorial-python-numpy-allen-cahn-phase-field-mean-curvature-motion-allen-cahn-1979-stage-floor-webxr" className={lk}>
            Allen–Cahn phase field — non-conserved interface motion
          </Link>{" "}
          — the deterministic cousin of KPZ: no noise term, purely curvature-driven.
        </li>
        <li>
          <Link href="/tutorials/blender-tutorial-python-numpy-cahn-hilliard-phase-field-spinodal-decomposition-ostwald-ripening-stage-floor-webxr" className={lk}>
            Cahn–Hilliard spinodal decomposition
          </Link>{" "}
          — conserved order parameter; Ostwald ripening obeys ⟨L⟩ ~ t^{1/3}.
        </li>
        <li>
          <Link href="/tutorials/blender-tutorial-python-numpy-swift-hohenberg-pde-hexagonal-rolls-benard-convection-stage-floor-webxr" className={lk}>
            Swift–Hohenberg — Bénard convection rolls and hexagons
          </Link>{" "}
          — deterministic pattern-forming PDE; contrast with KPZ&apos;s stochastic roughness.
        </li>
        <li>
          <Link href="/tutorials/blender-tutorial-python-numpy-ising-model-metropolis-monte-carlo-phase-transition-critical-height-field-webxr" className={lk}>
            Ising model — Metropolis Monte Carlo phase transition
          </Link>{" "}
          — another statistical-physics height field; critical fluctuations vs. KPZ scaling.
        </li>
        <li>
          <Link href="/tutorials/blender-tutorial-python-numpy-complex-ginzburg-landau-pde-spiral-turbulence-benjamin-feir-defect-height-field-stage-floor-webxr" className={lk}>
            Complex Ginzburg–Landau — spiral turbulence and phase defects
          </Link>{" "}
          — driven dissipative PDE; compare its ordered-vs-chaotic phases to KPZ universality.
        </li>
      </ul>

      <h2>Outside sources</h2>
      <ul className="list-disc pl-5 space-y-1">
        <li>
          Kardar M, Parisi G, Zhang Y-C (1986){" "}
          <a href="https://doi.org/10.1103/PhysRevLett.56.889" className={lk} target="_blank" rel="noopener noreferrer">
            Dynamic scaling of growing interfaces. PRL 56(9):889
          </a>{" "}
          — original KPZ paper; mathematical content PD (&gt;35 yr). Related: Edwards–Wilkinson 1982.
        </li>
        <li>
          Edwards SF, Wilkinson DR (1982){" "}
          <a href="https://doi.org/10.1098/rspa.1982.0056" className={lk} target="_blank" rel="noopener noreferrer">
            The surface statistics of a granular aggregate. Proc R Soc Lond A 381:17
          </a>{" "}
          — linear baseline (EW equation); equations PD (&gt;40 yr). Related: Family–Vicsek scaling 1985.
        </li>
        <li>
          NumPy contributors —{" "}
          <a href="https://numpy.org/doc/stable/user/" className={lk} target="_blank" rel="noopener noreferrer">
            NumPy User Guide
          </a>{" "}
          (BSD-3-Clause). Related: SciPy (BSD-3-Clause), CuPy (MIT).
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
    "stochastic",
    "pde",
    "surface-growth",
    "statistical-physics",
    "height-field",
    "webxr",
  ],
  libraryPath: `blends/scripting/${SLUG.replace("blender-tutorial-", "")}/`,
});
