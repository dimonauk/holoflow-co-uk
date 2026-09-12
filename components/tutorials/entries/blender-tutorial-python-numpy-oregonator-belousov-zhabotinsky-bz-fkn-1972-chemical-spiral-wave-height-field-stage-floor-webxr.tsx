import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-oregonator-belousov-zhabotinsky-bz-fkn-1972-" +
  "chemical-spiral-wave-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — Oregonator BZ Reaction-Diffusion " +
  "Field-Körös-Noyes 1972 · Tyson-Fife 1980: " +
  "ε∂u/∂t = u(1−u) − f·v·(u−q)/(u+q) + Du∇²u  ∂v/∂t = u−v " +
  "ε=0.04 f=1.4 q=0.002 Du=1.0 Forward Euler dt=0.002 Stability dt<2ε/(max|λ|) " +
  "128×128=16384V 16129Q " +
  "Basis(broken-wave t=40)/SK_Fast(ε=0.02)/SK_Rings(pacemaker)/SK_Meander(f=1.6 turbulent) " +
  "BZ_Conc FLOAT_COLOR Cobalt–Amber " +
  "Belousov-Zhabotinsky Chemical Oscillator Self-Organising Spiral Waves " +
  "Height-Field Stage Floor WebXR (Blender 5.1)";

const LEDE =
  "In 1951 Boris Belousov noticed that a flask of bromate, cerium, and malonic acid " +
  "kept changing colour — blue to colourless and back, rhythmically, for minutes. " +
  "Colleagues thought he was mistaken; a chemical reaction was supposed to reach " +
  "equilibrium monotonically. Belousov was right, and in 1961 Zhabotinsky showed " +
  "that the same chemistry in a thin layer spontaneously organises into rotating " +
  "blue-and-gold spiral waves visible to the naked eye. " +
  "This blueprint integrates the Oregonator kinetics (Field-Körös-Noyes 1972, " +
  "reduced to two variables by Tyson-Fife 1980) on a periodic 128×128 grid " +
  "and maps activator concentration to height and colour — " +
  "a chemical oscillator as a WebXR stage floor.";

