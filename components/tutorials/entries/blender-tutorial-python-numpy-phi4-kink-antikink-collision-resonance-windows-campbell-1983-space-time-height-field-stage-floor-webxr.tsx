import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-phi4-kink-antikink-collision-resonance-" +
  "windows-campbell-1983-space-time-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — φ⁴ Scalar Field Theory: " +
  "∂²φ/∂t² = ∂²φ/∂x² + φ − φ³  V(φ)=¼(1−φ²)² " +
  "Kink φ_K=tanh[γ(x−vt)/√2] γ=1/√(1−v²) " +
  "Non-Integrable KK̄ Collision Bion Capture v<v_c≈0.260 " +
  "Resonance Windows Campbell-Schonfeld-Wingate 1983 " +
  "Leapfrog DT=0.04 CFL=0.43 128×128=16384V 16129Q " +
  "Basis(v=0.10 bion)/SK_TwoBounce(v=0.193 2-bounce)/SK_Critical(v=0.26)/SK_Escape(v=0.40) " +
  "Phi4_Field FLOAT_COLOR Cobalt–Teal–Amber " +
  "Space-Time Height-Field Stage Floor WebXR (Blender 5.1)";

const LEDE =
  "φ⁴ (phi-four) field theory is the textbook example of a spontaneously broken " +
  "discrete symmetry: the potential V(φ) = ¼(1−φ²)² has two degenerate minima " +
  "at φ = ±1, and the kink solution interpolates between them — a topological " +
  "domain wall that cannot be smoothed away without infinite energy. " +
  "When a kink and its mirror image (the antikink) approach at speed v, " +
  "they do not simply pass through each other as KdV solitons do. " +
  "Instead the outcome depends exquisitely on v: below a critical speed v_c ≈ 0.260 " +
  "the pair is usually captured into an oscillating bound state called a bion; " +
  "within narrow resonance windows it bounces exactly n times then escapes; " +
  "above v_c it flies apart in a single pass leaving a radiation splash at the centre. " +
  "This blueprint simulates all four regimes and lays the space-time history flat " +
  "as a Blender stage floor: space runs along the x-axis, time forward " +
  "along the y-axis, and the field value rises as height.";

