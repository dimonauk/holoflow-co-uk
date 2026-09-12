"""
φ⁴ Scalar Field Theory — Kink-Antikink Collision and Resonance Windows
Campbell-Schonfeld-Wingate 1983 · Space-Time Height-Field Stage Floor

TECHNIQUE : Blender 5.1 · Python + NumPy · bpy direct-data API · CC0
EQUATION  : ∂²φ/∂t² = ∂²φ/∂x² + φ − φ³       [EOM from V(φ) = ¼(1−φ²)²]
            V'(φ) = φ(φ²−1)  →  EOM: φ_tt − φ_xx = φ − φ³
KINK IC   : φ(x,0) = tanh[γ(x+a)/√2] − tanh[γ(x−a)/√2] − 1
            φ_t(0) = −(vγ/√2)[sech²(γ(x+a)/√2) + sech²(γ(x−a)/√2)]
            γ = 1/√(1−v²)  Lorentz factor,  a = initial half-separation
SOLVER    : Leapfrog (Störmer-Verlet) — 2nd-order, time-reversible, symplectic
            φⁿ⁺¹ = 2φⁿ − φⁿ⁻¹ + DT²·[φ_xx + φ − φ³]
            Stability: DT/DX < 1  (CFL,  wave speed c = 1)
GEOMETRY  : 128×128 height-field stage floor
            x-axis = space  ∈ [−6, 6],   world ∈ [−2, 2] m
            y-axis = time   ∈ [0, 30],   world ∈ [ 0, 3] m
            z      = (φ+1)·Z_SCALE       (vacuum φ=−1 → z=0)
SHAPE KEYS:
  Basis        v=0.10  below v_c — kinks captured, oscillating bion forever
  SK_TwoBounce v=0.193 two-bounce resonance window — escape after two collisions
  SK_Critical  v=0.26  near critical v_c≈0.2598 — barely escape, dense radiation
  SK_Escape    v=0.40  well above v_c — clean single-pass escape with radiation plumes

Run in Blender 5.1 → Scripting workspace → Run Script.
Output: phi4_kink_floor.blend  +  phi4_kink_floor.glb
"""

import bpy
import math
import numpy as np
import pathlib

# ── Grid / integration constants ──────────────────────────────────────────────
N_X        = 128          # spatial grid points
N_T        = 128          # time-snapshot rows  (height-field y-axis)
L          = 12.0         # domain length, x ∈ [−L/2, L/2] = [−6, 6]
T_FINAL    = 30.0         # total simulation time
DT         = 0.04         # time step   (CFL: DT/DX = 0.04/0.094 ≈ 0.43 < 1 ✓)
INI_SEP    = 2.0          # initial kink centre distance from origin (a)

DX         = L / N_X      # ≈ 0.094 m (physical)
N_STEPS    = round(T_FINAL / DT)        # = 750 leapfrog steps

# ── World-space scaling ───────────────────────────────────────────────────────
X_WORLD    = 2.0          # half-width in metres
T_WORLD    = 3.0          # y-extent in metres
Z_SCALE    = 0.26         # metres per unit of (φ+1) — range 0→2 gives 0→0.52 m

# ── Colour palette (linear sRGB) ──────────────────────────────────────────────
COL_VAC    = (0.025, 0.130, 0.600, 1.0)   # cobalt  — vacuum, φ = −1
COL_MID    = (0.040, 0.320, 0.420, 1.0)   # teal    — mid-field, φ = 0
COL_TOP    = (1.000, 0.640, 0.010, 1.0)   # amber   — kink-core / false vacuum, φ = +1

# ── Object names ─────────────────────────────────────────────────────────────
ATTR_NAME  = "Phi4_Field"
OBJ_NAME   = "phi4_kink_floor"
BLEND_NAME = "phi4_kink_floor.blend"
GLB_NAME   = "phi4_kink_floor.glb"


# ── Physics helpers ───────────────────────────────────────────────────────────

def kink_antikink_ic(x: np.ndarray, v: float) -> tuple[np.ndarray, np.ndarray]:
    """
    Superposition IC for a kink (at −a, velocity +v) and antikink (at +a,
    velocity −v) approaching each other.

    WHY the minus-one shift: the kink alone gives φ(−∞)=−1, φ(+∞)=+1.
    The antikink gives the reverse.  Their sum gives 0 on both sides, not −1.
    The −1 offset restores the correct far-field vacuum φ = −1 everywhere
    outside the kink-antikink pair.

    WHY this is an approximation: the exact two-kink solution of φ⁴ is not
    known (unlike KdV or sine-Gordon, which are integrable).  The superposition
    is accurate when the separation 2a ≫ kink width √2 (here 2a/√2 ≈ 2.8 ≫ 1).
    """
    g   = 1.0 / math.sqrt(max(1e-12, 1.0 - v * v))   # Lorentz factor
    s   = math.sqrt(2.0)
    aL  = g * (x + INI_SEP) / s     # argument for left kink
    aR  = g * (x - INI_SEP) / s     # argument for right antikink
    phi0  = np.tanh(aL) - np.tanh(aR) - 1.0
    # Both kinks move inward → both contribute −vγ/√2 to φ_t at t=0
    phi_t = -(v * g / s) * (1.0 / np.cosh(aL) ** 2 + 1.0 / np.cosh(aR) ** 2)
    return phi0, phi_t


