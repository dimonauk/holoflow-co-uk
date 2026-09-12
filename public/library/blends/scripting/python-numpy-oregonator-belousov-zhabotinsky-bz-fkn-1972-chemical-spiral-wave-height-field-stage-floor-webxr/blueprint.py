"""
Oregonator BZ Reaction-Diffusion  —  Field-Körös-Noyes 1972
Belousov-Zhabotinsky chemical oscillator · self-organising spiral waves
128×128 = 16384 V / 16129 Q  ·  height-field stage floor for WebXR

Equations  (Tyson-Fife 1980 dimensionless two-variable reduction):
    ε ∂u/∂t = u(1 − u) − f·v·(u − q)/(u + q)  + Du ∇²u
         ∂v/∂t = u − v

  u ∈ [0, 1]  : HBrO₂ (autocatalytic activator, 'the spark')
  v ∈ [0, 1]  : Ce⁴⁺  (inhibitor, 'the brake')
  ε = 0.04    : fast/slow timescale ratio  (ε ≪ 1 ⟹ excitable/oscillatory)
  f = 1.4     : stoichiometric factor      (controls spiral wavelength)
  q = 0.002   : rate constant ratio        (sets pulse-front sharpness)
  Du = 1.0    : activator diffusivity      (inhibitor v does not diffuse in gel)

Stability  (explicit Euler):
  Reaction stiffness near u ≈ q: |λ_max| ≈ 2q·f·v / (ε(u+q)²) ≤ 850 at rest.
  Euler stable iff dt × 850 < 2  →  dt < 0.00235.  Using DT = 0.002.
  Diffusion  stable iff dt < dx²/(4Du) = 0.25  ← not binding.

Shape keys:
  Basis   : f=1.4 ε=0.04  broken-wave IC      t=40  four-armed spiral
  SK_Fast : f=1.4 ε=0.02  broken-wave IC      t=40  narrower, faster arms
  SK_Rings: f=1.4 ε=0.04  pacemaker disk IC   t=40  concentric target rings
  SK_Meander: f=1.6 ε=0.04 random-noise IC   t=60  spiral breakup/turbulence

Blender 5.1 · CC0 (public-domain mathematics)
Source: Field R J, Körös E, Noyes R M (1972) JACS 94 8649–8664
        Tyson J J, Fife P C (1980) J Chem Phys 73 2224–2237
"""

import bpy, bmesh, numpy as np
from mathutils import Matrix

# ── parameters ───────────────────────────────────────────────────────────────
N       = 128          # grid points per axis
DX      = 1.0          # spatial step (dimensionless)
DT      = 0.002        # time step  (within explicit-Euler stability bound)
D_U     = 1.0          # activator diffusivity
F_BASE  = 1.4          # stoichiometric factor  (Basis / SK_Fast / SK_Rings)
F_HIGH  = 1.6          # higher f  →  SK_Meander (closer to oscillation edge)
EPS_BASE  = 0.04       # ε  standard BZ timescale
EPS_TIGHT = 0.02       # ε  half → twice-as-fast oscillation, tighter spirals
Q       = 0.002        # rate constant ratio
ZSCALE  = 0.40         # vertical scale in metres
WORLD   = 4.0          # floor half-width → 8 m × 8 m
OBJ_NAME = "bz_oregonator_floor"
GLB_PATH = "//bz_oregonator_floor.glb"

N_BASIS   = 20_000   # dt × N = t = 40
N_FAST    = 20_000
N_RINGS   = 20_000
N_MEANDER = 30_000   # t = 60  →  more chaotic pattern


# ── numerics ─────────────────────────────────────────────────────────────────
def _lap(u: np.ndarray) -> np.ndarray:
    """5-point periodic Laplacian — WHY periodic: toroidal domain avoids
    boundary artefacts that would pin spiral tips to edges."""
    return (
        np.roll(u, 1, 0) + np.roll(u, -1, 0) +
        np.roll(u, 1, 1) + np.roll(u, -1, 1) - 4.0 * u
    ) / (DX * DX)


