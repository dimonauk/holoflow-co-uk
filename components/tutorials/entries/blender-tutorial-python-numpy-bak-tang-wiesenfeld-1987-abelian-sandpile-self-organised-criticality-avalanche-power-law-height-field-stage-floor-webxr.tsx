import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-bak-tang-wiesenfeld-1987-abelian-sandpile-self-organised-criticality-avalanche-power-law-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — Bak–Tang–Wiesenfeld 1987 Abelian Sandpile: Self-Organised Criticality, Avalanche Power Laws, Fractal Cluster Height-Field Stage Floor for WebXR (Blender 5.1)";

const LEDE =
  "Per Bak, Chao Tang, and Kurt Wiesenfeld introduced the sandpile model in 1987 as the first concrete example of self-organised criticality — a mechanism by which many natural systems reach a critical state without any external tuning. Drop one grain of sand onto a lattice. When any site accumulates four or more grains it topples, passing one grain to each neighbour. Repeat a million times. The result is a height field whose avalanche sizes obey a power law P(S) ~ S^{−1.11} over many decades, and whose avalanche clusters are fractals with Hausdorff dimension D_f ≈ 2.75. This blueprint runs the full BTW simulation in NumPy inside Blender 5.1, bakes the critical state and two avalanche cluster snapshots into shape keys, and exports a 128 × 128 quad-grid stage floor as a Draco-compressed GLB ready for WebXR.";