def laplacian1d(phi: np.ndarray) -> np.ndarray:
    """
    Centred finite-difference d²φ/dx² with Dirichlet BCs: φ[ghost] = −1.
    Dirichlet −1 is consistent with the asymptotic vacuum φ → −1 for both
    kink and antikink as x → ±∞; it prevents spurious reflections provided
    the disturbance never reaches the domain walls (verified below).
    """
    d2 = np.empty_like(phi)
    d2[1:-1] = (phi[2:] - 2.0 * phi[1:-1] + phi[:-2]) / DX ** 2
    d2[0]    = (phi[1]  - 2.0 * phi[0]    + (-1.0)) / DX ** 2   # left ghost
    d2[-1]   = ((-1.0)  - 2.0 * phi[-1]   + phi[-2]) / DX ** 2   # right ghost
    return d2


def rhs(phi: np.ndarray) -> np.ndarray:
    """
    EOM RHS: f(φ) = φ_xx + φ − φ³.

    V(φ) = ¼(1−φ²)²  has degenerate minima at φ = ±1 (Z₂ symmetry).
    V'(φ) = φ(φ²−1).  EOM: φ_tt − φ_xx = −V'(φ) = φ − φ³.

    The φ³ term makes φ⁴ non-integrable: unlike sine-Gordon (sin φ → φ−φ³/6+…
    which IS integrable via the inverse-scattering transform), φ⁴ kink-antikink
    collisions radiate energy and can form bound 'bion' states.  This is why
    the scattering is rich rather than trivially elastic.
    """
    return laplacian1d(phi) + phi - phi ** 3


def integrate(v_kink: float) -> np.ndarray:
    """
    Leapfrog integration; return space-time snapshot array st[N_T, N_X].

    Bootstrap step: φ⁻¹ = φ⁰ − DT·φ_t⁰ + ½DT²·f(φ⁰)
    (Taylor expansion, 2nd-order consistent with the leapfrog recurrence).

    Snapshot schedule: evenly spaced N_T frames from t=0 to t=T_FINAL.
    snap_frames[k] = round(k × N_STEPS / (N_T − 1))
    """
    x           = np.linspace(-L / 2, L / 2, N_X, endpoint=False)
    phi0, dpt0  = kink_antikink_ic(x, v_kink)
    phi_prev    = phi0 - DT * dpt0 + 0.5 * DT ** 2 * rhs(phi0)   # bootstrap
    phi_curr    = phi0.copy()

    snap_frames = np.round(np.linspace(0, N_STEPS, N_T)).astype(int)
    st          = np.empty((N_T, N_X), dtype=np.float64)
    snap_idx    = 0
    st[0]       = phi0
    snap_idx    = 1

    for step in range(1, N_STEPS + 1):
        phi_next = 2.0 * phi_curr - phi_prev + DT ** 2 * rhs(phi_curr)
        phi_prev, phi_curr = phi_curr, phi_next
        if snap_idx < N_T and step == snap_frames[snap_idx]:
            st[snap_idx] = phi_curr
            snap_idx += 1

    return st


# ── Mesh construction ─────────────────────────────────────────────────────────

def build_mesh(st: np.ndarray) -> tuple[list, list, list]:
    """
    Map the space-time field to a 128×128 vertex grid.
    Layout: x = space (world −X_WORLD…+X_WORLD), y = time (world 0…T_WORLD).
    Height z = max(0, φ+1)·Z_SCALE  — vacuum sits flush with the stage.
    Colour: three-stop ramp cobalt (φ=−1) → teal (φ=0) → amber (φ=+1).
    """
    verts, faces, col = [], [], []
    for it in range(N_T):
        for ix in range(N_X):
            phi_val = float(st[it, ix])
            wx = (ix / (N_X - 1) - 0.5) * 2.0 * X_WORLD
            wy = (it / (N_T - 1)) * T_WORLD
            wz = max(0.0, phi_val + 1.0) * Z_SCALE
            verts.append((wx, wy, wz))

            # Normalised field value t ∈ [0, 1] maps −1 → 0 (cobalt), +1 → 1 (amber)
            t = max(0.0, min(1.0, (phi_val + 1.0) * 0.5))
            if t < 0.5:
                s = 2.0 * t
                r = COL_VAC[0] + s * (COL_MID[0] - COL_VAC[0])
                g = COL_VAC[1] + s * (COL_MID[1] - COL_VAC[1])
                b = COL_VAC[2] + s * (COL_MID[2] - COL_VAC[2])
            else:
                s = 2.0 * t - 1.0
                r = COL_MID[0] + s * (COL_TOP[0] - COL_MID[0])
                g = COL_MID[1] + s * (COL_TOP[1] - COL_MID[1])
                b = COL_MID[2] + s * (COL_TOP[2] - COL_MID[2])
            col.append((r, g, b, 1.0))

    for it in range(N_T - 1):
        for ix in range(N_X - 1):
            v0 = it * N_X + ix
            faces.append((v0, v0 + 1, v0 + N_X + 1, v0 + N_X))

    return verts, faces, col


