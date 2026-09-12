"""
Gross-Pitaevskii Equation — Rotating BEC Abrikosov Vortex Lattice
===================================================================
The Gross-Pitaevskii equation is the mean-field theory of a zero-temperature
Bose-Einstein condensate. In a rotating harmonic trap above a critical angular
velocity Ω_c1, the ground state nucleates quantised vortices — topological
defects where |ψ|=0 and the superfluid phase winds by 2π. Multiple vortices
repel logarithmically and arrange into a triangular Abrikosov lattice, the
superfluid analogue of the flux-line lattice in type-II superconductors.

Technique: imaginary-time split-operator propagation. Replace t→−iτ; the GPE
becomes a steepest-descent equation in the Hilbert-space metric that projects
onto the lowest-energy state in the planted topological sector.

Blender 5.1 · Python + NumPy · CC0
GPE: Gross 1961 Il Nuovo Cim 20:454; Pitaevskii 1961 JETP 13:451
Review: Dalfovo et al. Rev Mod Phys 71:463 (1999) arXiv:cond-mat/9806038
"""

import bpy, numpy as np
from math import pi

# ── parameters ─────────────────────────────────────────────────────────────────
N            = 128        # grid points per axis
L            = 8.0        # half-box in oscillator units ℓ = √(ℏ/mω)
G            = 500.0      # dimensionless coupling g₀=4πaN (Thomas-Fermi limit)
              # μ_TF = √(G/π) ≈ 12.6;  R_TF = (2μ_TF)^½ ≈ 5.0  (condensate radius)
DT           = 0.02       # imaginary-time step (converges well for G=500)
N_ITER       = 3000       # propagation steps per configuration
DISP_SCALE   = 0.50       # Z = |ψ|²_norm × DISP_SCALE  (metres, stage-floor height)
WORLD_SCALE  = 4.0        # XY span: vertices cover [−WORLD_SCALE, +WORLD_SCALE] m
OBJ_NAME     = "gpe_bec_vortex"
ATTR_NAME    = "GPE_Density"
# Cobalt → amber: vortex core (density≈0) → condensate bulk (density=peak)
COBALT = (0.027, 0.159, 0.408, 1.0)
AMBER  = (1.000, 0.702, 0.000, 1.0)

# ── spatial grid ───────────────────────────────────────────────────────────────
x1d  = np.linspace(-L, L, N, endpoint=False)
DX   = x1d[1] - x1d[0]
X, Y = np.meshgrid(x1d, x1d, indexing='ij')   # (N,N)
R2   = X**2 + Y**2

# WHY meshgrid indexing='ij': X[i,j]=x1d[i], Y[i,j]=x1d[j] → vertex i*N+j=(xs[i],xs[j])
# This matches the ravel() order used in foreach_set below.

# Fourier grid for full FFT (field is complex → rfft2 symmetry does not apply)
kx1d = 2 * pi * np.fft.fftfreq(N, d=DX)
KX, KY = np.meshgrid(kx1d, kx1d, indexing='ij')
K2 = KX**2 + KY**2

# Kinetic propagator: precomputed once. exp(−½k²dτ) damps high-k modes.
EXP_K = np.exp(-0.5 * K2 * DT)

# Thomas-Fermi profile: ψ_TF = √(max(0, μ_TF − ½r²)/G)
# WHY: TF amplitude is the G→∞ ground state; starting here beats a Gaussian
# initialisation by ~10× in convergence steps.
MU_TF  = np.sqrt(G / pi)
TF_AMP = np.sqrt(np.maximum(0.0, (MU_TF - 0.5 * R2) / G))

# Vertex XY coordinates in metres (used for all shape keys — only Z changes)
xs_m    = np.linspace(-WORLD_SCALE, WORLD_SCALE, N, dtype=np.float32)
IX, IJ  = np.meshgrid(np.arange(N), np.arange(N), indexing='ij')
X_VERT  = xs_m[IX.ravel()]   # (N²,)  all X coords
Y_VERT  = xs_m[IJ.ravel()]   # (N²,)  all Y coords


