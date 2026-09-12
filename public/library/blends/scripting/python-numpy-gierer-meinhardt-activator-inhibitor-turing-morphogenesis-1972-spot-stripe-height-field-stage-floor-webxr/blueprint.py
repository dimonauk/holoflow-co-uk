"""
Gierer-Meinhardt Activator-Inhibitor Pattern Formation — Gierer & Meinhardt 1972
Short-range activation, long-range inhibition: the Turing morphogenesis engine
128×128 = 16 384 V / 16 129 Q · height-field stage floor for WebXR

Equations (Gierer A, Meinhardt H, 1972, Kybernetik 12:30-39):
    ∂a/∂t = D_a ∇²a  +  ρ · a² / h  −  μ · a  +  ρ₀
    ∂h/∂t = D_h ∇²h  +  ρ · a²       −  ν · h

  a > 0 : activator  — locally self-stimulating (short-range)
  h > 0 : inhibitor  — activated by a, suppresses a (long-range)
  D_a ≪ D_h  (activator diffuses slowly, inhibitor spreads fast)

Steady state (no diffusion, ∂a/∂t = ∂h/∂t = 0):
  h* = ρ · a*² / ν       (from inhibitor equation)
  ν   − μ · a* + ρ₀ = 0  (substituting h* into activator equation)
  ⟹  a* = (ν + ρ₀) / μ,   h* = ρ(a*)² / ν

Turing instability (Turing 1952):
  tr(J) = f_a + g_h = (2ν/a* − μ) − ν < 0          ← stable without diffusion
  det(J) = f_a·g_h − f_h·g_a > 0
  Turing condition: D_h · f_a + D_a · g_h > 0  AND
                    (D_h f_a + D_a g_h)² > 4 D_a D_h det(J)
  ⟹ requires D_h / D_a ≫ 1 (inhibitor diffuses many times faster)

Stability of explicit Euler:
  Diffusion: dt · D_h / dx² ≤ 0.5  ⟹  dt ≤ 10  (D_h=0.05, dx=1)
  Reaction:  |λ_j| at steady state ≈ 0.053 i  ⟹  dt · 0.053 = 0.025 ≪ 1
  Using DT = 0.5 (well inside both bounds).

Shape keys (separate simulations, same 128²  mesh):
  Basis         : ρ₀=0.004 μ=0.04 ν=0.07 → isolated spots   (t = 7500)
  SK_Labyrinthine: ρ₀=0.002 μ=0.03 ν=0.05 → connected stripes (t = 7500)
  SK_Dense      : ρ₀=0.008 μ=0.04 ν=0.07 → small dense spots  (t = 5000)
  SK_Seascape   : ρ₀=0.004 μ=0.05 ν=0.09 → sparse large spots (t = 5000)

Vertex colour: GM_Activator  FLOAT_COLOR  cobalt (low a) → amber (high a)
Blender 5.1 · CC0 (public-domain mathematics)
"""

import bpy, bmesh, numpy as np
from mathutils import Matrix

# ── parameters ────────────────────────────────────────────────────────────────
N       = 128          # grid points per axis
DX      = 1.0          # spatial step (dimensionless grid units)
DT      = 0.5          # time step — inside explicit-Euler stability bounds
RHO     = 0.02         # cross-production rate ρ (activator drives inhibitor)
D_A     = 0.001        # activator diffusivity (slow — short-range activation)
D_H     = 0.05         # inhibitor diffusivity (fast — long-range inhibition)

# Basis regime
MU_B  = 0.04;  NU_B  = 0.07;  RHO0_B  = 0.004;  N_B  = 15_000  # t=7500
# SK_Labyrinthine
MU_L  = 0.03;  NU_L  = 0.05;  RHO0_L  = 0.002;  N_L  = 15_000
# SK_Dense
MU_D  = 0.04;  NU_D  = 0.07;  RHO0_D  = 0.008;  N_D  = 10_000  # t=5000
# SK_Seascape
MU_S  = 0.05;  NU_S  = 0.09;  RHO0_S  = 0.004;  N_S  = 10_000

ZSCALE   = 0.35        # height in metres at maximum activator value
WORLD    = 4.0         # floor half-extent → 8 m × 8 m stage
OBJ_NAME = "gm_activator_floor"
GLB_PATH = "//gm_activator_floor.glb"

