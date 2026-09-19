"""
TASEP — Totally Asymmetric Simple Exclusion Process
Derrida B, Evans MR, Hakim V, Pasquier V (1993) J Phys A 26:1493–1517
doi:10.1088/0305-4470/26/7/011  (Public Domain — >30 yr)

THE PHYSICS
-----------
Particles hop rightward along a 1-D lattice of L sites under hard-core
exclusion (at most one particle per site).  Open boundaries:

  Left  reservoir  — injects at rate α if site 0 is empty.
  Right reservoir  — absorbs at rate β if site L−1 is occupied.
  Bulk             — each particle hops right at rate 1 if next site empty.

EXACT PHASE DIAGRAM (Derrida et al. 1993; Schütz & Domany 1993)
-----------------------------------------------------------------
Three phases are separated by one first-order line (α=β<1/2) and two
continuous lines (α=1/2 at β>1/2; β=1/2 at α>1/2):

  Low-density  (LD)  α<1/2 and α<β   ρ_bulk = α,   J = α(1−α)
  High-density (HD)  β<1/2 and β<α   ρ_bulk = 1−β, J = β(1−β)
  Maximal-curr (MC)  α≥1/2 and β≥1/2 ρ_bulk = 1/2, J = 1/4

On the coexistence line α=β<1/2 a macroscopic shock — a domain wall
separating a LD region (left) from a HD region (right) — executes a
symmetric random walk with D_shock = J·(1−2α)/N (Derrida et al. 1997).

KPZ UNIVERSALITY
-----------------
Integrated-current fluctuations Q(x,t) in TASEP scale as t^{1/3} and
converge to the Tracy–Widom GUE distribution (Johansson 2000; Prähofer
& Spohn 2002).  TASEP is therefore the canonical exactly-solvable member
of the Kardar–Parisi–Zhang universality class.

ALGORITHM — SYNCHRONOUS PARALLEL UPDATE
-----------------------------------------
One time step:
  1. Injection:  sigma[0]=0 and r[0]<α → new[0]=1
  2. Bulk hops:  for all i, sigma[i]=1 and sigma[i+1]=0 → hop simultaneously.
     Proof of conflict-freedom: can_hop[i]=True requires sigma[i+1]=0,
     which forces can_hop[i+1]=False; hence no two adjacent hops trigger.
  3. Extraction: sigma[L−1]=1 and r[L−1]<β → new[L−1]=0
All three rules read from the OLD state sigma; they write to a copy `new`.

The synchronous update has the same steady-state phase structure as the
canonical random-sequential update (RSU) in the large-L limit (Rajewsky
et al. 1998) but runs as pure NumPy with no Python loops over sites.

VISUALISATION
-------------
128 × 128 kymograph: x-axis = site index, y-axis = time row.
Each row = mean occupancy over N_AVG successive steps → density ∈ [0,1].
Height = density × Z_SCALE.  Colour: Cobalt (ρ=0) → Amber (ρ=1).

SHAPE KEYS
----------
Basis      (α=0.30, β=0.70)  LD  ρ_bulk ≈ 0.30  sparse current flow
SK_HDphase (α=0.70, β=0.30)  HD  ρ_bulk ≈ 0.70  dense, holes drift left
SK_MaxCurr (α=0.80, β=0.80)  MC  ρ_bulk = 0.50  J = 1/4 maximum current
SK_Shock   (α=β=0.30)        1st-order line, mobile random-walk shock

PARAMETERS (edit here)
"""

import bpy
import numpy as np
from numpy.random import default_rng

# ── lattice ────────────────────────────────────────────────────────────────────
N        = 128       # sites (space) = rows (time) → 128×128 quad mesh
N_AVG    = 32        # sweeps averaged per kymograph row; density ∈ {0, 1/32, …, 1}
N_SETTLE = 2_500     # burn-in sweeps before collection starts
SEED     = 0xDEAD5EED

# ── phase parameters ──────────────────────────────────────────────────────────
ALPHA_LD = 0.30; BETA_LD = 0.70   # LD: ρ_bulk = α = 0.30
ALPHA_HD = 0.70; BETA_HD = 0.30   # HD: ρ_bulk = 1−β = 0.70
ALPHA_MC = 0.80; BETA_MC = 0.80   # MC: ρ_bulk = 0.50, J = 0.25
ALPHA_SH = 0.30; BETA_SH = 0.30   # Shock: α=β < 1/2, mobile domain wall

