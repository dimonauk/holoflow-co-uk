"""
Magnetic Skyrmion — Skyrme (1962), Bogomol'ny (1976)
Dzyaloshinskii–Moriya Interaction on a 2-D classical Heisenberg lattice.

H = −J Σ_{⟨ij⟩} m_i·m_j
    −D Σ_{⟨ij⟩} (m_i × m_j)·ê_ij        ← Néel-type DMI
    −K Σ_i (m_iz)²                         ← easy-axis anisotropy
    −B Σ_i m_iz                             ← applied field (z)

Topological charge (Pontryagin index):
  Q = (1/4π) ∫ m·(∂_x m × ∂_y m) d²x  ∈ ℤ
computed on the lattice via Berg–Lüscher solid-angle summation (1981).

Relaxation: damped Landau-Lifshitz (LLG-α) — gradient descent on S²:
  δm_i = α (H_eff,i − (m_i·H_eff,i) m_i),  then normalise.
For α → ∞ this is pure gradient descent; α = 0.10 gives rapid convergence
while avoiding overshooting into metastable states.

Visualisation: 128×128 stage-floor height-field.
  height = m_z · Z_SCALE
  colour = colour-wheel (φ = atan2(m_y, m_x)) blended with cobalt-amber
           by in-plane fraction sin(θ) = √(m_x² + m_y²).
           mz = +1 → amber;  mz = −1 → cobalt;  in-plane → hue wheel.

Shape keys (four phases of the magnetic phase diagram):
  Basis      — single isolated Néel skyrmion      Q = −1
  SK_Lattice — 3×3 skyrmion crystal lattice       Q ≈ −9
  SK_Helical — helical stripe phase (B = 0)       Q =  0
  SK_FM      — field-polarised ferromagnet        Q =  0
"""

import bpy
import numpy as np
import math

# ── parameters ────────────────────────────────────────────────────────────────
N          = 128        # lattice size (128×128 = 16 384 verts, 16 129 quads)
J          = 1.0        # ferromagnetic exchange coupling
D          = 0.35       # DMI strength (Néel type, interfacial)
K_BASE     = 0.08       # easy-axis anisotropy (positive = easy-z)
Z_SCALE    = 0.45       # m_z maps to this height range (Blender units)
WORLD_SIZE = 4.0        # mesh spans ±WORLD_SIZE in X and Y
ALPHA      = 0.10       # LLG damping — tangential gradient step size
N_RELAX    = 5000       # relaxation iterations for main scenarios

COBALT = (0.027, 0.141, 0.557)
AMBER  = (0.980, 0.620, 0.050)

OBJ_NAME  = "skyrmion_floor"
MAT_NAME  = "SKY_Mat"
ATTR_NAME = "SKY_Spin"
OUT_BLEND = "//skyrmion_floor.blend"
OUT_GLB   = "//skyrmion_floor.glb"

# ── physics ───────────────────────────────────────────────────────────────────

def _heff(m, J, D, K, B):
    """H_eff = −∂H/∂m at every site (shape N×N×3).

    Néel DMI: D_{ij} = D·r̂_{ij}.  Discretised with centred differences:
      H_DMI = D (x̂×∂_x m + ŷ×∂_y m)
    where x̂×v = (0, −v_z, v_y) and ŷ×v = (v_z, 0, −v_x).
    Periodic boundary conditions throughout.
    """
    # Exchange: ∑ 4 nearest neighbours
    H = J * (np.roll(m, 1, 0) + np.roll(m, -1, 0) +
             np.roll(m, 1, 1) + np.roll(m, -1, 1))
    # Centred-difference gradients
    dx = (np.roll(m, -1, 0) - np.roll(m, 1, 0)) * 0.5   # ∂_x m
    dy = (np.roll(m, -1, 1) - np.roll(m, 1, 1)) * 0.5   # ∂_y m
    # Néel DMI contribution to H_eff
    H[..., 0] += D *  dy[..., 2]                          # ŷ×dy: x-component
    H[..., 1] -= D *  dx[..., 2]                          # x̂×dx: y-component (−)
    H[..., 2] += D * (dx[..., 1] - dy[..., 0])            # z-components sum
    # Anisotropy (favours m_z) and applied field
    H[..., 2] += 2.0 * K * m[..., 2] + B
    return H


def _relax(m, J, D, K, B, alpha=ALPHA, steps=N_RELAX):
    """Damped LLG: geodesic gradient descent on unit-sphere manifold."""
    for _ in range(steps):
        H    = _heff(m, J, D, K, B)
        proj = np.einsum('ijk,ijk->ij', m, H)[..., None]  # m·H scalar
        m    = m + alpha * (H - proj * m)                  # tangential step
        m   /= np.linalg.norm(m, axis=-1, keepdims=True).clip(1e-12)
    return m


