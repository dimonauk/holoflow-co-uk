import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-dla-diffusion-limited-aggregation-witten-sander-1981-fractal-growth-dendritic-crystal-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — Diffusion-Limited Aggregation: Witten & Sander 1981 Fractal Dendritic Crystal Growth, D_f≈1.71, Height-Field Stage Floor for WebXR (Blender 5.1)";

const LEDE =
  "Tom Witten and Len Sander published a two-page letter in 1981 that accidentally explained snowflakes, lightning channels, mineral dendrites, and electrodeposited zinc in one algorithm: release a random walker from a far-away circle, let it diffuse until it touches a seed particle, and let it stick permanently. After 2 000 walkers the cluster has a fractal dimension D_f ≈ 1.71 — a number that appears, universally, across wildly different physical systems. This blueprint runs the full on-lattice DLA simulation in NumPy inside Blender 5.1, bakes four growth stages into shape keys with cobalt-to-amber temporal colouring, and exports a 128 × 128 quad-grid stage floor as a Draco-compressed GLB ready for WebXR.";

function Body() {
  return (
    <>
      <p>
        The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-bak-tang-wiesenfeld-1987-abelian-sandpile-self-organised-criticality-avalanche-power-law-height-field-stage-floor-webxr"
        >
          BTW sandpile
        </Link>{" "}
        achieves self-organised criticality through deterministic toppling rules.
        DLA achieves fractal growth through stochastic diffusion. Both are
        parameter-free — no coupling constant, no temperature dial. The
        fractal geometry emerges from the walk itself.
      </p>

      <h2>The model</h2>

      <p>
        Place a 128 × 128 integer grid. Seed one particle at the centre.
        Repeat until <em>N</em> walkers have stuck:
      </p>

      <pre>{`1. Choose theta ∈ [0, 2π) uniformly at random.
2. Launch walker from (cx + r_launch·cos θ, cy + r_launch·sin θ),
   where r_launch = r_cluster + 5.
3. Random walk: each step is N/S/E/W chosen uniformly.
4. If any 4-neighbour of (x, y) is in the cluster:
       cluster[x, y] = True
       arrival[x, y] = num_stuck / N  (normalised arrival time)
       update r_cluster
       break
5. If distance(walker, centre) > r_kill: discard, go to step 1.`}</pre>

      <p>
        The adaptive launch radius matters. A walker launched at a fixed
        large radius when the cluster is small wastes O(r²) steps on
        straight-line diffusion. Starting 5 cells beyond the current cluster
        tip keeps the average walk length roughly constant as the cluster grows.
      </p>

      <h2>Why the tips grow fastest</h2>

      <p>
        The walker&apos;s path is a random walk, and random walks in 2D have a
        probability density that satisfies the Laplace equation far from the
        cluster. The flux of walkers hitting any surface element is proportional
        to the local gradient of that density. At a protruding tip the gradient
        is steeper than in a screened fjord — so tips receive more walkers per
        unit time. Tips grow; fjords starve. This feedback is the screened
        growth instability, and it is mathematically identical to the dielectric
        breakdown model and to viscous fingering in a Hele-Shaw cell.
      </p>

      <h2>Fractal dimension D_f ≈ 1.71</h2>

      <p>
        Count cluster mass <em>N</em> inside a circle of radius <em>r</em>:
      </p>

      <pre>{`N(r) ~ r^{D_f},   D_f ≈ 1.71`}</pre>

      <p>
        D_f = 1.71 sits between a line (D=1) and a filled disc (D=2). The
        cluster is denser than a simple curve but too branchy to fill the plane.
        Paul Meakin confirmed this value computationally in 1983 for large
        off-lattice clusters. Turkevich and Scher (1985) derived it from a
        fixed-point of the screened growth equation. It is the same across
        on-lattice square, triangular, and honeycomb geometries, and across
        off-lattice continuous simulations — universality in the strictest sense.
      </p>

      <p>
        The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-kpz-kardar-parisi-zhang-1986-stochastic-surface-growth-universality-height-field-stage-floor-webxr"
        >
          KPZ equation
        </Link>{" "}
        describes stochastic surface growth in a different universality class
        (β ≈ 0.24 in 2D). DLA is not in the KPZ class — the walker&apos;s
        diffusive screening is a non-local effect absent from the local KPZ
        noise term.
      </p>

      <h2>Blueprint walkthrough</h2>

      <p>
        Open <code>blueprint.py</code> in Blender 5.1&apos;s Scripting workspace
        and press <strong>Run Script</strong>.
      </p>

      <h3>Step 1 — run DLA</h3>

      <pre>{`rng     = np.random.default_rng(SEED)  # reproducible
arrival = run_dla(N_BASIS, rng)         # float32 [N, N], range (0, 1]`}</pre>

      <p>
        <code>run_dla</code> returns an N×N float32 array. Empty cells hold 0.
        Cluster cells hold <code>num_stuck / N_BASIS</code> — the seed particle
        gets the smallest value (≈ 0.0005) and the last-stuck walker gets 1.0.
        Arrival order encodes <em>time</em>, not position.
      </p>

      <h3>Step 2 — build the quad grid</h3>

      <pre>{`build_height_field_mesh(MESH_NAME)
# → N×N vertices, (N−1)×(N−1) quads, all z=0 initially`}</pre>

      <p>
        The mesh uses the direct BMesh API rather than
        <code>bpy.ops.mesh.primitive_grid_add</code> because the operator
        applies the active object&apos;s matrix, which can silently bake an
        unwanted rotation into vertex positions. Direct vertex creation is
        context-independent.
      </p>

      <h3>Step 3 — shape keys</h3>

      <pre>{`apply_shape_key(obj, "Basis",      arrival)
apply_shape_key(obj, "SK_Small",   mask_arrival(arrival, 400,  2000))
apply_shape_key(obj, "SK_Mid",     mask_arrival(arrival, 1200, 2000))
apply_shape_key(obj, "SK_Inverse", inv)   # core high, tips low`}</pre>

      <p>
        <code>mask_arrival(arrival, n_show, n_total)</code> zeroes out all
        arrivals later than <code>n_show / n_total</code>, effectively
        &lsquo;rewinding&rsquo; the cluster to an earlier growth stage without
        re-running the simulation. The SK_Inverse key swaps the height
        encoding so the seed becomes the peak — useful for a coral or
        lightning-tree silhouette.
      </p>

      <h3>Step 4 — colour attribute</h3>

      <pre>{`COBALT = (0.027, 0.141, 0.557, 1.0)  # oldest → seed
AMBER  = (0.980, 0.620, 0.050, 1.0)  # youngest → branch tips
colour = mix(COBALT, AMBER, arrival[j, i])`}</pre>

      <p>
        FLOAT_COLOR vertex colours survive Draco compression without the
        4-bit banding that plagues BYTE_COLOR attributes. The gamma node
        in the shader (γ = 0.45) lifts the perceptual mid-tone without
        blowing out the amber tips.
      </p>

      <p>
        Compare the colouring approach with the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-gray-scott-1984-pearson-1993-activator-depletion-turing-spot-worm-hole-height-field-stage-floor-webxr"
        >
          Gray–Scott reaction-diffusion blueprint
        </Link>
        , which also uses a cobalt-to-amber gradient but maps it to
        activator concentration rather than growth-time.
      </p>

      <h2>Shape key visual guide</h2>

      <pre>{`Basis      — 2 000 particles; cobalt core, amber tips
SK_Small   — 400 particles; 3–5 primary arms, no secondary branches
SK_Mid     — 1 200 particles; secondary branching visible, fjords forming
SK_Inverse — 2 000 particles; core = max height; reads as a mountain`}</pre>

      <h2>Physical applications</h2>

      <p>
        Electrodeposition is the laboratory canonical: dissolve zinc sulphate
        in water, pass a current between two copper plates, photograph the
        cathode surface every 30 seconds. The deposit matches DLA fractal
        statistics to within measurement error (Brady & Ball 1984). Snowflake
        growth follows DLA in the diffusion-limited regime before surface
        tension corrections become relevant. Lightning selects the path of
        least resistance through a stochastic dielectric-breakdown process
        mathematically equivalent to DLA. Mineral dendrites — those fern-like
        black patterns in limestone — are pyrolusite (MnO₂) deposited at a
        rock–water interface via slow diffusion.
      </p>

      <p>
        The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-cahn-hilliard-phase-field-spinodal-decomposition-1958-height-field-stage-floor-webxr"
        >
          Cahn–Hilliard spinodal decomposition
        </Link>{" "}
        is another diffusion-controlled growth process, but it is conservative
        (total concentration is fixed) and produces labyrinthine coarsening
        rather than fractal dendrites, because the driving force is a bulk
        free-energy gradient rather than a Laplacian screening field.
      </p>

      <h2>Troubleshooting</h2>

      <pre>{`Cluster looks too compact (no fractal arms)
  → Reduce r_kill or remove the kill radius entirely.
    With r_kill = ∞ each particle walks until it sticks, which
    produces a correct DLA cluster but runs ~5× slower.

Script hangs (never terminates)
  → The cluster has touched the grid edge. Reduce N_BASIS or
    increase N to give more room.

Shape keys snap instead of blending smoothly in the viewport
  → In the Shape Keys panel set Interpolation to "Key (Ease In/Out)"
    before scrubbing the value slider.

GLB has banding in vertex colours
  → Ensure export_colors=True and that the attribute is FLOAT_COLOR
    not BYTE_COLOR. Verify draco_level ≤ 6; level 7 can degrade colours.`}</pre>

      <h2>Outside sources</h2>

      <p>
        The original paper:{" "}
        <a
          className={lk}
          href="https://doi.org/10.1103/PhysRevLett.47.1400"
          target="_blank"
          rel="noopener noreferrer"
        >
          Witten & Sander 1981, Phys. Rev. Lett. 47:1400
        </a>{" "}
        (Public Domain). The fractal dimension measurement:{" "}
        <a
          className={lk}
          href="https://doi.org/10.1103/PhysRevA.27.1495"
          target="_blank"
          rel="noopener noreferrer"
        >
          Meakin 1983, Phys. Rev. A 27:1495
        </a>{" "}
        (Public Domain). Numerical computing provided by{" "}
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

export const blenderTutorialPythonNumpyDlaDiffusionLimitedAggregationWittenSander1981FractalGrowthDendriticCrystalHeightFieldStageFloorWebxrEntry: Entry =
  buildInstructable({
    slug: SLUG,
    date: "2026-09-19",
    title: TITLE,
    lede: LEDE,
    tags: [
      "scripting",
      "fractals",
      "diffusion",
      "stochastic",
      "growth",
      "dendritic",
      "webxr",
      "stage-floor",
    ],
    body: Body,
  });
