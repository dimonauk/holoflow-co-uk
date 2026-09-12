import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-kadomtsev-petviashvili-kp-ii-1970-" +
  "exact-web-soliton-hirota-tau-stage-floor-webxr";

const TITLE =
  "Python numpy — KP-II (Kadomtsev–Petviashvili 1970): " +
  "∂/∂x(u_t + 6u u_x + u_xxx) + 3u_yy = 0 " +
  "Exact N-Soliton Hirota τ-Function " +
  "Dispersion ω=k³+3l²/k A_ij=[(kᵢ−kⱼ)²+3Δv²]/[(kᵢ+kⱼ)²+3Δv²] " +
  "128×128=16384V 16129Q " +
  "Basis(2-soliton t=0)/SK_YJunction(resonant Mach-stem)/SK_Web4(4-soliton Gr(2,4))/SK_Temporal(t=8) " +
  "KP_Height FLOAT_COLOR Cobalt–Amber Height-Field Stage Floor WebXR (Blender 5.1)";

const LEDE =
  "Kadomtsev and Petviashvili derived their equation in 1970 to study whether " +
  "KdV solitons remain stable once allowed to spread sideways. " +
  "The answer for KP-II (positive y-Laplacian) is yes — and the new equation " +
  "introduces a richer family of exact solutions: two solitons can meet at a " +
  "resonant angle and fuse into a Y-shaped junction, whilst four solitons can " +
  "tile the plane with a rectangular web. " +
  "This blueprint computes every shape key from the exact Hirota τ-function " +
  "rather than from a numerical integration, so there is no truncation error — " +
  "the mesh is a precise analytic surface rendered in Blender.";

function Body() {
  return (
    <>
      <p>
        The KP-II equation sits at the top of a hierarchy of integrable wave models.
        KdV describes waves on a line; KP-II describes nearly-unidirectional waves on a
        plane. The extra term <code>+3 u_yy</code> acts like weak transverse dispersion,
        and its positive sign is exactly what makes line solitons transversely stable —
        the defining property that separates KP-II from KP-I (which has lump solitons
        instead of line solitons).
      </p>

      <h2>The equation and its dispersion relation</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`KP-II:  ∂/∂x [ u_t + 6u u_x + u_xxx ] + 3 u_yy = 0

1-soliton:  u(x,y,t) = (k²/2) sech²(½ η)
            η = k·x + l·y − ω·t + φ₀
Dispersion: ω = k³ + 3l²/k        (KP-II, + sign)

Amplitude: A = k²/2              speed in x: v_x = k² + 3l²/k²
Direction: the crest line is  k·x + l·y = const
           slope in xy-plane: dy/dx = −k/l`}
      </pre>
      <p>
        Note the dispersion relation <em>ω = k³ + 3l²/k</em> reduces to the KdV
        relation <em>ω = k³</em> when <em>l = 0</em>. The <em>3l²/k</em> term
        is the cost of running at an angle to the x-axis: a tilted soliton runs faster
        than a straight one of the same x-wavenumber.
      </p>

      <h2>The Hirota τ-function</h2>
      <p>
        Set <code>u = 2 ∂²_x log τ</code>. The bilinear KP-II equation for τ then
        admits an exact N-soliton solution as a polynomial in exponentials:
      </p>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`τ = Σ_{S ⊆ [N]}  A(S) · exp( Σ_{i ∈ S} η_i )

A(∅)  = 1                                    (constant term)
A({i}) = 1                                   (single soliton)
A(S)  = ∏_{i < j, i,j ∈ S} A_ij            (all pairwise products)

Hirota interaction factor for KP-II:
A_ij = [(kᵢ−kⱼ)² + 3(lᵢ/kᵢ − lⱼ/kⱼ)²]
      /[(kᵢ+kⱼ)² + 3(lᵢ/kᵢ − lⱼ/kⱼ)²]
  ∈ (0, 1]  for all real kᵢ,kⱼ > 0     (KP-II is always repulsive)

Stable quotient formula (avoids log of near-zero τ):
u = 2 (τ · τ_xx − τ_x²) / τ²`}
      </pre>
      <p>
        For <em>N = 2</em> solitons the sum has 2² = 4 terms; for <em>N = 4</em>
        it has 16 terms — all computed in NumPy in a single vectorised loop over the
        128 × 128 grid with no time-stepping at all. The computational cost is
        O(2^N · N²) per grid point, which is negligible for N ≤ 4.
      </p>

      <h2>Resonance and the Y-junction (Mach stem)</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Two solitons (k,l) and (k,−l) form a Mach-stem when:
  ω₁ + ω₂ = ω₃      (frequencies add)
  k₁ + k₂ = k₃      (k adds)
  l₁ + l₂ = l₃      (l adds → l₃ = 0, horizontal stem)

  2(k³ + 3l²/k) = (2k)³  ⟺  6l²/k = 6k²  ⟺  l = k²

