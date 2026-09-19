"""
Kane-Mele Model 2005 — Quantum Spin Hall / Z₂ Topological Insulator
====================================================================
TECHNIQUE (2–3 sentences):
  Kane & Mele (2005 PRL 95:226801) extended Haldane's honeycomb tight-binding
  to spin-1/2 electrons: two copies of the Haldane model (one per spin) with
  spin-orbit coupling (SOC) λ_SO replacing the staggered magnetic flux, and
  time-reversal symmetry (TRS) preserved. The Chern numbers cancel — C_↑=+1,
  C_↓=−1, total C=0, no Hall conductance — but the SPIN Hall conductance is
  quantised at σ_xy^s = e/4π and protected by a Z₂ topological invariant ν∈{0,1}.
  We compute the SPIN Berry curvature Ω_s(k) = 2·Ω_↑(k) via the gauge-free
  solid-angle formula on the spin-up 2×2 Bloch Hamiltonian and display it as a
  stage-floor height field whose double-peaked structure (amber K, amber K′)
  contrasts with Haldane's single-signed peaks — the visual signature that both
  valleys contribute constructively to spin Hall transport.

MATHEMATICS:
  Spin-up 2×2 Bloch Hamiltonian (Haldane sector φ=+π/2, t₂=λ_SO):
    h_↑(k) = d₀(k)·I + d(k)·σ
      dₓ + i·dᵧ = t₁ Σⱼ exp(ik·δⱼ)              [NN hopping, three δⱼ]
      dz         = M − 2λ_SO sin(π/2) Σⱼ sin(k·bⱼ) = M − h_soc
      d₀         = 2λ_SO cos(π/2) Σⱼ cos(k·bⱼ) = 0  [vanishes at φ=π/2]

  Spin-down 2×2 Hamiltonian (TRS partner, φ=−π/2):
    h_↓(k) = σ_y h_↑*(−k) σ_y  →  Ω_↓(k) = −Ω_↑(−k) = −Ω_↑(k) [at inversion pts]

  Spin Berry curvature (solid-angle formula for 2-band model):
    Ω_↑(k) = −½ ĥ↑ · (∂_kx ĥ↑ × ∂_ky ĥ↑)    ĥ↑ = d/|d|
    Ω_s(k)  = Ω_↑(k) − Ω_↓(k) = 2 Ω_↑(k)  [same sign at both K and K′]

  Topological invariants:
    Spin Chern number:  C_s = (1/2π) ∫_BZ Ω_s d²k = 2C_↑ ∈ {−2, 0, +2}
    Z₂ invariant:       ν = C_s/2 mod 2 ∈ {0, 1}    [ν=1 ↔ QSH insulator]
    Phase boundary:     |M| < 3√3 λ_SO  (topological)  vs  |M| > 3√3 λ_SO (trivial)
    Critical mass:      M_c = 3√3 λ_SO ≈ 5.196 λ_SO

  Rashba SOC (λ_R): spin-mixing NN hopping that BREAKS Sz conservation
    H_R = iλ_R Σ_{<ij>} c†_i (ê_z × δ̂_ij)·σ c_j
    Topology survives for λ_R < λ_R^c ≈ 2λ_SO (full-gap condition).
    Z₂ is protected by TRS alone; Sz non-conservation only kills the quantised
    σ_xy^s value, not the topological phase boundary.

  WHY solid-angle over FHS lattice-gauge for this basis:
    At M=0 the spin-up and spin-down bands are Kramer's-degenerate at every k;
    the non-Abelian FHS formula (det of 2×2 link matrices) would give C_total=0
    everywhere, obscuring the spin topology. The solid-angle formula operates on
    the SPIN-RESOLVED 2×2 sector — gauge-independent, and physically meaningful:
    it measures the winding of ĥ↑: T² → S² which captures C_↑=+1 directly.

SOURCES (permissive):
  Kane CL Mele EJ 2005 PRL 95:226801 doi:10.1103/PhysRevLett.95.226801
    — original QSH prediction (mathematical results, public domain)
  Haldane FDM 1988 PRL 61:2015 doi:10.1103/PhysRevLett.61.2015
    — Chern insulator precursor (public domain) — Nobel Physics 2016
  Asbóth JK Oroszlány L Pályi A 2016 arXiv:1509.02295 CC-BY 4.0
    — A Short Course on Topological Insulators, Chapters 5–6
  NumPy — BSD-3-Clause  https://numpy.org  github.com/numpy/numpy
"""

import bpy
import numpy as np
import pathlib

# ── Constants ─────────────────────────────────────────────────────────────────
N            = 128          # BZ grid N×N
WORLD_SCALE  = 4.0          # mesh half-width (m)
HEIGHT_SCALE = 0.70
T1           = 1.0          # NN hopping
SQ3          = np.sqrt(3)

