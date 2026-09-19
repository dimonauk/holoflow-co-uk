"""
Wigner Quasi-Probability Distribution (1932) — Quantum Phase-Space Representation
E.P. Wigner, Phys. Rev. 40:749-759 (1932)

WHY THIS MATTERS:
The Wigner function W(q,p) is the unique bilinear map from density matrices to
real phase-space functions that recovers both quantum marginals exactly:
  ∫W(q,p)dp = |ψ(q)|²    (position probability)
  ∫W(q,p)dq = |φ(p)|²    (momentum probability)

Unlike classical probability distributions, W can be negative — those regions
are the unambiguous signature of a non-classical quantum state. Hudson's theorem
(1974) states that W≥0 everywhere if and only if ψ is a Gaussian; all other
pure states have W<0 somewhere. This blueprint visualises that negativity as a
height depression and an amber colour shift on a 128×128 WebXR stage floor.

BLENDER 5.1 APPROACH:
Direct bpy/bmesh mesh construction from numpy arrays.
No rendering operators; all data-API. Runs headless or in Blender's scripting tab.

Shape keys capture five physically distinct quantum states:
  Basis     : Fock |0⟩  — ground state, strictly Gaussian, always positive
  SK_Fock1  : Fock |1⟩  — first excited, negative centre (doughnut)
  SK_Fock5  : Fock |5⟩  — fifth excited, five concentric alternating rings
  SK_Cat    : (|+2⟩+|-2⟩)/N — Schrödinger cat α=2, interference fringes
  SK_Squeezed : Squeezed vacuum r=1.2, elliptical Gaussian σ_q/σ_p = e^{-2r}

Author: Holoflow Studio  |  Licence: CC0
"""

import bpy
import bmesh
import numpy as np
from scipy.special import eval_genlaguerre   # Laguerre polynomials — BSD-3-Clause

# ──────────────────────────────────────────────────────────────────────────────
# PARAMETERS
# ──────────────────────────────────────────────────────────────────────────────
N            = 128          # grid resolution along each axis
Q_RANGE      = 4.0          # phase-space extent: q ∈ [-Q_RANGE, +Q_RANGE]
P_RANGE      = 4.0          # phase-space extent: p ∈ [-P_RANGE, +P_RANGE]
HEIGHT_SCALE = 0.30         # metres per unit of W (scale for WebXR comfort)
W_CLIP       = 0.8          # clip W before height so floor stays shallow
WORLD_SCALE  = 2.0          # floor half-width in metres
MESH_NAME    = "wigner_phase_floor"
COL_ATTR     = "WQP_Phase"  # FLOAT_COLOR vertex attribute

# Schrödinger cat parameters
CAT_ALPHA    = 2.0          # coherent amplitude: |α⟩+|-α⟩  (separability ≈ e^{-2α²})

# Squeeze parameter for SK_Squeezed
SQUEEZE_R    = 1.2          # σ_q = e^{-r}/√2, σ_p = e^r/√2

# Cobalt → amber colour ramp  (negative W → amber, positive W → cobalt)
COL_POS = (0.08, 0.28, 0.90, 1.0)   # cobalt
COL_NEG = (0.90, 0.45, 0.05, 1.0)   # amber

# ──────────────────────────────────────────────────────────────────────────────
# PHYSICS: WIGNER FUNCTIONS
# All formulae in natural units ħ = 1, ω = 1, m = 1
# ──────────────────────────────────────────────────────────────────────────────

def _make_grid():
    q = np.linspace(-Q_RANGE, Q_RANGE, N)
    p = np.linspace(-P_RANGE, P_RANGE, N)
    Q, P = np.meshgrid(q, p, indexing='ij')   # shape (N,N), axis 0 = q, axis 1 = p
    return Q, P

def wigner_fock(n: int, Q, P):
    """
    Wigner function for harmonic-oscillator Fock state |n⟩ (natural units ħ=1).

    W_n(q,p) = ((-1)^n / π) · exp(-2r²) · L_n(4r²)

    where r² = q² + p² and L_n is the nth Laguerre polynomial.

    This follows directly from the matrix element of the parity operator
    ρ_n in the Fock basis (see Schleich 2001 §3.3).

    Key behaviour:
      n=0: Gaussian (always ≥ 0)
      n=1: negative at origin, positive ring at r² = 1/2
      n≥2: n concentric shells alternating ±, innermost sign = (-1)^n
    """
    r2 = Q**2 + P**2
    return ((-1)**n / np.pi) * np.exp(-2.0 * r2) * eval_genlaguerre(n, 0, 4.0 * r2)