Choosing k = 1, l = 1:  ω₁ = ω₂ = 4,  ω₃ = 8  ✓
Interaction factor: A₁₂ = (0 + 3·4)/(4 + 3·4) = 12/16 = 3/4

The τ-function τ = 1 + e^{η₁} + e^{η₂} + (3/4) e^{η₁+η₂}
contains a hidden third soliton in the  (3/4)e^{η₁+η₂}  term:
  η₁ + η₂ = 2kx + 0·y − 8t + φ₁+φ₂  ≡  η₃ for k₃=2, l₃=0`}
      </pre>
      <p>
        This is the key insight of the resonance: the Hirota cross-term
        <em> A₁₂ exp(η₁ + η₂)</em> is itself a soliton when the resonance condition
        holds, because its phase profile matches that of a third KP-II soliton
        exactly. The junction at the origin is where all three solitons coexist at
        equal amplitude — a single point in space-time that acts as the vertex of a Y.
      </p>

      <h2>4-soliton web pattern (Grassmannian structure)</h2>
      <p>
        Kodama and Williams (2011) classified all KP-II web solitons using totally
        non-negative Grassmannians Gr(M, N)≥0. The simplest non-trivial web is the
        <strong> Gr(2, 4) box type</strong>: two resonant pairs whose stems cross at
        right angles, tiling the plane with rectangular cells. Shape key
        <code>SK_Web4</code> uses two pairs:
      </p>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Pair A:  (k=1.0, l=+0.8)  and  (k=1.0, l=−0.8)
Pair B:  (k=0.8, l=+0.64) and  (k=0.8, l=−0.64)
Each pair satisfies l = k² resonance ✓
Together they produce a rectangular lattice of amplitude peaks.`}
      </pre>

      <h2>Bench steps (Blender 5.1)</h2>
      <ol className="list-decimal list-inside space-y-1">
        <li>Open the <strong>Scripting</strong> workspace.</li>
        <li>
          Load <code>blueprint.py</code> and run it (<kbd>Alt+P</kbd> or the ▶ button).
          The script creates the mesh, all four shape keys, and saves{" "}
          <code>kp_ii_web_soliton_floor.blend</code> + <code>.glb</code>.
        </li>
        <li>
          Switch to the <strong>3D Viewport</strong>. In the Properties sidebar
          (N-panel → Item) open <em>Shape Keys</em> and drag each key&apos;s
          Value slider to see the transitions.
        </li>
        <li>
          In Material Preview (<kbd>Z</kbd> → Material Preview), the Cobalt–Amber
          colour ramp driven by <code>KP_Height</code> is visible on the mesh.
        </li>
        <li>
          To record: load <code>record.py</code>, set the output path, and run.
          EEVEE-Next renders the 90-frame animation to <code>viewport.mp4</code>.
        </li>
      </ol>

      <h2>Troubleshooting</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Flat mesh / all zeros:
  → Check that u_arr.max() > 0 after _kp_u().  If all η_i are out-of-range
    after clipping, the solitons lie outside the domain.  Reduce phi0 values
    or enlarge WORLD_SCALE.

