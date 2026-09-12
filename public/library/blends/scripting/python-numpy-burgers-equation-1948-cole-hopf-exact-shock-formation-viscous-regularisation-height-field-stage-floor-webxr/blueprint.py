"""
Burgers Equation — Cole-Hopf Exact Solution, Shock Formation,
Viscous Regularisation: Space-Time Height-Field Stage Floor

TECHNIQUE : Blender 5.1 · Python + NumPy · bpy direct-data API · CC0
EQUATION  : ∂u/∂t + u ∂u/∂x = ν ∂²u/∂x²   (Burgers 1948)
TRANSFORM : Cole-Hopf  u = −2ν ∂ ln φ/∂x  reduces to heat equation
            ∂φ/∂t = ν ∂²φ/∂x²  (Hopf 1950, Cole 1951)
SOLUTION  : EXACT — no time-stepping; Fourier heat-kernel propagation
            φ̂(k,t) = φ̂₀(k) · exp(−νk²t)
IC        : u₀ = −sin(πx)  on x ∈ [−1, 1]  (periodic, period 2)
            Shock forms at x=0,  t_shock = 1/π ≈ 0.318
GEOMETRY  : 128×128 height-field floor; x=space, y=time, z=u(x,t)
SHAPE KEYS:
  Basis     u₀=−sin(πx)   ν=0.010  moderate shock
  SK_HighNu u₀=−sin(πx)   ν=0.100  over-damped, shock dissolved
  SK_LowNu  u₀=−sin(πx)   ν=0.005  near-inviscid, sharp shock layer
  SK_NWave  u₀=−sin(2πx)  ν=0.010  N-wave, two simultaneous shocks

Run in Blender 5.1 → Scripting workspace → Run Script.
Output: burgers_shock_floor.blend  +  burgers_shock_floor.glb
"""

import bpy
import math
import numpy as np
import pathlib

# ── Grid constants ─────────────────────────────────────────────────────────────
N_X      = 128        # spatial points on x ∈ [−1, 1]   (power of 2 for FFT)
N_T      = 128        # time-sample rows in the mesh
L        = 2.0        # domain length (period)
T_FINAL  = 1.5        # simulate to t = 1.5  (shock ≈ 0.318, well resolved)

# ── World-space scaling ────────────────────────────────────────────────────────
X_WORLD  = 2.0        # x ∈ [−1, 1] → world ∈ [−2, 2]
T_WORLD  = 3.0        # t ∈ [0, T_FINAL] → world y ∈ [0, 3]
Z_SCALE  = 0.22       # metres per unit of u

# ── Colour palette (RGBA linear) ───────────────────────────────────────────────
COL_NEG  = (0.030, 0.150, 0.580, 1.0)   # cobalt   (u < 0)
COL_ZERO = (0.050, 0.200, 0.200, 1.0)   # dark teal (u = 0)
COL_POS  = (1.000, 0.650, 0.000, 1.0)   # amber     (u > 0)
U_NORM   = 1.0                           # colour clamp at ±U_NORM

# ── Names ─────────────────────────────────────────────────────────────────────
ATTR_NAME  = "Burgers_Vel"
OBJ_NAME   = "burgers_shock_floor"
BLEND_NAME = "burgers_shock_floor.blend"
GLB_NAME   = "burgers_shock_floor.glb"


# ── Cole-Hopf exact solver ─────────────────────────────────────────────────────

def _cole_hopf(u0: np.ndarray, nu: float) -> np.ndarray:
    """
    Return space-time field u[N_T, N_X] via the Cole-Hopf transformation.

    1. Spectral antiderivative:  θ̂ = û₀/(ik),  k ≠ 0  →  θ = ∫u₀ dξ
    2. Cole-Hopf initial data:   φ₀ = exp(−θ/(2ν))
       (subtract mean of θ to keep exp in float64 range)
    3. Exact heat-equation evolution: φ̂(k,t) = φ̂₀(k)·exp(−νk²t)
    4. Recover velocity: u = −2ν · IFFT(ik·φ̂) / IFFT(φ̂)
    """
    k  = 2.0 * math.pi * np.fft.fftfreq(N_X, d=L / N_X)
    ik = 1j * k

    # 1 — spectral antiderivative
    u0_hat = np.fft.fft(u0)
    th_hat = np.zeros(N_X, dtype=complex)
    nz     = k != 0
    th_hat[nz] = u0_hat[nz] / ik[nz]
    theta  = np.fft.ifft(th_hat).real

    # 2 — Cole-Hopf initial data (centre θ to avoid overflow)
    phi0_hat = np.fft.fft(np.exp(-(theta - theta.mean()) / (2.0 * nu)))

    # 3 & 4 — exact evolution + velocity recovery
    t_arr = np.linspace(0.0, T_FINAL, N_T)
    k2    = k * k
    u_st  = np.empty((N_T, N_X))
    u_st[0] = u0

    for i in range(1, N_T):
        ph_hat  = phi0_hat * np.exp(-nu * k2 * t_arr[i])
        phi     = np.fft.ifft(ph_hat).real
        dphi_dx = np.fft.ifft(ik * ph_hat).real
        eps     = max(float(np.abs(phi).max()) * 1e-12, 1e-300)
        phi_safe = np.where(np.abs(phi) < eps,
                            np.sign(phi + 1e-300) * eps, phi)
        u_st[i] = -2.0 * nu * dphi_dx / phi_safe

    return u_st


# ── Mesh helpers ───────────────────────────────────────────────────────────────