# ── mesh geometry ─────────────────────────────────────────────────────────────
WORLD_SCALE = 4.0    # mesh spans [−WS, +WS]² in XY before rotation
Z_SCALE     = 0.35   # maximum height (ρ=1)

# ── material / export ──────────────────────────────────────────────────────────
ATTR_NAME = "TASEP_Density"
OBJ_NAME  = "tasep_floor"
MAT_NAME  = "MAT_tasep_floor"
OUT_BLEND = "tasep_floor.blend"
OUT_GLB   = "tasep_floor.glb"

COBALT = (0.027, 0.141, 0.557, 1.0)   # ρ = 0 (empty site)
AMBER  = (0.980, 0.620, 0.050, 1.0)   # ρ = 1 (occupied site)


# ── simulation ────────────────────────────────────────────────────────────────

def _step(sigma: np.ndarray, alpha: float, beta: float,
          r: np.ndarray) -> np.ndarray:
    """
    One synchronous TASEP step; r is a (L,) uniform[0,1) array.
    Reads exclusively from sigma, writes to a copy — no ordering artefacts.
    """
    new = sigma.copy()
    L = len(sigma)
    # injection at left boundary
    if sigma[0] == 0 and r[0] < alpha:
        new[0] = 1
    # bulk hops: conflict-free because can_hop[i] ⟹ sigma[i+1]=0
    #            ⟹ can_hop[i+1] requires sigma[i+1]=1 — contradiction.
    can_hop = (sigma[:-1] == 1) & (sigma[1:] == 0)
    new[:-1][can_hop] = 0
    new[1:][can_hop] = 1
    # extraction at right boundary
    if sigma[L - 1] == 1 and r[L - 1] < beta:
        new[L - 1] = 0
    return new


def run_tasep(alpha: float, beta: float, rng) -> np.ndarray:
    """
    Burn in N_SETTLE steps, then collect an (N, N) float32 kymograph.
    Row i = mean occupancy over N_AVG steps → continuous density in [0,1].

    Initial density: min(α, 1−β, 0.5) puts the chain near its expected
    steady-state density, accelerating burn-in by O(L) sweeps.
    """
    L = N
    rho_init = float(min(alpha, 1.0 - beta, 0.5))
    sigma = (rng.random(L) < rho_init).astype(np.int8)

    for _ in range(N_SETTLE):
        sigma = _step(sigma, alpha, beta, rng.random(L))

    grid = np.zeros((N, N), dtype=np.float32)
    for row in range(N):
        acc = np.zeros(L, dtype=np.float32)
        for _ in range(N_AVG):
            sigma = _step(sigma, alpha, beta, rng.random(L))
            acc  += sigma
        grid[row] = acc / N_AVG
    return grid


# ── mesh ──────────────────────────────────────────────────────────────────────

def build_floor_mesh(me: bpy.types.Mesh, grid: np.ndarray) -> None:
    """
    N×N quad grid; vertex (i,j) at (x_i, y_j, grid[i,j]·Z_SCALE).
    Faces wound CCW (Blender front-face convention).
    """
    xs = np.linspace(-WORLD_SCALE, WORLD_SCALE, N)
    ys = np.linspace(-WORLD_SCALE, WORLD_SCALE, N)
    xi, yj = np.meshgrid(xs, ys, indexing='ij')
    verts = np.column_stack((xi.ravel(), yj.ravel(),
                              (grid * Z_SCALE).ravel()))

    i_idx = np.arange(N - 1).repeat(N - 1)
    j_idx = np.tile(np.arange(N - 1), N - 1)
    v00 = i_idx * N + j_idx
    faces = np.column_stack((v00, v00 + N, v00 + N + 1, v00 + 1))

    NV = N * N
    NQ = (N - 1) ** 2
    me.vertices.add(NV)
    me.vertices.foreach_set("co", verts.ravel())
    me.loops.add(NQ * 4)
    me.loops.foreach_set("vertex_index", faces.ravel())
    me.polygons.add(NQ)
    me.polygons.foreach_set("loop_start", np.arange(NQ) * 4)
    me.polygons.foreach_set("loop_total", np.full(NQ, 4, dtype=np.int32))
    me.update()