def _react_u(u, v, eps, f):
    """Fast activator kinetics.  WHY divided by ε: the singular perturbation
    structure means u equilibrates on the O(ε) fast scale; the (u−q)/(u+q)
    factor is the 'gate' — zero at u=q, full at u≫q — that creates the
    threshold separating excitation from recovery."""
    return (u * (1.0 - u) - f * v * (u - Q) / (u + Q)) / eps


def _step(u, v, eps, f):
    ru = _react_u(u, v, eps, f)
    rv = u - v
    u2 = np.clip(u + DT * (ru + D_U * _lap(u)), 0.0, 1.0)
    v2 = np.clip(v + DT * rv,                   0.0, 1.0)
    return u2, v2


def run(u, v, n_steps, eps=EPS_BASE, f=F_BASE):
    for _ in range(n_steps):
        u, v = _step(u, v, eps, f)
    return u, v


# ── initial conditions ───────────────────────────────────────────────────────
def _rest():
    """Resting state u* ≈ 0.012, v* ≈ 0.012 (root of cubic nullcline v=u)."""
    # Algebraic solution: u² + u(f-1+q) − q(f+1) = 0  with v=u on v-nullcline
    a, b, c = 1.0, F_BASE - 1.0 + Q, -(Q * (F_BASE + 1.0))
    u_star = (-b + np.sqrt(b * b - 4.0 * a * c)) / (2.0 * a)
    return u_star


