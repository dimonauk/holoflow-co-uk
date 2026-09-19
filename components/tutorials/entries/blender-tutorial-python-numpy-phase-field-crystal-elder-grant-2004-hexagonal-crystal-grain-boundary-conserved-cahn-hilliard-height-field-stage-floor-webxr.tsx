import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-phase-field-crystal-elder-grant-2004-hexagonal-crystal-grain-boundary-conserved-cahn-hilliard-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — Phase-Field Crystal (PFC) Elder & Grant 2004 F[ψ]=(ψ/2)[r+(1+∇²)²]ψ+ψ⁴/4 Conserved Model B ∂ψ/∂t=∇²[δF/δψ] Λ(k)=−k²(r+(1−k²)²) ETD1 Spectral Cox–Matthews 2002 Hexagonal Crystal Grain Boundary Lamellar Stripe Liquid-Crystal Coexistence 128×128=16384V 16129Q Basis(r=−0.25 hexagonal)/SK_GrainBnd(polycrystalline boundary)/SK_Stripe(r=−0.07 lamellar)/SK_Coexist(partial ordering) PFC_Density FLOAT_COLOR Cobalt–Amber Crystal Relief Height-Field Stage Floor WebXR (Blender 5.1)";

const LEDE =
  "K.R. Elder and Martin Grant introduced the Phase-Field Crystal (PFC) model in 2002–2004 as a bridge between classical density-functional theory of freezing and the slow diffusive dynamics accessible to phase-field simulations. A single free energy F[ψ] = ∫{(ψ/2)[r+(1+∇²)²]ψ + ψ⁴/4} dr selects a preferred wavenumber k₀ = 1 whose triangular-lattice ground state is the 2D hexagonal crystal. The conserved (Model B) dynamics ∂ψ/∂t = ∇²[δF/δψ] preserve total density throughout, allowing the simulation to capture crystal nucleation, grain growth, grain boundaries and phase coexistence from a unified field description. This blueprint runs four ETD1 Fourier-spectral PFC simulations in NumPy inside Blender 5.1, baking hexagonal crystal, polycrystalline grain boundary, lamellar stripe, and liquid-crystal coexistence states into shape keys on a 128 × 128 quad-grid stage floor exported as a Draco-compressed GLB for WebXR.";

