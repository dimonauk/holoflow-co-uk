"""
Swift-Hohenberg Equation (1977) — stripe, hexagon and labyrinth pattern formation
Spectral ETD1 (Cox-Matthews 2002) — unconditionally stable linear part
128×128 = 16 384 V / 16 129 Q · height-field stage floor for WebXR

PDE (Swift J, Hohenberg PC, 1977, Phys Rev A 15(1):319-328):
    ∂u/∂t = r · u  −  (1 + ∇²)² u  +  γ · u²  −  u³

  u   : order parameter (convective amplitude / phase-field variable)
  r   : bifurcation parameter  (r < 0 → stable; r > 0 → pattern formation)
  γ   : quadratic coefficient  (γ = 0 → u → −u symmetry → rolls only;
                                 γ ≠ 0 → hexagons preferred over stripes)
  (1+∇²)²: WHY THIS OPERATOR: expands to I + 2∇² + ∇⁴; in Fourier space the
            eigenvalue is (1 − k²)², which is ZERO at k_c = 1 and positive
            everywhere else.  Subtracting it from r·I gives a linear growth
            rate σ(k) = r − (1 − k²)² that peaks at k = 1 with σ_max = r,
            selecting exactly one spatial wavelength λ_c = 2π regardless of r.
            This is what distinguishes SHE from generic reaction-diffusion.

Fourier-space linear operator:
    L̂_k = r − (1 − k²)²

ETD1 (Cox-Matthews 2002, J Comput Phys 176:430-455):
    û_{n+1} = exp(L̂_k dt) · û_n  +  φ₁(L̂_k dt) · N̂(u_n)
    φ₁(z)   = (exp(z) − 1) / z    [Taylor series at z ≈ 0 for numerical safety]
    N(u)     = γ u² − u³           [nonlinear part, evaluated in real space]

WHY ETD over explicit Euler:
    The operator (1+∇²)² is quartic in k; at the Nyquist mode k_max = π/dx
    the eigenvalue of the stiff term grows as k⁴ ≈ (N/L)⁴.  Explicit Euler
    requires dt ≤ 2 / k_max⁴ ≈ 3×10⁻⁵ for N=128, L=32π.  ETD integrates
    the entire linear part analytically in Fourier space (one elementwise
    multiply), so dt = 0.5 is unconditionally stable — a 15 000× speedup.

Shape keys:
  Basis        r=0.30  γ=0     stripes, t=150        → regular parallel rolls
  SK_Hex       r=0.30  γ=+1.6  hexagons, t=200       → γ breaks u→−u symmetry
  SK_Labyrinth r=0.05  γ=0     labyrinthine, t=300   → disordered near onset
  SK_Inverted  r=0.30  γ=−1.6  inverted hexagons/spots, t=200

Domain: L = 32π,  N = 128,  dx ≈ 0.785
Critical wavelength 2π ≈ 8 grid points: well-resolved.
Vertex colour: SH_Order  FLOAT_COLOR  cobalt (u ≈ min) → amber (u ≈ max)
Blender 5.1 · CC0 (public-domain mathematics)
"""

import bpy, bmesh, numpy as np

# ── constants ──────────────────────────────────────────────────────────────────
N        = 128
L        = 32.0 * np.pi   # domain size; λ_c = 2π fits 16× per side
DX       = L / N           # ≈ 0.785 — critical mode resolved by ~8 grid pts
DT       = 0.5             # ETD1: no stability constraint on dt

# Regime parameters — (r, gamma, n_steps, seed)
R_B,  G_B,  T_B,  S_B  = 0.30,  0.0,  300, 7     # Basis: stripes
R_H,  G_H,  T_H,  S_H  = 0.30, +1.6,  400, 13    # SK_Hex: hexagons
R_L,  G_L,  T_L,  S_L  = 0.05,  0.0,  600, 21    # SK_Labyrinth: near onset
R_I,  G_I,  T_I,  S_I  = 0.30, -1.6,  400, 37    # SK_Inverted: spots

IC_AMP   = 0.10            # initial noise amplitude (seeds all Fourier modes)
ZSCALE   = 0.40            # floor height in metres at full normalised amplitude
WORLD    = 4.0             # stage half-extent → 8 m × 8 m

