import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-gierer-meinhardt-activator-inhibitor-" +
  "turing-morphogenesis-1972-spot-stripe-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — Gierer-Meinhardt Activator-Inhibitor 1972 " +
  "∂a/∂t = D_a∇²a + ρa²/h − μa + ρ₀  ∂h/∂t = D_h∇²h + ρa² − νh " +
  "Short-Range Activation Long-Range Inhibition Turing Morphogenesis " +
  "D_a=0.001 D_h=0.05 Ratio=50 Steady State a*=(ν+ρ₀)/μ h*=ρa*²/ν " +
  "128×128=16384V 16129Q " +
  "Basis(spots ρ₀=0.004)/SK_Labyrinthine(stripes)/SK_Dense(ρ₀=0.008)/SK_Seascape(μ=0.05) " +
  "GM_Activator FLOAT_COLOR Cobalt–Amber " +
  "Biological Pattern Formation Spot Stripe Height-Field Stage Floor WebXR (Blender 5.1)";

const LEDE =
  "In 1952 Alan Turing showed mathematically that two chemical species — " +
  "one self-activating, one inhibitory — could spontaneously break a uniform " +
  "state into spatial pattern, given only that the inhibitor diffuses faster. " +
  "Twenty years later Alfred Gierer and Hans Meinhardt gave the first " +
  "biologically concrete equations for this mechanism, explaining why fish " +
  "carry evenly-spaced spots, why hair follicles form a triangular lattice, " +
  "and why a regenerating Hydra grows exactly one head. " +
  "This blueprint integrates their 1972 activator-inhibitor system on a " +
  "periodic 128 × 128 grid, maps activator concentration to height and colour, " +
  "and exports four parameter regimes — spots, stripes, dense, seascape — " +
  "as GLTF morph targets for a WebXR stage floor.";

function Body() {
  return (
    <>
      <p>
        The Turing instability is counterintuitive: diffusion usually smooths
        things out, yet here it <em>creates</em> spatial heterogeneity. The trick
        is asymmetric diffusivity. The activator amplifies itself locally but
        barely spreads; the inhibitor, stimulated by that same activator, races
        outwards and suppresses activation everywhere except the peak. Each peak
        therefore carves a &ldquo;shadow&rdquo; around itself, preventing neighbours from
        forming too close — a purely self-organised repulsion that sets the
        characteristic spacing you see on a zebra fish.
      </p>

      <h2>The Gierer-Meinhardt equations</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`∂a/∂t = D_a ∇²a  +  ρ · a² / h  −  μ · a  +  ρ₀    … activator
∂h/∂t = D_h ∇²h  +  ρ · a²         −  ν · h    … inhibitor

a > 0 : activator  — self-amplifying (short-range)
h > 0 : inhibitor  — suppresses a  (long-range)
D_a = 0.001,  D_h = 0.05  (D_h / D_a = 50)
ρ = 0.02     cross-production rate
μ, ν         activator / inhibitor decay rates (vary per regime)
ρ₀           basal activator production (prevents trivial zero state)`}
      </pre>

      <h2>Homogeneous steady state</h2>
      <p>
        Setting spatial gradients and time derivatives to zero:
      </p>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`h* = ρ · (a*)² / ν         ← from inhibitor equation
ν − μ · a* + ρ₀ = 0        ← substituting into activator
⟹  a* = (ν + ρ₀) / μ,   h* = ρ(a*)² / ν

Basis regime: μ=0.04 ν=0.07 ρ₀=0.004
  a* = (0.07 + 0.004) / 0.04 = 1.85
  h* = 0.02 × 1.85² / 0.07  = 0.978`}
      </pre>

      <h2>Turing instability analysis</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Jacobian at (a*, h*):
  f_a = 2ν/a* − μ  = 0.0356   > 0  (activator self-amplifies)
  f_h = −ν²/(ρa*²) = −0.0714  < 0  (inhibitor suppresses activator)
  g_a = 2ρa*        = 0.074    > 0  (activator stimulates inhibitor)
  g_h = −ν          = −0.07

Stability without diffusion:
  tr(J) = f_a + g_h = −0.0344 < 0  ✓
  det(J) = f_a·g_h − f_h·g_a = 0.00279 > 0  ✓

Turing condition (instability with diffusion):
  D_h·f_a + D_a·g_h = 0.00171 > 0  ✓
  (0.00171)² = 2.9×10⁻⁶  >  4·D_a·D_h·det(J) = 5.6×10⁻⁷  ✓

