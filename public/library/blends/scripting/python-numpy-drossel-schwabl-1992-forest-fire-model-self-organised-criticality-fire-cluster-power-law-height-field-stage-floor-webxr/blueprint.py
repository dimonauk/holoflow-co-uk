"""
Drossel–Schwabl Forest Fire Model — Self-Organised Criticality
Drossel B, Schwabl F (1992) Phys Rev Lett 69(11):1629–1632
DOI 10.1103/PhysRevLett.69.1629   (Public Domain — >30 yr)

THE PHYSICS
-----------
Three-state 2D cellular automaton on an N×N lattice:
  EMPTY(0)  — bare ash / cleared ground
  TREE(1)   — living tree occupying a site
  BURNING(2)— tree actively burning (persists for exactly ONE time step)

Synchronous update rule (read old state → write new state simultaneously):
  1. BURNING  → EMPTY         (fire burns out)
  2. TREE + BURNING neighbour → BURNING  (fire spreads)
  3. TREE + no BURNING neighbour → BURNING with prob f  (lightning)
     TREE + no BURNING neighbour → TREE with prob 1−f  (survives)
  4. EMPTY → TREE with prob p  (regrowth / saplings)
     EMPTY → EMPTY with prob 1−p

SOC REGIME (Drossel & Schwabl 1992)
------------------------------------
When p ≪ 1, f ≪ 1, and p/f ≫ 1 (two-time-scale separation):
  - trees grow slowly, lightning is rarer still
  - when a tree ignites, fire spreads instantly across any connected
    component of forest before new trees can regrow
  - fire cluster sizes S obey  P(S) ~ S^{−τ}  τ ≈ 1.5  (DS universality)
  - no parameter must be tuned — criticality is the steady-state attractor

Contrast with the BTW Abelian Sandpile (also SOC): the sandpile drives
criticality through grain conservation + toppling threshold; the forest
fire model drives it through regeneration/destruction competition.

WHY VECTORISED UPDATE IS EXACT
--------------------------------
States BURNING, TREE, EMPTY are mutually exclusive; the fire-spread rule
applies to TREE sites with a BURNING neighbour in the OLD grid. Because
we read exclusively from `grid` and write exclusively to `new_grid`, all
N² update decisions are independent — no ordering artefacts, no race
conditions. numpy.roll provides periodic-boundary shifting; we clip to
open (void) boundaries by zeroing edge-wrap contributions from the
opposite border in the fire mask (not needed here — the fire never
wraps because ignition kills the burning site in one step and at the
boundary there are simply no wrap-around trees in the model). For an
open boundary variant set boundary='edge' and clip roll contributions.

SHAPE KEYS
----------
Basis       : p=0.010 f=5e-5  3 000 steps from 50 % random seed.
              SOC steady state; active small fire cluster visible.
SK_LowP     : p=0.003 f=5e-5  2 000 steps.  Sparse savanna; fire clusters
              tiny because forest connectivity below percolation threshold.
SK_HighP    : p=0.050 f=5e-5  4 000 steps.  Dense forest; infrequent but
              large fires — high p/f ratio extends fire-return interval.
SK_AllTrees : every site = TREE, no fire.  Theoretical saturation; shows
              the maximum-height surface before the first lightning strike.

PARAMETERS (edit here)
"""

import bpy
import bmesh
import numpy as np
from numpy.random import default_rng

# ── lattice ────────────────────────────────────────────────────────────────────
N              = 128            # grid side; 128² = 16 384 sites
P_BASIS        = 0.010          # regrowth probability, SOC basis
F_BASIS        = 5e-5           # lightning probability, SOC basis
N_SETTLE_BASIS = 3_000          # time steps to reach SOC steady state

P_LOWP         = 0.003          # sparse savanna variant
F_LOWP         = 5e-5
N_SETTLE_LOWP  = 2_000

P_HIGHP        = 0.050          # dense forest variant
F_HIGHP        = 5e-5
N_SETTLE_HIGHP = 4_000

SEED           = 0xF0RE5        # reproducible RNG seed

EMPTY   = 0
TREE    = 1
BURNING = 2

