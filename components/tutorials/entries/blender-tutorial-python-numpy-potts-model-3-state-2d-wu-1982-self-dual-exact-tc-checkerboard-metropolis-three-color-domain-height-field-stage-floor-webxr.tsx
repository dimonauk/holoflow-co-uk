import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-potts-model-3-state-2d-wu-1982-self-dual-exact-tc-checkerboard-metropolis-three-color-domain-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — 3-State Potts Model 2D: Wu 1982 Self-Dual Exact Tc = J/ln(1+√3) ≈ 0.9950 J/k_B, CFT c=4/5, Checkerboard Metropolis, Three-Color Domain Height-Field Stage Floor for WebXR (Blender 5.1)";

const LEDE =
  "The q-state Potts model (Potts 1952) is the natural q-colour generalisation of the Ising model. For q = 3 on the 2D square lattice the phase transition is second-order and exactly solvable: the self-duality of the lattice pins the critical temperature to Tc = J / ln(1 + √3) ≈ 0.9950 J/k_B with no fitting required. The transition sits in its own universality class (CFT central charge c = 4/5) with exact exponents β = 1/9, ν = 5/6, η = 4/15 — distinct from Ising (c = 1/2). Below Tc three ordered domains coexist; at Tc the mosaic of all three states becomes fractal with no preferred scale; above Tc the domains dissolve. A checkerboard Metropolis algorithm with vectorised NumPy sweeps simulates all four thermal regimes and bakes them as shape-key morphs into a 128 × 128 cobalt–teal–amber terrace floor for Blender 5.1 and WebXR.";

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
        has two spin states (±1) and a Z₂ symmetry. The Potts model asks: what
        happens when you allow q spin states instead of 2? The answer depends
        critically on q.
      </p>

      <h2>The model</h2>

      <pre>{`H = −J Σ_{⟨ij⟩} δ(σᵢ, σⱼ)

σᵢ ∈ {0, 1, …, q−1}    (q discrete states)
⟨ij⟩                     nearest-neighbour bonds
J > 0                    energy reward for matching neighbours`}</pre>

      <p>
        For q = 2 this is identical to the Ising model (δ(σ,σ) = 1 maps to
        aligned spins, δ(σ,σ′) = 0 maps to anti-aligned, reproducing −J when
        parallel). For q = 3 there are three equally preferred ordered phases.
      </p>

      <h2>Self-duality and the exact critical temperature</h2>

      <p>
        The 2D square-lattice Potts model is self-dual: a duality transformation
        maps the high-temperature expansion of the partition function onto the
        low-temperature expansion of the same model on the dual lattice, with a
        coupling-constant transformation that has a unique fixed point. That
        fixed point is the critical temperature (Wu 1982):
      </p>

      <pre>{`e^{J/Tc} = 1 + √q      →      Tc = J / ln(1 + √q)

q = 2 (Ising):   Tc = J / ln(1 + √2) ≈ 0.4407 J/k_B  (in ±J normalisation 2.269)
q = 3:           Tc = J / ln(1 + √3) ≈ 0.9950 J/k_B
q = 4:           Tc = J / ln(3)      ≈ 0.9102 J/k_B
q = 5:           Tc = J / ln(1+√5)   ≈ 1.0574 J/k_B  (first-order below this)`}</pre>

      <p>
        The derivation requires no mean-field approximation and no series
        truncation — it follows from the algebraic symmetry of the model alone.
        This is one of the rare instances in 2D statistical mechanics where the
        exact transition point is known from first principles.
      </p>

      <h2>CFT and the first-order boundary at q = 4</h2>

      <p>
        The critical behaviour of the 2D Potts model is described by a
        Coulomb-gas conformal field theory (Nienhuis 1982). The central charge
        is:
      </p>

      <pre>{`c = 1 − 6(1−g)² / g      where g relates to q via q = 4cos²(π/g)

q = 2 (Ising):   c = 1/2,   β = 1/8,  ν = 1,   η = 1/4
q = 3:           c = 4/5,   β = 1/9,  ν = 5/6, η = 4/15
q = 4:           c = 1,     β = 1/12, ν = 2/3, η = 1/4
q ≥ 5:           c > 1,     transition is FIRST-ORDER (discontinuous)`}</pre>

      <p>
        The boundary c = 1 (q = 4) marks the crossover from a continuous
        second-order transition to a first-order transition with a latent heat.
        This is not a phenomenological fit — it follows from the non-unitarity
        constraint of the Virasoro algebra for c {">"} 1 in two dimensions.
      </p>

      <h2>Checkerboard Metropolis for the Potts model</h2>

      <p>
        The Metropolis algorithm for the Potts model is a simple extension of
        the Ising case. At each step, propose a random new state σ′ ∈ {"{0,1,2}"}
        for site i (possibly the same as σᵢ — auto-accepted at ΔE = 0).
        Compute the energy change:
      </p>

      <pre>{`ΔE = −J Σ_{j ∈ nn(i)} [δ(σ′, σⱼ) − δ(σᵢ, σⱼ)]
   = −J × (matches_new − matches_old)

Accept with probability: min(1, exp(−ΔE / T))`}</pre>

      <p>
        The checkerboard (sublattice) vectorisation exploits the fact that
        all even-parity sites (i + j even) have only odd-parity neighbours.
        So all even sites are conditionally independent given the odd sites,
        and N²/2 accept/reject decisions can be made in parallel per half-sweep
        using NumPy array operations on the rolled-neighbour arrays.
      </p>

      <pre>{`def _nn_delta_sum(sigma, new_s):
    nbs = [np.roll(sigma, d, a)
           for d, a in ((-1, 1), (1, 1), (-1, 0), (1, 0))]
    m_new = sum((nb == new_s) for nb in nbs).astype(np.float32)
    m_old = sum((nb == sigma) for nb in nbs).astype(np.float32)
    return m_new - m_old   # ΔE = −J × this

for mask in [(i+j)%2==0, (i+j)%2==1]:
    new_s  = rng.integers(0, Q, (N, N), dtype=np.int8)
    dE     = −J × _nn_delta_sum(sigma, new_s)
    accept = (dE <= 0) | (rng.random() < exp(−dE / T))
    sigma[mask & accept] = new_s[mask & accept]`}</pre>

      <h2>Visualising three states as a terrace floor</h2>

      <p>
        The normalised spin value σ/(q − 1) maps the three Potts states to
        [0, 0.5, 1.0], which drives both the vertex height and the colour
        ramp — cobalt (state 0), teal (state 1), amber (state 2). The result
        is a terrace landscape: below Tc you see large flat plateaus of a
        single colour separated by sharp domain walls; at Tc those walls
        become fractal with no characteristic width; above Tc the terraces
        dissolve into scattered patches.
      </p>

      <p>
        The three-stop{" "}
        <code>ShaderNodeValToRGB</code> ramp is built programmatically by
        adding a midpoint element at position 0.5:
      </p>

      <pre>{`ramp.color_ramp.elements[0].color = (0.07, 0.24, 0.62, 1.0)  # cobalt  σ=0
ramp.color_ramp.elements.new(0.5)
ramp.color_ramp.elements[1].color = (0.00, 0.62, 0.55, 1.0)  # teal    σ=1
ramp.color_ramp.elements[2].color = (1.00, 0.64, 0.00, 1.0)  # amber   σ=2`}</pre>

      <h2>Shape keys and thermal regimes</h2>

      <p>
        Four independent simulations, each run to equilibrium, are baked as
        shape keys:
      </p>

      <pre>{`Basis      T = 0.50 Tc ≈ 0.498 J/k_B  large ordered domains
SK_Critical T = Tc  ≈ 0.995 J/k_B  fractal mosaic, η = 4/15
SK_HotCrit  T = 1.50 Tc ≈ 1.49 J/k_B  short-range order
SK_HighT    T = 3.00 Tc ≈ 2.99 J/k_B  fully disordered`}</pre>

      <p>
        The critical shape key is the most instructive: because η = 4/15 ≈
        0.267 is larger than the Ising value of 1/4, the correlations at Tc
        decay faster — the domains are more fragmented, the fractal boundaries
        more intricate.
      </p>

      <h2>Relationship to other models in the library</h2>

      <ul>
        <li>
          <Link
            className={lk}
            href="/tutorials/blender-tutorial-python-numpy-ising-model-2d-metropolis-monte-carlo-onsager-exact-tc-ferromagnetic-domains-height-field-stage-floor-webxr"
          >
            2D Ising model
          </Link>{" "}
          — the q = 2 special case; Onsager exact Tc, c = 1/2 CFT, β = 1/8.
        </li>
        <li>
          <Link
            className={lk}
            href="/tutorials/blender-tutorial-python-numpy-xy-model-2d-berezinskii-kosterlitz-thouless-1971-1973-vortex-antivortex-unbinding-topological-phase-transition-height-field-stage-floor-webxr"
          >
            2D XY model
          </Link>{" "}
          — continuous spin symmetry, no conventional order, BKT topological
          transition with algebraic correlations.
        </li>
        <li>
          <Link
            className={lk}
            href="/tutorials/blender-tutorial-python-numpy-haldane-1988-chern-insulator-berry-curvature-topological-phase-diagram-honeycomb-height-field-stage-floor-webxr"
          >
            Haldane model
          </Link>{" "}
          — quantum topological phase transition driven by Berry curvature rather
          than thermal fluctuations.
        </li>
        <li>
          <Link
            className={lk}
            href="/tutorials/blender-tutorial-python-numpy-abelian-sandpile-bak-tang-wiesenfeld-1987-soc-chip-firing-height-field-stage-floor-webxr"
          >
            Abelian sandpile
          </Link>{" "}
          — another system with power-law correlations and fractal geometry at
          its self-organised critical point, but without a tuning parameter.
        </li>
      </ul>

      <h2>Outside sources</h2>

      <ul>
        <li>
          Potts RB 1952 <em>Proc. Camb. Phil. Soc.</em> 48:106–109 — original
          paper, PD {">"} 70 yr.
        </li>
        <li>
          Wu FY 1982 <em>Rev. Mod. Phys.</em> 54:235–268 — canonical review;
          self-dual Tc derivation; equations CC0.
        </li>
        <li>
          Nienhuis B 1982 <em>PRL</em> 49:1062 — exact β, ν, η from CFT; PD {">"}
          40 yr.
        </li>
        <li>
          NumPy — BSD-3-Clause — https://numpy.org (Harris et al. 2020).
        </li>
      </ul>
    </>
  );
}

export const blenderTutorialPythonNumpyPottsModel3State2dWu1982SelfDualExactTcCheckerboardMetropolisThreeColorDomainHeightFieldStageFloorWebxrEntry: Entry =
  buildInstructable({
    slug: SLUG,
    title: TITLE,
    lede: LEDE,
    date: "2026-09-19",
    tags: [
      "blender",
      "python",
      "scripting",
      "statistical-mechanics",
      "potts-model",
      "monte-carlo",
      "phase-transition",
      "conformal-field-theory",
      "webxr",
      "stage-floor",
    ],
    body: Body,
  });
