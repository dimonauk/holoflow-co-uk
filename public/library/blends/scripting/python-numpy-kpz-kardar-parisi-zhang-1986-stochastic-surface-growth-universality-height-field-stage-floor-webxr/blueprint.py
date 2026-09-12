"""
KPZ (Kardar–Parisi–Zhang) Equation 1986 — Stochastic Interface Growth,
EW vs KPZ Universality Class, Height-Field Stage Floor (Blender 5.1)
M. Kardar, G. Parisi & Y.-C. Zhang (1986) · bpy direct-data API · CC0
────────────────────────────────────────────────────────────────────────

Stochastic PDE governing the height h(x,y,t) of a growing interface:

    ∂h/∂t = ν ∇²h  +  (λ/2)|∇h|²  +  σ η(x,y,t)

ν > 0  : surface-tension / diffusion coefficient — smooths the interface.
λ      : lateral-growth nonlinearity — tilted patches grow faster, breaking
         up–down symmetry and driving the interface into the KPZ universality
         class distinct from the linear Edwards–Wilkinson (EW) class.
σ      : noise amplitude; η is Gaussian white noise with
         ⟨η(r,t) η(r′,t′)⟩ = δ²(r−r′) δ(t−t′).

Setting λ=0 reduces to the Edwards–Wilkinson equation.  In 2+1 dimensions:
  EW:  surface width W(t) ~ t^{β_EW}  β_EW ≈ 0.20,  χ_EW = 0
  KPZ: W(t) ~ t^{β_KPZ}               β_KPZ ≈ 0.24, χ_KPZ ≈ 0.39

The nonlinear term can be verified exactly in 1d via the Hopf–Cole
substitution ψ = exp(λh/2ν), which maps KPZ to the stochastic heat
equation ∂ψ/∂t = ν∇²ψ + (λσ/2ν)ψη — analytically tractable (Hairer 2014,
Fields Medal).  In 2+1 dimensions the fixed point is still under active
mathematical investigation (Dauvergne–Ortmann–Virág 2022 preprint).

Integration: Euler–Maruyama explicit on a 128×128 periodic grid.
  h ← h + DT [ν ∇²h + ½λ|∇h|²] + σ√DT · ξ    ξ ~ N(0,1) per site per step

Stability condition: DT ≤ DX²/(4ν).  With DX=1, ν=1 → DT ≤ 0.25.
We use DT = 0.02, a factor of 12.5 below the limit.

Spatial stencils (periodic BCs via np.roll):
  ∇²h[i,j] ≈ (N + E + S + W − 4C) / DX²      (5-point stencil)
  ∂h/∂x    ≈ (h[i+1,j] − h[i−1,j]) / (2DX)   (central differences)

Four shape keys span the universality-class parameter space:
  Basis      EW limit (λ=0, σ=0.5, t=4)  — correlated diffusive topography
  SK_KPZ     Full KPZ (λ=2.0, σ=0.5, t=4) — nonlinear ridge sharpening
  SK_Strong  Strong noise (λ=2.0, σ=2.0, t=4) — high-roughness texture
  SK_Long    Long run (λ=2.0, σ=0.5, t=20) — well-developed KPZ morphology

Colour attribute: KPZ_Height FLOAT_COLOR — cobalt (low) → amber (high).
Export: +Y-up rotation applied; Draco-6 compression; WebP textures.
"""

import sys
import numpy as np

try:
    import bpy
    from mathutils import Matrix
except ModuleNotFoundError:
    print("Run inside Blender (Scripting workspace ▶ Run Script).")
    sys.exit(1)

import pathlib

# ── named constants ───────────────────────────────────────────────────────────
NU          = 1.0    # diffusion / surface-tension coefficient
LAMBDA_KPZ  = 2.0    # KPZ lateral-growth nonlinearity
SIGMA_DEF   = 0.5    # noise amplitude — default
SIGMA_STR   = 2.0    # noise amplitude — strong-noise variant
N           = 128    # grid points per axis → N² = 16 384 vertices / 16 129 quads
DX          = 1.0    # spatial step size (natural units)
DT          = 0.02   # time step — satisfies diffusion CFL DT ≤ DX²/(4ν) = 0.25
N_SHORT     = 200    # steps for t = 4 (Basis, SK_KPZ, SK_Strong)
N_LONG      = 1000   # steps for t = 20 (SK_Long — longer evolution)
WORLD       = 4.0    # mesh half-extent in Blender world units
ZSCALE      = 0.45   # height-field amplitude multiplier
SEED        = 1986   # reproducibility seed (year of KPZ publication)
OBJ_NAME    = "KPZ_Floor"
ATTR_NAME   = "KPZ_Height"
COBALT      = (0.027, 0.159, 0.408, 1.0)
AMBER       = (0.980, 0.620, 0.050, 1.0)


