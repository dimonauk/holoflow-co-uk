import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-schnakenberg-1979-activator-substrate-" +
  "turing-instability-spots-stripes-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — Schnakenberg 1979 Activator-Substrate " +
  "∂u/∂t=Du∇²u+γ(a−u+u²v) ∂v/∂t=Dv∇²v+γ(b−u²v) " +
  "ETD1 Spectral Cox-Matthews 2002 Unconditionally Stable dt=0.0005 " +
  "Turing k_c=√[(f_u·Dv+g_v·Du)/(2DuDv)] d=50 γ=1000 " +
  "128×128=16384V 16129Q " +
  "Basis(spots a=0.1268 b=0.7924)/SK_Coarse(a=0.10 b=0.90)/" +
  "SK_Fine(γ=3000 finer-λ)/SK_Bloom(a=0.18 b=0.90 dense) " +
  "SC_Activator FLOAT_COLOR Cobalt–Amber " +
  "Height-Field Stage Floor WebXR (Blender 5.1)";

const LEDE =
  "In 1952 Alan Turing proved that two diffusing chemicals — one slow activator, " +
  "one fast inhibitor — could spontaneously break a uniform state into periodic " +
  "spots and stripes. Johannes Schnakenberg (1979) distilled the minimal chemistry " +
  "capable of this: a cubic autocatalysis u²v provides short-range activation, " +
  "and the depletion of substrate v provides long-range inhibition. " +
  "Because the nonlinearity is polynomial rather than rational, " +
  "the Turing conditions and critical wavenumber are closed-form — " +
  "making Schnakenberg the cleanest system for teaching pattern-formation theory. " +
  "This blueprint integrates the coupled PDEs with ETD1 spectral time-stepping, " +
  "maps the activator field onto a height-field stage floor, " +
  "and exports four distinct spot-array regimes as WebXR GLTF morph targets.";

