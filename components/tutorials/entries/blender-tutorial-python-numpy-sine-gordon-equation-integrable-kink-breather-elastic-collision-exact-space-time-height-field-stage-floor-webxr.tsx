import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-sine-gordon-equation-integrable-kink-" +
  "breather-elastic-collision-exact-space-time-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — Sine-Gordon Equation: φ_tt − φ_xx + sin φ = 0 " +
  "Completely Integrable 1+1D PDE Lax Pair AKNS Inverse Scattering 1973 " +
  "Kink φ_K=4arctan[exp(γ(x−vt))] γ=1/√(1−v²) Topological Charge Q=+1 " +
  "Elastic Kink-Antikink Collision Phase Shift Δ=(2/γ)log(2v) " +
  "Stationary Breather ω=0.50 Bound State Mass 16β<2M_kink " +
  "Exact Hirota τ-function 128×128=16384V 16129Q " +
  "Basis(v=0.65)/SK_Breather(ω=0.50)/SK_Collision(v=0.65)/SK_TwoKink(v₁=0.80,v₂=0.30) " +
  "SG_Field FLOAT_COLOR Cobalt–Amber " +
  "Space-Time Height-Field Stage Floor WebXR (Blender 5.1)";

const LEDE =
  "The Sine-Gordon equation φ_tt − φ_xx + sin φ = 0 is the simplest " +
  "relativistic field theory with a periodic potential V(φ) = 1 − cos φ. " +
  "Its complete integrability — proved via the AKNS inverse scattering transform " +
  "(Ablowitz, Kaup, Newell, Segur 1973) — means every multi-soliton solution " +
  "is given by a closed algebraic formula: no numerical stepping required, " +
  "no CFL constraint, no discretisation error. " +
  "Kinks pass through each other with perfect elasticity, leaving only a phase shift " +
  "as the sole evidence of the meeting. " +
  "A breather — an oscillating kink-antikink bound state that cannot exist in φ⁴ — " +
  "survives indefinitely because integrability forbids energy loss to radiation. " +
  "This blueprint evaluates four exact solutions on a 128×128 space-time grid " +
  "and lays them flat as a Blender stage floor: space along x, time along y, " +
  "field value as height. The shape keys let you flip between the four solution regimes " +
  "without re-running any simulation.";

