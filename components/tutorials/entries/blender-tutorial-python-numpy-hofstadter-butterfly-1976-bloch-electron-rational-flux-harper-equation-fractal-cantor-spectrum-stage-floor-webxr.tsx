import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-hofstadter-butterfly-1976-bloch-electron-rational-flux-harper-equation-fractal-cantor-spectrum-stage-floor-webxr";

const TITLE =
  "Python numpy — Hofstadter Butterfly 1976 Bloch Electron Rational Magnetic Flux Harper Equation H[n,n]=2cos(2πnα) H[n,n±1]=1 Cyclic Tridiagonal q×q Farey Sequence Cantor-Set Spectrum log₁₀(1+count) Basis(Q_MAX=100)/SK_Coarse(q≤30)/SK_Dense(q≤200)/SK_Central(α∈[0.4,0.6] self-similar) 128×128=16384V 16129Q Hofstadter_Butterfly FLOAT_COLOR Cobalt–Amber Fractal Spectrum Height-Field Stage Floor WebXR (Blender 5.1)";

const LEDE =
  "Douglas Hofstadter's 1976 paper produced one of the most beautiful figures in physics: plot the allowed energies of a square-lattice electron against the perpendicular magnetic flux ratio α = Φ/Φ₀, and you get a fractal butterfly — wings inside wings — whose gaps are indexed by the integers that, six years later, Thouless, Kohmoto, Nightingale and den Nijs would identify as topological Chern numbers. This blueprint computes the butterfly inside Blender 5.1 by diagonalising the q×q cyclic Harper matrix for every rational α = p/q with q ≤ 100, accumulates all 16 000-odd eigenvalues into a 128 × 128 density histogram, and lifts the counts as a height-field stage floor. Four shape keys reveal the fractal at coarse, standard, fine and zoomed-central resolutions.";

