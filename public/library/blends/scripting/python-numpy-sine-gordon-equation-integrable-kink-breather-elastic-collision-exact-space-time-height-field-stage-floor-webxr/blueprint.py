"""
Sine-Gordon Equation — Integrable 1+1D PDE
φ_tt − φ_xx + sin φ = 0

Exact multi-soliton solutions via inverse scattering / Bäcklund transform.
Scott, Chu, McLaughlin (1973) Proc. IEEE 61(10):1443-1483 — PD equations.
Ablowitz, Kaup, Newell, Segur (1973) PRL 30:1262 — AKNS inverse scattering.

WHY exact rather than numerical:
  Sine-Gordon is completely integrable — it possesses a Lax pair and an
  infinite tower of conserved charges. Every N-soliton solution is given
  by a closed algebraic formula via the Hirota τ-function. Using exact
  solutions shows the qualitative difference from φ⁴: here, kinks pass
  through each other ELASTICALLY with only a phase shift. In φ⁴ the
  interaction is inelastic and can trap a bion. A breather (oscillating
  kink-antikink bound state) exists in SG but not in φ⁴.

Four solution regimes → four Blender shape keys on a 128×128 space-time
height field. Spatial axis → world X, time axis → world Y, φ/(4π) → Z.
"""

import bpy
import math
import numpy as np

# ─────────────────────────────────────────────────────────────
# Parameters — safe to edit
# ─────────────────────────────────────────────────────────────
NX, NT         = 128, 128          # grid resolution (vertices per axis)
X_MIN, X_MAX   = -12.0, 12.0      # spatial domain; kink width ≈ 1 unit
T_MIN, T_MAX   =  -8.0,  8.0      # time domain
HEIGHT_SCALE   = 0.80              # metres: full φ ∈ [0, 4π] → HEIGHT_SCALE
FLOOR_W        = 4.0               # stage floor world width  (metres, X)
FLOOR_D        = 4.0               # stage floor world depth  (metres, Y)

# Single-kink / collision parameters
V_KINK         = 0.65              # kink velocity |v| < 1 (sub-luminal)

# Breather (SK_Breather)
OMEGA_B        = 0.50              # breather oscillation frequency ω ∈ (0,1)

# Two-kink (SK_TwoKink)
V1_TK, V2_TK  = 0.80, 0.30       # two kinks at different speeds
X01_TK         = -7.0              # initial position of faster kink
X02_TK         =  6.0             # initial position of slower kink

MESH_NAME      = "SineGordon_Floor"
ATTR_NAME      = "SG_Field"        # FLOAT_COLOR vertex attribute
OBJ_NAME       = "sg_floor"
EXPORT_PATH    = "//sine_gordon_floor.glb"


# ─────────────────────────────────────────────────────────────
# Exact solutions
# All formulae are public-domain mathematics; no third-party
# licence concerns.
# ─────────────────────────────────────────────────────────────

def _gamma(v):
    """Lorentz factor γ = 1/√(1 − v²). Clipped for numerical safety."""
    return 1.0 / math.sqrt(max(1.0 - v * v, 1e-10))


def phi_kink(X, T, v=0.65, x0=0.0):
    """
    Single kink (topological charge Q = +1):
      φ_K(x,t) = 4 arctan[exp(γ(x − vt − x₀))]

    As x → −∞: φ → 0 (vacuum).  As x → +∞: φ → 4π (vacuum).
    Width ∝ 1/γ (Lorentz-contracted at speed v).
    """
    g = _gamma(v)
    return 4.0 * np.arctan(np.exp(g * (X - v * T - x0)))


