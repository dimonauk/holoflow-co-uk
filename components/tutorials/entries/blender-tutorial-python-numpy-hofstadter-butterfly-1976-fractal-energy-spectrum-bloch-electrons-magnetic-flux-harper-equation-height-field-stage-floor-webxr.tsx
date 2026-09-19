import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-hofstadter-butterfly-1976-fractal-energy-spectrum-bloch-electrons-magnetic-flux-harper-equation-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — Hofstadter Butterfly 1976: Fractal Energy Spectrum of Bloch Electrons in a Magnetic Field, Harper Equation, TKNN Chern Numbers, 128×128 Height-Field Stage Floor for WebXR (Blender 5.1)";

const LEDE =
  "The Hofstadter butterfly is one of the most beautiful objects in condensed-matter physics: the exact energy spectrum of a 2D tight-binding electron in a transverse magnetic field, computed by Douglas Hofstadter in 1976. When the magnetic flux per plaquette α = p/q is rational, the Bloch Hamiltonian is a q×q Harper matrix with exactly q bands; sweeping α across [0,1] traces out a self-similar fractal whose every gap carries an integer Chern number — the quantised Hall conductance σ_xy = C e²/h (Thouless–Kohmoto–Nightingale–den Nijs 1982). A pure-NumPy spectral-density computation diagonalises ~35k Harper matrices, bins the eigenvalues into a 128×128 (α, E) grid, and bakes the result as a cobalt–amber height-field stage floor with four shape keys: the full butterfly, the left-half zoomed, the 1/3 sub-butterfly, and a next-nearest-neighbour-warped variant that breaks particle-hole symmetry.";

