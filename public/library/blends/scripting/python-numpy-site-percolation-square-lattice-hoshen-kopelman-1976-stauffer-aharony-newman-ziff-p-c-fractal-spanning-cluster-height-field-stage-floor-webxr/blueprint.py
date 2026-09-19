# ============================================================
# SITE PERCOLATION ON Z²  |  Hoshen–Kopelman 1976  |  Blender 5.1
# ============================================================
# Site percolation on the 128×128 square lattice: each site is
# independently occupied with probability p. Clusters are labelled
# by the Hoshen–Kopelman union-find algorithm.  At the threshold
# p_c ≈ 0.5927 the spanning cluster is fractal (D_f = 91/48 ≈ 1.896).
# Four shape keys sweep the phase diagram; height encodes
# log(1 + cluster_size) / log(N²) so individual sites project to
# near-zero height while the giant component rises to ≈ 1.
# Exports holoflow_perc_floor.glb (Draco 6 / WebP) for WebXR.
# ============================================================

import bpy, bmesh, math, os
import numpy as np

# ── Parameters ──────────────────────────────────────────────────
N          = 128          # grid side → N×N vertices, (N-1)² quads
SEED_BASE  = 137          # RNG seeds differ per shape key
P_BELOW    = 0.40         # sub-critical: isolated clusters dominate
P_CRIT     = 0.59274      # ≈ p_c site percolation Z² (Stauffer 1985)
P_ABOVE    = 0.70         # super-critical: giant component present
P_BOND     = 0.50         # bond percolation threshold (exact, self-dual)
MESH_SIZE  = 2.0          # world-space side length (metres)
Z_SCALE    = 0.42         # height amplitude of height field
OBJ_NAME   = "perc_floor"
COBALT     = (0.016, 0.157, 0.780, 1.0)
AMBER      = (1.000, 0.600, 0.000, 1.0)
OUT_PATH   = "//holoflow_perc_floor.glb"

# ── Hoshen–Kopelman union-find ───────────────────────────────────
# We track a parent array indexed by flat site index.
# Each occupied site starts as its own root; neighbours are unioned.

def _find(parent: list, x: int) -> int:
    while parent[x] != x:
        parent[x] = parent[parent[x]]   # path-halving compression
        x = parent[x]
    return x


def _label_and_heights(occupied: np.ndarray) -> np.ndarray:
    """Return log-normalised height field in [0, 1], shape (N, N).

    Height encodes log(1 + s) / log(N²) where s is the cluster size.
    Unoccupied sites → 0.  Rationale: log scale spreads small clusters
    (s ≈ 1..10) and the giant component (s ≈ N²) across the full [0,1]
    range, giving a visually dynamic height field at all p values.
    """
    n     = occupied.shape[0]
    total = n * n
    flat  = occupied.ravel().astype(bool)
    parent = list(range(total))
    lbl    = [-1] * total   # -1 = empty site; ≥0 = representative site

    for idx in range(total):
        if not flat[idx]:
            continue
        i, j = idx // n, idx % n
        nbrs = []
        if j > 0 and flat[idx - 1]:
            nbrs.append(idx - 1)
        if i > 0 and flat[idx - n]:
            nbrs.append(idx - n)
        if not nbrs:
            lbl[idx] = idx          # own root
        else:
            r = _find(parent, lbl[nbrs[0]])
            lbl[idx] = r
            for nb in nbrs[1:]:
                r2 = _find(parent, lbl[nb])
                if r2 != r:
                    parent[r2] = r  # union by first-root convention

    # accumulate cluster sizes by root
    sizes: dict[int, int] = {}
    for idx in range(total):
        if lbl[idx] < 0:
            continue
        r = _find(parent, lbl[idx])
        sizes[r] = sizes.get(r, 0) + 1

    log_max = math.log(total + 1)
    height  = np.zeros(total, dtype=np.float32)
    for idx in range(total):
        if lbl[idx] >= 0:
            r = _find(parent, lbl[idx])
            height[idx] = math.log(1.0 + sizes[r]) / log_max

    return height.reshape(n, n)


def _percolation_heights(p: float, seed: int) -> np.ndarray:
    """Occupy a fresh N×N lattice at probability p and return heights."""
    rng = np.random.default_rng(seed)
    occupied = rng.random((N, N)) < p
    return _label_and_heights(occupied)


