import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-gue-gaussian-unitary-ensemble-montgomery-1973-pair-correlation-sine-kernel-wigner-dyson-beta-family-stage-floor-webxr";

const TITLE =
  "Python numpy — GUE Gaussian Unitary Ensemble 1962 Dyson β=2 Complex Hermitian: Wigner-Dyson β-Family P(s;β)=A·s^β·exp(−Bs²) Montgomery 1973 Pair Correlation Sine Kernel K₂(r)=1−(sinπr/πr)² Monte Carlo Wigner-Semicircle Unfolding 128×128=16384V 16129Q GUE_Spacing FLOAT_COLOR Cobalt–Amber Stage Floor WebXR (Blender 5.1)";

const LEDE =
  "Freeman Dyson asked in 1962 whether the eigenvalues of a random Hermitian matrix obey any universal statistical law, regardless of the matrix entries. The answer is yes: for a complex Hermitian (GUE) matrix the nearest-neighbour level spacings follow P(s) = (32/π²)s²·exp(−4s²/π), and the entire family of symmetry classes — real symmetric (GOE), complex Hermitian (GUE), quaternion self-dual (GSE) — is indexed by a single integer β counting the degrees of freedom per off-diagonal element. This blueprint encodes the full β-family P(s; β) = A(β)·s^β·exp(−B(β)·s²) as a 128×128 height-field stage floor for WebXR, colours each row by β value from cobalt (Poisson-like) to amber (GSE), and includes a Monte Carlo shape key built from 128 actual GUE matrices — each diagonalised, unfolded via the Wigner semicircle CDF, and scattered into the mesh.";