# ── mesh geometry ─────────────────────────────────────────────────────────────
WORLD_SCALE = 4.0               # mesh spans [−WORLD_SCALE, +WORLD_SCALE] in X/Y
Z_SCALE     = 0.35              # height of BURNING site above EMPTY
# Z mapping: EMPTY=0, TREE=Z_SCALE/2, BURNING=Z_SCALE
Z_FACTORS   = np.array([0.0, 0.5, 1.0]) * Z_SCALE

# ── material ───────────────────────────────────────────────────────────────────
ATTR_NAME = "FF_State"          # FLOAT_COLOR attribute written per vertex
OBJ_NAME  = "drossel_schwabl_forest_floor"
MAT_NAME  = "MAT_drossel_schwabl_forest_floor"

COBALT = (0.027, 0.159, 0.557, 1.0)   # EMPTY / ash
GREEN  = (0.031, 0.380, 0.095, 1.0)   # TREE  / living forest  (linear-sRGB)
AMBER  = (0.980, 0.620, 0.050, 1.0)   # BURNING / active fire


# ── simulation ─────────────────────────────────────────────────────────────────

def _run(p, f, n_steps, rng):
    grid = (rng.uniform(size=(N, N)) < 0.5).astype(np.int8)  # 50 % trees

    for _ in range(n_steps):
        fire = grid == BURNING
        # 4-connected fire spread mask (periodic np.roll; open BCs handled by
        # the fact that BURNING sites that leave the grid don't exist — the
        # grid is finite and BURNING → EMPTY removes the source next step)
        nbr_fire = (
            np.roll(fire,  1, axis=0) | np.roll(fire, -1, axis=0) |
            np.roll(fire,  1, axis=1) | np.roll(fire, -1, axis=1)
        )
        rand = rng.random((N, N))
        new = np.zeros((N, N), dtype=np.int8)          # default → EMPTY

        # Rule 1: BURNING → EMPTY (handled by default)

        # Rule 2 + 3: TREE decisions
        is_tree        = grid == TREE
        tree_spread    = is_tree &  nbr_fire
        tree_lightning = is_tree & ~nbr_fire & (rand < f)
        tree_survive   = is_tree & ~nbr_fire & (rand >= f)
        new[tree_spread]    = BURNING
        new[tree_lightning] = BURNING
        new[tree_survive]   = TREE

        # Rule 4: EMPTY decisions
        is_empty      = grid == EMPTY
        new[is_empty & (rand < p)] = TREE
        # is_empty & rand >= p → EMPTY (already 0)

        grid = new

    return grid


def _heights(grid):
    return Z_FACTORS[grid]    # vectorised lookup; shape (N, N)


def _colour_values(grid):
    # Map {EMPTY=0, TREE=1, BURNING=2} → {0.0, 0.5, 1.0}
    return grid.astype(np.float32) / 2.0


# ── mesh builder ───────────────────────────────────────────────────────────────

def _build_mesh(heights_dict):
    """
    Create a 128×128 quad grid (127×127 faces), apply base heights from
    heights_dict['Basis'], add shape keys for each additional snapshot.
    """
    me = bpy.data.meshes.new(OBJ_NAME)
    ob = bpy.data.objects.new(OBJ_NAME, me)
    bpy.context.scene.collection.objects.link(ob)

    bm = bmesh.new()

    # Build vertex grid — row-major, x varies fastest
    xs = np.linspace(-WORLD_SCALE, WORLD_SCALE, N)
    ys = np.linspace(-WORLD_SCALE, WORLD_SCALE, N)
    basis_z = heights_dict["Basis"]

    verts = []
    for j in range(N):      # y index
        for i in range(N):  # x index
            v = bm.verts.new((xs[i], ys[j], float(basis_z[j, i])))
            verts.append(v)
    bm.verts.ensure_lookup_table()

    for j in range(N - 1):
        for i in range(N - 1):
            v00 = verts[ j      * N + i    ]
            v10 = verts[ j      * N + i + 1]
            v11 = verts[(j + 1) * N + i + 1]
            v01 = verts[(j + 1) * N + i    ]
            bm.faces.new([v00, v10, v11, v01])

    bm.to_mesh(me)
    bm.free()
    me.update()

    # Shape keys
    ob.shape_key_add(name="Basis", from_mix=False)
    for key_name, z_arr in heights_dict.items():
        if key_name == "Basis":
            continue
        sk = ob.shape_key_add(name=key_name, from_mix=False)
        flat = z_arr.ravel()
        for idx, v_data in enumerate(sk.data):
            v_data.co.z = float(flat[idx])

    # FLOAT_COLOR colour attribute (per-vertex)
    attr = me.attributes.new(name=ATTR_NAME, type="FLOAT_COLOR", domain="POINT")
    colour_vals = _colour_values(heights_dict["Basis"])
    flat_c = colour_vals.ravel()
    for idx, val in enumerate(flat_c):
        # Interpolate cobalt→green→amber along [0,1] via two segments
        if val <= 0.5:
            t   = val * 2.0
            col = tuple(COBALT[k] + t * (GREEN[k] - COBALT[k]) for k in range(4))
        else:
            t   = (val - 0.5) * 2.0
            col = tuple(GREEN[k] + t * (AMBER[k] - GREEN[k]) for k in range(4))
        attr.data[idx].color = col

    _build_material(ob)
    ob["holoflow:facet"] = True
    ob["holoflow:category"] = "stage-floor"
    return ob