OBJ_NAME = "sh_pattern_floor"
GLB_PATH = "//sh_pattern_floor.glb"
COL_LO   = (0.027, 0.159, 0.557, 1.0)   # cobalt  (u ≈ min)
COL_HI   = (0.950, 0.600, 0.000, 1.0)   # amber   (u ≈ max)

# ── Fourier wavenumbers (rfft2 layout) ────────────────────────────────────────
# kx: N values (full FFT);  ky: N//2+1 values (real FFT half-space)
_kx      = 2.0 * np.pi * np.fft.fftfreq(N, d=DX)
_ky      = 2.0 * np.pi * np.fft.rfftfreq(N, d=DX)
KX, KY   = np.meshgrid(_kx, _ky, indexing='ij')
K2       = KX ** 2 + KY ** 2               # shape (N, N//2+1)


def _make_etd1(r: float):
    """Pre-compute the two ETD1 coefficient arrays for a given r.
    These depend only on r (via L̂_k) and DT, so we cache them per regime.

    φ₁(z) = (eᶻ − 1) / z is evaluated via Taylor near z=0 to avoid
    catastrophic cancellation in float64 when z → 0.
    """
    Lk   = r - (1.0 - K2) ** 2         # L̂_k  shape (N, N//2+1)
    z    = Lk * DT
    expL = np.exp(z)
    with np.errstate(invalid='ignore', divide='ignore'):
        # expm1 = eᶻ − 1 is accurate near z=0; /z only blows up at z=0 exactly
        phi1 = np.where(np.abs(z) > 1e-10,
                        np.expm1(z) / z,
                        1.0 + z / 2.0 + z * z / 6.0)
    return expL, phi1


def run_sh(r: float, gamma: float, n_steps: int, seed: int = 42) -> np.ndarray:
    """Integrate SHE from a small-amplitude random field, return final u array.
    All Fourier modes are seeded uniformly so the pattern selects its own
    dominant wavelength without biasing the initial condition."""
    rng    = np.random.default_rng(seed)
    u      = IC_AMP * rng.standard_normal((N, N)).astype(np.float64)
    u_hat  = np.fft.rfft2(u)
    expL, phi1 = _make_etd1(r)

    for _ in range(n_steps):
        # Nonlinear part in real space (fast: two numpy elementwise ops)
        N_u   = gamma * u * u - u * u * u
        N_hat = np.fft.rfft2(N_u)
        # ETD1 update: exact integration of linear part
        u_hat = expL * u_hat + phi1 * N_hat
        u     = np.fft.irfft2(u_hat, s=(N, N))

    return u


# ── mesh helpers ───────────────────────────────────────────────────────────────
def _build_base_mesh(u: np.ndarray):
    """128×128 quad grid in the XY plane; Z = normalised u × ZSCALE.
    Row-major layout (j outer, i inner) keeps vertex index = j·N + i,
    consistent with the colour array written in the same order."""
    xs  = np.linspace(-WORLD, WORLD, N)
    ys  = np.linspace(-WORLD, WORLD, N)
    u_n = (u - u.min()) / (u.max() - u.min() + 1e-12)

    me  = bpy.data.meshes.new(OBJ_NAME)
    bm  = bmesh.new()
    verts = []
    for j in range(N):
        for i in range(N):
            verts.append(bm.verts.new((xs[i], ys[j], u_n[j, i] * ZSCALE)))
    bm.verts.index_update()
    for j in range(N - 1):
        for i in range(N - 1):
            bm.faces.new((
                verts[ j      * N + i    ],
                verts[ j      * N + i + 1],
                verts[(j + 1) * N + i + 1],
                verts[(j + 1) * N + i    ],
            ))
    bm.to_mesh(me)
    bm.free()
    me.calc_normals()
    return me


