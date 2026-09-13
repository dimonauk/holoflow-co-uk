import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-swift-hohenberg-1977-stripe-hexagon-" +
  "labyrinth-etd1-spectral-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — Swift-Hohenberg Equation (1977) " +
  "∂u/∂t = r·u − (1+∇²)²u + γu² − u³ " +
  "ETD1 Spectral Unconditionally Stable " +
  "Critical Wavenumber k_c=1 σ_max=r Stripe Hexagon Labyrinth " +
  "γ=0 Rolls γ=±1.6 Hexagons Supercritical/Subcritical Bifurcation " +
  "128×128=16384V 16129Q " +
  "Basis(r=0.30 stripes)/SK_Hex(γ=+1.6)/SK_Labyrinth(r=0.05)/SK_Inverted(γ=−1.6) " +
  "SH_Order FLOAT_COLOR Cobalt–Amber " +
  "Height-Field Stage Floor WebXR (Blender 5.1)";

const LEDE =
  "In 1977 Jack Swift and Pierre Hohenberg were studying thermal convection " +
  "in a fluid heated from below — the Rayleigh-Bénard problem — and noticed " +
  "that near the onset of convection the full Navier-Stokes system could be " +
  "reduced to a single amplitude equation with a peculiar operator: (1+∇²)². " +
  "That operator has a single remarkable property — it suppresses every " +
  "Fourier mode except the one at wavenumber k = 1, selecting exactly one " +
  "spatial wavelength regardless of how far the system is driven. " +
  "The resulting Swift-Hohenberg equation became the reference model for " +
  "studying pattern selection (stripes vs hexagons), order-disorder transitions, " +
  "front propagation, and defect dynamics across fluid mechanics, optics, " +
  "soft matter, and neuroscience. " +
  "This blueprint integrates the SHE spectrally using ETD1 — an exponential " +
  "time-differencing scheme that integrates the stiff linear part exactly, " +
  "lifting the CFL restriction by a factor of ≈ 15 000 — and maps the " +
  "order-parameter field to a WebXR stage floor with four morph targets.";