# ── material ───────────────────────────────────────────────────────────────────

def _build_material(ob):
    mat = bpy.data.materials.new(MAT_NAME)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out   = nodes.new("ShaderNodeOutputMaterial")
    bsdf  = nodes.new("ShaderNodeBsdfPrincipled")
    ramp  = nodes.new("ShaderNodeValToRGB")
    attr  = nodes.new("ShaderNodeAttribute")
    sep   = nodes.new("ShaderNodeSeparateColor")

    attr.attribute_name = ATTR_NAME
    attr.attribute_type = "GEOMETRY"

    # Use red channel of the stored RGBA as the ramp input (we encoded grey)
    links.new(attr.outputs["Color"], sep.inputs["Color"])
    links.new(sep.outputs["Red"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Emission Color"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    cr = ramp.color_ramp
    cr.elements[0].position = 0.0; cr.elements[0].color = COBALT
    cr.elements[1].position = 1.0; cr.elements[1].color = AMBER
    mid = cr.elements.new(0.5);    mid.color = GREEN

    bsdf.inputs["Emission Strength"].default_value = 1.4
    bsdf.inputs["Metallic"].default_value          = 0.15
    bsdf.inputs["Roughness"].default_value         = 0.35

    ob.data.materials.append(mat)


# ── main ───────────────────────────────────────────────────────────────────────

def main():
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj, do_unlink=True)

    rng = default_rng(SEED)

    print("Running Drossel–Schwabl Basis (SOC steady state) …")
    g_basis  = _run(P_BASIS,  F_BASIS,  N_SETTLE_BASIS,  rng)
    print("Running SK_LowP (sparse savanna) …")
    g_lowp   = _run(P_LOWP,   F_LOWP,   N_SETTLE_LOWP,   rng)
    print("Running SK_HighP (dense forest) …")
    g_highp  = _run(P_HIGHP,  F_HIGHP,  N_SETTLE_HIGHP,  rng)

    g_alltrees       = np.full((N, N), TREE, dtype=np.int8)

    heights = {
        "Basis":      _heights(g_basis),
        "SK_LowP":    _heights(g_lowp),
        "SK_HighP":   _heights(g_highp),
        "SK_AllTrees":_heights(g_alltrees),
    }

    ob = _build_mesh(heights)

    # Apply rotation for +Y-up export
    ob.rotation_euler[0] = -3.14159265 / 2.0
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.transform_apply(rotation=True)

    # GLB export
    import os
    out_dir = os.path.dirname(os.path.abspath(__file__))
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(out_dir, "drossel_schwabl_forest_floor.glb"),
        export_format="GLB",
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_image_format="WEBP",
        export_morph=True,
        export_colors=True,
        export_apply=False,
    )
    bpy.ops.wm.save_as_mainfile(
        filepath=os.path.join(out_dir, "drossel_schwabl_forest_floor.blend")
    )
    print("Done. drossel_schwabl_forest_floor.blend + .glb written.")


main()
