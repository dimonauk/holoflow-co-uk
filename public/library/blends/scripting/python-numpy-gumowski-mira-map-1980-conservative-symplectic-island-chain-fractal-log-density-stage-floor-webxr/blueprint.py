"""
Gumowski–Mira Map (1980) — Conservative Symplectic Island Chains
================================================================
Blender 5.1 · Holoflow Studio · CC0

Source:  Gumowski I & Mira C (1980) "Recurrences and Discrete Dynamic Systems"
         Springer Lecture Notes in Mathematics 809  doi:10.1007/BFb0089165
         Mathematical results/equations are in the public domain.

TECHNIQUE:
  The Gumowski–Mira map is a 2-D area-preserving (symplectic) recurrence that
  produces coexisting KAM tori and chaotic seas in the same phase portrait.
  Unlike dissipative maps (Hénon, Lozi) it has no strange attractor — instead
  the KAM theorem guarantees closed invariant curves near elliptic fixed points,
  separated from the chaotic sea by a last invariant torus.  The rational
  nonlinearity G(x) saturates at ±2, bounding all orbits in a compact region.

MAP EQUATIONS:
    G(x)  =  μ·x  +  2·(1−μ)·x² / (1 + x²)          (rational twist)
    x'    =  y + G(x)                                    ... step (1)
    y'    = −x + G(x')       (uses updated x' from step 1)

JACOBIAN DETERMINANT = 1 (exactly):
  ∂x'/∂x = G'(x),   ∂x'/∂y = 1
  ∂y'/∂x = −1 + G'(x')·G'(x),   ∂y'/∂y = G'(x')
  det J  = G'(x)·G'(x') − 1·(−1 + G'(x')·G'(x)) = 1  ✓
  WHY det=1: the composition of two symplectic twist maps is symplectic.
  Consequence: Liouville theorem holds — no volume contraction, no global
  attractor, KAM tori coexist with Birkhoff chains and chaotic homoclinic zones.

G(x) NONLINEARITY RATIONALE:
  2(1−μ)x²/(1+x²) saturates to 2(1−μ) for |x|→∞, bounding the forcing.
  At x=0: G'(0)=μ — the twist rate at the origin.  μ=0: pure quadratic fold.
  μ=±1: G(x)=±x, the identity/flip — no chaos.  The sweet spot near μ≈−0.5
  gives rich island-chain structure with large chaotic zones.

SHAPE KEYS (four μ regimes):
  Basis   μ = −0.496   classical Gumowski–Mira galaxy
  SK_Ring μ = −0.120   flower / nested-ring topology, mostly KAM
  SK_Web  μ = −0.450   dense island-chain web, intermediate chaos
  SK_Fish μ = +0.008   large central elliptic island ("fish-eye" appearance)

Mesh: 128×128 = 16 384 vertices · 127×127 = 16 129 quad faces
Colour attribute: GM_Density  FLOAT_COLOR  POINT domain
N_ORBITS=200 × N_STEPS=25 000 = 5 M points per shape key
"""

import bpy, bmesh, math, numpy as np
import mathutils

# ── Named constants ──────────────────────────────────────────────────────────
MU_BASIS   = -0.496    # classical Gumowski–Mira galaxy
MU_RING    = -0.120    # flower / nested-ring topology
MU_WEB     = -0.450    # island-chain web
MU_FISH    =  0.008    # large elliptic island, "fish-eye"

N_ORBITS   = 200       # initial conditions (y₀=0, x₀ evenly spaced)
N_STEPS    = 25_000    # iterations per orbit (5 M total per shape key)
WARM       = 500       # transient discarded before recording

GRID_N     = 128       # histogram bins per axis → 128×128 = 16 384 vertices
X_RANGE    = 4.0       # phase-space ±x extent (all four μ regimes fit in ±3.5)
Y_RANGE    = 4.0       # phase-space ±y extent
ZSCALE     = 0.40      # peak Z height for log-density [m]
WORLD      = 4.0       # physical mesh half-side [m]