def _topological_Q(m):
    """Lattice Pontryagin index — Berg & Lüscher, Nucl Phys B 190:412 (1981).
    Each plaquette (i,j) is split into two triangles; their solid angles sum
    to the winding contribution. Total Q = Σ / 4π.
    """
    def _tri(a, b, c):
        num = np.einsum('ijk,ijk->ij', a, np.cross(b, c, axis=-1))
        den = (1.0
               + np.einsum('ijk,ijk->ij', a, b)
               + np.einsum('ijk,ijk->ij', b, c)
               + np.einsum('ijk,ijk->ij', c, a))
        return 2.0 * np.arctan2(num, den)

    # b = m[i+1,j], c = m[i,j+1], d = m[i+1,j+1]
    b = np.roll(m, -1, 0)
    c = np.roll(m, -1, 1)
    d = np.roll(np.roll(m, -1, 0), -1, 1)
    return np.sum(_tri(m, b, d) + _tri(m, d, c)) / (4.0 * math.pi)


# ── initial conditions ────────────────────────────────────────────────────────

def _ferromagnet():
    m = np.zeros((N, N, 3))
    m[..., 2] = 1.0
    return m


def _skyrmion_at(x0, y0, R):
    """Analytic Néel skyrmion: θ(r) = π(1−r/R)Θ(R−r), φ = atan2(y,x)."""
    ii, jj = np.mgrid[:N, :N].astype(float)
    r   = np.sqrt((ii - x0)**2 + (jj - y0)**2) + 1e-9
    phi = np.arctan2(jj - y0, ii - x0)           # Néel helicity = 0
    th  = np.pi * np.clip(1.0 - r / R, 0.0, 1.0)
    m   = np.stack([np.sin(th) * np.cos(phi),
                    np.sin(th) * np.sin(phi),
                    np.cos(th)], axis=-1)
    m[r > R] = [0.0, 0.0, 1.0]                    # ferromagnetic background
    return m


def _lattice_skyrmions(n_row=3):
    """n_row×n_row Néel skyrmions on a square superlattice."""
    m       = _ferromagnet()
    spacing = N // n_row
    R_sk    = spacing // 3
    for i in range(n_row):
        for j in range(n_row):
            cx = int(spacing * (i + 0.5))
            cy = int(spacing * (j + 0.5))
            sk = _skyrmion_at(cx, cy, R_sk)
            # Paste skyrmion into ferromagnetic background
            ri, ci = np.mgrid[:N, :N]
            region = np.sqrt((ri - cx)**2 + (ci - cy)**2) < R_sk + 2
            m[region] = sk[region]
    return m


def _helix():
    """Helical spin spiral: m = (0, sin(qx), cos(qx)), q = arctan(D/J)."""
    q     = math.atan(D / J)          # exact wavevector on square lattice
    phase = q * np.arange(N, dtype=float)
    m     = np.zeros((N, N, 3))
    m[:, :, 1] = np.sin(phase)[:, None]
    m[:, :, 2] = np.cos(phase)[:, None]
    return m


# ── colour mapping ────────────────────────────────────────────────────────────

def _spin_colour(m):
    """Standard skyrmion colour coding.

    In-plane spins acquire hue from the azimuthal angle φ = atan2(m_y, m_x),
    blended into the cobalt–amber base by the in-plane fraction sin(θ).
    Poles: mz = +1 → amber;  mz = −1 → cobalt.
    """
    mx, my, mz = m[..., 0], m[..., 1], m[..., 2]
    phi  = np.arctan2(my, mx) / (2.0 * math.pi) % 1.0   # hue [0,1)
    s_th = np.sqrt(mx**2 + my**2)                         # sin(θ) ∈ [0,1]
    t    = (mz + 1.0) * 0.5                               # [0,1] cobalt→amber

    # HSV colour wheel at V=S=1
    h6  = phi * 6.0
    ih  = np.floor(h6).astype(np.int32) % 6
    f   = h6 - np.floor(h6)
    sel = [ih == k for k in range(6)]
    hr  = np.select(sel, [1., 1-f, 0., 0., f,  1.])
    hg  = np.select(sel, [f,  1., 1., 1-f, 0., 0.])
    hb  = np.select(sel, [0., 0., f,  1., 1., 1-f])

    # Cobalt–amber base, then blend in colour wheel by sin(θ)
    br = COBALT[0] + t * (AMBER[0] - COBALT[0])
    bg = COBALT[1] + t * (AMBER[1] - COBALT[1])
    bb = COBALT[2] + t * (AMBER[2] - COBALT[2])
    s  = s_th * 0.65
    r  = (br * (1 - s) + hr * s).astype(np.float32)
    g  = (bg * (1 - s) + hg * s).astype(np.float32)
    b  = (bb * (1 - s) + hb * s).astype(np.float32)
    return r, g, b


# ── mesh helpers ──────────────────────────────────────────────────────────────

