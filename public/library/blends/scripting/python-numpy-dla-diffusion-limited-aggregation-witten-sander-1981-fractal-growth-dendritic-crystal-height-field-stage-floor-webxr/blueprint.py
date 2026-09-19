"""
Diffusion-Limited Aggregation — Witten & Sander 1981
T. A. Witten Jr. and L. M. Sander,
"Diffusion-Limited Aggregation, a Kinetic Critical Phenomenon,"
Physical Review Letters 47(19):1400–1403 (1981).
DOI 10.1103/PhysRevLett.47.1400  (Public Domain — >40 years)

TECHNIQUE
---------
A single seed particle sits at the centre of a 128×128 grid. Walkers are
launched one at a time from a circle of radius r_launch = r_cluster + 5.
Each walker takes a random step (N/S/E/W) until it either sticks to a
grid-neighbour of the existing cluster, or wanders past r_kill = r_launch + 20
and is discarded. The cluster grows via this stochastic rule into a fractal
dendritic structure with Hausdorff dimension D_f ≈ 1.71 (Meakin 1983).

WHY NOT VECTORISE THE WALK: each particle's path length is random and
statistically O(r²) steps — particles near the edge of a large cluster may
walk thousands of steps before sticking. Vectorising over simultaneous
walkers risks cache thrashing without simplifying the per-step adjacency
check. A tight Python loop with numpy.random.integers is fast enough for
2 000–3 500 particles on a 128×128 grid in under 30 seconds.

WHY ADAPTIVE r_launch: launching from a fixed large circle when the cluster
is still tiny wastes steps on long straight runs. Tracking r_cluster lets
the walker start just 5 cells beyond the current dendritic tips.

HEIGHT ENCODING: arrival_order[i,j] = (num_stuck)/N_PARTICLES ∈ (0,1].
Empty cells stay 0. This means the YOUNGEST tips are the highest points
(amber); the original seed is the lowest cluster point (cobalt), revealing
the temporal growth history of each branch.

PARAMETERS — tune here, not scattered through the body.
"""

import bpy
import bmesh
import math
import numpy as np

# ── simulation ─────────────────────────────────────────────────────────────────
N            = 128        # grid resolution (N×N height-field vertices)
N_BASIS      = 2000       # particles for Basis shape key
N_SMALL      = 400        # particles for SK_Small (early growth)
N_MED        = 1200       # particles for SK_Mid (mid growth)
SEED         = 42         # NumPy RNG seed for reproducibility

# ── geometry ───────────────────────────────────────────────────────────────────
WORLD_SCALE  = 4.0        # floor footprint: ±WORLD_SCALE/2 in X and Y (m)
Z_SCALE      = 0.40       # peak height (m); youngest tips reach this
COBALT       = (0.027, 0.141, 0.557, 1.0)   # seed / core colour
AMBER        = (0.980, 0.620, 0.050, 1.0)   # tips / youngest colour
MESH_NAME    = "DLA_Cluster"
OBJ_NAME     = "dla_cluster_floor"
OUT_BLEND    = "//dla_cluster_floor.blend"
OUT_GLB      = "//dla_cluster_floor.glb"


# ── DLA core ──────────────────────────────────────────────────────────────────

def run_dla(n_particles: int, rng: np.random.Generator) -> np.ndarray:
    """
    Run 2D on-lattice DLA.  Returns float32 array arrival[i,j]:
      0.0  → empty cell
      k/n  → cell stuck as the k-th particle (k ∈ 1..n_particles).

    Why 4-connectivity (not 8): 4-connectivity gives a fractal dimension
    closer to the theoretical 1.71; 8-connectivity over-branches (D_f ≈ 1.90)
    and produces less dendritic, more filled clusters.
    """
    grid    = np.zeros((N, N), dtype=bool)
    arrival = np.zeros((N, N), dtype=np.float32)

    cx, cy = N // 2, N // 2
    grid[cx, cy]    = True      # seed
    arrival[cx, cy] = 1 / n_particles   # seed = earliest particle
    r_max   = 1
    num_stuck = 1

    while num_stuck < n_particles:
        r_launch = r_max + 5
        r_kill   = r_launch + 20

        theta = rng.uniform(0.0, 2.0 * math.pi)
        x = cx + int(round(r_launch * math.cos(theta)))
        y = cy + int(round(r_launch * math.sin(theta)))
        x = max(1, min(N - 2, x))
        y = max(1, min(N - 2, y))

        while True:
            # 4-adjacency stick test — array indexing beats any set lookup
            if (grid[x - 1, y] or grid[x + 1, y] or
                    grid[x, y - 1] or grid[x, y + 1]):
                grid[x, y]    = True
                num_stuck    += 1
                arrival[x, y] = num_stuck / n_particles
                dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                r_max = max(r_max, int(dist) + 1)
                break

            step = rng.integers(0, 4)
            if   step == 0: x -= 1
            elif step == 1: x += 1
            elif step == 2: y -= 1
            else:           y += 1

            if math.sqrt((x - cx) ** 2 + (y - cy) ** 2) > r_kill:
                break   # walker escaped → discard, launch fresh one

            x = max(1, min(N - 2, x))
            y = max(1, min(N - 2, y))

    return arrival