function Body() {
  return (
    <>
      <p>
        The equation ∂²φ/∂t² = ∂²φ/∂x² + φ − φ³ comes from varying the Lagrangian
        ℒ = ½(∂_μφ)² − V(φ) with V(φ) = ¼(1−φ²)². It is the simplest
        four-dimensional (in field-theoretic language: one space + one time) model
        that is Lorentz-covariant, has a double-well potential, and therefore has
        topological kink solutions. The same equation, with minor rescaling, governs
        the Ising-model domain-wall dynamics in one spatial dimension, structural
        phase transitions in solids, and is a prototypical model for the Higgs
        mechanism of electroweak symmetry breaking.
      </p>

      <h2>The kink solution and topological charge</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Static kink centred at x₀:
  φ_K(x) = tanh[(x − x₀) / √2]

  As x → −∞:  φ_K → −1  (vacuum)
  As x → +∞:  φ_K → +1  (vacuum)
  At x = x₀:  φ_K =  0  (field passes through hill of potential)

Topological (winding) charge:
  Q = ½ [φ(+∞) − φ(−∞)] = ½ [1 − (−1)] = +1  (kink)
  Q = −1 for the antikink   φ_Ā = −tanh[(x − x₀)/√2]

Lorentz-boosted kink at velocity v:
  φ_K(x, t) = tanh[γ(x − x₀ − vt) / √2]
  γ = 1/√(1 − v²)    (Lorentz factor)
  Width contracts:  √2/γ  (Lorentz contraction)

Kink rest mass:  M_K = ∫ T₀₀ dx = 4√2 / 3 ≈ 1.886`}
      </pre>
      <p>
        The key word is <em>topological</em>: the kink cannot decay into the vacuum
        because that would require the field to simultaneously equal +1 everywhere —
        impossible if it starts at −1 on the left and +1 on the right.
        The antikink (Q = −1) has opposite topology. A kink plus antikink has
        Q = 0, so the pair <em>can</em> annihilate — but whether it does
        depends on the dynamics, not just the topology.
      </p>

      <h2>Why φ⁴ is non-integrable (unlike KdV)</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Integrable:     KdV  u_t + 6u u_x + u_xxx = 0
                Soliton collision is ELASTIC: shapes, speeds unchanged.
                Inverse-scattering transform → exact N-soliton solution.
                No radiation emitted.

Non-integrable: φ⁴  φ_tt − φ_xx + φ³ − φ = 0
                Kink-antikink collision is INELASTIC:
                  • radiation is emitted (continuous spectrum)
                  • pair can be captured into a bion (discrete mode)
                  • outcome depends sensitively on initial velocity
                No known exact multi-kink solution for t > 0.

Sine-Gordon:    φ_tt − φ_xx + sin φ = 0  IS integrable (Bäcklund transform)
                φ⁴ is NOT: the Taylor series sin φ ≈ φ − φ³/6 + … is
                integrable; the φ⁴ truncation that drops all higher terms
                destroys integrability.`}
      </pre>

      <h2>Resonance windows and the Peyrard-Campbell mechanism</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Critical velocity:  v_c ≈ 0.2598

v < v_c (generic):  KK̄ captured → bion oscillates at ω_b ≈ √8/3 ≈ 0.943
v = 0.10  (Basis):  deep bion, oscillation visible as standing wave in carpet

Resonance windows (narrow escape bands within the capture region):
  First  two-bounce window:  v ≈ 0.193
    KK̄ collide at t₁ ≈ 10.4,
    temporarily trap, exchange energy with internal mode,
    collide again at t₂ ≈ 18–20,  then escape.

Mechanism (Peyrard & Campbell 1983):
  The kink has an internal vibrational mode at ω_int ≈ √3 ≈ 1.732.
  At first collision, kinetic energy is partially transferred to this mode.
  If the stored energy is returned coherently at the second collision,
  the pair escapes.  Resonance condition:
    ω_int · Δt = n · π  →  discrete window structure.

  Window widths shrink toward v_c following Fibonacci-like scaling,
  generating a self-similar fractal pattern — an early example of
  what Grebogi, Ott & Yorke (1983) formalised as fractal basin boundaries.

v > v_c (SK_Escape v=0.40):
  Collision is too fast for energy to flow into internal mode.
  Single inelastic pass: kinks fly apart; radiation burst remains centred.`}
      </pre>

      <h2>Numerical method: leapfrog on a 1D grid</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Grid:    N_X = 128,  L = 12,  DX = 12/128 ≈ 0.094
         N_T = 128 time snapshots,  T_FINAL = 30

Leapfrog (Störmer-Verlet):
  φⁿ⁺¹ = 2φⁿ − φⁿ⁻¹ + DT²·[φ_xx(φⁿ) + φⁿ − (φⁿ)³]

WHY leapfrog: it is symplectic (area-preserving in phase space) and
time-reversible, so it conserves the energy integral exactly up to
DT²-order errors — critical for long-time bion dynamics.

CFL stability:  DT < DX  →  0.04 < 0.094 ✓  (σ = 0.43)

Bootstrap:  φ⁻¹ = φ⁰ − DT·φ_t⁰ + ½DT²·f(φ⁰)
Boundary:   Dirichlet ghost cells φ[−1] = φ[N] = −1 (vacuum)

Kink resolution: kink width = √2 ≈ 1.414 → 1.414/0.094 ≈ 15 points ✓`}
      </pre>

      <h2>Reading the space-time carpet</h2>
      <p>
        Look at the floor as a map: the front-left and front-right corners each show
        an amber ridge entering the scene — these are the kink and antikink worldlines.
        They converge toward the centre.  In the <strong>Basis</strong> shape key
        (v = 0.10, deep capture), the ridges meet and then the central strip
        oscillates amber-cobalt-amber: the bion breathing.  The oscillation never
        damps because the simulation has no radiation-damping mechanism (the exact
        φ⁴ bion is a semi-classical bound state, weakly stable).
      </p>
      <p>
        In <strong>SK_TwoBounce</strong> (v = 0.193), look for the characteristic
        double-touch: the ridges meet once, pull back, then converge again before
        finally separating.  Between the two collision events there is a narrow amber
        central strip — the energy trapped in the internal mode.  After the second
        collision, outward-going radiation trails appear as faint cobalt-teal ripples.
      </p>
      <p>
        <strong>SK_Escape</strong> (v = 0.40) shows the cleanest version of the
        carpet: two clean ridges enter, cross once at the front, then diverge with
        a residual amber-gold splash in the collision region.  The splash decays
        toward teal as the radiation disperses.
      </p>

      <h2>Cross-references</h2>
      <ul className="list-disc pl-5">
        <li>
          <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-korteweg-de-vries-1895-soliton-collision-pseudospectral-rk4-space-time-height-field-stage-floor-webxr">
            KdV Soliton Collision — the integrable contrast
          </Link>{" "}
          — same space-time floor format; KdV solitons pass through without
          radiation while φ⁴ kinks emit and can be trapped.
        </li>
        <li>
          <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-burgers-equation-1948-cole-hopf-exact-shock-formation-viscous-regularisation-height-field-stage-floor-webxr">
            Burgers Equation (1948) — Cole-Hopf space-time floor
          </Link>{" "}
          — another x-space / y-time carpet; Burgers shocks form by characteristic
          crossing rather than topological collision.
        </li>
        <li>
          <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-dini-surface-pseudosphere-sine-gordon-kink-tractrix-poi-webxr">
            Dini Surface — Sine-Gordon kink as geometry
          </Link>{" "}
          — the sine-Gordon kink solution mapped to a pseudosphere; sine-Gordon IS
          integrable (Bäcklund transform); compare its exact collisions with φ⁴.
        </li>
        <li>
          <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-oregonator-belousov-zhabotinsky-bz-fkn-1972-chemical-spiral-wave-height-field-stage-floor-webxr">
            Oregonator BZ Reaction-Diffusion — propagating chemical fronts
          </Link>{" "}
          — excitable-medium fronts share the notion of a wave that can annihilate
          on collision; the BZ spiral and the φ⁴ kink bion are both
          dissipative-vs-conservative counterparts of the same topological idea.
        </li>
      </ul>

      <h2>Outside sources</h2>
      <ul className="list-disc pl-5">
        <li>
          Campbell DK, Schonfeld JF, Wingate CA (1983){" "}
          <em>Resonance structure in kink-antikink interactions in φ⁴ theory</em>,
          Physica D 9(1-2):1–32.{" "}
          <a className={lk} href="https://doi.org/10.1016/0167-2789(83)90289-0" target="_blank" rel="noreferrer">
            doi:10.1016/0167-2789(83)90289-0
          </a>
          {" "}— the paper that mapped out the resonance windows numerically and
          explained the Peyrard-Campbell mechanism. Related: Peyrard M & Campbell DK
          (1983) same volume, kink interactions in double sine-Gordon equation.
        </li>
        <li>
          Dorey P, Mersh K, Romanczukiewicz T, Sutcliffe P (2011){" "}
          <em>Kink-Antikink Scattering in φ⁴ Theory and One-Dimensional Magnets</em>,{" "}
          <a className={lk} href="https://arxiv.org/abs/1110.2378" target="_blank" rel="noreferrer">
            arXiv:1110.2378
          </a>
          {" "}— open-access update linking φ⁴ kink scattering to magnetic domain-wall
          dynamics; contains a clear review of the resonance-window structure.
          Related: Manton N & Sutcliffe P,{" "}
          <em>Topological Solitons</em>, Cambridge (2004) — canonical monograph.
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
  tags:      ["blender", "python", "numpy", "physics", "pde", "soliton", "webxr"],
  body:      Body,
  blend:     "phi4_kink_floor.blend",
  glb:       "phi4_kink_floor.glb",
  blendPath: "blends/scripting/python-numpy-phi4-kink-antikink-collision-resonance-windows-campbell-1983-space-time-height-field-stage-floor-webxr/",
});