def assign_colour(me: bpy.types.Mesh, grid: np.ndarray) -> None:
    attr = me.color_attributes.new(
        name=ATTR_NAME, type='FLOAT_COLOR', domain='POINT')
    t = grid.ravel().astype(np.float32)
    colours = np.column_stack((
        COBALT[0] + t * (AMBER[0] - COBALT[0]),
        COBALT[1] + t * (AMBER[1] - COBALT[1]),
        COBALT[2] + t * (AMBER[2] - COBALT[2]),
        np.ones_like(t),
    ))
    attr.data.foreach_set("color", colours.ravel())


def add_shape_key(obj: bpy.types.Object, name: str,
                  grid: np.ndarray) -> None:
    sk = obj.shape_key_add(name=name, from_mix=False)
    NV = N * N
    co = np.empty(NV * 3, dtype=np.float32)
    obj.data.vertices.foreach_get("co", co)
    co = co.reshape(NV, 3)
    co[:, 2] = (grid * Z_SCALE).ravel()
    sk.data.foreach_set("co", co.ravel())


def make_material() -> bpy.types.Material:
    mat = bpy.data.materials.new(MAT_NAME)
    mat.use_nodes = True
    nd = mat.node_tree.nodes
    lk = mat.node_tree.links
    nd.clear()
    vc   = nd.new("ShaderNodeVertexColor");    vc.layer_name = ATTR_NAME
    bsdf = nd.new("ShaderNodeBsdfPrincipled"); bsdf.inputs["Metallic"].default_value = 0.15
    bsdf.inputs["Roughness"].default_value = 0.30
    em   = nd.new("ShaderNodeEmission");       em.inputs["Strength"].default_value = 1.6
    mix  = nd.new("ShaderNodeMixShader");      mix.inputs["Fac"].default_value = 0.35
    out  = nd.new("ShaderNodeOutputMaterial")
    lk.new(vc.outputs["Color"],     bsdf.inputs["Base Color"])
    lk.new(vc.outputs["Color"],     em.inputs["Color"])
    lk.new(bsdf.outputs["BSDF"],    mix.inputs[1])
    lk.new(em.outputs["Emission"],  mix.inputs[2])
    lk.new(mix.outputs["Shader"],   out.inputs["Surface"])
    return mat


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    rng = default_rng(SEED)

    print("TASEP LD  (α=0.30, β=0.70) …"); grid_ld = run_tasep(ALPHA_LD, BETA_LD, rng)
    print("TASEP HD  (α=0.70, β=0.30) …"); grid_hd = run_tasep(ALPHA_HD, BETA_HD, rng)
    print("TASEP MC  (α=0.80, β=0.80) …"); grid_mc = run_tasep(ALPHA_MC, BETA_MC, rng)
    print("TASEP SHK (α=β=0.30)       …"); grid_sh = run_tasep(ALPHA_SH, BETA_SH, rng)

    bpy.ops.wm.read_factory_settings(use_empty=True)

    me  = bpy.data.meshes.new(OBJ_NAME)
    build_floor_mesh(me, grid_ld)
    assign_colour(me, grid_ld)
    obj = bpy.data.objects.new(OBJ_NAME, me)
    bpy.context.collection.objects.link(obj)

    obj.shape_key_add(name="Basis", from_mix=False)
    add_shape_key(obj, "SK_HDphase", grid_hd)
    add_shape_key(obj, "SK_MaxCurr", grid_mc)
    add_shape_key(obj, "SK_Shock",   grid_sh)

    me.materials.append(make_material())
    obj["holoflow:category"] = "stage-floor"
    obj["holoflow:facet"]    = True
    obj.rotation_euler[0]    = -np.pi / 2
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
    bpy.ops.export_scene.gltf(
        filepath=OUT_GLB, export_format='GLB',
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_image_format='WEBP',
        export_morph=True, export_colors=True, export_yup=True,
    )
    print(f"✓  {OUT_BLEND}  {OUT_GLB}")


if __name__ == "__main__":
    main()
