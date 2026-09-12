import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-talbot-effect-henry-fox-talbot-1836-self-imaging-diffraction-grating-fractional-talbot-gauss-sum-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — Talbot Effect 1836: " +
  "U(x,z)=Σcₙexp(2πinx/d)exp(−iπn²λz/d²) " +
  "Near-Field Huygens–Fresnel Self-Imaging " +
  "128×128=16384V 16129Q " +
  "Basis(Binary)/SK_Sine/SK_Blazed/SK_Phase " +
  "TC_Intensity FLOAT_COLOR Cobalt–Amber " +
  "Fractional Talbot Gauss Sum Height-Field Stage Floor WebXR (Blender 5.1)";

const LEDE =
  "Henry Fox Talbot observed in 1836 that a periodic diffraction grating " +
  "illuminated by coherent light re-creates a perfect image of itself at " +
  "distances z_T = 2d²/λ — and at every rational fraction p/q of that " +
  "distance, q interleaved copies of the grating appear simultaneously, " +
  "their weights given by Gauss sums. At irrational distances the intensity " +
  "is a fractal of Hausdorff dimension 3/2. The entire structure — self-images, " +
  "fractional sub-images, and the fractal carpet between them — follows from " +
  "one line of paraxial optics.";

function Body() {
  return (
    <>
      <p>
        The Talbot effect is perhaps the simplest non-trivial prediction of
        wave optics: illuminate a periodic grating with a coherent plane wave
        and the grating re-images itself at regular distances downstream,
        with no lens required. Talbot published the observation in 1836 as
        part of a series of notes on optical phenomena; the theoretical
        explanation via Fresnel diffraction came later from Rayleigh (1881),
        who identified the critical length z_T = 2d²/λ now called the
        Talbot length.
      </p>

      <h2>Why the self-imaging occurs</h2>
      <p>
        A grating of period d has a discrete spectrum of spatial frequencies:
        k_n = 2πn/d. In the paraxial (Fresnel) approximation, each harmonic
        n propagates as a tilted plane wave and accumulates a quadratic
        phase relative to the on-axis direction:
      </p>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Δφ_n(z)  =  −π n² λ z / d²

At z = z_T = 2d²/λ:
  Δφ_n(z_T) = −π n² λ · 2d²/λ / d²
             = −2π n²
             ≡ 0  (mod 2π)  for all n ∈ ℤ   ✓`}
      </pre>
      <p>
        All harmonics return simultaneously to their original phase
        relationship — hence the exact self-image. The key insight is that
        the phase is <em>quadratic</em> in n: for a linear phase the
        propagation would merely shift the grating laterally, but the
        quadratic form ensures that the phases wrap to zero simultaneously
        at z_T, regardless of the harmonic order.
      </p>
      <p>
        Compare this with the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-fraunhofer-diffraction-fft-aperture-psf-airy-disk-stage-floor-webxr"
        >
          Fraunhofer diffraction
        </Link>{" "}
        tutorial, which operates in the far field where the quadratic Fresnel
        phase has been replaced by a linear one. The Talbot effect is an
        entirely near-field phenomenon: it disappears in the Fraunhofer limit
        because the quadratic phase responsible for self-imaging is precisely
        the term discarded in the far-field approximation.
      </p>

      <h2>Fractional Talbot images and Gauss sums</h2>
      <p>
        At z = (p/q)·z_T, with gcd(p,q) = 1, each phase factor becomes
        exp(−2πin²p/q). Berry & Klein (1996) showed that the intensity
        decomposes into exactly q shifted copies of the grating:
      </p>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`I(x, (p/q)·z_T)  =  Σ_{k=0}^{q−1}  W_{p,q,k}  · I₀(x − kd/q)

where  W_{p,q,k}  =  |G(p,q,k)|² / q²

G(p,q,k)  =  Σ_{m=0}^{q−1}  exp(2πi(m²p/q + mk/q))

G is a Gauss sum — the same sums that appear in quadratic residues,
the theory of modular forms, and the proof of quadratic reciprocity.`}
      </pre>
      <p>
        For q=2 (half Talbot distance): the image is a single copy of the
        grating shifted by d/2 — the binary grating reappears inverted.
        For q=3: three equally spaced copies at 0, d/3, 2d/3. For large q
        the images become too closely spaced to resolve and the intensity
        approaches a fractal distribution.
      </p>
      <p>
        The connection to the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-scipy-cornu-spiral-fresnel-clothoid-linear-curvature-bishop-tube-poi-webxr"
        >
          Cornu spiral
        </Link>{" "}
        is instructive: the Cornu spiral traces the Fresnel integral
        C(t) + iS(t) for a single edge, while the Talbot carpet is the
        Fresnel integral evaluated for a periodic boundary condition — the
        discrete analogue of the continuous Fresnel transform.
      </p>

      <h2>The Talbot carpet as fractal</h2>
      <p>
        At irrational z/z_T, the Gauss-sum decomposition breaks down and
        Berry & Klein proved that I(x,z) is a fractal measure. Specifically,
        for a binary grating the graph of I(·,z) has Hausdorff dimension 3/2
        — midway between a smooth curve (dimension 1) and a space-filling set
        (dimension 2). The carpet is therefore not merely a pretty pattern
        but a mathematical object with a non-integer dimension provably
        determined by the quadratic nature of the Fresnel phase.
      </p>
      <p>
        This fractal dimension 3/2 is the same as for Brownian motion paths,
        and for the same reason: Brownian paths are the continuum limit of
        random walks with quadratic variance growth, while the Talbot carpet
        is built from quadratic phases exp(−iπn²·) — both are governed by
        the same class of quadratic exponential sums.
      </p>

      <h2>Four grating profiles</h2>
      <p>
        The four shape keys demonstrate how the Fourier spectrum of the
        grating controls the richness of the carpet:
      </p>
      <ul className="list-disc pl-5 space-y-1">
        <li>
          <strong>Basis (binary, 50% duty cycle)</strong> — all odd harmonics
          contribute: c_n = sin(nπ/2)/(nπ), so c_1=1/π, c_3=−1/(3π), …
          The resulting carpet is the classical Talbot image: dense bright
          stripes at z_T and z_T/2, complex sub-images at z_T/4, etc.
        </li>
        <li>
          <strong>SK_Sine (sinusoidal)</strong> — only the DC term
          c_0=0.5 and the first harmonic c_±1=0.25 are non-zero.
          The carpet simplifies dramatically: pure cosine interference
          with a single self-imaging distance, no sub-structure. This is
          the minimum non-trivial grating.
        </li>
        <li>
          <strong>SK_Blazed (sawtooth 0→1)</strong> — Fourier coefficients
          c_n = i/(2πn) for n≠0 include <em>both</em> odd and even
          harmonics. The carpet is asymmetric (the sawtooth has no centre
          of symmetry) and shows richer sub-image structure because even
          harmonics at n=2, 4, … create additional Talbot periods at
          z_T/4, z_T/8, etc.
        </li>
        <li>
          <strong>SK_Phase (binary ±1 phase grating)</strong> — amplitude
          is uniform (|t|=1 everywhere), so the grating plane z=0 looks
          flat. But at z=z_T/4 the phase differences have accumulated into
          amplitude modulation, and the self-image appears there — shifted
          by a quarter period from the amplitude-grating case. The carpet
          looks visually different from the binary amplitude case despite
          using the same spatial frequency distribution.
        </li>
      </ul>

      <h2>Algorithm</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`# Z_TALBOT = 2d²/λ = 40  (d=1.0, λ=0.05)
n = np.arange(-N_HARM, N_HARM+1)      # (41,) harmonic indices
cn = fourier_coeffs(grating, n)        # (41,) complex

x = np.linspace(0, d, 128, endpoint=False)   # grating coordinate
z = np.linspace(0, 2*Z_TALBOT, 128)          # propagation coordinate

# x_modes[i,k] = exp(2πi·n[k]·x[i]/d)
x_modes = np.exp(2j*np.pi * n[None,:] * (x[:,None]/d))    # (128,41)

# z_modes[j,k] = exp(−iπ·n[k]²·λ·z[j]/d²)
z_modes = np.exp(-2j*np.pi * n[None,:]**2 * (z[:,None]/Z_T))  # (128,41)

cx_modes = cn[None,:] * x_modes        # (128,41)
U        = cx_modes @ z_modes.T        # (128,128)  ← single matmul
I        = np.abs(U)**2                # real intensity`}
      </pre>
      <p>
        The entire carpet is computed by one matrix multiplication. The
        x-modes and z-modes are independent arrays that factor the 2D
        exponential into two 1D problems — a consequence of the
        separability of the paraxial propagation kernel. For N_HARM=20 and
        GRID_N=128, this is a (128×41) @ (41×128) multiply: roughly 430 000
        complex floating-point operations, completing in milliseconds.
      </p>
      <p>
        The same FFT-based strategy is used in the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-tdse-split-operator-fft-double-slit-quantum-interference-webxr"
        >
          TDSE split-operator
        </Link>{" "}
        tutorial, where the Schrödinger equation&apos;s kinetic phase
        exp(−i·k²·dt/2) has the same quadratic-in-k structure as the
        Talbot propagation phase exp(−iπn²λz/d²). The Talbot effect is
        therefore mathematically identical to free-particle quantum
        mechanics with a periodic initial condition.
      </p>

      <h2>Shape key implementation</h2>
      <p>
        Each shape key stores per-vertex Z offsets from the Basis geometry.
        The blueprint computes the binary-grating carpet first, builds the
        mesh, registers the Basis shape key, then for each additional grating
        type recomputes the carpet and calls{" "}
        <code>sk.data[idx].co = (x, y, z_new)</code>. The{" "}
        <code>TC_Intensity</code> colour attribute is set once from the
        Basis density and kept fixed across all shape keys — it acts as a
        legend for the binary carpet even when SK_Phase is active. See also
        the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-laguerre-gaussian-optical-vortex-allen-1992-orbital-angular-momentum-height-field-stage-floor-webxr"
        >
          Laguerre–Gaussian optical vortex
        </Link>{" "}
        tutorial for the same stage-floor pattern applied to beam intensity
        profiles.
      </p>

      <h2>Troubleshooting</h2>
      <ul className="list-disc pl-5 space-y-1">
        <li>
          <strong>Flat mesh at grating plane:</strong> the SK_Phase shape key
          will look flat at z=0 by design — phase objects have uniform
          amplitude. Slide the SK_Phase key to 1.0 and rotate to a side view
          (Numpad 1) to see height variation along z.
        </li>
        <li>
          <strong>Colour missing:</strong> open{" "}
          <em>Object Data Properties → Color Attributes</em> and confirm{" "}
          <code>TC_Intensity</code> exists with domain POINT. Re-run
          blueprint.py if absent.
        </li>
        <li>
          <strong>GLB export fails:</strong> confirm Blender 5.1 has the
          built-in glTF 2.0 exporter enabled (Extensions → glTF 2.0) and
          that the blend file has been saved at least once (the{" "}
          <code>//</code> relative path requires a saved file).
        </li>
        <li>
          <strong>Carpet looks wrong:</strong> increase N_HARM in the script
          constants to 30 for a denser harmonic series, or decrease to 10 for
          faster iteration. Fewer harmonics give a smoother but less detailed
          carpet.
        </li>
      </ul>
    </>
  );
}

export const entry: Entry = buildInstructable({
  slug:        SLUG,
  title:       TITLE,
  lede:        LEDE,
  date:        "2026-09-12",
  topics:      ["scripting", "numpy", "optics", "diffraction", "stage-floor", "webxr"],
  body:        <Body />,
  libraryPath: `blends/scripting/${SLUG.replace("blender-tutorial-", "")}`,
});
