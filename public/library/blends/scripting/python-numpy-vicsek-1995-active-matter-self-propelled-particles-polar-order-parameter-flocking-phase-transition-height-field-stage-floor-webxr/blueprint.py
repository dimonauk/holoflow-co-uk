"""
Vicsek Model (1995) — Active Matter Flocking Phase Transition
Vicsek T, Czirók A, Ben-Jacob E, Cohen I, Shochet O (1995)
  Novel type of phase transition in a system of self-propelled particles.
  Phys Rev Lett 75(6):1226–1229.  doi:10.1103/PhysRevLett.75.1226
  arXiv:cond-mat/9507131 (Public Domain > 30 yr)

THE PHYSICS
-----------
N self-propelled point particles move at constant speed v₀ in a periodic 2-D
box of side L.  At each discrete time step every particle i adopts the mean
heading of all particles j within interaction radius R, then adds a bounded
uniform noise ξ_i ~ U[−η·π, η·π]:

  θ_i(t+1) = arg ⟨exp(iθ_j(t))⟩_{|rⱼ−rᵢ|<R}  +  ξ_i
  rᵢ(t+1) = rᵢ(t) + v₀ (cos θ_i(t+1), sin θ_i(t+1))   (mod L)

η ∈ [0,1]:  η = 0 → zero noise;  η = 1 → isotropic random direction each step.

PHASE TRANSITION
-----------------
The global polar order parameter

  Φ = (1/N) |Σ_i exp(iθ_i)|  ∈ [0, 1]

undergoes a continuous (finite-size) transition near η_c ≈ 0.35 for the
original parameters (ρ = N/L² ≈ 6.0, v₀ = 0.03).  Below η_c particles form
a coherent flock (Φ → 1); above it motion is disordered (Φ → 0).

CHATÉ–GRÉGOIRE BANDS (2008)
----------------------------
At intermediate η just below η_c and in sufficiently large systems, the
ordered phase does NOT transition to disorder continuously.  Instead, dense
travelling bands of aligned particles — first described by Chaté, Ginelli,
Grégoire & Raynaud (Phys Rev E 77:046113, 2008) — cross the disordered
background.  The Vicsek transition is now understood to be weakly first-order
in the thermodynamic limit, driven by these density waves.  SK_Bands captures
this intermediate regime (η = 0.28).

ALGORITHM — CELL-LIST NEIGHBOUR SEARCH
----------------------------------------
Divide the box into CELL_N × CELL_N cells of side CELL_SIZE ≈ R.
Each particle belongs to one cell.  For every cell, accumulate per-cell
velocity sums (Σ cos θ, Σ sin θ) using np.bincount — O(N), no Python loops
over particles.  A 3×3 rolling-sum convolution (9 × np.roll on CELL_N²
arrays) gives each particle's neighbourhood average in O(CELL_N²) extra work.
This overestimates the interaction range slightly (R→√5/2·R at corners) but
preserves all qualitative phase behaviour.

VISUALISATION
-------------
128 × 128 stage-floor mesh.  Each vertex (i,j) sits at height
  z = local_order(i,j) · Z_SCALE
where local_order is the time-averaged magnitude of the local velocity field,
smoothed with a periodic Gaussian (σ = SMOOTH_SIG cells) via scipy.ndimage.
Colour: Cobalt (Φ_local = 0, disordered) → Amber (Φ_local = 1, ordered).

SHAPE KEYS
----------
Basis     η = 0.10  ordered flocking   Φ ≈ 0.88  near-uniform amber surface
SK_Bands  η = 0.28  band-forming       Φ ≈ 0.55  amber stripes on cobalt sea
SK_Crit   η = 0.36  near-critical      Φ ≈ 0.30  patchy, large fluctuations
SK_Dis    η = 0.70  disordered         Φ ≈ 0.03  flat cobalt floor
"""

import bpy
import numpy as np
from numpy.random import default_rng

try:
    from scipy.ndimage import gaussian_filter as _gf
    _HAS_SCIPY = True
except ImportError:
    _HAS_SCIPY = False

# ── simulation ────────────────────────────────────────────────────────────────
N_PARTICLES = 6144     # matches Vicsek density: ρ = 6144 / 32² = 6.0
L           = 32.0     # periodic box side (length units)
R           = 1.0      # interaction radius (units)
V0          = 0.03     # particle speed per step (Vicsek 1995 value)
CELL_N      = 32       # CELL_SIZE = L / CELL_N = 1.0 = R  (exact)
CELL_SIZE   = L / CELL_N  # = 1.0

N_SETTLE    = 2000     # burn-in steps before measurement
N_COLLECT   = 60       # steps averaged for the order-field snapshot
SEED        = 0xBEAD_C0ED