function Body() {
  return (
    <>
      <p>
        The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-ising-model-2d-metropolis-monte-carlo-onsager-exact-tc-ferromagnetic-domains-height-field-stage-floor-webxr"
        >
          2D Ising model
        </Link>{" "}
        and the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-potts-model-3-state-2d-wu-1982-self-dual-exact-tc-checkerboard-metropolis-three-color-domain-height-field-stage-floor-webxr"
        >
          3-state Potts model
        </Link>{" "}
        both require a precisely tuned temperature to see critical behaviour.
        The BTW sandpile sidesteps this entirely: criticality is the
        unavoidable attractor. No coupling constant, no temperature, no
        fine-tuning. The pile simply fills up until it cannot hold more sand,
        and at that point every grain addition triggers an avalanche whose
        size is drawn from a power-law distribution spanning all scales.
      </p>

      <h2>The model</h2>

      <p>
        Place integer-valued sand heights h(i, j) on an N × N square lattice.
        The update rule is:
      </p>

      <pre>{`Add one grain: h[i, j] += 1

If h[i, j] >= 4 (CRITICAL_HEIGHT), site (i, j) topples:
    h[i, j]     -= 4
    h[i±1, j]   += 1  (if neighbour exists)
    h[i, j±1]   += 1  (if neighbour exists)

Repeat until all h < 4 (one avalanche complete).
Grains leaving the grid boundary are lost — open boundary condition.`}</pre>

      <p>
        After ~5 × N² grain additions the height field reaches the stationary
        distribution. From that point on, each new grain triggers an avalanche
        whose size S (number of distinct toppled sites) obeys:
      </p>

      <pre>{`P(S) ~ S^{-τ}        τ  ≈ 1.11   (2D BTW universality class)
P(T) ~ T^{-τ_t}      τ_t ≈ 1.50  (avalanche duration)
D_f  ≈ 2.75                       (Hausdorff dimension of cluster)`}</pre>

      <h2>The Abelian property — why vectorised toppling is exact</h2>

      <p>
        Deepak Dhar proved in 1990 that BTW toppling is commutative: if sites A
        and B are both unstable, the final stable configuration after all
        cascades is the same whether A or B topples first. This is called the
        Abelian Sandpile Model (ASM) for exactly this reason.
      </p>

      <p>
        The consequence for the NumPy implementation is significant. Instead of
        toppling one site at a time (which would require a Python loop over
        every unstable site), we can topple every unstable site
        simultaneously in a single array operation — and the result is
        physically identical. The blueprint&apos;s <code>_relax</code> function
        exploits this: each iteration masks all sites with{" "}
        <code>h &gt;= 4</code> and applies the four-direction spread in five
        NumPy statements, then loops until the grid is stable.
      </p>

      <h2>Shape keys</h2>

      <p>
        Four shape keys capture the model at different moments:
      </p>

      <pre>{`Basis       critical-state height field.  Z = h/3 × Z_SCALE.
            Colour: cobalt (h = 0, bare substrate) → amber (h = 3, full).

SK_SmallAval  Basis heights PLUS a small avalanche cluster (5–35 cells)
            raised by Z_BOOST = 0.28 m above the surrounding surface.
            The fractal boundary is directly visible in the viewport.

SK_LargeAval  Same but for a large (≥ 700-cell) system-spanning avalanche.
            The cluster reaches from one region of the lattice to the
            edges, crossing many length scales.

SK_Maximal  All h = 3 everywhere — the maximally stable uniform state
            just before any grain has been dropped.  The mesh is a flat,
            uniformly amber raised plateau.`}</pre>

      <p>
        For SK_SmallAval and SK_LargeAval, the blueprint searches the
        post-critical pile for a grain addition that causes an avalanche of the
        target size range, then stores (critical_heights + cluster_boost) as
        the shape key positions. The fractal silhouette of the cluster is
        readable as a raised island in the mesh.
      </p>

      <h2>Running the blueprint</h2>

      <ol>
        <li>Open Blender 5.1. Choose a new General scene.</li>
        <li>
          Switch to the Scripting workspace. Open{" "}
          <code>blueprint.py</code> in the text editor (Text → Open).
        </li>
        <li>
          Press <kbd>Alt</kbd>+<kbd>P</kbd> (or the ▶ Run Script button).
          The console prints:
          <pre>{`BTW sandpile: running to criticality …
BTW sandpile: hunting small avalanche …
BTW sandpile: small avalanche size = 17
BTW sandpile: hunting large avalanche …
BTW sandpile: large avalanche size = 1243
Saved  //.../btw_sandpile_floor.blend
Export //.../btw_sandpile_floor.glb`}</pre>
          Allow 1–3 minutes; 1.2 M grain relaxations drive the NumPy
          operations but no Blender operators are called during simulation.
        </li>
        <li>
          Switch to the 3-D Viewport. The mesh appears as a cobalt–amber
          height field. Open{" "}
          <strong>Properties → Object Data → Shape Keys</strong> and drag
          each key to 1.0 to inspect the four states.
        </li>
      </ol>

      <h2>Comparison with adjacent tutorials</h2>

      <p>
        The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-kpz-kardar-parisi-zhang-1986-stochastic-surface-growth-universality-height-field-stage-floor-webxr"
        >
          KPZ surface growth tutorial
        </Link>{" "}
        also produces a rough height field driven by a stochastic process, but
        the KPZ universality class is entirely different (β ≈ 0.24 vs no
        thermal exponents in BTW). Both produce WebXR-ready floor meshes from
        pure-Python scripts.
      </p>

      <p>
        The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-gray-scott-1984-pearson-1993-activator-depletion-turing-spot-worm-hole-height-field-stage-floor-webxr"
        >
          Gray–Scott reaction-diffusion tutorial
        </Link>{" "}
        similarly produces spatially structured fields with fractal-like
        boundaries, but driven by coupled PDEs rather than cellular-automaton
        rules. The sandpile is arguably the simpler system: one integer per
        site, one rule.
      </p>

      <p>
        The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-allen-cahn-phase-field-mean-curvature-motion-allen-cahn-1979-stage-floor-webxr"
        >
          Allen–Cahn phase-field tutorial
        </Link>{" "}
        shows how interface dynamics and coarsening also produce scale-invariant
        patterns over time — a different route to emergent criticality.
      </p>

      <h2>Outside sources</h2>

      <p>
        The original model and SOC concept:{" "}
        <strong>
          Bak P, Tang C, Wiesenfeld K (1987) &ldquo;Self-organized criticality:
          An explanation of the 1/f noise&rdquo; Phys Rev Lett 59(4):381–384.
        </strong>{" "}
        DOI{" "}
        <a
          className={lk}
          href="https://link.aps.org/doi/10.1103/PhysRevLett.59.381"
          target="_blank"
          rel="noopener noreferrer"
        >
          10.1103/PhysRevLett.59.381
        </a>
        . Public Domain (&gt;35 yr). The paper introduced the term
        &ldquo;self-organised criticality&rdquo; and remains one of the
        most cited papers in statistical physics. Related APS resources at{" "}
        <a
          className={lk}
          href="https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.59.381"
          target="_blank"
          rel="noopener noreferrer"
        >
          journals.aps.org/prl
        </a>
        .
      </p>

      <p>
        Proof of the Abelian property and exact critical exponents:{" "}
        <strong>
          Dhar D (1990) &ldquo;Self-organized critical state of sandpile automaton
          models&rdquo; Phys Rev Lett 64(14):1613–1616.
        </strong>{" "}
        DOI{" "}
        <a
          className={lk}
          href="https://link.aps.org/doi/10.1103/PhysRevLett.64.1613"
          target="_blank"
          rel="noopener noreferrer"
        >
          10.1103/PhysRevLett.64.1613
        </a>
        . Public Domain (&gt;30 yr). Dhar proved that toppling commutes,
        introduced the burning algorithm for counting recurrent
        configurations, and placed the exact exponents on rigorous
        footing. Sibling work: Dhar D (1999) &ldquo;The Abelian sandpile and
        related models&rdquo; Physica A 263:4–25 reviews the full theory.
      </p>

      <p>
        Numerical backbone:{" "}
        <strong>NumPy (BSD-3-Clause)</strong>{" "}
        <a
          className={lk}
          href="https://numpy.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          numpy.org
        </a>
        . Harris et al. 2020 Nature 585:357–362. Sibling:{" "}
        <a
          className={lk}
          href="https://scipy.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          SciPy (BSD-3-Clause)
        </a>
        {" "}for sparse-matrix and graph methods useful in cluster analysis.
      </p>
    </>
  );
}

export const blenderTutorialPythonNumpyBakTangWiesenfeld1987AbelianSandpileSelfOrganisedCriticalityAvalanchePowerLawHeightFieldStageFloorWebxrEntry: Entry =
  buildInstructable({
    slug: SLUG,
    date: "2026-09-19",
    title: TITLE,
    lede: LEDE,
    tags: [
      "scripting",
      "statistical-mechanics",
      "self-organised-criticality",
      "sandpile",
      "power-law",
      "fractals",
      "webxr",
      "stage-floor",
    ],
    body: Body,
  });