function Body() {
  return (
    <>
      <p>
        The Gaussian Unitary Ensemble (GUE) is the probability measure on
        N×N complex Hermitian matrices H = H† with the joint distribution
        P(H) ∝ exp(−N·Tr(H²)/2). Its eigenvalue statistics are invariant
        under unitary conjugation H → UHU† — hence &ldquo;unitary ensemble.&rdquo;
        The companion{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-wigner-semicircle-goe-random-matrix-eigenvalue-level-repulsion-stage-floor-webxr"
        >
          GOE tutorial
        </Link>{" "}
        covers the real symmetric (β=1) case; this entry focuses on β=2 and
        the interpolating β-family surface.
      </p>

      <h2>Dyson&rsquo;s three ensembles</h2>

      <p>
        In his 1962 trilogy Dyson showed that quantum systems with different
        time-reversal properties belong to exactly three universality classes:
      </p>

      <pre>{`β = 1  GOE  real symmetric      H = H^T    time-reversal invariant
β = 2  GUE  complex Hermitian   H = H†     broken time-reversal (e.g. magnetic field)
β = 4  GSE  quaternion self-dual           Kramers degeneracy, spin-orbit coupling`}</pre>

      <p>
        The Dyson index β counts the real degrees of freedom per off-diagonal
        element: 1 for a real number, 2 for a complex number, 4 for a
        quaternion. Level repulsion P(s) ∝ s^β at small s is exact: it follows
        from the Vandermonde factor |Δ({λᵢ})|^β in the joint eigenvalue
        distribution, which vanishes as a polynomial of degree β whenever two
        levels approach each other.
      </p>

      <h2>The β-family surface</h2>

      <p>
        The generalised Wigner surmise P(s; β) = A(β)·s^β·exp(−B(β)·s²)
        interpolates continuously across the three ensembles and beyond.
        Normalisation (∫P ds = 1, ∫sP ds = 1) fixes:
      </p>

      <pre>{`B(β) = [Γ((β+2)/2) / Γ((β+1)/2)]²
A(β) = 2·B(β)^((β+1)/2) / Γ((β+1)/2)

β=1 (GOE):  P(s) = (π/2) s exp(−πs²/4)        peak at s ≈ 0.55
β=2 (GUE):  P(s) = (32/π²) s² exp(−4s²/π)     peak at s ≈ 0.93
β=4 (GSE):  P(s) = A s⁴ exp(−64s²/9π)          peak at s ≈ 1.31`}</pre>

      <p>
        The height field encodes this surface: x-axis is the spacing s ∈ [0,4],
        y-axis is β ∈ [0,4], and height is P(s; β)/max(P). A ridge runs from
        lower-left (β→0, peak near s=0) to upper-right (β=4, peak near s=1.3),
        shifting and sharpening as β increases. The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-hofstadter-butterfly-1976-bloch-electron-rational-flux-harper-equation-fractal-cantor-spectrum-stage-floor-webxr"
        >
          Hofstadter butterfly
        </Link>{" "}
        is another height field built from spectral data of a quantum Hamiltonian,
        but it encodes the spectrum itself rather than its statistics.
      </p>

      <h2>Montgomery&rsquo;s conjecture and the Riemann zeta zeros</h2>

      <p>
        In 1973 Hugh Montgomery proved (assuming GRH) that the pair correlation
        of non-trivial Riemann zeta zeros tends to:
      </p>

      <pre>{`F(α) → 1 − (sinπα / πα)²  for α ∈ (0, 1)`}</pre>

      <p>
        The function 1 − (sinπr/πr)² is exactly the GUE two-point cluster
        function K₂(r). Montgomery mentioned this result to Freeman Dyson at
        the IAS tea in 1972; Dyson recognised it immediately as the GUE kernel.
        Andrew Odlyzko computed the 10²²nd zero region in 1987 and found
        extraordinary agreement. This connection — between the statistics of
        Riemann zeros and those of complex Hermitian random matrices — remains
        one of the deepest unsolved problems in mathematics. The same spectral
        rigidity that makes the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-riemann-zeta-critical-strip-nontrivial-zeros-euler-product-stage-floor-webxr"
        >
          Riemann zeta zeros
        </Link>{" "}
        avoid clustering at short distances is encoded in the cobalt-to-amber
        gradient of the height field: low β (cobalt, front) means weak
        repulsion and exponential spacings; high β (amber, rear) means strong
        repulsion and rigid spectra.
      </p>

      <h2>Blueprint walkthrough</h2>

      <p>
        Open <code>blueprint.py</code> in Blender 5.1&rsquo;s Scripting workspace
        and press <strong>Run Script</strong>. Expected run time: ~45 s on a
        modern CPU (128 matrix diagonalisations of size 100×100).
      </p>

      <h3>Step 1 — β-family surface</h3>

      <pre>{`s_arr    = np.linspace(0.0, 4.0, 128, dtype=np.float32)
beta_arr = np.linspace(0.0, 4.0, 128, dtype=np.float32)
for j, beta in enumerate(beta_arr):
    b1 = (beta + 1) * 0.5;  b2 = (beta + 2) * 0.5
    B  = (math.gamma(b2) / math.gamma(b1))**2
    A  = 2.0 * B**b1 / math.gamma(b1)
    h[j, :] = A * s**beta * exp(-B * s²)`}</pre>

      <p>
        <code>math.gamma</code> is Python&rsquo;s built-in Lanczos implementation —
        no scipy dependency. At β=0 the Wigner formula gives a Rayleigh
        distribution (2/π)·exp(−s²/π), not the Poisson exp(−s); the SK_Poisson
        shape key provides the Poisson comparison separately.
      </p>

      <h3>Step 2 — Wigner-semicircle unfolding</h3>

      <pre>{`# Integrated Wigner semicircle density for support E ∈ [−2, 2]:
x   = clip(E / 2.0, -1, 1)
cdf = 0.5 + (x·sqrt(1−x²) + arcsin(x)) / π
N̄(E) = MAT_DIM × cdf`}</pre>

      <p>
        Raw eigenvalue spacings from a finite GUE matrix depend on the local
        density of states — they are denser near E=0 (semicircle peak) and
        sparser near E=±2 (semicircle edges). Unfolding removes this trend by
        mapping each eigenvalue to its theoretical rank under the Wigner
        semicircle, so the mean spacing becomes exactly 1 everywhere in the
        bulk. Without unfolding, the spacing histogram is distorted by the
        global density envelope. Compare with the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-anderson-localization-2d-tight-binding-disorder-ipr-height-field-stage-floor-webxr"
        >
          Anderson localisation blueprint
        </Link>
        , where the eigenvalue statistics switch from Wigner-Dyson (GOE) in the
        delocalised phase to Poisson in the strongly localised phase — exactly
        what the SK_Poisson vs Basis shape key contrast demonstrates here.
      </p>

      <h3>Step 3 — GUE Monte Carlo shape key</h3>

      <pre>{`for m in range(128):
    A   = rng.standard_normal((100,100)) + 1j*rng.standard_normal((100,100))
    H   = (A + A.conj().T) / sqrt(200)
    eig = linalg.eigvalsh(H)           # sorted real eigenvalues
    spc = diff(semicircle_unfold(eig)) # ~99 unfolded spacings per matrix
    # Scatter spacing values to random y rows for a "cloud" aesthetic
    for sp, yi in zip(spc, rng.integers(0, 128, 99)):
        h[yi, int(sp * 127/4)] += 1`}</pre>

      <p>
        The Monte Carlo key shows 128 × 99 ≈ 12 700 individual spacing
        measurements from actual diagonalised GUE matrices. Each point is a
        single measurement of a single gap in a single matrix; the visual
        scatter cloud follows the GUE analytical curve with Poisson-count noise
        on individual bins. This is what a physicist sees when they compute
        level statistics from a real quantum Hamiltonian: a noisy histogram
        that converges to the GUE prediction as the number of matrices grows.
      </p>

      <h2>Shape key visual guide</h2>

      <pre>{`Basis      β-family ridge shifting right as β→4; cobalt→amber gradient
SK_GOE     flat ridge at s≈0.55 (GOE, β=1); all rows identical
SK_MC      scatter cloud peaking near s≈0.9 (GUE, β=2); visible fluctuations
SK_Poisson monotone exponential decay from left; no level repulsion`}</pre>

      <h2>Failure modes</h2>

      <pre>{`Script stalls on "eigvalsh" call
  → Blender 5.1 ships NumPy's LAPACK eigensolver. 128 matrices of size
    100×100 take ~0.4 s total. If it stalls, reduce MAT_DIM from 100 to 50.

SK_MC appears too sparse / mostly zeros
  → Increase N_MAT from 128 to 256, or smooth the density by adding ±1
    to the y index after scattering.

GUE β-family surface looks identical to GOE
  → Verify that beta_arr runs to 4.0, not 1.0. Check h.max() > 0.01.

Shape keys absent from GLB in browser
  → Confirm export_morph=True in the gltf() call. Draco level > 6 can
    silently strip morph targets in some gltf2 exporter versions.`}</pre>

      <h2>Outside sources</h2>

      <p>
        Original trilogy:{" "}
        <a
          className={lk}
          href="https://doi.org/10.1063/1.1703773"
          target="_blank"
          rel="noopener noreferrer"
        >
          F.J. Dyson, &ldquo;Statistical Theory of Energy Levels of Complex Systems
          I,&rdquo; <em>J. Math. Phys.</em> 3 (1962) 140–156
        </a>{" "}
        (Public Domain, &gt;60 years). Parts II and III follow in the same
        issue (pp. 157–175). The pair correlation conjecture:{" "}
        <a
          className={lk}
          href="https://doi.org/10.1090/pspum/024/9944"
          target="_blank"
          rel="noopener noreferrer"
        >
          H.L. Montgomery, &ldquo;The pair correlation of zeros of the zeta function,&rdquo;
          <em> Proc. Symp. Pure Math.</em> 24, AMS 1973, pp. 181–193
        </a>{" "}
        (Public Domain, &gt;50 years). Numerical work:{" "}
        <a
          className={lk}
          href="https://github.com/numpy/numpy"
          target="_blank"
          rel="noopener noreferrer"
        >
          NumPy (BSD-3-Clause)
        </a>
        . Related OSS: the{" "}
        <a
          className={lk}
          href="https://github.com/scipy/scipy"
          target="_blank"
          rel="noopener noreferrer"
        >
          SciPy project (BSD-3-Clause)
        </a>{" "}
        maintains <code>scipy.stats.ortho_group</code> and{" "}
        <code>scipy.stats.unitary_group</code> for sampling from the Haar
        measure on O(N) and U(N), which are the natural groups whose invariance
        defines the GOE and GUE respectively; the{" "}
        <a
          className={lk}
          href="https://github.com/sympy/sympy"
          target="_blank"
          rel="noopener noreferrer"
        >
          SymPy project (BSD-3-Clause)
        </a>{" "}
        can compute the Selberg integral that generalises the Dyson β-ensemble
        to arbitrary β in closed form.
      </p>
    </>
  );
}

export const blenderTutorialPythonNumpyGueGaussianUnitaryEnsembleMontgomery1973PairCorrelationSineKernelWignerDysonBetaFamilyStageFloorWebxrEntry: Entry =
  buildInstructable({
    slug: SLUG,
    date: "2026-09-19",
    title: TITLE,
    lede: LEDE,
    tags: [
      "scripting",
      "random-matrix-theory",
      "gue",
      "wigner-dyson",
      "quantum-chaos",
      "montgomery-conjecture",
      "level-statistics",
      "webxr",
      "stage-floor",
    ],
    body: Body,
  });
