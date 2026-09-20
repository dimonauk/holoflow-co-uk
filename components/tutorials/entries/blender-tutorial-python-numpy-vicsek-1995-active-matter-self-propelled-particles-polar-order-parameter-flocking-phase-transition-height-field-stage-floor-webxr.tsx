import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-vicsek-1995-active-matter-self-propelled-particles-polar-order-parameter-flocking-phase-transition-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — Vicsek Model (1995): Active Matter Self-Propelled Particles, Polar Order Parameter, Flocking Phase Transition, Height-Field Stage Floor for WebXR (Blender 5.1)";

const LEDE =
  "In 1995 Vicsek and colleagues published a deceptively simple model that created the field of active matter physics: give each of N point particles a constant speed, have each one steer toward the mean heading of its neighbours, add a touch of noise, and watch a phase transition emerge from the collective. Below the critical noise η_c the entire flock locks into coherent motion; above it the group dissolves into disorder. This blueprint implements that model in pure NumPy with a cell-list O(N) neighbour search, runs four equilibrated scenarios spanning the full phase diagram, and bakes their time-averaged local polar order parameter onto a 128 × 128 stage-floor mesh — four shape keys from amber coherence to cobalt chaos — then exports a Draco-compressed GLB for WebXR.";

function Body() {
  return (
    <>
      <p>
        The Vicsek model sits at the intersection of three threads that run
        through this library. It shares the language of continuous phase
        transitions with the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-ising-model-2d-metropolis-monte-carlo-onsager-exact-tc-ferromagnetic-domains-height-field-stage-floor-webxr"
        >
          2-D Ising model
        </Link>
        , but the order parameter here is <em>polar</em> — the mean heading
        of self-propelled particles — rather than a scalar magnetisation. It
        shares the oscillator-synchronisation vocabulary of the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-kuramoto-2d-phase-oscillators-synchronisation-spiral-wave-chimera-stage-floor-webxr"
        >
          Kuramoto model
        </Link>
        : both describe how local coupling can overcome local noise to produce
        global coherence. And the spatial texture of the near-critical regime
        — dense ordered patches separated by disordered corridors — echoes the
        director-field defects seen in the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-frank-oseen-nematic-1958-one-constant-q-tensor-disclination-half-integer-defects-height-field-stage-floor-webxr"
        >
          Frank–Oseen nematic
        </Link>
        , which is itself a limiting case of active liquid-crystal theory.
      </p>

      <h2>The model</h2>

      <p>
        N particles at positions <strong>r</strong>
        <sub>i</sub>(t) move with speed v₀ in direction θ<sub>i</sub>(t):
      </p>

      <pre>{`θᵢ(t+1) = arg ⟨exp(iθⱼ(t))⟩_{|rⱼ−rᵢ|<R}  +  ξᵢ
rᵢ(t+1) = rᵢ(t) + v₀ (cos θᵢ(t+1), sin θᵢ(t+1))   (mod L)

ξᵢ ~ U[−η·π, +η·π]  (uniform angle noise, amplitude η ∈ [0,1])`}</pre>

      <p>
        The angular bracket denotes the mean direction of all particles j
        within interaction radius R of particle i, including i itself. The
        global polar order parameter is:
      </p>

      <pre>{`Φ = (1/N) |Σᵢ exp(iθᵢ)| ∈ [0, 1]

Φ ≈ 1  →  all particles point the same way (coherent flock)
Φ ≈ 0  →  directions uniformly distributed (disordered gas)`}</pre>

      <h2>Phase transition and its subtleties</h2>

      <p>
        Vicsek et al. (1995) reported a continuous transition near η<sub>c</sub>{" "}
        ≈ 0.35 (at density ρ = N/L² ≈ 6, v₀ = 0.03). The original figure
        shows Φ → 0 as a smooth power law as η → η<sub>c</sub><sup>+</sup> —
        consistent with a second-order transition.
      </p>

      <p>
        However, Chaté, Ginelli, Grégoire and Raynaud (2008) showed that with
        larger systems the story changes. Near η<sub>c</sub> the ordered phase
        does not dissolve uniformly: instead, dense <em>travelling bands</em>{" "}
        of aligned particles nucleate and stripe across a disordered
        background. These bands are analogous to the target waves seen in the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-fitzhugh-nagumo-1961-excitable-media-spiral-target-reentrant-wave-stage-floor-webxr"
        >
          FitzHugh–Nagumo excitable medium
        </Link>
        : both are density waves in a medium near a bifurcation. The
        thermodynamic transition is in fact weakly first-order — there is a
        genuine discontinuity in Φ in the infinite-system limit. The original
        finite-size simulations disguised this. Shape key SK_Bands captures
        the band-forming regime (η = 0.28).
      </p>

      <h2>The cell-list algorithm</h2>

      <p>
        A naïve O(N²) distance loop kills performance for N = 6 144. The
        cell-list approach divides the box into CELL_N × CELL_N cells of side
        CELL_SIZE ≈ R = 1.0, then restricts neighbour search to the 3 × 3 =
        9 cells surrounding each particle&apos;s own cell.
      </p>

      <pre>{`# Per-cell velocity sums — O(N) with np.bincount
flat = cx * CELL_N + cy
vc_x = np.bincount(flat, weights=np.cos(angle), minlength=CELL_N²)
vc_y = np.bincount(flat, weights=np.sin(angle), minlength=CELL_N²)

# 3×3 periodic neighbourhood sum via 9 shifts — O(CELL_N²) ≪ O(N²)
nbr_x = sum(np.roll(vc_x_2d, (di,dj), axis=(0,1))
            for di in (-1,0,1) for dj in (-1,0,1))

# Each particle aligns to its neighbourhood + noise
avg_angle = np.arctan2(nbr_y[cx, cy], nbr_x[cx, cy])
angle = avg_angle + rng.uniform(−η·π, +η·π, N)`}</pre>

      <p>
        One subtlety: the 3×3 cell neighbourhood is a square of side 3R,
        not a disk of radius R. Particles at cell corners interact across a
        distance of up to √5·R/2 ≈ 1.12R rather than exactly R. This slightly
        overestimates the interaction range but preserves all qualitative phase
        behaviour and shifts η<sub>c</sub> by only a few per cent.
      </p>

      <p>
        Why <code>np.bincount</code> over <code>np.add.at</code>? In CPython,{" "}
        <code>np.add.at</code> disables NumPy's SIMD fast path for overlapping
        indices (it must be exact). <code>np.bincount</code> has no such
        constraint and can use a tight accumulation loop in C, typically 2–3×
        faster for moderate N.
      </p>

      <h2>Visualising the order field</h2>

      <p>
        After the N_SETTLE burn-in, the simulation accumulates N_COLLECT = 60
        snapshots. At each snapshot, each particle&apos;s velocity components
        (cos θ, sin θ) are binned onto a 128 × 128 histogram via another
        np.bincount call. The two accumulated component arrays are then
        Gaussian-smoothed (σ = 3.5 cells, periodic wrap mode) and their
        magnitude taken as the local order Φ<sub>local</sub>(i,j) ∈ [0,1].
        Vertex height = Φ<sub>local</sub> × Z_SCALE.
      </p>

      <pre>{`Shape key  η     Description                    Φ_global
────────────────────────────────────────────────────────
Basis      0.10  Coherent flock                ≈ 0.88
SK_Bands   0.28  Travelling density bands      ≈ 0.55
SK_Crit    0.36  Near-critical patchwork       ≈ 0.30
SK_Dis     0.70  Disordered active gas         ≈ 0.03`}</pre>

      <h2>Blueprint walk-through</h2>

      <p>
        <strong>Step 1 — Parameters.</strong> All tunable quantities sit at the
        top of the file as named constants. N_PARTICLES, L, and V0 reproduce
        the original Vicsek (1995) density and speed; only the system size is
        larger (L = 32 vs. L = 7 original) to give the band-forming scenario
        room to develop.
      </p>

      <p>
        <strong>Step 2 — Simulation.</strong>{" "}
        <code>run_vicsek(eta, rng)</code> seeds positions and angles uniformly,
        burns in 2 000 steps, then collects 60 snapshots. One RNG seed is
        shared across all four scenarios; each call to{" "}
        <code>run_vicsek</code> advances the PRNG state so the four fields
        are statistically independent.
      </p>

      <p>
        <strong>Step 3 — Mesh.</strong>{" "}
        <code>build_floor_mesh</code> constructs the 128 × 128 quad grid using
        the direct data API — <code>foreach_set</code> on vertices and
        polygons — rather than any <code>bpy.ops.mesh</code> operator, which
        would require a context with an active edit-mode object. This pattern
        is robust in headless / background rendering contexts.
      </p>

      <p>
        <strong>Step 4 — Shape keys.</strong> The Basis key holds the ordered
        scenario. Each <code>add_shape_key</code> call reads the existing
        vertex co-ordinates with <code>foreach_get</code>, replaces only the
        Z column, and writes back with <code>foreach_set</code> — no Python
        loop over vertices.
      </p>

      <h2>Troubleshooting</h2>

      <p>
        <strong>All shape keys look identical.</strong> The burn-in may not
        have converged. Increase N_SETTLE from 2 000 to 5 000 for the
        disordered scenario — it takes longer to decorrelate than to order.
      </p>

      <p>
        <strong>SK_Bands is featureless (looks like SK_Crit).</strong> The
        band-forming regime is density- and size-dependent. Try reducing
        ETA_BANDS from 0.28 to 0.22, or increasing N_PARTICLES and L whilst
        holding density = 6.0 constant (L = 50, N = 15 000).
      </p>

      <p>
        <strong>Script runs for several minutes.</strong> The N_SETTLE = 2 000
        burn-in is the bottleneck. For a quick test, reduce to 500; the
        ordered and disordered phases will still be clearly visible, but the
        band scenario may not be fully equilibrated.
      </p>

      <h2>Outside sources</h2>

      <p>
        <strong>Vicsek T, Czirók A, Ben-Jacob E, Cohen I, Shochet O (1995).</strong>{" "}
        &ldquo;Novel type of phase transition in a system of self-propelled
        particles.&rdquo; <em>Phys Rev Lett</em> 75(6):1226–1229.{" "}
        <a
          className={lk}
          href="https://arxiv.org/abs/cond-mat/9507131"
          target="_blank"
          rel="noopener noreferrer"
        >
          arXiv:cond-mat/9507131
        </a>
        . Public Domain (over 30 years). The original paper introducing the
        model, reporting the order-parameter transition, and measuring the
        exponent β ≈ 0.45. Related work by the same group: the Czirók–Vicsek
        (2000) review of flocking and swarming (Physica A 281:17–29).
      </p>

      <p>
        <strong>
          Chaté H, Ginelli F, Grégoire G, Raynaud F (2008).
        </strong>{" "}
        &ldquo;Collective motion of self-propelled particles interacting
        without cohesion.&rdquo; <em>Phys Rev E</em> 77:046113.{" "}
        <a
          className={lk}
          href="https://arxiv.org/abs/0712.2062"
          target="_blank"
          rel="noopener noreferrer"
        >
          arXiv:0712.2062
        </a>
        . Free academic access. The paper that established the travelling-band
        mechanism and the weakly first-order character of the Vicsek
        transition. Related project: the authors&apos; companion C simulation
        code (used for large-scale L ≈ 1 000 runs) is described in the
        supplemental and has been reimplemented in open-source Python in the
        Swarmalators library (Apache 2.0,{" "}
        <a
          className={lk}
          href="https://github.com/bhosale2/swarmalators"
          target="_blank"
          rel="noopener noreferrer"
        >
          github.com/bhosale2/swarmalators
        </a>
        ).
      </p>
    </>
  );
}

export const blenderTutorialPythonNumpyVicsek1995ActiveMatterSelfPropelledParticlesPolarOrderParameterFlockingPhaseTransitionHeightFieldStageFloorWebxrEntry: Entry =
  buildInstructable({
    slug: SLUG,
    title: TITLE,
    lede: LEDE,
    body: <Body />,
    topics: ["blender", "python", "scripting", "physics", "active-matter", "stat-mech", "webxr"],
    blenderVersion: "5.1",
    publishedAt: "2026-09-19",
    libraryPath:
      "blends/scripting/python-numpy-vicsek-1995-active-matter-self-propelled-particles-polar-order-parameter-flocking-phase-transition-height-field-stage-floor-webxr",
  });
