import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

function Body() {
  return (
    <>
      <p>
        In 1687 Isaac Newton showed that every mass in the universe attracts
        every other mass with a force proportional to the product of their
        masses and inversely proportional to the square of the distance between
        them. For two bodies the resulting orbit is a perfect Keplerian ellipse.
        Add a third body — even with equal masses and symmetric starting
        conditions — and the system is generally{" "}
        <em>not integrable</em>: no closed-form solution exists, the long-term
        behaviour is sensitive to initial conditions, and trajectories are
        chaotic in the Poincaré sense. The three-body problem was the original
        motivation for Poincaré&apos;s development of qualitative (topological)
        dynamics in the 1890s.
      </p>
      <p>
        This blueprint integrates eight equal-mass bodies under mutual
        Newtonian gravity using the{" "}
        <em>leapfrog (Störmer–Verlet) symplectic integrator</em>. Each body
        leaves a growing neon tube trail — the same reveal technique as the{" "}
        <Link
          href="/tutorials/blender-tutorial-gn-simulation-zone-lorenz-attractor-poi-light-painting"
          className={lk}
        >
          Lorenz Attractor light-painting tutorial
        </Link>{" "}
        — and a poi-head UV sphere tracks each body&apos;s tip via
        per-frame location keyframes. EEVEE Next bloom on a black world
        produces a ten-second slow-exposure orbital dance ready for WebXR.
      </p>

      <h2>Why leapfrog and not RK4?</h2>
      <p>
        Runge–Kutta 4 (RK4) has fourth-order accuracy per step: global error
        O(h⁴). It is excellent for short integrations where absolute accuracy
        matters. But gravity simulations run for thousands or millions of
        timesteps, and RK4 is <em>not symplectic</em>: it does not preserve the
        Poincaré invariants of Hamiltonian mechanics. Over long runs RK4 bleeds
        energy out of the system (or pumps it in, depending on the step size)
        causing orbits to slowly spiral inward or outward.
      </p>
      <p>
        The leapfrog scheme is only second-order accurate per step, but it
        exactly preserves a{" "}
        <em>modified Hamiltonian</em> that differs from the true Hamiltonian by
        O(h²). This means energy and angular momentum <em>oscillate</em> about
        their true values rather than drifting monotonically — the system stays
        bound for arbitrarily long integrations. Every planetary N-body code
        (JPL Horizons, MERCURY, REBOUND) uses symplectic integrators for this
        reason.
      </p>
      <pre>{`Leapfrog (kick–drift–kick form):

  1. v_{n+½}  = v_n + a(x_n) · dt/2          ← half kick
  2. x_{n+1}  = x_n + v_{n+½} · dt            ← drift
  3. a_{n+1}  = F(x_{n+1}) / m               ← force eval
  4. v_{n+1}  = v_{n+½} + a_{n+1} · dt/2      ← half kick

  For efficiency we combine steps 4 and 1:
  v_{n+3/2} = v_{n+½} + a_{n+1} · dt (full kick between drifts)`}</pre>

      <h2>Plummer softening — preventing singularities</h2>
      <p>
        Newton&apos;s force F = Gm₁m₂/r² diverges as r → 0. In a discrete
        simulation, if two bodies pass very close together in a single timestep,
        the force spikes, the velocity kicks to enormous values, and the body
        is ejected from the system. This is not unphysical (gravitational
        slingshots are real) but it is numerically disastrous at low resolution.
      </p>
      <p>
        The <em>Plummer softening</em> (Plummer 1911, originally derived for
        star clusters) replaces the denominator r³ in the acceleration formula
        with (r² + ε²)^(3/2):
      </p>
      <pre>{`a_i = G · Σⱼ≠ᵢ mⱼ · (xⱼ - xᵢ) / (|xⱼ - xᵢ|² + ε²)^(3/2)

ε = SOFT_EPS = 0.05 (Blender units)

For r ≫ ε: reduces to exact Newtonian gravity
For r ≈ 0: force magnitude caps at G·mⱼ/ε²`}</pre>
      <p>
        This corresponds to modelling each body as an extended Plummer sphere
        (density ρ ∝ (r²+ε²)^(-5/2)) rather than a point mass. The
        gravitational potential of such a sphere is -Gm/√(r²+ε²) — smooth
        everywhere.
      </p>

      <h2>Initial conditions and centre-of-mass correction</h2>
      <p>
        Bodies are placed on a slightly perturbed annulus with tangential
        velocities scaled to approximate circular orbits: v ≈ √(G·N/r) × 0.55.
        The factor 0.55 makes the system slightly sub-circular so orbits
        precess and bodies exchange angular momentum visibly. After setting
        individual velocities, the centre-of-mass velocity is subtracted
        so the cluster stays centred in frame throughout the animation.
      </p>

      <h2>Building the scene in Python</h2>
      <p>
        The blueprint uses only the{" "}
        <Link
          href="/tutorials/blender-tutorial-python-bpy-gn-tree-from-python-index-switch-poi-head-webxr"
          className={lk}
        >
          bpy data API
        </Link>{" "}
        — no operators that require UI context. This makes it safe to run
        headlessly or from a startup handler. Each body gets:
      </p>
      <ul>
        <li>
          A <code>POLY</code> spline curve with bevel tube; bevel_factor_end
          animated 0→1 across N_FRAMES for the growing-trail reveal.
        </li>
        <li>
          A UV sphere (<code>head_{"{idx}"}</code>) whose location is keyframed
          per frame from the recorded positions — equivalent to the{" "}
          <Link
            href="/tutorials/blender-tutorial-animation-constraints-follow-path-track-to"
            className={lk}
          >
            Follow Path constraint
          </Link>{" "}
          but simpler for programmatically generated curves.
        </li>
        <li>
          An emission material (unique cobalt/pink/green/amber/violet/teal/
          yellow/orange neon hue per body) with EEVEE Bloom wired in via
          scene settings.
        </li>
      </ul>

      <h2>EEVEE Next Bloom settings</h2>
      <p>
        Bloom in EEVEE Next (Blender 5.1) is a compositing pass applied after
        the render buffer. Blueprint sets:
      </p>
      <pre>{`scene.eevee.use_bloom         = True
scene.eevee.bloom_threshold   = 0.30  (HDR values above this bloom)
scene.eevee.bloom_intensity   = 1.20
scene.eevee.bloom_radius      = 5.0   (kernel spread in pixels)`}</pre>
      <p>
        Emission Strength=8 places all eight body colours at HDR values
        well above the threshold. Increasing bloom_radius to 9 gives a more
        diffuse nebula look; reducing to 2 keeps crisp hot-point halos.
        See also the{" "}
        <Link
          href="/tutorials/blender-tutorial-eevee-next-bloom-emission-glow-cel-shade"
          className={lk}
        >
          EEVEE Next Bloom & Emission tutorial
        </Link>
        .
      </p>

      <h2>GLB export for WebXR</h2>
      <p>
        At N_FRAMES the script sets the scene to the final frame (full trails
        visible) and exports with <code>export_apply=True</code> to convert
        curves to mesh geometry. The Holoflow WebXR pipeline expects +Y up,
        transforms applied, and snake_case root names — all satisfied by the
        blueprint. Animation data (location keyframes on the head spheres) is
        included in the GLB via <code>export_animations=True</code>. See the{" "}
        <Link href="/tutorials/blender-tutorial-cycles-lightmap-bake-webxr-uv2" className={lk}>
          Lightmap Bake for WebXR tutorial
        </Link>{" "}
        for baking emissive textures onto the trail geometry if a static
        version is needed.
      </p>
    </>
  );
}

