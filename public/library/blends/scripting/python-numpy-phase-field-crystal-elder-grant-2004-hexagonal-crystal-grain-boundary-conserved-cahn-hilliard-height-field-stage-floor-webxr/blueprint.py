"""
Phase-Field Crystal (PFC) Model — Elder & Grant 2004
Elder KR, Grant M (2004) Phys Rev E 70(5):051605
DOI 10.1103/PhysRevE.70.051605

THE PHYSICS
-----------
The Phase-Field Crystal model describes a density field ψ(r,t) that
captures the periodic structure of a crystal on atomic length scales
while allowing slow diffusive dynamics on mesoscopic time scales.

Free energy functional (in dimensionless units, Elder & Grant 2004 Eq 1):
    F[ψ] = ∫ { (ψ/2)[r + (1+∇²)²]ψ + ψ⁴/4 } dr

The operator (1+∇²)² penalises deviations from the k₀=1 wavenumber,
selecting a periodic ground state with lattice spacing a₀ = 4π/√3.
The parameter r < 0 drives the system into the ordered (crystal) phase;
r > 0 keeps it disordered (liquid).

Conserved Model B dynamics (total density ψ̄ is conserved):
    ∂ψ/∂t = ∇²[δF/δψ] = ∇²[ (r+(1+∇²)²)ψ + ψ³ ]

In Fourier space, writing k² = k_x² + k_y²:
    ∂ψ̂/∂t = Λ(k)·ψ̂ − k²·FT(ψ³)
    Λ(k) = −k²·(r + (1−k²)²)

Growth rate Λ(k₀=1) = −r > 0 for r<0: modes at |k|=1 are linearly
unstable and grow until the ψ³ term saturates them, selecting the
triangular lattice (three wavevectors at mutual 60°, sum to zero).

ETD1 INTEGRATOR (Cox & Matthews 2002, unconditionally stable linear part)
--------------------------------------------------------------------------
    E_k  = exp(Λ(k)·dt)
    φ₁_k = expm1(Λ(k)·dt) / (Λ(k)·dt)     [Taylor-safe at Λ→0]
    ψ̂^{n+1} = E_k · ψ̂^n  +  φ₁_k · dt · (−k²) · FT(ψ³^n)

At k=0: Λ=0, E=1, −k²=0 → ψ̂(0) unchanged. Total density is exactly
conserved to floating-point precision.

SHAPE KEYS
----------
Basis       : r=−0.25, ψ̄=−0.50, T=800 steps  — perfect hexagonal crystal
SK_GrainBnd : r=−0.25, ψ̄=−0.50, T=600 steps  — two nuclei with offset
              random seeds → polycrystalline domain with grain boundary
SK_Stripe   : r=−0.07, ψ̄=−0.25, T=800 steps  — lower density → lamellar
              stripe phase (1D periodic instead of 2D hexagonal)
SK_Coexist  : r=−0.12, ψ̄=−0.38, T=300 steps  — liquid-crystal coexistence,
              partially ordered with disordered amorphous regions

PARAMETERS (edit here only)
"""

import bpy
import bmesh
import numpy as np
from numpy.fft import rfft2, irfft2, fftfreq, rfftfreq

# ── grid ───────────────────────────────────────────────────────────────────────
N         = 128        # points per side (128² = 16 384 vertices)
DX        = 1.0        # spatial step in dimensionless units
DT        = 0.50       # time step
Z_SCALE   = 0.45       # metres — height amplitude of crystal relief

# ── PFC parameters ─────────────────────────────────────────────────────────────
R_BASIS   = -0.25      # r for Basis and SK_GrainBnd (deep crystal)
PSI_BASIS = -0.50      # mean density ψ̄ for Basis and SK_GrainBnd
T_BASIS   = 800        # steps for Basis

R_STRIPE  = -0.07      # r for SK_Stripe (lamellar phase)
PSI_STRIPE= -0.25      # mean density for SK_Stripe
T_STRIPE  = 800        # steps for SK_Stripe