Critical wavenumber  k_c: growth rate σ(k)=0 at the threshold.
  k_c² ≈ (D_h·f_a + D_a·g_h) / (2·D_a·D_h) − …
  → characteristic wavelength λ_c ≈ 10–14 grid units at these params.`}
      </pre>

      <h2>Numerical integration</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`Forward Euler, 5-point periodic Laplacian, dt = 0.5, dx = 1.

Stability:
  Diffusion:  dt · D_h / dx² = 0.025  ≤  0.5  ✓
  Reaction:   |λ_max| at steady state ≈ 0.054 (complex pair)
              dt · 0.054 = 0.027  ≪  1  ✓

Initialisation: a = a*(1 + 5%·noise), h = h*(1 + 5%·noise)
  WHY not start at zero: a=0 is an absorbing state (a²/h=0), so ρ₀
  provides a floor, but we still need non-zero IC to seed the modes
  above k_c that will grow into the Turing pattern.

Runtime (pure numpy on CPU):
  128² grid, 15 000 steps ≈ 6–10 s on a modern laptop.`}
      </pre>

      <h2>Blueprint walk-through</h2>
      <ul className="list-disc pl-5">
        <li>
          <strong>run_gm()</strong> — integrates activator and inhibitor fields
          for a given number of steps; returns the final activator array. Called
          four times (once per shape-key regime) with different μ, ν, ρ₀.
        </li>
        <li>
          <strong>_build_base_mesh()</strong> — creates a 128 × 128 quad grid in
          the XY plane; Z = normalised activator × ZSCALE (0.35 m). Row-major
          vertex layout so index maths stays simple.
        </li>
        <li>
          <strong>_apply_vertex_colour()</strong> — cobalt (low a) → amber (high a)
          using <code>FLOAT_COLOR POINT</code> domain.{" "}
          <code>foreach_set()</code> pushes the full 16 384-element RGBA array in
          one C-level call — ≈ 40× faster than per-vertex Python loops.
        </li>
        <li>
          <strong>_add_shape_key()</strong> — for each additional regime, builds a
          new normalised Z-column and writes it to a shape key via{" "}
          <code>foreach_set('co', …)</code>.
        </li>
        <li>
          <strong>_build_material()</strong> — Principled BSDF with{" "}
          <code>ShaderNodeAttribute</code> feeding both Base Color and Emission
          Color from <code>GM_Activator</code>; Emission Strength 1.5 gives the
          peaks a subtle glow in Eevee Next without blowing out the valleys.
        </li>
      </ul>

      <h2>Pattern regimes</h2>
      <ul className="list-disc pl-5">
        <li>
          <strong>Basis (spots):</strong> μ = 0.04, ν = 0.07 — activator decay
          and inhibitor decay balanced so each peak remains isolated. Classic
          fish-spot topology, roughly hexagonal lattice after ≈ 7 500 time units.
        </li>
        <li>
          <strong>SK_Labyrinthine:</strong> μ = 0.03, ν = 0.05 — lower μ widens
          the activator peak; lower ν weakens inhibitor strength, allowing peaks
          to elongate and connect into labyrinthine stripes — similar to the
          patterns on a zebra or on adult zebrafish flanks.
        </li>
        <li>
          <strong>SK_Dense:</strong> ρ₀ = 0.008 — higher basal production raises
          the background noise floor, nucleating more seed points; the equilibrium
          spacing shrinks proportionally, packing more spots into the domain.
        </li>
        <li>
          <strong>SK_Seascape:</strong> μ = 0.05, ν = 0.09 — faster decay rates
          shift the steady state to a lower a*, reducing the typical amplitude;
          fewer but larger, rounder peaks reminiscent of coral or seabed topology.
        </li>
      </ul>

      <h2>Differences from Gray-Scott</h2>
      <p>
        The{" "}
        <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-gray-scott-reaction-diffusion-turing-pattern-height-field-webxr">
          Gray-Scott model
        </Link>{" "}
        uses a &ldquo;feed/kill&rdquo; framework (uv² autocatalysis, F-k parameter space)
        and is controlled by replenishment of a precursor species. Gierer-Meinhardt
        is driven by a²/h autocatalysis with independent decay rates; it lacks a
        precursor reservoir but includes basal production ρ₀, making the zero state
        non-absorbing. The two models sit in the same Turing universality class but
        differ in their nullcline geometry and bifurcation structure, so the same
        (F,k) intuitions do not transfer directly.
      </p>
      <p>
        The{" "}
        <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-brusselator-prigogine-lefever-1968-turing-instability-hopf-dissipative-stage-floor-webxr">
          Brusselator
        </Link>{" "}
        is a three-variable trimolecular model; the GM model is cleaner for
        biology because each term has a direct cellular-signalling interpretation
        (autocrine, paracrine, receptor saturation).
      </p>

      <h2>Relation to other studio content</h2>
      <ul className="list-disc pl-5">
        <li>
          <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-oregonator-belousov-zhabotinsky-bz-fkn-1972-chemical-spiral-wave-height-field-stage-floor-webxr">
            Oregonator BZ spirals
          </Link>{" "}
          — oscillating chemistry; GM is a stationary pattern generator, not oscillatory.
        </li>
        <li>
          <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-allen-cahn-phase-field-mean-curvature-motion-allen-cahn-1979-stage-floor-webxr">
            Allen-Cahn phase field
          </Link>{" "}
          — single-variable gradient flow; GM adds a second species with
          cross-coupling that breaks the gradient-flow symmetry.
        </li>
        <li>
          <Link className={lk} href="/tutorials/blender-tutorial-python-numpy-cahn-hilliard-phase-field-spinodal-decomposition-ostwald-ripening-stage-floor-webxr">
            Cahn-Hilliard spinodal decomposition
          </Link>{" "}
          — conserved-order-parameter coarsening ⟨L⟩ ∼ t^(1/3); GM patterns do
          not coarsen once selected, making them preferred for fixed-size biological features.
        </li>
      </ul>

      <h2>Outside sources</h2>
      <ul className="list-disc pl-5">
        <li>
          Gierer A, Meinhardt H (1972).{" "}
          <em>A theory of biological pattern formation.</em>{" "}
          <a className={lk} href="https://doi.org/10.1007/BF00289234" target="_blank" rel="noopener noreferrer">
            Kybernetik 12(1):30–39
          </a>
          {" "}· PD (&gt;50 years) · the original activator-inhibitor model;
          related:{" "}
          <a className={lk} href="https://github.com/numpy/numpy" target="_blank" rel="noopener noreferrer">
            NumPy (BSD-3)
          </a>
        </li>
        <li>
          Koch A J, Meinhardt H (1994).{" "}
          <em>
            Biological pattern formation: from basic mechanisms to complex structures.
          </em>{" "}
          <a className={lk} href="https://doi.org/10.1103/RevModPhys.66.1481" target="_blank" rel="noopener noreferrer">
            Rev Mod Phys 66(4):1481–1507
          </a>
          {" "}· PD (equations) · comprehensive parameter-space survey; related:{" "}
          <a className={lk} href="https://github.com/scipy/scipy" target="_blank" rel="noopener noreferrer">
            SciPy (BSD-3)
          </a>
        </li>
        <li>
          Turing A M (1952).{" "}
          <em>The chemical basis of morphogenesis.</em>{" "}
          <a className={lk} href="https://royalsocietypublishing.org/doi/10.1098/rstb.1952.0012" target="_blank" rel="noopener noreferrer">
            Phil Trans R Soc B 237:37–72
          </a>
          {" "}· PD (&gt;70 years) · foundational stability analysis; related:{" "}
          <a className={lk} href="https://github.com/numpy/numpy" target="_blank" rel="noopener noreferrer">
            NumPy (BSD-3)
          </a>
        </li>
      </ul>

      <h2>Troubleshooting</h2>
      <ul className="list-disc pl-5">
        <li>
          <strong>Pattern is uniform (no spots form):</strong> Turing instability
          not triggered for the chosen parameters. Verify D_h / D_a &gt; ≈ 20 and
          that tr(J) &lt; 0, det(J) &gt; 0 at the steady state.
        </li>
        <li>
          <strong>Simulation blows up (NaN):</strong> a²/h explodes if a spikes
          before h responds. Reduce DT to 0.1 or tighten the clip ceiling in
          _step(). The transient first ~200 steps are worst; after that the
          dynamics settle.
        </li>
        <li>
          <strong>All four shape keys look identical:</strong> check that run_gm()
          is called with different seed values; the same seed produces the same
          noise pattern and nearly the same final state.
        </li>
        <li>
          <strong>No colour in Three.js / Babylon:</strong> ensure
          export_colors=True and that the viewer material uses vertexColors: true
          (Three.js) or enableVertexColors: true (Babylon).
        </li>
        <li>
          <strong>Shape key slider in browser does nothing:</strong> export_morph=True
          is required; also confirm the GLB consumer supports morph targets
          (Three.js r140+, Babylon.js 6+).
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
