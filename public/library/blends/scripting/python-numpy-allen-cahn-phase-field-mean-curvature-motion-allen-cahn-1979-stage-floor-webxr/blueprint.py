"""
Allen–Cahn Phase-Field Equation: Interface Motion by Mean Curvature
====================================================================
TECHNIQUE (2–3 sentences):
  The Allen–Cahn equation is a non-conserved phase-field model in which a
  scalar order parameter φ(x,y,t) ∈ [−1,+1] evolves toward one of two
  equilibrium phases (φ = ±1) under a Ginzburg–Landau double-well free energy.
  Interfaces — the thin transition layers where φ ≈ 0 — move by their local
  mean curvature, so small islands shrink and vanish while large ones grow
  (Allen & Cahn 1979). Unlike Cahn–Hilliard, the phase integral is NOT
  conserved: the slower phase progressively disappears.

MATHEMATICS:
  ∂φ/∂t = ε²∇²φ − F′(φ)          (Ginzburg–Landau gradient flow)
  F(φ)   = ¼(1 − φ²)²             (double-well free energy)
  F′(φ)  = φ³ − φ = φ(φ−1)(φ+1)  (zero at φ=−1, 0, +1)

  Sharp-interface limit: interfaces move with normal velocity v_n = ε κ,
  where κ is the mean curvature. Small circular domains shrink as R(t)²
  ≈ R₀² − 2ε²t. Domain coarsening law: ⟨L⟩ ∼ t^(1/2)  (vs t^(1/3) for CH).

NUMERICAL METHOD — ETD1 (Exponential Time Differencing, Cox & Matthews 2002):
  Split ∂φ/∂t = L̂φ + N(φ) with L̂ = ε²∇² + 1 (in Fourier: λ_k = 1 − ε²|k|²)
  and N(φ) = −φ³ (the truly nonlinear part after shifting the +φ into L̂).

  ETD1 step (exact for linear, Euler for nonlinear):
    φ̂(t+dt) = E_k · φ̂(t) + φ₁(λ_k dt)·dt · F̂{N(φ(t))}
  where
    E_k    = exp(λ_k · dt)              (propagator — exact linear evolution)
    φ₁(z)  = expm1(z)/z  ≈ 1 + z/2     (ETD weight; stable via expm1 for z≈0)

  WHY ETD1 over semi-implicit: for Allen-Cahn the linear eigenvalue λ_k
  crosses zero at k² = 1/ε². Semi-implicit denominators near zero yield
  near-singular updates; ETD1 uses the exact propagator and avoids this.
  High-k modes (λ_k << 0) are damped to near-zero in one step — fully stable.

SOURCES (permissive):
  Allen SM & Cahn JW 1979 Acta Met 27:1085 doi:10.1016/0001-6160(79)90196-2
    — mathematical equations (public domain as mathematical content)
  Cox SM & Matthews PC 2002 J Comput Phys 176:430 doi:10.1006/jcph.2002.6995
    — ETD1 algorithm (mathematical method, equations public domain)
  NumPy — BSD-3-Clause https://numpy.org github.com/numpy/numpy
"""

import bpy, bmesh, numpy as np, pathlib, math

# ── Named constants ────────────────────────────────────────────────────────────
N             = 128       # grid resolution N×N
WORLD_SCALE   = 4.0       # mesh half-width (metres in Blender units)
HEIGHT_SCALE  = 0.40      # φ → z amplitude (φ=+1 → +0.40 m peak)
EPS_BASIS     = 0.020     # interface thickness ε  (Basis + Coarsened)
EPS_FINE      = 0.012     # sharper ε → fine-scale texture (SK_Fine)
EPS_BROAD     = 0.040     # broader ε → diffuse interfaces (SK_Broad)
DT            = 0.10      # ETD1 time step (unconditionally stable for linear)
STEPS_BASIS   = 100       # Basis: t=10, rapid nucleation
STEPS_COARSE  = 600       # SK_Coarsened: t=60, moderate domain growth
STEPS_FINE    = 250       # SK_Fine: t=25, sharp fractal-like texture
STEPS_BROAD   = 150       # SK_Broad: t=15, diffuse soft domains
SEED          = 42
COL_M1        = (0.030, 0.200, 0.780, 1.0)  # cobalt  (φ=−1 phase)
COL_P1        = (0.980, 0.620, 0.050, 1.0)  # amber   (φ=+1 phase)
ATTR_NAME     = "AC_Phase"
OBJ_NAME      = "allen_cahn_floor"
BLEND_NAME    = "allen_cahn_floor.blend"
GLB_NAME      = "allen_cahn_floor.glb"
OUTPUT_DIR    = pathlib.Path(bpy.path.abspath("//"))


