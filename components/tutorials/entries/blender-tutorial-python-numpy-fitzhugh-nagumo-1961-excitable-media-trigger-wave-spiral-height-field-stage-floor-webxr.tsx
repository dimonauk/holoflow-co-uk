import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-fitzhugh-nagumo-1961-excitable-media-" +
  "trigger-wave-spiral-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — FitzHugh-Nagumo 1961 Excitable Media " +
  "∂u/∂t = DU∇²u + u − u³/3 − v + I  ∂v/∂t = ε(u + A − Bv) " +
  "ETD1 Spectral Unconditionally Stable dt=0.10 (vs Euler dt<0.0005) " +
  "128×128=16384V 16129Q " +
  "Basis(edge-pulse)/SK_Spiral(S1+S2)/SK_Target(pacemaker)/SK_Reentry(line-defect) " +
  "FHN_U_Volt FLOAT_COLOR Cobalt–Amber " +
  "Trigger Wave Spiral Reentrant Height-Field Stage Floor WebXR (Blender 5.1)";

const LEDE =
  "In 1952 Alan Hodgkin and Andrew Huxley wrote four coupled ODEs for the " +
  "nerve impulse — precise, but computationally expensive. " +
  "Richard FitzHugh (1961) showed that the essential excitable behaviour " +
  "survives in just two variables: a fast cubic activator u (voltage-like) " +
  "and a slow recovery variable v. " +
  "Add spatial diffusion of u only, and the system self-organises into " +
  "trigger waves, rotating spirals, and concentric target rings — " +
  "the same reentrant dynamics that underlie ventricular fibrillation. " +
  "This blueprint integrates the FHN PDEs with ETD1 spectral time-stepping, " +
  "maps the voltage field to a height-field stage floor, " +
  "and exports four excitable-media regimes as WebXR GLTF morph targets.";