# ── helpers ────────────────────────────────────────────────────────────────────
def _normalise(psi):
    """Renormalise ψ to unit norm: ∫|ψ|² d²r = 1."""
    return psi / (np.sqrt(np.sum(np.abs(psi)**2) * DX**2) + 1e-30)


def _plant_vortices(positions):
    """Sum of arctan2 winding phases around each vortex centre."""
    phase = np.zeros((N, N), dtype=np.float64)
    for cx, cy in positions:
        phase += np.arctan2(Y - cy, X - cx)
    return phase


def _imaginary_step(psi):
    """
    Strang-split imaginary-time step  ψ → ψ/‖ψ‖.
    H = K + V,  K = −½∇²,  V = ½r² + G|ψ|²

    exp(−V·dτ/2) → IFFT[EXP_K·FFT] → exp(−V·dτ/2) → renormalise.

    WHY Strang and not plain Lie: splits K and V at O(dτ²) accuracy instead
    of O(dτ) for no extra FFT; the half-step form evaluates V at mid-point.
    WHY renormalise: imaginary-time is not unitary — norm shrinks. Renormalising
    each step implicitly tracks chemical potential μ = −d(log‖ψ‖)/dτ.
    """
    V   = 0.5 * R2 + G * np.abs(psi)**2
    psi = np.exp(-V * (DT * 0.5)) * psi               # half potential
    psi = np.fft.ifft2(EXP_K * np.fft.fft2(psi))      # full kinetic (Fourier)
    V   = 0.5 * R2 + G * np.abs(psi)**2
    psi = np.exp(-V * (DT * 0.5)) * psi               # second half potential
    return _normalise(psi)


def run_gpe(vortex_positions, n_iter=N_ITER):
    """
    Run imaginary-time propagation from Thomas-Fermi + planted vortices.
    Returns |ψ|²  normalised to peak = 1.
    """
    psi = _normalise(TF_AMP * np.exp(1j * _plant_vortices(vortex_positions)))
    for _ in range(n_iter):
        psi = _imaginary_step(psi)
    dens = np.abs(psi)**2
    return (dens / (dens.max() + 1e-30)).real.astype(np.float32)


# ── four vortex configurations ─────────────────────────────────────────────────
# Vortex count scales with effective rotation rate:  N_v ≈ Ω × R_TF²  (Ω/π per area).
# Hexagonal packing (Abrikosov 1957/Tkachenko 1965) is the energy minimum.

r7 = 2.2   # hexagonal ring radius  (inside R_TF ≈ 5, avoids low-density edge)
POS_SMOOTH = []
POS_SINGLE = [(0.0, 0.0)]
POS_HEX7   = [(0.0, 0.0)] + [(r7 * np.cos(k*pi/3), r7 * np.sin(k*pi/3)) for k in range(6)]
r_in, r_out = 1.5, 3.2
POS_HEX19  = (
    [(0.0, 0.0)]
    + [(r_in  * np.cos(k*pi/3),          r_in  * np.sin(k*pi/3))          for k in range(6)]
    + [(r_out * np.cos(k*pi/6 + pi/12),  r_out * np.sin(k*pi/6 + pi/12)) for k in range(12)]
)

print("GPE — imaginary-time propagation …")
D_SMOOTH = run_gpe(POS_SMOOTH)   # Ω=0: smooth Thomas-Fermi ground state
D_SINGLE = run_gpe(POS_SINGLE)   # 1 vortex: single dimple at centre
D_HEX7   = run_gpe(POS_HEX7)    # 7 vortices: classic Abrikosov hexagonal lattice
D_HEX19  = run_gpe(POS_HEX19)   # 19 vortices: denser two-shell lattice
print("GPE — done.")


# ── mesh + shape keys ──────────────────────────────────────────────────────────
for name in (OBJ_NAME,):
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    if name in bpy.data.meshes:
        bpy.data.meshes.remove(bpy.data.meshes[name])

def _dens_to_z(d):
    return (d * DISP_SCALE).astype(np.float32)

# Basis vertex positions
z_base = _dens_to_z(D_SMOOTH)
verts  = list(zip(X_VERT.tolist(), Y_VERT.tolist(), z_base.ravel().tolist()))
faces  = [(i*N+j, i*N+j+1, (i+1)*N+j+1, (i+1)*N+j)
          for i in range(N-1) for j in range(N-1)]

