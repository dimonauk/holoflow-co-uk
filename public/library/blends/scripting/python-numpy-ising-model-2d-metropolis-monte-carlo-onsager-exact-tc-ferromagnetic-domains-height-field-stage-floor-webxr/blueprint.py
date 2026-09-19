"""
2D Ising Model — Metropolis Monte Carlo
Ising 1925 · Onsager 1944 exact solution Tc = 2J/ln(1+√2)

THE PHYSICS
-----------
The 2D ferromagnetic Ising model places classical binary spins s_i ∈ {−1, +1}
on a square lattice with nearest-neighbour interaction:

    H = −J Σ_{⟨ij⟩} s_i·s_j − h Σ_i s_i

At zero external field (h = 0):
  • T < Tc  →  spontaneous magnetisation, long-range ordered domains
  • T = Tc  →  second-order phase transition, diverging correlation length ξ
  • T > Tc  →  paramagnetic, short-range order only

Onsager (1944) solved the model exactly in 2D (one of the few exactly solved
models in statistical mechanics):
  Tc = 2J / ln(1 + √2) ≈ 2.2692 J/k_B

Critical exponents (exact):
  β   = 1/8   (magnetisation M ~ |T−Tc|^β)
  γ   = 7/4   (susceptibility χ ~ |T−Tc|^{−γ})
  ν   = 1     (correlation length ξ ~ |T−Tc|^{−ν})
  η   = 1/4   (correlation function G(r) ~ r^{−(d−2+η)} at Tc)
  α   = 0     (heat capacity C ~ −ln|T−Tc|  — logarithmic divergence)

These are the 2D Ising universality class. Any model sharing the same
symmetry (Z₂ order parameter, 2D) belongs to it.

METROPOLIS-HASTINGS ALGORITHM
------------------------------
1. Pick a random site i.
2. Compute ΔE = 2·J·s_i·Σ_{j∈nn(i)} s_j  (energy cost to flip s_i).
3. Accept the flip with probability min(1, exp(−ΔE / k_B T)).

Why Metropolis? It satisfies detailed balance, ensuring the Markov chain
converges to the Boltzmann distribution at temperature T. The acceptance
criterion is numerically exact — only five possible ΔE values exist on a
square lattice (ΔE ∈ {−8, −4, 0, +4, +8}J), so we precompute exp(−ΔE/T).

VECTORISATION NOTE
------------------
Sequential site-by-site Metropolis is O(N²) per sweep and very slow in
Python. We use the standard **checkerboard decomposition**: colour the
lattice black/white (like a chess board), then flip all sites of one colour
simultaneously. Sites of the same colour are not nearest neighbours, so
each flip is independent — the steps are vectorisable with NumPy.

Checkerboard order introduces a tiny systematic at very short times, but the
equilibrated statistics are identical to random-order Metropolis.

VISUAL REPRESENTATION
---------------------
Each shape key stores the spin field s(x,y) ∈ {−1, +1} mapped to
a height:
  z = (s + 1) / 2 · Z_SCALE   →   down-spin at floor, up-spin raised

Colour attribute uses the same mapping with cobalt (down) → amber (up),
making domain structure immediately visible as tiled colour regions.

Four shape keys capture the thermal evolution:
  Basis       : T = 0.50 Tc   — nearly fully magnetised (cold)
  SK_Critical : T = 1.00 Tc   — at Onsager Tc, fractal critical cluster
  SK_Hot      : T = 1.50 Tc   — paramagnetic, salt-and-pepper noise
  SK_Quench   : T = 0.25 Tc   — quenched from T→∞ initial condition,
                                  showing coarsening domain walls

PARAMETERS (as named constants — edit here only)
"""

import bpy
import bmesh
import numpy as np
from numpy.random import default_rng

# ── lattice ────────────────────────────────────────────────────────────────────
N           = 128          # grid points per side (128×128 = 16 384 spins)
J           = 1.0          # coupling constant (energy units)
K_B         = 1.0          # Boltzmann constant (set = 1 in natural units)

# Onsager exact critical temperature
TC = 2.0 * J / np.log(1.0 + np.sqrt(2.0))   # ≈ 2.2692

# temperatures for shape keys (in units where J = k_B = 1)
T_COLD      = 0.50 * TC    # deep ferromagnet
T_CRIT      = 1.00 * TC    # Onsager critical point
T_HOT       = 1.50 * TC    # paramagnet
T_QUENCH    = 0.25 * TC    # quench temperature (domains coarsen here)

# ── Monte Carlo schedule ───────────────────────────────────────────────────────
N_EQUIL     = 5_000        # sweeps to reach equilibrium (discarded)
N_PROD      = 2_000        # production sweeps (for statistics)
# one sweep = N² attempted single-spin flips via checkerboard
N_SWEEPS_COLD   = N_EQUIL + N_PROD
N_SWEEPS_CRIT   = N_EQUIL + N_PROD
N_SWEEPS_HOT    = N_EQUIL + N_PROD
N_SWEEPS_QUENCH = 2_000    # quench: fewer sweeps → domain walls still visible

SEED = 0xC0BALT