# ── integration helpers ───────────────────────────────────────────────────────

def _laplacian(h: np.ndarray) -> np.ndarray:
    """5-point Laplacian with periodic BCs using np.roll.
    roll(-1) shifts the array so neighbour i+1 aligns with index i;
    roll(+1) gives neighbour i−1.  No boundary special-case needed."""
    return (
        np.roll(h,  1, axis=0) + np.roll(h, -1, axis=0) +
        np.roll(h,  1, axis=1) + np.roll(h, -1, axis=1) - 4.0 * h
    ) / (DX * DX)


def _grad_sq(h: np.ndarray) -> np.ndarray:
    """Central-difference |∇h|² = (∂h/∂x)² + (∂h/∂y)², periodic.
    Central differences cancel odd-order error; forward differences
    would introduce a systematic O(DX) tilt that corrupts β measurements."""
    gx = (np.roll(h, -1, axis=0) - np.roll(h, 1, axis=0)) / (2.0 * DX)
    gy = (np.roll(h, -1, axis=1) - np.roll(h, 1, axis=1)) / (2.0 * DX)
    return gx * gx + gy * gy


def _run(rng, n_steps: int, lam: float, sigma: float) -> np.ndarray:
    """Euler–Maruyama integration from flat h=0.
    Returns mean-subtracted height field so the mesh sits at z=0."""
    h       = np.zeros((N, N), dtype=np.float64)
    sqrt_dt = np.sqrt(DT)
    for _ in range(n_steps):
        noise = rng.standard_normal((N, N))
        h += DT * (NU * _laplacian(h) + 0.5 * lam * _grad_sq(h)) \
             + sigma * sqrt_dt * noise
    h -= h.mean()   # remove global drift; shape (not width) is unaffected
    return h


# ── mesh helpers ──────────────────────────────────────────────────────────────

def _sigma_scale(h: np.ndarray) -> np.ndarray:
    """σ-normalise then scale by ZSCALE so all shape keys use same z range."""
    return (h / (h.std() + 1e-12)) * ZSCALE


def _verts_faces(h: np.ndarray):
    """Build 128×128 quad mesh from height field h."""
    xs = np.linspace(-WORLD, WORLD, N)
    ys = np.linspace(-WORLD, WORLD, N)
    XG, YG = np.meshgrid(xs, ys, indexing="ij")
    ZG     = _sigma_scale(h)
    verts  = list(zip(XG.ravel(), YG.ravel(), ZG.ravel()))
    faces  = []
    for r in range(N - 1):
        for c in range(N - 1):
            a = r * N + c
            faces.append((a, a + 1, a + N + 1, a + N))
    return verts, faces, XG, YG


def _make_mesh(verts, faces) -> bpy.types.Object:
    me = bpy.data.meshes.new(OBJ_NAME)
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(OBJ_NAME, me)
    bpy.context.collection.objects.link(ob)
    ob.shape_key_add(name="Basis", from_mix=False)  # reference key
    return ob


def _add_shape_key(ob: bpy.types.Object, name: str, h: np.ndarray, XG, YG):
    """Add a shape key using foreach_set — 10–100× faster than per-vertex loop."""
    zs  = _sigma_scale(h).ravel().astype(np.float32)
    sk  = ob.shape_key_add(name=name, from_mix=False)
    buf = np.empty(N * N * 3, dtype=np.float32)
    buf[0::3] = XG.ravel()
    buf[1::3] = YG.ravel()
    buf[2::3] = zs
    sk.data.foreach_set("co", buf)


