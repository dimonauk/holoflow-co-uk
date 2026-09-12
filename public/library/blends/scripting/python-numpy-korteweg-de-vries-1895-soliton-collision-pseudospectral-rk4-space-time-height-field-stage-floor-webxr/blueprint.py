"""
KdV (Korteweg–de Vries) Equation 1895 — Soliton Collisions,
Fourier Pseudospectral + RK4, Space-Time Height-Field Stage Floor (Blender 5.1)
Korteweg D J & de Vries G (1895) · bpy direct-data API · CC0
────────────────────────────────────────────────────────────────────────────────

TECHNIQUE:
  The Korteweg–de Vries equation governs weakly nonlinear dispersive waves in
  shallow water, plasmas, and optical fibres.  Its N-soliton solutions survive
  collisions elastically: each wave packet emerges with its original shape and
  speed but with a measurable spatial phase shift — the hallmark of complete
  integrability.  This blueprint builds a space-time diagram as a stage floor:
  the x-axis is space, the y-axis is time, and height encodes u(x,t).

MATHEMATICS — KdV and its solitons:
  u_t + 6u u_x + u_xxx = 0

  1-soliton (right-moving hump):
    u₁(x,t) = 2κ² sech²(κ(x − 4κ²t − x₀))
    speed c = 4κ²  amplitude A = c/2 = 2κ²  FWHM ≈ 3.526/κ

  2-soliton asymptotic phase shift (κ₁ > κ₂):
    Δx₊ = (2/κ₁) ln((κ₁+κ₂)/(κ₁-κ₂))  (faster soliton, shifted forward)
    Δx₋ = (2/κ₂) ln((κ₁+κ₂)/(κ₁-κ₂))  (slower soliton, shifted backward)
    For κ₁=1, κ₂=0.5: Δx₊≈2.20 m, Δx₋≈4.39 m — clearly visible in the floor.

  Conserved quantities (integrability invariants):
    I₁ = ∫u dx,  I₂ = ½∫u² dx,  I₃ = ∫(u³ − ½u_x²) dx  (+infinite tower)

NUMERICAL METHOD — Fourier Pseudospectral + RK4:
  Periodic domain x ∈ [0, L], N_X points, wavenumbers k_j = 2π/L · j.
  Fourier formulation: û_t = ik³ û − 3ik FFT(u²)
    ik³ û  : linear dispersive operator (purely imaginary eigenvalues)
    −3ik FFT(u²) : from −6u u_x = −3∂(u²)/∂x, evaluated pseudospectrally.

  WHY pseudospectral over FD: derivatives are exact to machine precision in
  spectral space; exponential convergence for smooth solitons; no numerical
  dispersion from spatial discretisation.

  WHY RK4 not ETDRK4: ik³ has purely imaginary eigenvalues — no stiff real
  part. ETD1's key benefit (treating negative-real stiffness exactly) does not
  apply here. RK4 is correct and simpler when de-aliased k_max³·dt < 2√2.

  Dealiasing: 2/3-rule (Orszag 1971) — zero out |k| > 2/3·k_Nyquist before
  evaluating u² in real space, preventing aliasing energy from quadratic NL.

  Stability: |ik³·dt| ≤ 2√2 ≈ 2.83 for RK4 on the imaginary axis.
  With L=64, N=128, de-aliased k_max≈4.19: dt_stable≤0.038.  DT=0.02. ✓

SHAPE KEYS (space-time diagrams):
  Basis     2-soliton κ=[1, 0.5], x₀=[8, 32] — collision at t≈8, phase shift visible
  SK_Single 1-soliton κ=1, x₀=16 — diagonal ridge, verifies speed c=4κ²
  SK_Three  3-soliton κ=[1, 0.75, 0.5], x₀=[5, 18, 32] — sequential collisions
  SK_Slow   2-soliton κ=[0.75, 0.5], x₀=[5, 20] — slower pair, longer interaction

Colour: KdV_Height FLOAT_COLOR — cobalt (u≈0) → amber (soliton peak).
Vertices: 128×128=16384.  Quads: 127×127=16129.
Export: +Y-up; Draco-6; WebP; morph targets for shape keys.
"""

