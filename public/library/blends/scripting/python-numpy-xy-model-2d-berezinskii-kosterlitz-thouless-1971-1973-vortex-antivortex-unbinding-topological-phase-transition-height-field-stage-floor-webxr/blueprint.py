"""
2D XY Model — Berezinskii-Kosterlitz-Thouless Transition
Berezinskii 1971 · Kosterlitz & Thouless 1973 · Nobel Prize 2016

THE PHYSICS
-----------
The 2D classical XY model places unit-vector spins (cos θᵢ, sin θᵢ) on a
square lattice. The Hamiltonian is purely nearest-neighbour:

    H = −J Σ_{⟨ij⟩} cos(θᵢ − θⱼ)    θᵢ ∈ [0, 2π)

Unlike the Ising model the spin has a continuous U(1) symmetry.  The
Mermin-Wagner theorem (1966) proves this symmetry *cannot* be broken at
any finite temperature in 2D: conventional ferromagnetic order is
forbidden.  Yet experiment shows the 2D XY universality class (helium
films, Josephson arrays, planar magnets) exhibits a sharp phase transition.

The resolution — discovered by Berezinskii (1971) and Kosterlitz-Thouless
(1973) — is topological.  The key objects are **vortices**: configurations
in which the phase angle θ winds by ±2π around a plaquette.  The topological
charge (winding number) q = ±1 is conserved modulo 2π.

Below T_BKT vortices and antivortices are bound in tight pairs; the system
has *quasi-long-range order*:

    G(r) = ⟨cos(θ₀ − θᵣ)⟩  ~  r^{−η(T)}     (algebraic decay)

where η(T) = k_B T / (2π J) ↗ 1/4 as T → T_BKT from below.

At T_BKT the vortex pairs unbind.  Above T_BKT free vortices proliferate
and correlations decay exponentially:

    G(r) ~ exp(−r / ξ)     ξ ~ exp(b / √(T − T_BKT))   (essential singularity)

The transition is *infinite order*: all derivatives of the free energy are
continuous at T_BKT (no Landau order parameter).

Square-lattice Monte Carlo gives T_BKT ≈ 0.8935 J/k_B (Hasenbusch 2005,
PRB 71:184420; VCTM 2006).

Nelson-Kosterlitz universal jump (1977):  just below T_BKT the superfluid
stiffness (helicity modulus) ρs satisfies:

    lim_{T→T_BKT^{-}} ρs(T) / T_BKT = 2/π  ≈ 0.6366

This discontinuous jump in ρs is the experimental signature of BKT.

METROPOLIS ALGORITHM (checkerboard vectorised)
----------------------------------------------
For the continuous XY model the standard Metropolis move proposes
    θᵢ_new = θᵢ + δ,    δ ~ Uniform(−DELTA, +DELTA)
and accepts with  min(1, exp(−ΔE / k_B T)).  ΔE only depends on the four
nearest-neighbour angles, so the checkerboard decomposition (even/odd
sublattice) still works: all sites of one colour can be updated
simultaneously because no two share a nearest neighbour.

WHY cosine height field?
The scalar  z(i,j) = cos(θ(i,j))  makes vortex topology visible: each
vortex core is a phase singularity surrounded by a smooth winding, which
maps to a characteristic cos-wave ripple around the defect.  Bound
vortex-antivortex pairs produce paired ripples; free vortices produce
isolated spirals.  Below T_BKT the field is nearly flat (all angles
similar); above T_BKT it looks like random noise.

SHAPE KEYS
----------
  Basis         T = 0.40 T_BKT  — quasi-LRO, large spin-wave background
  SK_BKT        T = T_BKT       — critical, algebraic G(r) ~ r^{−1/4}
  SK_Unbound    T = 1.20 T_BKT  — free vortices, exponential decay
  SK_HighT      T = 2.50 T_BKT  — disordered, random phase

PARAMETERS (all named constants — change here only)
"""

import bpy
import bmesh
import numpy as np
from numpy.random import default_rng

# ── lattice ────────────────────────────────────────────────────────────────────
N            = 128          # grid points per side  (128×128 = 16 384 spins)
J            = 1.0          # ferromagnetic coupling (J > 0)
K_B          = 1.0          # Boltzmann constant (natural units)