# ── phase parameters ─────────────────────────────────────────────────────────
ETA_ORDER   = 0.10    # low noise: coherent flock
ETA_BANDS   = 0.28    # band-forming intermediate regime (Chaté 2008)
ETA_CRIT    = 0.36    # near-critical: large-fluctuation patchwork
ETA_DIS     = 0.70    # disordered

# ── visualisation ─────────────────────────────────────────────────────────────
HIST_GRID   = 128
HIST_SIZE   = L / HIST_GRID   # = 0.25 (hist cell side)
SMOOTH_SIG  = 3.5             # Gaussian σ in HIST_GRID cells (periodic wrap)

WORLD_SCALE = 4.0             # mesh spans [−WS, +WS]² in XY
Z_SCALE     = 0.45

ATTR_NAME  = "Vicsek_Order"
OBJ_NAME   = "vicsek_floor"
MAT_NAME   = "MAT_vicsek_floor"
OUT_BLEND  = "vicsek_floor.blend"
OUT_GLB    = "vicsek_floor.glb"

COBALT = (0.027, 0.141, 0.557, 1.0)   # Φ_local = 0 (disordered)
AMBER  = (0.980, 0.620, 0.050, 1.0)   # Φ_local = 1 (ordered)


# ── simulation ────────────────────────────────────────────────────────────────

def _step(pos, angle, eta, rng):
    """
    One Vicsek step.  Cell-list O(N) neighbour search via np.bincount;
    periodic 3×3 cell neighbourhood sum via np.roll on CELL_N² arrays.
    Returns (updated pos, updated angle) in-place arrays.
    """
    # Integer cell coordinates — periodic wrap guaranteed by % CELL_N
    cx = (pos[:, 0] / CELL_SIZE).astype(np.int32) % CELL_N
    cy = (pos[:, 1] / CELL_SIZE).astype(np.int32) % CELL_N
    flat = cx * CELL_N + cy  # linear cell index, shape (N,)

    # Per-cell velocity component sums — np.bincount is faster than add.at
    vc_x = np.bincount(flat, weights=np.cos(angle),
                       minlength=CELL_N ** 2).reshape(CELL_N, CELL_N)
    vc_y = np.bincount(flat, weights=np.sin(angle),
                       minlength=CELL_N ** 2).reshape(CELL_N, CELL_N)

    # 3×3 periodic neighbourhood sum (includes self cell)
    nbr_x = sum(np.roll(vc_x, (di, dj), axis=(0, 1))
                for di in (-1, 0, 1) for dj in (-1, 0, 1))
    nbr_y = sum(np.roll(vc_y, (di, dj), axis=(0, 1))
                for di in (-1, 0, 1) for dj in (-1, 0, 1))

    # New angle = neighbourhood average + uniform noise ξ ~ U[−ηπ, +ηπ]
    avg_angle = np.arctan2(nbr_y[cx, cy], nbr_x[cx, cy])
    angle[:] = avg_angle + rng.uniform(-eta * np.pi, eta * np.pi, N_PARTICLES)

    # Position update with periodic boundary conditions
    pos[:, 0] = (pos[:, 0] + V0 * np.cos(angle)) % L
    pos[:, 1] = (pos[:, 1] + V0 * np.sin(angle)) % L
    return pos, angle


def run_vicsek(eta, rng):
    """
    Initialise uniformly, burn in N_SETTLE steps, accumulate N_COLLECT
    velocity-component snapshots, Gaussian-smooth (periodic), return
    normalised 128×128 float32 local-order field.
    """
    pos   = rng.uniform(0.0, L, (N_PARTICLES, 2))
    angle = rng.uniform(-np.pi, np.pi, N_PARTICLES)

    for _ in range(N_SETTLE):
        pos, angle = _step(pos, angle, eta, rng)

    # Accumulate on HIST_GRID×HIST_GRID bins
    acc_x = np.zeros((HIST_GRID, HIST_GRID))
    acc_y = np.zeros((HIST_GRID, HIST_GRID))

    for _ in range(N_COLLECT):
        pos, angle = _step(pos, angle, eta, rng)
        hx = (pos[:, 0] / HIST_SIZE).astype(np.int32) % HIST_GRID
        hy = (pos[:, 1] / HIST_SIZE).astype(np.int32) % HIST_GRID
        hflat = hx * HIST_GRID + hy
        acc_x += np.bincount(hflat, weights=np.cos(angle),
                              minlength=HIST_GRID ** 2).reshape(HIST_GRID, HIST_GRID)
        acc_y += np.bincount(hflat, weights=np.sin(angle),
                              minlength=HIST_GRID ** 2).reshape(HIST_GRID, HIST_GRID)

    # Gaussian smooth preserves periodicity; fallback: skip smoothing
    if _HAS_SCIPY:
        acc_x = _gf(acc_x, sigma=SMOOTH_SIG, mode='wrap')
        acc_y = _gf(acc_y, sigma=SMOOTH_SIG, mode='wrap')

    order = np.sqrt(acc_x ** 2 + acc_y ** 2).astype(np.float32)
    m = order.max()
    if m > 0:
        order /= m
    return order


