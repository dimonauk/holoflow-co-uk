import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-gumowski-mira-map-1980-conservative-symplectic-island-chain-fractal-log-density-stage-floor-webxr";

const TITLE =
  "Python numpy — Gumowski–Mira Map 1980: " +
  "G(x)=μx+2(1−μ)x²/(1+x²) x'=y+G(x) y'=−x+G(x') " +
  "Conservative Symplectic det J=1 KAM Island Chains Coexisting Chaotic Sea " +
  "128×128=16384V 16129Q 5M Points/SK " +
  "Basis(μ=−0.496 galaxy)/SK_Ring(μ=−0.12 flower)/SK_Web(μ=−0.45 web)/SK_Fish(μ=+0.008 elliptic) " +
  "GM_Density FLOAT_COLOR Cobalt–Amber Log-Density Height-Field Stage Floor WebXR (Blender 5.1)";

const LEDE =
  "The Gumowski–Mira map — x' = y + G(x), y' = −x + G(x') with G(x) = μx + " +
  "2(1−μ)x²/(1+x²) — has an exact Jacobian determinant of 1 for all (x,y). " +
  "That single algebraic fact means it is conservative: no phase-space volume " +
  "contracts, no strange attractor exists, and the KAM theorem guarantees " +
  "closed invariant tori near the elliptic origin — surrounded by chaotic seas " +
  "that are equally real, equally permanent, and visually staggering.";

