import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-frank-oseen-nematic-1958-one-constant-q-tensor-disclination-half-integer-defects-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — Frank-Oseen Nematic Liquid Crystal 1958, One-Constant Approximation, Q-Tensor Director Field, ±½ Disclination Defects, Order Parameter Height-Field Stage Floor for WebXR (Blender 5.1)";

const LEDE =
  "A nematic liquid crystal has orientational order but no positional order: rod-like molecules align along a common director n̂ ∈ RP¹ (n̂ ≡ −n̂). Frank and Oseen (1958) showed the elastic free energy depends on three distortion modes — splay, twist, and bend — each with its own elastic constant. In the one-constant approximation (K₁=K₂=K₃=K), the free energy reduces to F = K/2 ∫|∇θ|² dA and the Euler–Lagrange equation becomes Laplace's equation: ∇²θ = 0. This admits an exact analytic solution for any configuration of point disclinations via superposition of arctan2 functions. The result is a 128×128 order-parameter height-field mesh in Blender 5.1 with four shape keys covering the principal defect topologies: the charge-neutral quadrupole, the isolated +½ comet, the integer +1 hedgehog, and a tight ±½ annihilating pair.";

function Body() {
  return (
    <>
      <p>
        Liquid crystals sit between the crystalline solid and the isotropic
        liquid: they flow like a fluid yet carry orientational order. The
        nematic phase — the simplest and most technologically important — is
        described by a{" "}
        <em>headless</em> director field n̂(x,y) ∈ RP¹, meaning n̂ and −n̂
        are physically identical. This Z₂ symmetry is what allows half-integer
        topological defects (disclinations) that have no counterpart in
        ordinary polar vector fields, and the colour encoding in this blueprint
        — (θ mod π)/π rather than θ/(2π) — respects it exactly. Compare the
        ±1 vortex-antivortex pairs of the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-xy-model-2d-berezinskii-kosterlitz-thouless-1971-1973-vortex-antivortex-unbinding-topological-phase-transition-height-field-stage-floor-webxr"
        >
          XY model (BKT topological phase transition)
        </Link>
        , where the order parameter is a full angle θ ∈ [0,2π) and
        defects carry integer charge.
      </p>

      <h2>Frank–Oseen elastic energy</h2>

      <p>
        The three-constant Frank elastic energy density for a 2D nematic is:
      </p>

      <pre>{`f = ½K₁(∇·n̂)²  +  ½K₂(n̂·∇×n̂)²  +  ½K₃(n̂×∇×n̂)²
       splay              twist               bend`}</pre>

      <p>
        In the one-constant approximation K₁=K₂=K₃=K, this collapses to
        F = K/2 ∫|∇θ|² dA. The Euler–Lagrange equation is simply Laplace's
        equation:
      </p>

      <pre>{`∇²θ = 0`}</pre>

      <p>
        This is the same equation governing electrostatics, 2D fluid flow, and
        — crucially — the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-xy-model-2d-berezinskii-kosterlitz-thouless-1971-1973-vortex-antivortex-unbinding-topological-phase-transition-height-field-stage-floor-webxr"
        >
          XY model in its spin-wave approximation
        </Link>
        . The difference is that sₐ ∈ ½ℤ for nematics, while polar (XY) systems
        require sₐ ∈ ℤ.
      </p>

      <h2>Exact superposition solution</h2>

      <p>
        For a configuration of N disclinations at positions (xₐ,yₐ) with
        topological charges sₐ, the exact solution is:
      </p>

      <pre>{`θ(x,y) = Σₐ sₐ · arctan2(y − yₐ, x − xₐ)`}</pre>

      <p>
        Each term is a harmonic function away from its pole —
        ∇²arctan2(y,x) = 0 — so the sum solves Laplace's equation everywhere
        except the defect cores. The charge sₐ is the winding number:
        going around defect α once, the director rotates by 2π·sₐ. For a
        nematic, s=+½ gives a &ldquo;comet&rdquo; pattern in which all
        director lines radiate from the core; s=−½ gives a three-armed
        &ldquo;trefoil&rdquo;.
      </p>

      <p>
        A closed domain requires total charge Σ sₐ = 0 (the topological
        constraint on a closed surface). On an open square domain the boundary
        absorbs any net charge — the SK_Comet and SK_Hedgehog shape keys use
        single defects for illustration, with the boundary providing the
        compensating charge.
      </p>

      <h2>Order parameter and height field</h2>

      <p>
        Deep inside a disclination core the nematic order is destroyed:
        molecules are no longer aligned. Landau–de Gennes theory describes
        this through a scalar order parameter S ∈ [0,1], with S=0 at the
        isotropic core and S=1 in the perfectly ordered bulk. The blueprint
        uses a Gaussian model:
      </p>

      <pre>{`S(x,y) = 1 − exp(−d_min² / ξ²)

where d_min = min distance to any defect
      ξ     = R_CORE  (Frank coherence length)`}</pre>

      <p>
        Height Z = S × Z_SCALE creates a flat plateau with pits precisely at
        defect positions. The four shape keys move the pits as each defect
        configuration changes, giving a topological &ldquo;terrain&rdquo; whose
        valleys reveal where order breaks down.
      </p>

      <p>
        This is structurally similar to the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-complex-ginzburg-landau-pde-spiral-turbulence-benjamin-feir-defect-height-field-stage-floor-webxr"
        >
          Complex Ginzburg–Landau equation
        </Link>
        , where the amplitude |A| = 0 at topological defects (phase vortices)
        and the height field visualises the order parameter envelope. There the
        defects are dynamic; here they are frozen at analytically placed
        positions.
      </p>

      <h2>Colour encoding and the Z₂ symmetry</h2>

      <pre>{`Colour attribute  LC_Director  (FLOAT_COLOR, POINT domain)
Value             (θ mod π) / π  ∈ [0, 1)
Map               0 → COBALT   (0.027, 0.141, 0.557)
                  1 → AMBER    (0.980, 0.620, 0.050)`}</pre>

      <p>
        Using θ mod π rather than θ mod 2π ensures the colour completes
        exactly one cycle per 180° rotation of the director — the correct
        period for a headless vector. Around a +½ defect the colour runs
        through half a cycle; around a +1 defect it runs through a full cycle.
        This is the same convention used in polarised-light microscopy images
        of nematics, where a λ/2 wave plate produces identical colours for
        n̂ and −n̂.
      </p>

      <h2>Blueprint parameters</h2>

      <pre>{`N       = 128       # 128×128 = 16 384 vertices, 16 129 quads
R_CORE  = 0.14      # core radius in [−1,1] domain  (≈ 14% of half-width)
Z_SCALE = 0.40      # height amplitude (metres)`}</pre>

      <h2>Running the blueprint</h2>

      <pre>{`# In Blender 5.1 → Scripting tab → open blueprint.py → Run Script
# Saves lc_nematic_floor.blend and exports lc_nematic_floor.glb

# For the viewport animation:
# open record.py in Scripting tab → Run Script
# Outputs public/library/videos/scripting/<slug>/viewport.mp4`}</pre>

      <h2>Shape key guide</h2>

      <p>
        <strong>Basis — quadrupole (+½,+½,−½,−½).</strong> The most common
        texture observed in confined planar nematic cells. Two positive
        (+½) and two negative (−½) disclinations sit at the four corners of
        a square, giving a charge-neutral configuration that minimises the
        total Frank energy. The +½ comets point outward; the −½ trefoils
        sit between them. This is the analogue of the four-vortex state in
        the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-allen-cahn-phase-field-mean-curvature-motion-allen-cahn-1979-stage-floor-webxr"
        >
          Allen–Cahn order parameter field
        </Link>
        , where domain walls connect the order-parameter wells.
      </p>

      <p>
        <strong>SK_Comet — single +½ disclination.</strong> All director lines
        radiate from the core at angles uniformly spaced by 180° (not 360°,
        because of the Z₂ symmetry). The colour spans half the cobalt–amber
        cycle as you orbit the defect. In practice this texture appears at the
        tip of liquid-crystal cells and near surface-anchoring defects.
      </p>

      <p>
        <strong>SK_Hedgehog — single +1 integer defect.</strong> A full radial
        &ldquo;hedgehog&rdquo; pattern: director lines point in every direction
        from the core, spanning the full colour cycle. In a 2D nematic this
        configuration is metastable — it can lower its energy by &ldquo;escaping
        into the third dimension&rdquo; (the director tilts out of the plane
        at the core, converting +1 → +½+½ with a lower total Frank energy).
        Integer disclinations in true 2D nematics are thus unstable relative
        to pairs of half-integer ones.
      </p>

      <p>
        <strong>SK_Anneal — tight ±½ pair.</strong> A +½ comet at (0.15,0) and
        a −½ trefoil at (−0.15,0). Like opposite electric charges, opposite-sign
        disclinations attract; the elastic energy of the pair decreases
        logarithmically as they approach. At short range the cores overlap, the
        order parameter returns to S=1 everywhere, and both defects annihilate.
        This annihilation is the key relaxation mechanism in nematic films
        after a rapid quench from the isotropic phase — compare the coarsening
        dynamics of the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-gray-scott-1984-pearson-1993-activator-depletion-turing-spot-worm-hole-height-field-stage-floor-webxr"
        >
          Gray–Scott reaction-diffusion system
        </Link>
        , where spot-annihilation drives pattern selection.
      </p>

      <h2>Trade-offs and limitations</h2>

      <pre>{`One-constant vs three-constant:
  Real nematics have K₁ ≠ K₂ ≠ K₃. Splay-dominated defects (K₁ large)
  have rounder +½ cores; bend-dominated ones have sharper features.
  The one-constant solution gives qualitatively correct topology but
  not quantitative core shapes.

2D vs 3D:
  In a thin nematic film, confinement forces all directors into the plane,
  justifying the 2D model. In bulk nematics the director can escape into
  the third dimension, converting +1 disclinations into point defects
  (hedgehogs) of lower total energy.

Arctan2 branch cuts:
  arctan2(y,x) has a branch cut along −x. Near a defect at the left edge
  of the domain you may see a sharp colour jump. This is an artefact of
  the arctan2 representation, not a physical feature; the order parameter
  S (which depends only on d_min) is unaffected.

Core size:
  R_CORE = 0.14 is chosen to give visually distinct pits. In a real nematic
  ξ ≈ 10–100 nm, far below the cell size; scale accordingly for quantitative
  work.`}</pre>

      <h2>Outside sources</h2>

      <p>
        <strong>
          Frank, F.C. (1958). &ldquo;Liquid crystals. On the theory of liquid
          crystals.&rdquo;
        </strong>{" "}
        <em>Discuss. Faraday Soc.</em> 25:19–28.{" "}
        <a
          className={lk}
          href="https://doi.org/10.1039/df9582500019"
          target="_blank"
          rel="noopener noreferrer"
        >
          doi:10.1039/df9582500019
        </a>
        . Public Domain (&gt;50 yr). The foundational paper unifying Oseen&apos;s
        splay and Zocher&apos;s twist into the three-constant elastic energy used
        today. Related project: Oseen CW 1933 Trans. Faraday Soc. 29:883 (PD
        &gt;80 yr) — the earlier partial formulation; Zocher H 1933 Trans.
        Faraday Soc. 29:945 (PD &gt;80 yr) — contemporary independent work on
        anisotropic fluid distortions.
      </p>

      <p>
        <strong>
          Harris, C.R. et al. (2020). &ldquo;Array programming with
          NumPy.&rdquo;
        </strong>{" "}
        <em>Nature</em> 585:357–362.{" "}
        <a
          className={lk}
          href="https://doi.org/10.1038/s41586-020-2649-2"
          target="_blank"
          rel="noopener noreferrer"
        >
          doi:10.1038/s41586-020-2649-2
        </a>
        . BSD-3-Clause (NumPy source); CC-BY 4.0 (article). The blueprint uses
        NumPy for the arctan2 superposition, meshgrid, and minimum-distance
        order-parameter computation. Related project: SciPy (BSD-3-Clause,{" "}
        <a
          className={lk}
          href="https://github.com/scipy/scipy"
          target="_blank"
          rel="noopener noreferrer"
        >
          github.com/scipy/scipy
        </a>
        ) — used for special functions and Voronoi geometry in related
        tutorials.
      </p>
    </>
  );
}

export const blenderTutorialPythonNumpyFrankOseenNematic1958OneConstantQTensorDisclinationHalfIntegerDefectsHeightFieldStageFloorWebxrEntry: Entry = buildInstructable({
  slug: SLUG,
  title: TITLE,
  lede: LEDE,
  body: <Body />,
  topics: ["blender", "python", "scripting", "physics", "soft-matter", "webxr"],
  blenderVersion: "5.1",
  publishedAt: "2026-09-19",
  libraryPath:
    "blends/scripting/python-numpy-frank-oseen-nematic-1958-one-constant-q-tensor-disclination-half-integer-defects-height-field-stage-floor-webxr",
});