def wigner_cat(alpha: float, Q, P):
    """
    Wigner function for the even Schrödinger cat state |ψ⟩ = N(|α⟩ + |-α⟩).

    Starting from the density matrix ρ = |ψ⟩⟨ψ|:

      W_cat = N²[ W_{+α} + W_{-α} + 2·cos(4p·α)·exp(-2(r² + α²)) / π ]

    where N² = 1/(2 + 2e^{-2α²}).

    The third term is the quantum interference contribution; it oscillates
    in p with period π/(2α), producing 'rabbit ears' fringes in the p-direction.
    These fringes have no classical analogue and are the hallmark of non-classical
    superposition. For α=2: fringe spacing ≈ 0.39 in p.
    """
    r2 = Q**2 + P**2
    norm_sq = 1.0 / (2.0 + 2.0 * np.exp(-2.0 * alpha**2))
    W_plus  = (2.0 / np.pi) * np.exp(-2.0 * ((Q - alpha)**2 + P**2))
    W_minus = (2.0 / np.pi) * np.exp(-2.0 * ((Q + alpha)**2 + P**2))
    # Interference: from cross-term ⟨+α|ρ(q)|-α⟩ in position representation
    W_inter = (2.0 / np.pi) * np.exp(-2.0 * (r2 + alpha**2)) * 2.0 * np.cos(4.0 * P * alpha)
    return norm_sq * (W_plus + W_minus + W_inter)

def wigner_squeezed(r_sq: float, Q, P):
    """
    Wigner function for squeezed vacuum |0,ξ⟩ with real squeeze parameter r_sq.

    A squeezing operator S(ξ) with ξ=r·e^{iφ} (real: φ=0) transforms the ground
    state to a Gaussian with:
      σ_q = e^{-r}/√2,   σ_p = e^{r}/√2   (Heisenberg: σ_q·σ_p = 1/2)

    W_sq(q,p) = (2/π) · exp(-2e^{2r}·q² - 2e^{-2r}·p²)

    The floor shows a squeezed ellipse: narrow in q, broad in p.
    """
    return (2.0 / np.pi) * np.exp(
        -2.0 * np.exp( 2.0 * r_sq) * Q**2
        -2.0 * np.exp(-2.0 * r_sq) * P**2
    )

# ──────────────────────────────────────────────────────────────────────────────
# COLOUR MAP
# ──────────────────────────────────────────────────────────────────────────────

def _colour(W_flat):
    """Map W → RGBA: positive = cobalt, negative = amber, linear blend."""
    W_norm = np.clip(W_flat / W_CLIP, -1.0, 1.0)   # in [-1, 1]
    t = (W_norm + 1.0) * 0.5                         # in [0, 1], 0=neg, 1=pos
    colours = np.zeros((len(W_flat), 4), dtype=np.float32)
    for ch in range(4):
        colours[:, ch] = COL_NEG[ch] * (1.0 - t) + COL_POS[ch] * t
    return colours

# ──────────────────────────────────────────────────────────────────────────────
# MESH BUILDER
# ──────────────────────────────────────────────────────────────────────────────

def _build_floor_mesh(name: str, W_2d: np.ndarray):
    """
    Construct a 128×128 quad mesh from W_2d with height along Z.
    Returns bpy.types.Mesh with vertices, faces, and COL_ATTR colour attribute.

    WHY direct data API: bpy.ops.mesh.primitive_grid_add is context-dependent
    and unreliable in headless execution. Constructing via foreach_set is O(N)
    and works in any context.
    """
    N2 = N * N
    q_lin = np.linspace(-WORLD_SCALE, WORLD_SCALE, N)
    p_lin = np.linspace(-WORLD_SCALE, WORLD_SCALE, N)
    GQ, GP = np.meshgrid(q_lin, p_lin, indexing='ij')

    W_h = np.clip(W_2d / W_CLIP, -1.0, 1.0) * HEIGHT_SCALE

    # Flatten in row-major order: vertex index = iq * N + ip
    verts_x = GQ.ravel().astype(np.float32)
    verts_y = GP.ravel().astype(np.float32)
    verts_z = W_h.ravel().astype(np.float32)

    # Quad faces: (iq, ip) → (iq+1, ip), (iq+1, ip+1), (iq, ip+1)
    iq = np.arange(N - 1).repeat(N - 1)
    ip = np.tile(np.arange(N - 1), N - 1)
    v0 = iq * N + ip
    faces = np.stack([v0, v0 + N, v0 + N + 1, v0 + 1], axis=1)

    me = bpy.data.meshes.new(name)
    me.vertices.add(N2)
    me.vertices.foreach_set("co", np.column_stack([verts_x, verts_y, verts_z]).ravel())
    me.loops.add(faces.size)
    me.polygons.add(len(faces))
    me.loops.foreach_set("vertex_index", faces.ravel())
    loop_start = np.arange(len(faces)) * 4
    me.polygons.foreach_set("loop_start", loop_start)
    me.polygons.foreach_set("loop_total", np.full(len(faces), 4, dtype=np.int32))
    me.update()

    # Vertex colour attribute
    attr = me.color_attributes.new(name=COL_ATTR, type='FLOAT_COLOR', domain='POINT')
    attr.data.foreach_set("color", _colour(W_2d.ravel()).ravel())

    return me

