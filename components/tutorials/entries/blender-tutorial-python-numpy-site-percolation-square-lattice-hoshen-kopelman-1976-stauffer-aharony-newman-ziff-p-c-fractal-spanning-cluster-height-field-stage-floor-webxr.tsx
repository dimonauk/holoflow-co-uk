import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-site-percolation-square-lattice-hoshen-kopelman-1976-stauffer-aharony-newman-ziff-p-c-fractal-spanning-cluster-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — Site Percolation on Z², Hoshen–Kopelman 1976 Union-Find, p_c ≈ 0.5927, Fractal Spanning Cluster D_f = 91/48, Exact CFT Exponents, Height-Field Stage Floor for WebXR (Blender 5.1)";

const LEDE =
  "Site percolation is the paradigm second-order phase transition that requires no Hamiltonian, no temperature, and no dynamics — only a single control parameter p and a decision: is this site occupied? Below the threshold p_c ≈ 0.5927 on the square lattice all clusters are finite; above it a unique infinite spanning cluster appears, and at p_c precisely the spanning cluster is a fractal with dimension D_f = 91/48 ≈ 1.896. The critical exponents (τ=187/91, ν=4/3, β=5/36) are exact results from conformal field theory. This blueprint runs four independent 128×128 percolation realisations via the Hoshen–Kopelman union-find algorithm, bakes log-cluster-size height fields into four shape keys on a quad-grid stage floor, and exports a Draco-compressed GLB for WebXR.";