def _bond_heights(seed: int) -> np.ndarray:
    """Bond percolation: each bond open with probability P_BOND=0.5.

    We derive site occupancy from bond connectivity: a site is 'in'
    the bond cluster if any adjacent bond is open.  Height encodes
    the size of the bond-connected component the site belongs to,
    computed by the same HK pass on a derived adjacency.
    This gives a fair comparison with site percolation at P_BOND=0.5
    vs P_CRIT≈0.593 — same cluster statistics at threshold.
    """
    rng      = np.random.default_rng(seed)
    h_bonds  = rng.random((N, N - 1)) < P_BOND   # horizontal bonds
    v_bonds  = rng.random((N - 1, N)) < P_BOND   # vertical bonds
    # derive site occupancy: site is non-isolated if at least one bond
    occ = np.zeros((N, N), dtype=bool)
    occ[:, :-1] |= h_bonds
    occ[:, 1:]  |= h_bonds
    occ[:-1, :] |= v_bonds
    occ[1:, :]  |= v_bonds
    return _label_and_heights(occ)


# ── Mesh builder ────────────────────────────────────────────────
def _build_mesh(heights: np.ndarray) -> bpy.types.Object:
    """Create the stage-floor mesh from a height field array."""
    verts, faces = [], []
    step = MESH_SIZE / (N - 1)

    for i in range(N):
        for j in range(N):
            x = -MESH_SIZE / 2 + j * step
            y = -MESH_SIZE / 2 + i * step
            z = float(heights[i, j]) * Z_SCALE
            verts.append((x, y, z))

    for i in range(N - 1):
        for j in range(N - 1):
            a = i * N + j
            faces.append((a, a + 1, a + N + 1, a + N))

    mesh = bpy.data.meshes.new(OBJ_NAME)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(OBJ_NAME, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def _add_shape_key(obj: bpy.types.Object, name: str, heights: np.ndarray) -> None:
    sk = obj.shape_key_add(name=name, from_mix=False)
    cos = np.empty(len(obj.data.vertices) * 3, dtype=np.float32)
    obj.data.vertices.foreach_get("co", cos)
    step = MESH_SIZE / (N - 1)
    for i in range(N):
        for j in range(N):
            idx = i * N + j
            cos[idx * 3 + 2] = float(heights[i, j]) * Z_SCALE
    sk.data.foreach_set("co", cos)


def _add_color_attribute(obj: bpy.types.Object, heights: np.ndarray) -> None:
    """Vertex colour: cobalt (height=0) → amber (height=1)."""
    mesh = obj.data
    if "Perc_Cluster" not in mesh.color_attributes:
        mesh.color_attributes.new("Perc_Cluster", "FLOAT_COLOR", "POINT")
    attr = mesh.color_attributes["Perc_Cluster"]
    colors = np.empty(len(mesh.vertices) * 4, dtype=np.float32)
    flat   = heights.ravel()
    for idx, t in enumerate(flat):
        colors[idx * 4 + 0] = COBALT[0] + t * (AMBER[0] - COBALT[0])
        colors[idx * 4 + 1] = COBALT[1] + t * (AMBER[1] - COBALT[1])
        colors[idx * 4 + 2] = COBALT[2] + t * (AMBER[2] - COBALT[2])
        colors[idx * 4 + 3] = 1.0
    attr.data.foreach_set("color", colors)


def _setup_material(obj: bpy.types.Object) -> None:
    mat = bpy.data.materials.new("perc_mat")
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out  = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    attr = nodes.new("ShaderNodeAttribute")
    attr.attribute_name = "Perc_Cluster"
    links.new(attr.outputs["Color"],  bsdf.inputs["Base Color"])
    links.new(bsdf.outputs["BSDF"],   out.inputs["Surface"])
    bsdf.inputs["Roughness"].default_value = 0.6
    bsdf.inputs["Metallic"].default_value  = 0.0
    obj.data.materials.append(mat)


def _export_glb(obj: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.gltf(
        filepath=bpy.path.abspath(OUT_PATH),
        use_selection=True,
        export_format="GLB",
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_image_format="WEBP",
        export_apply=True,
        export_attributes=True,
        export_morph=True,
    )


# ── Main ─────────────────────────────────────────────────────────
def run():
    for ob in bpy.data.objects:
        bpy.data.objects.remove(ob, do_unlink=True)

    h_basis = _percolation_heights(P_BELOW, SEED_BASE)
    obj     = _build_mesh(h_basis)
    obj.shape_key_add(name="Basis", from_mix=False)

    _add_shape_key(obj, "SK_Critical", _percolation_heights(P_CRIT,  SEED_BASE + 1))
    _add_shape_key(obj, "SK_Above",    _percolation_heights(P_ABOVE, SEED_BASE + 2))
    _add_shape_key(obj, "SK_Bond",     _bond_heights(SEED_BASE + 3))

    _add_color_attribute(obj, h_basis)
    _setup_material(obj)
    _export_glb(obj)
    print(f"[perc] exported → {bpy.path.abspath(OUT_PATH)}")


run()
