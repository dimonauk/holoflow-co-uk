import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-ssh-su-schrieffer-heeger-1979-zak-phase-topological-edge-states-spectral-flow-stage-floor-webxr";

const TITLE =
  "Python numpy — SSH Model: Su–Schrieffer–Heeger 1979 Topological Insulator, Zak Phase, Bulk–Edge Correspondence, Spectral-Flow Stage Floor for WebXR (Blender 5.1)";

const LEDE =
  "Change the intercell hopping from 0.9 to 1.1 and two amber threads appear in the band gap — not because you added new states, but because the chain crossed a topological phase boundary. The SSH model is the simplest system exhibiting bulk–edge correspondence: a global integer (the Zak phase) forces localised zero-energy states at open boundaries whenever that integer is non-trivial. This blueprint diagonalises the 128-site chain at 128 values of t₂/t₁ and maps the resulting spectral flow onto a cobalt–amber height-field stage floor.";

function Body() {
  return (
    <>
      <p>
        Most condensed-matter systems that exhibit &ldquo;topological
        protection&rdquo; are complicated: three-dimensional crystals with
        spin-orbit coupling, non-collinear magnetic textures, fractional
        quantum Hall fluids. The SSH chain cuts away all that complexity.
        It has one spatial dimension, no spin, no interactions, and only
        nearest-neighbour hopping — yet it contains the essential mechanism
        that underpins all of them: a bulk integer invariant that forces
        boundary states to exist.
      </p>

      <p>
        The chain alternates between two hopping amplitudes t₁ (intracell)
        and t₂ (intercell). When t₁ &gt; t₂ the system is trivial; when
        t₂ &gt; t₁ it is topological. The difference is invisible in the bulk
        band structure — the gap is 2|t₁ − t₂| either way. The difference
        shows only at boundaries: in the topological phase, a finite open chain
        carries exactly two zero-energy states, one localised at each end,
        whose existence is guaranteed by the Zak phase being π rather than 0.
        Compare this with the Berry-phase geometry of the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-bloch-sphere-qubit-rabi-precession-berry-phase-su2-pauli-poi-webxr"
        >
          Bloch-sphere qubit tutorial
        </Link>
        : the Zak phase is the same geometric quantity — the Berry phase
        accumulated by the Bloch eigenstate as k winds once around the
        Brillouin zone — but here it governs the existence of physical states
        rather than a precession angle.
      </p>

      <h2>Model and equations</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`SSH Hamiltonian (Su, Schrieffer & Heeger 1979):

H = Σ_n [ t₁(c†_{nA}c_{nB} + h.c.) + t₂(c†_{n+1,A}c_{nB} + h.c.) ]

  Unit cell n contains sites 2n (A sublattice) and 2n+1 (B sublattice).
  t₁ = intracell hopping (within cell n)
  t₂ = intercell hopping (B of cell n → A of cell n+1)

Bloch Hamiltonian (Fourier-transform to momentum k):
  h(k) = d(k) · σ
  d(k) = ( t₁ + t₂ cos k,   t₂ sin k,   0 )

Energy bands:
  E±(k) = ±|d(k)| = ±√(t₁² + t₂² + 2t₁t₂ cos k)
  Band gap at k = π:  Δ = 2|t₁ − t₂|   (closes only at t₁ = t₂)

Zak phase (Berry phase over the Brillouin zone):
  γ = ∮_{−π}^{π} ⟨u_k| i ∂_k |u_k⟩ dk
  γ = 0   if t₁ > t₂  (trivial — d-vector loop does not enclose origin)
  γ = π   if t₂ > t₁  (topological — d-vector loops around origin once)

Winding number:  ν = γ/π ∈ {0, 1}

Bulk–edge correspondence:
  For open BC in the topological phase (ν = 1), there exist exactly 2
  zero-energy edge states, one per boundary.

Left-edge state (exact result):
  ψ_L(n) ∝ (−t₁/t₂)^n  on A sites only (sites 0, 2, 4, …)
  Localisation length:  ξ = 1 / |ln(t₁/t₂)| unit cells
  Energy = 0 exactly (protected by chiral symmetry {H, Γ} = 0)

Chiral symmetry operator:
  Γ = diag(+1, −1, +1, −1, …)  (alternating sign = sublattice)
  {H, Γ} = 0  ⟹  if |E⟩ is an eigenstate, so is Γ|E⟩ at energy −E
  Edge states live at the only energy invariant under this: E = 0.`}
      </pre>

      <h2>Spectral-flow mesh</h2>
      <p>
        The blueprint does not simulate any time evolution. It diagonalises
        the SSH Hamiltonian at 128 values of t₂/t₁ (from 0.15 to 2.5) and
        turns the 128 × 128 matrix of energy eigenvalues into a height-field
        mesh. Each row of the mesh is a single value of t₂/t₁; each column
        is one eigenstate, sorted by ascending energy. The z-height is the
        normalised eigenvalue. This picture is called the <em>spectral flow</em>
        — it shows how eigenvalues evolve continuously as a parameter changes.
      </p>
      <p>
        The key feature is two amber threads that appear at mid-gap height
        (z ≈ HEIGHT_SCALE/2, corresponding to E = 0) for all rows where
        t₂ &gt; t₁. These are the topological edge states. They are amber
        because their edge-weight statistic — the total probability density on
        the four boundary sites — is close to 1.0 (all their amplitude is at
        the chain ends), whereas bulk states score ≈ 0.016 (uniformly
        distributed). Compare this cross-field spectral structure with the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-tight-binding-2d-square-lattice-dispersion-fermi-surface-van-hove-singularity-stage-floor-webxr"
        >
          2D tight-binding dispersion floor
        </Link>
        , where the height field maps band energy across the Brillouin zone
        rather than across a parameter sweep, and the Van Hove singularity
        appears as a saddle rather than a threading zero mode.
      </p>

      <h2>Blueprint walk-through</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`# Named constants at top — edit these to explore

N_CELLS      = 64      # 64 unit cells = 128 sites
T1           = 1.0     # intracell hopping (fixed reference)
T2_MIN       = 0.15    # t₂ scan start (trivial phase)
T2_MAX       = 2.50    # t₂ scan end   (strongly topological)
T3_NNN       = 0.30    # next-nearest-neighbour hopping for SK_NNN
DELTA_SYM    = 0.40    # staggered onsite energy for SK_SymBreak
HEIGHT_SCALE = 0.70    # energy → z amplitude (metres)
E_CLIP       = 3.60    # energy clip for normalisation`}
      </pre>

      <h3>Hamiltonian construction</h3>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`def _h_open(t2):
    H = np.zeros((N_SITES, N_SITES))
    for n in range(N_CELLS):
        a, b = 2*n, 2*n + 1
        H[a, b] = H[b, a] = T1          # intracell bond
        if n < N_CELLS - 1:
            H[b, b+1] = H[b+1, b] = t2  # intercell bond

# WHY tridiagonal? The SSH Hamiltonian in the site basis is
# tridiagonal with alternating t1, t2 on the super- and sub-diagonal.
# numpy.linalg.eigh exploits this via LAPACK's dsbtrd (band matrix
# tridiagonalisation) even though H is passed as a dense array —
# the zeros are handled efficiently internally.`}
      </pre>

      <h3>Spectral flow scan</h3>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`def _scan(ham_fn):
    t2_vals = np.linspace(T2_MIN, T2_MAX, N_PARAM)
    E = np.empty((N_PARAM, N_SITES))
    W = np.empty((N_PARAM, N_SITES))   # edge weight
    for i, t2 in enumerate(t2_vals):
        evals, evecs = np.linalg.eigh(ham_fn(t2))
        E[i] = evals
        W[i] = evecs[0]**2 + evecs[1]**2 + evecs[-2]**2 + evecs[-1]**2

# WHY eigh not eig?  eigh is specialised for real symmetric / complex
# Hermitian matrices: it guarantees real eigenvalues, returns them
# sorted ascending (no post-sort needed), and uses LAPACK dsyev which
# is about 3× faster than the general dgeev used by eig.

# WHY edge weight = sum on 4 boundary sites?  Each edge state spans
# two sites (one per sublattice) at each end.  Summing 4 boundary
# sites ensures the metric is near 1.0 for any localisation length
# and distinguishes edge states from bulk states unambiguously.`}
      </pre>

      <h3>Shape keys</h3>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`# Basis (open BC) — the default, shows topological zero modes
# SK_Periodic — closes the chain with H[N-1, 0] = t2 wrap bond
#   Effect: bulk–edge correspondence disappears (no boundary), gap
#   closes linearly at t2 = t1 without threading zero modes
# SK_NNN — adds t3 = 0.30 on same-sublattice next-nearest bonds
#   Effect: breaks chiral symmetry {H,Γ}=0, so zero modes move
#   from exactly E=0 to a small nonzero energy ≈ ±0.05 t1.
#   WHY still topological? Winding number is defined mod 2π,
#   and a small t3 does not close the gap — ν stays 1.
# SK_SymBreak — adds staggered onsite ±δ (A: +δ, B: −δ)
#   Effect: explicitly breaks chiral symmetry; gaps out edge states.
#   WHY does this destroy protection? The staggered term anti-commutes
#   with the wrong operator (it commutes with H rather than anti-commutes),
#   so E=0 is no longer the only symmetry-invariant energy and the
#   edge states can hybridise with bulk states.`}
      </pre>

      <h2>Failure modes and troubleshooting</h2>
      <p>
        <strong>Zero modes not visible:</strong> check that T2_MAX &gt; T1 = 1.0 and
        that N_CELLS ≥ 8. For very small chains the two edge states hybridise
        (energy splitting ∝ (t₁/t₂)^{N} grows large); the amber threads
        shift away from z = HEIGHT_SCALE/2.
      </p>
      <p>
        <strong>Mesh looks wrong after rotation:</strong> the blueprint applies a
        −90° rotation around X then calls{" "}
        <code>bpy.ops.object.transform_apply(rotation=True)</code>. This bakes
        the rotation into vertex coordinates so the GLB exporter sees a
        +Y-up mesh. If you skip the apply step, the GLB will be rotated 90°
        in the WebXR scene.
      </p>
      <p>
        <strong>Edge weight ≈ 0 for all states:</strong> this happens if you pass
        the periodic Hamiltonian instead of the open one for the Basis scan.
        Periodic BC has no boundary, so <em>no</em> state has elevated probability
        on the &ldquo;edge&rdquo; sites — the mesh turns uniformly cobalt.
      </p>

      <h2>The Gross–Pitaevskii connection</h2>
      <p>
        The SSH model shares a structural feature with the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-gross-pitaevskii-bec-rotating-vortex-lattice-abrikosov-imaginary-time-stage-floor-webxr"
        >
          Gross–Pitaevskii BEC vortex lattice
        </Link>
        : both produce topological objects whose existence is guaranteed by
        an integer invariant. In the BEC case, the vortex winding number
        ν = (1/2π)∮ ∇φ · dl must be an integer because the superfluid
        wave-function is single-valued. In the SSH case, the Zak-phase
        winding number ν = (1/2π)∮ dφ_k must be an integer for the same
        reason — the Bloch eigenstate must return to itself (up to phase)
        as k winds across the Brillouin zone. In both systems, the invariant
        cannot change without closing a gap (vortex core energy vs. band gap).
      </p>

      <h2>Outside sources</h2>
      <ul className="list-disc pl-5 space-y-1">
        <li>
          Su WP, Schrieffer JR, Heeger AJ (1979){" "}
          <em>Solitons in Polyacetylene</em>{" "}
          Phys Rev Lett 42:1698–1701. Original SSH model paper; equations
          public domain. Heeger shared the 2000 Nobel Prize in Chemistry for
          this work. Related: NumPy (BSD-3-Clause){" "}
          <code>github.com/numpy/numpy</code>.
        </li>
        <li>
          Asbóth JK, Oroszlány L, Pályi A (2016){" "}
          <em>A Short Course on Topological Insulators</em>{" "}
          arXiv:1509.02295 CC-BY 4.0. Chapter 1 covers SSH in detail with
          worked Python exercises. Related: topocm/topocm_content (CC0){" "}
          <code>github.com/topocm/topocm_content</code>.
        </li>
        <li>
          Zak J (1989) <em>Berry&rsquo;s Phase for Energy Bands in Solids</em>{" "}
          Phys Rev Lett 62:2747–2750. Establishes the Zak phase as the 1D
          analogue of the Chern number; equations public domain. Related:
          NumPy (BSD-3-Clause).
        </li>
      </ul>
    </>
  );
}

export const entry: Entry = buildInstructable({
  slug: SLUG,
  title: TITLE,
  lede: LEDE,
  date: "2026-09-19",
  topics: ["blender", "python", "scripting", "numpy", "condensed-matter", "topology", "webxr"],
  Body,
});

export const blenderTutorialPythonNumpySshSuSchriefferHeeger1979ZakPhaseTopologicalEdgeStatesSpectralFlowStageFloorWebxrEntry =
  entry;
