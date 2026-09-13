import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-fisher-kpp-1937-kolmogorov-petrovsky-piskunov-" +
  "pulled-wave-bistable-allee-etd1-spectral-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — Fisher-KPP 1937 Kolmogorov–Petrovsky–Piskunov " +
  "∂u/∂t=D∇²u+ru(1−u) " +
  "ETD1 Spectral Cox-Matthews 2002 Unconditionally Stable dt=0.10 " +
  "Pulled Wave c*=2√(Dr) Bistable Allee θ=0.30 " +
  "128×128=16384V 16129Q " +
  "Basis(D=0.5 r=1.0 t=30)/SK_FastR(r=2.0)/SK_LowD(D=0.1)/SK_Bistable(θ=0.30) " +
  "Fisher_U FLOAT_COLOR Cobalt–Amber " +
  "Height-Field Stage Floor WebXR (Blender 5.1)";

const LEDE =
  "Ronald Fisher introduced this deceptively simple reaction-diffusion equation " +
  "in 1937 to model the geographic spread of a gene with selective advantage. " +
  "The same year, Kolmogorov, Petrovsky and Piskunov proved its central theorem: " +
  "any initial perturbation with compact support evolves into a travelling wave " +
  "whose speed converges to the minimum c* = 2√(Dr) — the 'pulled' speed, " +
  "driven entirely by the unstable u = 0 tip. " +
  "Adding the Allee factor (u − θ) flips the tip to stable, " +
  "producing a 'pushed' wave that only propagates from a large enough nucleus. " +
  "This blueprint solves both regimes on a 128 × 128 grid with ETD1 Fourier " +
  "spectral time-stepping, maps density onto a cobalt-to-amber height field, " +
  "and exports four wave regimes as WebXR GLTF morph targets.";

function Body() {
  return (
    <>
      <p>
        The Fisher-KPP equation sits at the intersection of three fields: population
        genetics (Fisher), rigorous PDE analysis (Kolmogorov et al.), and nonlinear
        wave theory. It is the simplest scalar reaction-diffusion equation that
        produces a genuine travelling wave with a well-defined minimum speed — making
        it the canonical testbed for front-propagation theory and the starting point
        for almost every spatial ecology or epidemic model written since.
      </p>

      <h2>The PDEs</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Monostable (KPP):
  ∂u/∂t = D ∇²u  +  r · u(1 − u)

Bistable (Allee effect):
  ∂u/∂t = D ∇²u  +  r · u(1 − u)(u − θ)     0 < θ < 0.5

State space:
  u = 0   unstable in KPP   |  stable in bistable (f ′(0) = −r·θ < 0)
  u = 1   stable in both
  u = θ   —                 |  unstable saddle in bistable`}
      </pre>
      <p>
        The monostable form has a logistic reaction term: growth is maximal at
        small <em>u</em> and self-limits to the carrying capacity <em>u = 1</em>.
        The bistable form multiplies by <em>(u − θ)</em>, which is negative for
        small <em>u</em> — any population below the Allee threshold is driven to
        extinction rather than growth.
      </p>

      <h2>The pulled-wave theorem</h2>
      <p>
        Linearise the KPP equation around <em>u = 0</em>: the perturbation grows
        like <em>{"e^{r·t}"}</em>. An exponential front{" "}
        <em>{"u ~ e^{-λ(x − ct)}"}</em> is consistent if
      </p>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Dispersion relation:  c = D λ + r/λ
Minimise over λ:       dc/dλ = D − r/λ² = 0  →  λ* = √(r/D)
Minimum speed:         c* = 2√(D r)`}
      </pre>
      <p>
        The remarkable fact — proved by KPP 1937 — is that this minimum speed
        is <em>selected</em> for any compactly supported initial condition.
        The front does not run at the maximum possible speed; it runs at the
        minimum. This is the <strong>pulled</strong> mechanism: the tip region,
        where <em>u</em> is exponentially small, races ahead and the bulk is
        "pulled" behind it.
      </p>

      <h2>Bistable / pushed wave</h2>
      <p>
        With the Allee factor, <em>u = 0</em> becomes locally stable. Small
        perturbations decay. Only an initial colony large enough to exceed the
        Allee threshold <em>θ</em> can generate a propagating front — the
        "pushed" wave, whose speed depends on the nonlinear dynamics of the
        interior rather than the linearised tip.
      </p>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`f(u) = r · u(1−u)(u−θ)
f ′(0) = −r·θ < 0    → u=0 stable (extinction below threshold)
f ′(θ) = r·θ(1−θ) > 0 → u=θ unstable (Allee saddle)
f ′(1) = −r(1−θ) < 0   → u=1 stable (carrying capacity)`}
      </pre>

      <h2>ETD1 spectral time-stepping</h2>
      <p>
        We split the right-hand side at the linearised reaction rate:
      </p>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Monostable split:
  L̂_k = −D k²  +  r         (linear — diffusion + linearised growth)
  N(u)  = −r u²              (nonlinear — purely quadratic)

