"""
N-Body Gravitational Dynamics — Leapfrog Integration — Poi Orbital Dance for WebXR
Blender 5.1  |  Python 3.11  |  bpy + mathutils only

TECHNIQUE
---------
Direct-sum N-body gravity: every pair of point masses attracts via Newton's
inverse-square law.  The softened potential

    F_ij = G · m_i · m_j · r_ij / (|r_ij|² + ε²)^(3/2)

replaces the denominator |r|³ with the Plummer-softened form so close
encounters don't blow up.  Integration uses the leapfrog (Störmer–Verlet)
scheme:

    v_{n+1/2} = v_{n-1/2} + a_n · dt          (kick)
    x_{n+1}   = x_n + v_{n+1/2} · dt          (drift)
    a_{n+1}   = F(x_{n+1}) / m                (compute)

Leapfrog is symplectic: it exactly conserves a modified Hamiltonian, so
energy and angular momentum drift is zero on average (vs Euler which bleeds
energy each step). This is WHY planetary integrators (e.g. MERCURY) prefer
leapfrog/Verlet over RK4 despite RK4's higher accuracy per step.

OUTPUT
------
N_BODIES point masses.  Each body leaves a POLY curve trail (bevel tube)
whose bevel_factor_end is animated 0→1 → growing-trail light-painting.
One poi-head UV sphere is parented to the last point of each trail object
via a Follow Path + a constraint driven by the same factor.  Instead, we
use Python to keyframe each sphere to follow the recorded position directly.

File layout expected by Holoflow webxr exporter:
  holoflow:facet  = False (smooth bodies)
  root name       = snake_case per body  (body_0, body_1 …)
  transforms      = applied at export

Run order: blueprint.py → record.py → SCREEN-RECORDING-NOTES for screen.mp4
"""

import math
import bpy
import mathutils

# ── PARAMETERS ──────────────────────────────────────────────────────────────

N_BODIES     = 8          # number of gravitating bodies
G            = 2.0        # gravitational constant (scene units)
SOFT_EPS     = 0.05       # Plummer softening radius (prevents singularities)
DT           = 0.012      # leapfrog timestep (tune smaller → more accuracy)
N_FRAMES     = 300        # recorded frames (at 30 fps → 10 s video)
N_SUBSTEPS   = 8          # leapfrog sub-steps per Blender frame
WARM_UP      = 200        # throw-away steps before recording starts
TUBE_R       = 0.012      # trail tube bevel radius (Blender units ≈ 12 mm)
BEVEL_RES    = 3          # bevel circle resolution (8 sides)
SPHERE_R     = 0.045      # poi-head sphere radius
SPHERE_SEG   = 10         # sphere LOD (UV segments — kept low for WebXR)
SCENE_SCALE  = 0.5        # scale all initial positions by this

# Initial conditions — 8-body figure-eight-style cluster
# Positions are on a unit circle with slight z offsets; velocities chosen
# so the ensemble has roughly zero net linear momentum.
import random
random.seed(42)

def _initial_conditions():
    """
    Place bodies on a slightly perturbed annulus.  Give each body a
    tangential velocity so the system has angular momentum but no net
    linear drift.  Masses are equal — avoids one body ejecting others.
    """
    positions = []
    velocities = []
    masses = []
    for i in range(N_BODIES):
        angle = (2 * math.pi * i) / N_BODIES
        r = 1.0 + 0.15 * (random.random() - 0.5)
        z = 0.20 * (random.random() - 0.5)
        x = r * math.cos(angle) * SCENE_SCALE
        y = r * math.sin(angle) * SCENE_SCALE
        z = z * SCENE_SCALE
        positions.append(mathutils.Vector((x, y, z)))

        # tangential velocity (perpendicular to radial, in XY-plane)
        # v_tan = sqrt(G * total_mass / r) → circular orbit approximation
        v_circ = math.sqrt(G * N_BODIES / r) * 0.55
        vx = -math.sin(angle) * v_circ
        vy =  math.cos(angle) * v_circ
        vz = 0.05 * (random.random() - 0.5)
        velocities.append(mathutils.Vector((vx, vy, vz)))
        masses.append(1.0)

    # subtract centre-of-mass velocity so the cluster stays in frame
    vcm = mathutils.Vector((0, 0, 0))
    for v, m in zip(velocities, masses):
        vcm += v * m
    total_m = sum(masses)
    vcm /= total_m
    velocities = [v - vcm for v in velocities]
    return positions, velocities, masses