def _build_mesh(me, mz):
    """Construct a flat-ish N×N quad grid. mz is an N×N float array."""
    xs = np.linspace(-WORLD_SIZE, WORLD_SIZE, N)
    xi, yj = np.meshgrid(xs, xs, indexing='ij')
    verts = np.column_stack(
        (xi.ravel(), yj.ravel(), (mz * Z_SCALE).ravel())
    ).astype(np.float32)
    NV = N * N
    NQ = (N - 1) ** 2
    ii  = np.arange(N - 1).repeat(N - 1)
    jj  = np.tile(np.arange(N - 1), N - 1)
    v00 = (ii * N + jj).astype(np.int32)
    # CCW quads: (i,j) → (i+1,j) → (i+1,j+1) → (i,j+1)
    faces = np.column_stack((v00, v00 + N, v00 + N + 1, v00 + 1))
    me.vertices.add(NV)
    me.vertices.foreach_set("co", verts.ravel())
    me.loops.add(NQ * 4)
    me.loops.foreach_set("vertex_index", faces.ravel())
    me.polygons.add(NQ)
    me.polygons.foreach_set("loop_start", np.arange(NQ, dtype=np.int32) * 4)
    me.polygons.foreach_set("loop_total", np.full(NQ, 4, dtype=np.int32))
    me.update()


def _add_shape_key(obj, name, mz):
    sk   = obj.shape_key_add(name=name, from_mix=False)
    NV   = N * N
    co   = np.empty(NV * 3, dtype=np.float32)
    obj.data.vertices.foreach_get("co", co)
    co   = co.reshape(NV, 3)
    co[:, 2] = (mz * Z_SCALE).ravel()
    sk.data.foreach_set("co", co.ravel())


def _assign_colour(me, m):
    attr = me.color_attributes.new(ATTR_NAME, type='FLOAT_COLOR', domain='POINT')
    r, g, b = _spin_colour(m)
    rgba = np.column_stack(
        (r.ravel(), g.ravel(), b.ravel(), np.ones(N * N, dtype=np.float32))
    )
    attr.data.foreach_set("color", rgba.ravel())


def _make_material():
    mat  = bpy.data.materials.new(MAT_NAME)
    mat.use_nodes = True
    nd   = mat.node_tree.nodes
    lk   = mat.node_tree.links
    nd.clear()
    vc   = nd.new("ShaderNodeVertexColor");    vc.layer_name = ATTR_NAME
    bsdf = nd.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Metallic"].default_value   = 0.12
    bsdf.inputs["Roughness"].default_value  = 0.30
    em   = nd.new("ShaderNodeEmission");       em.inputs["Strength"].default_value = 1.6
    mix  = nd.new("ShaderNodeMixShader");      mix.inputs["Fac"].default_value     = 0.28
    out  = nd.new("ShaderNodeOutputMaterial")
    lk.new(vc.outputs["Color"],    bsdf.inputs["Base Color"])
    lk.new(vc.outputs["Color"],    em.inputs["Color"])
    lk.new(bsdf.outputs["BSDF"],   mix.inputs[1])
    lk.new(em.outputs["Emission"], mix.inputs[2])
    lk.new(mix.outputs["Shader"],  out.inputs["Surface"])
    return mat


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    # Basis: single Néel skyrmion (Q = −1)
    print("Relaxing Basis: single skyrmion …")
    m0 = _skyrmion_at(N // 2, N // 2, N // 12)
    m0 = _relax(m0, J, D, K=K_BASE, B=0.42)
    print(f"  Q = {_topological_Q(m0):.2f}")

    # SK_Lattice: 3×3 skyrmion crystal (Q ≈ −9)
    print("Relaxing SK_Lattice: 3×3 skyrmion crystal …")
    m_lat = _lattice_skyrmions(n_row=3)
    m_lat = _relax(m_lat, J, D, K=K_BASE * 0.5, B=0.18)
    print(f"  Q = {_topological_Q(m_lat):.1f}")

    # SK_Helical: helical stripe phase (Q = 0, B = 0)
    print("Relaxing SK_Helical: helical phase …")
    m_hel = _helix()
    m_hel = _relax(m_hel, J, D, K=0.0, B=0.0, steps=3000)

    # SK_FM: field-polarised ferromagnet (Q = 0)
    print("Relaxing SK_FM: ferromagnet …")
    m_fm = _ferromagnet()
    m_fm = _relax(m_fm, J, D, K=K_BASE, B=0.80, steps=500)

    # Build scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    me  = bpy.data.meshes.new(OBJ_NAME)
    _build_mesh(me, m0[..., 2])
    _assign_colour(me, m0)

    obj = bpy.data.objects.new(OBJ_NAME, me)
    bpy.context.collection.objects.link(obj)

    obj.shape_key_add(name="Basis", from_mix=False)
    _add_shape_key(obj, "SK_Lattice", m_lat[..., 2])
    _add_shape_key(obj, "SK_Helical", m_hel[..., 2])
    _add_shape_key(obj, "SK_FM",      m_fm[..., 2])

    me.materials.append(_make_material())
    obj["holoflow:category"] = "stage-floor"
    obj["holoflow:facet"]    = True
    obj.rotation_euler[0]    = -math.pi / 2
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
    bpy.ops.export_scene.gltf(
        filepath=OUT_GLB,
        export_format='GLB',
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_image_format='WEBP',
        export_morph=True,
        export_colors=True,
        export_yup=True,
    )
    print(f"Saved  {OUT_BLEND}  and  {OUT_GLB}")


main()