def _verts_faces(u_st: np.ndarray):
    """Flat vertex list and quad faces for a 2-D height field."""
    x  = np.linspace(-1.0, 1.0, N_X, endpoint=False)
    t  = np.linspace(0.0, T_FINAL, N_T)
    xx, tt = np.meshgrid(x, t)            # shape (N_T, N_X)
    vx = (xx * X_WORLD).ravel()
    vy = (tt * (T_WORLD / T_FINAL)).ravel()
    vz = (u_st * Z_SCALE).ravel()
    verts = np.column_stack([vx, vy, vz])

    faces = []
    for r in range(N_T - 1):
        for c in range(N_X - 1):
            i0 = r * N_X + c
            faces.append((i0, i0 + 1, i0 + N_X + 1, i0 + N_X))
    return verts.tolist(), faces


def _apply_colour(me, u_st: np.ndarray) -> None:
    """Assign signed cobalt-teal-amber colour per vertex."""
    if ATTR_NAME not in me.attributes:
        me.attributes.new(name=ATTR_NAME, type='FLOAT_COLOR', domain='POINT')
    attr = me.attributes[ATTR_NAME]
    u_f  = u_st.ravel() / U_NORM
    n    = len(u_f)
    cols = np.empty((n, 4))
    pos_t = np.clip(u_f,  0.0, 1.0)
    neg_t = np.clip(-u_f, 0.0, 1.0)
    for ch in range(4):
        pos_c = (1.0 - pos_t) * COL_ZERO[ch] + pos_t * COL_POS[ch]
        neg_c = (1.0 - neg_t) * COL_ZERO[ch] + neg_t * COL_NEG[ch]
        cols[:, ch] = np.where(u_f >= 0, pos_c, neg_c)
    attr.data.foreach_set("color", cols.ravel().tolist())


def _add_shape_key(ob, u_st: np.ndarray, name: str):
    """Append a shape key from a new height field."""
    sk = ob.shape_key_add(name=name, from_mix=False)
    x  = np.linspace(-1.0, 1.0, N_X, endpoint=False)
    t  = np.linspace(0.0, T_FINAL, N_T)
    xx, tt = np.meshgrid(x, t)
    coords = np.column_stack([
        (xx * X_WORLD).ravel(),
        (tt * (T_WORLD / T_FINAL)).ravel(),
        (u_st * Z_SCALE).ravel(),
    ]).ravel().tolist()
    sk.data.foreach_set("co", coords)
    return sk


# ── Material ───────────────────────────────────────────────────────────────────

def _make_material(ob) -> None:
    """Principled BSDF + emissive glow reading Burgers_Vel colour attribute."""
    mat  = bpy.data.materials.new("Burgers_Mat")
    mat.use_nodes = True
    nt   = mat.node_tree
    nt.nodes.clear()

    out  = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = ATTR_NAME

    bsdf.inputs["Roughness"].default_value         = 0.35
    bsdf.inputs["Metallic"].default_value          = 0.10
    bsdf.inputs["Emission Strength"].default_value = 0.25

    nt.links.new(attr.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(attr.outputs["Color"], bsdf.inputs["Emission Color"])
    nt.links.new(bsdf.outputs["BSDF"],  out.inputs["Surface"])
    out.location  = (400, 0)
    bsdf.location = (100, 0)
    attr.location = (-200, 0)

    if ob.data.materials:
        ob.data.materials[0] = mat
    else:
        ob.data.materials.append(mat)
    mat["holoflow:facet"]    = False
    mat["holoflow:category"] = "stage-floor"


# ── GLB export ─────────────────────────────────────────────────────────────────

def _export(ob) -> None:
    here = pathlib.Path(bpy.path.abspath("//"))
    glb  = here / GLB_NAME
    bpy.ops.export_scene.gltf(
        filepath                             = str(glb),
        use_selection                        = True,
        export_format                        = 'GLB',
        export_draco_mesh_compression_enable = True,
        export_draco_mesh_compression_level  = 6,
        export_image_format                  = 'WEBP',
        export_morph                         = True,
        export_colors                        = True,
        export_yup                           = True,
    )
    print(f"[blueprint] GLB → {glb}")


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    x = np.linspace(-1.0, 1.0, N_X, endpoint=False)

    # ── Basis: u₀ = −sin(πx), ν = 0.010 ──────────────────────────────────────
    u0_base = -np.sin(math.pi * x)
    u_basis = _cole_hopf(u0_base, nu=0.010)

    verts, faces = _verts_faces(u_basis)
    me = bpy.data.meshes.new(OBJ_NAME)
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(OBJ_NAME, me)
    bpy.context.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)

    _apply_colour(me, u_basis)
    ob.shape_key_add(name="Basis", from_mix=False)          # required reference

    # ── SK_HighNu: ν = 0.100 — over-damped, shock dissolved ───────────────────
    _add_shape_key(ob, _cole_hopf(u0_base, nu=0.100), "SK_HighNu")

    # ── SK_LowNu: ν = 0.005 — near-inviscid, sharp shock layer ────────────────
    _add_shape_key(ob, _cole_hopf(u0_base, nu=0.005), "SK_LowNu")

    # ── SK_NWave: u₀ = −sin(2πx), ν = 0.010 — N-wave, two shocks ─────────────
    u0_nw = -np.sin(2.0 * math.pi * x)
    _add_shape_key(ob, _cole_hopf(u0_nw,   nu=0.010), "SK_NWave")

    _make_material(ob)

    here  = pathlib.Path(bpy.path.abspath("//"))
    blend = here / BLEND_NAME
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    print(f"[blueprint] .blend → {blend}")

    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    _export(ob)


main()
