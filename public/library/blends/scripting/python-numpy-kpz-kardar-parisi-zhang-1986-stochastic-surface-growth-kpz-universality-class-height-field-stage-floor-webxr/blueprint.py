"""
KPZ Equation: Stochastic Surface Growth and the KPZ Universality Class
=======================================================================
TECHNIQUE (2–3 sentences):
  The Kardar–Parisi–Zhang (KPZ) equation (Kardar, Parisi & Zhang 1986) is the
  canonical model for stochastic surface growth: ∂h/∂t = ν∇²h + (λ/2)|∇h|² + η.
  The linear ν∇²h term smooths the surface; the quadratic (λ/2)|∇h|² tilts
  the growth direction toward the local surface normal, accelerating growth
  on slopes; η is Gaussian white noise that roughens the interface. Setting
  λ = 0 recovers the earlier Edwards–Wilkinson (EW) theory; switching λ on
  shifts the universality class (roughness α, growth β, dynamic z exponents)
  and changes the surface statistics from Gaussian to Tracy–Widom GUE.

MATHEMATICS:
  KPZ equation (Kardar, Parisi, Zhang 1986 PRL 56:889):
    ∂h/∂t = ν∇²h + (λ/2)|∇h|² + η(x,t)
  Noise statistics:
    ⟨η(x,t)⟩ = 0
    ⟨η(x,t)η(x′,t′)⟩ = 2D δ²(x−x′) δ(t−t′)

  Hopf–Cole: h = (2ν/λ) log Z → ∂Z/∂t = ν∇²Z + (λ/2ν)ηZ (exact in 1D).
  2D KPZ exponents (numerical): α≈0.38, β≈0.24, z≈1.58.
  EW (λ=0): α=1/2, β=1/4, z=2. Family–Vicsek: W(L,t) = L^α·f(t/L^z).

NUMERICAL METHOD — pseudo-spectral semi-implicit (Euler–Maruyama):
  Split: ∂h/∂t = L̂h + N(h) + η  with  L̂h = ν∇²h  (linear, stiff)
                                         N(h) = (λ/2)|∇h|²  (nonlinear)

  Semi-implicit update in Fourier space:
    ĥ_new(k) = [ ĥ(k) + dt·( N̂(k) + η̂(k) ) ] / (1 + ν|k|²·dt)

  Semi-implicit: ν∇²h eigenvalues −ν|k|²→−∞; explicit requires dt<0.001.
  Denominator (1+ν|k|²dt) is unconditionally stable for any dt.
  Gradient: irfft2(i·kx·rfft2(h)) — spectral accuracy, no aliasing.
  Noise σ = sqrt(2D/(dx²·dt)): dx² concentrates continuous δ²(x-x') per cell.
  Mean removal: ⟨h⟩→0 each step; ⟨(λ/2)|∇h|²⟩>0 causes drift otherwise.

SOURCES (permissive):
  Kardar M, Parisi G, Zhang Y-C 1986 Phys Rev Lett 56:889
    doi:10.1103/PhysRevLett.56.889  — math content (public domain)
  Edwards SF, Wilkinson DR 1982 Proc R Soc A 381:17
    doi:10.1098/rspa.1982.0056  — EW baseline (math public domain)
  NumPy — BSD-3-Clause  https://numpy.org  github.com/numpy/numpy
"""

import bpy, bmesh, numpy as np, pathlib

# ── Named constants ─────────────────────────────────────────────────────────
N            = 128       # grid resolution N×N
WORLD_SCALE  = 4.0       # mesh half-width (metres)
HEIGHT_SCALE = 0.35      # normalised height amplitude (metres)
NU           = 0.50      # surface-tension coefficient ν
LAM_BASIS    = 1.00      # KPZ coupling λ — Basis + SK_Long
LAM_STRONG   = 2.00      # stronger KPZ — SK_Strong
# LAM_EW = 0.0 → Edwards–Wilkinson limit
NOISE_D      = 0.30      # noise temperature D: ⟨η²⟩ = 2D/dx²/dt
DT           = 0.05      # Euler–Maruyama time step
STEPS_BASIS  = 60        # Basis: t = 3.0 early roughening
STEPS_LONG   = 240       # SK_Long: t = 12.0 developed KPZ surface
STEPS_EW     = 240       # SK_EW: λ=0 Edwards–Wilkinson at t = 12.0
STEPS_STRONG = 240       # SK_Strong: λ=2.0, pronounced grooves at t = 12.0
SEED         = 137
COL_LO       = (0.030, 0.200, 0.780, 1.0)  # cobalt  (valleys)
COL_HI       = (0.980, 0.620, 0.050, 1.0)  # amber   (ridges)
ATTR_NAME    = "KPZ_Height"
OBJ_NAME     = "kpz_growth_floor"
BLEND_NAME   = "kpz_growth_floor.blend"
GLB_NAME     = "kpz_growth_floor.glb"
OUTPUT_DIR   = pathlib.Path(bpy.path.abspath("//"))