import bpy, numpy as np, pathlib, math

# ── Named constants ────────────────────────────────────────────────────────────
N_X          = 128          # spatial grid points  (x-axis)
N_T          = 128          # time snapshot rows   (y-axis / time)
L            = 64.0         # spatial domain length (periodic)
T_FINAL      = 12.0         # simulation end time
N_STEPS      = 600          # RK4 steps  →  DT = 0.02  (stability bound ≤ 0.038)
DT           = T_FINAL / N_STEPS   # = 0.02
WORLD_SCALE  = 2.0          # floor half-width (Blender metres)
HEIGHT_SCALE = 0.18         # u / U_NORM → this many metres above floor
U_NORM       = 2.0          # normalisation: 2κ² at κ=1 (tallest soliton amplitude)
COL_LOW      = (0.030, 0.150, 0.580, 1.0)   # cobalt  (u≈0 background)
COL_HIGH     = (1.000, 0.650, 0.000, 1.0)   # amber   (soliton peak)
ATTR_NAME    = "KdV_Height"
OBJ_NAME     = "kdv_soliton_floor"
BLEND_NAME   = "kdv_soliton_floor.blend"
GLB_NAME     = "kdv_soliton_floor.glb"
OUTPUT_DIR   = pathlib.Path(bpy.path.abspath("//"))


# ── Physics helpers ────────────────────────────────────────────────────────────
def _wavenumbers(n: int, domain_length: float) -> np.ndarray:
    """
    Angular wavenumbers for an n-point periodic FFT grid of length L.
    np.fft.fftfreq(n) × n gives integer cycle counts [0,1,…,N/2-1,-N/2,…,-1].
    Multiply by 2π/L to get radians/unit.
    """
    return (2.0 * np.pi / domain_length) * np.fft.fftfreq(n, d=1.0 / n)


def _dealias_mask(k: np.ndarray) -> np.ndarray:
    """
    2/3-rule mask: exactly zeros the top 1/3 of wavenumbers.
    Quadratic NL creates wavenumbers up to 2·k_max; to prevent aliasing into
    the resolved band, we need 2·k_max ≤ k_Nyquist, i.e. k_max ≤ k_Nyq/2,
    which via k_Nyq = 3/2·k_max gives the 2/3 threshold.  (Orszag 1971.)
    """
    return (np.abs(k) <= (2.0 / 3.0) * np.abs(k).max()).astype(complex)


def _soliton_ic(x: np.ndarray, kappas, x0s) -> np.ndarray:
    """
    Superposition of 1-soliton ICs at t=0 for form u_t + 6u u_x + u_xxx = 0.
    u₁(x; κ, x₀) = 2κ² sech²(κ(x − x₀)).  Amplitude = 2κ², speed = 4κ².
    Superposition is exact only at t=0; interactions emerge from the PDE.
    """
    u = np.zeros_like(x, dtype=float)
    for kap, x0 in zip(kappas, x0s):
        theta = kap * (x - x0)
        u += 2.0 * kap**2 / np.cosh(theta)**2
    return u