R_COEX    = -0.12      # r for SK_Coexist
PSI_COEX  = -0.38      # mean density for SK_Coexist
T_COEX    = 300        # steps — partially ordered, liquid pockets remain

# ── colour palette (cobalt → amber, matching studio convention) ────────────────
COL_LO    = (0.03, 0.14, 0.56, 1.0)   # cobalt  — ψ low (crystal troughs)
COL_HI    = (1.00, 0.65, 0.00, 1.0)   # amber   — ψ high (crystal peaks)

MESH_NAME = "PFC_Crystal_Floor"
ATTR_NAME = "PFC_Density"
OBJ_NAME  = "pfc_crystal_floor"
GLB_PATH  = "//pfc_crystal_floor.glb"

# ── Fourier wavenumber arrays ───────────────────────────────────────────────────
kx = fftfreq(N, d=DX) * (2 * np.pi)        # shape (N,)
ky = rfftfreq(N, d=DX) * (2 * np.pi)       # shape (N//2+1,)
KX, KY = np.meshgrid(kx, ky, indexing='ij')
K2 = KX**2 + KY**2                          # k² shape (N, N//2+1)

# Linear PFC operator in Fourier space: Λ(k) = −k²·(r + (1−k²)²)
def _make_etd1(r, dt):
    lam = -K2 * (r + (1.0 - K2)**2)
    E   = np.exp(lam * dt)
    z   = lam * dt
    # Taylor-safe φ₁: avoids 0/0 at k=0 (lam=0 there)
    phi1 = np.where(np.abs(z) < 1e-10, 1.0, np.expm1(z) / z)
    return E, phi1

def _step(psi_hat, E, phi1, dt):
    psi = irfft2(psi_hat, s=(N, N))
    nl  = -K2 * rfft2(psi**3)
    return E * psi_hat + phi1 * dt * nl

def _run_pfc(r, psi_mean, n_steps, rng_seed=0):
    """Evolve PFC from small-noise initial condition; return ψ(x,y)."""
    rng   = np.random.default_rng(rng_seed)
    psi   = psi_mean + 0.02 * rng.standard_normal((N, N))
    E, phi1 = _make_etd1(r, DT)
    psi_hat = rfft2(psi)
    for _ in range(n_steps):
        psi_hat = _step(psi_hat, E, phi1, DT)
    return irfft2(psi_hat, s=(N, N))