OBJ_NAME   = "GumowskiMira_Floor"
ATTR_NAME  = "GM_Density"
BLEND_NAME = "gumowski_mira_floor.blend"
GLB_NAME   = "gumowski_mira_floor.glb"

COBALT = (0.027, 0.159, 0.408, 1.0)   # sparse (low density)
AMBER  = (0.980, 0.620, 0.050, 1.0)   # dense  (high density)

SHAPE_KEYS = [
    ("Basis",   MU_BASIS),
    ("SK_Ring", MU_RING),
    ("SK_Web",  MU_WEB),
    ("SK_Fish", MU_FISH),
]


# ── Map & density ────────────────────────────────────────────────────────────

def _G(x: np.ndarray, mu: float) -> np.ndarray:
    """
    Gumowski–Mira nonlinearity G(x) = μx + 2(1-μ)x²/(1+x²).
    WHY vectorised: called N_STEPS × 2 times on arrays of N_ORBITS — numpy
    ufuncs give 100× speedup over a Python inner loop.
    """
    return mu * x + 2.0 * (1.0 - mu) * x * x / (1.0 + x * x)


def density_for(mu: float) -> np.ndarray:
    """
    Iterate N_ORBITS initial conditions from y₀=0 for N_STEPS steps,
    bin into GRID_N × GRID_N histogram, return log1p-normalised density.

    WHY start on the y=0 line: the x-axis is a Poincaré section that
    intersects every invariant set — KAM tori, separatrices, and the
    chaotic sea.  Varying x₀ sweeps from the elliptic centre to the
    outer chaotic boundary, giving a dense cross-section at minimal cost.
    """
    x = np.linspace(-X_RANGE * 0.95, X_RANGE * 0.95, N_ORBITS)
    y = np.zeros(N_ORBITS, dtype=np.float64)

    # warm-up: advance past transient without storing
    for _ in range(WARM):
        xn = y + _G(x, mu)
        x, y = xn, -x + _G(xn, mu)

    # record 5 M points (200 orbits × 25 000 steps)
    xs_all = np.empty(N_ORBITS * N_STEPS, dtype=np.float32)
    ys_all = np.empty(N_ORBITS * N_STEPS, dtype=np.float32)

    for step in range(N_STEPS):
        xn = y + _G(x, mu)
        yn = -x + _G(xn, mu)
        x, y = xn, yn
        base = step * N_ORBITS
        xs_all[base : base + N_ORBITS] = x
        ys_all[base : base + N_ORBITS] = y

    # np.histogram2d bins all 5 M points in one vectorised pass
    # WHY histogram2d not add.at: ~10× faster for large point counts
    H, _, _ = np.histogram2d(
        xs_all, ys_all,
        bins=GRID_N,
        range=[[-X_RANGE, X_RANGE], [-Y_RANGE, Y_RANGE]],
    )
    # H shape is (N_x_bins, N_y_bins); transpose to (row=y, col=x)
    raw = np.log1p(H.T.astype(np.float64))
    mx  = raw.max()
    return (raw / mx) if mx > 0.0 else raw


# ── Mesh ─────────────────────────────────────────────────────────────────────

def _verts_faces(density: np.ndarray):
    """
    Build (GRID_N × GRID_N) vertex list and (GRID_N-1)² quad face list.
    Vertex (row i, col j) → (x=xs[j], y=ys[i], z=density[i,j]*ZSCALE).
    """
    coords = np.linspace(-WORLD, WORLD, GRID_N)
    xs_g, ys_g = np.meshgrid(coords, coords)
    zs = density * ZSCALE

    verts = list(zip(xs_g.ravel().tolist(),
                     ys_g.ravel().tolist(),
                     zs.ravel().tolist()))

    R, C = GRID_N, GRID_N
    i, j = np.mgrid[0:R-1, 0:C-1]
    i0   = (i * C + j).ravel()
    faces_arr = np.column_stack([i0, i0 + 1, i0 + C + 1, i0 + C])
    faces = faces_arr.tolist()
    return verts, faces