function Body() {
  return (
    <>
      <p>
        I. Gumowski and C. Mira published the map in 1980 as part of a broader
        study of bounded recurrences with rational nonlinearities. The rational
        sigmoid G(x) was chosen so that all orbits remain in a compact region
        (G saturates to ±2(1−μ) for large |x|), while the twist parameter μ
        controls how quickly the origin rotates nearby orbits. The result is one
        of the most visually rich examples of a{" "}
        <em>mixed phase space</em> — a dynamical system where regular and chaotic
        motion coexist in the same phase portrait, separated by the last
        surviving KAM torus.
      </p>

      <h2>Why det J = 1 makes all the difference</h2>
      <p>
        Compare the Gumowski–Mira map with the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-henon-map-strange-attractor-fractal-basin-poi-webxr"
        >
          Hénon map
        </Link>
        , which has |det J| = 0.3 — it contracts phase-space area by 30% per
        step, so after many iterations all orbits collapse onto a fractal
        strange attractor of dimension ≈ 1.26. The Gumowski–Mira map has
        |det J| = 1 everywhere. By Liouville&apos;s theorem, phase-space
        volume is conserved; the Birkhoff ergodic theorem then tells us that
        time-averaged quantities equal ensemble averages over the
        <em>invariant measure</em> of whichever component of phase space the
        orbit belongs to.
      </p>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`det J = G'(x)·G'(x') − 1·(−1 + G'(x')·G'(x))
       = G'(x)·G'(x') + 1 − G'(x')·G'(x)
       = 1       ✓  (exact cancellation)`}
      </pre>
      <p>
        This cancellation is not accidental. The map is a composition of two
        symplectic twist maps, each of the form (q, p) → (q + G(p), p) or
        (q, p) → (q, p − G(q)), and the composition of symplectic maps is
        symplectic. Gumowski and Mira designed the rational form of G precisely
        to keep this structure whilst introducing global boundedness — something
        a simple linear twist cannot provide.
      </p>

      <h2>KAM tori and the last invariant curve</h2>
      <p>
        The Kolmogorov–Arnold–Moser (KAM) theorem guarantees that sufficiently
        irrational invariant tori of a nearby integrable system survive small
        perturbations. For the Gumowski–Mira map at μ near 0, the phase
        portrait near the origin is close to a family of concentric circles
        (the integrable limit). As |μ| increases, island chains (Birkhoff
        periodic orbits) appear between surviving tori, and chaotic zones
        thicken around homoclinic tangles. Compare this with the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-chirikov-standard-map-kam-breakdown-greene-critical-threshold-stage-floor-webxr"
        >
          Chirikov standard map
        </Link>
        , where Greene&apos;s residue criterion predicts the critical coupling
        at which the last KAM torus breaks into a Cantorus — a Cantor-set
        remnant that still inhibits diffusion but no longer fully confines
        orbits.
      </p>
      <p>
        In the Gumowski–Mira map at μ = −0.496, the outer boundary of the
        visible island structure is precisely such a last surviving KAM torus.
        Beyond it, orbits wander ergodically through the chaotic sea,
        accumulating density in a broad band that surrounds the islands. The
        height-field encodes this directly: the amber ridge at the island
        boundary is the densest region, where orbits linger longest near the
        separatrix; the flat cobalt sea beyond is the ergodic zone.
      </p>

      <h2>Four parameter regimes</h2>
      <p>
        The four shape keys sample qualitatively different topologies of the
        phase portrait by varying μ alone:
      </p>
      <ul className="list-disc pl-5 space-y-1">
        <li>
          <strong>Basis (μ = −0.496)</strong> — the classical Gumowski–Mira
          figure: a galaxy of island chains around a central elliptic fixed
          point, with a large chaotic sea forming the outer amber ring. This
          is the parameter value most reproduced in the literature since 1980.
        </li>
        <li>
          <strong>SK_Ring (μ = −0.120)</strong> — weaker twist rate moves the
          last KAM torus outward and compresses the chaotic zone. The result
          is a series of nearly-concentric rings — each one a surviving KAM
          torus visible as a density ridge — with very little chaotic spread.
        </li>
        <li>
          <strong>SK_Web (μ = −0.450)</strong> — intermediate twist: the
          island chains are denser and more entangled, the separatrices
          between them wider, producing the characteristic Gumowski–Mira
          &ldquo;web&rdquo; pattern where chains of period-5 and period-7
          orbits interpenetrate.
        </li>
        <li>
          <strong>SK_Fish (μ = +0.008)</strong> — near-zero μ gives a large,
          smooth central elliptic island. The twist rate at the origin is
          near-zero so orbits precess very slowly; only a thin chaotic zone
          appears at the outer boundary. The result has been described as a
          &ldquo;fish-eye&rdquo; because of the lens-shaped central region.
        </li>
      </ul>

      <h2>Why log-density as height</h2>
      <p>
        After 5 million orbit steps, visit counts span roughly three decades:
        cells on the densest KAM tori accumulate ~10 000 visits while sparse
        chaotic filaments accumulate ~5–10. Raw counts as height would produce
        a wall-of-spikes with no filament detail. <code>log(1 + count)</code>{" "}
        compresses this range into legible geometry — the same transform used
        in the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-arnolds-cat-map-anosov-diffeomorphism-golden-ratio-torus-chaos-poi-disc-webxr"
        >
          Arnold&apos;s cat map
        </Link>
        {" "}and{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-zaslavsky-stochastic-web-kicked-oscillator-qfold-quasicrystal-stage-floor-webxr"
        >
          Zaslavsky stochastic web
        </Link>{" "}
        blueprints. Adding 1 inside the log avoids log(0) at empty cells,
        which emerge at Z = 0 — a flat sea that reads spatially as the
        &ldquo;absence of phase-space structure&rdquo;.
      </p>

      <h2>Algorithm</h2>
      <pre className="overflow-x-auto rounded bg-black/30 p-3 text-sm">
        {`# Vectorised: all 200 orbits run simultaneously as numpy arrays
x = np.linspace(-3.8, 3.8, 200)    # initial x₀ values (y₀ = 0)
y = np.zeros(200)

for _ in range(500):                # warm-up: discard transient
    xn = y + G(x, mu)
    x, y = xn, -x + G(xn, mu)

# record 5 M points
xs_all = np.empty(200 * 25_000)
ys_all = np.empty(200 * 25_000)
for step in range(25_000):
    xn = y + G(x, mu)
    yn = -x + G(xn, mu)
    x, y = xn, yn
    xs_all[step*200:(step+1)*200] = x
    ys_all[step*200:(step+1)*200] = y

H, _, _ = np.histogram2d(xs_all, ys_all, bins=128, range=[[-4,4],[-4,4]])
density = np.log1p(H.T)             # (y-rows, x-cols)`}
      </pre>
      <p>
        <code>np.histogram2d</code> bins 5 million floating-point pairs in a
        single vectorised pass — roughly 10× faster than{" "}
        <code>np.add.at</code> for arrays of this size. The loop overhead is
        just 25 000 numpy operations on 200-element arrays, completing in
        under two seconds per shape key.
      </p>
      <p>
        The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-arnold-tongue-circle-map-mode-locking-poi-disc-webxr"
        >
          Arnold tongue circle map
        </Link>{" "}
        tutorial uses a similar multi-initial-condition sweep but for a
        dissipative circle map; the contrast with the Gumowski–Mira
        conservative case is instructive — tongues versus islands, same
        scanning strategy, completely different dynamics.
      </p>

      <h2>Shape key implementation</h2>
      <p>
        Blender&apos;s shape key system stores per-vertex position offsets from
        a reference &ldquo;Basis&rdquo; shape. The blueprint builds the mesh
        geometry at Basis density, calls{" "}
        <code>obj.shape_key_add(name=&quot;Basis&quot;, from_mix=False)</code>{" "}
        to register the reference, then for each additional key iterates the
        map at the new μ, recomputes the height field, and sets{" "}
        <code>sk.data[idx].co = vertex_position</code>. The cobalt–amber colour
        attribute stays fixed at the Basis density — it reads as a legend for
        the galactic island structure even when the SK_Fish key is active.
      </p>

      <h2>Troubleshooting</h2>
      <ul className="list-disc pl-5 space-y-1">
        <li>
          <strong>Flat mesh, no height:</strong> the shape key named
          &ldquo;Basis&rdquo; is at value 0.0 in the shape key panel. Either
          it is the active reference (correct) or it needs to be slid to 1.0
          — check which other SK has value 1.0.
        </li>
        <li>
          <strong>Colour missing:</strong> open{" "}
          <em>Object Data Properties → Color Attributes</em> and confirm{" "}
          <code>GM_Density</code> exists with domain POINT. If absent, re-run
          the blueprint.
        </li>
        <li>
          <strong>GLB export fails:</strong> confirm Blender 5.1 has the
          built-in glTF 2.0 exporter enabled (Extensions → glTF 2.0
          importer/exporter) and that the blend file has been saved at least
          once (the <code>//</code> relative path requires a saved file).
        </li>
        <li>
          <strong>Very slow computation:</strong> reduce N_ORBITS to 100 and
          N_STEPS to 10 000 for a quick preview; the density will be sparser
          but the island structure will still be visible.
        </li>
      </ul>
    </>
  );
}

export const entry: Entry = buildInstructable({
  slug:        SLUG,
  title:       TITLE,
  lede:        LEDE,
  date:        "2026-09-12",
  topics:      ["scripting", "numpy", "chaos", "maps", "stage-floor", "webxr"],
  body:        <Body />,
  libraryPath: `blends/scripting/${SLUG.replace("blender-tutorial-", "")}`,
});