def _apply_colour(ob: bpy.types.Object, h_basis: np.ndarray):
    """KPZ_Height FLOAT_COLOR point attribute — cobalt (troughs) → amber (peaks)."""
    lo, hi = h_basis.min(), h_basis.max()
    t = ((h_basis - lo) / (hi - lo + 1e-12)).ravel().astype(np.float32)
    attr = ob.data.color_attributes.new(ATTR_NAME, "FLOAT_COLOR", "POINT")
    cols = np.empty(N * N * 4, dtype=np.float32)
    cols[0::4] = COBALT[0] + (AMBER[0] - COBALT[0]) * t
    cols[1::4] = COBALT[1] + (AMBER[1] - COBALT[1]) * t
    cols[2::4] = COBALT[2] + (AMBER[2] - COBALT[2]) * t
    cols[3::4] = 1.0
    attr.data.foreach_set("color", cols)


def _add_material(ob: bpy.types.Object):
    mat  = bpy.data.materials.new(f"{OBJ_NAME}_Mat")
    mat.use_nodes = True
    nt   = mat.node_tree;  nt.nodes.clear()
    atr  = nt.nodes.new("ShaderNodeAttribute");        atr.attribute_name = ATTR_NAME;  atr.location = (-420,  0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled");   bsdf.location = (-100,  60)
    bsdf.inputs["Metallic"].default_value  = 0.30
    bsdf.inputs["Roughness"].default_value = 0.25
    emit = nt.nodes.new("ShaderNodeEmission");         emit.location = (-100, -200); emit.inputs["Strength"].default_value = 1.6
    mix  = nt.nodes.new("ShaderNodeMixShader");        mix.location  = ( 200,    0); mix.inputs["Fac"].default_value = 0.35
    out  = nt.nodes.new("ShaderNodeOutputMaterial");   out.location  = ( 450,    0)
    lk   = nt.links
    lk.new(atr.outputs["Color"],       bsdf.inputs["Base Color"])
    lk.new(atr.outputs["Color"],       emit.inputs["Color"])
    lk.new(bsdf.outputs["BSDF"],       mix.inputs[1])
    lk.new(emit.outputs["Emission"],   mix.inputs[2])
    lk.new(mix.outputs["Shader"],      out.inputs["Surface"])
    ob.data.materials.append(mat)


def _export(ob: bpy.types.Object, blend_path: str, glb_path: str):
    """Apply +Y-up rotation then export .blend and .glb."""
    ob.rotation_euler[0] = -1.5707963267948966  # −90° around X → +Y up
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.transform_apply(rotation=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format="GLB",
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_image_format="WEBP",
        export_morph=True,
        export_colors=True,
    )


# ── main ──────────────────────────────────────────────────────────────────────

BASE = pathlib.Path(bpy.data.filepath).parent if bpy.data.filepath else pathlib.Path.cwd()

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()

# independent RNG instances, same seed → each variant starts identically
rng_ew     = np.random.default_rng(SEED)
rng_kpz    = np.random.default_rng(SEED)
rng_strong = np.random.default_rng(SEED)
rng_long   = np.random.default_rng(SEED)

h_ew     = _run(rng_ew,     N_SHORT, lam=0.0,        sigma=SIGMA_DEF)
h_kpz    = _run(rng_kpz,    N_SHORT, lam=LAMBDA_KPZ, sigma=SIGMA_DEF)
h_strong = _run(rng_strong, N_SHORT, lam=LAMBDA_KPZ, sigma=SIGMA_STR)
h_long   = _run(rng_long,   N_LONG,  lam=LAMBDA_KPZ, sigma=SIGMA_DEF)

verts, faces, XG, YG = _verts_faces(h_ew)
ob = _make_mesh(verts, faces)

_add_shape_key(ob, "SK_KPZ",    h_kpz,    XG, YG)
_add_shape_key(ob, "SK_Strong", h_strong, XG, YG)
_add_shape_key(ob, "SK_Long",   h_long,   XG, YG)

_apply_colour(ob, h_ew)
_add_material(ob)
ob["holoflow:facet"]    = True
ob["holoflow:category"] = "stage-floor"

blend_path = str(BASE / "kpz_floor.blend")
glb_path   = str(BASE / "kpz_floor.glb")
_export(ob, blend_path, glb_path)

print(f"✓ {blend_path}")
print(f"✓ {glb_path}")
print(f"  Basis (EW t=4):   W = {h_ew.std():.4f}")
print(f"  SK_KPZ (t=4):     W = {h_kpz.std():.4f}")
print(f"  SK_Strong (t=4):  W = {h_strong.std():.4f}")
print(f"  SK_Long (t=20):   W = {h_long.std():.4f}")
