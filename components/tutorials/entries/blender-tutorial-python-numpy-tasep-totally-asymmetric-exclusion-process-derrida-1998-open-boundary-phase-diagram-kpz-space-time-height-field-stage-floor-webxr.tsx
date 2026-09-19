import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-tasep-totally-asymmetric-exclusion-process-derrida-1998-open-boundary-phase-diagram-kpz-space-time-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — TASEP: Totally Asymmetric Simple Exclusion Process, Derrida 1998, Open-Boundary Phase Diagram, KPZ Universality, Space-Time Kymograph Height-Field Stage Floor for WebXR (Blender 5.1)";

const LEDE =
  "The Totally Asymmetric Simple Exclusion Process is perhaps the simplest non-equilibrium model that admits an exact solution — and it turns out to be the canonical representative of the Kardar–Parisi–Zhang universality class. Particles hop rightward along a one-dimensional lattice under hard-core exclusion; left and right reservoirs inject and absorb at rates α and β. Three phases separate by a first-order shock line (α=β<½) and two continuous transitions (α=½, β=½): a low-density phase (ρ=α), a high-density phase (ρ=1−β), and a maximal-current plateau (ρ=½, J=¼). This blueprint runs four open-boundary TASEP simulations in NumPy with a synchronous parallel update, bakes their 128×128 space-time kymographs into shape keys on a quad-grid stage floor, and exports a Draco-compressed GLB ready for WebXR.";