# ──────────────────────────────────────────────────────────────────────────────
# SHAPE KEY UTILITY
# ──────────────────────────────────────────────────────────────────────────────

def _add_shape_key(obj, sk_name: str, W_2d: np.ndarray):
    """Append a shape key with height driven by W_2d."""
    sk = obj.shape_key_add(name=sk_name, from_mix=False)
    q_lin = np.linspace(-WORLD_SCALE, WORLD_SCALE, N)
    p_lin = np.linspace(-WORLD_SCALE, WORLD_SCALE, N)
    GQ, GP = np.meshgrid(q_lin, p_lin, indexing='ij')
    W_h = np.clip(W_2d / W_CLIP, -1.0, 1.0) * HEIGHT_SCALE
    coords = np.column_stack([GQ.ravel(), GP.ravel(), W_h.ravel()]).ravel()
    sk.data.foreach_set("co", coords.astype(np.float32))

# ──────────────────────────────────────────────────────────────────────────────
# MATERIAL
# ──────────────────────────────────────────────────────────────────────────────

def _build_material(name: str) -> bpy.types.Material:
    """Attribute-driven BSDF: WQP_Phase → Base Colour, smooth metallic sheen."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out  = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = COL_ATTR
    attr.attribute_type = 'GEOMETRY'

    bsdf.inputs["Roughness"].default_value       = 0.25
    bsdf.inputs["Metallic"].default_value        = 0.65
    bsdf.inputs["IOR"].default_value             = 1.45

    nt.links.new(attr.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(bsdf.outputs["BSDF"],  out.inputs["Surface"])

    out.location  = (400, 0)
    bsdf.location = (150, 0)
    attr.location = (-100, 0)
    return mat

# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def run():
    # ── Clean scene ───────────────────────────────────────────────────────────
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in list(bpy.data.meshes) + list(bpy.data.materials):
        bpy.data.meshes.remove(block) if isinstance(block, bpy.types.Mesh) else \
        bpy.data.materials.remove(block)

    Q, P = _make_grid()

    # ── Basis: Fock |0⟩ (Gaussian ground state) ───────────────────────────────
    # W_0(q,p) = (2/π)·exp(-2r²)  — always positive, most classical pure state
    W_fock0 = wigner_fock(0, Q, P)

    me   = _build_floor_mesh(MESH_NAME, W_fock0)
    mat  = _build_material(MESH_NAME + "_mat")
    me.materials.append(mat)
    obj  = bpy.data.objects.new(MESH_NAME, me)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Basis shape key
    obj.shape_key_add(name="Basis", from_mix=False)

    # ── SK_Fock1: Fock |1⟩ — negative centre ─────────────────────────────────
    # W_1 = (1/π)·(4r²-1)·exp(-2r²); zero at r²=1/4, negative for r<1/2
    _add_shape_key(obj, "SK_Fock1", wigner_fock(1, Q, P))

    # ── SK_Fock5: Fock |5⟩ — five concentric rings alternating ± ────────────
    # W_5 = (1/π)·L_5(4r²)·exp(-2r²), zeros at roots of L_5
    _add_shape_key(obj, "SK_Fock5", wigner_fock(5, Q, P))

    # ── SK_Cat: Schrödinger cat (|+2⟩+|-2⟩)/N ───────────────────────────────
    # Two Gaussian peaks at q=±2, p=0  +  interference fringes along p
    _add_shape_key(obj, "SK_Cat", wigner_cat(CAT_ALPHA, Q, P))

    # ── SK_Squeezed: Squeezed vacuum r=1.2 ───────────────────────────────────
    # Elliptical Gaussian: narrow in q (factor e^{-1.2}≈0.30), wide in p
    _add_shape_key(obj, "SK_Squeezed", wigner_squeezed(SQUEEZE_R, Q, P))

    # ── Stage-floor orientation (+Y up for WebXR) ─────────────────────────────
    # WHY: Holoflow exporter expects +Y world up; rotate X-Y plane → X-Z plane
    obj.rotation_euler[0] = -1.5707963267948966  # -π/2
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

    # ── Smooth shading ────────────────────────────────────────────────────────
    for poly in me.polygons:
        poly.use_smooth = True
    me.use_auto_smooth = False

    print(f"[Wigner] mesh: {len(me.vertices)}V  {len(me.polygons)}F")
    print(f"[Wigner] W_min={W_fock0.min():.4f}  W_max={W_fock0.max():.4f}")
    print(f"[Wigner] shape keys: {[sk.name for sk in me.shape_keys.key_blocks]}")

    # ── GLB export ────────────────────────────────────────────────────────────
    import os
    out_path = os.path.join(os.path.dirname(bpy.data.filepath) or "/tmp",
                            "wigner_phase_floor.glb")
    bpy.ops.export_scene.gltf(
        filepath=out_path,
        export_format='GLB',
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_image_format='WEBP',
        export_morph=True,
        export_colors=True,
        export_apply=True,
        export_yup=True,
    )
    print(f"[Wigner] exported → {out_path}")

run()