# Square-lattice BKT critical temperature (Hasenbusch 2005 PRB 71:184420)
T_BKT        = 0.8935       # in units where J = k_B = 1

T_BELOW      = 0.40 * T_BKT   # ≈ 0.357  well below BKT: quasi-LRO
T_CRIT       = 1.00 * T_BKT   # ≈ 0.894  critical
T_ABOVE      = 1.20 * T_BKT   # ≈ 1.072  above BKT: free vortices
T_HIGH       = 2.50 * T_BKT   # ≈ 2.234  high-T disordered

# ── Metropolis move width ──────────────────────────────────────────────────────
DELTA_ANGLE  = np.pi / 4.0   # proposal width;  wider → faster decorrelation
                              # π/4 is a good balance for T ~ J

# ── MC schedule ───────────────────────────────────────────────────────────────
N_EQUIL      = 8_000         # sweeps to equilibrate (discarded)
N_PROD       = 2_000         # production sweeps (last config stored)
SEED         = 0x4B545F      # hex for "BKT_"

# ── mesh geometry ─────────────────────────────────────────────────────────────
WORLD_SCALE  = 4.0           # mesh spans [−WORLD_SCALE, +WORLD_SCALE]
Z_SCALE      = 0.45          # height range for cos(θ) ∈ [−1, +1]

# ── material / attribute ──────────────────────────────────────────────────────
ATTR_NAME    = "XY_CosTheta"
OBJ_NAME     = "xy_bkt_floor"
MAT_NAME     = "MAT_xy_bkt_floor"

COBALT = (0.027, 0.141, 0.557, 1.0)   # cos(θ) ≈ −1  (anti-aligned)
AMBER  = (0.980, 0.620, 0.050, 1.0)   # cos(θ) ≈ +1  (aligned)

# ── holoflow ──────────────────────────────────────────────────────────────────
HOLOFLOW_CATEGORY = "stage-floor"
HOLOFLOW_FACET    = True


# ──────────────────────────────────────────────────────────────────────────────
# XY METROPOLIS CORE (checkerboard vectorised)
# ──────────────────────────────────────────────────────────────────────────────

def _nn_sum_cos(theta: np.ndarray, delta: np.ndarray) -> np.ndarray:
    """
    Compute  Σ_{nn} cos(theta_new − θ_nn) − Σ_{nn} cos(theta_old − θ_nn)
    for all sites simultaneously.  Both theta and delta are (N, N) arrays.

    WHY: ΔE = −J · [Σ cos(θ_new − θ_nn) − Σ cos(θ_old − θ_nn)]
            = −J · Σ [cos(θ+δ − θ_nn) − cos(θ − θ_nn)]
    We use the product-to-sum identity only implicitly; rolling gives the
    four-neighbour arrays in O(N²) without explicit loops.
    """
    theta_new = theta + delta
    NN = (
        np.roll(theta, -1, axis=0) +   # south
        np.roll(theta, +1, axis=0) +   # north  (unused as array sum trick)
        np.roll(theta, -1, axis=1) +   # east
        np.roll(theta, +1, axis=1)     # west   — this is wrong; need per-nn
    )
    # Correct form: compute cos(θ_new − θ_nn) for each neighbour separately
    cos_new = (
        np.cos(theta_new - np.roll(theta, -1, axis=0)) +
        np.cos(theta_new - np.roll(theta, +1, axis=0)) +
        np.cos(theta_new - np.roll(theta, -1, axis=1)) +
        np.cos(theta_new - np.roll(theta, +1, axis=1))
    )
    cos_old = (
        np.cos(theta - np.roll(theta, -1, axis=0)) +
        np.cos(theta - np.roll(theta, +1, axis=0)) +
        np.cos(theta - np.roll(theta, -1, axis=1)) +
        np.cos(theta - np.roll(theta, +1, axis=1))
    )
    return cos_new - cos_old   # positive → more aligned → dE negative → favoured