function Body() {
  return (
    <>
      <p>
        The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-cahn-hilliard-phase-field-spinodal-decomposition-ostwald-ripening-stage-floor-webxr"
        >
          Cahn–Hilliard equation
        </Link>{" "}
        describes conserved phase separation without any preferred length
        scale — a diffuse interface grows and coarsens indefinitely. The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-swift-hohenberg-1977-stripe-hexagon-labyrinth-etd1-spectral-height-field-stage-floor-webxr"
        >
          Swift–Hohenberg equation
        </Link>{" "}
        introduces the preferred wavenumber through (1+∇²)² but uses
        non-conserved (Model A) dynamics, so the spatial average of the
        order parameter can drift. The Phase-Field Crystal combines both
        ideas: the (1+∇²)² free-energy term locks the crystal to k₀ = 1,
        while ∇² in the dynamics enforces strict conservation of total
        density ψ̄.
      </p>

      <h2>Free energy and natural length scale</h2>

      <p>
        The PFC free energy in dimensionless units (Elder & Grant 2004,
        Eq. 1):
      </p>

      <pre>{`F[ψ] = ∫ { (ψ/2)[r + (1+∇²)²]ψ + ψ⁴/4 } dr`}</pre>

      <p>
        The operator (1+∇²)² has a unique zero at k₀ = 1 in Fourier space:
        (1−k₀²)² = 0. Every other wavenumber pays an elastic energy cost.
        The ground state therefore has density modulations exclusively at
        |k| = k₀ = 1, which in 2D selects the three wavevectors of the
        triangular lattice — the densest periodic packing of circles — giving
        a lattice parameter a₀ = 4π/√3 ≈ 7.26 (in units where k₀ = 1).
      </p>

      <p>
        The scalar r is the reduced temperature. For r {'< 0'} the crystal
        phase has lower free energy than the homogeneous liquid; for r {'>'} 0
        the liquid is globally stable. The nonlinear ψ⁴/4 term saturates the
        crystal amplitude — without it the density would grow without bound.
      </p>

      <h2>Conserved Model B dynamics</h2>

      <p>
        The chemical potential is μ = δF/δψ = [r+(1+∇²)²]ψ + ψ³. The
        dynamics follow the continuity equation:
      </p>

      <pre>{`∂ψ/∂t = ∇²μ = ∇²{ [r + (1+∇²)²]ψ + ψ³ }`}</pre>

      <p>
        In Fourier space (k² = k_x² + k_y², (1+∇²)² → (1−k²)²):
      </p>

      <pre>{`∂ψ̂/∂t = Λ(k)·ψ̂ − k²·FT(ψ³)
Λ(k) = −k²·(r + (1−k²)²)`}</pre>

      <p>
        Λ(k₀=1) = −r {'>'} 0 for r {'< 0'}: the crystal modes grow. Because the
        ∇² prefactor makes the k=0 coefficient exactly zero, the mean density
        ψ̂(k=0) is invariant — a stronger conservation guarantee than an
        approximate constraint.
      </p>

      <h2>ETD1 integrator — why not simple Euler?</h2>

      <p>
        The fastest-growing mode (k=k₀) has linear growth rate |r|. A
        forward-Euler step requires dt {'<'} 2/|r| for stability — workable, but
        the high-k modes where Λ(k) is large and negative (strong damping)
        impose a far tighter restriction: dt {'<'} 2/(k⁴_max · 1) ≈ 2/(64π)⁴ on
        a 128-point grid — practically zero. The ETD1 scheme (Cox & Matthews
        2002) sidesteps this entirely:
      </p>

      <pre>{`E_k  = exp(Λ(k)·dt)                         # exact linear propagator
φ₁_k = expm1(Λ(k)·dt) / (Λ(k)·dt)          # Taylor-safe at k=0
ψ̂ⁿ⁺¹ = E_k · ψ̂ⁿ  +  φ₁_k · dt · (−k²) · FT(ψ³ⁿ)`}</pre>

      <p>
        The linear operator is integrated exactly regardless of step size.
        The nonlinear ψ³ term is treated explicitly (first-order), which
        limits stability for very large dt — in practice dt = 0.5 is
        sufficient for all four simulations. Compare with the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-allen-cahn-phase-field-mean-curvature-motion-allen-cahn-1979-stage-floor-webxr"
        >
          Allen–Cahn ETD1 tutorial
        </Link>{" "}
        which uses the same φ₁ stabilisation for a non-conserved field.
      </p>

      <h2>Phase diagram and the four shape keys</h2>

      <p>
        <strong>Basis (r=−0.25, ψ̄=−0.50).</strong> Deep inside the crystal
        phase. After 800 ETD1 steps (t = 400 dimensionless time units) the
        field shows a nearly perfect triangular lattice with hexagonal
        Wigner–Seitz cells. Cobalt valleys between atoms graduate to amber
        density peaks.
      </p>

      <p>
        <strong>SK_GrainBnd (r=−0.25, ψ̄=−0.50).</strong> The domain is split
        into left and right halves with different random-noise seeds before
        the dynamics begin. Each half nucleates and crystallises
        independently, arriving at a different lattice orientation. Where the
        two crystal grains meet, a grain boundary forms — a line of defects
        (dislocations and stacking faults) that costs extra elastic energy.
        Grain boundaries are central to materials science: they control
        mechanical strength, electrical conductivity, and corrosion in
        polycrystalline metals.
      </p>

      <p>
        <strong>SK_Stripe (r=−0.07, ψ̄=−0.25).</strong> Shallower quench
        and lower mean density push the system into the lamellar phase: only
        one Fourier mode grows instead of three, giving parallel stripes
        rather than a triangular lattice. The lamellar-to-hexagonal boundary
        in the PFC phase diagram is analogous to the nematic-to-smectic
        transition in liquid crystals.
      </p>

      <p>
        <strong>SK_Coexist (r=−0.12, ψ̄=−0.38).</strong> Only 300 steps —
        the system has not finished ordering. Crystal nuclei (regular bumps)
        float in a sea of still-disordered liquid (smooth regions). This
        resembles the snapshot immediately after a metal is quenched below
        its melting point but before the grains have grown to fill the
        volume.
      </p>

      <h2>Relation to other studio tutorials</h2>

      <p>
        The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-ising-model-2d-metropolis-monte-carlo-onsager-exact-tc-ferromagnetic-domains-height-field-stage-floor-webxr"
        >
          2D Ising model
        </Link>{" "}
        shows discrete-spin ordering; the PFC gives the continuous-field
        analogue where the periodic crystal structure itself is the order
        parameter rather than a single scalar magnetisation.
      </p>

      <p>
        The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-gray-scott-1984-pearson-1993-activator-depletion-turing-spot-worm-hole-height-field-stage-floor-webxr"
        >
          Gray–Scott reaction-diffusion system
        </Link>{" "}
        also produces hexagonal spot patterns via Turing instability — but
        the spots are not a true crystal because the interspot spacing varies
        and there is no restoring force selecting a single k₀. The PFC
        crystal is energetically locked.
      </p>

      <h2>Blueprint parameters</h2>

      <pre>{`N         = 128     # grid side — 128² = 16 384 vertices
DX        = 1.0     # spatial step (k₀ = 1 in these units)
DT        = 0.50    # ETD1 time step
Z_SCALE   = 0.45    # metres — vertical amplitude of crystal relief

R_BASIS   = -0.25   # reduced temperature — deep crystal phase
PSI_BASIS = -0.50   # conserved mean density
T_BASIS   = 800     # ETD1 steps → t = 400 time units

R_STRIPE  = -0.07   # shallower quench → lamellar stripe
PSI_STRIPE= -0.25   # lower density → stripe (not hexagonal)
T_STRIPE  = 800

R_COEX    = -0.12   # partial quench
PSI_COEX  = -0.38   # intermediate density → coexistence
T_COEX    = 300     # stopped early — nuclei still forming`}</pre>

      <h2>Outside sources</h2>

      <p>
        The PFC free energy derives from classical density-functional theory
        (Ramakrishnan & Yussouff 1979); Elder & Grant&apos;s 2002 Physical
        Review Letters paper (
        <a
          className={lk}
          href="https://link.aps.org/doi/10.1103/PhysRevLett.88.245701"
          target="_blank"
          rel="noopener noreferrer"
        >
          doi:10.1103/PhysRevLett.88.245701
        </a>
        ) introduced the simplest PFC free energy and showed it reproduces
        elastic and plastic deformation of crystals. The 2004 Physical Review
        E paper (
        <a
          className={lk}
          href="https://link.aps.org/doi/10.1103/PhysRevE.70.051605"
          target="_blank"
          rel="noopener noreferrer"
        >
          doi:10.1103/PhysRevE.70.051605
        </a>
        ) extended it to nonequilibrium processing. The ETD1 integrator is
        from Cox & Matthews 2002 J. Comput. Phys. 176:430–455 (
        <a
          className={lk}
          href="https://doi.org/10.1006/jcph.2002.6995"
          target="_blank"
          rel="noopener noreferrer"
        >
          doi:10.1006/jcph.2002.6995
        </a>
        ). NumPy FFT routines (BSD-3-Clause,{" "}
        <a
          className={lk}
          href="https://numpy.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          numpy.org
        </a>
        ) handle all spectral operations; sibling project SciPy (
        <a
          className={lk}
          href="https://scipy.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          scipy.org
        </a>
        , BSD-3-Clause) provides related sparse-matrix and signal tools used
        in other studio blueprints.
      </p>
    </>
  );
}

export const entry: Entry = buildInstructable({
  slug: SLUG,
  title: TITLE,
  lede: LEDE,
  date: "2026-09-19",
  topics: ["scripting", "physics", "phase-field", "crystal", "numpy"],
  body: Body,
  blueprintPath:
    "public/library/blends/scripting/python-numpy-phase-field-crystal-elder-grant-2004-hexagonal-crystal-grain-boundary-conserved-cahn-hilliard-height-field-stage-floor-webxr/blueprint.py",
});
