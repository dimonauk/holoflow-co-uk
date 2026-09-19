import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-kane-mele-2005-quantum-spin-hall-z2-topological-insulator-spin-hall-curvature-honeycomb-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — Kane-Mele Model 2005: Quantum Spin Hall Effect, Z₂ Topological Insulator, Spin-Hall Berry Curvature over the Hexagonal Brillouin Zone, Honeycomb Height-Field Stage Floor for WebXR (Blender 5.1)";

const LEDE =
  "Add spin-orbit coupling to graphene and both K and K′ Dirac points bloom into equal amber peaks on the Berry-curvature floor — the visual signature that topology here is protected by time-reversal, not broken by it. Kane and Mele's 2005 paper showed that these two Haldane-insulator valleys, with opposite Berry curvature signs in each spin channel, cancel in charge but reinforce in spin, giving a quantised spin Hall conductance σˢₓᵧ = e/4π and a Z₂ topological invariant ν ∈ {0, 1}. Drive the on-site mass M past the critical value 3√3 λ_SO and the floor goes flat — topology collapses — but add Rashba coupling alone and the two amber peaks survive intact.";

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
        carries a Z invariant in 1D. The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-haldane-1988-chern-insulator-berry-curvature-topological-phase-diagram-honeycomb-height-field-stage-floor-webxr"
        >
          Haldane model
        </Link>{" "}
        carries a Chern number in 2D, but only by breaking
        time-reversal with a staggered magnetic flux. Kane and Mele (2005)
        asked: what if the electrons have spin? The SOC already provides a
        flux-like phase shift — and it preserves time-reversal. The result is
        the Quantum Spin Hall insulator: topologically non-trivial, yet
        magnetically inert.
      </p>

      <h2>Two Haldane layers</h2>

      <p>
        The Kane-Mele Hamiltonian is two decoupled Haldane models (when
        Rashba coupling λ_R = 0):
      </p>

      <pre>{`
H = h_↑(k) ⊕ h_↓(k)

h_↑(k): Haldane with φ = +π/2,  t₂ = λ_SO,  C_↑ = +1
h_↓(k): Haldane with φ = −π/2,  t₂ = λ_SO,  C_↓ = −1
         (time-reversal partner: h_↓(k) = σ_y h_↑*(−k) σ_y)

Charge Chern number:    C = C_↑ + C_↓ = 0   (no Hall conductance)
Spin Chern number:      C_s = C_↑ − C_↓ = 2
Z₂ invariant:           ν = C_s/2 mod 2 = 1   → topological insulator

Spin Hall conductance:  σˢₓᵧ = e/4π   (quantised when λ_R = 0)
`}</pre>

      <p>
        The d-vector of the spin-up 2×2 block (in the notation of the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-haldane-1988-chern-insulator-berry-curvature-topological-phase-diagram-honeycomb-height-field-stage-floor-webxr"
        >
          Haldane blueprint
        </Link>
        ):
      </p>

      <pre>{`
dₓ + i·dᵧ = t₁ Σⱼ exp(ik·δⱼ)              [NN structure factor f(k)]
dz         = M − 2λ_SO Σⱼ sin(k·bⱼ)       [mass + SOC imaginary NNN]
d₀         = 0                               [cos(π/2) = 0 → no energy offset]

Phase boundary:  |M| < 3√3 λ_SO   → topological (ν = 1)
                 |M| > 3√3 λ_SO   → trivial (ν = 0)
`}</pre>

      <h2>Spin Berry curvature — solid-angle formula</h2>

      <p>
        The spin Berry curvature density is twice the spin-up curvature:
      </p>

      <pre>{`
Ω_↑(k) = −½ ĥ↑ · (∂_kx ĥ↑ × ∂_ky ĥ↑)   ĥ↑ = d/|d|

Ω_s(k) = Ω_↑(k) − Ω_↓(k) = 2 Ω_↑(k)
         (by TRS: Ω_↓(k) = −Ω_↑(−k) = −Ω_↑(k) at inversion-symmetric points)

Spin Hall conductance:  σˢₓᵧ = (e/4π) ∫_BZ Ω_s d²k / (2π)² = e/4π
`}</pre>

      <p>
        This differs fundamentally from the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-tight-binding-2d-square-lattice-dispersion-fermi-surface-van-hove-singularity-stage-floor-webxr"
        >
          ordinary 2D band dispersion
        </Link>{" "}
        (which has no Berry curvature when spin is ignored): the
        topology here lives in the space of spinors, not in the energy landscape.
      </p>

      <h2>Visual difference from Haldane</h2>

      <p>
        In the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-haldane-1988-chern-insulator-berry-curvature-topological-phase-diagram-honeycomb-height-field-stage-floor-webxr"
        >
          Haldane tutorial
        </Link>{" "}
        with M = 0 and φ = π/2 the two amber peaks at K and K′ are equal
        (inversion symmetry is unbroken), integrating to 2π (C = +1). In the
        Kane-Mele floor the peaks look identical — but they represent <em>spin</em>{" "}
        Hall curvature integrating to 4π (C_s = 2), and time-reversal forces
        the equality even when M ≠ 0. Introduce an on-site mass: in Haldane
        one peak grows and the other shrinks; in Kane-Mele the same happens
        in the spin-up channel only, and the Z₂ invariant flips when the
        spin-up gap closes at one valley.
      </p>

      <h2>Rashba coupling</h2>

      <p>
        Rashba SOC mixes spin-up and spin-down:
      </p>

      <pre>{`
H_R = iλ_R Σ_{⟨ij⟩} c†_i (ê_z × δ̂_ij)·σ c_j

Effect on topology:
  λ_R ≠ 0  →  Sz no longer a good quantum number
  σˢₓᵧ loses quantisation but Z₂ invariant ν survives
  Critical Rashba: λ_R^c ≈ 2λ_SO (above this the full gap closes → ν = 0)
`}</pre>

      <p>
        The survival of topology without Sz conservation is the deepest
        statement of the Z₂ classification: the invariant is protected by
        time-reversal alone (T² = −1 for spin-1/2), not by any continuous
        symmetry.
      </p>

      <h2>Blueprint sketch</h2>

      <pre>{`
# 1. BZ grid via reduced coordinates (same as Haldane)
KX, KY = s1·B1 + s2·B2   (N=128, s∈[0,1))

# 2. Spin-up d-vector
dx, dy = Re(f_k), Im(f_k)   where f_k = t₁ Σ exp(ik·δⱼ)
dz     = M − 2λ_SO Σ sin(k·bⱼ)

# 3. Solid-angle Berry curvature
ĥ = (dx,dy,dz)/|d|
Ω_↑(k) = −½ ĥ·(∂_kx ĥ × ∂_ky ĥ)
Ω_s    = 2·Ω_↑

# 4. Height field + cobalt–amber colour → FLOAT_COLOR KM_SpinBC
# 5. Shape keys: Basis / SK_StrongSOC / SK_NearCrit / SK_Trivial
# 6. GLB export: Draco-6, WebP, +Y-up, morph+colors
`}</pre>

      <h2>Shape keys</h2>

      <p>
        Each key sweeps one parameter of the phase diagram:
      </p>

      <ul>
        <li>
          <strong>Basis</strong> — λ_SO = 0.20, M = 0: two equal amber peaks at K and K′, ν = 1.
        </li>
        <li>
          <strong>SK_StrongSOC</strong> — λ_SO = 0.40, M = 0: stronger confinement, narrower peaks.
        </li>
        <li>
          <strong>SK_NearCrit</strong> — λ_SO = 0.20, M = 0.95 M_c: K′ peak begins to collapse (gap closing imminently).
        </li>
        <li>
          <strong>SK_Trivial</strong> — λ_SO = 0.20, M = 1.50 M_c: ν = 0, flat cobalt floor.
        </li>
      </ul>

      <h2>Helical edge states (the experimentally observed signature)</h2>

      <p>
        The bulk-boundary correspondence of the Z₂ invariant guarantees two
        helical edge modes on any boundary between the topological (ν = 1) and
        trivial (ν = 0) regions: one right-mover with spin ↑, one left-mover
        with spin ↓. Back-scattering between them requires a spin-flip, which
        time-reversal forbids (Kramers&rsquo; theorem: T|k,↑⟩ = |−k,↓⟩). These
        helical channels were first observed in HgTe/CdTe quantum wells by
        König et al. (2007 Science 318:766), confirming Kane-Mele&rsquo;s prediction.
      </p>

      <h2>Troubleshooting</h2>

      <ul>
        <li>
          <strong>Flat floor at M = 0</strong> — check that λ_SO &gt; 0; the
          spin-up and spin-down sectors are degenerate at M = 0 so the total
          charge Berry curvature is zero, but the spin curvature Ω_s = 2Ω_↑
          is non-zero. Confirm the d-vector magnitude is &gt; 1 × 10⁻¹² everywhere.
        </li>
        <li>
          <strong>Chern number wrong</strong> — integrate Ω_↑ over the BZ using
          numpy.sum and compare to 2π. Off by a sign? Check the winding convention
          of the NNN vectors (must be CCW for ν_ij = +1).
        </li>
        <li>
          <strong>Shape key identical to Basis at SK_StrongSOC</strong> — confirm
          λ_SO was changed; d₀ = 0 for φ = π/2 so the only λ_SO effect is through dz.
        </li>
      </ul>
    </>
  );
}