# Shape-key parameter table: (λ_SO, M, label)
M_CRIT_BASE = 3.0 * SQ3 * 0.20  # M_c at λ_SO=0.20
PARAMS_BASIS  = (0.20, 0.00,                  "ν=1 QSH, equal K/K′ peaks C_↑=+1")
PARAMS_STRONG = (0.40, 0.00,                  "ν=1 stronger SOC, sharper confinement")
PARAMS_NEAR   = (0.20, M_CRIT_BASE * 0.95,   "ν=1→0 approaching phase boundary")
PARAMS_TRIV   = (0.20, M_CRIT_BASE * 1.50,   "ν=0 trivial insulator, flat landscape")

COL_LOW  = (0.030, 0.200, 0.780, 1.0)   # cobalt — negative/zero Ω
COL_HIGH = (0.980, 0.620, 0.050, 1.0)   # amber  — positive Ω
ATTR_NAME = "KM_SpinBC"
OBJ_NAME  = "kane_mele_floor"

# ── Reciprocal geometry (same as Haldane) ─────────────────────────────────────
B1 = np.array([2*np.pi,       -2*np.pi/SQ3])
B2 = np.array([0.0,            4*np.pi/SQ3])

s1, s2 = np.meshgrid(np.linspace(0, 1, N, endpoint=False),
                      np.linspace(0, 1, N, endpoint=False), indexing='ij')
KX = s1 * B1[0] + s2 * B2[0]   # (N,N)
KY = s1 * B1[1] + s2 * B2[1]

# NN A→B vectors
NN_DELTA = np.array([[0, 1/SQ3], [-0.5, -1/(2*SQ3)], [0.5, -1/(2*SQ3)]])
# NNN CCW vectors (A→A)
NNN_B    = np.array([[1, 0], [-0.5, SQ3/2], [-0.5, -SQ3/2]])

# Pre-dot products: (N,N,3)
kk = np.stack([KX, KY], axis=-1)            # (N,N,2)
nn_dot  = kk @ NN_DELTA.T                   # (N,N,3)
nnn_dot = kk @ NNN_B.T                      # (N,N,3)


# ── Spin-up 2×2 d-vector (φ=π/2) ─────────────────────────────────────────────
def _d_up(lso, M):
    """Return (dx, dy, dz) arrays shaped (N,N) for spin-up Haldane sector."""
    h_ab = T1 * np.sum(np.exp(1j * nn_dot), axis=-1)   # NN structure factor
    dx   = h_ab.real
    dy   = h_ab.imag
    h_soc = 2 * lso * np.sum(np.sin(nnn_dot), axis=-1)  # SOC = Im(NNN) at φ=π/2
    dz   = M - h_soc
    return dx, dy, dz


# ── Solid-angle Berry curvature ────────────────────────────────────────────────
def _spin_berry_curvature(lso, M):
    """
    Spin Berry curvature Ω_s(k) = 2 Ω_↑(k) on the N×N BZ grid.
    Uses gauge-free solid-angle formula (Haldane 1988 supplementary method):
      Ω_↑ = −½ ĥ · (∂_kx ĥ × ∂_ky ĥ)
    ∫ Ω_s = 2C_↑ ∈ {−2, 0, +2};  Z₂ = C_↑ mod 2 ∈ {0, 1}.
    """
    dx, dy, dz = _d_up(lso, M)
    d_mag = np.maximum(np.sqrt(dx**2 + dy**2 + dz**2), 1e-12)
    hx, hy, hz = dx / d_mag, dy / d_mag, dz / d_mag

    # Gradients along reciprocal axes s1 and s2, then chain-rule to kx, ky.
    # np.gradient uses centred finite differences (2nd order).
    dhx0, dhx1 = np.gradient(hx, axis=0), np.gradient(hx, axis=1)
    dhy0, dhy1 = np.gradient(hy, axis=0), np.gradient(hy, axis=1)
    dhz0, dhz1 = np.gradient(hz, axis=0), np.gradient(hz, axis=1)

    # Cross product columns for the solid-angle integrand
    cx = dhy0 * dhz1 - dhz0 * dhy1
    cy = dhz0 * dhx1 - dhx0 * dhz1
    cz = dhx0 * dhy1 - dhy0 * dhx1

    # Factor 2: Ω_s = Ω_↑ − Ω_↓ = 2 Ω_↑ (TRS: Ω_↓ = −Ω_↑ at every k)
    omega_s = 2.0 * (-0.5) * (hx * cx + hy * cy + hz * cz)
    return omega_s


# ── Build single height field ─────────────────────────────────────────────────
def _make_heights(omega, global_max):
    """Map Ω_s ∈ [−max, max] → z ∈ [0, HEIGHT_SCALE]."""
    return (omega / global_max + 1.0) * (HEIGHT_SCALE / 2.0)