# colour stops: cobalt (low) → amber (high)
COL_LO = (0.027, 0.159, 0.557, 1.0)
COL_HI = (0.950, 0.600, 0.000, 1.0)


# ── numerics ──────────────────────────────────────────────────────────────────
def _lap(u: np.ndarray) -> np.ndarray:
    """5-point periodic Laplacian.
    WHY periodic BC: avoids Dirichlet artefacts (activator peaks pinning to
    edges) — the torus domain lets patterns form without boundary effects."""
    return (np.roll(u,  1, 0) + np.roll(u, -1, 0) +
            np.roll(u,  1, 1) + np.roll(u, -1, 1) - 4.0 * u) / (DX * DX)


def _steady_state(mu, nu, rho0):
    """Analytical homogeneous steady state.
    a* = (ν + ρ₀) / μ  ensures ν − μa* + ρ₀ = 0 by construction."""
    a_star = (nu + rho0) / mu
    h_star = RHO * a_star ** 2 / nu
    return a_star, h_star


def _step(a, h, mu, nu, rho0):
    """Single forward-Euler step.
    WHY a²/h form: autocatalytic numerator a² means a small seed is
    self-amplifying; h in the denominator is the inhibitory 'brake'.
    The a²/h kinetics (unlike Gray-Scott uv²) grow without bound if h
    depletes, so clamping at a reasonable ceiling prevents blow-up
    in the first ~50 transient steps before inhibitor catches up."""
    ra = D_A * _lap(a) + RHO * a * a / h - mu * a + rho0
    rh = D_H * _lap(h) + RHO * a * a       - nu * h
    a2 = np.clip(a + DT * ra, 1e-6, 50.0)   # clamp: transient can spike
    h2 = np.clip(h + DT * rh, 1e-6, 500.0)
    return a2, h2


def run_gm(mu, nu, rho0, n_steps, seed=42):
    """Integrate GM from near-steady-state + noise.
    WHY start near steady state not zero: a=0 is an absorbing state for the
    a²/h reaction; ρ₀ provides a floor but still needs a non-zero seed."""
    rng  = np.random.default_rng(seed)
    a0, h0 = _steady_state(mu, nu, rho0)
    # 5 % amplitude noise — enough to seed all Fourier modes above cutoff k_c
    a = a0 * (1.0 + 0.05 * rng.standard_normal((N, N)))
    h = h0 * (1.0 + 0.05 * rng.standard_normal((N, N)))
    a = np.clip(a, 1e-6, None)
    h = np.clip(h, 1e-6, None)
    for _ in range(n_steps):
        a, h = _step(a, h, mu, nu, rho0)
    return a  # activator field drives height and colour


# ── mesh utilities ─────────────────────────────────────────────────────────────
def _build_base_mesh(a_field):
    """Create 128×128 quad grid with height = a_field.
    Vertex layout: row-major (j, i) so X = world-x, Y = world-y (Blender +Y up)."""
    xs = np.linspace(-WORLD, WORLD, N)
    ys = np.linspace(-WORLD, WORLD, N)
    a_norm = (a_field - a_field.min()) / (a_field.max() - a_field.min() + 1e-12)

    me = bpy.data.meshes.new(OBJ_NAME)
    bm = bmesh.new()

    # verts — WHY pre-allocate in array then batch-add: Python loop over
    # 16 384 calls to bm.verts.new() is ≈ 10× slower than build-once strategy
    verts = []
    for j in range(N):
        for i in range(N):
            v = bm.verts.new((xs[i], ys[j], a_norm[j, i] * ZSCALE))
            verts.append(v)
    bm.verts.index_update()

    for j in range(N - 1):
        for i in range(N - 1):
            v0 = verts[ j      * N + i    ]
            v1 = verts[ j      * N + i + 1]
            v2 = verts[(j + 1) * N + i + 1]
            v3 = verts[(j + 1) * N + i    ]
            bm.faces.new((v0, v1, v2, v3))

    bm.to_mesh(me)
    bm.free()
    me.calc_normals()
    return me