def _accel(positions, masses):
    """Direct-sum acceleration for each body (O(N²) — fine for N≤32)."""
    n = len(positions)
    acc = [mathutils.Vector((0, 0, 0)) for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            r_ij = positions[j] - positions[i]
            dist2 = r_ij.length_squared + SOFT_EPS ** 2
            dist3 = dist2 ** 1.5
            factor = G / dist3
            acc[i] += r_ij * (masses[j] * factor)
            acc[j] -= r_ij * (masses[i] * factor)
    return acc


def _integrate():
    """
    Leapfrog integration.  Returns list of N lists of Vector positions,
    one entry per recorded frame.
    """
    pos, vel, masses = _initial_conditions()

    # Half-kick to initialise leapfrog (kick–drift–kick form needs v at -½dt)
    acc = _accel(pos, masses)
    vel = [v + a * (0.5 * DT) for v, a in zip(vel, acc)]

    # Warm-up (let the cluster relax from the initial conditions)
    for _ in range(WARM_UP):
        for _ in range(N_SUBSTEPS):
            acc = _accel(pos, masses)
            vel = [v + a * DT for v, a in zip(vel, acc)]          # kick
            pos = [p + v * DT for p, v in zip(pos, vel)]          # drift

    # Recording pass
    trails = [[] for _ in range(N_BODIES)]
    for _ in range(N_FRAMES):
        for _ in range(N_SUBSTEPS):
            acc = _accel(pos, masses)
            vel = [v + a * DT for v, a in zip(vel, acc)]
            pos = [p + v * DT for p, v in zip(pos, vel)]
        for i, p in enumerate(pos):
            trails[i].append(p.copy())

    return trails


# ── SCENE SETUP ─────────────────────────────────────────────────────────────

NEON = [
    (0.05, 0.55, 1.00),   # cobalt-blue
    (1.00, 0.25, 0.55),   # hot-pink
    (0.15, 1.00, 0.40),   # neon-green
    (1.00, 0.65, 0.05),   # amber
    (0.75, 0.10, 1.00),   # violet
    (0.05, 0.95, 0.90),   # cyan-teal
    (1.00, 0.90, 0.05),   # yellow
    (1.00, 0.40, 0.10),   # orange
]
EMIT_STR = 8.0


def _purge():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=True, confirm=False)
    for block in (bpy.data.meshes, bpy.data.curves, bpy.data.materials,
                  bpy.data.actions, bpy.data.objects):
        for item in list(block):
            block.remove(item, do_unlink=True)


def _emission_mat(name, rgb, strength=EMIT_STR):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = False
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    emit = nodes.new("ShaderNodeEmission")
    emit.inputs["Color"].default_value = (*rgb, 1.0)
    emit.inputs["Strength"].default_value = strength
    out = nodes.new("ShaderNodeOutputMaterial")
    links.new(emit.outputs["Emission"], out.inputs["Surface"])
    return mat


def _make_trail(idx, pts, mat):
    """Create a POLY curve with bevel tube and animate bevel_factor_end."""
    cu = bpy.data.curves.new(f"trail_{idx}", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = TUBE_R
    cu.bevel_resolution = BEVEL_RES
    cu.use_fill_caps = True
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for k, p in enumerate(pts):
        sp.points[k].co = (*p, 1.0)

    ob = bpy.data.objects.new(f"trail_{idx}", cu)
    ob.data.materials.append(mat)
    bpy.context.scene.collection.objects.link(ob)

    # Animate bevel_factor_end 0 → 1 across N_FRAMES
    cu.bevel_factor_end = 0.0
    cu.keyframe_insert("bevel_factor_end", frame=1)
    cu.bevel_factor_end = 1.0
    cu.keyframe_insert("bevel_factor_end", frame=N_FRAMES)

    for fc in cu.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"

    return ob


def _make_head(idx, pts, mat):
    """UV sphere that tracks the tip of trail idx via object keyframes."""
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=SPHERE_R, segments=SPHERE_SEG, ring_count=SPHERE_SEG,
        location=(0, 0, 0)
    )
    ob = bpy.context.active_object
    ob.name = f"head_{idx}"
    ob.data.name = f"head_mesh_{idx}"
    ob.data.materials.append(mat)

    # Per-frame location keyframes from the recorded trail positions
    # Frame stride: we only have N_FRAMES positions — map frame 1→N_FRAMES
    for frame_i, p in enumerate(pts):
        ob.location = p
        ob.keyframe_insert("location", frame=frame_i + 1)

    for fc in ob.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"

    return ob


def _setup_camera():
    cam_data = bpy.data.cameras.new("cam")
    cam_data.type = "PERSP"
    cam_data.lens = 50
    cam_ob = bpy.data.objects.new("cam", cam_data)
    cam_ob.location = (0, -2.5, 1.2)
    cam_ob.rotation_euler = (math.radians(65), 0, 0)
    bpy.context.scene.collection.objects.link(cam_ob)
    bpy.context.scene.camera = cam_ob


def _setup_eevee():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.eevee.use_bloom = True
    scene.eevee.bloom_threshold = 0.30
    scene.eevee.bloom_intensity = 1.2
    scene.eevee.bloom_radius = 5.0
    world = bpy.data.worlds.new("world")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0, 0, 0, 1)
    bg.inputs["Strength"].default_value = 0.0
    scene.world = world
    scene.frame_start = 1
    scene.frame_end = N_FRAMES
    scene.render.fps = 30


# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    _purge()
    trails = _integrate()

    mats = [_emission_mat(f"mat_{i}", NEON[i % len(NEON)]) for i in range(N_BODIES)]

    for i in range(N_BODIES):
        _make_trail(i, trails[i], mats[i])
        _make_head(i, trails[i], mats[i])

    _setup_camera()
    _setup_eevee()

    scene = bpy.context.scene
    scene.frame_set(N_FRAMES)

    out_glb = bpy.path.abspath(
        "//../../../../glbs/geometry-nodes/"
        "gn-simulation-zone-n-body-gravity-leapfrog-orbital-dance-poi-webxr/"
        "nbody_orbital.glb"
    )
    bpy.ops.export_scene.gltf(
        filepath=out_glb,
        export_apply=True,
        export_format="GLB",
        export_animations=True,
        export_yup=True,
    )
    print(f"[blueprint] GLB exported → {out_glb}")


if __name__ == "__main__":
    main()