def _run_grain_boundary(n_steps):
    """Two sub-domains with different seeds → grain boundary."""
    E, phi1 = _make_etd1(R_BASIS, DT)
    rng_L = np.random.default_rng(42)
    rng_R = np.random.default_rng(99)
    psi   = np.empty((N, N))
    psi[:, :N//2]  = PSI_BASIS + 0.02 * rng_L.standard_normal((N, N//2))
    psi[:, N//2:]  = PSI_BASIS + 0.02 * rng_R.standard_normal((N, N//2))
    psi_hat = rfft2(psi)
    for _ in range(n_steps):
        psi_hat = _step(psi_hat, E, phi1, DT)
    return irfft2(psi_hat, s=(N, N))

def _norm(psi):
    lo, hi = psi.min(), psi.max()
    if hi == lo:
        return np.zeros_like(psi)
    return (psi - lo) / (hi - lo)

# ── Run all four PFC simulations ────────────────────────────────────────────────
print("PFC: running Basis (hexagonal crystal) …")
psi_basis   = _run_pfc(R_BASIS,  PSI_BASIS,  T_BASIS,  rng_seed=7)
print("PFC: running SK_GrainBnd …")
psi_grain   = _run_grain_boundary(n_steps=600)
print("PFC: running SK_Stripe (lamellar) …")
psi_stripe  = _run_pfc(R_STRIPE, PSI_STRIPE, T_STRIPE, rng_seed=13)
print("PFC: running SK_Coexist (partial) …")
psi_coexist = _run_pfc(R_COEX,   PSI_COEX,   T_COEX,   rng_seed=21)

n_basis = _norm(psi_basis)

# ── Clear scene ────────────────────────────────────────────────────────────────
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# ── Build N×N quad-grid mesh ───────────────────────────────────────────────────
mesh = bpy.data.meshes.new(MESH_NAME)
bm   = bmesh.new()

verts = []
for j in range(N):
    for i in range(N):
        z = float(n_basis[i, j]) * Z_SCALE
        verts.append(bm.verts.new((i * DX, j * DX, z)))

bm.verts.ensure_lookup_table()
for j in range(N - 1):
    for i in range(N - 1):
        v0 = verts[j * N + i]
        v1 = verts[j * N + i + 1]
        v2 = verts[(j + 1) * N + i + 1]
        v3 = verts[(j + 1) * N + i]
        bm.faces.new((v0, v1, v2, v3))

bm.to_mesh(mesh)
bm.free()

obj = bpy.data.objects.new(OBJ_NAME, mesh)
obj['holoflow:facet'] = True
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj

# ── Colour attribute (FLOAT_COLOR, POINT domain) ───────────────────────────────
attr = mesh.color_attributes.new(ATTR_NAME, 'FLOAT_COLOR', 'POINT')
flat = n_basis.ravel()                 # row-major matches vertex creation order
for v_idx, val in enumerate(flat):
    r = COL_LO[0] + val * (COL_HI[0] - COL_LO[0])
    g = COL_LO[1] + val * (COL_HI[1] - COL_LO[1])
    b = COL_LO[2] + val * (COL_HI[2] - COL_LO[2])
    attr.data[v_idx].color = (r, g, b, 1.0)

# ── Shape keys ─────────────────────────────────────────────────────────────────
obj.shape_key_add(name='Basis', from_mix=False)
mesh.shape_keys.use_relative = False   # absolute shape keys for animation

def _add_sk(name, psi_field):
    sk = obj.shape_key_add(name=name, from_mix=False)
    n  = _norm(psi_field)
    for v_idx, v in enumerate(mesh.vertices):
        i, j = v_idx % N, v_idx // N
        sk.data[v_idx].co = (v.co.x, v.co.y, float(n[i, j]) * Z_SCALE)

_add_sk('SK_GrainBnd', psi_grain)
_add_sk('SK_Stripe',   psi_stripe)
_add_sk('SK_Coexist',  psi_coexist)

# ── Material (attribute-driven colour + emission) ──────────────────────────────
mat = bpy.data.materials.new('PFC_Mat')
mat.use_nodes = True
nt  = mat.node_tree
nt.nodes.clear()

attr_nd  = nt.nodes.new('ShaderNodeAttribute')
attr_nd.attribute_name = ATTR_NAME

bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Metallic'].default_value    = 0.20
bsdf.inputs['Roughness'].default_value   = 0.28
bsdf.inputs['Emission Strength'].default_value = 1.4

out = nt.nodes.new('ShaderNodeOutputMaterial')
nt.links.new(attr_nd.outputs['Color'], bsdf.inputs['Base Color'])
nt.links.new(attr_nd.outputs['Color'], bsdf.inputs['Emission Color'])
nt.links.new(bsdf.outputs['BSDF'],    out.inputs['Surface'])
obj.data.materials.append(mat)

# ── GLB export ─────────────────────────────────────────────────────────────────
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.ops.export_scene.gltf(
    filepath            = bpy.path.abspath(GLB_PATH),
    use_selection       = True,
    export_draco_mesh_compression_enable = True,
    export_draco_mesh_compression_level  = 6,
    export_image_format = 'WEBP',
    export_morph        = True,
    export_colors       = True,
    export_yup          = True,
    export_apply        = True,
)
print(f"PFC blueprint complete → {GLB_PATH}")