function Body() {
  return (
    <>
      <p>
        The BZ reaction is not unusual chemistry gone wrong; it is a dissipative
        structure — a far-from-equilibrium steady state that continuously consumes
        reactants to maintain spatial organisation. Prigogine called these{" "}
        <em>dissipative structures</em> in 1969 and received a Nobel Prize for the
        concept in 1977. The spirals you see in a Petri dish are a macroscopic
        signature of molecular autocatalysis: HBrO₂ catalyses its own production,
        which makes the local concentration shoot up, then the inhibitory Ce⁴⁺
        accumulates, switches the reaction off, and the cycle repeats.
      </p>

      <h2>The Oregonator equations</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Two-variable Tyson-Fife (1980) dimensionless reduction:

  ε ∂u/∂t = u(1 − u) − f·v·(u − q)/(u + q)  +  Du ∇²u   ... [fast u]
       ∂v/∂t = u − v                                         ... [slow v]

  u ∈ [0,1]  HBrO₂ activator  (autocatalytic 'spark')
  v ∈ [0,1]  Ce⁴⁺  inhibitor  ('brake')
  ε = 0.04   timescale ratio   (ε ≪ 1 → excitable / oscillatory)
  f = 1.4    stoichiometric factor
  q = 0.002  rate constant ratio  (sets front sharpness)
  Du = 1.0   activator diffusivity  (v immobile in gel)

Limit cycle resting state (v-nullcline v = u intersects u-nullcline):
  u² + u(f − 1 + q) − q(f + 1) = 0
  u* ≈ 0.012,  v* ≈ 0.012`}
      </pre>
      <p>
        The factor (u − q)/(u + q) is the 'gate'. When u ≪ q it is nearly −1
        (inhibition works against autocatalysis); when u ≫ q it saturates at +1
        (full autocatalysis). This asymptotic sharpness gives the Oregonator its
        steep pulse fronts compared to, say, the FitzHugh–Nagumo model's smoother
        cubic kinetics.
      </p>

      <h2>Why spirals and not blobs?</h2>
      <p>
        The BZ reaction in the oscillatory regime (f = 1.4, ε = 0.04) has a
        stable limit cycle: every point oscillates spontaneously. Diffusion couples
        adjacent points, so a spatial phase gradient forms a travelling wave. A
        'broken wavefront' — the canonical initial condition — creates a
        topological phase singularity (a point where the phase is undefined) that
        acts as the pivot of a rotating spiral. The spiral's angular velocity is
        set by the local limit-cycle frequency, and its wavelength by the
        diffusion length{" "}
        <span className="font-mono">λ ≈ 2π√(Du·T)</span> where T is the oscillation
        period.
      </p>

      <h2>Numerical scheme and stability</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Forward Euler on periodic 128×128 grid, dx = 1.0:

  Laplacian: Lap(u)[i,j] = (u[i±1,j] + u[i,j±1] − 4u[i,j]) / dx²
             → 5-point stencil, np.roll for periodic BC

  Step:
    u += dt × [(1/ε)(u(1-u) - f·v·(u-q)/(u+q)) + Du·Lap(u)]
    v += dt × (u - v)
    u, v clipped to [0, 1]

Stability bound (worst case near u ≈ q, large v):
  |λ_max| = (1/ε)·f·v·2q/(u+q)² ≤ 850  at (u,v) = (q, 1)
  Euler stable iff dt × 850 < 2  →  dt < 0.00235
  Using dt = 0.002  (safety margin × 1.18)`}
      </pre>
      <p>
        Note the clipping to [0, 1] after each step. This is not a physical
        constraint — the continuous equations stay in [0, 1] by construction — but
        it absorbs the O(dt²) Euler error that occasionally pushes a grid point
        fractionally outside the valid range during the steep upstroke. Without
        clipping, one step of u = −0.001 propagates through the (u − q)/(u + q)
        gate and destabilises the simulation.
      </p>

      <h2>Shape keys: four regimes of the same equations</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Basis    ε=0.04 f=1.4  broken-wave IC  t=40  four-armed spiral
SK_Fast  ε=0.02 f=1.4  broken-wave IC  t=40  narrower faster arms
SK_Rings ε=0.04 f=1.4  pacemaker disk  t=40  concentric target rings
SK_Meander ε=0.04 f=1.6 random noise  t=60  spiral breakup / turbulence

Broken-wave IC:  u=1 for x<N/2,  v=1 for y<N/2  + small noise
  → phase singularity at each quadrant-boundary crossing
Pacemaker IC:   central disk r<10 at u=0.85, rest at u*≈0.012
  → single wave source → expanding concentric rings
Random IC:      broad noise near u*  → spontaneous nucleation of many tips`}
      </pre>
      <p>
        <strong>SK_Fast</strong>: halving ε doubles the temporal frequency. The
        diffusion length contracts proportionally, so spirals pack more tightly.
        Compare the arm spacing in Basis versus SK_Fast — this is the direct
        visual signature of the timescale ratio.
      </p>
      <p>
        <strong>SK_Meander</strong>: at f = 1.6 the system approaches the spiral
        breakup boundary. Spiral tips begin to meander erratically (the
        'hypermeander' instability), neighbouring spirals collide and annihilate,
        and the pattern loses coherence. This is the onset of spatiotemporal
        chemical chaos.
      </p>

      <h2>Colour and height</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`z  = u × 0.40 m     (excited front  → 0.40 m above resting level)
BZ_Conc FLOAT_COLOR  (POINT domain):
  u = 0.0  →  cobalt  [0.027, 0.159, 0.408, 1.0]   (resting / refractory)
  u = 1.0  →  amber   [0.980, 0.620, 0.050, 1.0]   (excited front)
Shader: MixShader(Principled + Emission) fac=0.35, strength=1.4`}
      </pre>
      <p>
        The cobalt-to-amber gradient directly corresponds to the ferroin indicator
        dye used in real BZ experiments: ferroin (Fe²⁺) is red-orange
        (here approximated as amber), and ferriïn (Fe³⁺) is blue. The height
        emphasises the activator wavefront in 3-D — a physical conceit, but one
        that makes the rotating topological structure immediately legible in WebXR.
      </p>

      <h2>Cross-references</h2>
      <ul className="list-disc pl-5">
        <li>
          <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-barkley-excitable-medium-spiral-wave-uv-sphere-poi-head-webxr">
            Barkley excitable-medium spirals on a UV sphere
          </Link>{" "}
          — piecewise-linear kinetics that approximate BZ but are cheaper to integrate
        </li>
        <li>
          <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-gray-scott-reaction-diffusion-turing-pattern-height-field-webxr">
            Gray-Scott reaction-diffusion (spots and stripes)
          </Link>{" "}
          — autocatalysis without inhibitor oscillation: Turing not BZ
        </li>
        <li>
          <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-complex-ginzburg-landau-pde-spiral-turbulence-benjamin-feir-defect-height-field-stage-floor-webxr">
            Complex Ginzburg-Landau spiral turbulence
          </Link>{" "}
          — the normal-form PDE for oscillatory media; topologically identical spiral
          breakup to SK_Meander but derived from amplitude equations
        </li>
        <li>
          <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-kuramoto-sivashinsky-pde-spatiotemporal-chaos-flame-front-height-field-stage-floor-webxr">
            Kuramoto-Sivashinsky spatiotemporal chaos
          </Link>{" "}
          — a 1-D analogue of spiral turbulence in flame fronts
        </li>
      </ul>

      <h2>Outside sources</h2>
      <ul className="list-disc pl-5">
        <li>
          Field R J, Körös E, Noyes R M (1972).{" "}
          <em>
            Oscillations in chemical systems. IV. Limit cycle behavior in a model
            of a real chemical reaction.
          </em>{" "}
          <a className={lk} href="https://doi.org/10.1021/ja00780a001" target="_blank" rel="noopener noreferrer">
            JACS 94(25):8649–8664
          </a>
          {" "}· PD (&gt;50 years) · original Oregonator kinetics
        </li>
        <li>
          Tyson J J, Fife P C (1980).{" "}
          <em>
            Target waves in a realistic model of the Belousov-Zhabotinskii reaction.
          </em>{" "}
          <a className={lk} href="https://doi.org/10.1063/1.440418" target="_blank" rel="noopener noreferrer">
            J Chem Phys 73(5):2224–2237
          </a>
          {" "}· PD (&gt;40 years) · two-variable reduction; related:{" "}
          <a className={lk} href="https://github.com/scipy/scipy" target="_blank" rel="noopener noreferrer">
            SciPy (BSD-3)
          </a>
        </li>
        <li>
          Winfree A T (1991).{" "}
          <em>
            Varieties of spiral wave behavior: An experimentalist's approach to the
            theory of excitable media.
          </em>{" "}
          <a className={lk} href="https://doi.org/10.1063/1.165844" target="_blank" rel="noopener noreferrer">
            Chaos 1(3):303–334
          </a>
          {" "}· PD equations · comprehensive experimental / theoretical survey;
          related:{" "}
          <a className={lk} href="https://github.com/numpy/numpy" target="_blank" rel="noopener noreferrer">
            NumPy (BSD-3)
          </a>
        </li>
      </ul>

      <h2>Troubleshooting</h2>
      <ul className="list-disc pl-5">
        <li>
          <strong>Simulation blows up (NaN / inf):</strong> dt is too large. Reduce
          to 0.001. Check that q &gt; 0 (u + q in denominator must never be zero).
        </li>
        <li>
          <strong>Pattern looks frozen:</strong> not enough steps. BZ spirals need
          ~5 oscillation periods to stabilise; increase N_BASIS toward 30 000.
        </li>
        <li>
          <strong>No colour on GLB in Three.js:</strong> ensure export_colors=True
          and the Three.js material uses{" "}
          <span className="font-mono">vertexColors: true</span>.
        </li>
        <li>
          <strong>Shape key slider in browser does nothing:</strong> check
          export_morph=True and that the GLB viewer supports morph targets
          (Babylon.js, Three.js r140+ both do).
        </li>
      </ul>
    </>
  );
}

export const entry = buildInstructable({
  slug: SLUG,
  title: TITLE,
  lede: LEDE,
  date: "2026-09-12",
  topics: ["blender", "scripting", "physics", "reaction-diffusion", "webxr"],
  body: Body,
});