def ic_broken_wave(rng, noise=0.01):
    """Canonical spiral IC: u = 1 in left half, v = 1 in bottom half.
    The four quadrant-boundary crossings each seed one spiral tip — WHY:
    the BZ dynamics requires a broken wavefront for topological winding."""
    x = np.arange(N)
    _, Y = np.meshgrid(x, x, indexing='ij')
    Xg = np.arange(N)[:, None]
    u = np.where(Xg < N // 2, 1.0, _rest()) + rng.uniform(-noise, noise, (N, N))
    v = np.where(Y < N // 2, 1.0, _rest()) + rng.uniform(-noise, noise, (N, N))
    return np.clip(u, 0, 1), np.clip(v, 0, 1)


def ic_pacemaker(rng, radius=10, noise=0.005):
    """Central excited disk — WHY: one pacemaker region that fires first
    then spreads as concentric 'target' rings, the BZ equivalent of a stone
    dropped in a pond."""
    c = N // 2
    ii, jj = np.mgrid[0:N, 0:N]
    r2 = (ii - c) ** 2 + (jj - c) ** 2
    u_r = _rest()
    u = np.where(r2 < radius ** 2, 0.85, u_r) + rng.uniform(-noise, noise, (N, N))
    v = np.full((N, N), u_r) + rng.uniform(-noise * 0.5, noise * 0.5, (N, N))
    return np.clip(u, 0, 1), np.clip(v, 0, 1)


def ic_random(rng, amp=0.25):
    """Broad random perturbation — WHY: seeds many spiral tips spontaneously,
    leading to competing domains and eventual spiral breakup (chemical turbulence)
    when f is raised toward the oscillation-edge bifurcation."""
    u_r = _rest()
    u = np.clip(u_r + rng.uniform(0, amp, (N, N)), 0, 1)
    v = np.clip(u_r + rng.uniform(0, amp * 0.5, (N, N)), 0, 1)
    return u, v


# ── geometry ──────────────────────────────────────────────────────────────────
def _verts_faces(u_field):
    xs = np.linspace(-WORLD, WORLD, N)
    XG, YG = np.meshgrid(xs, xs, indexing='ij')
    ZG = u_field * ZSCALE
    verts = list(zip(XG.ravel(), YG.ravel(), ZG.ravel()))
    faces = [(i * N + j, (i + 1) * N + j,
              (i + 1) * N + (j + 1), i * N + (j + 1))
             for i in range(N - 1) for j in range(N - 1)]
    return verts, faces


def _add_sk(obj, u_field, name):
    sk = obj.shape_key_add(name=name, from_mix=False)
    xs = np.linspace(-WORLD, WORLD, N)
    XG, YG = np.meshgrid(xs, xs, indexing='ij')
    ZG = u_field * ZSCALE
    buf = np.empty((N * N, 3))
    buf[:, 0] = XG.ravel()
    buf[:, 1] = YG.ravel()
    buf[:, 2] = ZG.ravel()
    sk.data.foreach_set("co", buf.ravel())


def _apply_colour(mesh, u_field):
    """BZ_Conc FLOAT_COLOR — cobalt (u=0) → amber (u=1).
    WHY: blue 'wave backs' and golden 'wave fronts' mirror the visual of
    real BZ experiments using ferroin indicator dye."""
    cobalt = np.array([0.027, 0.159, 0.408, 1.0])
    amber  = np.array([0.980, 0.620, 0.050, 1.0])
    u_flat = u_field.ravel()[:, None]
    colours = cobalt + u_flat * (amber - cobalt)
    attr = mesh.attributes.new("BZ_Conc", "FLOAT_COLOR", "POINT")
    attr.data.foreach_set("color", colours.ravel())


def _make_material(obj):
    mat = bpy.data.materials.new("BZ_Spiral")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out  = nt.nodes.new("ShaderNodeOutputMaterial")
    mix  = nt.nodes.new("ShaderNodeMixShader")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    emit = nt.nodes.new("ShaderNodeEmission")
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = "BZ_Conc"
    bsdf.inputs["Roughness"].default_value = 0.65
    emit.inputs["Strength"].default_value = 1.4
    mix.inputs["Fac"].default_value = 0.35
    nt.links.new(attr.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(attr.outputs["Color"], emit.inputs["Color"])
    nt.links.new(bsdf.outputs["BSDF"],  mix.inputs[1])
    nt.links.new(emit.outputs["Emission"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"],  out.inputs["Surface"])
    obj.data.materials.append(mat)


# ── main ─────────────────────────────────────────────────────────────────────
def main():
    rng = np.random.default_rng(seed=1972)   # FKN paper year

    print("BZ Oregonator: Basis (broken-wave, ε=0.04, f=1.4) …")
    u, v = ic_broken_wave(rng)
    u, v = run(u, v, N_BASIS, eps=EPS_BASE, f=F_BASE)
    u_basis = u.copy()

    print("SK_Fast (ε=0.02) …")
    u, v = ic_broken_wave(np.random.default_rng(1972))
    u, v = run(u, v, N_FAST, eps=EPS_TIGHT, f=F_BASE)
    u_fast = u.copy()

    print("SK_Rings (pacemaker) …")
    u, v = ic_pacemaker(np.random.default_rng(2024))
    u, v = run(u, v, N_RINGS, eps=EPS_BASE, f=F_BASE)
    u_rings = u.copy()

    print("SK_Meander (random, f=1.6) …")
    u, v = ic_random(np.random.default_rng(1951))
    u, v = run(u, v, N_MEANDER, eps=EPS_BASE, f=F_HIGH)
    u_meander = u.copy()

    # build mesh from Basis
    verts, faces = _verts_faces(u_basis)
    mesh = bpy.data.meshes.new(OBJ_NAME)
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    _apply_colour(mesh, u_basis)

    # object
    if OBJ_NAME in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[OBJ_NAME], do_unlink=True)
    obj = bpy.data.objects.new(OBJ_NAME, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # shape keys
    obj.shape_key_add(name="Basis", from_mix=False)
    _add_sk(obj, u_fast,    "SK_Fast")
    _add_sk(obj, u_rings,   "SK_Rings")
    _add_sk(obj, u_meander, "SK_Meander")

    _make_material(obj)

    # holoflow metadata
    obj["holoflow:facet"]    = True
    obj["holoflow:category"] = "stage-floor"

    # orient for WebXR (+Y up)
    obj.rotation_euler = (-1.5707963, 0, 0)
    bpy.ops.object.transform_apply(rotation=True)

    # GLB export
    bpy.ops.export_scene.gltf(
        filepath=bpy.path.abspath(GLB_PATH),
        export_format="GLB",
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_image_format="WEBP",
        export_morph=True,
        export_colors=True,
        use_selection=True,
    )
    print(f"Done → {GLB_PATH}")


if __name__ == "__main__":
    main()