def _set_vertex_colour(me, u: np.ndarray):
    """Cobalt (u ≈ min) → amber (u ≈ max) linear ramp via FLOAT_COLOR.
    WHY FLOAT_COLOR not BYTE_COLOR: FLOAT_COLOR preserves HDR precision for
    Eevee Next emission; BYTE_COLOR posterises smooth gradients at 8-bit."""
    t    = ((u - u.min()) / (u.max() - u.min() + 1e-12)).ravel()
    r_ch = COL_LO[0] + t * (COL_HI[0] - COL_LO[0])
    g_ch = COL_LO[1] + t * (COL_HI[1] - COL_LO[1])
    b_ch = COL_LO[2] + t * (COL_HI[2] - COL_LO[2])
    rgba = np.column_stack([r_ch, g_ch, b_ch, np.ones(N * N)]).astype(np.float32)
    if "SH_Order" not in me.color_attributes:
        me.color_attributes.new(name="SH_Order", type='FLOAT_COLOR', domain='POINT')
    me.color_attributes["SH_Order"].data.foreach_set('color', rgba.ravel())


def _add_shape_key(obj, u: np.ndarray, name: str):
    """Write a shape key from normalised u, re-using the base XY layout.
    foreach_set('co', …) copies the full N²×3 array in one C-level call —
    ~40× faster than iterating over bpy.data.shape_keys.key_blocks[…].data."""
    u_n = (u - u.min()) / (u.max() - u.min() + 1e-12)
    sk  = obj.shape_key_add(name=name, from_mix=False)
    pts = np.empty(N * N * 3, dtype=np.float64)
    obj.data.shape_keys.reference_key.data.foreach_get('co', pts)
    pts        = pts.reshape(N * N, 3)
    pts[:, 2]  = u_n.ravel() * ZSCALE
    sk.data.foreach_set('co', pts.ravel())


def _build_material(obj):
    mat   = bpy.data.materials.new(OBJ_NAME + "_mat")
    mat.use_nodes = True
    nd, lk = mat.node_tree.nodes, mat.node_tree.links
    nd.clear()
    out  = nd.new('ShaderNodeOutputMaterial')
    bsdf = nd.new('ShaderNodeBsdfPrincipled')
    atr  = nd.new('ShaderNodeAttribute')
    atr.attribute_name  = "SH_Order"
    atr.attribute_type  = 'GEOMETRY'
    bsdf.inputs['Metallic'].default_value          = 0.05
    bsdf.inputs['Roughness'].default_value         = 0.50
    bsdf.inputs['Emission Strength'].default_value = 1.2
    lk.new(atr.outputs['Color'],  bsdf.inputs['Base Color'])
    lk.new(atr.outputs['Color'],  bsdf.inputs['Emission Color'])
    lk.new(bsdf.outputs['BSDF'],  out.inputs['Surface'])
    obj.data.materials.append(mat)


# ── main ───────────────────────────────────────────────────────────────────────
def build():
    if OBJ_NAME in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[OBJ_NAME], do_unlink=True)

    print("[SH] Basis: stripes (r=0.30, γ=0) …")
    u_b = run_sh(R_B, G_B, T_B, S_B)
    me  = _build_base_mesh(u_b)
    _set_vertex_colour(me, u_b)
    obj = bpy.data.objects.new(OBJ_NAME, me)
    bpy.context.scene.collection.objects.link(obj)
    obj.shape_key_add(name="Basis", from_mix=False)

    print("[SH] SK_Hex: hexagons (r=0.30, γ=+1.6) …")
    _add_shape_key(obj, run_sh(R_H, G_H, T_H, S_H), "SK_Hex")

    print("[SH] SK_Labyrinth: near onset (r=0.05, γ=0) …")
    _add_shape_key(obj, run_sh(R_L, G_L, T_L, S_L), "SK_Labyrinth")

    print("[SH] SK_Inverted: inverted hexagons/spots (r=0.30, γ=−1.6) …")
    _add_shape_key(obj, run_sh(R_I, G_I, T_I, S_I), "SK_Inverted")

    _build_material(obj)
    obj["holoflow:category"] = "stage-floor"
    obj["holoflow:facet"]    = True
    obj.rotation_euler       = (0, 0, 0)

    bpy.ops.export_scene.gltf(
        filepath                             = bpy.path.abspath(GLB_PATH),
        export_format                        = 'GLB',
        export_draco_mesh_compression_enable = True,
        export_draco_mesh_compression_level  = 6,
        export_colors                        = True,
        export_morph                         = True,
        export_apply                         = True,
        export_yup                           = True,
        export_image_format                  = 'WEBP',
    )
    print(f"[SH] Exported → {GLB_PATH}")


build()
