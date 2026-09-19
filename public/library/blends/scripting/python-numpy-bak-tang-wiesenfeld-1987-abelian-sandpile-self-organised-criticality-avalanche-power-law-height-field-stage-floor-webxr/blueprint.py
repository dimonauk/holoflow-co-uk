"""
Bak–Tang–Wiesenfeld Abelian Sandpile — Self-Organised Criticality
Bak P, Tang C, Wiesenfeld K (1987) Phys Rev Lett 59(4):381-384
DOI 10.1103/PhysRevLett.59.381   (Public Domain — >35 yr)

THE PHYSICS
-----------
A 2D lattice of integer-valued sand heights. One grain is added
to a uniformly random site. When any site accumulates CRITICAL_HEIGHT
(= 4) or more grains it topples, losing 4 grains and giving 1 to each
of its four axis-aligned neighbours (with open boundaries, edge grains
are lost). Toppling cascades until all h < 4. This cascade is the
*avalanche*.

The remarkable result: no temperature, coupling constant, or external
field is tuned. The system self-organises to a stationary distribution
where avalanche sizes follow a power law without any parameter choice:

    P(S) ~ S^{-τ}        τ ≈ 1.11  (2D BTW, exact: Dhar 1999)
    P(T) ~ T^{-τ_t}      τ_t ≈ 1.50 (avalanche duration)
    Fractal dim D_f       D_f ≈ 2.75 (cluster Hausdorff dimension)

Compare the Ising model: Tc must be precisely tuned to see power laws.
In the BTW sandpile, criticality is the inevitable attractor.

THE ABELIAN PROPERTY (Dhar 1990, PRL 64:1613)
----------------------------------------------
Toppling is commutative: if sites A and B are both unstable, the final
stable configuration after all cascades is independent of whether A or
B topples first. This "Abelian" property (hence the name Abelian
Sandpile Model, ASM) means we can topple ALL unstable sites
simultaneously in a single NumPy step each iteration — the vectorised
relaxation is physically exact, not an approximation.

Proof sketch: each toppling operator Δ_i commutes with every other
because ∂h_j/∂(n topples of i) depends only on the lattice graph
topology, not on the order of operations.

SHAPE KEYS
----------
Basis       : critical-state height field  h ∈ {0, 1, 2, 3}
              Z = h/3 * Z_SCALE, colour cobalt(h=0) → amber(h=3)
SK_SmallAval: Basis heights + small-avalanche cluster members raised
              by Z_BOOST, revealing the fractal cluster geometry
SK_LargeAval: same but for a large (system-spanning) avalanche
SK_Maximal  : uniform h=3 everywhere (maximally stable initial state
              — all grains loaded, none toppled yet)

PARAMETERS (edit here; do not scatter magic numbers through the code)
"""

import bpy
import bmesh
import numpy as np
from numpy.random import default_rng

# ── lattice ────────────────────────────────────────────────────────────────────
N                 = 128         # grid points per side (128² = 16 384 sites)
CRITICAL_HEIGHT   = 4           # BTW threshold: h >= 4 → topple
N_GRAIN_SETTLE    = 1_200_000   # grains to reach stationary distribution
                                # criterion: >> 5 × N² ≈ 82 000
SMALL_AVAL_MIN    = 5           # size bracket for the "small" avalanche shape key
SMALL_AVAL_MAX    = 35
LARGE_AVAL_MIN    = 700         # size bracket for the "large" avalanche shape key
MAX_TRIES         = 60_000      # grain drops when hunting for a target avalanche
SEED              = 0xBAD5A1D

# ── mesh geometry ─────────────────────────────────────────────────────────────
WORLD_SCALE       = 4.0         # mesh spans [−WORLD_SCALE, WORLD_SCALE] in X and Y
Z_SCALE           = 0.35        # height of h=3 site above h=0 site
Z_BOOST           = 0.28        # extra raise for avalanche-cluster members

# ── material ───────────────────────────────────────────────────────────────────
ATTR_NAME         = "BTW_Height"
OBJ_NAME          = "btw_sandpile_floor"
MAT_NAME          = "MAT_btw_sandpile_floor"

COBALT = (0.027, 0.159, 0.557, 1.0)   # bare substrate (h = 0)
AMBER  = (0.980, 0.620, 0.050, 1.0)   # maximally loaded (h = 3)

# ── holoflow metadata ─────────────────────────────────────────────────────────
HOLOFLOW_CATEGORY = "stage-floor"
HOLOFLOW_FACET    = True


# ──────────────────────────────────────────────────────────────────────────────
# SIMULATION
# ──────────────────────────────────────────────────────────────────────────────