# ── mesh geometry ─────────────────────────────────────────────────────────────
WORLD_SCALE = 4.0          # mesh spans [−WORLD_SCALE, +WORLD_SCALE] in X and Y
Z_SCALE     = 0.35         # height of up-spin (+1) above plane

# ── material ───────────────────────────────────────────────────────────────────
ATTR_NAME   = "Ising_Spin"
OBJ_NAME    = "ising_spin_floor"
MAT_NAME    = "MAT_ising_spin_floor"

COBALT = (0.027, 0.159, 0.557, 1.0)   # down-spin (s = −1)
AMBER  = (0.980, 0.620, 0.050, 1.0)   # up-spin   (s = +1)

# ── holoflow metadata ─────────────────────────────────────────────────────────
HOLOFLOW_CATEGORY = "stage-floor"
HOLOFLOW_FACET    = True


# ──────────────────────────────────────────────────────────────────────────────
# METROPOLIS CORE (checkerboard vectorised)
# ──────────────────────────────────────────────────────────────────────────────

def _metropolis_sweep(spins: np.ndarray, T: float, rng: np.random.Generator,
                      parity: int) -> None:
    """In-place checkerboard Metropolis sweep for one colour (parity 0 or 1).

    WHY checkerboard: sites of the same colour share no nearest neighbour on
    a square lattice, so all their flip decisions are conditionally independent
    — we can vectorise them with NumPy without violating detailed balance.
    """
    N = spins.shape[0]
    # build index arrays for the chosen sublattice parity
    rows, cols = np.meshgrid(np.arange(N), np.arange(N), indexing="ij")
    mask = ((rows + cols) % 2) == parity

    ri = rows[mask]
    ci = cols[mask]

    # nearest-neighbour sum (periodic boundary conditions via modulo)
    nn_sum = (
        spins[(ri + 1) % N, ci]
        + spins[(ri - 1) % N, ci]
        + spins[ri, (ci + 1) % N]
        + spins[ri, (ci - 1) % N]
    )
    # energy change if we flip spin i
    dE = 2.0 * J * spins[ri, ci] * nn_sum

    # Metropolis acceptance: accept if ΔE ≤ 0 or with probability exp(−ΔE/T)
    accept = (dE <= 0) | (rng.random(ri.size) < np.exp(-dE / (K_B * T)))
    spins[ri[accept], ci[accept]] *= -1


def run_ising(T: float, n_sweeps: int, rng: np.random.Generator,
              start: str = "random") -> np.ndarray:
    """Run the Metropolis algorithm and return the spin lattice.

    Parameters
    ----------
    T        : temperature (in units J/k_B)
    n_sweeps : total number of lattice sweeps to perform
    rng      : NumPy Generator for reproducibility
    start    : 'random' — infinite-temperature initial condition
               'ordered'— fully magnetised (T→0 initial condition)
    """
    if start == "ordered":
        spins = np.ones((N, N), dtype=np.int8)
    else:
        spins = rng.choice([-1, 1], size=(N, N)).astype(np.int8)

    for _ in range(n_sweeps):
        _metropolis_sweep(spins, T, rng, parity=0)
        _metropolis_sweep(spins, T, rng, parity=1)

    return spins


# ──────────────────────────────────────────────────────────────────────────────
# MESH BUILDER
# ──────────────────────────────────────────────────────────────────────────────

def _build_base_mesh(spins: np.ndarray) -> bpy.types.Object:
    """Create an N×N quad grid from the spin field; return the object.

    Vertex layout: row-major (ix, iy) → vertex index ix*N + iy.
    Faces: CCW quads.  Z from spin field.
    """
    xs = np.linspace(-WORLD_SCALE, WORLD_SCALE, N)
    ys = np.linspace(-WORLD_SCALE, WORLD_SCALE, N)
    xx, yy = np.meshgrid(xs, ys, indexing="ij")

    # spin ∈ {−1, +1} → height ∈ {0, Z_SCALE}
    zz = ((spins.astype(float) + 1.0) / 2.0) * Z_SCALE

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


def _set_vertex_colour(obj: bpy.types.Object, spins: np.ndarray) -> None:
    """Write per-vertex FLOAT_COLOR attribute (cobalt → amber for down → up).

    We store colours on POINT domain so each vertex has one colour,
    matching the spin at that lattice site.
    """
    mesh = obj.data

    if ATTR_NAME in mesh.attributes:
        mesh.attributes.remove(mesh.attributes[ATTR_NAME])

    attr = mesh.attributes.new(name=ATTR_NAME, type="FLOAT_COLOR", domain="POINT")
    n_verts = len(mesh.vertices)

    flat = spins.ravel()                        # length N²
    t = ((flat.astype(float) + 1.0) / 2.0)     # 0 = down (cobalt), 1 = up (amber)

    colours = np.empty(n_verts * 4, dtype=np.float32)
    for ch, (c0, c1) in enumerate(zip(COBALT, AMBER)):
        colours[ch::4] = c0 + t * (c1 - c0)

    attr.data.foreach_set("color", colours)