mesh = bpy.data.meshes.new(OBJ_NAME)
mesh.from_pydata(verts, [], faces)
mesh.update()
obj  = bpy.data.objects.new(OBJ_NAME, mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj

# shape keys
sk_names = ["SK_Single", "SK_Hex7", "SK_Hex19"]
sk_dens  = [D_SINGLE, D_HEX7, D_HEX19]
obj.shape_key_add(name="Basis", from_mix=False)
for sname, sdens in zip(sk_names, sk_dens):
    sk = obj.shape_key_add(name=sname, from_mix=False)
    z_sk = _dens_to_z(sdens)
    buf  = np.empty(N * N * 3, dtype=np.float32)
    buf[0::3] = X_VERT
    buf[1::3] = Y_VERT
    buf[2::3] = z_sk.ravel()
    sk.data.foreach_set("co", buf)


# ── vertex colours ─────────────────────────────────────────────────────────────
# Cobalt (density≈0) → Amber (density=peak): vortex cores are deep blue wells
# in a warm amber condensate plateau — immediate visual identification.
attr = mesh.color_attributes.new(name=ATTR_NAME, type='FLOAT_COLOR', domain='POINT')
t = D_SMOOTH.ravel()
r_ch = (COBALT[0] + (AMBER[0] - COBALT[0]) * t).astype(np.float32)
g_ch = (COBALT[1] + (AMBER[1] - COBALT[1]) * t).astype(np.float32)
b_ch = (COBALT[2] + (AMBER[2] - COBALT[2]) * t).astype(np.float32)
a_ch = np.ones(N*N, dtype=np.float32)
attr.data.foreach_set("color", np.stack([r_ch, g_ch, b_ch, a_ch], axis=1).ravel())


# ── material ───────────────────────────────────────────────────────────────────
mat   = bpy.data.materials.new(OBJ_NAME)
mat.use_nodes = True
nt    = mat.node_tree
nt.nodes.clear()
out_n   = nt.nodes.new('ShaderNodeOutputMaterial')
mix_n   = nt.nodes.new('ShaderNodeMixShader')
bsdf_n  = nt.nodes.new('ShaderNodeBsdfPrincipled')
emit_n  = nt.nodes.new('ShaderNodeEmission')
attr_n  = nt.nodes.new('ShaderNodeAttribute')
attr_n.attribute_name = ATTR_NAME
attr_n.attribute_type = 'GEOMETRY'
bsdf_n.inputs['Metallic'].default_value    = 0.35
bsdf_n.inputs['Roughness'].default_value   = 0.22
emit_n.inputs['Strength'].default_value    = 1.6
mix_n.inputs['Fac'].default_value          = 0.35
lk = nt.links.new
lk(attr_n.outputs['Color'], bsdf_n.inputs['Base Color'])
lk(attr_n.outputs['Color'], emit_n.inputs['Color'])
lk(bsdf_n.outputs['BSDF'],    mix_n.inputs[1])
lk(emit_n.outputs['Emission'], mix_n.inputs[2])
lk(mix_n.outputs['Shader'],   out_n.inputs['Surface'])
mesh.materials.append(mat)


# ── holoflow properties + +Y-up ────────────────────────────────────────────────
obj["holoflow:facet"]    = True
obj["holoflow:category"] = "stage-floor"
import mathutils
obj.matrix_world = mathutils.Matrix.Rotation(pi/2, 4, 'X') @ obj.matrix_world
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.ops.object.transform_apply(rotation=True)


# ── save + export ──────────────────────────────────────────────────────────────
import os
_dir = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(_dir, "gpe_bec_vortex.blend"))
bpy.ops.export_scene.gltf(
    filepath=os.path.join(_dir, "gpe_bec_vortex.glb"),
    export_format='GLB',
    export_draco_mesh_compression_enable=True,
    export_draco_mesh_compression_level=6,
    export_image_format='WEBP',
    export_morph=True,
    export_colors=True,
    export_yup=True,
)
print(f"Done — {N*N} verts · {(N-1)**2} quads · 4 shape keys · GPE_Density FLOAT_COLOR")