# ── Physics helpers ────────────────────────────────────────────────────────────
def _wavenumbers_rfft(n: int):
    """Return |k|² for rfft2 output shape (n, n//2+1)."""
    kx = np.fft.fftfreq(n, d=1.0/n)[:, None]   # (n, 1) — integer cycles/grid
    ky = np.fft.rfftfreq(n, d=1.0/n)[None, :]   # (1, n//2+1)
    return kx**2 + ky**2                          # (n, n//2+1)


def _etd1_coefficients(k2, eps: float, dt: float):
    """
    Precompute ETD1 coefficients for Allen–Cahn.
    λ_k = 1 − ε²k²  (linear Fourier eigenvalue after shifting +φ into L̂)
    E_k = exp(λ_k · dt)               (exact propagator)
    P_k = expm1(λ_k·dt)/(λ_k·dt)     (φ₁ weight, stable via expm1)
    WHY separate E and P: E handles stiff high-k decay exactly; P weights the
    nonlinear update correctly when dt is large relative to λ_k.
    """
    lam    = 1.0 - eps**2 * k2      # (n, n//2+1) — positive for low-k
    lam_dt = lam * dt
    E_k    = np.exp(lam_dt)
    # φ₁(z) = (exp(z)−1)/z, numerically: expm1(z)/z. Taylor for z≈0.
    safe   = np.abs(lam_dt) > 1e-10
    P_k    = np.where(
        safe,
        np.expm1(np.where(safe, lam_dt, 0.0)) / np.where(safe, lam_dt, 1.0),
        1.0 + lam_dt * (0.5 + lam_dt * (1.0/6.0 + lam_dt / 24.0))
    )
    return E_k, P_k                  # both (n, n//2+1) for rfft2


def _integrate(phi: np.ndarray, k2, E_k, P_k, dt: float, steps: int):
    """
    Run ETD1 integration of Allen–Cahn for `steps` time steps.
    Returns updated φ field (not mutated in-place — caller owns clone).
    WHY rfft2: φ is real; rfft2 halves the FFT work and avoids spurious
    imaginary components from rounding in the inverse transform.
    """
    phi = phi.copy()
    for _ in range(steps):
        phi_hat = np.fft.rfft2(phi)
        nl_hat  = np.fft.rfft2(-phi**3)        # N(φ) = −φ³ (nonlinear part)
        phi_hat = E_k * phi_hat + P_k * dt * nl_hat
        phi     = np.fft.irfft2(phi_hat, s=(N, N))
        phi     = np.clip(phi, -2.0, 2.0)      # guard against rare blow-up
    return phi


# ── Mesh helpers ───────────────────────────────────────────────────────────────
def _verts_faces(phi: np.ndarray):
    """Build flat N×N grid vertices and (N−1)² quad faces from φ field."""
    xs = np.linspace(-WORLD_SCALE, WORLD_SCALE, N)
    ys = np.linspace(-WORLD_SCALE, WORLD_SCALE, N)
    # z = φ mapped to [−HEIGHT_SCALE, +HEIGHT_SCALE]
    zs = phi * HEIGHT_SCALE
    gx, gy = np.meshgrid(xs, ys, indexing='ij')
    verts  = np.stack([gx.ravel(), gy.ravel(), zs.ravel()], axis=1)
    # CCW quads: (i,j), (i+1,j), (i+1,j+1), (i,j+1)
    i  = np.arange(N - 1)[:, None]
    j  = np.arange(N - 1)[None, :]
    v0 = (i * N + j).ravel()
    faces = np.stack([v0, v0 + N, v0 + N + 1, v0 + 1], axis=1)
    return verts, faces


def _build_or_replace_mesh(phi: np.ndarray, name: str):
    """Create or replace the Blender mesh object from φ field."""
    verts, faces = _verts_faces(phi)
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts.tolist(), [], faces.tolist())
    me.update()
    ob = bpy.data.objects.get(OBJ_NAME)
    if ob:
        bpy.data.objects.remove(ob, do_unlink=True)
    ob = bpy.data.objects.new(OBJ_NAME, me)
    bpy.context.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    return ob


def _apply_colour(me, phi: np.ndarray):
    """
    Write FLOAT_COLOR vertex attribute AC_Phase.
    Colour = LERP(cobalt, amber, (φ+1)/2).
    WHY FLOAT_COLOR not BYTE_COLOR: preserves full-range phase values in GLB;
    BYTE_COLOR clamps and quantises to 8-bit per channel.
    """
    attr = me.attributes.get(ATTR_NAME)
    if attr:
        me.attributes.remove(attr)
    attr = me.attributes.new(ATTR_NAME, 'FLOAT_COLOR', 'POINT')
    t   = (phi.ravel() + 1.0) / 2.0           # [0, 1]
    r   = COL_M1[0] + t * (COL_P1[0] - COL_M1[0])
    g   = COL_M1[1] + t * (COL_P1[1] - COL_M1[1])
    b   = COL_M1[2] + t * (COL_P1[2] - COL_M1[2])
    a   = np.ones_like(r)
    cols = np.stack([r, g, b, a], axis=1).ravel()
    attr.data.foreach_set("color", cols.tolist())