def run_xy(T: float, n_sweeps: int, rng: np.random.Generator,
           theta_init: np.ndarray | None = None) -> np.ndarray:
    """
    Run the 2D XY Metropolis simulation at temperature T.

    Returns the final spin configuration theta (N × N float64, radians).

    WHY checkerboard? Sites of the same parity share no nearest neighbour,
    so all parity-0 (or parity-1) sites can be updated in one vectorised
    pass while satisfying detailed balance exactly.
    """
    if theta_init is None:
        theta = rng.uniform(0.0, 2.0 * np.pi, (N, N))
    else:
        theta = theta_init.copy()

    # Checkerboard masks: rows+cols even/odd
    ii, jj   = np.mgrid[0:N, 0:N]
    mask_0   = (ii + jj) % 2 == 0   # "white" squares
    mask_1   = ~mask_0               # "black" squares

    inv_T = 1.0 / (K_B * T)

    for _ in range(n_sweeps):
        for mask in (mask_0, mask_1):
            delta             = rng.uniform(-DELTA_ANGLE, DELTA_ANGLE, (N, N))
            delta[~mask]      = 0.0               # leave the other sublattice alone

            cos_diff = _nn_sum_cos(theta, delta)  # Σcos_new − Σcos_old per site
            dE       = -J * cos_diff              # energy change (negative = good)

            # Metropolis accept/reject
            log_r    = rng.random((N, N))
            accept   = (dE <= 0.0) | (log_r < np.exp(-dE * inv_T))
            accept  &= mask

            theta[accept] = (theta[accept] + delta[accept]) % (2.0 * np.pi)

    return theta


# ──────────────────────────────────────────────────────────────────────────────
# VORTEX DETECTION  (plaquette winding number)
# ──────────────────────────────────────────────────────────────────────────────

def _vortex_charge(theta: np.ndarray) -> np.ndarray:
    """
    Compute the integer vortex charge q(i,j) ∈ {−1, 0, +1} for every
    plaquette (i,j) → (i+1,j) → (i+1,j+1) → (i,j+1).

    The plaquette winding is the sum of four directed angle differences
    wrapped to (−π, π].  A winding of +2π → charge +1 (vortex);
    −2π → charge −1 (antivortex); 0 → regular.

    WHY: this is the discrete analogue of q = (1/2π) ∮ ∇θ · dl.  Only
    integer windings can appear (topological charge conservation).
    """
    def wrap(x):
        return (x + np.pi) % (2.0 * np.pi) - np.pi

    # Four bonds of each plaquette (periodic boundary conditions)
    d_right  = wrap(theta - np.roll(theta, -1, axis=1))   # (i,j) → (i,j+1)
    d_down   = wrap(np.roll(theta, -1, axis=1) -
                    np.roll(np.roll(theta, -1, axis=0), -1, axis=1))
    d_left   = wrap(np.roll(np.roll(theta, -1, axis=0), -1, axis=1) -
                    np.roll(theta, -1, axis=0))
    d_up     = wrap(np.roll(theta, -1, axis=0) - theta)

    winding  = d_right + d_down + d_left + d_up   # ≈ ±2π or ≈ 0
    charge   = np.round(winding / (2.0 * np.pi)).astype(np.int8)
    return charge   # shape (N, N)


# ──────────────────────────────────────────────────────────────────────────────
# HEIGHT FIELD: cos(θ)  with vortex-charge tint overlay
# ──────────────────────────────────────────────────────────────────────────────

def _cos_field_norm(theta: np.ndarray) -> np.ndarray:
    """
    Map  cos(θ) ∈ [−1, +1]  →  [0, 1]  for height / colour use.
    """
    return (np.cos(theta) + 1.0) / 2.0   # 0 = anti-aligned, 1 = aligned


# ──────────────────────────────────────────────────────────────────────────────
# MESH BUILDERS
# ──────────────────────────────────────────────────────────────────────────────