Bistable split (f ′(0) = −r θ):
  L̂_k = −D k²  −  r θ       (linear — diffusion + linearised decay)
  N(u)  = r u²(1 + θ − u)   (nonlinear — shifted cubic)

ETD1 update:
  û(t+Δt) = e^{L̂ Δt} û(t)  +  φ₁(L̂ Δt) · N̂(u(t)) · Δt
  φ₁(z)   = (eᶻ − 1) / z   (→ 1 as z → 0 — Taylor branch for safety)`}
      </pre>
      <p>
        Absorbing the linear part into the exponential propagator makes the
        scheme <em>unconditionally stable</em> for diffusion — no CFL condition
        on Δt. The quadratic nonlinear part adds only a mild constraint
        Δt · r ≪ 1; with r = 2 and Δt = 0.10 we have 0.20 ≪ 1 ✓.
        <br />
        The φ₁ formula is numerically dangerous near z = 0 (cancellation of
        two large numbers), so the code uses{" "}
        <code>np.expm1(z) / z</code> with a Taylor branch at{" "}
        <code>|z| &lt; 1e-10</code>.
      </p>

      <h2>Shape key regimes</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Basis      D=0.5  r=1.0  t=30   c* ≈ 1.41 px/tu  ring radius ≈ 42 px
SK_FastR   D=0.5  r=2.0  t=20   c* ≈ 2.00 px/tu  ring radius ≈ 40 px
SK_LowD    D=0.1  r=1.0  t=60   c* ≈ 0.63 px/tu  ring radius ≈ 38 px
SK_Bistable D=0.5 r=1.0  θ=0.30 t=60  pushed wave from peak IC=0.80 > θ`}
      </pre>
      <p>
        All four regimes start from a Gaussian nucleus centred at (0.5, 0.5)
        in the unit square, with periodic boundary conditions. The Basis, FastR,
        and LowD runs produce expanding concentric rings. The Bistable run
        produces a similar ring but with a sharper interior transition and
        a characteristic flat plateau where <em>u ≈ 1</em> behind the front.
      </p>

      <h2>Failure modes and remedies</h2>
      <ul className="list-disc space-y-1 pl-5">
        <li>
          <strong>u exceeds 1 or goes negative</strong>: the nonlinear step is
          first-order accurate in Δt. Add{" "}
          <code>np.clip(u, 0, 1)</code> after each step (already in blueprint).
        </li>
        <li>
          <strong>Bistable wave doesn't move</strong>: IC peak must exceed θ.
          The blueprint uses <code>amp=0.80 &gt; θ=0.30</code>; if you change
          θ above 0.80, increase amp accordingly.
        </li>
        <li>
          <strong>Ring wraps across periodic boundaries</strong>: expected once
          c* · t ≳ N/2. Run to smaller t or increase N.
        </li>
        <li>
          <strong>Bistable ring shrinks instead of expanding</strong>: the
          pushed wave speed can be negative for small θ or large D. Increase
          the initial nucleus radius (reduce <code>spread</code> in the IC).
        </li>
      </ul>

      <h2>Studio connections</h2>
      <p>
        The wavefront topology — a sharp interface between two stable states — is
        closely related to the phase-field models in the library:
      </p>
      <ul className="list-disc space-y-1 pl-5">
        <li>
          <Link href="/tutorials/blender-tutorial-python-numpy-allen-cahn-phase-field-mean-curvature-motion-allen-cahn-1979-stage-floor-webxr" className={lk}>
            Allen–Cahn phase field
          </Link>{" "}
          — also a bistable scalar PDE; Allen-Cahn drives interface motion by
          mean curvature, while bistable FKPP adds the propagation speed.
        </li>
        <li>
          <Link href="/tutorials/blender-tutorial-python-numpy-fitzhugh-nagumo-1961-excitable-media-trigger-wave-spiral-height-field-stage-floor-webxr" className={lk}>
            FitzHugh–Nagumo excitable media
          </Link>{" "}
          — two-component version; the inhibitor prevents re-excitation,
          giving spiral rather than expanding ring waves.
        </li>
        <li>
          <Link href="/tutorials/blender-tutorial-python-numpy-schnakenberg-1979-activator-substrate-turing-instability-spots-stripes-height-field-stage-floor-webxr" className={lk}>
            Schnakenberg Turing patterns
          </Link>{" "}
          — also a two-component RD system, but the instability is spatial
          (Turing) rather than a wavefront.
        </li>
        <li>
          <Link href="/tutorials/blender-tutorial-python-numpy-gierer-meinhardt-activator-inhibitor-turing-morphogenesis-1972-spot-stripe-height-field-stage-floor-webxr" className={lk}>
            Gierer–Meinhardt morphogenesis
          </Link>{" "}
          — the activator-inhibitor archetype; Turing instability from
          short-range activation / long-range inhibition.
        </li>
        <li>
          <Link href="/tutorials/blender-tutorial-shape-keys-morph-targets" className={lk}>
            Shape keys / morph targets
          </Link>{" "}
          — the four wavefront regimes are stored as GLTF morph targets for
          real-time blending in WebXR.
        </li>
      </ul>

      <h2>Outside sources</h2>
      <ul className="list-disc space-y-1 pl-5">
        <li>
          <a
            href="https://doi.org/10.1111/j.1469-1809.1937.tb02153.x"
            className={lk}
            target="_blank"
            rel="noopener noreferrer"
          >
            Fisher R A (1937) — The wave of advance of advantageous genes —{" "}
            <em>Ann. Eugenics</em> 7(4):355–369
          </a>{" "}
          — Public Domain. Introduced the equation; gene-frequency interpretation;
          first travelling-wave solution. Related:{" "}
          <a href="https://github.com/numpy/numpy" className={lk} target="_blank" rel="noopener noreferrer">numpy (BSD-3)</a>.
        </li>
        <li>
          Kolmogorov A N, Petrovsky I G, Piskunov N S (1937) — A study of the
          diffusion equation with increase in the amount of substance, and its
          application to a biological problem —{" "}
          <em>Bull. Univ. Moscow Ser. Int. A</em> 1(6):1–25. — Public Domain.
          Proved existence of travelling waves and the minimum-speed selection
          theorem. Related:{" "}
          <a href="https://github.com/scipy/scipy" className={lk} target="_blank" rel="noopener noreferrer">scipy (BSD-3)</a>.
        </li>
        <li>
          <a
            href="https://doi.org/10.1006/jcph.2002.6995"
            className={lk}
            target="_blank"
            rel="noopener noreferrer"
          >
            Cox S M, Matthews P C (2002) — Exponential time differencing for
            stiff systems — <em>J. Comput. Phys.</em> 176(2):430–455
          </a>{" "}
          — Public Domain. ETD1 and ETD2RK schemes used throughout the library.
          Related:{" "}
          <a href="https://github.com/numpy/numpy" className={lk} target="_blank" rel="noopener noreferrer">numpy (BSD-3)</a>.
        </li>
      </ul>
    </>
  );
}

