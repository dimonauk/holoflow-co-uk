import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-anderson-localization-2d-tight-binding-disorder-ipr-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — Anderson Localisation 1958 2D Tight-Binding Diagonal Disorder H=−TΣc†c+Σεc†c ξ/a≈exp(πT/W) Exact Diagonalisation numpy.linalg.eigh 4096×4096 IPR=Σ|ψ|⁴ Basis(W=0.50 quasi-extended)/SK_Medium(W=2.0)/SK_Strong(W=5.0 localised)/SK_MaxIPR(W=8.0 highest-IPR) Anderson_Floor FLOAT_COLOR Cobalt–Amber Quantum Wavefunction Height-Field Stage Floor WebXR (Blender 5.1)";

const LEDE =
  "Philip Anderson showed in 1958 that a quantum particle on a crystal lattice with even tiny amounts of random disorder can become completely immobilised — not by classical friction, but by destructive interference of scattered waves. This blueprint runs the full 2D Anderson model inside Blender 5.1: it assembles a 4 096 × 4 096 tight-binding Hamiltonian with uniform on-site disorder, calls numpy.linalg.eigh for exact diagonalisation, and maps the probability density |ψ(i,j)|² of the eigenstate nearest the band centre onto a 64 × 64 quad-grid stage floor. Four shape keys sweep from the quasi-extended weak-disorder regime through to a starkly localised spike at W = 8, making the Anderson transition tangible in the WebXR viewport.";