function Body() {
  return (
    <>
      <p>
        The Sine-Gordon equation was first encountered in the theory of surfaces of
        constant negative Gaussian curvature (K = −1) by Bour (1862) and Bäcklund
        (1880), where it appeared as the integrability condition for the angle between
        asymptotic lines on a pseudosphere. Its modern importance as a relativistic
        field theory dates from the 1970s, when the AKNS group showed that it possessed
        a Lax pair and therefore an infinite tower of conserved charges — the defining
        hallmarks of complete integrability.
      </p>

      <h2>The kink and its Lorentz contraction</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Single kink (topological charge Q = +1):
  φ_K(x, t) = 4 arctan[ exp( γ(x − vt − x₀) ) ]    γ = 1/√(1 − v²)

  x → −∞:  φ_K → 0   (vacuum at 0)
  x → +∞:  φ_K → 4π  (vacuum at 4π, equivalent by periodicity)
  At x = x₀ + vt:  φ_K = 2π  (centre of kink)

  Width ∝ 1/γ — Lorentz-contracted at speed v.
  Rest mass:  M_K = 8   (8 units of ℏc/ξ where ξ is the healing length)

Antikink (Q = −1):
  φ_Ā(x, t) = −4 arctan[ exp( γ(x − vt − x₀) ) ]`}
      </pre>
      <p>
        The kink solution interpolates between two adjacent minima of V(φ) = 1 − cos φ.
        The topological charge Q = (1/4π)[φ(+∞) − φ(−∞)] = +1 counts how many times
        the field winds around the internal circle. Because Q is a topological
        invariant — unchanged by any smooth deformation — a single kink cannot decay
        or disappear unless it meets an antikink (Q = −1) to give Q = 0.
      </p>

      <h2>The breather: a bound state unique to Sine-Gordon</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Stationary breather (ω ∈ (0, 1)):
  φ_B(x, t) = 4 arctan[ (β/ω) sin(ωt) / cosh(βx) ]    β = √(1 − ω²)

  Oscillation frequency:  ω
  Spatial width:          ∝ 1/β = 1/√(1−ω²)
  Breather mass:          M_B = 16β = 16√(1−ω²)

Binding:  M_B < 2 M_K = 16  for all ω ∈ (0, 1)
  → the breather IS a genuine bound state (not a resonance).

Limit ω → 0:  β → 1,  two well-separated kink and antikink.
Limit ω → 1:  β → 0,  small-amplitude sine wave (phonon, no topology).

ω = 0.50 chosen here:  β = √3/2 ≈ 0.866,  M_B ≈ 13.9 (vs 2×8 = 16 for free pair).`}
      </pre>
      <p>
        The breather exists because Sine-Gordon integrability forbids energy loss
        to radiation during a kink-antikink approach. In φ⁴ theory — which is
        non-integrable — the equivalent bound state (the bion) slowly radiates
        away its energy and is therefore only a quasi-stable resonance.
        The Sine-Gordon breather is exactly stable: it oscillates forever without
        any energy drain.
      </p>

      <h2>Elastic collision and phase shift</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Kink-antikink exact two-soliton:
  φ(x, t) = 4 arctan[ v sinh(γx) / cosh(γvt) ]

  t → −∞:  kink at  x = +|v|t  (approaching from right)
            antikink at x = −|v|t  (approaching from left)

  t → +∞:  kink at  x = +|v|t − Δ  (emerging on right, shifted inward)
            antikink at x = −|v|t + Δ  (emerging on left, shifted inward)

Phase shift:  Δ = (2/γ) log(2v)  (only trace of the interaction)

Elastic collision signature:
  • Speeds unchanged before and after.
  • Shapes unchanged (no radiation emitted).
  • The ONLY effect is the phase shift Δ — the solitons appear to
    have jumped past each other, then stepped back by Δ each.

Compare with φ⁴:  inelastic, radiation emitted, outcome v-sensitive.`}
      </pre>

      <h2>Two-kink co-propagation</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Two co-propagating kinks at speeds v₁ > v₂  (superposition):
  φ(x, t) ≈ φ_K(x, t; v₁, x₀₁) + φ_K(x, t; v₂, x₀₂) − 4π

  The −4π offset corrects the double winding (each kink adds 4π).

  v₁ = 0.80 (fast kink):   starts at x₀₁ = −7
  v₂ = 0.30 (slow kink):  starts at x₀₂ = +6

  As t → T_MAX = 8: fast kink overtakes slow kink.
  After elastic interaction: each emerges with original speed, shifted by Δ.

Exact two-kink via Bäcklund composition differs from the superposition
above by a phase shift that vanishes exponentially away from the
interaction region; superposition is exact in the asymptotic regions.`}
      </pre>

      <h2>Why exact rather than numerical?</h2>
      <p>
        Because the exact solutions exist and are algebraic. The Hirota bilinear
        method (Hirota 1971) writes every N-soliton solution as a ratio of
        determinants — the τ-function — giving a closed formula for arbitrarily
        many interacting solitons. Compare with φ⁴, which{" "}
        <em>must</em> use a time-stepper because non-integrability means no
        closed-form multi-kink solution exists for t {'>'} 0. Using exact solutions here:
      </p>
      <ul className="list-disc pl-5">
        <li>Demonstrates integrability concretely: the elastic collision is mathematically exact, not approximate.</li>
        <li>Avoids discretisation error and the CFL stability constraint on DT/DX.</li>
        <li>Lets us sample the full space-time grid at any resolution with no extra cost.</li>
        <li>Shows that the phase shift Δ = (2/γ)log(2v) is the literal, exact output — not an artefact of finite grid size.</li>
      </ul>

      <h2>Reading the space-time floor</h2>
      <p>
        The floor is a map: x (space) runs left-to-right, t (time) runs
        front-to-back, and φ/(4π) ∈ [0, 1] is encoded as both height and colour
        (cobalt at 0, amber at 1). The vacuum φ = 0 is the cobalt floor; the
        vacuum φ = 4π is the amber plateau.
      </p>
      <p>
        In the <strong>Basis</strong> shape key (single kink, v = 0.65), look for a
        diagonal ridge sweeping from lower-left to upper-right. Its slope encodes the
        kink velocity: steeper ridge = faster kink. The Lorentz-contracted kink width
        (≈ 1/γ ≈ 0.76 world-space units at v = 0.65) is visible as the sharpness of
        the ridge edge.
      </p>
      <p>
        <strong>SK_Breather</strong> (ω = 0.50) shows a symmetric butterfly: a waist-
        shaped dip in the centre of the floor oscillating in t, flanked by cobalt wings.
        The oscillation period T = 2π/ω ≈ 12.6 in simulation time spans roughly 80%
        of the displayed t-range. The spatial width 1/β ≈ 1.15 is visible as the
        narrow extent of the central structure.
      </p>
      <p>
        <strong>SK_Collision</strong> (kink-antikink, v = 0.65) produces a clean X
        pattern: two incoming ridges, a bright amber flash at the origin (the moment of
        closest approach), then two outgoing ridges offset inward by the phase shift Δ.
        The shift Δ = (2/1.316)log(2×0.65) ≈ 0.37 is small but visible as the slight
        mismatch between the incoming and outgoing ridge angles.
      </p>
      <p>
        <strong>SK_TwoKink</strong> (v₁ = 0.80, v₂ = 0.30) shows two parallel ridges
        at different slopes. The faster kink (shallower ridge, higher v) enters from
        the back-left and overtakes the slower kink (steeper ridge). Near the
        interaction region the ridges briefly merge, then separate again — each
        continuing at its original slope but with a spatial offset.
      </p>

      <h2>Cross-references</h2>
      <ul className="list-disc pl-5">
        <li>
          <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-phi4-kink-antikink-collision-resonance-windows-campbell-1983-space-time-height-field-stage-floor-webxr">
            φ⁴ Kink-Antikink Collision — the non-integrable contrast
          </Link>{" "}
          — same stage-floor format, same v = 0.65 kink velocity; φ⁴ collisions
          are inelastic (radiation emitted, bion capture, resonance windows) while
          Sine-Gordon collisions are exactly elastic. Side-by-side comparison makes
          integrability visible.
        </li>
        <li>
          <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-korteweg-de-vries-1895-soliton-collision-pseudospectral-rk4-space-time-height-field-stage-floor-webxr">
            KdV Soliton Collision — pseudospectral RK4 space-time floor
          </Link>{" "}
          — another completely integrable PDE on the same floor format; KdV solitons
          also collide elastically but are not topological — they have no analogue of
          the Sine-Gordon breather.
        </li>
        <li>
          <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-dini-surface-pseudosphere-sine-gordon-kink-tractrix-poi-webxr">
            Dini Surface — Sine-Gordon kink as constant-K geometry
          </Link>{" "}
          — the same Sine-Gordon equation arises as the integrability condition for
          K = −1 surfaces; the kink solution maps to the pseudosphere/tractrix. This
          entry shows the PDE itself; that entry shows the geometric interpretation.
        </li>
        <li>
          <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-kadomtsev-petviashvili-kp-ii-1970-exact-web-soliton-hirota-tau-stage-floor-webxr">
            KP-II — exact web soliton via Hirota τ-function
          </Link>{" "}
          — both entries use the Hirota bilinear / τ-function framework for exact
          multi-soliton solutions; KP-II extends KdV to 2+1 dimensions while
          Sine-Gordon lives in 1+1D but has the additional breather degree of freedom.
        </li>
      </ul>

      <h2>Outside sources</h2>
      <ul className="list-disc pl-5">
        <li>
          Scott AC, Chu FYF, McLaughlin DW (1973){" "}
          <em>The soliton: A new concept in applied science</em>,
          Proc. IEEE 61(10):1443–1483.{" "}
          <a className={lk} href="https://doi.org/10.1109/PROC.1973.9296" target="_blank" rel="noreferrer">
            doi:10.1109/PROC.1973.9296
          </a>
          {" "}— authoritative survey that introduced soliton physics to the engineering
          community; reviews the sine-Gordon kink, breather, and two-soliton solutions
          with physical applications in superconducting Josephson junctions and DNA
          base-pair dynamics.
        </li>
        <li>
          Ablowitz MJ, Kaup DJ, Newell AC, Segur H (1973){" "}
          <em>Method for Solving the Sine-Gordon Equation</em>,
          Physical Review Letters 30(25):1262.{" "}
          <a className={lk} href="https://doi.org/10.1103/PhysRevLett.30.1262" target="_blank" rel="noreferrer">
            doi:10.1103/PhysRevLett.30.1262
          </a>
          {" "}— the AKNS paper establishing the Lax pair for Sine-Gordon and deriving
          all exact N-soliton solutions via inverse scattering; the formulae used in
          this blueprint follow directly from this work.
        </li>
      </ul>
    </>
  );
}

export const entry: Entry = buildInstructable({
  slug:      SLUG,
  title:     TITLE,
  lede:      LEDE,
  date:      "2026-09-12",
  topic:     "blender",
  tags:      ["blender", "python", "numpy", "physics", "pde", "soliton", "integrable", "webxr"],
  body:      Body,
  blend:     "sine_gordon_floor.blend",
  glb:       "sine_gordon_floor.glb",
  blendPath: "blends/scripting/python-numpy-sine-gordon-equation-integrable-kink-breather-elastic-collision-exact-space-time-height-field-stage-floor-webxr/",
});