function Body() {
  return (
    <>
      <p>
        The Schnakenberg model is a stripped-back two-component reaction-diffusion
        system. Its kinetics represent the simplest chemical network that (a) has
        a unique positive steady state, (b) is unstable to spatial perturbations
        when diffusivities differ sufficiently, and (c) generates a bounded
        pattern without blowing up. Those three properties make it the canonical
        <em> minimal Turing system</em>.
      </p>

      <h2>The PDEs</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`∂u/∂t = Du ∇²u  +  γ(a − u + u²v)     activator u
∂v/∂t = Dv ∇²v  +  γ(b − u²v)          substrate v

Steady state:  u* = a + b,   v* = b / (a+b)²`}
      </pre>
      <p>
        The term <code>u²v</code> is the autocatalytic heart of the model: it
        produces <em>u</em> from <em>v</em> at a rate that grows with{" "}
        <em>u</em> itself — short-range positive feedback. The substrate{" "}
        <em>v</em> is consumed by the same term, and because{" "}
        <em>v</em> diffuses far faster (<em>d = Dv/Du = 50</em>), any local
        excess of <em>u</em> draws substrate from a wide neighbourhood —
        long-range negative feedback. Turing&apos;s 1952 instability is the
        result.
      </p>

      <h2>Turing instability — the closed-form derivation</h2>
      <p>
        Linearise around <em>(u*, v*)</em>. The reaction Jacobian is:
      </p>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`A = γ · ⎡ (b−a)/(a+b)      (a+b)²   ⎤
          ⎣ −2b/(a+b)       −(a+b)²  ⎦

tr A  = γ [(b−a)/(a+b) − (a+b)²]   < 0 when b < a + (a+b)³  (stable ODE)
det A = γ² (a+b)³                   > 0 always`}
      </pre>
      <p>
        Add diffusion: the <em>k</em>-th Fourier mode grows as{" "}
        <em>σ(k)</em> = solutions of
        <code>λ² − (tr A − (Du+Dv)k²)λ + h(k²) = 0</code> where
      </p>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`h(k²) = Du Dv k⁴ − (f_u Dv + g_v Du) k² + det A

Turing instability ⟺ h(k_c²) < 0 for some k_c² > 0
  ⟺ (f_u Dv + g_v Du)² > 4 Du Dv det A   AND   f_u Dv + g_v Du > 0

Critical wavenumber: k_c² = (f_u Dv + g_v Du) / (2 Du Dv)`}
      </pre>
      <p>
        For <em>a = 0.1268</em>, <em>b = 0.7924</em>, <em>Du = 1</em>,{" "}
        <em>Dv = 50</em>, <em>γ = 1000</em>: <em>k_c ≈ 18.8</em>, giving a
        pattern wavelength <em>λ_c = 2π/k_c ≈ 0.33</em>. On a domain{" "}
        <em>L = 10</em> this yields roughly 30 spots per axis — the rich,
        cobblestone-like field visible in the Basis shape key.
      </p>

      <h2>ETD1 spectral integrator</h2>
      <p>
        Standard forward Euler on the full PDE requires{" "}
        <em>dt &lt; dx²/(2 Dv)</em>, which for <em>Dv = 50</em> on a
        fine grid is prohibitively small. ETD1 (Cox &amp; Matthews 2002)
        integrates the <em>linear</em> (diffusion) part exactly in spectral
        space — no stability constraint from diffusion — and advances the
        nonlinear (reaction) part by forward Euler:
      </p>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`ũ(t+dt) = E_u · ũ(t)  +  φ₁_u · Ñu(t)
E_u    = exp(−Du k² dt)                [propagator, ≤1 for all k]
φ₁_u  = (E_u − 1) / (−Du k²)          [absorbs dt; limit = dt at k=0]

Nonlinear Euler stability: dt < 2 / |∂Nu/∂u|_max
  |∂Nu/∂u| = γ|−1 + 2uv| ≤ γ(2u*v* − 1) ≈ 724  →  dt_max ≈ 0.00276
  We use dt = 0.0005 for a ×5 safety margin.`}
      </pre>

      <h2>Pattern regimes (shape keys)</h2>
      <p>
        All four regimes are verified to satisfy the Turing conditions before
        running; the script prints a table to the Blender console.
      </p>
      <ul className="list-disc pl-6">
        <li>
          <strong>Basis</strong> — Murray (2003) textbook parameters
          (a = 0.1268, b = 0.7924, γ = 1000). Compact hexagonal spot array.
        </li>
        <li>
          <strong>SK_Coarse</strong> — larger steady-state u* = 1.0, coarser
          wavelength; spots are bigger and more sparsely packed.
        </li>
        <li>
          <strong>SK_Fine</strong> — same (a, b) but γ = 3000. Because
          <em> λ_c ∝ 1/√γ</em>, the pattern wavelength shrinks by
          factor 1/√3 ≈ 0.58; spots are fine and dense.
        </li>
        <li>
          <strong>SK_Bloom</strong> — (a = 0.18, b = 0.90), higher u*; the
          activator field spans a broader range producing a blooming,
          irregular spot array.
        </li>
      </ul>

      <h2>Difference from other Turing systems in this library</h2>
      <ul className="list-disc pl-6">
        <li>
          <Link
            href="/tutorials/blender-tutorial-python-numpy-gierer-meinhardt-activator-inhibitor-turing-morphogenesis-1972-spot-stripe-height-field-stage-floor-webxr"
            className={lk}
          >
            Gierer–Meinhardt (1972)
          </Link>{" "}
          — activation term is <em>u²/h</em> (ratio), inhibitor is a
          separate species with linear self-decay. The denominator creates a
          rational nonlinearity absent in Schnakenberg.
        </li>
        <li>
          <Link
            href="/tutorials/blender-tutorial-python-numpy-brusselator-prigogine-lefever-1968-turing-instability-hopf-dissipative-stage-floor-webxr"
            className={lk}
          >
            Brusselator (1968)
          </Link>{" "}
          — trimolecular kinetics 2X + Y → 3X; two feed species A and B;
          exhibits Hopf bifurcation as well as Turing, making the phase
          diagram richer but harder to analyse.
        </li>
        <li>
          <Link
            href="/tutorials/blender-tutorial-python-numpy-cahn-hilliard-phase-field-spinodal-decomposition-ostwald-ripening-stage-floor-webxr"
            className={lk}
          >
            Cahn–Hilliard (1958)
          </Link>{" "}
          — conservative phase separation (conserved order parameter);
          Schnakenberg is non-conservative (u + v need not be constant).
        </li>
        <li>
          <Link
            href="/tutorials/blender-tutorial-python-numpy-gray-scott-reaction-diffusion-spot-stripe-webxr"
            className={lk}
          >
            Gray–Scott (1983)
          </Link>{" "}
          — feed/kill framing F(1−u) and (F+k)v; the u=1 base state for the
          inhibitor creates a different null-cline geometry.
        </li>
        <li>
          <Link
            href="/tutorials/blender-tutorial-shape-keys-morph-targets"
            className={lk}
          >
            Shape keys / morph targets
          </Link>{" "}
          — the core Blender mechanic used to store multiple simulation states
          as smoothly interpolatable geometry for WebXR.
        </li>
      </ul>

      <h2>Troubleshooting</h2>
      <ul className="list-disc pl-6">
        <li>
          <strong>Uniform flat field, no spots</strong> — check the Turing
          verification table in the Blender console. If a regime shows ✗,
          either d = Dv/Du is too small or (a, b) is outside the Turing space.
          Increase d or reduce a.
        </li>
        <li>
          <strong>NaN / exploding field</strong> — dt is too large. The
          nonlinear Euler stability limit is dt_max = 2 / (γ|2u*v* − 1|).
          At γ = 3000, this drops to ~0.00092; use dt = 0.0003 for SK_Fine.
        </li>
        <li>
          <strong>Square-lattice bias in spots</strong> — you are using finite
          differences, not the spectral scheme. The rfft2 path in blueprint.py
          gives isotropic diffusion by construction.
        </li>
        <li>
          <strong>GLB export missing morph colours</strong> — Blender 5.1
          GLTF exporter requires <em>export_colors=True</em> and{" "}
          <em>export_attributes=True</em> both set. Check the export call at
          the bottom of blueprint.py.
        </li>
      </ul>

      <h2>Outside sources</h2>
      <ul className="list-disc pl-6">
        <li>
          <a
            href="https://doi.org/10.1016/0022-5193(79)90079-3"
            className={lk}
            target="_blank"
            rel="noopener noreferrer"
          >
            Schnakenberg J. (1979) — &ldquo;Simple chemical reaction systems
            with limit cycle behaviour&rdquo; — J. Theor. Biol. 81:389–400
          </a>{" "}
          — original paper, public domain equations.{" "}
          <a
            href="https://github.com/numpy/numpy"
            className={lk}
            target="_blank"
            rel="noopener noreferrer"
          >
            NumPy (BSD-3)
          </a>{" "}
          implements the spectral transforms.
        </li>
        <li>
          <a
            href="https://doi.org/10.1006/jcph.2002.6995"
            className={lk}
            target="_blank"
            rel="noopener noreferrer"
          >
            Cox &amp; Matthews (2002) — &ldquo;Exponential time differencing
            for stiff systems&rdquo; — J. Comput. Phys. 176:430–455
          </a>{" "}
          — source of the ETD1 φ₁ formula. Public domain.{" "}
          <a
            href="https://github.com/scipy/scipy"
            className={lk}
            target="_blank"
            rel="noopener noreferrer"
          >
            SciPy (BSD-3)
          </a>{" "}
          is a related sibling project used for spectral analysis.
        </li>
      </ul>
    </>
  );
}

export const entry: Entry = buildInstructable({
  slug: SLUG,
  title: TITLE,
  lede: LEDE,
  date: "2026-09-13",
  topic: "scripting",
  tags: [
    "reaction-diffusion",
    "turing-patterns",
    "schnakenberg",
    "etd1-spectral",
    "height-field",
    "webxr",
    "numpy",
    "shape-keys",
  ],
  body: Body,
});