def phi_breather(X, T, omega=0.50):
    """
    Stationary breather — the kink-antikink bound state unique to SG:
      φ_B(x,t) = 4 arctan[(β/ω) sin(ωt) / cosh(βx)]  where β = √(1−ω²)

    Breather mass M_B = 16β < 2M_kink = 16 — it is genuinely bound.
    Oscillation frequency ω; spatial width ∝ 1/β.
    Limit ω → 0: two separated kink + antikink.
    Limit ω → 1: small-amplitude sine wave (phonon).

    WHY a breather exists in SG but NOT in φ⁴:
    The complete integrability of SG forbids energy loss to radiation
    during a kink-antikink approach, forcing the pair into a stable orbit.
    In φ⁴ the resonance windows allow quasi-periodic behaviour but slow
    radiation eventually destroys the bion.
    """
    beta = math.sqrt(max(1.0 - omega * omega, 1e-12))
    return 4.0 * np.arctan((beta / omega) * np.sin(omega * T) / np.cosh(beta * X))


def phi_kink_antikink(X, T, v=0.65):
    """
    Exact kink-antikink head-on collision (two-soliton):
      φ_{KĀ}(x,t) = 4 arctan[v sinh(γx) / cosh(γvt)]

    t → −∞: kink at x = +|v|t, antikink at x = −|v|t (approaching).
    t → +∞: kink at x = +|v|t − Δ, antikink at x = −|v|t + Δ (separating).

    Phase shift Δ = (2/γ) log(2v) — the solitons' only memory of the meeting.
    The collision is completely elastic: speeds and shapes unchanged.
    This is the experimental signature of integrability.
    """
    g = _gamma(v)
    # Guard the sinh/cosh argument against overflow at large |x|
    arg = g * X
    arg_clipped = np.clip(arg, -500.0, 500.0)
    denom_arg = g * v * T
    denom_clipped = np.clip(denom_arg, -500.0, 500.0)
    return 4.0 * np.arctan(
        v * np.sinh(arg_clipped) / np.cosh(denom_clipped)
    )


def phi_two_kink(X, T, v1=0.80, v2=0.30, x01=-7.0, x02=6.0):
    """
    Two co-propagating kinks at different speeds via additive superposition.
    Valid when the kinks are well-separated (separation ≫ kink width ≈ 1).
    The exact Bäcklund-composed two-kink differs by a phase shift that
    vanishes exponentially away from the interaction region.

    As t increases: faster kink (v₁ > v₂) eventually overtakes slower kink.
    After their elastic interaction both emerge with original speeds.
    """
    p1 = phi_kink(X, T, v=v1, x0=x01)
    p2 = phi_kink(X, T, v=v2, x0=x02)
    # Each kink adds 4π; total vacuum → 8π. Shift so basis starts at 0.
    return p1 + p2 - 4.0 * np.pi


# ─────────────────────────────────────────────────────────────
# Grid helpers
# ─────────────────────────────────────────────────────────────

def make_meshgrid():
    xi = np.linspace(X_MIN, X_MAX, NX)
    tj = np.linspace(T_MIN, T_MAX, NT)
    return xi, tj, *np.meshgrid(xi, tj, indexing="ij")   # X, T each (NX,NT)


def field_to_verts(phi, xi, tj):
    """Flatten φ(NX,NT) into vertex coordinates for bpy.types.Mesh.from_pydata."""
    scale_x = FLOOR_W / (X_MAX - X_MIN)
    scale_t = FLOOR_D / (T_MAX - T_MIN)
    h_norm  = HEIGHT_SCALE / (4.0 * math.pi)

    X_world = (xi[:, None] - X_MIN) * scale_x - FLOOR_W / 2.0   # (NX,1)
    T_world = (tj[None, :] - T_MIN) * scale_t - FLOOR_D / 2.0   # (1,NT)
    Z_world = phi * h_norm                                         # (NX,NT)

    # Stack and reshape to (NX*NT, 3)
    XW = np.broadcast_to(X_world, (NX, NT))
    TW = np.broadcast_to(T_world, (NX, NT))
    return np.stack([XW, TW, Z_world], axis=-1).reshape(-1, 3)


def make_quad_faces():
    """Row-major (x-major) CCW quad faces for a NX×NT grid."""
    faces = []
    for i in range(NX - 1):
        for j in range(NT - 1):
            v0 = i * NT + j
            v1 = v0 + 1
            v2 = (i + 1) * NT + (j + 1)
            v3 = (i + 1) * NT + j
            faces.append((v0, v1, v2, v3))
    return faces