function Body() {
  return (
    <>
      <p>
        The studio&apos;s condensed-matter quartet — the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-ssh-su-schrieffer-heeger-1979-zak-phase-topological-edge-states-spectral-flow-stage-floor-webxr"
        >
          SSH Zak-phase tutorial
        </Link>
        ,{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-haldane-1988-chern-insulator-berry-curvature-topological-phase-diagram-honeycomb-height-field-stage-floor-webxr"
        >
          Haldane Chern insulator
        </Link>{" "}
        and{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-kane-mele-2005-quantum-spin-hall-z2-topological-insulator-spin-hall-curvature-honeycomb-height-field-stage-floor-webxr"
        >
          Kane–Mele Z₂ invariant
        </Link>{" "}
        — all live on Hamiltonians defined in momentum space k. The Hofstadter
        butterfly is the missing piece: it is the original demonstration that
        energy spectra can themselves be fractal, and it is the physical context
        in which Chern numbers were first discovered as topological invariants
        of energy gaps.
      </p>

      <p>
        The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-tight-binding-2d-square-lattice-dispersion-fermi-surface-van-hove-singularity-stage-floor-webxr"
        >
          2D tight-binding dispersion tutorial
        </Link>{" "}
        builds the field-free version of the same Hamiltonian: E(k) = −2t[cos
        kₓ + cos kᵧ], four bands, a single Fermi surface. The Hofstadter
        butterfly is what happens when you pierce that lattice with a rational
        magnetic flux Φ = (p/q)Φ₀: the single band fractures into exactly q
        sub-bands, and every gap between them carries a quantised Hall
        conductance σ_H = ne²/h.
      </p>

      <h2>The Harper equation</h2>

      <p>
        In the Landau gauge <strong>A</strong> = (0, Φx, 0), the
        nearest-neighbour tight-binding Hamiltonian for flux α = p/q reduces,
        after a Bloch ansatz along x with crystal momentum kₓ, to a 1D
        recurrence on the q-site unit cell:
      </p>

      <pre>{`ε ψₙ  =  ψₙ₊₁ + ψₙ₋₁ + 2 cos(2πnα − kₓ) ψₙ

Setting kₓ = 0 (sufficient to map the full spectrum) gives
the q×q cyclic Harper matrix:

  H[n, n]     = 2 cos(2π n p/q)   ← Peierls phase: magnetic potential
  H[n, n±1]  = 1                   ← hopping amplitude t = 1
  H[0, q−1]  = H[q−1, 0] = 1      ← periodic boundary (Bloch closure)

numpy.linalg.eigvalsh(H) returns q real eigenvalues ∈ [−4, 4].`}</pre>

      <p>
        Why <code>eigvalsh</code> rather than <code>eig</code>? The Harper
        matrix is real symmetric, so LAPACK&apos;s <code>dsyev</code> (which{" "}
        <code>eigvalsh</code> calls) uses a divide-and-conquer algorithm that is
        roughly three times faster and more numerically stable than the general
        complex eigensolver.
      </p>

      <h2>Farey sequence and the density grid</h2>

      <p>
        The butterfly is the union of all spectra {"{"}E_n(p/q){"}"}. To fill
        the 128 × 128 grid we iterate over the Farey sequence: all distinct
        fractions p/q with 0 ≤ p ≤ q, gcd(p, q) = 1, 1 ≤ q ≤ Q_MAX. For
        Q_MAX = 100 that is roughly 3 000 Harper matrices, each of size at most
        100 × 100 — the whole computation completes in a few seconds on a
        laptop.
      </p>

      <pre>{`density[i_E, i_α] += 1   # for each eigenvalue E of H(p/q)

height = log₁₀(1 + density)

Why log: α = 1/2 contributes 2 eigenvalues but they sit at E = ±2
(the entire bandwidth collapses to two points for a half-flux quantum).
Without log-compression those two pixels dominate and the intricate
fractal sub-structure at large q is invisible.`}</pre>

      <h2>Topological gaps — the TKNN integers</h2>

      <p>
        Thouless, Kohmoto, Nightingale and den Nijs (1982) showed that the Hall
        conductance contributed by all filled sub-bands below a gap is
        σ_H = (e²/h) × C, where the Chern number C is an integer satisfying
        the Diophantine equation:
      </p>

      <pre>{`p · s  +  q · t  =  1      (Bézout identity)
r = r(α, gap)  — gap-label integer (continuous in α)
s = s(α, gap)  — Chern number of each filled sub-band

Every visible gap in the butterfly persists over a continuous range of α
and carries a unique integer pair (r, s). This is why the gaps do not
close under small perturbations — they are topologically protected.`}</pre>

      <p>
        This is the mathematical ancestor of the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-haldane-1988-chern-insulator-berry-curvature-topological-phase-diagram-honeycomb-height-field-stage-floor-webxr"
        >
          Haldane Chern insulator
        </Link>
        : Haldane found a lattice model with C = ±1 without a net flux, showing
        that topology, not Landau levels, is the essential ingredient.
      </p>

      <h2>Shape keys</h2>

      <p>
        Four shape keys let the viewer explore the hierarchy in the WebXR
        viewport:
      </p>

      <pre>{`Basis      : Q_MAX=100, α∈[0,1]
              Standard butterfly — clear main wings, first-level sub-bands

SK_Coarse  : Q_MAX=30, α∈[0,1]
              Only the simplest rationals (α = 1/2, 1/3, 2/3, 1/4 …)
              Broad lobes, no branch detail — good for explaining the idea

SK_Dense   : Q_MAX=200, α∈[0,1]
              Fine sub-bands of sub-bands visible; computation is heavier
              but reveals the Cantor-set nature of the spectrum at irrational α

SK_Central : Q_MAX=150, α∈[0.4, 0.6]
              The same mesh rescaled so the central wing fills the whole floor.
              Self-similarity: the zoomed centre is a smaller copy of the whole.`}</pre>

      <h2>Connection to Anderson localisation</h2>

      <p>
        The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-anderson-localization-2d-tight-binding-disorder-ipr-height-field-stage-floor-webxr"
        >
          Anderson localisation tutorial
        </Link>{" "}
        adds random on-site disorder ε_i to the same tight-binding lattice.
        Where disorder delocalises via random scattering, the butterfly&apos;s
        fractal gaps survive magnetic perturbation — they are topologically
        protected from any disorder that preserves the magnetic translation
        symmetry. The interplay between the two is the subject of active
        research in topological Anderson insulators.
      </p>

      <h2>Troubleshooting</h2>

      <pre>{`Blank mesh (all z = 0)
  → No (p, q) pairs landed in any bin.
    Check that Q_MAX ≥ 1 and alpha_range is a subset of [0, 1].

SK_Dense hangs Blender
  → Q_MAX=200 builds ~28 000 Harper matrices.
    On a slow machine, run from the command line:
    blender --background --python blueprint.py
    and wait for "Export …glb" before opening the .blend.

Butterfly looks smeared
  → The 128×128 grid quantises α in steps of 1/128 ≈ 0.008.
    Rationals with large q land in the correct bin but may share a bin
    with neighbours; this is expected at N=128. Increase N in blueprint.py
    to 256 for sharper resolution at the cost of 4× more vertices.`}</pre>

      <h2>Outside sources</h2>

      <ul>
        <li>
          Hofstadter, D.R. (1976).{" "}
          <em>
            Energy levels and wave functions of Bloch electrons in rational and
            irrational magnetic fields.
          </em>{" "}
          <em>Physical Review B</em> <strong>14</strong>(6):2239–2249.{" "}
          <a
            className={lk}
            href="https://doi.org/10.1103/PhysRevB.14.2239"
            target="_blank"
            rel="noreferrer"
          >
            doi:10.1103/PhysRevB.14.2239
          </a>{" "}
          — Public Domain (&gt;50 yr). The original paper; all butterfly figures
          reproduced in the literature trace back here.
        </li>
        <li>
          Thouless, D.J., Kohmoto, M., Nightingale, M.P. &amp; den Nijs, M.
          (1982). &ldquo;Quantised Hall conductance in a two-dimensional
          periodic potential.&rdquo; <em>Physical Review Letters</em>{" "}
          <strong>49</strong>(6):405–408.{" "}
          <a
            className={lk}
            href="https://doi.org/10.1103/PhysRevLett.49.405"
            target="_blank"
            rel="noreferrer"
          >
            doi:10.1103/PhysRevLett.49.405
          </a>{" "}
          — Public Domain (&gt;40 yr). Introduces the TKNN integers and proves
          each butterfly gap carries a Chern number.{" "}
          <em>Related</em>: the TopoCM course content (CC0,{" "}
          <a
            className={lk}
            href="https://github.com/topocm/topocm_content"
            target="_blank"
            rel="noreferrer"
          >
            github.com/topocm/topocm_content
          </a>
          ) covers TKNN in lecture 4; the NumPy project (BSD-3,{" "}
          <a
            className={lk}
            href="https://github.com/numpy/numpy"
            target="_blank"
            rel="noreferrer"
          >
            github.com/numpy/numpy
          </a>
          ) provides <code>eigvalsh</code>.
        </li>
      </ul>
    </>
  );
}

export const entry: Entry = buildInstructable({
  slug:  SLUG,
  title: TITLE,
  lede:  LEDE,
  date:  "2026-09-19",
  topics: ["scripting", "condensed-matter", "topology", "height-field", "webxr"],
  Body,
});

export const blenderTutorialPythonNumpyHofstadterButterfly1976BlochElectronRationalFluxHarperEquationFractalCantorSpectrumStageFloorWebxrEntry =
  entry;
