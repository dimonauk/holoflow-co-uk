import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-ising-model-2d-metropolis-monte-carlo-onsager-exact-tc-ferromagnetic-domains-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — 2D Ising Model Metropolis Monte Carlo: Onsager Exact Critical Temperature, Ferromagnetic Domain Coarsening, Height-Field Stage Floor for WebXR (Blender 5.1)";

const LEDE =
  "Lars Onsager solved the 2D Ising model exactly in 1944 and found a critical temperature Tc = 2J / ln(1 + √2) ≈ 2.269 J/k_B — one of the very few closed-form results in statistical mechanics. Below Tc the spins order into cobalt/amber ferromagnetic domains; at Tc the domain boundaries become fractal with no characteristic length scale; above Tc the lattice is a paramagnetic salt-and-pepper. The Metropolis-Hastings algorithm samples from the Boltzmann distribution at any temperature, and by vectorising it on a checkerboard colouring of the lattice we can simulate all four thermal regimes on a 128 × 128 grid, bake the results into shape keys, and drop the whole thing into a Blender scene as a height-field stage floor.";

function Body() {
  return (
    <>
      <p>
        The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-haldane-1988-chern-insulator-berry-curvature-topological-phase-diagram-honeycomb-height-field-stage-floor-webxr"
        >
          Haldane model
        </Link>{" "}
        and the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-kane-mele-2005-quantum-spin-hall-z2-topological-insulator-spin-hall-curvature-honeycomb-height-field-stage-floor-webxr"
        >
          Kane-Mele model
        </Link>{" "}
        are quantum-mechanical, zero-temperature systems with topological order.
        The Ising model is their classical statistical-mechanics cousin: same Z₂
        order parameter (the spin can only be ±1), but now temperature is the
        control parameter and phase order is destroyed by thermal fluctuations
        rather than protected by topology.
      </p>

      <h2>The model and its exact solution</h2>

      <p>The Hamiltonian at zero external field:</p>

      <pre>{`H = −J Σ_{⟨ij⟩} s_i · s_j

s_i ∈ {−1, +1}    (down-spin / up-spin)
⟨ij⟩               nearest neighbours on the square lattice
J > 0              ferromagnetic coupling (like neighbours prefer parallel)`}</pre>

      <p>
        Onsager (1944) solved this model exactly using a transfer-matrix
        approach, a technical tour-de-force that took 33 pages. The punchline:
      </p>

      <pre>{`Tc = 2J / ln(1 + √2)  ≈  2.2692 J/k_B

Critical exponents (exact, 2D Ising universality class):
  β  = 1/8      magnetisation  M ~ |T − Tc|^β       below Tc
  γ  = 7/4      susceptibility χ ~ |T − Tc|^{−γ}
  ν  = 1        correlation length ξ ~ |T − Tc|^{−ν}
  η  = 1/4      G(r) ~ r^{−(d−2+η)}  at Tc
  α  = 0        heat capacity C ~ −A·ln|T − Tc|      (log divergence)`}</pre>

      <p>
        These exponents are universal: they apply to every system in the 2D
        Ising universality class, not just the square lattice. The class is
        defined by Z₂ symmetry breaking in two spatial dimensions. The
        universality class is also realised by the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-allen-cahn-phase-field-mean-curvature-motion-allen-cahn-1979-stage-floor-webxr"
        >
          Allen-Cahn phase field
        </Link>
        , which gives a continuous PDE description of the same domain-coarsening
        dynamics.
      </p>

      <h2>Metropolis-Hastings algorithm</h2>

      <p>
        To sample spin configurations from the Boltzmann distribution
        P(σ) ∝ exp(−H(σ)/k_BT) we use Metropolis (1953):
      </p>

      <pre>{`1. Pick a site i at random.
2. Compute ΔE = 2J · s_i · Σ_{j ∈ nn(i)} s_j
   (ΔE is the energy cost of flipping s_i given its four neighbours)
3. Accept the flip with probability min(1, exp(−ΔE / k_BT)).
4. Repeat for N² steps = one lattice sweep.`}</pre>

      <p>
        The acceptance rule satisfies <em>detailed balance</em>:
        P(σ)·R(σ→σ′) = P(σ′)·R(σ′→σ). This guarantees the Markov chain
        converges to the correct Boltzmann distribution. On a square lattice
        only five values of ΔE are possible (−8J, −4J, 0, +4J, +8J), so we
        precompute the acceptance probabilities and look them up.
      </p>

      <h2>Vectorised checkerboard decomposition</h2>

      <p>
        Sequential site-by-site Metropolis is O(N²) per sweep in Python — very
        slow. The standard fix is the checkerboard (or &ldquo;red-black&rdquo;)
        decomposition:
      </p>

      <pre>{`Colour the N×N lattice like a chess board.
Every "black" site has only "white" nearest neighbours and vice versa.
→ All black-site flip decisions are conditionally independent given white-site values.
→ We can attempt all N²/2 black flips simultaneously with NumPy.
Then do the same for white sites.

One full sweep = one black half-sweep + one white half-sweep.
Detailed balance: identical equilibrium statistics to random-order Metropolis.`}</pre>

      <pre>{`# checkerboard Metropolis, one colour
rows, cols = np.meshgrid(np.arange(N), np.arange(N), indexing="ij")
mask = ((rows + cols) % 2) == parity        # 0 or 1

ri, ci = rows[mask], cols[mask]             # ~N²/2 sites

nn_sum = (spins[(ri+1)%N, ci]
        + spins[(ri-1)%N, ci]
        + spins[ri, (ci+1)%N]
        + spins[ri, (ci-1)%N])

dE     = 2.0 * J * spins[ri, ci] * nn_sum
accept = (dE <= 0) | (rng.random(ri.size) < np.exp(-dE / T))
spins[ri[accept], ci[accept]] *= -1`}</pre>

      <h2>Four shape keys</h2>

      <p>
        The blueprint runs four separate simulations and stores each spin field
        as a height-field shape key.
      </p>

      <pre>{`Basis       T = 0.50 Tc  ≈ 1.135   Deep ferromagnet
                                    ⟨m⟩ ≈ +0.97 (Onsager: m ≈ (1−sinh⁻⁴(2J/T))^{1/8})
                                    Large, compact cobalt/amber domains

SK_Critical T = 1.00 Tc  ≈ 2.269   Onsager critical point
                                    ⟨m⟩ ≈ ±0.05 (finite-size rounds the transition)
                                    Scale-free domain clusters, percolation structure

SK_Hot      T = 1.50 Tc  ≈ 3.404   Paramagnetic phase
                                    ⟨m⟩ ≈ ±0.01  salt-and-pepper random noise
                                    Height approximately uniform at Z_SCALE / 2

SK_Quench   T = 0.25 Tc  ≈ 0.567   Quench from T = ∞ initial condition
                                    Only 2000 sweeps — coarsening arrested mid-way
                                    Visible domain walls as Z-height steps`}</pre>

      <p>
        The quench key is particularly instructive: starting from a fully random
        state and evolving at low temperature, the system minimises energy by
        growing domains, but the coarsening is slow (⟨L⟩ ~ t^{1/2} in the 2D
        Ising universality class, same as the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-allen-cahn-phase-field-mean-curvature-motion-allen-cahn-1979-stage-floor-webxr"
        >
          Allen-Cahn equation
        </Link>
        ). Stopping after 2 000 sweeps freezes the domain wall pattern mid-flight.
      </p>

      <h2>Height encoding and colour map</h2>

      <pre>{`Spin value       Height                  Colour
s_i = −1 (down)  z = 0                   cobalt  (0.027, 0.159, 0.557)
s_i = +1 (up)    z = Z_SCALE = 0.35 m    amber   (0.980, 0.620, 0.050)

Formula: z = ((s + 1) / 2) · Z_SCALE      ∈ [0, 0.35]
         t = (s + 1) / 2                  ∈ {0, 1}
         colour = cobalt + t · (amber − cobalt)`}</pre>

      <p>
        Colour is stored as a <code>FLOAT_COLOR</code> vertex attribute on the{" "}
        <code>POINT</code> domain (one colour per vertex, not per loop), driven
        by a <code>ShaderNodeAttribute</code> node set to{" "}
        <code>&quot;Ising_Spin&quot;</code>. The Principled BSDF uses this for
        both Base Colour and Emission Colour at strength 1.6, so the domains
        glow in WebXR.
      </p>

      <h2>Mesh construction</h2>

      <pre>{`N = 128     →   16 384 vertices,  16 129 quad faces

xs = np.linspace(-WORLD_SCALE, +WORLD_SCALE, N)   # WORLD_SCALE = 4.0 m
ys = np.linspace(-WORLD_SCALE, +WORLD_SCALE, N)
xx, yy = np.meshgrid(xs, ys, indexing="ij")        # row-major

zz = ((spins.astype(float) + 1.0) / 2.0) * Z_SCALE

verts = np.stack([xx.ravel(), yy.ravel(), zz.ravel()], axis=1).tolist()

# CCW quad: (v0, v0+N, v0+N+1, v0+1)
faces = [(ix*N+iy, ix*N+iy+N, ix*N+iy+N+1, ix*N+iy+1)
         for ix in range(N-1) for iy in range(N-1)]`}</pre>

      <p>
        After construction the object is rotated −90° about X and the transform
        applied, putting the mesh into the +Y-up convention used by the
        Holoflow WebXR exporter.
      </p>

      <h2>Holoflow export</h2>

      <pre>{`obj["holoflow:category"] = "stage-floor"
obj["holoflow:facet"]    = True          # flat-shaded facets for the cel look

# GLB export
bpy.ops.export_scene.gltf(
    filepath        = "ising_spin_floor.glb",
    export_format   = "GLB",
    export_draco_mesh_compression_enable = True,
    export_draco_mesh_compression_level  = 6,
    export_image_format = "WEBP",
    export_morph    = True,              # bakes shape keys as morph targets
    export_colors   = True,              # exports FLOAT_COLOR attribute
)`}</pre>

      <h2>Troubleshooting</h2>

      <pre>{`Problem: magnetisation near zero even for T = 0.5 Tc
Fix:     start="ordered" initial condition ensures one domain dominates.
         With start="random" the system can get trapped symmetrically.

Problem: critical cluster looks too uniform (no fractal structure)
Cause:   N_EQUIL too small — lattice not equilibrated at Tc.
Fix:     Increase N_EQUIL to 10_000.  Tc slows down by a factor ξ/a ≫ 1
         (critical slowing down) so equilibration genuinely takes longer.

Problem: shape key heights look identical across all keys
Cause:   foreach_set("co", ...) wrote to wrong shape key slot.
Fix:     Call obj.shape_key_add() BEFORE foreach_set, then target sk.data.

Problem: GLB has no morph targets
Fix:     Confirm export_morph=True and that the object has multiple shape keys.
         The "Basis" key must be key_blocks[0].`}</pre>

      <h2>Outside sources</h2>

      <p>
        <strong>Ising E (1925)</strong> &ldquo;Beitrag zur Theorie des Ferro- und
        Paramagnetismus.&rdquo; <em>Z. Physik</em> 31:253–258. PD (&gt;100 yr).
        Original 1D chain paper (no phase transition); the 2D model was studied
        by Kramers, Wannier, and then solved exactly by Onsager.
        Related: Kramers HA &amp; Wannier GH 1941{" "}
        <em>Phys Rev</em> 60:252–276 (transfer matrix, star-triangle relation).
      </p>

      <p>
        <strong>Onsager L (1944)</strong> &ldquo;Crystal statistics I.&rdquo;{" "}
        <em>Physical Review</em> 65:117–149.{" "}
        doi:<a className={lk} href="https://doi.org/10.1103/PhysRev.65.117">
          10.1103/PhysRev.65.117
        </a>
        . PD (&gt;80 yr). Exact Tc and free energy; the order parameter
        exponent β = 1/8 was derived later by Yang (1952).
        Related: Yang CN 1952 <em>Phys Rev</em> 85:808–816 (spontaneous
        magnetisation); McCoy BM &amp; Wu TT 1973 <em>The Two-Dimensional Ising
        Model</em> Harvard UP (comprehensive reference).
      </p>

      <p>
        <strong>Metropolis N et al. (1953)</strong> &ldquo;Equation of state
        calculations by fast computing machines.&rdquo;{" "}
        <em>Journal of Chemical Physics</em> 21:1087–1092.{" "}
        doi:<a className={lk} href="https://doi.org/10.1063/1.1699114">
          10.1063/1.1699114
        </a>
        . PD (&gt;70 yr). The original Metropolis algorithm.
        Related: Hastings WK 1970 <em>Biometrika</em> 57:97–109 (generalisation);
        Newman MEJ &amp; Barkema GT 1999 <em>Monte Carlo Methods in Statistical
        Physics</em> OUP.
      </p>

      <p>
        <strong>NumPy</strong> BSD-3-Clause.{" "}
        <a className={lk} href="https://numpy.org">numpy.org</a>.
        Harris et al. 2020 <em>Nature</em> 585:357–362.
        Related: SciPy BSD-3-Clause{" "}
        <a className={lk} href="https://github.com/scipy/scipy">
          github.com/scipy/scipy
        </a>
        .
      </p>

      <h2>Studio cross-references</h2>

      <ul>
        <li>
          <Link
            className={lk}
            href="/tutorials/blender-tutorial-python-numpy-allen-cahn-phase-field-mean-curvature-motion-allen-cahn-1979-stage-floor-webxr"
          >
            Allen-Cahn phase field
          </Link>{" "}
          — continuous PDE description of the same Z₂ domain coarsening, same
          ⟨L⟩ ~ t^{1/2} growth law, same universality class.
        </li>
        <li>
          <Link
            className={lk}
            href="/tutorials/blender-tutorial-python-numpy-gierer-meinhardt-activator-inhibitor-turing-morphogenesis-1972-spot-stripe-height-field-stage-floor-webxr"
          >
            Gierer-Meinhardt activator-inhibitor
          </Link>{" "}
          — Turing-class pattern formation, also driven by a reaction-diffusion
          instability, also produces domain-like structures on the height field.
        </li>
        <li>
          <Link
            className={lk}
            href="/tutorials/blender-tutorial-python-numpy-gray-scott-1984-pearson-1993-activator-depletion-turing-spot-worm-hole-height-field-stage-floor-webxr"
          >
            Gray-Scott reaction-diffusion
          </Link>{" "}
          — twelve distinct morphologies, some visually similar to the critical
          Ising percolation cluster.
        </li>
        <li>
          <Link
            className={lk}
            href="/tutorials/blender-tutorial-python-numpy-haldane-1988-chern-insulator-berry-curvature-topological-phase-diagram-honeycomb-height-field-stage-floor-webxr"
          >
            Haldane Chern insulator
          </Link>{" "}
          — quantum phase transition (Chern number C = 0 ↔ 1) also driven by a
          single control parameter, but the order is topological not spontaneous.
        </li>
        <li>
          <Link
            className={lk}
            href="/tutorials/blender-tutorial-python-numpy-ssh-su-schrieffer-heeger-1979-zak-phase-topological-edge-states-spectral-flow-stage-floor-webxr"
          >
            SSH model
          </Link>{" "}
          — 1D topological insulator with a Z winding number, the 1D analogue
          of the Z₂ Ising order parameter.
        </li>
      </ul>
    </>
  );
}

export const blenderTutorialPythonNumpyIsingModel2dMetropolisMonteCarloOnsagerExactTcFerromagneticDomainsHeightFieldStageFloorWebxrEntry: Entry =
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
      "ising-model",
      "monte-carlo",
      "phase-transition",
      "webxr",
      "stage-floor",
    ],
    body: Body,
  });