export const blenderTutorialPythonNumpyKaneMele2005QuantumSpinHallZ2TopologicalInsulatorSpinHallCurvatureHoneycombHeightFieldStageFloorWebxrEntry: Entry =
  buildInstructable({
    slug: SLUG,
    title: TITLE,
    lede: LEDE,
    date: "2026-09-19",
    topics: ["blender", "python", "numpy", "topology", "physics", "webxr"],
    body: Body,
    blenderVersion: "5.1",
    libraryPath:
      "blends/scripting/python-numpy-kane-mele-2005-quantum-spin-hall-z2-topological-insulator-spin-hall-curvature-honeycomb-height-field-stage-floor-webxr",
    externalSources: [
      {
        title:
          "Kane CL, Mele EJ 2005 — Z₂ Topological Order and the Quantum Spin Hall Effect",
        url: "https://doi.org/10.1103/PhysRevLett.95.226801",
        licence: "PD",
        author: "Kane & Mele",
        relatedProjects: ["APS Physics"],
      },
      {
        title:
          "Asbóth, Oroszlány, Pályi 2016 — A Short Course on Topological Insulators (arXiv:1509.02295)",
        url: "https://arxiv.org/abs/1509.02295",
        licence: "CC-BY-4.0",
        author: "Asbóth JK, Oroszlány L, Pályi A",
        relatedProjects: ["https://github.com/topocm/topocm_content (CC0)"],
      },
    ],
  });