function Body() {
  return (
    <>
      <p>
        Every gap in the{" "}
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
          Kane–Mele model
        </Link>{" "}
        carries a topological invariant — the Chern number. The Hofstadter
        butterfly is the object that first made this connection concrete: every
        gap in the fractal is labelled by an integer, and those integers are
        exactly the Hall conductances measured in quantum-Hall experiments.
      </p>

      <h2>The model</h2>

      <p>
        Consider a 2D square lattice of hopping electrons in a perpendicular
        magnetic field B. In the Landau gauge <code>A = (0, Bx, 0)</code>, the
        vector potential gives each y-hop at column m a Peierls phase
        exp(i 2π α m), where α = Ba²/Φ₀ is the flux per plaquette in units of
        the flux quantum. The Hamiltonian (with hopping t = 1):
      </p>

      <pre>{`H = − Σ_{m,n} ( c†_{m+1,n} c_{m,n}  +  c†_{m,n+1} c_{m,n} exp(i 2π α m)  +  h.c. )`}</pre>

      <p>
        For <em>irrational</em> α the spectrum is a Cantor set of measure zero
        — the electron is neither a free Bloch wave (α = 0) nor a Landau level
        (α → 0 gradually, classical cyclotron). For{" "}
        <em>rational</em> α = p/q the magnetic unit cell has q lattice sites,
        the Bloch Hamiltonian is a q×q matrix, and the spectrum consists of
        exactly q bands.
      </p>

      <h2>Harper equation</h2>

      <p>
        Taking the Bloch ansatz ψ_(m,n) = exp(i k·r) u_m, the
        eigenvalue problem reduces to the Harper (Mathieu) equation:
      </p>

      <pre>{`ψ_{m+1} + ψ_{m−1} + 2 cos(2π α m + k_y) ψ_m = E ψ_m`}</pre>

      <p>
        This is a one-dimensional tight-binding chain with a quasiperiodic
        on-site potential. For α = p/q it has period q in m, so the Bloch
        condition closes it into a q×q periodic matrix:
      </p>

      <pre>{`H_{m,m}   = 2 cos(2π α m + k_y)     [diagonal: y-hopping with Peierls phase]
H_{m,m±1} = 1                         [off-diagonal: x-hopping, open chain]
H_{0,q−1} = exp(−i q k_x)            [periodic boundary, Bloch phase]
H_{q−1,0} = exp(+i q k_x)`}</pre>

      <p>
        Its q eigenvalues, computed at every (k_x, k_y) in the magnetic
        Brillouin zone [0, 2π/q] × [0, 2π], form q energy bands. When
        plotted as a function of α, those bands tile the (α, E) plane with the
        fractal butterfly pattern.
      </p>

      <h2>TKNN integers and the quantum Hall effect</h2>

      <p>
        Thouless, Kohmoto, Nightingale, and den Nijs (1982) showed that the
        Hall conductance contributed by the r lowest bands is:
      </p>

      <pre>{`σ_xy = e²/h × C_r

C_r = (1/2π) ∫_{BZ} Ω_r(k) d²k   (integral of Berry curvature over BZ)

C_r ∈ ℤ   (integer — topological invariant, cannot change continuously)`}</pre>

      <p>
        The integers{" "}
        <code>
          C<sub>r</sub>
        </code>{" "}
        label every gap in the butterfly and satisfy a Diophantine equation
        due to Strěda (1982): if gap G is at energy E_G and flux α, then
        C_r and s_r satisfy <code>r = C_r α + s_r</code> for all α in that
        gap. This is why the butterfly carries a rigidly integer Hall
        conductance in each gap regardless of α.
      </p>

      <h2>Computing the butterfly</h2>

      <p>
        For each of the 128 α values in [0, 1] we find the best rational
        approximation p/q with q ≤ 50 via the continued-fraction convergent
        recurrence (not the Python <code>fractions</code> module, which is
        slower). We then diagonalise the q×q Harper matrix at N_K² = 576
        random (k_x, k_y) points and bin the q eigenvalues into 128 energy
        slots between −4 and +4:
      </p>

      <pre>{`def _best_pq(alpha, q_max):          # continued-fraction convergents
    h_prev, h_curr = 1, int(alpha)
    k_prev, k_curr = 0, 1
    remainder = alpha − int(alpha)
    for _ in range(40):
        if remainder < 1e-10: break
        a_next    = int(1.0 / remainder)
        remainder = 1.0 / remainder − a_next
        h_next    = a_next * h_curr + h_prev
        k_next    = a_next * k_curr + k_prev
        if k_next > q_max: break
        h_prev, h_curr = h_curr, h_next
        k_prev, k_curr = k_curr, k_next
    return h_curr, k_curr            # best p/q

for i, alpha in enumerate(alphas):
    p, q = _best_pq(alpha, Q_MAX)   # Q_MAX = 50
    for kx in kx_vals:               # 24 values in [0, 2π)
        for ky in ky_vals:
            H      = harper_matrix(q, p, kx / q, ky)
            evals  = np.linalg.eigh(H)[0]   # sorted real
            for e in evals:
                j = int((e − E_MIN) / de)
                if 0 <= j < N_E:
                    density[i, j] += 1`}</pre>

      <p>
        Total matrix diagonalisations: 128 × 576 = ~74k (each at most 50×50).
        Runtime is a few seconds in CPython; the butterfly emerges without any
        special treatment of irrational α because the continued-fraction
        approximation is already the best rational at each resolution.
      </p>

      <h2>Height-field layout</h2>

      <p>
        The density array{" "}
        <code>density[i_alpha, j_energy]</code> is log1p-normalised and
        assigned to the Z coordinate of the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-tight-binding-2d-square-lattice-dispersion-fermi-surface-van-hove-singularity-stage-floor-webxr"
        >
          tight-binding
        </Link>{" "}
        -style stage floor:
      </p>

      <pre>{`x-axis  →  α ∈ [0, 1]   (magnetic flux quanta)
y-axis  →  E ∈ [−4, 4]  (tight-binding energy bandwidth)
z-value →  log1p(density) / log1p(max)   × Z_SCALE`}</pre>

      <p>
        Gaps in the butterfly appear as flat cobalt trenches; high-DOS band
        centres rise as amber peaks. A cobalt-to-amber{" "}
        <code>ShaderNodeValToRGB</code> ramp driven by the{" "}
        <code>HF_Density FLOAT_COLOR</code> vertex attribute completes the
        visual.
      </p>

      <h2>Shape keys</h2>

      <ul>
        <li>
          <strong>Basis</strong> — the full butterfly, α ∈ [0, 1]. The
          reflection symmetry α → 1 − α (particle-hole symmetry in the y
          sector) is immediately visible: the left and right halves are
          mirror images.
        </li>
        <li>
          <strong>SK_Half</strong> — α ∈ [0, 0.5] magnified to the full
          128-cell grid. The sub-butterfly near α = 1/4 becomes clearly
          resolved, and the fine structure near α → 0 (where bands collapse
          toward ε(k) = 2cos k) is visible.
        </li>
        <li>
          <strong>SK_Zoom</strong> — α ∈ [0.25, 0.50], the 1/3-sub-butterfly
          at full grid resolution. This is the key shape key for demonstrating
          self-similarity: the butterfly you see here at the scale of 1/3 is
          identical in structure to the Basis butterfly, confirming the fractal
          is exact.
        </li>
        <li>
          <strong>SK_NNN</strong> — next-nearest-neighbour hopping t₂ = 0.3.
          This adds both x-NNN (H_m,m±2 += t₂) and y-NNN diagonal terms
          2t₂cos(4παm + 2k_y), breaking the particle-hole symmetry E → −E.
          The butterfly warps: the lower half compresses, the upper half
          expands, and the gaps shift in energy. This variant is relevant to
          graphene (where t₂/t₁ ≈ 0.1) and the twisted bilayer graphene
          moiré band structure.
        </li>
      </ul>

      <h2>Relationship to other models in the library</h2>

      <ul>
        <li>
          <Link
            className={lk}
            href="/tutorials/blender-tutorial-python-numpy-haldane-1988-chern-insulator-berry-curvature-topological-phase-diagram-honeycomb-height-field-stage-floor-webxr"
          >
            Haldane model
          </Link>{" "}
          — the Chern-number machinery that labels Hofstadter gaps also labels
          the topological phase of the Haldane model. Hofstadter predates it
          by twelve years.
        </li>
        <li>
          <Link
            className={lk}
            href="/tutorials/blender-tutorial-python-numpy-kane-mele-2005-quantum-spin-hall-z2-topological-insulator-spin-hall-curvature-honeycomb-height-field-stage-floor-webxr"
          >
            Kane–Mele model
          </Link>{" "}
          — the Z₂ topological invariant of the KM model generalises the TKNN
          integer; the Hofstadter butterfly carries the integer analogue.
        </li>
        <li>
          <Link
            className={lk}
            href="/tutorials/blender-tutorial-python-numpy-ssh-su-schrieffer-heeger-1979-zak-phase-topological-edge-states-spectral-flow-stage-floor-webxr"
          >
            SSH model
          </Link>{" "}
          — the Zak phase (1D Berry phase) is the 1D precursor to the 2D Chern
          number. Hofstadter gaps carry the full 2D version.
        </li>
        <li>
          <Link
            className={lk}
            href="/tutorials/blender-tutorial-python-numpy-tight-binding-2d-square-lattice-dispersion-fermi-surface-van-hove-singularity-stage-floor-webxr"
          >
            Tight-binding band dispersion
          </Link>{" "}
          — the Hofstadter model is the α-dependent generalisation of the
          standard square-lattice dispersion; at α = 0 the butterfly
          degenerates to the cosine band E(k) = −2(cos k_x + cos k_y).
        </li>
      </ul>

      <h2>Outside sources</h2>

      <ul>
        <li>
          Hofstadter DR 1976{" "}
          <em>Phys. Rev. B</em> 14:2239–2249 —
          original butterfly; PD {">"}40 yr.
          Related: the 2013 three-group experimental realisations in graphene
          (Dean et al., Hunt et al., Ponomarenko et al.{" "}
          <em>Nature</em> 497/499) confirmed the butterfly in solid state.
        </li>
        <li>
          Thouless DJ, Kohmoto M, Nightingale MP, den Nijs M 1982{" "}
          <em>PRL</em> 49:405 — TKNN integers; PD {">"}40 yr.
          Related: TKNN formed the basis of the 2016 Nobel Prize in Physics
          (Thouless, Haldane, Kosterlitz). Sibling paper: Strěda P 1982{" "}
          <em>J. Phys. C</em> 15:L717 — Diophantine gap labelling.
        </li>
        <li>
          NumPy — BSD-3-Clause —{" "}
          <a
            className={lk}
            href="https://numpy.org"
            target="_blank"
            rel="noopener noreferrer"
          >
            numpy.org
          </a>{" "}
          (Harris et al. 2020).
        </li>
      </ul>
    </>
  );
}

export const blenderTutorialPythonNumpyHofstadterButterfly1976FractalEnergySpectrumBlochElectronsMagneticFluxHarperEquationHeightFieldStageFloorWebxrEntry: Entry =
  buildInstructable({
    slug: SLUG,
    title: TITLE,
    lede: LEDE,
    date: "2026-09-19",
    tags: [
      "blender",
      "python",
      "scripting",
      "condensed-matter",
      "topology",
      "quantum-hall",
      "fractal",
      "magnetic-field",
      "webxr",
      "stage-floor",
    ],
    body: Body,
  });
