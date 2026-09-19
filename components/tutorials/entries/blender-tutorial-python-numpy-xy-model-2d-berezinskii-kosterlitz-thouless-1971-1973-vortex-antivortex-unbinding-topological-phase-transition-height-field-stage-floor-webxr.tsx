import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-xy-model-2d-berezinskii-kosterlitz-thouless-1971-1973-vortex-antivortex-unbinding-topological-phase-transition-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — 2D XY Model Berezinskii-Kosterlitz-Thouless Transition: Vortex-Antivortex Unbinding, Topological Phase Transition, Height-Field Stage Floor for WebXR (Blender 5.1)";

const LEDE =
  "The Berezinskii-Kosterlitz-Thouless transition is one of the most surprising results in statistical mechanics: a phase transition that has no order parameter, no symmetry breaking, and an essential singularity that makes every Landau-theory derivative continuous at the critical temperature. What changes is purely topological — pairs of vortex-antivortex excitations that are tightly bound below T_BKT ≈ 0.8935 J/k_B unbind and proliferate above it, destroying the algebraic long-range order. The 2016 Nobel Prize in Physics was awarded to Kosterlitz and Thouless for this discovery. This tutorial runs a checkerboard-vectorised Metropolis Monte Carlo simulation of the 2D classical XY model, detects vortices via plaquette winding numbers, encodes cos(θ(x,y)) as a 128 × 128 height-field mesh, and bakes four thermal snapshots into shape keys for a stage-floor object ready to drop into a WebXR scene.";

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
        has a discrete Z₂ spin and a conventional symmetry-breaking phase
        transition at Onsager&apos;s exact critical temperature. The 2D XY model
        replaces the binary spin with a continuous angle θ ∈ [0, 2π) — a unit
        vector that can point anywhere in the plane. This seemingly small change
        has a profound consequence: the Mermin-Wagner theorem (1966) proves that
        no continuous symmetry can be spontaneously broken in two dimensions at
        any finite temperature. There is no ferromagnetic ordered phase, ever.
      </p>

      <p>
        And yet the 2D XY universality class exhibits a sharp phase transition.
        Superfluid helium films, Josephson junction arrays, and planar magnets
        all show a clear critical point. Berezinskii (1971) and Kosterlitz and
        Thouless (1973) resolved the paradox: the transition is topological, not
        magnetic. The relevant excitations are{" "}
        <em>vortices</em> — configurations in which the phase angle θ winds by
        ±2π as you walk a closed loop around a plaquette. Paired
        vortex-antivortex configurations bind below a critical temperature
        T_BKT; above it they unbind and proliferate freely. This is the
        BKT transition.
      </p>

      <p>
        This tutorial belongs to the topological physics series alongside the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-haldane-1988-chern-insulator-berry-curvature-topological-phase-diagram-honeycomb-height-field-stage-floor-webxr"
        >
          Haldane Chern insulator
        </Link>{" "}
        and the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-kane-mele-2005-quantum-spin-hall-z2-topological-insulator-spin-hall-curvature-honeycomb-height-field-stage-floor-webxr"
        >
          Kane-Mele quantum spin Hall insulator
        </Link>
        . Those are quantum systems at zero temperature; BKT is classical and
        thermal, which makes the vortex physics more tangible and the Monte
        Carlo simulation straightforward to write from scratch.
      </p>

      <h2>The Hamiltonian</h2>

      <pre>{`H = −J Σ_{⟨ij⟩} cos(θᵢ − θⱼ)

θᵢ ∈ [0, 2π)          — spin angle at site i
⟨ij⟩                  — nearest-neighbour pairs on the square lattice
J > 0                  — ferromagnetic coupling (aligned spins lower energy)`}</pre>

      <p>
        The ground state is θᵢ = const (all spins parallel), which has energy
        −2NJ per site. At any finite temperature, spin-wave fluctuations roughen
        this state. Because the spin is continuous the low-energy excitations are
        acoustic: a spin-wave of wavevector k costs energy ~ Jk², so long-wavelength
        fluctuations are cheap and, in 2D, destroy any Bragg peak. This is the
        Mermin-Wagner theorem in action.
      </p>

      <h2>Vortex topology and the BKT mechanism</h2>

      <p>
        Beyond spin waves the field admits topological excitations with integer
        winding number. A single vortex of charge q = +1 has:
      </p>

      <pre>{`θ(r, φ) = φ + const      (φ = azimuthal angle around vortex core)

Energy of an isolated vortex: E_v = π J ln(L/a)
  L = system size,  a = lattice spacing

Cost diverges logarithmically with L — an isolated vortex cannot exist in
a large system at finite temperature.`}</pre>

      <p>
        However, a bound <em>vortex-antivortex pair</em> has a finite binding
        energy proportional to the pair separation. The free energy of a pair at
        separation r is:
      </p>

      <pre>{`F(r) = E(r) − T·S(r)
     = 2π J ln(r/a) − 2k_B T ln(r/a)
     = (2π J − 2k_B T) ln(r/a)

F increases with r  when  T < π J / k_B = T_BKT     → pairs stay bound
F decreases with r  when  T > T_BKT                 → pairs unbind, gain entropy`}</pre>

      <p>
        The entropy of a vortex grows as 2k_B ln(r/a) because the vortex can sit
        at any of ~(r/a)² sites. At T_BKT the entropic and energetic terms
        exactly balance — this is the Kosterlitz-Thouless argument at its
        simplest. The true transition temperature on the square lattice, found by
        Monte Carlo, is T_BKT ≈ 0.8935 J/k_B rather than π/2 ≈ 1.571 J/k_B
        because the renormalised coupling J decreases with temperature.
      </p>

      <h2>Correlation functions</h2>

      <pre>{`Below T_BKT:   G(r) = ⟨cos(θ₀ − θᵣ)⟩ ~ r^{−η(T)}
                η(T) = k_BT / (2π J_R(T))   where J_R is the renormalised coupling
                η(T_BKT⁻) = 1/4  (universal, from the renormalisation group)

Above T_BKT:   G(r) ~ exp(−r / ξ)
                ξ ~ exp(b / √(T − T_BKT))   (essential singularity — all derivatives
                                              of ξ are continuous at T_BKT)

The essential singularity means the BKT transition is of infinite order:
no Landau theory can capture it because every C^∞ function of T−T_BKT
is analytic, while exp(−c/√x) has zero Taylor radius at x = 0.`}</pre>

      <h2>The Nelson-Kosterlitz universal jump</h2>

      <p>
        The helicity modulus ρs (superfluid stiffness) measures the free-energy
        cost of a small twist imposed across the system. Nelson and Kosterlitz
        (1977) showed that ρs vanishes above T_BKT but jumps discontinuously to
        a universal value just below it:
      </p>

      <pre>{`lim_{T → T_BKT⁻} ρs(T) / T_BKT = 2/π ≈ 0.6366

This universal number was measured experimentally by Bishop and Reppy (1978)
in thin ⁴He films adsorbed on Mylar, confirming the BKT theory.`}</pre>

      <h2>Monte Carlo algorithm — checkerboard Metropolis</h2>

      <p>
        For the continuous XY spin the standard Metropolis move proposes a
        random angle perturbation:
      </p>

      <pre>{`1. Pick a site i (or a checkerboard sublattice simultaneously).
2. Propose  θᵢ_new = θᵢ + δ,   δ ~ Uniform(−Δ, +Δ),  Δ = π/4.
3. Compute  ΔE = −J Σ_{j ∈ nn(i)} [cos(θᵢ_new − θⱼ) − cos(θᵢ − θⱼ)].
4. Accept with probability min(1, exp(−ΔE / k_BT)).`}</pre>

      <p>
        The move width Δ = π/4 is a practical choice: wide enough to decorrelate
        efficiently, narrow enough not to waste too many proposals. At T ≈ T_BKT
        the optimal Δ is slightly narrower; π/4 gives ≈ 50% acceptance there.
      </p>

      <p>
        The checkerboard decomposition vectorises this over the entire sublattice
        at once. Sites of the same parity share no nearest neighbours, so
        updating all of them simultaneously still satisfies detailed balance
        exactly. This is the same trick used in the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-ising-model-2d-metropolis-monte-carlo-onsager-exact-tc-ferromagnetic-domains-height-field-stage-floor-webxr"
        >
          Ising model tutorial
        </Link>
        , extended here to continuous angles.
      </p>

      <h2>Vortex detection — plaquette winding number</h2>

      <pre>{`For each plaquette (i,j) → (i,j+1) → (i+1,j+1) → (i+1,j), compute:

  Winding = Σ wrap(Δθ_bond)   for the four directed bonds

  wrap(x) = ((x + π) mod 2π) − π   (maps to (−π, π])

  q = round(Winding / 2π)  ∈ {−1, 0, +1}

A plaquette with q = +1 is a vortex core; q = −1 is an antivortex core.
The total charge Σ q = 0 always (periodic boundary conditions).`}</pre>

      <p>
        This discrete winding number is the lattice analogue of
        q = (1/2π) ∮ ∇θ · dl. On a periodic lattice the winding is an integer
        because θ is single-valued. Vortices and antivortices always come in
        pairs (Σ q = 0 by Stokes&apos; theorem on the torus).
      </p>

      <h2>Height field visualisation — cos(θ)</h2>

      <p>
        We map the scalar cos(θ(x,y)) to the mesh height z = (cos θ + 1)/2 ×
        Z_SCALE. This choice makes vortex topology visible: each vortex is a
        phase singularity with θ winding by 2π, so cos(θ) traces a full
        oscillation as you orbit the core. Below T_BKT this produces paired
        ripple signatures; above T_BKT the ripples become isolated spirals
        scattered across the field.
      </p>

      <pre>{`Below T_BKT (Basis):  large-scale smooth undulations from spin waves
                       a few faint paired bumps from tightly bound vortices

At T_BKT (SK_BKT):    fine-scale ripples, characteristic power-law texture
                       vortex pairs separated by ~5-10 lattice spacings

Above T_BKT (SK_Unbound): isolated spirals, disordered background
                          free vortices visible as sharp amber peaks

High T (SK_HighT):    random salt-and-pepper, no spatial correlation`}</pre>

      <p>
        The cobalt-to-amber colour ramp maps cos θ ≈ −1 (anti-aligned spin,
        z = 0) to cobalt and cos θ ≈ +1 (aligned spin, z = Z_SCALE) to amber.
        Vortex cores receive a white highlight because the nearby phase winding
        sweeps through all values rapidly, raising the local cos-field variance.
        This technique is similar to the vortex visualisation in the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-gross-pitaevskii-bec-rotating-vortex-lattice-abrikosov-imaginary-time-stage-floor-webxr"
        >
          Gross-Pitaevskii BEC vortex lattice
        </Link>
        , where quantum vortices appear as density-depleted cores.
      </p>

      <h2>Blueprint walkthrough</h2>

      <pre>{`# --- constants ---
N        = 128
T_BKT    = 0.8935          # Hasenbusch 2005
DELTA    = π/4             # Metropolis move width
N_EQUIL  = 8_000           # equilibration sweeps
N_PROD   = 2_000           # production sweeps

# --- checkerboard mask ---
ii, jj  = np.mgrid[0:N, 0:N]
mask_0  = (ii + jj) % 2 == 0
mask_1  = ~mask_0

# --- one Monte Carlo sweep ---
for mask in (mask_0, mask_1):
    delta           = rng.uniform(-DELTA, DELTA, (N, N))
    delta[~mask]    = 0.0
    cos_new = Σ_nn cos(θ_new − θ_nn)   # four rolling sums
    cos_old = Σ_nn cos(θ     − θ_nn)
    dE      = −J * (cos_new − cos_old)
    accept  = (dE ≤ 0) | (rng.random() < exp(−dE/T))
    accept &= mask
    theta[accept] = (theta + delta)[accept] % 2π

# --- plaquette winding ---
def wrap(x): return (x + π) % 2π − π
charge = round((wrap(Δθ_right)+wrap(Δθ_down)+wrap(Δθ_left)+wrap(Δθ_up)) / 2π)

# --- height field ---
z = (cos(theta) + 1) / 2 * Z_SCALE`}</pre>

      <h2>Four shape keys and their physics</h2>

      <p>
        The four shape keys encode the four qualitatively distinct regimes. In
        the completed mesh Blender&apos;s shape-key slider lets you morph
        continuously between them:
      </p>

      <p>
        <strong>Basis — T = 0.40 T_BKT ≈ 0.36 J/k_B:</strong> Deep in the
        quasi-LRO phase. The spin configuration is nearly uniform with large
        spin-wave fluctuations. Vortex-antivortex pairs are rare and tightly
        bound at separations of 1–2 lattice spacings. The cos(θ) field is
        smooth with gentle undulations. This is the ground state topology
        relevant to ⁴He near absolute zero.
      </p>

      <p>
        <strong>SK_BKT — T = T_BKT ≈ 0.89 J/k_B:</strong> Critical. The
        correlation length has formally diverged (it grows as the essential
        singularity exp(b/√(T−T_BKT)) as T approaches from above). The pair
        separation distribution follows a power law with exponent η = 1/4.
        The cos(θ) field has a characteristic scale-free crumpled texture;
        paired vortex-antivortex bumps are visible at all separations, following
        the Coulomb-gas universality of the 2D BKT renormalisation group.
      </p>

      <p>
        <strong>SK_Unbound — T = 1.20 T_BKT ≈ 1.07 J/k_B:</strong> Free
        vortex phase. Pairs have unbound. Free ±1 topological charges scatter
        across the lattice; each one produces an isolated spiral phase field.
        The cos(θ) height field becomes noticeably noisier with isolated sharp
        peaks and troughs corresponding to single vortex cores.
      </p>

      <p>
        <strong>SK_HighT — T = 2.50 T_BKT ≈ 2.23 J/k_B:</strong> High
        temperature disordered phase. The spin correlation length is only a few
        lattice spacings. The cos(θ) field looks like random noise; the mesh
        surface is irregular and roughly flat on average.
      </p>

      <h2>Blender workflow</h2>

      <pre>{`1. Scripting workspace → open blueprint.py → Run Script
   Terminal output: "[DONE] Object 'xy_bkt_floor' created."

2. Switch to 3D Viewport → Numpad 5 (ortho) → Numpad 1 (front)
   You should see a flat cobalt plane with amber bumps at vortex sites.

3. Properties → Object Data → Shape Keys:
   Drag SK_BKT to 1.0, Basis to 0.0 — surface crumples into BKT texture.
   Drag SK_Unbound to 1.0 — isolated vortex spires appear.

4. Export GLB: File → Export → glTF 2.0
   Compression: Draco level 6
   Textures: WebP
   Include: Shape Keys ✓   Vertex Colours ✓
   Axis: +Y Up

5. (Optional) Run record.py to render viewport.mp4 animation.`}</pre>

      <h2>Troubleshooting</h2>

      <p>
        <strong>Surface is flat (no height variation):</strong> Check that
        Z_SCALE = 0.45 in blueprint.py. The shape-key Basis z-values are written
        explicitly from the cos field; if they look flat, the theta array may be
        uniform — confirm N_EQUIL is at least 1 000 sweeps for T &gt; 0.5.
      </p>

      <p>
        <strong>Vortex count does not change across shape keys:</strong> The
        colour attribute is baked from the Basis theta field. The shape keys
        store only z-positions, not colour. Vortex highlights in colour are
        fixed at the Basis state; to see highlights morph you would need a
        separate colour bake per shape key and driver-based switching.
      </p>

      <p>
        <strong>N_EQUIL not enough — still sees ordered domain from T=0 start:</strong>{" "}
        For T near T_BKT the correlation time diverges (critical slowing down).
        8 000 sweeps is adequate for most temperatures but at exactly T_BKT you
        may need 20 000–50 000 sweeps for full decorrelation. The shape-key
        texture at SK_BKT will look more uniform/striped than expected if
        insufficiently equilibrated.
      </p>

      <p>
        <strong>bpy.ops.object.select_all fails:</strong> This happens if no
        3D Viewport context is active. Prefix with{" "}
        <code>bpy.context.view_layer.objects.active = None</code> or run the
        script from the Scripting workspace with the 3D Viewport open in another
        panel.
      </p>

      <h2>Outside sources</h2>

      <p>
        <strong>
          Berezinskii VL (1971). &ldquo;Destruction of long-range order in
          one-dimensional and two-dimensional systems having a continuous
          symmetry group.&rdquo; <em>Soviet Physics JETP</em> 32:493-500.
        </strong>{" "}
        Public domain (&gt;50 yr). First identification of the topological phase
        and bound-vortex state. Related projects: NumPy (BSD-3-Clause,
        https://github.com/numpy/numpy).
      </p>

      <p>
        <strong>
          Kosterlitz JM, Thouless DJ (1973). &ldquo;Ordering, metastability and
          phase transitions in two-dimensional systems.&rdquo;{" "}
          <em>Journal of Physics C: Solid State Physics</em> 6:1181-1203.
          doi:10.1088/0022-3719/6/7/010.
        </strong>{" "}
        Public domain (&gt;50 yr). Full renormalisation-group treatment;
        Nobel Prize 2016. Related projects: SciPy (BSD-3-Clause,
        https://github.com/scipy/scipy); topocm/topocm_content (CC0,
        https://github.com/topocm/topocm_content — an open course covering BKT).
      </p>

      <p>
        <strong>
          Hasenbusch M (2005). &ldquo;The two-dimensional XY model at the
          transition temperature: a high-precision Monte Carlo study.&rdquo;{" "}
          <em>Physical Review B</em> 71:184420. doi:10.1103/PhysRevB.71.184420.
        </strong>{" "}
        CC0 (equations and published data). Establishes the benchmark
        T_BKT = 0.8935 J/k_B used throughout this tutorial.
      </p>

      <h2>Cross-references within this studio</h2>

      <p>
        The BKT mechanism is the classical counterpart of topological protection
        in quantum systems. See the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-haldane-1988-chern-insulator-berry-curvature-topological-phase-diagram-honeycomb-height-field-stage-floor-webxr"
        >
          Haldane model
        </Link>{" "}
        for a quantum topological phase with a Chern number that is the
        quantum-mechanical analogue of the BKT winding number, and the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-gross-pitaevskii-bec-rotating-vortex-lattice-abrikosov-imaginary-time-stage-floor-webxr"
        >
          Gross-Pitaevskii BEC vortex lattice
        </Link>{" "}
        for the quantum superfluid whose stiffness ρs is described by exactly the
        Nelson-Kosterlitz relation above its superfluid transition. The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-complex-ginzburg-landau-pde-spiral-turbulence-benjamin-feir-defect-height-field-stage-floor-webxr"
        >
          Complex Ginzburg-Landau equation
        </Link>{" "}
        also supports ±1 topological defects (phase vortices) in its spiral and
        defect-chaos regimes, making it the dynamical counterpart of the
        equilibrium BKT physics shown here.
      </p>
    </>
  );
}

export const blenderTutorialPythonNumpyXyModel2dBerezinskiiKosterlitzThouless19711973VortexAntivortexUnbindingTopologicalPhaseTransitionHeightFieldStageFloorWebxrEntry: Entry = buildInstructable({
  slug: SLUG,
  title: TITLE,
  lede: LEDE,
  date: "2026-09-19",
  tags: [
    "blender",
    "python",
    "scripting",
    "statistical-mechanics",
    "xy-model",
    "monte-carlo",
    "topological-phase-transition",
    "berezinskii-kosterlitz-thouless",
    "vortex",
    "webxr",
    "stage-floor",
  ],
  body: Body,
});