# ── Spectral helpers ─────────────────────────────────────────────────────────
def _wavenumbers(n: int, world: float):
    """
    Return kx, ky wavenumber arrays for rfft2 output (n, n//2+1).
    Physical units: kx[i] = 2π·i_freq / L where L = 2*world.
    WHY physical units: ν∇²h in Fourier = −ν|k|² ĥ with PHYSICAL |k|.
    If we used integer cycles/grid the factor L would cancel into ν, but
    being explicit avoids confusion when comparing to textbook formulae.
    """
    L   = 2.0 * world           # domain side length (8 m)
    dx  = L / n                 # grid spacing
    # fftfreq returns cycles per sample; multiply by 2π/dx to get rad/m
    kx = (2.0 * np.pi / L) * np.fft.fftfreq(n, d=1.0/n)[:, None]  # (n,1)
    ky = (2.0 * np.pi / L) * np.fft.rfftfreq(n, d=1.0/n)[None, :]  # (1,n//2+1)
    k2 = kx**2 + ky**2          # (n, n//2+1)
    return kx, ky, k2, dx


def _denom(k2, nu: float, dt: float):
    """
    Semi-implicit denominator D(k) = 1 + ν|k|²·dt.
    Treating ν∇²h implicitly: ĥ_new = (ĥ_old + dt·RHS) / D(k).
    WHY: explicit Euler requires dt < 1/(ν·k_max²) ≈ 1e-4 — unusable.
    Semi-implicit is unconditionally stable for the linear part at any dt.
    """
    return 1.0 + nu * k2 * dt


def _noise_std(noise_d: float, dx: float, dt: float) -> float:
    """
    Per-grid-point noise standard deviation for one Euler–Maruyama step.
    Continuous: ⟨η(x)η(x)⟩ = 2D → discretised per cell area dx² and
    per time step dt → σ = sqrt(2D / (dx² · dt)).
    The factor dx² (not 1/dx²) appears because we accumulate η into ∂h/∂t·dt.
    """
    return float(np.sqrt(2.0 * noise_d / (dx**2 * dt)))


# ── KPZ simulation ───────────────────────────────────────────────────────────
def _simulate(n: int, lam: float, nu: float, d_noise: float,
              dt: float, steps: int, world: float,
              rng: np.random.Generator) -> np.ndarray:
    """
    Integrate the KPZ equation on an N×N periodic 2D domain.
    Returns h[i, j] (float64), mean-zeroed, normalised to [-1, +1].
    """
    kx, ky, k2, dx = _wavenumbers(n, world)
    denom  = _denom(k2, nu, dt)
    sig    = _noise_std(d_noise, dx, dt)

    # Initialise: flat surface + tiny seed perturbation (breaks symmetry)
    h = 0.01 * rng.standard_normal((n, n)).astype(np.float64)

    for _ in range(steps):
        # Spectral gradient: ∂h/∂x = irfft2(i·kx·rfft2(h)), likewise y
        h_hat   = np.fft.rfft2(h)
        dhx     = np.fft.irfft2(1j * kx * h_hat, s=(n, n))
        dhy     = np.fft.irfft2(1j * ky * h_hat, s=(n, n))

        # KPZ nonlinear term: (λ/2)|∇h|²
        nl      = (lam * 0.5) * (dhx**2 + dhy**2)

        # White noise increment: σ · N(0,1) per grid point
        noise   = sig * rng.standard_normal((n, n))

        # Semi-implicit update
        rhs_hat = np.fft.rfft2(nl + noise)
        h_hat   = (h_hat + dt * rhs_hat) / denom
        h       = np.fft.irfft2(h_hat, s=(n, n))

        # Remove mean: prevents unbounded drift from |∇h|² source term
        h -= h.mean()

    # Normalise to [-1, +1] for consistent HEIGHT_SCALE across shape keys
    mx = np.abs(h).max()
    if mx > 1e-12:
        h /= mx
    return h


# ── Mesh construction ────────────────────────────────────────────────────────
def _build_grid(n: int, world: float) -> tuple:
    """
    Build an N×N quad grid in bmesh; return (bm, verts_2d).
    Vertices laid out with +Y up convention for Holoflow GLB export.
    """
    bm      = bmesh.new()
    coords  = np.linspace(-world, world, n)
    verts   = [[bm.verts.new((float(x), float(y), 0.0))
                for y in coords] for x in coords]
    for i in range(n - 1):
        for j in range(n - 1):
            bm.faces.new((verts[i][j], verts[i+1][j],
                           verts[i+1][j+1], verts[i][j+1]))
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    return bm, verts


def _apply_height(verts_2d, h: np.ndarray, height_scale: float):
    """Set z coordinates of a flat grid from a 2D height array."""
    n = len(verts_2d)
    for i in range(n):
        for j in range(n):
            verts_2d[i][j].co.z = float(h[i, j]) * height_scale