# ── mesh helpers ──────────────────────────────────────────────────────────────

def build_floor_mesh(me, grid):
    """N×N quad grid, vertex z = grid[i,j]·Z_SCALE, span [−WS, +WS]²."""
    xs = np.linspace(-WORLD_SCALE, WORLD_SCALE, HIST_GRID)
    ys = np.linspace(-WORLD_SCALE, WORLD_SCALE, HIST_GRID)
    xi, yj = np.meshgrid(xs, ys, indexing='ij')
    verts = np.column_stack((xi.ravel(), yj.ravel(),
                              (grid * Z_SCALE).ravel()))
    NV = HIST_GRID * HIST_GRID
    NQ = (HIST_GRID - 1) ** 2
    i_idx = np.arange(HIST_GRID - 1).repeat(HIST_GRID - 1)
    j_idx = np.tile(np.arange(HIST_GRID - 1), HIST_GRID - 1)
    v00   = i_idx * HIST_GRID + j_idx
    faces = np.column_stack((v00, v00 + HIST_GRID, v00 + HIST_GRID + 1, v00 + 1))
    me.vertices.add(NV)
    me.vertices.foreach_set("co", verts.ravel())
    me.loops.add(NQ * 4)
    me.loops.foreach_set("vertex_index", faces.ravel())
    me.polygons.add(NQ)
    me.polygons.foreach_set("loop_start", np.arange(NQ) * 4)
    me.polygons.foreach_set("loop_total", np.full(NQ, 4, dtype=np.int32))
    me.update()


def assign_colour(me, grid):
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


def add_shape_key(obj, name, grid):
    sk = obj.shape_key_add(name=name, from_mix=False)
    NV = HIST_GRID * HIST_GRID
    co = np.empty(NV * 3, dtype=np.float32)
    obj.data.vertices.foreach_get("co", co)
    co = co.reshape(NV, 3)
    co[:, 2] = (grid * Z_SCALE).ravel()
    sk.data.foreach_set("co", co.ravel())


def make_material():
    mat = bpy.data.materials.new(MAT_NAME)
    mat.use_nodes = True
    nd = mat.node_tree.nodes
    lk = mat.node_tree.links
    nd.clear()
    vc   = nd.new("ShaderNodeVertexColor");    vc.layer_name = ATTR_NAME
    bsdf = nd.new("ShaderNodeBsdfPrincipled"); bsdf.inputs["Metallic"].default_value  = 0.10
    bsdf.inputs["Roughness"].default_value = 0.35
    em   = nd.new("ShaderNodeEmission");       em.inputs["Strength"].default_value   = 1.8
    mix  = nd.new("ShaderNodeMixShader");      mix.inputs["Fac"].default_value       = 0.30
    out  = nd.new("ShaderNodeOutputMaterial")
    lk.new(vc.outputs["Color"],    bsdf.inputs["Base Color"])
    lk.new(vc.outputs["Color"],    em.inputs["Color"])
    lk.new(bsdf.outputs["BSDF"],   mix.inputs[1])
    lk.new(em.outputs["Emission"], mix.inputs[2])
    lk.new(mix.outputs["Shader"],  out.inputs["Surface"])
    return mat


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    rng = default_rng(SEED)

    print("Vicsek ORDER  η=0.10 …"); grid_ord  = run_vicsek(ETA_ORDER, rng)
    print("Vicsek BANDS  η=0.28 …"); grid_band = run_vicsek(ETA_BANDS, rng)
    print("Vicsek CRIT   η=0.36 …"); grid_crit = run_vicsek(ETA_CRIT,  rng)
    print("Vicsek DIS    η=0.70 …"); grid_dis  = run_vicsek(ETA_DIS,   rng)

    bpy.ops.wm.read_factory_settings(use_empty=True)

    me  = bpy.data.meshes.new(OBJ_NAME)
    build_floor_mesh(me, grid_ord)
    assign_colour(me, grid_ord)
    obj = bpy.data.objects.new(OBJ_NAME, me)
    bpy.context.collection.objects.link(obj)

    obj.shape_key_add(name="Basis", from_mix=False)
    add_shape_key(obj, "SK_Bands", grid_band)
    add_shape_key(obj, "SK_Crit",  grid_crit)
    add_shape_key(obj, "SK_Dis",   grid_dis)

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
