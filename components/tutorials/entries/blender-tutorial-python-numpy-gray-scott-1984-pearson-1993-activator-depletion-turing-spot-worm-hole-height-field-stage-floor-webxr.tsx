import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-gray-scott-1984-pearson-1993-activator-depletion-turing-spot-worm-hole-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — Gray–Scott Reaction-Diffusion: Pearson 1993 Pattern Atlas — Spots, Worms, Holes, Self-Replicating Mitosis, Height-Field Stage Floor for WebXR (Blender 5.1)";

const LEDE =
  "Change the feed rate by 0.005 and a field of amber spots reorganises into worms; change the kill rate by another 0.003 and holes appear where the spots were. Pearson mapped this twelve-region phase diagram from a single pair of PDEs, and this blueprint walks all four corners of it — building a 128 × 128 height-field stage floor whose cobalt–amber gradient is the activator concentration of the Gray–Scott reaction-diffusion system, with shape-key morphs switching between pattern classes.";

function Body() {
  return (
    <>
      <p>
        Most Turing pattern tutorials use activator-inhibitor systems where a
        slow inhibitor chases a fast activator. Gray–Scott works differently:
        there is no separate inhibitor. Instead, the autocatalytic species v
        depletes the substrate u it needs to reproduce, creating
        &ldquo;activator-depletion&rdquo; feedback. The depletion signal
        diffuses faster than the activator (Du/Dv = 2 versus Schnakenberg&rsquo;s
        50), so the Turing condition is satisfied with a far smaller diffusivity
        ratio — which in turn means the (F, k) parameter plane is enormous
        and navigable.
      </p>

      <p>
        This belongs to the same family as the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-schnakenberg-1979-activator-substrate-turing-instability-spots-stripes-height-field-stage-floor-webxr"
        >
          Schnakenberg activator-substrate
        </Link>{" "}
        and{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-gierer-meinhardt-activator-inhibitor-turing-morphogenesis-1972-spot-stripe-height-field-stage-floor-webxr"
        >
          Gierer-Meinhardt activator-inhibitor
        </Link>{" "}
        tutorials, but it diverges in one crucial respect: Pearson&rsquo;s 1993
        Science paper systematically catalogued twelve distinct pattern classes
        by grid-search over (F, k), naming them with Greek letters. The δ-region
        contains the self-replicating spots he called &ldquo;mitosis&rdquo; —
        a single central perturbation divides repeatedly, filling the domain
        like a biological growth assay. Compare with the oscillatory patterns
        of the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-fitzhugh-nagumo-1961-excitable-media-trigger-wave-spiral-height-field-stage-floor-webxr"
        >
          FitzHugh-Nagumo excitable medium
        </Link>
        , which also starts from a small perturbation but produces travelling
        trigger waves rather than stationary Turing spots.
      </p>

      <h2>Equations</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Gray–Scott system  (Gray & Scott 1984, Pearson 1993):

∂u/∂t = Du∇²u − uv² + F(1 − u)       substrate
∂v/∂t = Dv∇²v + uv² − (F + k)v       activator

Shared reaction term: uv²
  − appears with − sign in u equation  (substrate consumed)
  + appears with + sign in v equation  (autocatalytic production)

Du = 0.16,  Dv = 0.08   (ratio 2 — WHY not 50?)
  Turing requires Du > Dv only; the required ratio depends on Jacobian
  eigenvalues at (u*, v*). Here J has a large off-diagonal entry from
  F, so the threshold ratio is small.

Nontrivial fixed point:
  u* = F + k          (e.g. 0.037 + 0.060 = 0.097 for spots)
  v* = √[F(1 − u*)/u*]                (≈ 0.346 for spots)

Turing instability condition (from linearisation):
  det(J − D k²I) = 0  for some wavenumber k²  >  0
  Pattern wavelength ≈ 2π / k_c`}
      </pre>

      <h2>Numerical method — explicit Euler + periodic 5-point Laplacian</h2>
      <p>
        The reaction term uv² is bilinear in both unknowns. Unlike
        Allen-Cahn&rsquo;s uniaxial φ³, you cannot cleanly split this into
        &ldquo;stiff linear + nonlinear&rdquo; for an ETD or semi-implicit
        scheme without solving a coupled quadratic each step. Explicit Euler is
        therefore not a concession — it is the rational choice, provided the
        CFL number stays below 0.25. At Du = 0.16, dx = 1, dt = 1:{" "}
        <code>Du · dt / dx² = 0.16 &lt; 0.25</code> ✓. The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-oregonator-belousov-zhabotinsky-bz-fkn-1972-chemical-spiral-wave-height-field-stage-floor-webxr"
        >
          Oregonator BZ system
        </Link>{" "}
        uses the same explicit Euler approach for the same reason.
      </p>

      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`# Periodic 5-point Laplacian — numpy.roll wraps indices O(1)
def _lap(f):
    return (roll(f,1,0) + roll(f,-1,0) +
            roll(f,1,1) + roll(f,-1,1) - 4*f)

# Explicit Euler step
uvv  = u * v * v          # reaction term — compute once, reuse
u   += dt*(Du*_lap(u) - uvv + F*(1-u))
v   += dt*(Dv*_lap(v) + uvv - (F+k)*v)
clip(u, 0, 1);  clip(v, 0, 1)`}
      </pre>

      <h2>Pearson&rsquo;s parameter atlas</h2>
      <p>
        The four shape keys step through four distinct regions of Pearson&rsquo;s
        (F, k) phase diagram:
      </p>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Basis     F=0.037 k=0.060  ε-region  symmetric isolated spots
SK_Worm   F=0.060 k=0.062  η-region  labyrinthine worms / mazes
SK_Hole   F=0.039 k=0.058  ζ-region  holes in active v-background
SK_Mitosis F=0.028 k=0.054 δ-region  self-replicating spot division

Colour: GS_V vertex attribute (cobalt v≈0 → amber v>0)
Height: z = v × 0.80  (v ≈ 0.35 max → z ≈ 0.28 m peak)`}
      </pre>

      <h2>Trade-offs and failure modes</h2>
      <ul className="list-disc pl-5 space-y-1">
        <li>
          <strong>F+k ≥ 1</strong> — trivial fixed point is globally stable;
          no patterning. Stay in the band 0.02 &le; F+k &le; 0.12.
        </li>
        <li>
          <strong>dt &gt; 1.5</strong> — explicit Euler loses stability and v
          diverges to NaN. The np.clip guard masks the problem rather than
          fixing it; lower dt.
        </li>
        <li>
          <strong>Mitosis pattern needs fewer noise, smaller seed</strong> —
          self-replication works from a clean 4 × 4 seed. Raising NOISE_AMP
          to 0.2 blurs the division events into a uniform blob.
        </li>
        <li>
          <strong>Worms need more steps than spots</strong> — η-region patterns
          take longer to achieve their lamellar steady state. Shortcutting to
          5 000 steps gives ragged proto-worms rather than smooth labyrinths.
        </li>
      </ul>

      <h2>Blueprint walkthrough</h2>
      <ol className="list-decimal pl-5 space-y-1">
        <li>
          <code>_lap(field)</code> — periodic 5-point Laplacian via four
          <code>np.roll</code> calls. Roll wraps the array without allocating a
          copy: it returns a view with adjusted strides.
        </li>
        <li>
          <code>_init(f_val, seed_off)</code> — places a central seed square
          (4 × 4 for mitosis, 20 × 20 for spots/worms) and adds weak white noise
          to break translational symmetry. Different <code>seed_off</code> values
          give each shape key a statistically independent initial condition while
          remaining fully reproducible.
        </li>
        <li>
          <code>_simulate()</code> — core loop; computes <code>uvv = u * v * v</code>{" "}
          once and reuses it in both update equations, halving the number of
          element-wise multiplications.
        </li>
        <li>
          <code>_build_mesh()</code> — constructs the height-field quad mesh
          and writes the FLOAT_COLOR <code>GS_V</code> attribute from the basis
          v-field (cobalt → amber via linear interpolation with a ×2 amplifier
          so v ≈ 0.5 maps to full amber rather than mid-grey).
        </li>
        <li>
          <code>_add_sk()</code> — adds subsequent shape keys by updating only
          vertex z; x and y are unchanged, keeping the planar grid topology for
          all four patterns.
        </li>
        <li>
          Rotation <code>−π/2 about X</code>, then <code>transform_apply</code>{" "}
          — bakes +Y-up orientation into the mesh data before GLB export, as
          required by the holoflow WebXR exporter.
        </li>
      </ol>
    </>
  );
}

const entry: Entry = buildInstructable({
  slug: SLUG,
  title: TITLE,
  lede: LEDE,
  date: "2026-09-13",
  topic: "blender",
  tags: [
    "blender-5-1",
    "python",
    "numpy",
    "reaction-diffusion",
    "gray-scott",
    "turing-pattern",
    "pearson-1993",
    "stage-floor",
    "webxr",
    "scripting",
  ],
  body: Body,
  externalLinks: [
    {
      label: "Pearson 1993 — Science 261:189 (doi)",
      url: "https://doi.org/10.1126/science.261.5118.189",
    },
    {
      label: "Gray & Scott 1984 — Chem Eng Sci 39:1087 (doi)",
      url: "https://doi.org/10.1016/0009-2509(84)87017-7",
    },
    {
      label: "pmneila/jsexp — interactive GS explorer (MIT)",
      url: "https://github.com/pmneila/jsexp",
    },
  ],
});

export const blenderTutorialPythonNumpyGrayScott1984Pearson1993ActivatorDepletionTuringSpotWormHoleHeightFieldStageFloorWebxrEntry =
  entry;
export default entry;
