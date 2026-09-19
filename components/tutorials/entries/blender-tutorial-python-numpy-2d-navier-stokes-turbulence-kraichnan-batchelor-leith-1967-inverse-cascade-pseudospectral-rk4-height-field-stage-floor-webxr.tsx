import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-2d-navier-stokes-turbulence-kraichnan-batchelor-leith-1967-inverse-cascade-pseudospectral-rk4-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — 2D Navier-Stokes Turbulence: Vorticity-Streamfunction Pseudospectral, Kraichnan-Batchelor-Leith (1967) Inverse Energy Cascade, Height-Field Stage Floor for WebXR (Blender 5.1)";

const LEDE =
  "Two-dimensional turbulence is the mirror image of the 3D turbulence you see in a river. In 3D, energy cascades from large eddies down to small viscous scales — Kolmogorov's famous k⁻⁵/³ forward cascade. In 2D, a second conserved quantity — enstrophy — prevents energy from flowing downscale. Instead it piles up in progressively larger structures: an inverse cascade. Robert Kraichnan, George Batchelor, and Cecil Leith independently predicted this in 1967, and it has since been verified in soap films, planetary atmospheres, and ocean mesoscale eddies. This tutorial integrates the 2D NS equations in spectral space using pseudo-spectral pseudospectral pseudo-spectral pseudospectral dealiasing and RK4, bakes four vorticity snapshots into shape keys, and exports the result as a height-field stage floor for WebXR.";