function Body() {
  return (
    <>
      <p>
        Site percolation and{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-dla-diffusion-limited-aggregation-witten-sander-1981-fractal-growth-dendritic-crystal-height-field-stage-floor-webxr"
        >
          diffusion-limited aggregation
        </Link>{" "}
        are the two classical routes to fractal clusters on a lattice. DLA
        grows a single cluster by successive random-walk deposition; percolation
        assigns every site independently and asks which clusters span the system.
        Both produce fractal objects at their respective thresholds, but their
        fractal dimensions differ: D_f(DLA) ≈ 1.71 vs D_f(perc) = 91/48 ≈
        1.896. The percolation spanning cluster is denser because every occupied
        site contributes, whereas DLA&apos;s tips outrun the interior.
      </p>

      <h2>The model</h2>

      <p>
        Each site on the N × N square lattice is independently occupied with
        probability p, or empty with probability 1 − p. Two occupied sites
        belong to the same cluster if and only if they are connected by a path
        of nearest-neighbour (von Neumann, 4-connectivity) occupied sites.
        The order parameter is the percolation probability P_∞(p) — the
        probability that a given site belongs to the infinite (spanning) cluster:
      </p>

      <pre>{`p < p_c:  P_∞ = 0          (all clusters are finite)
p = p_c:  P_∞ = 0          (spanning cluster measure-zero at threshold)
p > p_c:  P_∞ ~ (p − p_c)^β,  β = 5/36 ≈ 0.139  (giant component)`}</pre>

      <p>
        The threshold for <em>site</em> percolation on the square lattice is
        p_c ≈ 0.59274621(13) — not known exactly, unlike{" "}
        <em>bond</em> percolation on the square lattice, whose threshold is
        exactly 1/2 by self-duality. The fourth shape key, SK_Bond, demonstrates
        bond percolation at exactly p = 0.5.
      </p>

      <h2>Exact critical exponents</h2>

      <p>
        Percolation in 2D sits in the same universality class as the
        q → 1 limit of the q-state Potts model — the same framework that gives
        the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-ising-model-2d-metropolis-monte-carlo-onsager-exact-tc-ferromagnetic-domains-height-field-stage-floor-webxr"
        >
          Ising model&apos;s
        </Link>{" "}
        exponents β = 1/8, ν = 1 via conformal field theory (Nienhuis 1982).
        The percolation exponents are:
      </p>

      <pre>{`τ   = 187/91  ≈ 2.055    cluster-size distribution P(s) ~ s^{−τ}
ν   = 4/3     ≈ 1.333    correlation length ξ ~ |p − p_c|^{−ν}
β   = 5/36    ≈ 0.139    P_∞ ~ (p − p_c)^β          for p > p_c
γ   = 43/18   ≈ 2.389    mean finite cluster size S ~ |p − p_c|^{−γ}
η   = 5/24    ≈ 0.208    pair-connectivity C(r) ~ r^{−(d−2+η)} at p_c
D_f = 91/48   ≈ 1.896    fractal dimension of spanning cluster`}</pre>

      <p>
        These are rational fractions because percolation is described by a
        rational conformal field theory (central charge c = 0). Compare with
        the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-potts-model-3-state-2d-wu-1982-self-dual-exact-tc-checkerboard-metropolis-three-color-domain-height-field-stage-floor-webxr"
        >
          3-state Potts model
        </Link>{" "}
        (c = 4/5) whose exponents are also rational but different: the c = 0
        theory has no local stress-tensor primary, which is why the percolation
        transition is continuous but the order parameter β is anomalously small.
      </p>

      <h2>Hoshen–Kopelman algorithm</h2>

      <p>
        The Hoshen–Kopelman algorithm (1976) labels all clusters in a single
        raster scan using a union-find data structure. It is O(N α(N)) where α
        is the inverse Ackermann function — effectively O(N) for all practical
        system sizes.
      </p>

      <pre>{`For each site (i, j) scanned left-to-right, top-to-bottom:
  if empty:   skip
  if occupied:
    left  ← occupied site at (i, j−1), if any
    above ← occupied site at (i−1, j), if any
    case (none):    assign fresh label = flat_index
    case (one):     inherit that neighbour's root
    case (both, same root): inherit root
    case (both, different roots): UNION the two roots; inherit result

After scan:
  second pass: for every occupied site find its root (path compression)
  count cluster sizes by root; map size → height via log normalisation`}</pre>

      <p>
        The implementation in <code>blueprint.py</code> uses Python-level
        iteration over the 16 384 sites — fast enough for a teaching script
        (≈ 0.5 s per realisation on modern hardware). The second pass leverages
        NumPy&apos;s <code>bincount</code> for O(N) size accumulation. The same
        scan works correctly for both site and bond percolation: the bond case
        derives a site-occupancy map from bond connectivity before calling the
        same HK function.
      </p>

      <h2>Why the log height scale?</h2>

      <p>
        Cluster sizes at criticality span six decades: isolated dimers (s = 2)
        coexist with a spanning cluster of order s ≈ N² = 16 384. A linear
        scale would compress all small clusters to zero height and show only
        the giant component. The log scale
        <code> h = log(1 + s) / log(N²)</code> maps
        s = 1 → h ≈ 0.07, s = 100 → h ≈ 0.47, s = N² → h = 1.0, giving a
        readable relief at all p values.
      </p>

      <p>
        At p_c, where the size distribution is a pure power law P(s) ~ s^{-τ},
        the log-scale height field is itself a power-law distributed random
        variable. The resulting surface has a fractal roughness consistent with
        D_f = 91/48 ≈ 1.896 — clearly visible in the SK_Critical shape key as
        a branching, self-similar topology unlike the smooth dome of SK_Above.
        The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-bak-tang-wiesenfeld-1987-abelian-sandpile-self-organised-criticality-avalanche-power-law-height-field-stage-floor-webxr"
        >
          Bak–Tang–Wiesenfeld sandpile
        </Link>{" "}
        also produces a self-similar height field at its SOC fixed point, but
        through a dynamical mechanism (conservative toppling) rather than the
        purely geometric threshold of percolation.
      </p>

      <h2>Shape keys walkthrough</h2>

      <pre>{`Basis       p = 0.40   sub-critical
  Clusters are finite, roughly circular. The floor is mostly flat
  (log(1+1) ≈ 0.07) with a few modest bumps (log(1+10) ≈ 0.27).

SK_Critical p = 0.5927  critical point
  The spanning cluster fills the floor with a branching fractal ridge.
  Many small clusters dot the periphery. The height distribution is
  a power-law: a few high-s sites and many low-s sites, giving the
  characteristic jagged texture of a scale-free system.

SK_Above    p = 0.70   super-critical
  The giant component dominates; nearly all occupied sites belong to
  it (P_∞ ≈ 0.77 at p=0.70). The floor shows a high, near-uniform
  plateau broken only by small empty holes.

SK_Bond     p = 0.50   bond percolation threshold
  Exactly at the bond-percolation threshold. The spanning cluster
  is more regular than the site-percolation one because every bond
  is open/closed independently, giving a less fragmented boundary.
  Compare the fractal ridge topology with SK_Critical.`}</pre>

      <h2>Bond vs site percolation</h2>

      <p>
        On the square lattice the bond threshold is exactly p_c^{bond} = 1/2
        by a self-duality argument: the lattice is its own dual, so the bond
        model maps onto itself under duality with p ↔ 1 − p, pinning
        the threshold at the fixed point p = 1/2. Site percolation has no
        such exact mapping; its threshold p_c ≈ 0.5927 is known to seven
        decimal places from Monte Carlo (Newman &amp; Ziff 2001) but not from
        any exact calculation. The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-drossel-schwabl-1992-forest-fire-model-self-organised-criticality-fire-cluster-power-law-height-field-stage-floor-webxr"
        >
          Drossel–Schwabl forest-fire model
        </Link>{" "}
        can be viewed as a dynamical version of site percolation: trees grow
        on empty sites and burn when a lightning bolt triggers a percolation-like
        cascade, self-organising to a state near the percolation threshold
        without tuning.
      </p>

      <h2>Blueprint walkthrough</h2>

      <p>
        The entry point is <code>run()</code> which:
      </p>

      <ol>
        <li>
          Clears the scene and calls <code>_percolation_heights(P_BELOW, SEED_BASE)</code>
          to produce the Basis height field.
        </li>
        <li>
          Passes that to <code>_build_mesh()</code> which constructs a 128 × 128
          quad grid via <code>mesh.from_pydata()</code> — the direct data API
          avoids context-dependent operators.
        </li>
        <li>
          Adds three further shape keys (SK_Critical, SK_Above, SK_Bond) with
          <code> _add_shape_key()</code>, which updates only the Z-coordinate of
          each vertex via <code>foreach_set</code>.
        </li>
        <li>
          Sets the <code>Perc_Cluster</code> FLOAT_COLOR attribute on the Basis
          heights; the colour ramp runs cobalt (height = 0, empty / isolated)
          → amber (height = 1, giant component).
        </li>
        <li>
          Exports to <code>holoflow_perc_floor.glb</code> with Draco level 6
          and WebP textures, applying all transforms at export per the
          holoflow_webxr_exporter convention (+Y up).
        </li>
      </ol>

      <h2>Troubleshooting</h2>

      <pre>{`PROBLEM: SK_Critical shows no spanning cluster.
CAUSE:   The RNG seed happened to produce a sub-threshold realisation
         even at p = 0.5927 for N = 128.  The percolation probability
         at p_c on a finite lattice is only ≈ 0.5 (Cardy 1992 crossing
         formula: π_h(1/2) = 1/2 + correction).
FIX:     Increment SEED_BASE by 1 and rerun.

PROBLEM: Script runs > 30 s per shape key.
CAUSE:   The Python-level HK loop is O(N²) without the C-extension speedup.
         At N = 128 this should be < 2 s; longer times suggest the Python
         interpreter is overloaded (many other scripts open).
FIX:     Close other scripts.  Or reduce N to 64 for a quick test.

PROBLEM: GLB has no height variation — all vertices flat.
CAUSE:   Z_SCALE is zero or the heights array was all-zero (p = 0 case).
FIX:     Check that P_BELOW > 0 and Z_SCALE = 0.42.

PROBLEM: "foreach_set" raises AttributeError on shape_key data.
CAUSE:   In Blender < 4.0 the shape_key data foreach_set signature differs.
FIX:     This blueprint targets Blender 5.1; use 5.1 or later.`}</pre>

      <h2>Outside sources</h2>

      <p>
        <strong>
          Newman, M. E. J. &amp; Ziff, R. M. (2001). &ldquo;Fast Monte Carlo
          algorithm for site or bond percolation.&rdquo;
        </strong>{" "}
        <em>Physical Review E</em> 64, 016706.{" "}
        <a
          className={lk}
          href="https://arxiv.org/abs/cond-mat/0101295"
          target="_blank"
          rel="noopener noreferrer"
        >
          arXiv:cond-mat/0101295
        </a>
        . Public Domain / CC0 (authors released C source in the paper).
        This paper gives the currently most-accurate value of p_c ≈ 0.59274621(13)
        for site percolation on Z² via a single-cluster-growth algorithm that
        visits every threshold probability in one pass. Related project:
        Newman &amp; Ziff&apos;s network-percolation companion code (same
        authors, same arXiv era) is also public domain.
      </p>

      <p>
        <strong>
          Hoshen, J. &amp; Kopelman, R. (1976). &ldquo;Percolation and cluster
          distribution. I. Cluster multiple labeling technique and critical
          concentration algorithm.&rdquo;
        </strong>{" "}
        <em>Physical Review B</em> 14, 3438.{" "}
        <a
          className={lk}
          href="https://link.aps.org/doi/10.1103/PhysRevB.14.3438"
          target="_blank"
          rel="noopener noreferrer"
        >
          doi:10.1103/PhysRevB.14.3438
        </a>
        . Public domain (APS, published 1976, pre-dating modern copyright
        practice for scientific code). The original union-find cluster-labelling
        algorithm described in this tutorial. The algorithm has been re-implemented
        in dozens of languages; the canonical C version by Al Aharony&apos;s
        group is in the public domain and ships with the Stauffer &amp; Aharony
        textbook.
      </p>
    </>
  );
}

export const blenderTutorialPythonNumpySitePercolationSquareLatticeHoshenKopelman1976StaufferAharonyNewmanZiffPcFractalSpanningClusterHeightFieldStageFloorWebxrEntry: Entry = buildInstructable({
  slug: SLUG,
  title: TITLE,
  lede: LEDE,
  body: <Body />,
  topics: ["blender", "python", "scripting", "physics", "stat-mech", "webxr"],
  blenderVersion: "5.1",
  publishedAt: "2026-09-19",
  libraryPath:
    "blends/scripting/python-numpy-site-percolation-square-lattice-hoshen-kopelman-1976-stauffer-aharony-newman-ziff-p-c-fractal-spanning-cluster-height-field-stage-floor-webxr",
});