def _add_shape_key(obj: bpy.types.Object, spins: np.ndarray, name: str) -> None:
    """Add a shape key that sets vertex Z heights from a spin field."""
    mesh = obj.data
    flat = spins.ravel().astype(float)
    zz = ((flat + 1.0) / 2.0) * Z_SCALE

    sk = obj.shape_key_add(name=name, from_mix=False)

    coords = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
    mesh.vertices.foreach_get("co", coords)
    coords[2::3] = zz.astype(np.float32)
    sk.data.foreach_set("co", coords)


def _build_material(obj: bpy.types.Object) -> None:
    """Principled BSDF + Emission driven by the Ising_Spin colour attribute."""
    mat = bpy.data.materials.new(MAT_NAME)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    attr  = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = ATTR_NAME
    attr.location = (-400, 0)

    bsdf  = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (-100, 0)
    bsdf.inputs["Metallic"].default_value    = 0.10
    bsdf.inputs["Roughness"].default_value   = 0.30
    # Emission from attribute colour, strength 1.6 for WebXR bloom
    bsdf.inputs["Emission Strength"].default_value = 1.6

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (200, 0)

    nt.links.new(attr.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(attr.outputs["Color"], bsdf.inputs["Emission Color"])
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    # --- wipe scene ---
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)

    rng = default_rng(SEED)

    # ── run four simulations ──
    print(f"Running Ising MC:  Tc = {TC:.4f}")

    # 1. Cold — deep ferromagnet (start ordered so magnetisation is positive)
    print(f"  Cold  T = {T_COLD:.4f}  ({N_SWEEPS_COLD} sweeps)")
    s_cold   = run_ising(T_COLD,   N_SWEEPS_COLD,   rng, start="ordered")

    # 2. Critical — Onsager Tc, fractal domain structure
    print(f"  Crit  T = {T_CRIT:.4f}  ({N_SWEEPS_CRIT} sweeps)")
    s_crit   = run_ising(T_CRIT,   N_SWEEPS_CRIT,   rng, start="random")

    # 3. Hot — well above Tc, disordered paramagnet
    print(f"  Hot   T = {T_HOT:.4f}  ({N_SWEEPS_HOT} sweeps)")
    s_hot    = run_ising(T_HOT,    N_SWEEPS_HOT,    rng, start="random")

    # 4. Quench — start from infinite-T random state, quench to cold T
    #    Few sweeps so domain walls from coarsening are visible
    print(f"  Quench T = {T_QUENCH:.4f}  ({N_SWEEPS_QUENCH} sweeps)")
    s_quench = run_ising(T_QUENCH, N_SWEEPS_QUENCH, rng, start="random")

    # ── build mesh from Basis (cold) ──
    obj = _build_base_mesh(s_cold)
    _set_vertex_colour(obj, s_cold)

    # Basis shape key
    sk_basis = obj.shape_key_add(name="Basis", from_mix=False)

    # set Basis key z directly from cold spins
    mesh   = obj.data
    n_verts = len(mesh.vertices)
    flat_cold = s_cold.ravel().astype(float)
    zz_cold = ((flat_cold + 1.0) / 2.0) * Z_SCALE
    coords = np.empty(n_verts * 3, dtype=np.float32)
    mesh.vertices.foreach_get("co", coords)
    coords[2::3] = zz_cold.astype(np.float32)
    sk_basis.data.foreach_set("co", coords)

    _add_shape_key(obj, s_crit,   "SK_Critical")
    _add_shape_key(obj, s_hot,    "SK_Hot")
    _add_shape_key(obj, s_quench, "SK_Quench")

    # ── material ──
    _build_material(obj)

    # ── holoflow metadata ──
    obj["holoflow:category"] = HOLOFLOW_CATEGORY
    obj["holoflow:facet"]    = HOLOFLOW_FACET

    # ── apply rotation for +Y-up WebXR export ──
    import mathutils
    obj.rotation_euler = mathutils.Euler((-3.14159265 / 2.0, 0.0, 0.0), "XYZ")
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(rotation=True)

    # ── diagnostics ──
    m_cold  = s_cold.mean()
    m_crit  = s_crit.mean()
    m_hot   = s_hot.mean()
    print(f"\nDiagnostics:")
    print(f"  ⟨m⟩ cold   = {m_cold:+.4f}  (expected |m| > 0.95 at T/Tc=0.5)")
    print(f"  ⟨m⟩ crit   = {m_crit:+.4f}  (expected |m| ≈ 0.04–0.15)")
    print(f"  ⟨m⟩ hot    = {m_hot:+.4f}   (expected |m| < 0.05)")

    print(f"\n[DONE] Object '{OBJ_NAME}' created.")
    print(f"       Vertices  : {N * N:,}")
    print(f"       Quad faces: {(N - 1) ** 2:,}")
    print(f"       Shape keys: Basis / SK_Critical / SK_Hot / SK_Quench")
    print(f"       Attribute : {ATTR_NAME}  FLOAT_COLOR  POINT")
    print(f"       Tc exact  : {TC:.6f} J/k_B")


if __name__ == "__main__":
    main()