def mask_arrival(arrival: np.ndarray, n_show: int, n_total: int) -> np.ndarray:
    """Keep only first n_show arrivals; blank later ones to 0."""
    thresh = n_show / n_total
    masked = arrival.copy()
    masked[arrival > thresh] = 0.0
    return masked


# ── mesh builder ──────────────────────────────────────────────────────────────

def build_height_field_mesh(name: str) -> bpy.types.Object:
    """
    Create an N×N quad grid with flat z=0.  Shape keys are added later.
    Why BMesh: direct vertex creation avoids the overhead of bpy.ops.mesh.
    """
    mesh = bpy.data.meshes.new(name)
    bm   = bmesh.new()

    step = WORLD_SCALE / (N - 1)
    verts = []
    for j in range(N):
        for i in range(N):
            x =  i * step - WORLD_SCALE / 2
            y =  j * step - WORLD_SCALE / 2
            verts.append(bm.verts.new((x, y, 0.0)))

    bm.verts.ensure_lookup_table()
    for j in range(N - 1):
        for i in range(N - 1):
            a = verts[j * N + i]
            b = verts[j * N + i + 1]
            c = verts[(j + 1) * N + i + 1]
            d = verts[(j + 1) * N + i]
            bm.faces.new((a, b, c, d))

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(OBJ_NAME, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def apply_shape_key(obj: bpy.types.Object, name: str,
                    arrival: np.ndarray) -> None:
    """
    Write a shape key from a 2D arrival array.
    z = arrival[j,i] × Z_SCALE — empty cells (arrival=0) stay flat.
    Vertex order matches the j-outer, i-inner loop in build_height_field_mesh.
    """
    sk  = obj.shape_key_add(name=name, from_mix=False)
    pts = sk.data
    for j in range(N):
        for i in range(N):
            pts[j * N + i].co.z = arrival[j, i] * Z_SCALE


def apply_colour_attribute(obj: bpy.types.Object,
                           arrival: np.ndarray) -> None:
    """
    FLOAT_COLOR vertex attribute on POINT domain.
    Linear interpolation from COBALT (seed/old) to AMBER (tips/new).
    WHY FLOAT_COLOR not BYTE_COLOR: 32-bit floats survive Draco compression
    without banding; BYTE_COLOR clips to [0,1] and loses HDR head-room.
    """
    mesh = obj.data
    if "Col" in mesh.color_attributes:
        mesh.color_attributes.remove(mesh.color_attributes["Col"])
    attr = mesh.color_attributes.new(name="Col",
                                     type="FLOAT_COLOR",
                                     domain="POINT")
    for j in range(N):
        for i in range(N):
            t = float(arrival[j, i])   # 0=empty/seed, 1=youngest tip
            r = COBALT[0] + t * (AMBER[0] - COBALT[0])
            g = COBALT[1] + t * (AMBER[1] - COBALT[1])
            b = COBALT[2] + t * (AMBER[2] - COBALT[2])
            attr.data[j * N + i].color = (r, g, b, 1.0)


# ── material ──────────────────────────────────────────────────────────────────

def apply_material(obj: bpy.types.Object) -> None:
    """
    MixShader: Principled BSDF (metallic, low roughness) + Emission.
    Vertex-colour drives both Fac and emission strength — cluster points
    glow amber while the background stays deep cobalt.
    """
    mat  = bpy.data.materials.new("DLA_Height")
    mat.use_nodes = True
    nt   = mat.node_tree
    nt.nodes.clear()

    out   = nt.nodes.new("ShaderNodeOutputMaterial")
    mix   = nt.nodes.new("ShaderNodeMixShader")
    bsdf  = nt.nodes.new("ShaderNodeBsdfPrincipled")
    emit  = nt.nodes.new("ShaderNodeEmission")
    attr  = nt.nodes.new("ShaderNodeAttribute")
    gamma = nt.nodes.new("ShaderNodeGamma")

    attr.attribute_name   = "Col"
    bsdf.inputs["Metallic"].default_value       = 0.6
    bsdf.inputs["Roughness"].default_value      = 0.30
    emit.inputs["Strength"].default_value       = 1.4
    gamma.inputs["Gamma"].default_value         = 0.45   # perceptual lift

    nt.links.new(attr.outputs["Color"], gamma.inputs["Color"])
    nt.links.new(gamma.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(gamma.outputs["Color"], emit.inputs["Color"])
    nt.links.new(attr.outputs["Fac"],   mix.inputs["Fac"])
    nt.links.new(bsdf.outputs["BSDF"],  mix.inputs[1])
    nt.links.new(emit.outputs["Emission"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])

    obj.data.materials.append(mat)
    obj.data.color_attributes.active_color = obj.data.color_attributes["Col"]


# ── export helpers ────────────────────────────────────────────────────────────

def set_holoflow_props(obj: bpy.types.Object) -> None:
    obj["holoflow:facet"]    = True
    obj["holoflow:category"] = "stage-floor"


def apply_transforms_and_orient(obj: bpy.types.Object) -> None:
    """
    +Y up at export: rotate -90° around X, then apply so local axes
    become the glTF convention.  Transform apply resets rotation to 0,0,0.
    """
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    obj.rotation_euler[0] = -math.pi / 2
    bpy.ops.object.transform_apply(rotation=True)


def export_glb(path: str) -> None:
    bpy.ops.export_scene.gltf(
        filepath                  = path,
        export_format             = "GLB",
        export_draco_mesh_compression_enable = True,
        export_draco_mesh_compression_level  = 6,
        export_image_format       = "WEBP",
        export_morph              = True,
        export_colors             = True,
        use_selection             = False,
    )


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    # ── clear default scene ──
    bpy.ops.wm.read_homefile(app_template="")
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    # ── run DLA ──
    rng     = np.random.default_rng(SEED)
    print(f"[DLA] running {N_BASIS} particles on {N}×{N} grid …")
    arrival = run_dla(N_BASIS, rng)
    print(f"[DLA] done. cluster area = {np.count_nonzero(arrival)} cells")

    # ── build mesh ──
    obj = build_height_field_mesh(MESH_NAME)
    obj.shape_key_add(name="Basis", from_mix=False)   # basis is flat at first

    # Basis: full N_BASIS cluster
    apply_shape_key(obj, "Basis", arrival)

    # SK_Small: first 400 particles only — shows early sparse dendrites
    apply_shape_key(obj, "SK_Small", mask_arrival(arrival, N_SMALL, N_BASIS))

    # SK_Mid: first 1200 particles — intermediate growth
    apply_shape_key(obj, "SK_Mid",   mask_arrival(arrival, N_MED,   N_BASIS))

    # SK_Inverse: core high, tips low — shows age not growth-front
    inv = arrival.copy()
    inv[arrival > 0] = 1.0 - arrival[arrival > 0] + 1.0 / N_BASIS
    apply_shape_key(obj, "SK_Inverse", inv)

    # ── colour (from Basis arrival) ──
    apply_colour_attribute(obj, arrival)
    apply_material(obj)

    # ── holoflow metadata ──
    set_holoflow_props(obj)
    apply_transforms_and_orient(obj)

    # ── save + export ──
    bpy.ops.wm.save_as_mainfile(filepath=bpy.path.abspath(OUT_BLEND))
    export_glb(bpy.path.abspath(OUT_GLB))
    print("[DLA] blueprint complete — blend + glb saved.")


if __name__ == "__main__":
    main()