function Body() {
  return (
    <>
      <p>
        The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-tight-binding-2d-square-lattice-dispersion-fermi-surface-van-hove-singularity-stage-floor-webxr"
        >
          2D tight-binding band dispersion tutorial
        </Link>{" "}
        builds the same nearest-neighbour Hamiltonian but sets all on-site
        energies to zero, producing pristine Bloch waves and a Van Hove
        singularity at the band saddle point. Anderson localisation is what
        happens when you switch on disorder: every one of those extended
        eigenstates contracts to an exponentially decaying envelope, and the
        beautiful Fermi surface disappears.
      </p>

      <h2>The Hamiltonian</h2>

      <p>
        On an N × N square lattice with periodic boundary conditions, the
        Anderson model reads:
      </p>

      <pre>{`H = −T Σ_{⟨ij⟩} c†_i c_j  +  Σ_i ε_i c†_i c_i

⟨ij⟩  nearest-neighbour pairs (4 per site in 2D)
T     hopping amplitude = 1.0  (energy unit)
ε_i   on-site disorder, uniform on [−W/2, W/2]`}</pre>

      <p>
        The disorder-free bandwidth is B = 4T. The band centre sits at E = 0.
        With disorder, the density of states broadens but every eigenstate
        acquires a localisation length ξ. The 2D scaling-theory result
        (Abrahams et al. 1979) is exact: ξ is finite for ANY W &gt; 0 in 2D.
      </p>

      <h2>Exact diagonalisation</h2>

      <p>
        The N × N = 4 096 × 4 096 Hamiltonian is assembled in NumPy: diagonal
        elements are drawn from{" "}
        <code>rng.uniform(−W/2, W/2, N²)</code>, and off-diagonal hops are
        inserted using vectorised index arithmetic (no Python loops over sites).
        Then:
      </p>

      <pre>{`E, psi = numpy.linalg.eigh(H)
# E[k]    : eigenvalue (energy) of state k, ascending
# psi[:, k]: k-th eigenstate, L²-normalised
# eigh exploits Hermitian symmetry → LAPACK dsyevd (divide-and-conquer)
#   ~ 2x faster and more accurate than numpy.linalg.eig

# Pick state nearest E = 0 (band centre, most delocalised in weak-disorder limit):
k_mid = argmin(|E|)
psi2d = psi[:, k_mid].reshape(N, N)

# Height field:
z = |psi2d|² / max(|psi2d|²) * HEIGHT_SCALE`}</pre>

      <p>
        Runtime: four separate diagonalisations (one per shape key) each take
        10–40 seconds on a modern CPU, depending on whether NumPy links to
        Intel MKL or OpenBLAS. Total allow 2–5 minutes.
      </p>

      <h2>Inverse Participation Ratio</h2>

      <p>
        The IPR quantifies how spatially concentrated a wavefunction is:
      </p>

      <pre>{`IPR_k = Σ_i |ψ_k(i)|⁴

Extended Bloch wave → IPR ≈ 1/N²  (weight uniform over all N² sites)
Delta-function      → IPR = 1     (weight on one site only)

For SK_MaxIPR the blueprint searches ALL 4096 eigenstates for the one
with the highest IPR — typically a state deep in the disorder-broadened
band tail where the localisation length ξ ≈ a (lattice spacing).`}</pre>

      <h2>Shape keys</h2>

      <pre>{`Basis      W = 0.50  ξ/a ≈ 500  Quasi-extended — ξ >> N=64 so the
                                 wavefunction looks delocalized on
                                 this finite system. Gentle hills.

SK_Medium  W = 2.00  ξ/a ≈ 5   Partially localised. Wavefunction
                                 has a clear amplitude maximum but
                                 still spreads over several dozen sites.

SK_Strong  W = 5.00  ξ/a ≈ 1.9 Clearly localised. A sharp amber
                                 peak rises from a near-flat cobalt
                                 floor — probability density confined
                                 to a handful of sites.

SK_MaxIPR  W = 8.00  highest    Most localised state in the full
                     IPR        spectrum. The spike may be 1–2 sites
                                 wide at its base.`}</pre>

      <h2>Topology and disorder: contrast with adjacent tutorials</h2>

      <p>
        The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-ssh-su-schrieffer-heeger-1979-zak-phase-topological-edge-states-spectral-flow-stage-floor-webxr"
        >
          SSH model
        </Link>{" "}
        and{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-haldane-1988-chern-insulator-berry-curvature-chern-number-phase-diagram-hexagonal-bz-height-field-stage-floor-webxr"
        >
          Haldane Chern insulator
        </Link>{" "}
        demonstrate topological localisation: edge states pinned by global
        topological invariants rather than disorder. Those edge states are
        robust against moderate disorder. Anderson localisation is the opposite
        story — disorder destroys all extended states in 2D, including
        topologically trivial bulk bands. Adding strong Anderson disorder to the
        Haldane model eventually kills even the topological edge states, a
        transition called the topological Anderson insulator (Li et al. 2009).
      </p>

      <p>
        The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-ising-model-2d-metropolis-monte-carlo-onsager-exact-tc-ferromagnetic-domains-height-field-stage-floor-webxr"
        >
          2D Ising model
        </Link>{" "}
        also requires a specific tuned parameter (temperature T_c) to exhibit
        critical behaviour. Anderson localisation in 2D has no such threshold:
        there is no critical disorder strength. The conductance decays as
        g ∝ exp(−2L/ξ) for any W &gt; 0, making the 2D case qualitatively
        different from both the 1D (always localised) and 3D (mobility-edge
        metal–insulator transition) regimes.
      </p>

      <h2>Running the blueprint</h2>

      <ol>
        <li>Open Blender 5.1. New General scene.</li>
        <li>
          Scripting workspace → Text → Open → select <code>blueprint.py</code>.
        </li>
        <li>
          Press <kbd>Alt</kbd>+<kbd>P</kbd>. Console logs four diagonalisation
          steps then saves <code>anderson_localization_floor.blend</code> and
          exports <code>.glb</code>.
        </li>
        <li>
          Switch to 3D Viewport, Material Preview shading (<kbd>Z</kbd> →
          Material Preview). The cobalt–amber height field is the W = 0.50
          quasi-extended eigenstate.
        </li>
        <li>
          Properties → Object Data → Shape Keys. Drag{" "}
          <strong>SK_Strong</strong> to 1.0 while setting Basis to 0.0. A
          single amber spike appears — the localised wavefunction.
        </li>
      </ol>

      <h2>Outside sources</h2>

      <p>
        The founding paper:{" "}
        <strong>
          Anderson PW (1958) &ldquo;Absence of Diffusion in Certain Random
          Lattices&rdquo; Physical Review 109(5):1492–1505.
        </strong>{" "}
        DOI{" "}
        <a
          className={lk}
          href="https://link.aps.org/doi/10.1103/PhysRev.109.1492"
          target="_blank"
          rel="noopener noreferrer"
        >
          10.1103/PhysRev.109.1492
        </a>
        . Public Domain (&gt;65 yr). Anderson later described the paper as
        &ldquo;my most cited work, written in a few weeks in 1957, and I
        didn&apos;t realise at the time how important it was.&rdquo; He shared
        the 1977 Nobel Prize in Physics for this work. Sibling reading:{" "}
        Thouless DJ (1972) J Phys C 5:77 — one-parameter scaling precursor.
      </p>

      <p>
        The Gang of Four scaling theory:{" "}
        <strong>
          Abrahams E, Anderson PW, Licciardello DC, Ramakrishnan TV (1979)
          &ldquo;Scaling Theory of Localisation: Absence of Quantum Diffusion
          in Two Dimensions&rdquo; Physical Review Letters 42(10):673–676.
        </strong>{" "}
        DOI{" "}
        <a
          className={lk}
          href="https://link.aps.org/doi/10.1103/PhysRevLett.42.673"
          target="_blank"
          rel="noopener noreferrer"
        >
          10.1103/PhysRevLett.42.673
        </a>
        . Public Domain (&gt;45 yr). This paper proved on very general grounds
        that all electron states in 2D are localised for any positive disorder.
        Sibling: Lee PA & Ramakrishnan TV (1985) Rev Mod Phys 57:287 — the
        definitive disorder review.
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
        . Harris et al. 2020 Nature 585:357–362. For systems larger than
        N = 64, consider{" "}
        <a
          className={lk}
          href="https://scipy.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          SciPy (BSD-3-Clause)
        </a>{" "}
        <code>scipy.sparse.linalg.eigsh</code> with shift-invert mode, which
        finds a few eigenstates near E = 0 without full diagonalisation.
      </p>
    </>
  );
}

export const blenderTutorialPythonNumpyAndersonLocalization2dTightBindingDisorderIprHeightFieldStageFloorWebxrEntry: Entry =
  buildInstructable({
    slug: SLUG,
    date: "2026-09-19",
    title: TITLE,
    lede: LEDE,
    tags: [
      "scripting",
      "quantum-mechanics",
      "condensed-matter",
      "disorder",
      "localisation",
      "tight-binding",
      "numpy",
      "webxr",
      "stage-floor",
    ],
    body: Body,
  });