function Body() {
  return (
    <>
      <p>
        The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-complex-ginzburg-landau-pde-spiral-turbulence-benjamin-feir-defect-height-field-stage-floor-webxr"
        >
          Complex Ginzburg-Landau equation
        </Link>{" "}
        produces spiral defect turbulence — spatial chaos in a field of coupled
        oscillators. The 2D Navier-Stokes equations produce something more
        structured: a physical fluid where vortex filaments merge, pair, and
        condense into domain-scale coherent structures. The underlying reason is
        the double conservation law that 2D geometry imposes.
      </p>

      <h2>Why 2D turbulence is different</h2>

      <p>
        In a 2D incompressible fluid, two global quantities are conserved at
        zero viscosity:
      </p>

      <pre>{`Kinetic energy   E = ½ ∫ |u|² dA = ½ Σ_k |û_k|²
Enstrophy        Z = ½ ∫  ω²  dA = ½ Σ_k k² |ω̂_k|²

In 3D only E is conserved. The extra enstrophy constraint changes
everything: energy cannot cascade to small scales without simultaneously
generating infinite enstrophy, which is impossible. Instead:

  Energy → large scales   (inverse cascade,  E(k) ~ k^{-5/3}, k < k_f)
  Enstrophy → small scales (direct cascade,  E(k) ~ k^{-3},   k > k_f)

k_f = injection wavenumber (here k_f = 6).
Both E(k) exponents were predicted by Kraichnan (1967) using
dimensional analysis on the spectral flux — the same approach Kolmogorov
used for 3D but with two fluxes instead of one.`}</pre>

      <p>
        The direct consequence in the simulation: small eddies at wavenumber 6
        gradually merge into larger and larger structures. Over long enough
        time, a single large dipole fills the domain — turbulence
        &ldquo;condenses&rdquo; to the box scale. This condensation is visible in the{" "}
        <strong>SK_Condensed</strong> and <strong>SK_Forced</strong> shape keys.
      </p>

      <h2>Vorticity-streamfunction formulation</h2>

      <p>
        For a 2D incompressible fluid (∇·u = 0), we replace the primitive
        variables (u, v, p) with:
      </p>

      <pre>{`Vorticity      ω = ∂v/∂x − ∂u/∂y       (scalar in 2D, zero in irrotational flow)
Stream function ψ  defined by u = +∂ψ/∂y, v = −∂ψ/∂x

∇·u = ∂(+∂ψ/∂y)/∂x + ∂(−∂ψ/∂x)/∂y = 0   ← automatically satisfied
∇²ψ = −ω                                   ← Poisson equation`}</pre>

      <p>
        The pressure p disappears entirely (it can be recovered post-hoc from
        the Bernoulli equation if needed). The only prognostic equation is:
      </p>

      <pre>{`∂ω/∂t + u·∇ω = ν∇²ω + f

Left side:   material derivative of vorticity (Kelvin's theorem: vortex lines
             move with the fluid in 2D, they cannot be stretched like in 3D)
Right side:  viscous diffusion + external stochastic forcing`}</pre>

      <h2>Pseudo-spectral method</h2>

      <p>
        Spatial derivatives are exact in Fourier space: ∂/∂x → ik_x. The
        algorithm alternates between spectral and physical space:
      </p>

      <pre>{`Spectral step (linear terms):
  ψ̂_k = −ω̂_k / k²              Poisson solve (O(1) per mode)
  û_k = +ik_y ψ̂_k               velocity x
  v̂_k = −ik_x ψ̂_k               velocity y
  ∂ω̂/∂x = ik_x ω̂_k, ∂ω̂/∂y = ik_y ω̂_k

Physical step (nonlinear term, via IFFT):
  J = u·(∂ω/∂x) + v·(∂ω/∂y)    pointwise multiplication (exact)

Back to spectral:
  Ĵ = FFT(J)                    then dealias

Full RHS:
  ∂ω̂/∂t = −Ĵ − νk²ω̂ + f̂`}</pre>

      <h2>Dealiasing: the 2/3 rule</h2>

      <p>
        The nonlinear product u·∂ω/∂x in physical space involves two functions
        each with Fourier content up to wavenumber k_max = N/2. Their product
        has content up to 2·k_max = N, which exceeds the grid&rsquo;s Nyquist
        frequency N/2. The excess folds back (&ldquo;aliases&rdquo;) onto low
        wavenumbers. Orszag&rsquo;s 1971 fix:
      </p>

      <pre>{`Keep only modes with |k_x| < N/3  AND  |k_y| < N/3  (2/3 rule).
After dealiasing, the maximum product wavenumber is 2·(N/3) = 2N/3 < N/2 — safe.

Without this, aliasing errors inject spurious energy at large scales,
corrupting the inverse cascade within ~100 time steps.`}</pre>

      <pre>{`# in blueprint.py
kmax = N // 3
dm   = (np.abs(KX) < kmax) & (np.abs(KY) < kmax)   # Boolean mask, rfft2 shape`}</pre>

      <h2>RK4 time integration</h2>

      <p>
        Classical 4th-order Runge-Kutta applied to the full RHS (viscous +
        nonlinear + forcing). The stability limit for explicit RK4 on the viscous
        term is DT &lt; 2/ν·(2π/N)² ≈ 0.050; the nonlinear CFL DT &lt; Δx/U
        ≈ 0.05/(1.0) ≈ 0.05. Using DT = 0.004 gives CFL ≈ 0.08, safely stable.
      </p>

      <pre>{`k1 = rhs(ω̂)
k2 = rhs(ω̂ + ½·DT·k1)
k3 = rhs(ω̂ + ½·DT·k2)
k4 = rhs(ω̂ +    DT·k3)
ω̂_new = ω̂ + (DT/6)·(k1 + 2k2 + 2k3 + k4)`}</pre>

      <p>
        An alternative is the integrating-factor (ETD) approach used for the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-burgers-equation-1948-cole-hopf-exact-shock-formation-viscous-regularisation-height-field-stage-floor-webxr"
        >
          Burgers equation
        </Link>{" "}
        and the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-gray-scott-1984-pearson-1993-activator-depletion-turing-spot-worm-hole-height-field-stage-floor-webxr"
        >
          Gray-Scott system
        </Link>
        : multiply through by exp(νk²t) to make the viscous term exact.
        Explicit RK4 is adequate here because ν is small and the forced
        turbulent state is far from stiffness.
      </p>

      <h2>Stochastic forcing</h2>

      <pre>{`# thin ring at wavenumber K_FORCE = 6
k_mag = sqrt(KX² + KY²)
fmask = (k_mag >= K_FORCE − 0.5) & (k_mag <= K_FORCE + 0.5)

# random complex phase, normalised so energy injection is resolution-independent
phi = rng.uniform(0, 2π, shape)
fh  = AMP · fmask · exp(iφ) / max(fmask.sum(), 1)

Normalising by the number of forced modes ensures that doubling the
resolution does not double the energy input — an easy source of
resolution-dependent results.`}</pre>

      <h2>Four shape keys</h2>

      <pre>{`Basis         t ~ 300 Δt   Early turbulence: small eddies at forcing scale k=6.
                            Enstrophy forward cascade has filled small scales.
                            Inverse cascade has barely begun.

SK_Cascade    t ~ 800 Δt   Inverse cascade developing: eddies at k=3,4 visible.
                            KBL slope E(k)~k^{-5/3} emerging below k_f.
                            Height field shows broader, lower-frequency hills.

SK_Condensed  t ~ 1600 Δt  Coherent vortex condensation: a large cyclone-anticyclone
                            dipole pair dominates the domain. Domain-scale blue-amber
                            contrast. Classic signature of 2D turbulence in a box.

SK_Forced     t ~ 2600 Δt  Saturated forced state: large-scale vortex nearly fills
                            the domain. Energy input from forcing balanced by
                            viscous dissipation at small scales. Quasi-steady.`}</pre>

      <h2>Height encoding and colour</h2>

      <pre>{`ω_norm = (ω − ω_min) / (ω_max − ω_min)   ∈ [0, 1]
z      = ω_norm × Z_SCALE                  ∈ [0, 0.38 m]

colour = COBALT + ω_norm × (AMBER − COBALT)
       = (0.027, 0.159, 0.557) → (0.980, 0.620, 0.050)

Negative vorticity (clockwise / cyclonic)     → cobalt
Positive vorticity (anticlockwise / anticyclonic) → amber

Stored as FLOAT_COLOR attribute "NS2D_Vort" on the POINT domain.
Driven by ShaderNodeAttribute in the Principled BSDF (Base Colour
+ Emission Colour at strength 1.6) so vortex cores glow in WebXR.`}</pre>

      <h2>Mesh construction</h2>

      <pre>{`N = 128  →  16 384 vertices,  16 129 quad faces

xs = linspace(−WORLD_SCALE, +WORLD_SCALE, N)   WORLD_SCALE = 4.0 m
ys = linspace(−WORLD_SCALE, +WORLD_SCALE, N)
xx, yy = meshgrid(xs, ys, indexing="ij")

verts = column_stack([xx, yy, z_field]).tolist()
faces: CCW quads  (ix*N+iy, ix*N+iy+N, ix*N+iy+N+1, ix*N+iy+1)

After from_pydata: rotate −90° about X, apply transform.
holoflow:category = "stage-floor", holoflow:facet = True.`}</pre>

      <h2>Troubleshooting</h2>

      <pre>{`Problem: simulation blows up (vorticity → ∞) within 100 steps
Cause:   dealiasing mask not applied before IFFT of velocity/gradient fields.
Fix:     multiply u_h, v_h, wx_h, wy_h by dm before irfft2.
         Also apply dm to fft2(J) result.

Problem: inverse cascade not visible — all snapshots look the same
Cause:   AMP_FORCE too high; nonlinear term overwhelmed by forcing amplitude.
Fix:     Reduce AMP_FORCE to 0.3–0.5. Or increase N_BURN so small-scale
         turbulence is established before recording.

Problem: shape keys all look flat
Cause:   foreach_set("co", ...) called on obj.data.vertices instead of sk.data.
Fix:     Call obj.shape_key_add(name=…) first, then sk.data.foreach_set.
         The Basis key must be key_blocks[0].

Problem: GLB has no morph targets in Three.js
Fix:     Confirm export_morph=True in bpy.ops.export_scene.gltf.
         Three.js: mesh.morphTargetInfluences[i] = 1.0 to activate key i.

Problem: spectral ring too wide / too narrow
Cause:   K_FORCE ± 0.5 only covers 1 wavenumber; increase band to ± 1.5
         for broader energy injection. Wider band = faster turbulence onset.`}</pre>

      <h2>Outside sources</h2>

      <p>
        <strong>Kraichnan RH (1967)</strong> &ldquo;Inertial ranges in two-dimensional
        turbulence.&rdquo; <em>Physics of Fluids</em> 10:1417–1423.{" "}
        doi:<a className={lk} href="https://doi.org/10.1063/1.1762301">
          10.1063/1.1762301
        </a>. PD (&gt;50 yr). Predicts k⁻⁵/³ inverse energy cascade and k⁻³
        direct enstrophy cascade using dimensional analysis on the spectral
        fluxes — a radically different starting point from Kolmogorov (1941)&rsquo;s
        3D derivation because enstrophy imposes an additional constraint.
        Related: Batchelor GK (1969) <em>Phys Fluids Suppl</em> 12:233–239;
        Leith CE (1968) <em>Phys Fluids</em> 11:671–673 (independent simultaneous
        derivations); Tabeling P (2002) <em>Phys Rep</em> 362:1–62 (review).
      </p>

      <p>
        <strong>NumPy</strong> BSD-3-Clause.{" "}
        <a className={lk} href="https://numpy.org">numpy.org</a>.
        Harris CR et al. (2020) <em>Nature</em> 585:357–362.
        The rfft2/irfft2 pair used here runs at O(N² log N) per step — on a
        128² grid, the entire simulation is fast enough to run interactively in
        Blender&rsquo;s Python environment.
        Related: SciPy BSD-3-Clause{" "}
        <a className={lk} href="https://github.com/scipy/scipy">
          github.com/scipy/scipy
        </a>{" "}
        (add scipy.fft.next_fast_len for non-power-of-two N).
      </p>

      <h2>Studio cross-references</h2>

      <ul>
        <li>
          <Link
            className={lk}
            href="/tutorials/blender-tutorial-python-numpy-complex-ginzburg-landau-pde-spiral-turbulence-benjamin-feir-defect-height-field-stage-floor-webxr"
          >
            Complex Ginzburg-Landau equation
          </Link>{" "}
          — spiral defect turbulence driven by the Benjamin-Feir instability; a
          phase-field cousin of NS turbulence with a very different condensation
          mechanism (frozen defect cores vs. merging vortex dipoles).
        </li>
        <li>
          <Link
            className={lk}
            href="/tutorials/blender-tutorial-python-numpy-gray-scott-1984-pearson-1993-activator-depletion-turing-spot-worm-hole-height-field-stage-floor-webxr"
          >
            Gray-Scott reaction-diffusion
          </Link>{" "}
          — also uses pseudo-spectral + ETD stepping on a periodic 128² grid;
          the spot and worm morphologies are a reaction-diffusion analogue of
          the vortex structures that appear here.
        </li>
        <li>
          <Link
            className={lk}
            href="/tutorials/blender-tutorial-python-numpy-burgers-equation-1948-cole-hopf-exact-shock-formation-viscous-regularisation-height-field-stage-floor-webxr"
          >
            Burgers equation
          </Link>{" "}
          — 1D version of the NS advection term u·∂u/∂x; same viscosity /
          advection competition, same shock formation physics, solved with the
          Cole-Hopf exact solution rather than pseudospectral.
        </li>
        <li>
          <Link
            className={lk}
            href="/tutorials/blender-tutorial-python-numpy-kpz-kardar-parisi-zhang-1986-stochastic-surface-growth-universality-height-field-stage-floor-webxr"
          >
            Kardar-Parisi-Zhang stochastic growth
          </Link>{" "}
          — shares the (∇h)² nonlinearity with Burgers via the Hopf-Cole
          substitution; stochastic forcing on a height field, same WebXR
          height-field stage floor format.
        </li>
        <li>
          <Link
            className={lk}
            href="/tutorials/blender-tutorial-python-numpy-fitzhugh-nagumo-1961-excitable-media-trigger-wave-spiral-height-field-stage-floor-webxr"
          >
            FitzHugh-Nagumo excitable media
          </Link>{" "}
          — also produces 2D spiral wave patterns that visually resemble the
          vortex dipoles in 2D turbulence, but through reaction-diffusion rather
          than fluid mechanics.
        </li>
      </ul>
    </>
  );
}

export const blenderTutorialPythonNumpyNs2dTurbulenceKraichnanBatchelorLeith1967InverseCascadePseudospectralRk4HeightFieldStageFloorWebxrEntry: Entry =
  buildInstructable({
    slug: SLUG,
    title: TITLE,
    lede: LEDE,
    date: "2026-09-19",
    tags: [
      "blender",
      "python",
      "scripting",
      "fluid-dynamics",
      "turbulence",
      "navier-stokes",
      "pseudospectral",
      "inverse-cascade",
      "webxr",
      "stage-floor",
    ],
    body: Body,
  });
