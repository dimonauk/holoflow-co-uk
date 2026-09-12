import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-kpz-kardar-parisi-zhang-1986-stochastic-surface-growth-kpz-universality-class-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — KPZ Equation: Kardar–Parisi–Zhang 1986 Stochastic Surface Growth, Semi-Implicit Pseudo-Spectral, KPZ Universality Class vs Edwards–Wilkinson, Height-Field Stage Floor for WebXR (Blender 5.1)";

const LEDE =
  "Drip water onto dry sand and watch the spreading front: it does not grow as a smooth hemisphere — it roughens, with some fingers advancing faster than the average, driven by the very slope of the surface itself. That self-amplifying tilt is what the KPZ nonlinear term captures. This blueprint simulates the 1986 Kardar–Parisi–Zhang equation on a 128 × 128 periodic grid, compares it against the earlier Edwards–Wilkinson limit (λ = 0), and maps the stochastic height field to a cobalt–amber stage floor mesh for WebXR.";

function Body() {
  return (
    <>
      <p>
        Two equations govern stochastic surface growth. The earlier one, from
        1982, is due to Edwards and Wilkinson: the interface height satisfies a
        linear stochastic heat equation and fluctuations are Gaussian. Four years
        later, Kardar, Parisi, and Zhang added a single quadratic term —
        (λ/2)|∇h|² — and everything changed. That term measures how much the
        surface is tilted; where there is slope, growth is faster along the local
        normal rather than straight up. The consequence is a new universality
        class, with different scaling exponents, non-Gaussian height statistics,
        and — in 1D — an exact connection to the longest increasing subsequence
        of a random permutation and the longest eigenvalue edge of a large random
        matrix.
      </p>

      <p>
        Comparing the two models is the centrepiece of this tutorial. The{" "}
        <strong>SK_Long</strong> shape key runs KPZ (λ = 1) to t = 12; the{" "}
        <strong>SK_EW</strong> key runs Edwards–Wilkinson (λ = 0) to the same t
        with the same noise seed. The KPZ surface is rougher, the peaks are
        spikier relative to the valleys, and the height distribution is skewed —
        a fingerprint of the Tracy–Widom GUE law in 1D, and still non-Gaussian
        in 2D. The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-allen-cahn-phase-field-mean-curvature-motion-allen-cahn-1979-stage-floor-webxr"
        >
          Allen–Cahn
        </Link>{" "}
        and{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-cahn-hilliard-phase-field-spinodal-decomposition-ostwald-ripening-stage-floor-webxr"
        >
          Cahn–Hilliard
        </Link>{" "}
        equations are deterministic phase-field models on the same 128 × 128
        grid; this tutorial adds the stochastic layer that governs out-of-equilibrium
        interfaces.
      </p>

      <h2>Equation and universality class</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`KPZ equation (Kardar, Parisi, Zhang 1986 PRL 56:889):

  ∂h/∂t = ν∇²h  +  (λ/2)|∇h|²  +  η(x,t)
            ↑            ↑             ↑
       surface      tilt growth    white noise
       tension      (KPZ term)    ⟨η η⟩ = 2D δ(x−x′)δ(t−t′)

Hopf–Cole transformation (1D exact solution):
  h = (2ν/λ) log Z  →  ∂Z/∂t = ν∇²Z + (λ/2ν)ηZ
  (stochastic heat equation — exactly solvable in 1D)

Universality exponents (2D KPZ, numerical):
  α ≈ 0.38   roughness: W(L) ~ L^α  at saturation
  β ≈ 0.24   growth:    W(t) ~ t^β  for  t << L^z
  z ≈ 1.58   dynamic:   z = α/β

Edwards–Wilkinson limit (λ = 0):
  α = 1/2,  β = 1/4,  z = 2   (Gaussian, purely diffusive)

Family–Vicsek scaling: W(L,t) = L^α · f(t / L^z)`}
      </pre>

      <h2>Why the (λ/2)|∇h|² term is non-trivial</h2>
      <p>
        A flat interface (|∇h| = 0) is unaffected by the KPZ term. The moment
        noise creates any slope, the term is active: a tilted patch grows faster
        along its own outward normal rather than straight up. This is not a small
        correction — it changes the scaling class. The renormalisation-group
        analysis of Kardar, Parisi, and Zhang showed that in 1D and 2D, any
        non-zero λ flows to strong coupling and the EW fixed point is unstable.
        In 1D this is proven exactly via the Hopf–Cole mapping; in 2D it remains
        one of the outstanding problems of non-equilibrium statistical mechanics.
      </p>
      <p>
        The other PDE stage floors in this series — the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-swift-hohenberg-pde-hexagonal-rolls-benard-convection-stage-floor-webxr"
        >
          Swift–Hohenberg
        </Link>{" "}
        hexagonal rolls and the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-complex-ginzburg-landau-pde-spiral-turbulence-benjamin-feir-defect-height-field-stage-floor-webxr"
        >
          Complex Ginzburg–Landau
        </Link>{" "}
        spiral chaos — are deterministic. KPZ is intrinsically stochastic: run it
        twice with different seeds and you get statistically identical surfaces
        (same exponents, same distribution) but different realisations.
      </p>

      <h2>Numerical method — semi-implicit pseudo-spectral</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Split: ∂h/∂t = L̂h + N(h) + η
  L̂h = ν∇²h             (linear, stiff — treat implicitly)
  N(h) = (λ/2)|∇h|²     (nonlinear — explicit Euler)
  η = σ · N(0,1)         (Euler–Maruyama noise)

Semi-implicit update in Fourier space:
  ĥ_new(k) = [ ĥ(k) + dt · (N̂(k) + η̂(k)) ] / (1 + ν|k|²·dt)

Denominator stability: explicit Euler requires dt < 1/(ν·k_max²).
For k_max ≈ 50 rad/m and ν = 0.5: dt < 0.001 — impractical.
The denominator (1 + ν|k|²·dt) is unconditionally stable for any dt.

Gradient (spectral):
  ∂h/∂x = irfft2(i·kx·rfft2(h))  — spectral accuracy, no aliasing.

Noise amplitude (correct discretisation):
  σ = sqrt(2D / (dx² · dt))
  WHY dx²: continuous ⟨η(x)²⟩ = 2D concentrates 2D units per cell area dx².
  Omitting dx² underestimates roughening on coarse grids.

Mean removal: ⟨h⟩ → 0 each step.
  ⟨(λ/2)|∇h|²⟩ > 0 on a rough surface → mean height drifts up without removal.`}
      </pre>

      <h2>Blueprint walkthrough</h2>
      <p>
        Four simulation runs share the same random seed (137) so that the
        shape-key differences reflect physics, not luck. The constants block at
        the top sets <code>NU = 0.50</code> (surface tension),{" "}
        <code>LAM_BASIS = 1.0</code> and <code>LAM_STRONG = 2.0</code> (KPZ
        coupling), and <code>NOISE_D = 0.30</code> (noise temperature). The
        helper <code>_wavenumbers()</code> builds the rfft2 wavenumber arrays in
        physical units (rad/m), not integer cycles — this is essential so that ν
        carries the correct dimensional role and textbook formulae match without
        hidden factors of 2π.
      </p>
      <p>
        The simulation loop in <code>_simulate()</code> runs Euler–Maruyama: at
        each step, compute the spectral gradient to get |∇h|²; add noise; apply
        the semi-implicit denominator in Fourier space; subtract the mean. The
        result is normalised to [−1, +1] before being assigned to shape key data,
        so the mesh amplitude (HEIGHT_SCALE = 0.35 m) is consistent regardless
        of how rough the simulation grew.
      </p>
      <p>
        The vertex colour attribute <code>KPZ_Height</code> (FLOAT_COLOR) maps
        the Basis height linearly from cobalt (valleys, h = −1) to amber (ridges,
        h = +1). In Blender&apos;s Solid mode, switch{" "}
        <em>Colour → Attribute → KPZ_Height</em> to see the continuous cobalt–amber
        topology of the stochastic surface.
      </p>

      <h2>Shape-key physics guide</h2>
      <p>
        <strong>Basis</strong> (λ = 1, t = 3): the surface has roughened from
        flat. The texture is fine-grained; the height distribution is already
        slightly skewed toward sharper peaks. <strong>SK_Long</strong> (λ = 1,
        t = 12): the same KPZ process continued — coarser structure, deeper
        grooves, more pronounced asymmetry between peaks and valleys. This
        asymmetry is the visual signature of the Tracy–Widom skew: in 1D the
        exact probability of an anomalously high peak is an exponential tail,
        whereas the probability of an anomalously deep valley is a doubly
        exponential tail.
      </p>
      <p>
        <strong>SK_EW</strong> (λ = 0, t = 12): run the Edwards–Wilkinson
        equation to the same time with the same noise seed. The surface is
        perceptibly smoother, the peaks and valleys more symmetric. Scrubbing
        SK_Long → SK_EW in the Shape Keys panel is a direct visualisation of
        what the nonlinear KPZ term does to an interface. <strong>SK_Strong</strong>{" "}
        (λ = 2, t = 12): stronger coupling — the directional ridge structure
        is much more pronounced, with sharp ridgelines cutting across the mesh
        like a crumpled sheet of foil.
      </p>

      <h2>Failure modes and trade-offs</h2>
      <p>
        <strong>Aliasing from the nonlinear term:</strong> the (∇h)² product
        in real space generates Fourier modes up to twice the maximum resolved
        wavenumber. On a 128 × 128 grid without dealiasing these fold back.
        For moderate λ and dt the effect is small, but for SK_Strong (λ = 2)
        the surface can develop a small-scale grid-scale artefact. The fix is
        3/2-rule dealiasing (zero-pad the rfft2 output) — left out here to keep
        the blueprint concise; add <code>h_hat[n//3:2*n//3, :] = 0</code> before
        the update if you observe chessboard artefacts.
      </p>
      <p>
        <strong>dt too large:</strong> the semi-implicit scheme is stable for
        the linear part at any dt, but the explicit nonlinear and noise terms
        can go unstable for very large dt or λ. If the mesh produces NaN values
        reduce DT from 0.05 toward 0.01.
      </p>
      <p>
        <strong>Periodic vs flat boundary:</strong> the simulation uses periodic
        boundaries (natural for rfft2). The mesh stage floor looks best without
        visible seams. For the WebXR context this is fine — the Holoflow viewer
        tiles floor meshes.
      </p>

      <h2>Connections across the studio</h2>
      <p>
        The KPZ equation is the growth analogue of the deterministic phase-field
        models elsewhere in this series. Where{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-allen-cahn-phase-field-mean-curvature-motion-allen-cahn-1979-stage-floor-webxr"
        >
          Allen–Cahn
        </Link>{" "}
        minimises a free energy and{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-cahn-hilliard-phase-field-spinodal-decomposition-ostwald-ripening-stage-floor-webxr"
        >
          Cahn–Hilliard
        </Link>{" "}
        conserves a composition field, KPZ is irreversible: it grows the
        interface forever, roughening without bound in the thermodynamic limit.
        The pseudo-spectral method used here — rfft2 gradients plus semi-implicit
        linear treatment — is identical to the one in the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-swift-hohenberg-pde-hexagonal-rolls-benard-convection-stage-floor-webxr"
        >
          Swift–Hohenberg
        </Link>{" "}
        and{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-complex-ginzburg-landau-pde-spiral-turbulence-benjamin-feir-defect-height-field-stage-floor-webxr"
        >
          CGL
        </Link>{" "}
        blueprints.
      </p>

      <h2>Outside sources</h2>
      <p>
        <strong>Primary equation:</strong>{" "}
        <a
          className={lk}
          href="https://doi.org/10.1103/PhysRevLett.56.889"
          target="_blank"
          rel="noopener noreferrer"
        >
          Kardar M, Parisi G, Zhang Y-C (1986) "Dynamic scaling of growing
          interfaces" <em>Physical Review Letters</em> 56: 889–892
        </a>{" "}
        — mathematical content, public domain. Related:{" "}
        <a className={lk} href="https://github.com/spectralDNS/shenfun"
           target="_blank" rel="noopener noreferrer">spectralDNS/shenfun</a>{" "}
        (BSD-3) uses the same semi-implicit spectral approach at larger scale.
        <strong> Edwards–Wilkinson baseline:</strong>{" "}
        <a className={lk} href="https://doi.org/10.1098/rspa.1982.0056"
           target="_blank" rel="noopener noreferrer">Edwards &amp; Wilkinson (1982)
          <em> Proc. R. Soc. A</em> 381: 17–31</a>{" "}
        — mathematical content, public domain.
      </p>
    </>
  );
}

export const entry: Entry = buildInstructable({
  slug: SLUG,
  title: TITLE,
  lede: LEDE,
  date: "2026-09-12",
  topics: ["scripting", "physics", "pde", "stochastic", "numpy", "webxr"],
  body: <Body />,
  libraryPath:
    "blends/scripting/python-numpy-kpz-kardar-parisi-zhang-1986-stochastic-surface-growth-kpz-universality-class-height-field-stage-floor-webxr",
});
