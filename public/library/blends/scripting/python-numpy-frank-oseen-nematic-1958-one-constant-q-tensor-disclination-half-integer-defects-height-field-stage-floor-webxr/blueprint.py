# ============================================================
# Frank-Oseen Nematic LC  |  One-Constant Approximation  |  Blender 5.1
# ============================================================
# Nematic liquid crystals (LCs) have orientational order described by a
# headless director n̂ ∈ RP¹ (n̂ ≡ −n̂). Frank & Oseen (1958) derived the
# elastic free energy for distortions of n̂ in terms of three modes:
#
#   f = ½K₁(∇·n̂)²  +  ½K₂(n̂·∇×n̂)²  +  ½K₃(n̂×∇×n̂)²
#          splay              twist               bend
#
# One-constant approximation (K₁=K₂=K₃=K) collapses to:
#   F = K/2 ∫|∇θ|² dA    where n̂ = (cosθ, sinθ)
# Euler–Lagrange equation:  ∇²θ = 0   (Laplace equation!)
#
# For N point disclinations at {(xₐ,yₐ)} with charges sₐ ∈ ½ℤ:
#   θ(x,y) = Σₐ sₐ · arctan2(y − yₐ, x − xₐ)
# WHY valid: ∇²arctan2(y,x) = 0 away from its pole, so each term is
# harmonic; the sum satisfies ∇²θ = 0 everywhere except the poles.
# Going around defect α once, the director rotates by 2π·sₐ.
# Nematics allow half-integer sₐ because n̂ ≡ −n̂ — a 180° rotation
# of n̂ is physically indistinguishable from the identity.
#
# Order parameter (Landau–de Gennes):
#   S(x,y) = 1 − exp(−d_min² / ξ²)
# where d_min = min distance to any defect, ξ = R_CORE (coherence length).
# S=0 at the isotropic defect core; S→1 in the aligned bulk.
#
# Height: Z = S × Z_SCALE  (pits mark defect core positions)
# Colour: (θ mod π)/π → COBALT (0) … AMBER (1)  [Z₂ period = π]
#
# Shape keys:
#   Basis       — +½,+½,−½,−½ quadrupole (charge-neutral, most common
#                 experimental texture in confined planar cells)
#   SK_Comet    — single +½ disclination: comet / radial pattern
#   SK_Hedgehog — single +1 integer defect: hedgehog / radial escape
#   SK_Anneal   — close ±½ pair near annihilation (charge = 0)
#
# Artefacts: lc_nematic_floor.blend · lc_nematic_floor.glb (Draco 6 / WebP)
# ============================================================

import bpy, math
import numpy as np

# ── Parameters ───────────────────────────────────────────────
N        = 128           # N×N = 16 384 vertices; (N-1)² = 16 129 quads
R_CORE   = 0.14          # Frank coherence length ξ in [−1,1] domain units
Z_SCALE  = 0.40          # max height amplitude (metres)
OBJ_NAME = "lc_nematic_floor"
COBALT   = (0.027, 0.141, 0.557, 1.0)
AMBER    = (0.980, 0.620, 0.050, 1.0)
OUT_PATH = "//lc_nematic_floor.glb"

# ── Grid ─────────────────────────────────────────────────────
_x1d   = np.linspace(-1.0, 1.0, N, dtype=np.float64)
XX, YY = np.meshgrid(_x1d, _x1d, indexing="ij")   # XX[i,j]=x[i], YY[i,j]=x[j]

# ── Physics ──────────────────────────────────────────────────

def _director_angle(defects):
    """θ = Σ sₐ arctan2(y−yₐ, x−xₐ).
    Each arctan2 is harmonic off its pole → superposition solves ∇²θ = 0.
    Branch cuts along −x from each pole cancel in colour (mod π) and
    do not affect the order parameter (depends only on d_min).
    """
    theta = np.zeros((N, N), dtype=np.float64)
    for xd, yd, s in defects:
        theta += s * np.arctan2(YY - yd, XX - xd)
    return theta


def _order_parameter(defects):
    """S = 1 − exp(−d_min² / R_CORE²).
    d_min² is the minimum squared Euclidean distance to any defect.
    WHY exponential: the Landau-de Gennes free energy has a parabolic
    potential well at S=0, giving a Gaussian core profile; the
    characteristic width ξ (coherence length) ≈ R_CORE sets the
    length scale over which order recovers from the isotropic core.
    """
    d2_min = np.full((N, N), np.inf, dtype=np.float64)
    for xd, yd, _ in defects:
        np.minimum(d2_min, (XX - xd) ** 2 + (YY - yd) ** 2, out=d2_min)
    return 1.0 - np.exp(-d2_min / R_CORE ** 2)


def _colour(theta):
    """(θ mod π)/π ∈ [0,1) → linear interp COBALT → AMBER.
    WHY mod π: nematic Z₂ symmetry means a full rotation of the director
    spans θ ∈ [0,π), not [0,2π). Using 2π would double every colour cycle,
    mis-counting the topological winding around each defect.
    """
    t = (theta % math.pi) / math.pi       # (N,N) in [0,1)
    t = t.ravel().astype(np.float32)
    c = np.empty((t.size, 4), dtype=np.float32)
    for ch, (lo, hi) in enumerate(zip(COBALT, AMBER)):
        c[:, ch] = lo + (hi - lo) * t
    return c                               # (N*N, 4)