def _add_shape_key(obj, name: str, h: np.ndarray, n: int, height_scale: float):
    """
    Add a shape key to obj from h[i, j].
    WHY direct shape_key.data assignment: bpy.ops requires context; direct
    data API is reliable in headless/scripted sessions.
    """
    sk = obj.shape_key_add(name=name, from_mix=False)
    for vi, skv in enumerate(sk.data):
        i, j    = divmod(vi, n)
        skv.co.z = float(h[i, j]) * height_scale


def _colour_attr(obj, h: np.ndarray, n: int,
                  col_lo: tuple, col_hi: tuple, attr_name: str):
    """
    Write per-vertex FLOAT_COLOR (linear sRGB) from h ∈ [-1, +1].
    Cobalt at valleys (h ≈ −1), amber at ridges (h ≈ +1).
    Intermediate values lerp linearly between the two poles.
    """
    attr  = obj.data.color_attributes.new(
        name=attr_name, type='FLOAT_COLOR', domain='POINT')
    flat  = h.ravel(order='C')  # row-major = vertex index order
    for vi, val in enumerate(flat):
        t = float(val) * 0.5 + 0.5   # [−1,+1] → [0,1]
        col = tuple(col_lo[c] + t * (col_hi[c] - col_lo[c]) for c in range(4))
        attr.data[vi].color = col


# ── GLB export ───────────────────────────────────────────────────────────────
def _export_glb(obj, out_dir: pathlib.Path, glb_name: str):
    """
    Export obj to GLB with Holoflow studio conventions:
    +Y up (gltflib standard), Draco 6, WebP textures, morph targets, colours.
    """
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.gltf(
        filepath        = str(out_dir / glb_name),
        use_selection   = True,
        export_draco_mesh_compression_enable   = True,
        export_draco_mesh_compression_level    = 6,
        export_image_format                    = 'WEBP',
        export_morph    = True,
        export_colors   = True,
        export_yup      = True,
    )


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    rng = np.random.default_rng(SEED)

    # ── Four simulation runs ─────────────────────────────────────────────────
    # Each run re-seeds identically so we compare physics, not random draws.
    h_basis  = _simulate(N, LAM_BASIS,  NU, NOISE_D, DT, STEPS_BASIS,  WORLD_SCALE, np.random.default_rng(SEED))
    h_long   = _simulate(N, LAM_BASIS,  NU, NOISE_D, DT, STEPS_LONG,   WORLD_SCALE, np.random.default_rng(SEED))
    h_ew     = _simulate(N, 0.0,        NU, NOISE_D, DT, STEPS_EW,     WORLD_SCALE, np.random.default_rng(SEED))
    h_strong = _simulate(N, LAM_STRONG, NU, NOISE_D, DT, STEPS_STRONG, WORLD_SCALE, np.random.default_rng(SEED))

    # Width ratio (diagnostic): KPZ should be rougher than EW
    w_kpz = float(np.std(h_long))
    w_ew  = float(np.std(h_ew))
    print(f"KPZ width: {w_kpz:.4f} (normalised)  EW width: {w_ew:.4f}")

    # ── Build mesh ───────────────────────────────────────────────────────────
    bpy.ops.object.select_all(action='DESELECT')
    # Remove any prior object of the same name
    for o in list(bpy.data.objects):
        if o.name.startswith(OBJ_NAME):
            bpy.data.objects.remove(o, do_unlink=True)

    bm, verts_2d = _build_grid(N, WORLD_SCALE)
    _apply_height(verts_2d, h_basis, HEIGHT_SCALE)   # Basis z-position

    mesh = bpy.data.meshes.new(OBJ_NAME)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    obj = bpy.data.objects.new(OBJ_NAME, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # ── Shape keys ───────────────────────────────────────────────────────────
    obj.shape_key_add(name="Basis", from_mix=False)    # already set above
    _add_shape_key(obj, "SK_Long",   h_long,   N, HEIGHT_SCALE)
    _add_shape_key(obj, "SK_EW",     h_ew,     N, HEIGHT_SCALE)
    _add_shape_key(obj, "SK_Strong", h_strong, N, HEIGHT_SCALE)

    # ── Vertex colours (from Basis height field) ─────────────────────────────
    _colour_attr(obj, h_basis, N, COL_LO, COL_HI, ATTR_NAME)

    # ── Apply transforms before export ───────────────────────────────────────
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # ── Save .blend ──────────────────────────────────────────────────────────
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_DIR / BLEND_NAME))

    # ── Export GLB ───────────────────────────────────────────────────────────
    _export_glb(obj, OUTPUT_DIR, GLB_NAME)

    n_verts = len(obj.data.vertices)
    n_quads = len(obj.data.polygons)
    print(f"Done. {n_verts}V {n_quads}Q → {BLEND_NAME}  {GLB_NAME}")
    print(f"Shape keys: Basis (t={STEPS_BASIS*DT:.1f}s)  "
          f"SK_Long (t={STEPS_LONG*DT:.1f}s)  "
          f"SK_EW (λ=0 t={STEPS_EW*DT:.1f}s)  "
          f"SK_Strong (λ={LAM_STRONG} t={STEPS_STRONG*DT:.1f}s)")


main()