const entry: Entry = buildInstructable({
  slug: SLUG,
  title: TITLE,
  lede: LEDE,
  date: "2026-09-13",
  tags: [
    "blender",
    "python",
    "numpy",
    "reaction-diffusion",
    "fisher-kpp",
    "pde",
    "wavefront",
    "bistable",
    "stage-floor",
    "webxr",
    "scripting",
  ],
  body: Body,
  externalLinks: [
    {
      label: "Fisher 1937 — Ann. Eugenics (doi)",
      url: "https://doi.org/10.1111/j.1469-1809.1937.tb02153.x",
    },
    {
      label: "KPP 1937 — Moscow Bull. (Semantic Scholar)",
      url: "https://www.semanticscholar.org/paper/Study-of-the-Diffusion-Equation-with-Growth-of-the-Kolmogorov-Petrovsky/6b88b41b6fd5e7aaafb45fa17a46b5e48b3c0e1",
    },
    {
      label: "Cox & Matthews 2002 — J. Comput. Phys. (doi)",
      url: "https://doi.org/10.1006/jcph.2002.6995",
    },
  ],
});

export const blenderTutorialPythonNumpyFisherKpp1937KolmogorovPetrovskyPiskunovPulledWaveBistableAlleeEtd1SpectralHeightFieldStageFloorWebxrEntry =
  entry;
export default entry;