def _add_shape_key(ob, phi: np.ndarray, sk_name: str):
    """Add a shape key from a φ field; update z-coordinates only."""
    verts, _ = _verts_faces(phi)
    sk = ob.shape_key_add(name=sk_name, from_mix=False)
    co = np.zeros(len(verts) * 3)
    for idx, v in enumerate(verts):
        co[idx*3:idx*3+3] = v
    sk.data.foreach_set("co", co.tolist())


def _make_material(ob):
    """MixShader: Principled BSDF + Emission driven by AC_Phase attribute."""
    mat = bpy.data.materials.new("AC_Floor_Mat")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out  = nt.nodes.new('ShaderNodeOutputMaterial')
    mix  = nt.nodes.new('ShaderNodeMixShader')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    emi  = nt.nodes.new('ShaderNodeEmission')
    attr = nt.nodes.new('ShaderNodeAttribute')
    attr.attribute_name = ATTR_NAME
    attr.attribute_type = 'GEOMETRY'
    bsdf.inputs['Roughness'].default_value = 0.55
    emi.inputs['Strength'].default_value   = 1.8
    mix.inputs[0].default_value            = 0.35  # fac → blend bsdf/emi
    nt.links.new(attr.outputs['Color'], bsdf.inputs['Base Color'])
    nt.links.new(attr.outputs['Color'], emi.inputs['Color'])
    nt.links.new(bsdf.outputs['BSDF'], mix.inputs[1])
    nt.links.new(emi.outputs['Emission'], mix.inputs[2])
    nt.links.new(mix.outputs['Shader'], out.inputs['Surface'])
    ob.data.materials.append(mat)


def _export(ob):
    """Apply transforms (+Y up, holoflow convention) then export GLB."""
    import mathutils
    ob.rotation_euler = mathutils.Euler((math.pi / 2, 0, 0), 'XYZ')
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    ob["holoflow:facet"]    = True
    ob["holoflow:category"] = "stage-floor"
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath     = str(OUTPUT_DIR / GLB_NAME),
        use_selection=True,
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_image_format='WEBP',
        export_morph=True,
        export_colors=True,
        export_yup=True,
    )


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    rng = np.random.default_rng(SEED)
    k2  = _wavenumbers_rfft(N)

    # ── Precompute ETD1 coefficients for each variant ──────────────────────
    E_b, P_b = _etd1_coefficients(k2, EPS_BASIS, DT)
    E_f, P_f = _etd1_coefficients(k2, EPS_FINE,  DT)
    E_br, P_br= _etd1_coefficients(k2, EPS_BROAD, DT)

    # ── Initial condition: small random perturbation around φ=0 ────────────
    ic = rng.standard_normal((N, N)) * 0.05   # perturbation ≪ 1

    # Basis (t=10): early nucleation — many fine-scale islands
    phi_basis = _integrate(ic, k2, E_b, P_b, DT, STEPS_BASIS)
    ob = _build_or_replace_mesh(phi_basis, OBJ_NAME + "_mesh")
    ob.shape_key_add(name="Basis", from_mix=False)
    _apply_colour(ob.data, phi_basis)

    # SK_Coarsened (t=60): moderate domain growth, fewer larger blobs
    phi_coarse = _integrate(phi_basis, k2, E_b, P_b, DT, STEPS_COARSE)
    _add_shape_key(ob, phi_coarse, "SK_Coarsened")

    # SK_Fine (ε=0.012, t=25): sharper interfaces, fractal-like texture
    phi_fine = _integrate(ic, k2, E_f, P_f, DT, STEPS_FINE)
    _add_shape_key(ob, phi_fine, "SK_Fine")

    # SK_Broad (ε=0.040, t=15): diffuse interfaces, soft domain morphology
    phi_broad = _integrate(ic, k2, E_br, P_br, DT, STEPS_BROAD)
    _add_shape_key(ob, phi_broad, "SK_Broad")

    _make_material(ob)
    _export(ob)

    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_DIR / BLEND_NAME))
    print(f"[Allen–Cahn] Done. φ range: {phi_basis.min():.3f} .. {phi_basis.max():.3f}")
    print(f"[Allen–Cahn] Vertices: {N*N}  Quads: {(N-1)**2}")


main()