def _relax_step(h: np.ndarray) -> tuple[np.ndarray, bool]:
    """One simultaneous-toppling step.  Returns (h, changed)."""
    unstable = h >= CRITICAL_HEIGHT
    if not unstable.any():
        return h, False
    h = h - CRITICAL_HEIGHT * unstable.astype(np.int32)
    # Spread to the four neighbours; missing edge neighbours = open boundary.
    # WHY open: grains that fall off the edge drive the system toward
    # stationarity — without dissipation the pile would grow without limit.
    h[1:,  :] += unstable[:-1, :]
    h[:-1, :] += unstable[1:,  :]
    h[:,  1:] += unstable[:, :-1]
    h[:, :-1] += unstable[:, 1:]
    return h, True


def _relax(h: np.ndarray) -> np.ndarray:
    """Relax h in-place until stable.  Return boolean cluster mask."""
    cluster = np.zeros_like(h, dtype=bool)
    while True:
        unstable = h >= CRITICAL_HEIGHT
        if not unstable.any():
            break
        cluster |= unstable
        h -= CRITICAL_HEIGHT * unstable.astype(np.int32)
        h[1:,  :] += unstable[:-1, :]
        h[:-1, :] += unstable[1:,  :]
        h[:,  1:] += unstable[:, :-1]
        h[:, :-1] += unstable[:, 1:]
    return cluster


def run_to_criticality(rng: np.random.Generator) -> np.ndarray:
    """Drop N_GRAIN_SETTLE grains and relax after each; return stable height field.

    The stationary ("sandpile") measure is reached after roughly 5 × N²
    grains (Dhar 1990 estimate). N_GRAIN_SETTLE = 1.2 M > 14 × N² gives
    a well-equilibrated sample.
    """
    h = np.zeros((N, N), dtype=np.int32)
    sites_i = rng.integers(0, N, size=N_GRAIN_SETTLE)
    sites_j = rng.integers(0, N, size=N_GRAIN_SETTLE)
    for k in range(N_GRAIN_SETTLE):
        h[sites_i[k], sites_j[k]] += 1
        _relax(h)
    return h