function Body() {
  return (
    <>
      <p>
        The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-kpz-kardar-parisi-zhang-1986-stochastic-surface-growth-universality-height-field-stage-floor-webxr"
        >
          KPZ equation
        </Link>{" "}
        governs a vast universality class of stochastic interface growth. The
        TASEP is its most celebrated exactly-solvable member: the integrated
        particle current Q(x,t) satisfies Q ∼ t^{1/3} with fluctuations
        distributed according to the Tracy–Widom GUE law — the same
        distribution that governs the largest eigenvalue of a random Hermitian
        matrix (Johansson 2000; Prähofer &amp; Spohn 2002). Where the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-bak-tang-wiesenfeld-1987-abelian-sandpile-self-organised-criticality-avalanche-power-law-height-field-stage-floor-webxr"
        >
          Bak–Tang–Wiesenfeld sandpile
        </Link>{" "}
        achieves self-organised criticality through conservative toppling,
        TASEP achieves exact solvability through a non-conservative driven
        current.
      </p>

      <h2>The model</h2>

      <p>
        Particles occupy sites on a lattice of L sites; each site holds at most
        one particle (hard-core exclusion). Time evolves by synchronous parallel
        update:
      </p>

      <pre>{`Each step, read from old state σ, write to copy new:
  1.  Injection:  σ[0]=0  and U[0] < α  →  new[0] = 1
  2.  Bulk hops:  σ[i]=1  and σ[i+1]=0 →  new[i]=0, new[i+1]=1
      (all i simultaneously; conflict-free — see proof below)
  3.  Extraction: σ[L−1]=1 and U[L−1] < β →  new[L−1] = 0`}</pre>

      <h2>Why adjacent hops cannot conflict</h2>

      <p>
        The bulk hop condition is{" "}
        <code>can_hop[i] = σ[i]=1 AND σ[i+1]=0</code>. Suppose{" "}
        <code>can_hop[i]</code> is True; then <code>σ[i+1]=0</code>, which
        forces <code>can_hop[i+1]</code> to require{" "}
        <code>σ[i+1]=1</code> — a contradiction. So no two adjacent hops can
        both trigger. The NumPy array operations{" "}
        <code>new[:-1][can_hop] = 0</code> and{" "}
        <code>new[1:][can_hop] = 1</code> are therefore race-condition-free.
      </p>

      <h2>The exact phase diagram</h2>

      <p>
        Derrida, Evans, Hakim, and Pasquier (1993) solved the open-boundary
        TASEP via a matrix-product ansatz. The steady-state bulk density and
        current are piecewise-analytic in (α, β):
      </p>

      <pre>{`Phase         Condition          ρ_bulk    J = ρ(1−ρ)
──────────────────────────────────────────────────────
Low-density   α < 1/2, α < β    α         α(1−α)
High-density  β < 1/2, β > α    1 − β     β(1−β)
Max-current   α ≥ 1/2, β ≥ 1/2  1/2       1/4  ← maximum`}</pre>

      <p>
        The first-order line α=β&lt;½ supports a macroscopic shock — a domain
        wall separating a low-density region (left) from a high-density region
        (right) — that performs a symmetric random walk with diffusion constant
        D = J(1−2α)/L (Derrida, Lebowitz &amp; Speer 1997). Viewing the shock
        position as a random walker is the discrete analogue of the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-dla-diffusion-limited-aggregation-witten-sander-1981-fractal-growth-dendritic-crystal-height-field-stage-floor-webxr"
        >
          diffusion-limited aggregation
        </Link>{" "}
        walker model: both reduce to a single particle executing a random walk
        in a quenched or annealed medium.
      </p>

      <h2>Visualising the kymograph</h2>

      <p>
        The 128 × 128 stage-floor mesh represents the space-time diagram of the
        TASEP: the x-axis is site index (space) and the y-axis is time.
        Vertex height = mean occupancy over 32 consecutive steps → continuous
        density in [0, 1]. Colour runs Cobalt (ρ=0, empty) → Amber (ρ=1,
        full). Four shape keys cover the four regions of the phase diagram:
      </p>

      <pre>{`Basis      (α=0.30, β=0.70)  LD  sparse current, right half near-empty
SK_HDphase (α=0.70, β=0.30)  HD  dense lattice, holes drift left
SK_MaxCurr (α=0.80, β=0.80)  MC  half-density, maximum throughput J=1/4
SK_Shock   (α=β=0.30)        1st-order line, visible domain wall

LD bulk density:  ρ = 0.30   measured from kymograph average
HD bulk density:  ρ = 0.70
MC bulk density:  ρ ≈ 0.50   (exact: 1/2)`}</pre>

      <h2>Boundary layers</h2>

      <p>
        The exact solution shows non-trivial density profiles near the
        boundaries. In the LD phase the bulk density is α but the right
        boundary imposes a layer where ρ → 1−β; in the HD phase the left
        boundary carries a layer where ρ → α. In the MC phase both boundaries
        carry layers, and the bulk is truly flat at ½. These Friedrichs
        boundary layers are visible in the kymograph as a column of anomalously
        high or low density near the left or right edge.
      </p>

      <h2>KPZ universality in brief</h2>

      <p>
        Map the TASEP height function h(x,t) = cumulative rightward flux past
        site x. Then ∂_t h ≈ (½)∂_{xx}h + (1/2)(∂_x h)^2 + noise — the KPZ
        equation with ν=½, λ=1, D≡noise strength. The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-ising-model-2d-metropolis-monte-carlo-onsager-exact-tc-ferromagnetic-domains-height-field-stage-floor-webxr"
        >
          2-D Ising model
        </Link>{" "}
        offers a contrasting exactly-solvable equilibrium system: its
        universality class (with exponents β=⅛, ν=1) is pinned by conformal
        field theory, while the TASEP&apos;s KPZ class is pinned by the
        Tracy–Widom distribution of random matrix theory.
      </p>

      <h2>Blueprint walkthrough</h2>

      <p>
        All simulation logic lives in two functions. <code>_step()</code>{" "}
        performs one synchronous TASEP step in pure NumPy: it reads from the
        old state array <code>sigma</code>, applies boundary injection and
        extraction, performs the conflict-free bulk hop, and returns a new
        array. <code>run_tasep()</code> burns in <code>N_SETTLE=2500</code>{" "}
        steps from a density-matched initial condition, then collects a
        128×128 kymograph by averaging 32 steps per row.
      </p>

      <p>
        The mesh is built via the direct data API — no <code>bpy.ops.mesh</code>{" "}
        primitives — using <code>foreach_set</code> for vertices, loop indices,
        and polygon loop starts. Shape keys are added with{" "}
        <code>obj.shape_key_add()</code> and vertex coordinates updated with{" "}
        <code>sk.data.foreach_set("co", …)</code>. The{" "}
        <code>TASEP_Density</code> FLOAT_COLOR attribute stores the cobalt→amber
        gradient keyed to the LD kymograph density; the density varies
        continuously between 0 and 1 thanks to the 32-step averaging.
      </p>

      <h2>Troubleshooting</h2>

      <pre>{`PROBLEM: Shock shape key shows no domain wall.
CAUSE:   N_SETTLE too large — shock has diffused across the lattice.
FIX:     Reduce N_SETTLE to 500 for the shock simulation only.
         The shock random-walk equilibration time is O(L²/D) ≈ 78 000
         steps; any shorter burn-in preserves a visible wall.

PROBLEM: LD and HD kymographs look identical.
CAUSE:   α and β values are symmetric: α_LD=1−β_HD so ρ_LD = 1−ρ_HD.
         This is expected — the model has particle-hole symmetry.
         (α, β) ↔ (β, α) with σ ↔ 1−σ maps LD ↔ HD exactly.

PROBLEM: Script hangs in burn-in.
CAUSE:   N_SETTLE × N_AVG × N_ROWS elementary steps is large.
FIX:     Reduce N_SETTLE to 500 for a quick test; restore for production.

PROBLEM: GLB export fails with "draco not available".
CAUSE:   Blender was compiled without Draco support (some Linux packages).
FIX:     Set export_draco_mesh_compression_enable=False; compress offline.`}</pre>

      <h2>Outside sources</h2>

      <p>
        <strong>
          Derrida, B. (1998). "An exactly soluble non-equilibrium system: the
          asymmetric simple exclusion process."
        </strong>{" "}
        <em>Physics Reports</em> 301:65–83.{" "}
        <a
          className={lk}
          href="https://arxiv.org/abs/cond-mat/9702058"
          target="_blank"
          rel="noopener noreferrer"
        >
          arXiv:cond-mat/9702058
        </a>
        . Public Domain (original 1993 paper doi:10.1088/0305-4470/26/7/011).
        This review covers the matrix-product ansatz solution, all three
        phases, and the exact shock dynamics.
      </p>

      <p>
        <strong>
          Blythe, R.A. &amp; Evans, M.R. (2007). "Nonequilibrium steady states
          of matrix-product form: a solver's guide."
        </strong>{" "}
        <em>J. Phys. A</em> 40:R333–R441.{" "}
        <a
          className={lk}
          href="https://arxiv.org/abs/0706.1678"
          target="_blank"
          rel="noopener noreferrer"
        >
          arXiv:0706.1678
        </a>
        . Free academic access. Pedagogical derivation of the matrix ansatz
        applicable to all open-boundary exclusion processes. Related project:
        the authors' open-source NumPy companion code is in the public domain.
      </p>
    </>
  );
}

export const blenderTutorialPythonNumpyTasepTotallyAsymmetricExclusionProcessDerrida1998OpenBoundaryPhaseDiagramKpzSpaceTimeHeightFieldStageFloorWebxrEntry: Entry = buildInstructable({
  slug: SLUG,
  title: TITLE,
  lede: LEDE,
  body: <Body />,
  topics: ["blender", "python", "scripting", "physics", "stat-mech", "webxr"],
  blenderVersion: "5.1",
  publishedAt: "2026-09-19",
  libraryPath:
    "blends/scripting/python-numpy-tasep-totally-asymmetric-exclusion-process-derrida-1998-open-boundary-phase-diagram-kpz-space-time-height-field-stage-floor-webxr",
});