const data = {
  date: "2026-09-19",
  title:
    "N-Body Gravitational Dynamics — Leapfrog Symplectic Integration — Orbital Dance for Poi & WebXR (Blender 5.1)",
  lede: "Eight equal-mass bodies attract each other via Plummer-softened Newtonian gravity; integrated with the leapfrog (Störmer–Verlet) symplectic scheme for zero secular energy drift. Each body leaves a growing neon tube trail and drives a poi-head sphere via per-frame keyframes. EEVEE Next bloom on a black world produces a ten-second orbital-dance light painting ready for WebXR.",
  body: Body,
  libraryPath:
    "blends/geometry-nodes/gn-simulation-zone-n-body-gravity-leapfrog-orbital-dance-poi-webxr/",
  steps: [
    {
      title: "Run blueprint.py — leapfrog integration and scene construction",
      body: "Open Blender 5.1 · **Scripting** workspace. Open `blueprint.py` and press **Run Script**.\n\n`_purge()` clears all meshes, curves, materials, and actions so the script is idempotent — safe to re-run.\n\n`_initial_conditions()` places 8 bodies on a perturbed annulus with tangential velocities, then subtracts the centre-of-mass velocity so the cluster stays centred throughout. Masses are equal (1.0) to avoid slingshot ejections at low resolution.\n\n`_integrate()` runs `WARM_UP=200` leapfrog steps (discarded), then records `N_FRAMES=300` frames × `N_SUBSTEPS=8` substeps per frame at `DT=0.012` — total: (200 + 300×8)×0.012 = 31.2 simulation time units.\n\nAfter integration, `_make_trail()` creates a POLY curve + bevel tube for each body. `_make_head()` creates a UV sphere with per-frame location keyframes. Camera and EEVEE settings are applied. The script ends by exporting `nbody_orbital.glb` to the `glbs/` library folder.",
    },
    {
      title: "Understand the leapfrog integrator",
      body: "The full kick–drift loop in blueprint.py:\n\n```python\n# initialise: half-kick to get v at t=-dt/2\nacc = _accel(pos, masses)\nvel = [v + a * (0.5 * DT) for v, a in zip(vel, acc)]\n\n# main loop (per sub-step):\nacc = _accel(pos, masses)      # force at current positions\nvel = [v + a*DT ...]           # full kick (two half-kicks combined)\npos = [p + v*DT ...]           # drift\n```\n\nThe half-kick initialisation puts `vel` at the midpoint of the first step. Thereafter each full-kick advances `vel` by a full `DT` centred on the current `pos` — this interleaving of kick and drift is what makes leapfrog second-order and symplectic.\n\nTo verify: check that total kinetic + potential energy fluctuates but does NOT trend up or down over 300 frames. Add a debug print in `_integrate()` after each warm-up step to confirm.",
    },
    {
      title: "Inspect Plummer softening behaviour",
      body: "Set `SOFT_EPS = 0.0` (exact gravity) and `N_BODIES = 3` in blueprint.py. Re-run the script. With only three bodies you will occasionally see a close encounter where two bodies approach within the DT × velocity distance — the leapfrog step applies an enormous force spike and one body is ejected with a very high velocity (gravitational slingshot).\n\nRestore `SOFT_EPS = 0.05`. The same initial conditions now produce smooth, bounded trajectories: the maximum force between any pair is capped at G·m/ε² = 400 (scene units). This softening makes the system behave as though each body were an extended sphere of radius ε rather than a point mass.",
    },
    {
      title: "Tune N_BODIES for visual richness vs performance",
      body: "The direct-sum force calculation has cost O(N²): doubling N_BODIES quadruples the computation.\n\n| N_BODIES | pairs computed per sub-step | Approx. script time |\n|---|---|---|\n| 4 | 6 | < 1 s |\n| 8 | 28 | 2–4 s |\n| 16 | 120 | 10–20 s |\n| 32 | 496 | 60–120 s |\n\nAt N=8 the cluster shows clear exchange orbits where two bodies briefly pair up (a binary) and then separate — a hallmark of chaotic three-body-style encounters. At N=16 the cluster begins to look like a mini star cluster with a dense core and loose outer halo.\n\nFor N > 32 consider splitting into a Python script that outputs positions as a CSV, then imports the CSV into Blender — this avoids Blender's GIL overhead per frame.",
    },
    {
      title: "Growing trail animation — bevel_factor_end",
      body: "Each trail uses the same reveal technique as the Lorenz tutorial:\n\n```python\ncu.bevel_factor_end = 0.0\ncu.keyframe_insert('bevel_factor_end', frame=1)\ncu.bevel_factor_end = 1.0\ncu.keyframe_insert('bevel_factor_end', frame=N_FRAMES)\n```\n\n`bevel_factor_end` is a property on the **CURVE data-block** (`cu`), not the object. It controls what fraction of the spline has bevel geometry applied. With LINEAR interpolation between frame 1 and 300, exactly 1/300 of the tube is added per frame.\n\nThe poi-head sphere uses independent location keyframes (one per frame), not a Follow Path constraint. This is simpler for programmatically generated curves and gives exact position at every frame including the final export frame.",
    },
    {
      title: "GLB export and WebXR deployment",
      body: "The export at the end of blueprint.py:\n\n```python\nscene.frame_set(N_FRAMES)       # all trails fully visible\nbpy.ops.export_scene.gltf(\n    filepath=out_glb,\n    export_apply=True,           # curves → mesh geometry\n    export_format='GLB',\n    export_animations=True,      # sphere location keyframes included\n    export_yup=True,             # +Y up for WebXR\n)\n```\n\n`export_apply=True` converts POLY curve + bevel into a triangulated mesh at the current frame. The per-frame location animation on each `head_{idx}` sphere is baked into the GLB's animation channels.\n\nIn WebXR, load the GLB and play the animation via `THREE.AnimationMixer`. The sphere (poi head) will orbit while the trail remains static (it is frozen at frame N_FRAMES in the exported mesh). To animate the trail growing in WebXR, export at each frame and use morph targets — or use a shader-based reveal driven by `uv.y` along the tube length.",
    },
  ],
  finalResult:
    "Eight equal-mass bodies on a perturbed annulus, integrated with leapfrog (N_SUBSTEPS=8, DT=0.012) for 300 recorded frames × 8 sub-steps = 31.2 simulation time units after 200 warm-up steps. Plummer softening ε=0.05 prevents singularities. Each body has a POLY curve trail (TUBE_R=0.012, bevel_factor_end animated 0→1) and a poi-head UV sphere keyframed per frame. Eight neon emission materials with EEVEE Next bloom on a black world. GLB exported at frame 300 with full trail geometry and sphere animation channels for WebXR deployment.",
  variations: [
    "Set N_BODIES=3 with exact masses 1.0, 1.0, 1.0 and initial positions from the known figure-eight choreography (Chenciner & Montgomery 2000): three bodies chase each other around a figure-eight curve sharing a single planar orbit. This is a remarkable solution to the three-body problem that was only discovered in 2000. Set DT=0.001 and N_SUBSTEPS=40 for accuracy. The figure-eight is unstable — tiny perturbations will eventually break it.",
    "Replace the emission trail material with a Principled BSDF using Subsurface Scattering. This turns the neon light-painting look into a bioluminescent organism aesthetic — each trail glows from within rather than emitting raw light. Use CYCLES render engine (slow) or EEVEE with screen-space subsurface scattering enabled.",
    "Add a Gravity Force Field (bpy.ops.object.effector_add with FORCE type) at the scene origin set to strength=-500 (repulsive). The eight bodies now orbit a central mass while also repelling it — a crude analogy for a star cluster around a central black hole with a dark matter halo. Tune the Force Field falloff to INVERSE_SQUARE to match Newtonian gravity.",
    "Export each trail as a separate GLB and load them sequentially in WebXR with a 1-second stagger between visibility. This builds the orbital choreography progressively: first body appears, then 1 s later the second, etc., creating a reveal sequence rather than all eight simultaneously.",
    "Set WARM_UP=0 and use a straight-line initial condition: all bodies on the x-axis at equal spacing with zero velocity. Watch the collapse and bounce: the bodies fall toward each other, interact chaotically near the centre, then escape into hyperbolic trajectories. This is a gravitational N-body collapse — the opposite of the bound-cluster scenario.",
  ],
  troubleshooting: [
    {
      symptom: "Bodies escape the cluster and fly off screen by frame 50",
      cause:
        "DT is too large relative to the minimum inter-body distance, causing force spikes even with softening. Or SOFT_EPS is too small for the chosen DT.",
      fix: "Reduce DT to 0.006 and increase N_SUBSTEPS to 16 to maintain the same total simulation time. Alternatively increase SOFT_EPS to 0.10. As a diagnostic, print the maximum velocity across all bodies after each recorded frame: if any velocity exceeds ~5 Blender units/sim-unit the system is numerically unstable.",
    },
    {
      symptom: "All trails overlap — no visible separation between bodies",
      cause:
        "WARM_UP is too short and the bodies have not yet dispersed from the initial annulus. Or SCENE_SCALE is too small, making all bodies visually identical.",
      fix: "Increase WARM_UP to 500. The cluster needs time to develop exchange interactions. Also check SCENE_SCALE=0.5 is not accidentally set to 0.01 — this would compress all bodies to a single pixel.",
    },
    {
      symptom: "Poi-head spheres are static — they do not move during playback",
      cause:
        "The location keyframes were inserted on the wrong object, or frame range is outside scene.frame_start/frame_end.",
      fix: "In the Python console: `ob = bpy.data.objects['head_0']; print(ob.animation_data.action.fcurves)`. Confirm fcurves exist. Also confirm `scene.frame_end = N_FRAMES` matches the keyframe range. If fcurves are missing, rerun `_make_head()` for body 0 and verify no exception is raised.",
    },
    {
      symptom: "GLB file is 0 bytes or cannot be opened in three.js",
      cause:
        "`export_apply=True` with curves requires at least one visible object at the current frame. If `bevel_depth=0` or `bevel_factor_end=0`, the curve has no mesh to export.",
      fix: "Confirm `scene.frame_set(N_FRAMES)` is called before the export. Check `TUBE_R = 0.012` is non-zero. In Blender's GLTF export panel, tick 'Apply Modifiers'. If the GLB is empty, set the scene to frame N_FRAMES manually and use File → Export → GLTF 2.0 from the UI to diagnose.",
    },
  ],
  externalLinks: [
    {
      label:
        "REBOUND — N-body integrator (Rein & Liu 2012) — MIT Licence",
      href: "https://github.com/hannorein/rebound",
    },
    {
      label:
        "Plummer 1911 — On the Problem of Distribution in Globular Star Clusters — Public Domain (MNRAS)",
      href: "https://ui.adsabs.harvard.edu/abs/1911MNRAS..71..460P",
    },
    {
      label:
        "Blender Manual — Animation & Rigging: Keyframes — CC-BY-SA 4.0 (Blender Foundation)",
      href: "https://docs.blender.org/manual/en/5.1/animation/keyframes/introduction.html",
    },
  ],
  relatedTutorials: [
    {
      label:
        "GN Simulation Zone — Lorenz Attractor: Butterfly Chaos & Light-Painting Trails",
      href: "/tutorials/blender-tutorial-gn-simulation-zone-lorenz-attractor-poi-light-painting",
    },
    {
      label:
        "GN Simulation Zone — SPH Fluid: Pressure & Viscosity Kernel Light-Painting",
      href: "/tutorials/blender-tutorial-gn-simulation-zone-sph-fluid-pressure-viscosity-light-painting",
    },
    {
      label:
        "Points to Curves — Poi Trail & Particle Streak Ribbon for WebXR",
      href: "/tutorials/blender-tutorial-gn-points-to-curves-poi-trail-ribbon-webxr",
    },
    {
      label:
        "EEVEE Next — Bloom, Emission & Glow for Cel-Shading",
      href: "/tutorials/blender-tutorial-eevee-next-bloom-emission-glow-cel-shade",
    },
  ],
};

export const entry: Entry = buildInstructable(
  {
    slug: "blender-tutorial-gn-simulation-zone-n-body-gravity-leapfrog-orbital-dance-poi-webxr",
    title: data.title,
    lede: data.lede,
    date: data.date,
    tags: [
      "blender",
      "geometry-nodes",
      "simulation",
      "physics",
      "gravity",
      "n-body",
      "light-painting",
      "webxr",
    ],
    body: Body,
  },
  data,
);