# ── Defect configurations ─────────────────────────────────────

QUADRUPOLE = [                             # Basis: +½ +½ −½ −½ quadrupole
    ( 0.40,  0.40,  0.5),                  # +½ upper-right (comet pattern)
    (-0.40, -0.40,  0.5),                  # +½ lower-left  (comet pattern)
    (-0.40,  0.40, -0.5),                  # −½ upper-left  (trefoil pattern)
    ( 0.40, -0.40, -0.5),                  # −½ lower-right (trefoil pattern)
]
COMET    = [(0.00, 0.00,  0.5)]            # SK_Comet: isolated +½ disclination
HEDGEHOG = [(0.00, 0.00,  1.0)]            # SK_Hedgehog: integer +1 radial
ANNEAL   = [(0.15, 0.00,  0.5),            # SK_Anneal: tight ±½ pair
            (-0.15, 0.00, -0.5)]

# ── Compute Basis field ───────────────────────────────────────
S_basis     = _order_parameter(QUADRUPOLE)
theta_basis = _director_angle(QUADRUPOLE)

# ── Mesh from_pydata ──────────────────────────────────────────
verts = [
    (float(XX[i, j]), float(YY[i, j]), float(S_basis[i, j]) * Z_SCALE)
    for i in range(N) for j in range(N)
]
faces = [
    (i * N + j,      i * N + j + 1,
     (i+1) * N + j + 1, (i+1) * N + j)
    for i in range(N - 1) for j in range(N - 1)
]

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()

mesh = bpy.data.meshes.new(OBJ_NAME)
mesh.from_pydata(verts, [], faces)
obj  = bpy.data.objects.new(OBJ_NAME, mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)

# ── Shape keys ────────────────────────────────────────────────
obj.shape_key_add(name="Basis").interpolation = "KEY_LINEAR"

_base_co = np.empty(N * N * 3, dtype=np.float32)
mesh.vertices.foreach_get("co", _base_co)
_base_co = _base_co.reshape(-1, 3)        # reuse XY; replace Z per key


def _add_sk(name, defects):
    S  = _order_parameter(defects)
    sk = obj.shape_key_add(name=name, from_mix=False)
    sk.interpolation = "KEY_LINEAR"
    co = _base_co.copy()
    co[:, 2] = (S.ravel() * Z_SCALE).astype(np.float32)
    sk.data.foreach_set("co", co.ravel())


_add_sk("SK_Comet",    COMET)
_add_sk("SK_Hedgehog", HEDGEHOG)
_add_sk("SK_Anneal",   ANNEAL)

# ── Colour attribute ──────────────────────────────────────────
attr = mesh.color_attributes.new("LC_Director", "FLOAT_COLOR", "POINT")
attr.data.foreach_set("color", _colour(theta_basis).ravel())

# ── Material ──────────────────────────────────────────────────
mat = bpy.data.materials.new("LC_Nematic_Mat")
mat.use_nodes = True
nt  = mat.node_tree
nt.nodes.clear()

_vc  = nt.nodes.new("ShaderNodeVertexColor");    _vc.layer_name = "LC_Director"
_vc.location  = (-400, 200)
_em  = nt.nodes.new("ShaderNodeEmission");       _em.location  = (-200, 200)
_em.inputs["Strength"].default_value = 1.2
_pb  = nt.nodes.new("ShaderNodeBsdfPrincipled"); _pb.location  = (-200, 0)
_pb.inputs["Metallic"].default_value  = 0.10
_pb.inputs["Roughness"].default_value = 0.35
_mx  = nt.nodes.new("ShaderNodeMixShader");      _mx.location  = (100, 100)
_mx.inputs["Fac"].default_value = 0.30
_ou  = nt.nodes.new("ShaderNodeOutputMaterial"); _ou.location  = (350, 100)

nt.links.new(_vc.outputs["Color"],      _em.inputs["Color"])
nt.links.new(_vc.outputs["Color"],      _pb.inputs["Base Color"])
nt.links.new(_em.outputs["Emission"],   _mx.inputs[1])
nt.links.new(_pb.outputs["BSDF"],       _mx.inputs[2])
nt.links.new(_mx.outputs["Shader"],     _ou.inputs["Surface"])
mesh.materials.append(mat)

# ── Holoflow conventions ──────────────────────────────────────
obj["holoflow:facet"]    = True
obj["holoflow:category"] = "stage-floor"
obj.rotation_euler[0]    = -math.pi / 2   # −90° X → +Y-up at export
bpy.ops.object.transform_apply(rotation=True)

# ── GLB export ────────────────────────────────────────────────
bpy.ops.export_scene.gltf(
    filepath=bpy.path.abspath(OUT_PATH),
    export_format="GLB",
    export_draco_mesh_compression_enable=True,
    export_draco_mesh_compression_level=6,
    export_image_format="WEBP",
    export_morph=True,
    export_colors=True,
    export_yup=True,
)
print("✓ lc_nematic_floor.glb exported")