def _make_colors(omega, global_max):
    t = np.clip((omega / global_max + 1.0) / 2.0, 0.0, 1.0)  # (N,N), 0→cobalt, 1→amber
    r = COL_LOW[0] + t * (COL_HIGH[0] - COL_LOW[0])
    g = COL_LOW[1] + t * (COL_HIGH[1] - COL_LOW[1])
    b = COL_LOW[2] + t * (COL_HIGH[2] - COL_LOW[2])
    return np.stack([r, g, b, np.ones_like(t)], axis=-1)  # (N,N,4)


# ── Compute all four variants, find global |Ω|_max ───────────────────────────
all_params = [PARAMS_BASIS, PARAMS_STRONG, PARAMS_NEAR, PARAMS_TRIV]
omegas = [_spin_berry_curvature(p[0], p[1]) for p in all_params]
global_max = max(np.max(np.abs(o)) for o in omegas)


# ── Blender mesh ──────────────────────────────────────────────────────────────
def _kx_ky_world():
    """Return (xs, ys) in world space corresponding to BZ grid rows/cols."""
    xs = np.linspace(-WORLD_SCALE, WORLD_SCALE, N)
    ys = np.linspace(-WORLD_SCALE, WORLD_SCALE, N)
    return xs, ys


xs, ys = _kx_ky_world()
omega0  = omegas[0]
z0      = _make_heights(omega0, global_max).flatten()
cols0   = _make_colors(omega0, global_max)

# Vertex positions
verts = []
for j in range(N):
    for i in range(N):
        verts.append((xs[i], ys[j], z0[j * N + i]))

# Quad faces (CCW)
faces = []
for j in range(N - 1):
    for i in range(N - 1):
        a = j * N + i
        faces.append((a, a + 1, a + N + 1, a + N))

mesh = bpy.data.meshes.new(OBJ_NAME)
mesh.from_pydata(verts, [], faces)
mesh.update()
obj = bpy.data.objects.new(OBJ_NAME, mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj

# Colour attribute
col_attr = mesh.color_attributes.new(name=ATTR_NAME, type='FLOAT_COLOR', domain='POINT')
flat = cols0.reshape(-1, 4)
for idx, c in enumerate(flat):
    col_attr.data[idx].color = (float(c[0]), float(c[1]), float(c[2]), float(c[3]))

# ── Shape keys ────────────────────────────────────────────────────────────────
obj.shape_key_add(name="Basis", from_mix=False)
sk_names = ["SK_StrongSOC", "SK_NearCrit", "SK_Trivial"]

for sk_nm, (lso, M, _) in zip(sk_names, all_params[1:]):
    sk = obj.shape_key_add(name=sk_nm, from_mix=False)
    omega_i = omegas[all_params.index((lso, M, _))]
    z_i = _make_heights(omega_i, global_max).flatten()
    for v_idx in range(N * N):
        j, i = divmod(v_idx, N)
        sk.data[v_idx].co.z = z_i[v_idx]

# ── Material (Emission + Principled, same as library standard) ────────────────
mat = bpy.data.materials.new(name="KaneMele_Mat")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

attr  = nodes.new("ShaderNodeAttribute");   attr.attribute_name = ATTR_NAME
emit  = nodes.new("ShaderNodeEmission");    emit.inputs["Strength"].default_value = 1.8
princ = nodes.new("ShaderNodeBsdfPrincipled")
mix   = nodes.new("ShaderNodeMixShader");   mix.inputs["Fac"].default_value = 0.30
out   = nodes.new("ShaderNodeOutputMaterial")

links.new(attr.outputs["Color"], emit.inputs["Color"])
links.new(attr.outputs["Color"], princ.inputs["Base Color"])
princ.inputs["Metallic"].default_value   = 0.15
princ.inputs["Roughness"].default_value  = 0.25

links.new(emit.outputs["Emission"],  mix.inputs[1])
links.new(princ.outputs["BSDF"],     mix.inputs[2])
links.new(mix.outputs["Shader"],     out.inputs["Surface"])

obj.data.materials.append(mat)

# ── WebXR / holoflow metadata ─────────────────────────────────────────────────
obj["holoflow:facet"]   = True
obj["holoflow:category"] = "stage-floor"
obj.name = OBJ_NAME

# ── Apply transform, export ───────────────────────────────────────────────────
import math
obj.rotation_euler = (math.radians(-90), 0, 0)
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.ops.object.transform_apply(rotation=True)

OUT_DIR = pathlib.Path(__file__).parent
bpy.ops.wm.save_as_mainfile(filepath=str(OUT_DIR / "kane_mele_floor.blend"))

bpy.ops.export_scene.gltf(
    filepath=str(OUT_DIR / "kane_mele_floor.glb"),
    use_selection=True,
    export_format='GLB',
    export_draco_mesh_compression_enable=True,
    export_draco_mesh_compression_level=6,
    export_image_format='WEBP',
    export_morph=True,
    export_colors=True,
    export_yup=True,
)
print("✓ Kane-Mele floor exported.")