def _add_shape_key(obj: bpy.types.Object, name: str, density: np.ndarray) -> None:
    """Append one shape key derived from a density field."""
    sk    = obj.shape_key_add(name=name, from_mix=False)
    verts, _ = _verts_faces(density)
    for idx, v in enumerate(verts):
        sk.data[idx].co = v


# ── Colour ───────────────────────────────────────────────────────────────────

def _apply_colour(obj: bpy.types.Object, density: np.ndarray) -> None:
    """
    Write cobalt→amber FLOAT_COLOR on POINT domain from Basis density.
    WHY FLOAT_COLOR not BYTE_COLOR: preserves linear-light HDR range needed
    for the holoflow_webxr_exporter's colour-correct WebP bake.
    """
    me   = obj.data
    attr = me.color_attributes.new(
        name=ATTR_NAME, type="FLOAT_COLOR", domain="POINT",
    )
    flat = density.ravel()
    cols: list[float] = []
    for t in flat:
        cols += [
            COBALT[0] + t * (AMBER[0] - COBALT[0]),
            COBALT[1] + t * (AMBER[1] - COBALT[1]),
            COBALT[2] + t * (AMBER[2] - COBALT[2]),
            1.0,
        ]
    attr.data.foreach_set("color", cols)


# ── Material ──────────────────────────────────────────────────────────────────

def _make_material(obj: bpy.types.Object) -> None:
    mat  = bpy.data.materials.new("GM_Floor_Mat")
    mat.use_nodes = True
    nt   = mat.node_tree
    nd, lk = nt.nodes, nt.links
    nd.clear()

    attr = nd.new("ShaderNodeAttribute");  attr.attribute_name = ATTR_NAME
    bsdf = nd.new("ShaderNodeBsdfPrincipled")
    emit = nd.new("ShaderNodeEmission")
    mix  = nd.new("ShaderNodeMixShader")
    out  = nd.new("ShaderNodeOutputMaterial")

    bsdf.inputs["Metallic"].default_value  = 0.30
    bsdf.inputs["Roughness"].default_value = 0.22
    emit.inputs["Strength"].default_value  = 1.8
    mix.inputs["Fac"].default_value        = 0.35   # 35 % emission

    lk.new(attr.outputs["Color"], bsdf.inputs["Base Color"])
    lk.new(attr.outputs["Color"], emit.inputs["Color"])
    lk.new(bsdf.outputs["BSDF"], mix.inputs[1])
    lk.new(emit.outputs["Emission"], mix.inputs[2])
    lk.new(mix.outputs["Shader"], out.inputs["Surface"])
    obj.data.materials.append(mat)


# ── Build & export ────────────────────────────────────────────────────────────

def build() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    # Basis geometry
    print(f"[GumowskiMira] Computing Basis (μ={MU_BASIS}) …")
    dens_basis   = density_for(MU_BASIS)
    verts, faces = _verts_faces(dens_basis)

    me = bpy.data.meshes.new(OBJ_NAME)
    me.from_pydata(verts, [], faces)
    me.validate()
    obj = bpy.data.objects.new(OBJ_NAME, me)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj

    _apply_colour(obj, dens_basis)
    obj.shape_key_add(name="Basis", from_mix=False)

    for sk_name, mu in SHAPE_KEYS[1:]:
        print(f"[GumowskiMira] Computing {sk_name} (μ={mu}) …")
        _add_shape_key(obj, sk_name, density_for(mu))

    _make_material(obj)

    # Holoflow metadata
    obj["holoflow:facet"]    = True
    obj["holoflow:category"] = "stage-floor"

    # +Y-up for WebXR: rotate mesh data 90° around X, apply transforms
    obj.data.transform(mathutils.Matrix.Rotation(math.pi / 2, 4, "X"))
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    import os
    blend_path = bpy.path.abspath(f"//{BLEND_NAME}")
    glb_path   = bpy.path.abspath(f"//{GLB_NAME}")
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
    print(f"[GumowskiMira] Done — '{OBJ_NAME}' {GRID_N**2}V {(GRID_N-1)**2}Q")
    print(f"[GumowskiMira] Saved  → {blend_path}")
    print(f"[GumowskiMira] Export → {glb_path}")


build()