function Body() {
  return (
    <>
      <p>
        The FitzHugh-Nagumo model is the canonical two-variable reduction of
        Hodgkin-Huxley. Its phase-plane portrait has a single cubic nullcline
        for u (activator, voltage-like) and a near-linear nullcline for v
        (recovery, gating-variable-like). The system is <em>excitable</em>:
        near rest it is stable, but a supra-threshold perturbation sends it on
        a wide excursion before the recovery variable pulls it back — exactly
        the action-potential shape observed in neurons and cardiac cells.
      </p>

      <h2>The PDEs</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`∂u/∂t = DU ∇²u  +  u − u³/3 − v + I_ext     (fast activator)
∂v/∂t = ε (u + A − B·v)                        (slow recovery, no diffusion)

DU = 1.0   voltage diffusivity
ε  = 0.08  slow-fast ratio (small → fast wave, slow recovery)
A  = 0.70  recovery nullcline offset
B  = 0.80  recovery damping
I  = 0.50  applied current (sub-threshold)

Nullclines:
  u-nc: v = u − u³/3 + I     (cubic, S-shaped)
  v-nc: v = (u + A) / B      (near-linear, shifts left/right with A)`}
      </pre>

      <h2>ETD1 spectral integration</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`L_u(k) = −DU · |k|²     spectral diffusion operator for u
û(n+1) = exp(L_u·dt)·û(n) + φ₁(L_u·dt)·N̂_u·dt

φ₁(z) = expm1(z)/z   (Taylor-safe; uses numpy.expm1 to avoid
                       catastrophic cancellation when |z| ≪ 1)

N_u = u − u³/3 − v + I   nonlinear term (explicit)

Recovery (no diffusion → scalar ODE per grid point):
L_v = −ε·B
v(n+1) = exp(L_v·dt)·v(n) + φ₁(L_v·dt)·ε(u+A)·dt

Euler stability:  dt < dx² / (4·DU) ≈ 0.0005  at N=128
ETD1 stability:   dt = 0.10 (200× speedup for diffusion)`}
      </pre>

      <h2>Blueprint walk-through</h2>
      <ul className="list-disc pl-5">
        <li>
          <strong>_k2()</strong> — builds the rfft2 wavenumber grid:
          kx = fftfreq(N, d=1/N), ky = rfftfreq(N, d=1/N), shape (N, N//2+1).
          K² = (2π/N)²·(KX² + KY²).
        </li>
        <li>
          <strong>_etd1_u()</strong> — precomputes E = exp(L_u·dt) and
          φ₁ = expm1(L_u·dt)/L_u·dt once per run. The np.where guards the
          k = 0 mode (L = 0 → φ₁ = 1 exactly).
        </li>
        <li>
          <strong>_etd1_v()</strong> — scalar exact exponential for v decay;
          returns Python floats so the inner loop avoids array allocation.
        </li>
        <li>
          <strong>_ic_s1s2()</strong> — S1+S2 cross-field protocol: runs 300
          steps with an edge-pulse S1, then applies a half-domain S2 stimulus.
          The free spiral tip nucleates at the intersection of the excited and
          refractory regions — the same protocol used in cardiac
          defibrillation studies.
        </li>
        <li>
          <strong>_write_colour()</strong> — uses{" "}
          <code>foreach_set(&quot;color&quot;, rgba)</code> to push 16 384 RGBA values
          in one C-level call; ≈ 40× faster than a per-vertex Python loop.
        </li>
        <li>
          <strong>_add_shape_key()</strong> — constructs the full N²×3
          coordinate buffer with NumPy vectorised index arithmetic, then
          writes it via <code>foreach_set(&quot;co&quot;, buf)</code>.
        </li>
      </ul>

      <h2>Excitable-media regimes</h2>
      <ul className="list-disc pl-5">
        <li>
          <strong>Basis (edge pulse, 600 steps):</strong> a 10-row excited
          band sweeps rightward as a planar trigger wave. Resting state u ≈
          −1.2 (cobalt); excited front u ≈ +2 (amber); recovery tail
          u ≈ −1 (blue-violet).
        </li>
        <li>
          <strong>SK_Spiral (S1+S2, 1200 steps):</strong> two-armed Archimedean
          spiral with a free tip rotating at the intersection of the excited
          and refractory regions. Period ≈ 25 time units at these parameters.
        </li>
        <li>
          <strong>SK_Target (central pacemaker, 1400 steps):</strong> a small
          central disc maintained at u = 2 acts as a pacemaker, emitting
          concentric circular waves that fill the domain — analogous to a
          sino-atrial node in cardiac tissue.
        </li>
        <li>
          <strong>SK_Reentry (line defect, 900 steps):</strong> the top half
          of the domain is excited while the top-right quarter is simultaneously
          refractory. The resulting asymmetry produces a single reentrant spiral
          tip at the quadrant boundary.
        </li>
      </ul>

      <h2>Differences from the GN Simulation Zone version</h2>
      <p>
        The{" "}
        <Link className={lk} href="/tutorials/blender-tutorial-gn-simulation-zone-fitzhugh-nagumo-excitable-medium-spiral-reentry-poi">
          Geometry Nodes simulation-zone version
        </Link>{" "}
        runs the FHN equations inside Blender&apos;s node graph — elegant for
        real-time interactive sculpting of excitable media, but limited to
        finite-difference stencils and relatively small grids. The Python/NumPy
        ETD1 blueprint here runs a spectral integrator in a pre-computation
        step, stores each regime as a shape key, and exports a compact GLB with
        morph targets — better suited for large grids and WebXR deployment
        where the server-side compute is done once.
      </p>

      <h2>Relation to other studio content</h2>
      <ul className="list-disc pl-5">
        <li>
          <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-oregonator-belousov-zhabotinsky-bz-fkn-1972-chemical-spiral-wave-height-field-stage-floor-webxr">
            Oregonator BZ spirals
          </Link>{" "}
          — the Belousov-Zhabotinsky reaction uses a stiff three-variable
          Oregonator model with very different nullcline geometry; BZ spirals
          meander under the &ldquo;turbulent&rdquo; F = 1.6 parameter, whereas FHN spirals
          are anchored by the cubic nullcline shape.
        </li>
        <li>
          <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-gierer-meinhardt-activator-inhibitor-turing-morphogenesis-1972-spot-stripe-height-field-stage-floor-webxr">
            Gierer-Meinhardt Turing patterns
          </Link>{" "}
          — stationary Turing spots arise from long-range inhibition; FHN
          excitable media instead produce propagating waves from local kinetic
          bistability, with no inhibitor diffusion required.
        </li>
        <li>
          <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-gray-scott-reaction-diffusion-spot-stripe-webxr">
            Gray-Scott reaction-diffusion
          </Link>{" "}
          — GS uses two diffusing species and produces stationary patterns;
          FHN has only activator diffusion and produces travelling waves.
        </li>
      </ul>

      <h2>Outside sources</h2>
      <ul className="list-disc pl-5">
        <li>
          FitzHugh R. (1961).{" "}
          <em>Impulses and physiological states in theoretical models of
            nerve membrane.</em>{" "}
          <a className={lk} href="https://doi.org/10.1016/S0006-3495(61)86902-6"
             target="_blank" rel="noopener noreferrer">
            Biophys. J. 1(6):445–466
          </a>
          {" "}· PD · original FHN two-variable reduction; related:{" "}
          <a className={lk} href="https://github.com/numpy/numpy"
             target="_blank" rel="noopener noreferrer">
            NumPy (BSD-3)
          </a>
        </li>
        <li>
          Barkley D. (1991).{" "}
          <em>A model for fast computer simulation of waves in excitable
            media.</em>{" "}
          <a className={lk} href="https://doi.org/10.1016/0167-2789(91)90194-E"
             target="_blank" rel="noopener noreferrer">
            Physica D 49:61–70
          </a>
          {" "}· PD · Barkley parameterisation bridges FHN to cardiac models;
          related:{" "}
          <a className={lk} href="https://github.com/scipy/scipy"
             target="_blank" rel="noopener noreferrer">
            SciPy (BSD-3)
          </a>
        </li>
      </ul>

      <h2>Troubleshooting</h2>
      <ul className="list-disc pl-5">
        <li>
          <strong>No spiral (flat wave or static):</strong> check that{" "}
          <code>_ic_s1s2()</code> ran 300 pre-steps before applying S2; if the
          S1 wave hasn&apos;t crossed the domain the S2 stimulus cannot create a
          free tip.
        </li>
        <li>
          <strong>u field blows up (NaN):</strong> reduce DT below 0.10 — the
          ETD1 stability guarantee applies to the linear diffusion operator
          only; the explicit nonlinear term u³ can still destabilise if DT is
          too large and the field is very far from equilibrium.
        </li>
        <li>
          <strong>No colour gradient visible:</strong> confirm the material uses
          ShaderNodeAttribute with <code>ATTR_NAME = &quot;FHN_U_Volt&quot;</code> and
          that the GLB was exported with <code>export_colors=True</code>.
        </li>
        <li>
          <strong>Shape keys look identical:</strong> each IC function
          resets u and v independently; ensure that each VARIANTS entry
          calls a different IC key (edge_pulse / s1s2 / target / reentry).
        </li>
      </ul>
    </>
  );
}

export const entry = buildInstructable({
  slug: SLUG,
  title: TITLE,
  lede: LEDE,
  date: "2026-09-13",
  topics: ["blender", "scripting", "physics", "reaction-diffusion", "webxr"],
  body: Body,
});