def find_avalanche(
    h_start: np.ndarray,
    rng: np.random.Generator,
    min_size: int,
    max_size: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Hunt for a grain addition causing an avalanche in [min_size, max_size].

    Works on a copy so h_start is not modified.  Returns (h_after, cluster).
    h_work is updated after each grain so subsequent drops continue from a
    valid critical state — this keeps the search stationary.
    """
    h_work = h_start.copy()
    sites_i = rng.integers(0, N, size=MAX_TRIES)
    sites_j = rng.integers(0, N, size=MAX_TRIES)
    for k in range(MAX_TRIES):
        h_test = h_work.copy()
        h_test[sites_i[k], sites_j[k]] += 1
        cluster = _relax(h_test)
        size = int(cluster.sum())
        if min_size <= size <= max_size:
            return h_test, cluster
        # Keep h_work in the stationary regime after each attempted drop.
        h_work[sites_i[k], sites_j[k]] += 1
        _relax(h_work)
    # Fallback: return current state with empty cluster (should not trigger).
    return h_work, np.zeros((N, N), dtype=bool)


# ──────────────────────────────────────────────────────────────────────────────
# MESH BUILDER
# ──────────────────────────────────────────────────────────────────────────────

def _h_to_z(h: np.ndarray) -> np.ndarray:
    """Map h ∈ {0,1,2,3} → world-space Z."""
    return (h.astype(np.float32) / (CRITICAL_HEIGHT - 1)) * Z_SCALE


def _build_base_mesh(h: np.ndarray) -> bpy.types.Object:
    """N×N quad grid from height field; return Object linked into current scene."""
    xs = np.linspace(-WORLD_SCALE, WORLD_SCALE, N)
    ys = np.linspace(-WORLD_SCALE, WORLD_SCALE, N)
    xx, yy = np.meshgrid(xs, ys, indexing="ij")
    zz = _h_to_z(h)

    verts = np.stack([xx.ravel(), yy.ravel(), zz.ravel()], axis=1).tolist()
    faces = []
    for ix in range(N - 1):
        for iy in range(N - 1):
            v0 = ix * N + iy
            faces.append((v0, v0 + N, v0 + N + 1, v0 + 1))

    mesh = bpy.data.meshes.new(OBJ_NAME)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(OBJ_NAME, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def _set_vertex_colour(obj: bpy.types.Object, h: np.ndarray) -> None:
    """FLOAT_COLOR attribute: cobalt (h=0) → amber (h=3) per vertex."""
    mesh = obj.data
    if ATTR_NAME in mesh.attributes:
        mesh.attributes.remove(mesh.attributes[ATTR_NAME])
    attr = mesh.attributes.new(name=ATTR_NAME, type="FLOAT_COLOR", domain="POINT")

    t = h.ravel().astype(np.float32) / (CRITICAL_HEIGHT - 1)
    colours = np.empty(N * N * 4, dtype=np.float32)
    colours[0::4] = COBALT[0] + t * (AMBER[0] - COBALT[0])
    colours[1::4] = COBALT[1] + t * (AMBER[1] - COBALT[1])
    colours[2::4] = COBALT[2] + t * (AMBER[2] - COBALT[2])
    colours[3::4] = 1.0
    attr.data.foreach_set("color", colours)
    mesh.update()


def _add_shape_key(
    obj: bpy.types.Object,
    name: str,
    h: np.ndarray,
    cluster: np.ndarray | None = None,
) -> None:
    """Add shape key; cluster members raised by Z_BOOST over their h-height.

    WHY Z_BOOST? The avalanche cluster is a fractal with D_f ≈ 2.75.
    Elevating the cluster above the background height field makes the
    fractal boundary directly readable in the 3-D viewport — the viewer
    sees an island whose silhouette encodes the power-law geometry.
    """
    if obj.data.shape_keys is None:
        obj.shape_key_add(name="Basis", from_mix=False)
    sk = obj.shape_key_add(name=name, from_mix=False)

    xs = np.linspace(-WORLD_SCALE, WORLD_SCALE, N)
    ys = np.linspace(-WORLD_SCALE, WORLD_SCALE, N)
    xx, yy = np.meshgrid(xs, ys, indexing="ij")
    zz = _h_to_z(h).ravel()
    if cluster is not None:
        zz = zz + cluster.ravel().astype(np.float32) * Z_BOOST

    co = np.empty(N * N * 3, dtype=np.float32)
    co[0::3] = xx.ravel()
    co[1::3] = yy.ravel()
    co[2::3] = zz
    sk.data.foreach_set("co", co)
    obj.data.update()


def _build_material(obj: bpy.types.Object) -> None:
    """Attribute → Principled BSDF + Emission MixShader — standard studio recipe."""
    mat = bpy.data.materials.new(MAT_NAME)
    mat.use_nodes = True
    tree = mat.node_tree
    for node in list(tree.nodes):
        tree.nodes.remove(node)

    out  = tree.nodes.new("ShaderNodeOutputMaterial")
    mix  = tree.nodes.new("ShaderNodeMixShader")
    bsdf = tree.nodes.new("ShaderNodeBsdfPrincipled")
    emit = tree.nodes.new("ShaderNodeEmission")
    attr = tree.nodes.new("ShaderNodeAttribute")

    attr.attribute_name                   = ATTR_NAME
    bsdf.inputs["Metallic"].default_value  = 0.60
    bsdf.inputs["Roughness"].default_value = 0.18
    emit.inputs["Strength"].default_value  = 1.4
    mix.inputs["Fac"].default_value        = 0.35

    L = tree.links.new
    L(attr.outputs["Color"], bsdf.inputs["Base Color"])
    L(attr.outputs["Color"], emit.inputs["Color"])
    L(bsdf.outputs["BSDF"],  mix.inputs[1])
    L(emit.outputs["Emission"], mix.inputs[2])
    L(mix.outputs["Shader"],  out.inputs["Surface"])

    (obj.data.materials.append if not obj.data.materials else
     obj.data.materials.__setitem__)(0 if obj.data.materials else None, mat) \
        if obj.data.materials else obj.data.materials.append(mat)


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

rng = default_rng(SEED)

print("BTW sandpile: running to criticality …")
h_crit = run_to_criticality(rng)

print("BTW sandpile: hunting small avalanche …")
h_small, cl_small = find_avalanche(h_crit, rng, SMALL_AVAL_MIN, SMALL_AVAL_MAX)

print(f"BTW sandpile: small avalanche size = {cl_small.sum()}")

print("BTW sandpile: hunting large avalanche …")
h_large, cl_large = find_avalanche(h_small, rng, LARGE_AVAL_MIN, N * N)

print(f"BTW sandpile: large avalanche size = {cl_large.sum()}")

h_max = np.full((N, N), CRITICAL_HEIGHT - 1, dtype=np.int32)

# Build mesh from critical state (Basis heights)
obj = _build_base_mesh(h_crit)
_set_vertex_colour(obj, h_crit)

_add_shape_key(obj, "SK_SmallAval", h_crit, cl_small)
_add_shape_key(obj, "SK_LargeAval", h_crit, cl_large)
_add_shape_key(obj, "SK_Maximal",   h_max,  None)

_build_material(obj)

obj["holoflow:category"] = HOLOFLOW_CATEGORY
obj["holoflow:facet"]    = HOLOFLOW_FACET

# +Y-up studio convention (WebXR coordinate system)
import mathutils
obj.data.transform(mathutils.Matrix.Rotation(3.14159265 / 2, 4, "X"))
obj.data.update()

import os
blend_path = bpy.path.abspath(f"//{OBJ_NAME}.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)

glb_path = blend_path.replace(".blend", ".glb")
bpy.ops.export_scene.gltf(
    filepath                             = glb_path,
    export_format                        = "GLB",
    export_draco_mesh_compression_enable = True,
    export_draco_mesh_compression_level  = 6,
    export_image_format                  = "WEBP",
    export_morph                         = True,
    export_colors                        = True,
    export_apply                         = True,
    use_selection                        = False,
)
print(f"Saved  {blend_path}")
print(f"Export {glb_path}")
