import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-drossel-schwabl-1992-forest-fire-model-self-organised-criticality-fire-cluster-power-law-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — Drossel–Schwabl 1992 Forest Fire Model: Self-Organised Criticality, Fire Cluster Power Law P(S)∼S^{−1.5}, Three-State Height-Field Stage Floor for WebXR (Blender 5.1)";

const LEDE =
  "Bernhard Drossel and Franz Schwabl published the forest fire model in 1992 as a three-state cellular automaton that achieves self-organised criticality through an ecological rather than a toppling mechanism. Trees grow stochastically with probability p, lightning ignites isolated trees with probability f, and fire spreads synchronously across any connected forest patch before the next saplings can establish. When p ≪ f ≪ 1 and p/f ≫ 1, the system self-organises to a stationary state where fire-cluster sizes obey a power law P(S) ∼ S^{−1.5} across many decades — with no coupling constant to tune. This blueprint runs the full Drossel–Schwabl simulation in NumPy inside Blender 5.1, bakes four landscape states (SOC steady state, sparse savanna, dense forest, theoretical saturation) into shape keys, and exports a 128 × 128 quad-grid stage floor as a Draco-compressed GLB ready for WebXR.";

function Body() {
  return (
    <>
      <p>
        The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-bak-tang-wiesenfeld-1987-abelian-sandpile-self-organised-criticality-avalanche-power-law-height-field-stage-floor-webxr"
        >
          Bak–Tang–Wiesenfeld Abelian Sandpile
        </Link>{" "}
        achieves SOC through grain conservation and a toppling threshold: the
        critical state is approached from below as the pile fills up. The
        Drossel–Schwabl forest fire model takes the opposite route — it is
        dissipative, stochastic, and ecological in flavour. Trees are born and
        destroyed; the mechanism is competition between slow regeneration and
        catastrophic spread. Both produce power laws without tuning, but the
        exponents and the spatial geometry of the critical clusters differ.
      </p>

      <h2>The model</h2>

      <p>
        Each site on an N × N square lattice holds one of three states. The
        entire lattice updates synchronously each time step, reading the old
        state to produce the new:
      </p>

      <pre>{`States:   EMPTY(0) — ash / cleared ground
          TREE(1)  — living tree
          BURNING(2) — active fire (persists exactly ONE step)

Rules (applied simultaneously, old state → new state):
  1.  BURNING              → EMPTY
  2.  TREE + BURNING nbr   → BURNING    (fire spreads, 4-connected)
  3.  TREE + no BURNING nbr→ BURNING    with probability f  (lightning)
                           → TREE       with probability 1−f
  4.  EMPTY                → TREE       with probability p  (regrowth)
                           → EMPTY      with probability 1−p`}</pre>

      <p>
        The SOC regime requires two-time-scale separation: lightning is rarer
        than regrowth (<code>f ≪ p</code>), and both are slow compared to fire
        spread (<code>p ≪ 1</code>). In practice, <code>p = 0.01</code>,{" "}
        <code>f = 5 × 10⁻⁵</code> gives a ratio <code>p/f = 200</code>, which
        is sufficient on a 128 × 128 grid to observe the power-law scaling.
      </p>

      <h2>Why the vectorised update is exact</h2>

      <p>
        Because states BURNING, TREE, and EMPTY are mutually exclusive and we
        read exclusively from <code>grid</code> and write exclusively to{" "}
        <code>new_grid</code>, all N² update decisions are independent. There
        is no equivalent of the Abelian sandpile&apos;s commutation theorem here
        — instead, the correctness of simultaneous update is simply a
        consequence of the model&apos;s definition: Drossel and Schwabl
        specified a <em>synchronous</em> automaton. A single{" "}
        <code>numpy.roll</code> sweep across four axes produces the fire-spread
        mask in five array operations.
      </p>

      <h2>The fire cluster power law</h2>

      <p>
        A fire cluster is the set of all sites that burn in one time step as a
        result of a single lightning-ignition event — i.e., the connected
        component of TREE sites that includes the lightning strike and can be
        reached by fire spread before any regrowth occurs. In the SOC regime:
      </p>

      <pre>{`P(S) ~ S^{−τ}      τ ≈ 1.5   (Drossel–Schwabl universality class)
P(L) ~ L^{−α}      α ≈ 2.0   (fire-perimeter length distribution)

Compare Bak–Tang–Wiesenfeld sandpile:
  P(S) ~ S^{−1.11}            (different universality class)
  D_f  ≈ 2.75                 (fractal dimension of sandpile clusters)`}</pre>

      <p>
        The exponent τ ≈ 1.5 for the DS model is consistent with observed
        wildfire-size statistics in real landscapes (Malamud et al. 1998). The
        fractal dimension of the fire clusters at the critical percolation
        threshold of the forest is D_f ≈ 1.9.
      </p>

      <h2>Contrast with percolation</h2>

      <p>
        At the critical bond percolation threshold p_c ≈ 0.593 for a 2D square
        lattice (see the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-dla-diffusion-limited-aggregation-witten-sander-1981-fractal-growth-dendritic-crystal-height-field-stage-floor-webxr"
        >
          DLA fractal growth
        </Link>{" "}
        tutorial for cluster geometry), a spanning cluster first appears and
        the cluster-size distribution becomes a power law. In the DS model,
        the forest density fluctuates around a mean density that is itself
        dynamically maintained near the percolation threshold by the
        interplay of regrowth and fire — without any externally imposed density.
        This is the self-organisation: the system steers its own forest density
        to the critical point.
      </p>

      <h2>Shape keys</h2>

      <p>
        Four shape keys capture the landscape under different regrowth/lightning
        ratios:
      </p>

      <pre>{`Basis       p=0.010 f=5e-5  3 000 steps from 50% random seed
            SOC steady state: mixed ash (cobalt, Z=0), forest (green,
            Z=0.175), active fire cluster (amber, Z=0.35).

SK_LowP     p=0.003 f=5e-5  2 000 steps
            Sparse savanna: tree density below percolation threshold.
            Fire clusters remain tiny; ash dominates.

SK_HighP    p=0.050 f=5e-5  4 000 steps
            Dense forest: p/f=1000 — very long fire-return interval.
            When fires do occur, they are system-spanning.

SK_AllTrees Every site = TREE (maximum-density saturation)
            Theoretical upper bound. One lightning strike here would
            burn the entire lattice in one cascade.`}</pre>

      <h2>Height-field and colour encoding</h2>

      <p>
        Each vertex Z-height is <code>state × Z_SCALE / 2</code>, mapping the
        integer states to three distinct elevations: ash lies flat at Z = 0,
        trees form a canopy at Z = 0.175 m, and active fire peaks at Z = 0.35
        m. A per-vertex FLOAT_COLOR attribute <code>FF_State</code> stores
        the normalised state value (0, 0.5, 1.0), which drives a three-stop
        ColorRamp material — cobalt for ash, forest green for living trees, and
        amber for burning sites. The BURNING colour is deliberately the same
        amber used throughout the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-gray-scott-1984-pearson-1993-activator-depletion-turing-spot-worm-hole-height-field-stage-floor-webxr"
        >
          reaction-diffusion stage floors
        </Link>
        , preserving the studio cobalt–amber palette while adding the green
        midpoint.
      </p>

      <h2>Ecological interpretation</h2>

      <p>
        The DS model is the simplest mathematical formalisation of the
        observation that many real forests maintain a fire regime that looks
        critical. Slow fuel accumulation (trees growing) followed by rapid
        catastrophic release (fire) appears in diverse systems: boreal forest
        fires, savanna fires, coral bleaching, and even some epidemic spreading.
        The spatial pattern on the stage floor — patches of dense forest
        interrupted by ash lanes and isolated amber fire pixels — is immediately
        recognisable as a satellite view of a fire-adapted landscape.
      </p>

      <p>
        For the mathematical machinery behind another landscape process on this
        stage floor, the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-ising-model-2d-metropolis-monte-carlo-onsager-exact-tc-ferromagnetic-domains-height-field-stage-floor-webxr"
        >
          2D Ising model
        </Link>{" "}
        compares directly: both are nearest-neighbour 2D models with a critical
        point, but the Ising model requires its temperature to be finely tuned
        to T_c, while the DS model reaches its critical state autonomously.
      </p>

      <h2>Outside sources</h2>

      <p>
        The original model and its SOC characterisation appear in:{" "}
        <a
          className={lk}
          href="https://link.aps.org/doi/10.1103/PhysRevLett.69.1629"
          target="_blank"
          rel="noopener noreferrer"
        >
          Drossel B &amp; Schwabl F (1992) Phys Rev Lett 69(11):1629–1632
        </a>{" "}
        (Public Domain, &gt;30 yr). Related projects from the same research
        lineage: the APS publishes companion papers through its{" "}
        <a
          className={lk}
          href="https://journals.aps.org/prl/"
          target="_blank"
          rel="noopener noreferrer"
        >
          Physical Review Letters journal
        </a>
        . Array operations use{" "}
        <a
          className={lk}
          href="https://numpy.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          NumPy (BSD-3-Clause)
        </a>
        , with cluster-size analysis possible via{" "}
        <a
          className={lk}
          href="https://scipy.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          SciPy (BSD-3-Clause)
        </a>
        &apos;s{" "}
        <code>ndimage.label</code> for connected-component labelling.
      </p>

      <h2>Troubleshooting</h2>

      <pre>{`Grid all-TREE at end:  p is too high relative to f — try p=0.01, f=5e-5.
Grid all-EMPTY:        f is too high — try f=1e-5 or reduce N_SETTLE.
No SOC scaling:        N too small (< 64) or p/f < 50. Increase p/f ratio.
Very slow in Blender:  N_SETTLE × N² operations. N=128, 3000 steps = fine.
                       N=256, 3000 steps = ~4× slower; reduce to 1000 steps.`}</pre>

      <h2>Lenia comparison</h2>

      <p>
        The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-lenia-continuous-cellular-automaton-fft-soliton-webxr"
        >
          Lenia continuous cellular automaton
        </Link>{" "}
        generalises Game-of-Life-style automata to smooth, continuous-valued
        kernels — a complementary approach to the DS model&apos;s discrete
        three-state update. Where Lenia produces gliders and solitons, the DS
        model produces critical-exponent scaling; both are cellular automata
        in which complex spatial structure emerges from a simple local rule.
      </p>
    </>
  );
}

export const blenderTutorialPythonNumpyDrosselSchwabl1992ForestFireModelSelfOrganisedCriticalityFireClusterPowerLawHeightFieldStageFloorWebxrEntry: Entry =
  buildInstructable({
    slug: SLUG,
    date: "2026-09-19",
    title: TITLE,
    lede: LEDE,
    tags: [
      "scripting",
      "statistical-mechanics",
      "self-organised-criticality",
      "cellular-automaton",
      "forest-fire",
      "power-law",
      "fractals",
      "ecology",
      "webxr",
      "stage-floor",
    ],
    body: Body,
  });