# ── Blender scene ─────────────────────────────────────────────────────────────

def build_scene() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)

    me = bpy.data.meshes.new(OBJ_NAME)
    ob = bpy.data.objects.new(OBJ_NAME, me)
    bpy.context.scene.collection.objects.link(ob)

    # ── Basis: v=0.10, deep-capture bion ──────────────────────────────────────
    st_b = integrate(0.10)
    verts_b, faces_b, col_b = build_mesh(st_b)
    me.from_pydata(verts_b, [], faces_b)
    me.update()

    for poly in me.polygons:
        poly.use_smooth = False

    # Colour attribute on Basis geometry
    attr = me.color_attributes.new(name=ATTR_NAME, type='FLOAT_COLOR', domain='POINT')
    attr.data.foreach_set("color", [c for rgba in col_b for c in rgba])

    # Shape-key Basis
    ob.shape_key_add(name="Basis", from_mix=False)

    # ── Additional shape keys ─────────────────────────────────────────────────
    for sk_name, v_kink in (
        ("SK_TwoBounce", 0.193),   # inside two-bounce resonance window (Campbell 1983)
        ("SK_Critical",  0.26),    # near v_c ≈ 0.2598, threshold region
        ("SK_Escape",    0.40),    # clean escape with radiation burst
    ):
        st_sk = integrate(v_kink)
        verts_sk, _, _ = build_mesh(st_sk)
        sk = ob.shape_key_add(name=sk_name, from_mix=False)
        sk.data.foreach_set("co", [c for v in verts_sk for c in v])

    me.update()

    # ── Material: attribute colour + emission glow ─────────────────────────────
    mat   = bpy.data.materials.new(name="phi4_mat")
    mat.use_nodes = True
    mat.use_backface_culling = False
    tree  = mat.node_tree
    nodes, links = tree.nodes, tree.links
    nodes.clear()

    out_n  = nodes.new("ShaderNodeOutputMaterial");  out_n.location  = (400, 0)
    mix_n  = nodes.new("ShaderNodeMixShader");       mix_n.location  = (200, 0)
    pbr_n  = nodes.new("ShaderNodeBsdfPrincipled");  pbr_n.location  = (0, -120)
    emi_n  = nodes.new("ShaderNodeEmission");        emi_n.location  = (0,  100)
    att_n  = nodes.new("ShaderNodeAttribute");       att_n.location  = (-220, 0)

    att_n.attribute_name = ATTR_NAME
    att_n.attribute_type = 'GEOMETRY'
    emi_n.inputs["Strength"].default_value = 1.6
    mix_n.inputs["Fac"].default_value = 0.35   # 35 % emission, 65 % PBR

    links.new(att_n.outputs["Color"], emi_n.inputs["Color"])
    links.new(att_n.outputs["Color"], pbr_n.inputs["Base Color"])
    links.new(emi_n.outputs["Emission"], mix_n.inputs[1])
    links.new(pbr_n.outputs["BSDF"],     mix_n.inputs[2])
    links.new(mix_n.outputs["Shader"],   out_n.inputs["Surface"])

    ob.data.materials.append(mat)

    # ── holoflow metadata ─────────────────────────────────────────────────────
    ob["holoflow:facet"]    = True
    ob["holoflow:category"] = "stage-floor"

    # ── +Y-up rotation (WebXR) ────────────────────────────────────────────────
    ob.rotation_euler[0] = -math.pi / 2
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.transform_apply(rotation=True)

    # ── GLB export ────────────────────────────────────────────────────────────
    out_dir = pathlib.Path(bpy.path.abspath("//"))
    bpy.ops.export_scene.gltf(
        filepath                             = str(out_dir / GLB_NAME),
        export_format                        = 'GLB',
        export_draco_mesh_compression_enable = True,
        export_draco_mesh_compression_level  = 6,
        export_image_format                  = 'WEBP',
        export_morph                         = True,
        export_colors                        = True,
        export_yup                           = True,
    )
    bpy.ops.wm.save_as_mainfile(filepath=str(out_dir / BLEND_NAME))
    print(f"[blueprint.py] Done → {BLEND_NAME}  +  {GLB_NAME}")


build_scene()