function Body() {
  return (
    <>
      <p>
        The Rayleigh-Bénard instability is physically straightforward: heat a
        fluid from below, and when the temperature gradient exceeds a critical
        threshold the fluid tips over into convection rolls.  Near that threshold
        every roll has nearly the same wavelength — the fluid selects a preferred
        scale.  Swift and Hohenberg showed that this scale selection is entirely
        captured by a single amplitude PDE, which has since escaped its
        convection origins and turned up wherever a system breaks translational
        symmetry at a preferred length scale.
      </p>

      <h2>The equation</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
{`∂u/∂t = r·u  −  (1 + ∇²)²u  +  γ·u²  −  u³

u     order parameter (convective amplitude, phase-field variable)
r     bifurcation parameter  (r < 0 → flat; r > 0 → patterned)
γ     quadratic coefficient
        γ = 0 → equation is equivariant under u → −u → stripes only
        γ ≠ 0 → symmetry broken → hexagons or inverted hexagons preferred

Linear growth rate per Fourier mode k:
    σ(k) = r − (1 − k²)²

  σ(k) is maximised at k = k_c = 1:  σ_max = r
  Unstable band (r > 0): |1 − k²| < √r → k ∈ (√(1−√r), √(1+√r))`}
      </pre>

      <h2>Why the (1+∇²)² operator is elegant</h2>
      <p>
        The SHE encodes scale selection in one operator. Its Fourier eigenvalue
        (1 − k²)² is zero at k = 1 and positive everywhere else: large-scale
        and small-scale modes are both suppressed, leaving only the ring k = 1
        marginally unstable.  The ∇⁴ term is what makes explicit Euler
        impractical: at the Nyquist mode k_max the eigenvalue grows as k_max⁴,
        requiring dt ≤ 2×10⁻⁵ for N = 128.  ETD1 removes this constraint entirely.
      </p>

      <h2>ETD1 spectral scheme</h2>
      <p>
        Exponential time differencing (Cox &amp; Matthews 2002) splits the PDE into
        its linear and nonlinear parts and integrates the linear part analytically:
      </p>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
{`L̂_k = r − (1 − k²)²        ← linear operator in Fourier space
N(u) = γu² − u³             ← nonlinear part (evaluated in real space)

ETD1 update:
  û_{n+1} = exp(L̂_k dt) · û_n  +  φ₁(L̂_k dt) · N̂(u_n)

  φ₁(z) = (eᶻ − 1) / z

    WHY expm1 not exp-1: for |z| ≪ 1, eᶻ − 1 ≈ z; direct subtraction
    loses all significant figures; numpy.expm1 uses a separate algorithm
    accurate to machine epsilon for z → 0.

For z exactly 0 (mode at k_c = 1 when r = 0):
    φ₁(0) = 1 by L'Hôpital — Taylor series: 1 + z/2 + z²/6 + …
    Blueprint switches to Taylor series for |z| < 10⁻¹⁰.

Stability: ALL wavenumbers, ALL dt — exp(L̂_k dt) merely decays
  stable modes and grows unstable ones at the exact continuous rate.
  dt = 0.5 is used throughout (12 000× larger than explicit Euler minimum).`}
      </pre>

      <h2>Pattern regimes and bifurcation structure</h2>
      <ul className="list-disc pl-5">
        <li>
          <strong>Basis — stripes (r = 0.30, γ = 0, t = 150):</strong>{" "}
          The u → −u symmetry (γ = 0) forbids hexagons; rolls are the only
          periodic solution.  Starting from small random noise, the unstable
          band selects k ≈ 1 modes, which interact and align into roughly
          parallel rolls.  Defects (dislocations, grain boundaries) anneal
          slowly — the final state is ordered but not perfect, which is
          physically correct for a finite domain.
        </li>
        <li>
          <strong>SK_Hex — hexagons (r = 0.30, γ = +1.6, t = 200):</strong>{" "}
          A positive γ favours the u &gt; 0 phase.  Three roll modes at 60°
          offsets reinforce each other (the resonance condition k₁ + k₂ + k₃ = 0
          is satisfied on a hexagonal lattice), producing a honeycomb of bright
          peaks on a cobalt trough.  Hexagons nucleate faster than rolls near
          onset and can survive at r slightly below zero (subcritical branch).
        </li>
        <li>
          <strong>SK_Labyrinth — near onset (r = 0.05, γ = 0, t = 600):</strong>{" "}
          Very close to bifurcation the growth rate σ_max = 0.05 is slow; the
          pattern takes longer to emerge and never fully aligns.  Defects
          proliferate and freeze because the driving force to anneal them
          (∝ r) is weak.  The result is a labyrinthine field qualitatively
          identical to what appears in electroconvection experiments, ferro-
          fluid films, and some cortical models.
        </li>
        <li>
          <strong>SK_Inverted — spots (r = 0.30, γ = −1.6, t = 200):</strong>{" "}
          Negative γ favours the u &lt; 0 phase — the dark valleys become the
          selected state.  The pattern is the complement of SK_Hex: cobalt
          spots (peaks of −u) on an amber background.  This inversion is exact
          under the substitution (u, γ) → (−u, −γ), which blueprint.py
          exploits simply by passing G_I = −1.6.
        </li>
      </ul>

      <h2>Blueprint walk-through</h2>
      <ul className="list-disc pl-5">
        <li>
          <strong>_make_etd1(r)</strong> — pre-computes{" "}
          <code>exp(L̂_k dt)</code> and <code>φ₁(L̂_k dt)</code> for the
          given r.  These are (N, N/2+1) arrays cached outside the time loop —
          the only regime-specific computation before stepping begins.
        </li>
        <li>
          <strong>run_sh(r, gamma, n_steps, seed)</strong> — integrates using
          rfft2/irfft2 (real-to-complex FFT, half-spectrum).  The nonlinear
          term <code>γu² − u³</code> is evaluated in real space (two
          elementwise multiplications) then transformed.  The ETD1 update is
          a single elementwise multiply-add over the half-spectrum.
        </li>
        <li>
          <strong>_build_base_mesh / _set_vertex_colour / _add_shape_key</strong>{" "}
          — identical pattern to the{" "}
          <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-gierer-meinhardt-activator-inhibitor-turing-morphogenesis-1972-spot-stripe-height-field-stage-floor-webxr">
            Gierer-Meinhardt floor
          </Link>
          : row-major (j, i) vertex order, FLOAT_COLOR POINT attribute,
          foreach_set for bulk data transfer.
        </li>
      </ul>

      <h2>Relation to the studio pattern-formation library</h2>
      <ul className="list-disc pl-5">
        <li>
          <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-gierer-meinhardt-activator-inhibitor-turing-morphogenesis-1972-spot-stripe-height-field-stage-floor-webxr">
            Gierer-Meinhardt
          </Link>{" "}
          — two-species reaction-diffusion; patterns arise from a competition
          between a slow activator and a fast inhibitor.  SHE is phenomenological:
          it describes the amplitude of any near-onset pattern without specifying
          the underlying mechanism.  Both produce Turing-class patterns; SHE is
          analytically cleaner, GM is biologically interpretable.
        </li>
        <li>
          <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-cahn-hilliard-phase-field-spinodal-decomposition-ostwald-ripening-stage-floor-webxr">
            Cahn-Hilliard
          </Link>{" "}
          — conserved order parameter, coarsens as ⟨L⟩ ∼ t^(1/3) indefinitely.
          SHE is non-conserved and selects a fixed wavelength; it does NOT coarsen
          once the pattern is established (a key physical difference).
        </li>
        <li>
          <Link className={lk} href="/tutorials/blender-tutorial-gn-simulation-zone-reaction-diffusion-turing">
            Geometry Nodes reaction-diffusion
          </Link>{" "}
          — GPU-side Simulation Zone approach for real-time WebXR; SHE in
          blueprint.py runs on CPU at authoring time and bakes into morph targets,
          the complementary offline path.
        </li>
        <li>
          <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-allen-cahn-phase-field-mean-curvature-motion-allen-cahn-1979-stage-floor-webxr">
            Allen-Cahn
          </Link>{" "}
          — gradient flow for a double-well potential, interface motion by mean
          curvature.  SHE adds a ∇⁴ term that prevents the flat state from being
          stable even for large-scale perturbations, ensuring a non-trivial
          length scale is always selected.
        </li>
      </ul>

      <h2>Outside sources</h2>
      <ul className="list-disc pl-5">
        <li>
          Swift J, Hohenberg PC (1977).{" "}
          <em>Hydrodynamic fluctuations at the convective instability.</em>{" "}
          <a className={lk} href="https://doi.org/10.1103/PhysRevA.15.319" target="_blank" rel="noopener noreferrer">
            Phys Rev A 15(1):319–328
          </a>
          {" "}· PD (&gt;50 years) · original derivation of the SHE from
          Navier-Stokes near-onset expansion; related:{" "}
          <a className={lk} href="https://github.com/numpy/numpy" target="_blank" rel="noopener noreferrer">
            NumPy (BSD-3)
          </a>
        </li>
        <li>
          Cox SM, Matthews PC (2002).{" "}
          <em>Exponential time differencing for stiff systems.</em>{" "}
          <a className={lk} href="https://doi.org/10.1006/jcph.2002.6995" target="_blank" rel="noopener noreferrer">
            J Comput Phys 176(2):430–455
          </a>
          {" "}· PD (equations/method) · ETD1 and ETD2RK schemes; related:{" "}
          <a className={lk} href="https://github.com/scipy/scipy" target="_blank" rel="noopener noreferrer">
            SciPy (BSD-3)
          </a>
        </li>
        <li>
          Cross MC, Hohenberg PC (1993).{" "}
          <em>Pattern formation outside of equilibrium.</em>{" "}
          <a className={lk} href="https://doi.org/10.1103/RevModPhys.65.851" target="_blank" rel="noopener noreferrer">
            Rev Mod Phys 65(3):851–1112
          </a>
          {" "}· PD (&gt;30 years) · comprehensive survey of pattern selection,
          defect dynamics and hexagonal-stripe competition; related:{" "}
          <a className={lk} href="https://github.com/numpy/numpy" target="_blank" rel="noopener noreferrer">
            NumPy (BSD-3)
          </a>
        </li>
      </ul>

      <h2>Troubleshooting</h2>
      <ul className="list-disc pl-5">
        <li>
          <strong>Pattern stays flat (no stripes form):</strong> r must be
          positive.  Confirm R_B = 0.30 and that the script ran without
          error.  If the domain is very large (L ≫ 32π) the integration time
          may need to increase proportionally.
        </li>
        <li>
          <strong>SK_Hex shows stripes not hexagons:</strong> hexagons require
          γ ≥ γ_c (≈ 1.0 for r ≈ 0.3).  If γ is too small the symmetry is
          barely broken and rolls still dominate.  Increase G_H to 2.0.
        </li>
        <li>
          <strong>SK_Labyrinth looks too ordered:</strong> increase T_L (more
          steps) to let pattern disorder develop.  Near r = 0 pattern
          formation is slow; labyrinthine disorder freezes in within the
          first ∼100 time units.
        </li>
        <li>
          <strong>Shape key slider in Three.js has no effect:</strong> confirm
          export_morph=True was set; Three.js requires{" "}
          <code>mesh.morphTargetInfluences</code> to be set and the material
          must use <code>morphTargets: true</code>.
        </li>
        <li>
          <strong>All shape keys look identical:</strong> each call to
          run_sh() uses a different seed (S_B, S_H, S_L, S_I).  If seeds are
          accidentally the same the initial noise is identical, but the
          dynamics will still differ because r and γ differ.  Check the
          printed terminal headings to confirm all four regimes ran.
        </li>
      </ul>
    </>
  );
}

export const entry = buildInstructable({
  slug: SLUG,
  title: TITLE,
  lede: LEDE,
  date: "2026-09-13",
  topics: ["blender", "scripting", "physics", "pattern-formation", "webxr"],
  body: Body,
});