Crest missing in SK_YJunction:
  → The Y-junction vertex is at origin (0,0) only if phi0=0 for both solitons.
    Shift phases to centre the junction as needed.

export_scene.gltf attribute error:
  → Blender 5.1 requires export_attributes=True in the gltf operator call.
    Ensure holoflow_webxr_exporter add-on is enabled for Draco + WebP support.`}
      </pre>

      <h2>External sources</h2>
      <ul className="space-y-1">
        <li>
          <a
            href="https://doi.org/10.1103/PhysRevLett.27.1192"
            target="_blank"
            rel="noopener noreferrer"
            className={lk}
          >
            Hirota R 1971 — Exact solution for multiple soliton collisions (Phys. Rev. Lett.)
          </a>{" "}
          — public domain (&gt;50 yr). Bilinear τ-function and interaction coefficients.
        </li>
        <li>
          <a
            href="https://arxiv.org/abs/1108.4984"
            target="_blank"
            rel="noopener noreferrer"
            className={lk}
          >
            Kodama Y &amp; Williams LK 2011 — KP solitons and total positivity (arXiv)
          </a>{" "}
          — equations public domain. Grassmannian classification of all web-soliton types.
          Related repo:{" "}
          <a
            href="https://github.com/sagemath/sage"
            target="_blank"
            rel="noopener noreferrer"
            className={lk}
          >
            SageMath (Apache-2.0)
          </a>{" "}
          implements combinatorial Grassmannian data used in this classification.
        </li>
      </ul>

      <h2>Cross-references</h2>
      <ul className="space-y-1">
        <li>
          <Link
            href="/tutorials/blender-tutorial-python-numpy-korteweg-de-vries-1895-soliton-collision-pseudospectral-rk4-space-time-height-field-stage-floor-webxr"
            className={lk}
          >
            KdV pseudospectral stage floor
          </Link>{" "}
          — parent 1D equation; compare KdV soliton collisions to KP-II resonance.
        </li>
        <li>
          <Link
            href="/tutorials/blender-tutorial-python-numpy-complex-ginzburg-landau-pde-spiral-turbulence-benjamin-feir-defect-height-field-stage-floor-webxr"
            className={lk}
          >
            Complex Ginzburg–Landau stage floor
          </Link>{" "}
          — another 2D wave PDE as a height field; contrast integrable vs dissipative.
        </li>
        <li>
          <Link
            href="/tutorials/blender-tutorial-python-numpy-cahn-hilliard-phase-field-spinodal-decomposition-ostwald-ripening-stage-floor-webxr"
            className={lk}
          >
            Cahn–Hilliard spinodal decomposition
          </Link>{" "}
          — FFT semi-implicit height-field technique; compare with exact τ-function approach.
        </li>
        <li>
          <Link
            href="/tutorials/blender-tutorial-python-numpy-kpz-kardar-parisi-zhang-1986-stochastic-surface-growth-universality-height-field-stage-floor-webxr"
            className={lk}
          >
            KPZ stochastic surface growth
          </Link>{" "}
          — shares the KP acronym but is a stochastic PDE in a different universality class.
        </li>
        <li>
          <Link href="/codex" className={lk}>
            Holoflow Codex
          </Link>{" "}
          — studio conventions for WebXR export, facet flags, and Draco compression.
        </li>
      </ul>
    </>
  );
}

export const entry: Entry = buildInstructable({
  slug: SLUG,
  title: TITLE,
  lede: LEDE,
  date: new Date("2026-09-12"),
  topics: ["blender", "scripting", "mathematics", "physics", "webxr", "stage-floor"],
  body: Body,
  libraryPath:
    "blends/scripting/python-numpy-kadomtsev-petviashvili-kp-ii-1970-exact-web-soliton-hirota-tau-stage-floor-webxr",
});
