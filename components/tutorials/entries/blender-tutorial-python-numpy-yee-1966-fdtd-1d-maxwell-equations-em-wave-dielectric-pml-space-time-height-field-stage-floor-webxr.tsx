import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-yee-1966-fdtd-1d-maxwell-equations-em-wave-dielectric-pml-space-time-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — Yee 1966 FDTD: 1D Maxwell Equations, EM Wave Propagation, Dielectric Interface, Resonant Cavity & CPML Absorbing Boundaries, Space–Time Height-Field Stage Floor for WebXR (Blender 5.1)";

const LEDE =
  "In 1966 Kane Yee published a two-page paper showing that Maxwell's equations could be solved on a staggered spatial grid — E and H fields offset by half a cell — updated in alternating half-time-steps. That single insight, now called the FDTD method, underlies virtually every modern EM solver from antenna design to photonic crystal simulation. This blueprint implements the 1D Yee scheme in NumPy inside Blender 5.1, runs four EM wave scenarios (free-space propagation, Fresnel reflection at a dielectric interface, resonant cavity standing waves, and CPML absorbing boundaries), and bakes each into a shape key of a 128 × 128 space–time height-field stage floor exported as a Draco-compressed GLB for WebXR.";

function Body() {
  return (
    <>
      <p>
        The Yee staggered-grid scheme is the electromagnetic counterpart to the
        leapfrog symplectic integrators used in{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-gn-simulation-zone-n-body-gravity-leapfrog-orbital-dance-poi-webxr"
        >
          N-body orbital mechanics
        </Link>
        : interleaving the two field updates in both space and time keeps the
        scheme second-order accurate at negligible extra cost.  The same
        staggered philosophy appears in the pseudospectral approach used for the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-korteweg-de-vries-1895-soliton-collision-pseudospectral-rk4-space-time-height-field-stage-floor-webxr"
        >
          KdV soliton space–time floor
        </Link>
        , where E and H are replaced by the wave height and its velocity.
      </p>

      <h2>The equations (TM mode, 1D)</h2>

      <pre>{`Faraday:  ∂H_y/∂t = −(1/μ₀) ∂E_z/∂x
Ampere:   ∂E_z/∂t = +(1/ε₀ε_r) ∂H_y/∂x

Yee discretisation on staggered grid:
  H_y^{n+½}[j+½] = da[j]·H_y^{n−½}[j+½]  −  db[j]·(E_z[j+1]−E_z[j])
  E_z^{n+1}[j]   = ca[j]·E_z^n[j]          +  cb[j]·(H_y[j+½]−H_y[j−½])

Free space (ε_r=1, σ=0): da=db=1, cb=DT/DX = 0.45
CFL stability:  DT ≤ DX/c_max = 1.0  →  DT = 0.45 (CFL = 0.45)`}</pre>

      <p>
        The minus sign in the H update comes from Faraday&apos;s law: a
        positive spatial gradient ∂E_z/∂x drives H_y negative (the right-hand
        rule).  The plus sign in the E update comes from Ampere: a positive
        spatial gradient ∂H_y/∂x drives E_z positive.  Together they support
        right-going plane waves where E_z and H_y are in phase, and left-going
        waves where they are anti-phase.
      </p>

      <h2>Why CFL = 0.45 and not 0.5</h2>

      <p>
        The strict Courant–Friedrichs–Lewy stability limit for the 1D Yee
        scheme is CFL = DT·c/DX ≤ 1.  The numerical phase velocity equals the
        physical speed c exactly at CFL = 1, but any value below 1 is stable.
        Using CFL = 0.45 (DT = 0.45 in normalised units) leaves a margin for
        numerical rounding and for the CPML scenario where the effective wave
        speed inside the absorbing layer can temporarily exceed c/ε_r at the
        abrupt conductivity gradient.  Compare the explicit Euler limit for the
        stiff{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-fitzhugh-nagumo-1961-excitable-media-trigger-wave-spiral-height-field-stage-floor-webxr"
        >
          FitzHugh–Nagumo PDE
        </Link>
        , which requires ETD1 spectral integration because its stiffness ratio
        is ∼ 10⁶; the FDTD scheme, by contrast, is non-stiff as long as the CFL
        condition is respected.
      </p>

      <h2>Space–time height field</h2>

      <p>
        Each simulation stores NT_STORE = 128 E_z snapshots at evenly spaced
        intervals.  The resulting (128 time) × (128 space) matrix becomes the
        vertex z-coordinates of a 128 × 128 quad-mesh:
      </p>

      <pre>{`height[j, i] = 0.5 + 0.5 * Ez(x_i, t_j) / E_max   ∈ [0, 1]
colour[j, i] = |Ez(x_i, t_j)| / E_max              ∈ [0, 1]
              → cobalt (quiet) to amber (peak field)`}</pre>

      <p>
        This is the same space–time encoding used for the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-burgers-equation-1948-cole-hopf-exact-shock-formation-viscous-regularisation-height-field-stage-floor-webxr"
        >
          Burgers shock formation
        </Link>{" "}
        and KdV soliton floors.  In the Basis (free-space) key, the two
        wavefronts leaving the source at x=20 appear as two diagonal amber
        streaks at ±45° in the (x, t) plane — the slope is exactly DX/DT = 1/0.45
        (the normalised wave speed).
      </p>

      <h2>Scenario 1 — Basis: free space, PEC walls</h2>

      <pre>{`eps_r = 1 everywhere,  sigma = 0 everywhere
Source: soft Gaussian at x=20,  t₀=40,  σ_t=15
Boundaries: Ez[0] = Ez[127] = 0  (perfect electric conductor)
Duration: 256 steps  →  128 snapshots`}</pre>

      <p>
        The Gaussian pulse splits immediately into left-going and right-going
        halves.  The right-going copy reaches the PEC wall at x=127 around
        t ≈ 240 steps (107 cells / 0.45 grid steps per timestep ≈ 238 steps)
        and inverts on reflection (PEC forces E=0, so the reflected pulse has
        opposite sign).  The left-going copy reflects off x=0 sooner
        (20 cells / 0.45 ≈ 44 steps) and also inverts.  Both reflections are
        clearly visible as secondary diagonal streaks.
      </p>

      <h2>Scenario 2 — SK_Dielectric: Fresnel interface</h2>

      <pre>{`eps_r[0:64] = 1,  eps_r[64:] = 4  (ε_r = 4)
Wave speed in dielectric: c/√ε_r = 1/2 of free space
Fresnel coefficients at normal incidence:
  r = (√ε₁ − √ε₂)/(√ε₁ + √ε₂) = (1−2)/(1+2) = −1/3  (reflected, inverted)
  t = 2√ε₁/(√ε₁ + √ε₂) = 2/3  (transmitted E-field amplitude)`}</pre>

      <p>
        The incident pulse amplitude is normalised to 1.  After the interface
        at x=64, the transmitted pulse has amplitude 2/3 but travels at half
        the speed, so its diagonal slope doubles in the space–time plot.  A
        weak backward streak (amplitude 1/3, inverted) reflects toward x=0.
        This is the electromagnetic analogue of the quantum tunnelling
        reflection seen in the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-tdse-split-operator-fft-double-slit-quantum-interference-webxr"
        >
          TDSE double-slit blueprint
        </Link>
        , where a Gaussian wave-packet hitting a potential step splits into
        reflected and transmitted components with amplitudes governed by the
        impedance mismatch.
      </p>

      <h2>Scenario 3 — SK_Cavity: resonant standing waves</h2>

      <pre>{`eps_r = 1 everywhere
PEC walls enforced at Ez[16] = 0 and Ez[112] = 0
Cavity length: L = 112 − 16 = 96 cells
Source: at x=40 (offset from centre to couple to all modes)
Duration: 512 steps  →  128 snapshots (store every 4th step)

Resonant frequencies (normalised): f_n = n·c/(2L) = n/192   n = 1,2,3,…
Fundamental wavelength: λ₁ = 2L = 192 cells`}</pre>

      <p>
        The source injects energy at all frequencies simultaneously (a
        Gaussian pulse has broad bandwidth).  Only the cavity modes
        f_n = n/(2L) constructively interfere; all other frequencies are
        quickly damped by destructive interference at the PEC walls.  In
        the space–time height field the standing wave appears as vertical
        amber stripes (spatial antinodes, fixed in x) superimposed on the
        early-time transient.  Compare the modal structure with the Chladni
        eigenmodes in the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-chladni-figures-standing-wave-eigenmodes-nodal-lines-height-field-webxr"
        >
          Chladni figures blueprint
        </Link>
        , where the 2D plate modes are computed directly as eigenvectors of
        the Laplacian rather than via time-domain excitation.
      </p>

      <h2>Scenario 4 — SK_PML: CPML absorbing boundaries</h2>

      <pre>{`PML_CELLS = 12
σ(x) = σ_max · [(distance from boundary) / PML_CELLS]²
Matching condition: σ_H/μ = σ_E/ε  →  σ_H = σ_E (in free space)

CPML update coefficients:
  ca[j] = (2ε_r − σ_E·DT) / (2ε_r + σ_E·DT)
  cb[j] = (2·DT/DX)      / (2ε_r + σ_E·DT)
  da[j] = (2   − σ_H·DT) / (2    + σ_H·DT)
  db[j] = (2·DT/DX)      / (2    + σ_H·DT)`}</pre>

      <p>
        Berenger&apos;s 1994 PML works by matching the wave impedance Z₀ = √(μ/ε)
        at the PML interface: as long as σ_H/μ = σ_E/ε, an incoming plane wave
        of any angle and frequency passes into the PML without reflection and
        is exponentially attenuated.  The parabolic conductivity profile
        σ = σ_max·(dist/d)² avoids the step discontinuity that would cause
        reflections at the PML boundary itself.  In the space–time plot the
        pulse enters the PML region and simply vanishes — no backward streak,
        in contrast to the PEC wall reflections in the Basis key.
      </p>

      <p>
        The same impedance-matching principle governs the perfectly matched
        source used in the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-fraunhofer-diffraction-fft-aperture-psf-airy-disk-stage-floor-webxr"
        >
          Fraunhofer diffraction blueprint
        </Link>
        : forcing the aperture field to match the free-space wave impedance
        suppresses spurious edge reflections that would corrupt the far-field
        diffraction pattern.
      </p>

      <h2>Blueprint walkthrough</h2>

      <p>
        Open <code>blueprint.py</code> in Blender 5.1&apos;s Scripting workspace
        and press <strong>Run Script</strong> (or Alt+P).
      </p>

      <h3>Step 1 — CPML coefficient arrays</h3>

      <pre>{`# Parabolic conductivity profile (only nonzero inside PML region)
for i in range(PML_CELLS):
    dist_e = (PML_CELLS - i) / PML_CELLS       # E at integer position
    dist_h = (PML_CELLS - i - 0.5) / PML_CELLS # H at half-integer
    sigma_e[i] = SIGMA_MAX * dist_e**2
    sigma_e[NX-1-i] = SIGMA_MAX * dist_e**2    # symmetric right PML

# CPML update coefficients absorb both eps_r and sigma
ca = (2*eps_r - sigma_e*DT) / (2*eps_r + sigma_e*DT)
cb = (2*DT/DX)              / (2*eps_r + sigma_e*DT)`}</pre>

      <h3>Step 2 — leapfrog loop</h3>

      <pre>{`for t in range(nt_run):
    # H update — Faraday: H_y[j] depends on E_z[j] and E_z[j+1]
    Hy = da * Hy - db * (Ez[1:] - Ez[:-1])

    # Soft source: add pulse energy to E_z without overwriting
    Ez[source_pos] += exp(-0.5 * ((t - T0) / SIGMA_T)**2)

    # E update — Ampere: E_z[j] depends on H_y[j] and H_y[j-1]
    Ez[1:-1] = ca[1:-1]*Ez[1:-1] + cb[1:-1]*(Hy[1:] - Hy[:-1])`}</pre>

      <p>
        The key subtlety is the indexing: <code>Hy[1:] - Hy[:-1]</code> gives
        H_y[j] − H_y[j−1] for j = 1…NX−2, which is exactly the discrete
        gradient ΔH_y/Δx centred on the E node at position j·ΔX.  The H array
        has NX−1 elements (H at each half-integer position) so{" "}
        <code>Ez[1:] - Ez[:-1]</code> gives E_z[j+1] − E_z[j] for
        j = 0…NX−2, centred on the H node at (j+½)·ΔX.
      </p>

      <h3>Step 3 — mesh and shape keys</h3>

      <pre>{`# Each (128, 128) snapshot matrix → one set of vertex z-coordinates
h_sk, _ = normalise(sk_field)   # → [0, 1]
for j in range(NT_STORE):
    for i in range(NX):
        z = h_sk[j, i] * Z_SCALE
        coords.extend([x_off + i*cell_w, y_off + j*cell_h, z])
sk.data.foreach_set("co", coords)`}</pre>

      <h2>Troubleshooting</h2>

      <pre>{`Height field is flat (all 0.5)
  → E_max was near zero; check SOURCE_POS is inside the domain (1…NX-2).
  → For SK_PML, verify PML_CELLS < SOURCE_POS so the source isn't inside the PML.

SK_Cavity shows only transient noise, no clear standing wave
  → Increase NT_CAV from 512 to 800 to allow the resonance more time to build.
  → Move CAV_SOURCE off-centre (x=40 is already offset; x=50 also works).

PML reflections still visible in SK_PML
  → Increase SIGMA_MAX from 0.8 to 1.2, or increase PML_CELLS to 16.
  → A discontinuous step in σ at the inner PML boundary causes reflection;
    the parabolic profile avoids this, but numerical artefacts remain if σ
    grows too steeply over too few cells.

GLB has no morph targets in the browser
  → Verify export_morph=True in the GLB export call; Draco level > 6 can
    strip morph data in some gltf2 exporter versions.`}</pre>

      <h2>Outside sources</h2>

      <p>
        The foundational paper:{" "}
        <a
          className={lk}
          href="https://doi.org/10.1109/TAP.1966.1138693"
          target="_blank"
          rel="noopener noreferrer"
        >
          K. S. Yee, IEEE Trans. Antennas Propagat. 14(3):302–307, 1966
        </a>{" "}
        (Public Domain — &gt;50 years).  The CPML absorbing boundary:{" "}
        <a
          className={lk}
          href="https://doi.org/10.1006/jcph.1994.1159"
          target="_blank"
          rel="noopener noreferrer"
        >
          J.-P. Berenger, J. Comput. Phys. 114(2):185–200, 1994
        </a>{" "}
        (Public Domain — &gt;30 years).  Related open-source implementation:{" "}
        <a
          className={lk}
          href="https://github.com/NanoComp/meep"
          target="_blank"
          rel="noopener noreferrer"
        >
          MEEP — MIT Photonics FDTD (MIT licence)
        </a>
        .  Numerical computing:{" "}
        <a
          className={lk}
          href="https://github.com/numpy/numpy"
          target="_blank"
          rel="noopener noreferrer"
        >
          NumPy (BSD-3-Clause)
        </a>
        .
      </p>
    </>
  );
}

export const blenderTutorialPythonNumpyYee1966Fdtd1dMaxwellEquationsEmWaveDielectricPmlSpaceTimeHeightFieldStageFloorWebxrEntry: Entry =
  buildInstructable({
    slug: SLUG,
    date: "2026-09-19",
    title: TITLE,
    lede: LEDE,
    tags: [
      "scripting",
      "fdtd",
      "maxwell",
      "em-wave",
      "dielectric",
      "pml",
      "space-time",
      "webxr",
      "stage-floor",
    ],
    body: Body,
  });