# ─────────────────────────────────────────────────────────────
# Colour mapping — Cobalt → Amber by normalised φ ∈ [0, 4π]
# ─────────────────────────────────────────────────────────────
_COBALT = np.array([0.030, 0.150, 0.580, 1.0], dtype=np.float32)
_AMBER  = np.array([1.000, 0.650, 0.000, 1.0], dtype=np.float32)


def phi_to_rgba(phi):
    """Return flat float32 RGBA array (NX*NT * 4) for FLOAT_COLOR attribute."""
    t = np.clip(phi / (4.0 * math.pi), 0.0, 1.0).ravel()   # (NX*NT,)
    return (np.outer(1.0 - t, _COBALT) + np.outer(t, _AMBER)).astype(np.float32)


# ─────────────────────────────────────────────────────────────
# Blender scene
# ─────────────────────────────────────────────────────────────

def build_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.render.engine = "BLENDER_EEVEE_NEXT"

    xi, tj, X, T = make_meshgrid()
    faces = make_quad_faces()

    # ── Basis: single kink (kink origin offset so kink centre is in frame) ──
    phi_b = phi_kink(X, T, v=V_KINK, x0=-4.0)
    verts_b = field_to_verts(phi_b, xi, tj)

    mesh = bpy.data.meshes.new(MESH_NAME)
    mesh.from_pydata(verts_b.tolist(), [], faces)
    mesh.validate()

    obj = bpy.data.objects.new(OBJ_NAME, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj

    # FLOAT_COLOR attribute (Blender 4.x/5.x POINT domain)
    attr = mesh.attributes.new(ATTR_NAME, "FLOAT_COLOR", "POINT")
    attr.data.foreach_set("color", phi_to_rgba(phi_b).ravel())

    # ── Shape keys ──
    obj.shape_key_add(name="Basis", from_mix=False)

    def _sk(name, phi):
        sk = obj.shape_key_add(name=name, from_mix=False)
        sk.data.foreach_set("co", field_to_verts(phi, xi, tj).ravel())

    _sk("SK_Breather",  phi_breather(X, T, omega=OMEGA_B))
    _sk("SK_Collision", phi_kink_antikink(X, T, v=V_KINK))
    _sk("SK_TwoKink",   phi_two_kink(X, T, v1=V1_TK, v2=V2_TK, x01=X01_TK, x02=X02_TK))

    # ── Shade flat + metadata ──
    mesh.shade_flat()
    obj["holoflow:facet"]    = True
    obj["holoflow:category"] = "stage-floor"
    obj["holoflow:topic"]    = "sine-gordon-pde"

    # ── Emission material from vertex colour ──
    mat = bpy.data.materials.new("SG_Floor_Mat")
    mat.use_nodes = True
    t = mat.node_tree
    t.nodes.clear()
    out  = t.nodes.new("ShaderNodeOutputMaterial")
    emit = t.nodes.new("ShaderNodeEmission")
    att  = t.nodes.new("ShaderNodeAttribute")
    att.attribute_type  = "GEOMETRY"
    att.attribute_name  = ATTR_NAME
    emit.inputs["Strength"].default_value = 1.8
    t.links.new(att.outputs["Color"], emit.inputs["Color"])
    t.links.new(emit.outputs["Emission"], out.inputs["Surface"])
    mesh.materials.append(mat)

    # ── +Y-up transform ──
    obj.rotation_euler = (-math.pi / 2.0, 0.0, 0.0)
    bpy.ops.object.transform_apply(rotation=True)

    # ── GLB export ──
    bpy.ops.export_scene.gltf(
        filepath=EXPORT_PATH,
        export_format="GLB",
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_apply=True,
        export_morph=True,
        export_colors=True,
        export_yup=True,
        export_attributes=True,
        use_selection=False,
    )
    print("✓ Sine-Gordon stage floor exported →", EXPORT_PATH)


if __name__ == "__main__":
    build_scene()
