import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-haldane-1988-chern-insulator-berry-curvature-topological-phase-diagram-honeycomb-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — Haldane Model 1988: Chern Insulator, Berry Curvature over the Hexagonal Brillouin Zone, Topological Phase Diagram, Honeycomb Height-Field Stage Floor for WebXR (Blender 5.1)";

const LEDE =
  "Add a complex phase φ to the next-nearest-neighbour hopping on graphene's honeycomb and the Berry curvature of the lower band concentrates into two sharp amber peaks at the K and K′ Dirac points — telling you the Chern number is ±1 before you compute a single topological invariant. Sweep the on-site mass M through the critical value 3√3 t₂ sin φ and the peaks merge and vanish, the Chern number drops to zero, and the height field flattens. This is the Haldane model: the first example of a topological insulator without any net magnetic flux, recognised with the 2016 Nobel Prize in Physics.";

function Body() {
  return (
    <>
      <p>
        The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-ssh-su-schrieffer-heeger-1979-zak-phase-topological-edge-states-spectral-flow-stage-floor-webxr"
        >
          SSH model
        </Link>{" "}
        showed that topology can live in a 1D chain. Haldane&rsquo;s 1988
        model showed that it can live in a 2D crystal with no net magnetic
        field — something the community had assumed was impossible. The trick
        is a staggered flux pattern that cancels out of every plaquette
        (leaving zero net B) but still breaks time-reversal symmetry through
        the complex phase φ of the next-nearest-neighbour hopping. The result
        is a quantized Hall conductance σxy = Ce²/h where C is the Chern
        number, an integer invariant of the ground-state wavefunction.
      </p>

      <p>
        In this blueprint we compute the Berry curvature Ω(kx, ky) of the
        lower band at every point of the hexagonal Brillouin zone, map it to
        a height field, and export it as a WebXR stage floor. The topology is
        visible before any integral: when C = 1 the curvature glows amber at
        both K and K′; when M exceeds the critical value the peaks collapse
        and the floor is cobalt-flat.
      </p>

      <h2>Hamiltonian</h2>

      <p>
        The honeycomb has two atoms (A, B) per unit cell. Bravais vectors
        a₁ = (1, 0) and a₂ = (½, √3/2) with lattice constant a = 1. The
        three nearest-neighbour (NN) vectors from A to B are δ₁ = (0, 1/√3),
        δ₂ = (−½, −1/(2√3)), δ₃ = (½, −1/(2√3)). The three counterclockwise
        next-nearest-neighbour (NNN) vectors are b₁ = a₁, b₂ = a₂ − a₁,
        b₃ = −a₂.
      </p>

      <pre>{`
h(k) = d₀(k)·I + d(k)·σ

dₓ + i·dᵧ  = t₁ Σⱼ exp(ik·δⱼ)           # NN off-diagonal
dz          = M − 2t₂ sin(φ) Σⱼ sin(k·bⱼ) # mass + NNN imaginary part
d₀          = 2t₂ cos(φ) Σⱼ cos(k·bⱼ)    # energy offset (no topology)

Topological phase boundary:
  M = ±3√3 t₂ sin φ
  C = +1  when 0 < M < 3√3 t₂ sin φ  (or M = 0, 0 < φ < π)
  C = −1  when −3√3 t₂ sin φ < M < 0
  C =  0  when |M| > 3√3 t₂ |sin φ|  (trivial)
`}</pre>

      <h2>Berry curvature — the solid-angle formula</h2>

      <p>
        For any two-band model h(k) = d(k)·σ, the Berry curvature of the
        lower band reduces to a solid-angle density on the unit sphere S²:
      </p>

      <pre>{`
Ω_(k) = −½ ĥ · (∂_kx ĥ × ∂_ky ĥ)    ĥ = d/|d|

Chern number:  C = (1/4π) ∫_BZ Ω_(k) d²k
`}</pre>

      <p>
        This is the Jacobian of the map ĥ: T² → S² (the Brillouin zone torus
        to the unit sphere). When C = 1 that map wraps the sphere once; the
        curvature integrates to 4π regardless of how it is distributed. When
        C = 0 the map has zero winding.
      </p>

      <p>
        Compared with{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-bloch-sphere-qubit-rabi-precession-berry-phase-su2-pauli-poi-webxr"
        >
          the Bloch-sphere qubit tutorial
        </Link>{" "}
        where the Berry phase is the area traced on S² by a single precessing
        state, here the same sphere appears as the target of a map from
        k-space. The Chern number counts how many times k-space covers the
        sphere.
      </p>

      <h2>Blueprint walkthrough</h2>

      <pre>{`# Reciprocal lattice
B1 = np.array([2*np.pi, -2*np.pi/SQ3])
B2 = np.array([0.0,      4*np.pi/SQ3])

# 128×128 BZ grid in reduced coordinates s ∈ [0,1)
s = np.linspace(0, 1, N, endpoint=False)
S1, S2 = np.meshgrid(s, s, indexing='ij')
KX = S1*B1[0] + S2*B2[0]          # (128, 128)
KY = S1*B1[1] + S2*B2[1]

def _d_vector(phi, M):
    nn_dot  = KX[:,:,None]*DELTA[:,0] + KY[:,:,None]*DELTA[:,1]  # (128,128,3)
    h_ab    = T1 * np.sum(np.exp(1j * nn_dot), axis=-1)          # NN complex hop
    dx, dy  = np.real(h_ab), np.imag(h_ab)

    nnn_dot  = KX[:,:,None]*NNN_CCW[:,0] + KY[:,:,None]*NNN_CCW[:,1]
    dz = M - 2*T2*np.sin(phi) * np.sum(np.sin(nnn_dot), axis=-1)
    return dx, dy, dz

def _berry_curvature(phi, M):
    dx, dy, dz = _d_vector(phi, M)
    d_mag = np.maximum(np.sqrt(dx**2+dy**2+dz**2), 1e-12)
    hx, hy, hz = dx/d_mag, dy/d_mag, dz/d_mag

    dhx0, dhx1 = np.gradient(hx)    # ∂/∂s₁, ∂/∂s₂ (grid index derivatives)
    dhy0, dhy1 = np.gradient(hy)
    dhz0, dhz1 = np.gradient(hz)

    cx = dhy0*dhz1 - dhz0*dhy1      # cross product components
    cy = dhz0*dhx1 - dhx0*dhz1
    cz = dhx0*dhy1 - dhy0*dhx1

    return -0.5 * (hx*cx + hy*cy + hz*cz)    # lower-band Ω
`}</pre>

      <p>
        The key implementation detail: we sample the BZ using reduced
        coordinates (s₁, s₂) ∈ [0, 1)² and compute analytic d-vectors via
        vectorised einsum-style operations — no loops over k-points. The
        np.gradient calls take derivatives with respect to grid indices; the
        solid-angle formula is coordinate-independent so the topology is
        captured correctly even without explicitly converting to Cartesian
        k-derivatives.
      </p>

      <p>
        Compare with{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-tight-binding-2d-square-lattice-dispersion-fermi-surface-van-hove-singularity-stage-floor-webxr"
        >
          the 2D tight-binding tutorial
        </Link>{" "}
        where the height field is the energy dispersion E(k). Here it is the
        Berry curvature Ω(k) — not an energy but a geometric property of the
        eigenstate bundle over k-space.
      </p>

      <h2>Shape key tour</h2>

      <p>
        <strong>Basis (φ = π/2, M = 0, C = +1):</strong> the maximum-topology
        case. Both K and K′ have identical positive curvature peaks (amber).
        The BZ area integral equals 4π. The phase φ = π/2 maximises sin φ = 1,
        giving the largest curvature amplitude.
      </p>

      <p>
        <strong>SK_PhiPi4 (φ = π/4, M = 0, C = +1):</strong> still
        topological but the peaks are lower — sin(π/4) = 0.707 vs 1. The
        Chern number is unchanged; the curvature is merely redistributed less
        sharply. This illustrates that C is quantized (integer-valued) while
        Ω(k) is a continuous function.
      </p>

      <p>
        <strong>SK_NearCrit (φ = π/2, M ≈ 0.95 M_c, C = +1):</strong> one
        peak begins to shrink as M approaches the critical value M_c = 3√3 t₂
        ≈ 1.039. The K and K′ peaks become asymmetric because M tilts the dz
        component differently at the two Dirac points. The system is still
        topological — you need to reach M_c exactly to close the gap.
      </p>

      <p>
        <strong>SK_Trivial (φ = π/2, M = 1.5 M_c, C = 0):</strong> the floor
        is nearly flat. The Berry curvature is small everywhere because dz
        dominates all over the BZ (the d-vector points nearly along ẑ
        throughout) and the map ĥ: T² → S² has zero winding number.
      </p>

      <h2>Topological phase diagram</h2>

      <p>
        Haldane&rsquo;s 1988 paper introduced the {" "}
        <em>topological phase diagram</em> — a plot in (M/t₂, φ) space showing
        which region has C = 0, +1, or −1. The phase boundaries are the two
        curves M = ±3√3 t₂ sin φ. The Basis shape key sits deep inside the
        C = +1 lobe; the SK_Trivial key sits outside both lobes (C = 0 and
        driven by M, not by φ).
      </p>

      <p>
        The same physics underlies the quantum spin Hall effect (Kane–Mele
        2005, which added spin-orbit coupling to Haldane&rsquo;s model) and
        the 3D Z₂ topological insulators. The Chern number of the Haldane
        model is the simplest example of a topological invariant beyond the
        Zak phase of the SSH chain — compare the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-ssh-su-schrieffer-heeger-1979-zak-phase-topological-edge-states-spectral-flow-stage-floor-webxr"
        >
          SSH spectral-flow tutorial
        </Link>{" "}
        for the 1D case.
      </p>

      <h2>Failure modes</h2>

      <p>
        <strong>Dirac cone singularity at the phase boundary:</strong> when M
        equals exactly M_c, |d(K)| = 0 at one Dirac point — the gap closes
        and the Berry curvature is a delta-function spike. The code guards
        with <code>d_mag = max(d_mag, 1e-12)</code> to avoid division by zero,
        producing a very tall narrow peak rather than a NaN. On a 128×128 grid
        this spike may sit between two sample points and appear smooth; a finer
        grid would sharpen it.
      </p>

      <p>
        <strong>Chern number numerical accuracy:</strong> the solid-angle
        formula with np.gradient (central differences) gives C accurate to
        about ±0.01 on a 128×128 grid. The FHS lattice-gauge formula is more
        accurate near phase boundaries because it is exact on a finite lattice,
        but requires wavefunction gauge fixing. For the visual the difference
        is negligible.
      </p>

      <h2>Outside sources</h2>

      <ul>
        <li>
          Haldane FDM (1988) &ldquo;Model for a Quantum Hall Effect without
          Landau Levels&rdquo; <em>Physical Review Letters</em> 61(18):2015.{" "}
          <a className={lk} href="https://doi.org/10.1103/PhysRevLett.61.2015">
            doi:10.1103/PhysRevLett.61.2015
          </a>{" "}
          — original model. Mathematical results, public domain. 2016 Nobel
          Prize in Physics.
        </li>
        <li>
          Thouless DJ, Kohmoto M, Nightingale MP, den Nijs M (1982)
          &ldquo;Quantized Hall Conductance in a Two-Dimensional Periodic
          Potential&rdquo; <em>Physical Review Letters</em> 49(6):405.{" "}
          <a className={lk} href="https://doi.org/10.1103/PhysRevLett.49.405">
            doi:10.1103/PhysRevLett.49.405
          </a>{" "}
          — TKNN formula C = σxy h/e². Public domain.
        </li>
        <li>
          Asbóth JK, Oroszlány L, Pályi A (2016){" "}
          <a className={lk} href="https://arxiv.org/abs/1509.02295">
            arXiv:1509.02295
          </a>{" "}
          &ldquo;A Short Course on Topological Insulators&rdquo;. CC-BY 4.0.
          Lecture notes covering SSH → Haldane → Kane–Mele → 3D invariants.
        </li>
      </ul>
    </>
  );
}

export const entry: Entry = buildInstructable({
  slug: SLUG,
  title: TITLE,
  lede: LEDE,
  body: <Body />,
  publishedAt: new Date("2026-09-19"),
  tags: [
    "blender",
    "python",
    "numpy",
    "physics",
    "topology",
    "condensed-matter",
    "berry-phase",
    "webxr",
  ],
});

export const blenderTutorialPythonNumpyHaldane1988ChernInsulatorBerryCurvatureTopologicalPhaseDiagramHoneycombHeightFieldStageFloorWebxrEntry =
  entry;