def _apply_vertex_colour(me, a_field, layer_name="GM_Activator"):
    """Cobalt → amber colour ramp mapped to normalised activator.
    WHY FLOAT_COLOR not BYTE_COLOR: FLOAT_COLOR preserves the full HDR range
    needed for Eevee Next emission; BYTE_COLOR quantises to 8-bit which
    posterises gradient fields into banding artefacts at strength > 1."""
    a_norm = (a_field - a_field.min()) / (a_field.max() - a_field.min() + 1e-12)
    t_flat = a_norm.ravel()                   # row-major, matches vertex order
    r = COL_LO[0] + t_flat * (COL_HI[0] - COL_LO[0])
    g = COL_LO[1] + t_flat * (COL_HI[1] - COL_LO[1])
    b = COL_LO[2] + t_flat * (COL_HI[2] - COL_LO[2])
    rgba = np.column_stack([r, g, b, np.ones(N * N)]).astype(np.float32)

    if layer_name not in me.color_attributes:
        me.color_attributes.new(name=layer_name, type='FLOAT_COLOR', domain='POINT')
    attr = me.color_attributes[layer_name]
    attr.data.foreach_set('color', rgba.ravel())


def _add_shape_key(obj, a_field, key_name):
    """Append a shape key whose Z-displacements come from a new simulation.
    WHY foreach_set: Blender 5.x per-vertex loops in Python are ≈ 40× slower
    than the C-level bulk copy that foreach_set calls internally."""
    a_norm = (a_field - a_field.min()) / (a_field.max() - a_field.min() + 1e-12)
    sk = obj.shape_key_add(name=key_name, from_mix=False)
    pts = np.empty(N * N * 3, dtype=np.float64)
    obj.data.shape_keys.reference_key.data.foreach_get('co', pts)
    pts = pts.reshape(N * N, 3)
    pts[:, 2] = a_norm.ravel() * ZSCALE
    sk.data.foreach_set('co', pts.ravel())


def _build_material(obj):
    mat = bpy.data.materials.new(OBJ_NAME + "_mat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out   = nodes.new('ShaderNodeOutputMaterial')
    bsdf  = nodes.new('ShaderNodeBsdfPrincipled')
    attr  = nodes.new('ShaderNodeAttribute')
    attr.attribute_name = "GM_Activator"
    attr.attribute_type  = 'GEOMETRY'

    bsdf.inputs['Metallic'].default_value    = 0.10
    bsdf.inputs['Roughness'].default_value   = 0.45
    bsdf.inputs['Emission Strength'].default_value = 1.5

    links.new(attr.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(attr.outputs['Color'], bsdf.inputs['Emission Color'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    obj.data.materials.append(mat)


# ── main build ────────────────────────────────────────────────────────────────
def build():
    # clean slate
    for name in [OBJ_NAME]:
        if name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)

    print("[GM] Running Basis simulation …")
    a_basis = run_gm(MU_B, NU_B, RHO0_B, N_B, seed=7)

    me = _build_base_mesh(a_basis)
    _apply_vertex_colour(me, a_basis)
    obj = bpy.data.objects.new(OBJ_NAME, me)
    bpy.context.scene.collection.objects.link(obj)
    obj.shape_key_add(name="Basis", from_mix=False)

    print("[GM] Running SK_Labyrinthine simulation …")
    a_lab = run_gm(MU_L, NU_L, RHO0_L, N_L, seed=13)
    _add_shape_key(obj, a_lab,  "SK_Labyrinthine")

    print("[GM] Running SK_Dense simulation …")
    a_dens = run_gm(MU_D, NU_D, RHO0_D, N_D, seed=21)
    _add_shape_key(obj, a_dens, "SK_Dense")

    print("[GM] Running SK_Seascape simulation …")
    a_sea = run_gm(MU_S, NU_S, RHO0_S, N_S, seed=37)
    _add_shape_key(obj, a_sea,  "SK_Seascape")

    _build_material(obj)

    # holoflow export metadata
    obj["holoflow:category"] = "stage-floor"
    obj["holoflow:facet"]    = True

    # +Y-up for WebXR export (Blender is Z-up internally)
    obj.rotation_euler = (0, 0, 0)   # floor already in XY plane

    # GLB export
    bpy.ops.export_scene.gltf(
        filepath          = bpy.path.abspath(GLB_PATH),
        export_format     = 'GLB',
        export_draco_mesh_compression_enable = True,
        export_draco_mesh_compression_level  = 6,
        export_colors     = True,
        export_morph      = True,
        export_apply      = True,
        export_yup        = True,
        export_image_format = 'WEBP',
    )
    print(f"[GM] Exported → {GLB_PATH}")


build()