def _rhs(u_hat: np.ndarray, k: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """
    KdV RHS in Fourier space: û_t = ik³ û − 3ik FFT(u²).
    Dispersive term ik³ û: purely imaginary, no dissipation — the equation
    is Hamiltonian and conserves I₂ = ½∫u² dx exactly in infinite precision.
    Nonlinear term: −3ik FFT(u²) implements −3 ∂(u²)/∂x pseudospectrally.
    Mask applied before u² to prevent aliasing buildup over 600 steps.
    """
    u = np.fft.ifft(u_hat * mask).real
    u2_hat = np.fft.fft(u ** 2)
    return 1j * k**3 * u_hat - 3j * k * u2_hat


def _rk4_step(u_hat: np.ndarray, k: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """
    Classical 4th-order Runge–Kutta step in Fourier space.
    WHY RK4 here: error O(dt⁵) per step; with dt=0.02 and 600 steps the
    accumulated phase error is O(600·dt⁵) ≈ 7×10⁻⁹ per mode — negligible.
    Dealias at the end of each stage (k1 through k4) prevents aliasing energy
    from accumulating within the multi-stage evaluation.
    """
    k1 = _rhs(u_hat,                  k, mask)
    k2 = _rhs(u_hat + 0.5*DT*k1,     k, mask)
    k3 = _rhs(u_hat + 0.5*DT*k2,     k, mask)
    k4 = _rhs(u_hat + DT*k3,          k, mask)
    return (u_hat + (DT / 6.0) * (k1 + 2*k2 + 2*k3 + k4)) * mask


def _simulate(kappas, x0s) -> np.ndarray:
    """
    Integrate KdV from soliton ICs; collect N_T evenly-spaced snapshots.
    Returns u_spacetime (N_X, N_T): column j is u(x, t_j).
    Snapshot schedule: np.linspace(0, N_STEPS, N_T) rounded to integers,
    giving uniform time coverage without fractional-step interpolation.
    """
    x    = np.linspace(0.0, L, N_X, endpoint=False)
    k    = _wavenumbers(N_X, L)
    mask = _dealias_mask(k)
    u    = _soliton_ic(x, kappas, x0s)
    u_hat = np.fft.fft(u) * mask

    snap_at = np.round(np.linspace(0, N_STEPS, N_T)).astype(int)
    u_st   = np.zeros((N_X, N_T), dtype=float)
    step   = 0
    for it in range(N_T):
        while step < snap_at[it]:
            u_hat = _rk4_step(u_hat, k, mask)
            step += 1
        u_st[:, it] = np.fft.ifft(u_hat).real
    return u_st


# ── Mesh helpers ───────────────────────────────────────────────────────────────
def _verts_faces(u_st: np.ndarray):
    """
    N_X × N_T vertex grid; x=space, y=time (forward = past→future), z=u.
    Quads: (ix,it)→(ix+1,it)→(ix+1,it+1)→(ix,it+1). Row-major vertex index.
    Height clamped at 0 below (no artefacts from numerical noise) and 3·U_NORM
    above (prevents extreme colour saturation on 3-soliton triple peak).
    """
    xs = np.linspace(-WORLD_SCALE, WORLD_SCALE, N_X)
    ys = np.linspace(-WORLD_SCALE, WORLD_SCALE, N_T)
    gx, gy = np.meshgrid(xs, ys, indexing='ij')   # (N_X, N_T)
    gz = np.clip(u_st / U_NORM, 0.0, 3.0) * HEIGHT_SCALE
    verts = np.stack([gx.ravel(), gy.ravel(), gz.ravel()], axis=1)
    ix = np.arange(N_X - 1)[:, None]
    it = np.arange(N_T - 1)[None, :]
    v0 = (ix * N_T + it).ravel()
    faces = np.stack([v0, v0 + N_T, v0 + N_T + 1, v0 + 1], axis=1)
    return verts, faces


def _apply_colour(me, u_st: np.ndarray):
    """FLOAT_COLOR point attribute: cobalt (low) → amber (soliton peak)."""
    attr = me.attributes.get(ATTR_NAME)
    if attr:
        me.attributes.remove(attr)
    attr = me.attributes.new(ATTR_NAME, 'FLOAT_COLOR', 'POINT')
    t   = np.clip(u_st.ravel() / U_NORM, 0.0, 1.0)
    r   = COL_LOW[0] + t * (COL_HIGH[0] - COL_LOW[0])
    g   = COL_LOW[1] + t * (COL_HIGH[1] - COL_LOW[1])
    b   = COL_LOW[2] + t * (COL_HIGH[2] - COL_LOW[2])
    a   = np.ones_like(r)
    attr.data.foreach_set("color", np.stack([r, g, b, a], axis=1).ravel().tolist())


def _add_shape_key(ob, u_st: np.ndarray, name: str):
    """Append a new shape key holding the vertex positions for u_st."""
    verts, _ = _verts_faces(u_st)
    sk = ob.shape_key_add(name=name, from_mix=False)
    sk.data.foreach_set("co", verts.ravel().tolist())


def _make_material(ob):
    """MixShader: Principled BSDF + Emission driven by KdV_Height attribute."""
    mat = bpy.data.materials.new("KdV_Floor_Mat")
    mat.use_nodes = True
    nt  = mat.node_tree
    nt.nodes.clear()
    out  = nt.nodes.new('ShaderNodeOutputMaterial')
    mix  = nt.nodes.new('ShaderNodeMixShader');  mix.inputs[0].default_value = 0.35
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    emi  = nt.nodes.new('ShaderNodeEmission');   emi.inputs['Strength'].default_value = 1.6
    attr = nt.nodes.new('ShaderNodeAttribute')
    attr.attribute_name = ATTR_NAME
    attr.attribute_type = 'GEOMETRY'
    bsdf.inputs['Roughness'].default_value = 0.50
    nt.links.new(attr.outputs['Color'], bsdf.inputs['Base Color'])
    nt.links.new(attr.outputs['Color'], emi.inputs['Color'])
    nt.links.new(bsdf.outputs['BSDF'],      mix.inputs[1])
    nt.links.new(emi.outputs['Emission'],   mix.inputs[2])
    nt.links.new(mix.outputs['Shader'],     out.inputs['Surface'])
    ob.data.materials.append(mat)


def _export(ob):
    """Apply +Y-up rotation (Holoflow convention), tag, export GLB."""
    ob.rotation_euler = (math.pi / 2, 0, 0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    ob['holoflow:facet']    = False
    ob['holoflow:category'] = 'stage-floor'
    ob['holoflow:slug']     = OBJ_NAME
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath    = str(OUTPUT_DIR / GLB_NAME),
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

    print("[KdV] Basis — 2-soliton κ=[1, 0.5], x₀=[8, 32], collision t≈8…")
    u_basis = _simulate([1.0, 0.5], [8.0, 32.0])
    verts, faces = _verts_faces(u_basis)
    me = bpy.data.meshes.new(OBJ_NAME + "_mesh")
    me.from_pydata(verts.tolist(), [], faces.tolist())
    me.update()
    ob = bpy.data.objects.new(OBJ_NAME, me)
    bpy.context.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    ob.shape_key_add(name="Basis", from_mix=False)
    _apply_colour(ob.data, u_basis)

    print("[KdV] SK_Single — 1-soliton κ=1, x₀=16…")
    _add_shape_key(ob, _simulate([1.0], [16.0]), "SK_Single")

    print("[KdV] SK_Three — 3-soliton κ=[1, 0.75, 0.5], x₀=[5, 18, 32]…")
    _add_shape_key(ob, _simulate([1.0, 0.75, 0.5], [5.0, 18.0, 32.0]), "SK_Three")

    print("[KdV] SK_Slow — 2-soliton κ=[0.75, 0.5], x₀=[5, 20]…")
    _add_shape_key(ob, _simulate([0.75, 0.5], [5.0, 20.0]), "SK_Slow")

    _make_material(ob)
    _export(ob)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_DIR / BLEND_NAME))
    print(f"[KdV] Done. V={N_X*N_T}  Q={(N_X-1)*(N_T-1)}")
    print(f"[KdV] Basis u: {u_basis.min():.3f}..{u_basis.max():.3f}")


main()