def _build_base_mesh(theta: np.ndarray) -> bpy.types.Object:
    """
    Build an N×N quad mesh with z = cos(theta) * Z_SCALE.
    Vertex layout: row-major (j outer, i inner) so face winding is CCW.
    """
    xs = np.linspace(-WORLD_SCALE, WORLD_SCALE, N)
    ys = np.linspace(-WORLD_SCALE, WORLD_SCALE, N)
    zz = _cos_field_norm(theta) * Z_SCALE   # (N, N)

    verts = []
    for j in range(N):
        for i in range(N):
            verts.append((xs[i], ys[j], float(zz[j, i])))

    faces = []
    for j in range(N - 1):
        for i in range(N - 1):
            v0 = j * N + i
            v1 = j * N + i + 1
            v2 = (j + 1) * N + i + 1
            v3 = (j + 1) * N + i
            faces.append((v0, v1, v2, v3))

    mesh = bpy.data.meshes.new(OBJ_NAME)
    mesh.from_pydata(verts, [], faces)
    mesh.validate()
    mesh.update()

    obj = bpy.data.objects.new(OBJ_NAME, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def _set_vertex_colour(obj: bpy.types.Object, theta: np.ndarray,
                       charge: np.ndarray | None = None) -> None:
    """
    Write the FLOAT_COLOR attribute  XY_CosTheta  as a POINT domain attribute.

    Colour: cobalt (θ anti-aligned, cos ≈ −1) → amber (θ aligned, cos ≈ +1).
    If vortex charge map is provided, vortex cores (|charge| = 1) are
    highlighted towards white to make them pop.
    """
    mesh = obj.data

    if ATTR_NAME not in mesh.attributes:
        mesh.attributes.new(ATTR_NAME, "FLOAT_COLOR", "POINT")

    attr        = mesh.attributes[ATTR_NAME]
    n_verts     = len(mesh.vertices)
    t_cos       = _cos_field_norm(theta).ravel().astype(np.float32)

    # Optional vortex highlight
    if charge is not None:
        # Smooth the vortex mask to highlight the immediate neighbourhood
        from numpy import abs as nabs
        vx = nabs(charge.astype(np.float32))
        for _ in range(3):
            vx = 0.5 * vx + 0.125 * (
                np.roll(vx, -1, 0) + np.roll(vx, 1, 0) +
                np.roll(vx, -1, 1) + np.roll(vx, 1, 1))
        vx = np.clip(vx.ravel(), 0.0, 1.0)
    else:
        vx = np.zeros(n_verts, dtype=np.float32)

    colours = np.empty(n_verts * 4, dtype=np.float32)
    for ch in range(3):
        base = COBALT[ch] + t_cos * (AMBER[ch] - COBALT[ch])
        # Vortex highlight: blend towards white (1, 1, 1)
        colours[ch::4] = base * (1.0 - vx) + vx * 1.0
    colours[3::4] = 1.0   # alpha

    attr.data.foreach_set("color", colours)


def _add_shape_key(obj: bpy.types.Object, theta: np.ndarray,
                   name: str, charge: np.ndarray | None = None) -> None:
    """Add a shape key that stores z = cos(theta) * Z_SCALE for every vertex."""
    sk  = obj.shape_key_add(name=name, from_mix=False)
    mesh = obj.data
    n_verts = len(mesh.vertices)

    zz   = _cos_field_norm(theta).ravel().astype(np.float32) * Z_SCALE
    coords = np.empty(n_verts * 3, dtype=np.float32)
    mesh.vertices.foreach_get("co", coords)
    coords[2::3] = zz
    sk.data.foreach_set("co", coords)

    # Each shape key also updates the colour attribute for visual clarity
    # (Blender doesn't animate colour via shape keys natively, but the
    # transition between shape keys reads the Basis colour at runtime; we
    # log the stats here for the screen-recording session)
    n_vortex = 0 if charge is None else int(np.sum(np.abs(charge)))
    print(f"  [{name}] vortex count ≈ {n_vortex}  "
          f"⟨cos θ⟩ = {np.cos(theta).mean():+.4f}")


def _build_material(obj: bpy.types.Object) -> None:
    """Principled BSDF + Emission driven by XY_CosTheta colour attribute."""
    mat = bpy.data.materials.new(MAT_NAME)
    mat.use_nodes = True
    nt  = mat.node_tree
    nt.nodes.clear()

    attr  = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = ATTR_NAME
    attr.location = (-400, 0)

    bsdf  = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (-100, 0)
    bsdf.inputs["Metallic"].default_value          = 0.15
    bsdf.inputs["Roughness"].default_value         = 0.30
    bsdf.inputs["Emission Strength"].default_value = 1.8   # WebXR bloom

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (200, 0)

    nt.links.new(attr.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(attr.outputs["Color"], bsdf.inputs["Emission Color"])
    nt.links.new(bsdf.outputs["BSDF"],  out.inputs["Surface"])

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

    print(f"XY Model — BKT transition   T_BKT = {T_BKT:.4f} J/k_B")

    # ── Run four temperatures ──────────────────────────────────────────────────
    print(f"  Below BKT  T = {T_BELOW:.4f}  ({N_EQUIL + N_PROD} sweeps)")
    theta_below = run_xy(T_BELOW, N_EQUIL + N_PROD, rng)

    print(f"  Critical   T = {T_CRIT:.4f}  ({N_EQUIL + N_PROD} sweeps)")
    theta_crit  = run_xy(T_CRIT,  N_EQUIL + N_PROD, rng)

    print(f"  Above BKT  T = {T_ABOVE:.4f}  ({N_EQUIL + N_PROD} sweeps)")
    theta_above = run_xy(T_ABOVE, N_EQUIL + N_PROD, rng)

    print(f"  High-T     T = {T_HIGH:.4f}  ({N_EQUIL + N_PROD} sweeps)")
    theta_high  = run_xy(T_HIGH,  N_EQUIL + N_PROD, rng)

    # ── vortex detection ──────────────────────────────────────────────────────
    charge_below = _vortex_charge(theta_below)
    charge_crit  = _vortex_charge(theta_crit)
    charge_above = _vortex_charge(theta_above)
    charge_high  = _vortex_charge(theta_high)

    # ── build mesh from Basis (below BKT) ────────────────────────────────────
    obj = _build_base_mesh(theta_below)
    _set_vertex_colour(obj, theta_below, charge_below)

    # Basis shape key
    sk_basis = obj.shape_key_add(name="Basis", from_mix=False)
    mesh     = obj.data
    n_verts  = len(mesh.vertices)
    zz       = _cos_field_norm(theta_below).ravel().astype(np.float32) * Z_SCALE
    coords   = np.empty(n_verts * 3, dtype=np.float32)
    mesh.vertices.foreach_get("co", coords)
    coords[2::3] = zz
    sk_basis.data.foreach_set("co", coords)
    n_vortex_below = int(np.sum(np.abs(charge_below)))
    print(f"  [Basis]       vortex count ≈ {n_vortex_below}  "
          f"⟨cos θ⟩ = {np.cos(theta_below).mean():+.4f}")

    _add_shape_key(obj, theta_crit,  "SK_BKT",     charge_crit)
    _add_shape_key(obj, theta_above, "SK_Unbound",  charge_above)
    _add_shape_key(obj, theta_high,  "SK_HighT",    charge_high)

    # ── material ──────────────────────────────────────────────────────────────
    _build_material(obj)

    # ── holoflow metadata ─────────────────────────────────────────────────────
    obj["holoflow:category"] = HOLOFLOW_CATEGORY
    obj["holoflow:facet"]    = HOLOFLOW_FACET

    # ── apply rotation for +Y-up WebXR export ─────────────────────────────────
    import mathutils
    obj.rotation_euler = mathutils.Euler((-np.pi / 2.0, 0.0, 0.0), "XYZ")
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(rotation=True)

    # ── diagnostics ───────────────────────────────────────────────────────────
    print("\nDiagnostics — vortex count (|+1| + |−1|) and mean cos(θ):")
    print(f"  Below  T={T_BELOW:.3f}: {int(np.sum(np.abs(charge_below)))} vortices  "
          f"⟨cos θ⟩={np.cos(theta_below).mean():+.4f}")
    print(f"  BKT    T={T_CRIT:.3f}: {int(np.sum(np.abs(charge_crit)))} vortices  "
          f"⟨cos θ⟩={np.cos(theta_crit).mean():+.4f}")
    print(f"  Above  T={T_ABOVE:.3f}: {int(np.sum(np.abs(charge_above)))} vortices  "
          f"⟨cos θ⟩={np.cos(theta_above).mean():+.4f}")
    print(f"  High-T T={T_HIGH:.3f}: {int(np.sum(np.abs(charge_high)))} vortices  "
          f"⟨cos θ⟩={np.cos(theta_high).mean():+.4f}")
    print(f"\n[DONE]  Object '{OBJ_NAME}' created.")
    print(f"        Vertices  : {N * N:,}")
    print(f"        Quad faces: {(N - 1) ** 2:,}")
    print(f"        Shape keys: Basis / SK_BKT / SK_Unbound / SK_HighT")
    print(f"        Attribute : {ATTR_NAME}  FLOAT_COLOR  POINT")
    print(f"        T_BKT     : {T_BKT:.4f} J/k_B  (Hasenbusch 2005)")


if __name__ == "__main__":
    main()
