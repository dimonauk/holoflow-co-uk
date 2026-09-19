# ============================================================
# NLSE  |  Nonlinear Schrödinger Equation  |  Blender 5.1
# ============================================================
# Focusing NLSE: i∂ψ/∂t + ∂²ψ/∂x² + 2|ψ|²ψ = 0
# Background plane-wave ψ₀ = e^{2it} is unstable to perturbations
# with wavenumber q < 2 (Benjamin–Feir modulational instability).
# Four shape keys sweep from clean soliton collision (Basis) through
# the MI Akhmediev breather (SK_Akhmediev), a KM-type localised
# breathing mode (SK_KM), and the Peregrine rogue-wave exact formula
# (SK_Peregrine).  Each is a 128×128 space-time |ψ(x,t)| height field.
# Exports nlse_soliton_floor.glb (Draco 6 / WebP) for WebXR.
# ============================================================

import bpy, math
import numpy as np

# ── Parameters ──────────────────────────────────────────────────
N        = 128           # grid side → N×N vertices, (N-1)² quads
L        = 12.0          # spatial domain [-L/2, L/2], periodic
DT       = 0.10          # time step  (total time = 12.7 units)
NT       = 127           # → 128 frames at t = 0, DT, ..., NT·DT
Z_SCALE  = 0.45          # height-field amplitude (metres)
OBJ_NAME = "nlse_floor"
COBALT   = (0.027, 0.141, 0.557, 1.0)
AMBER    = (0.980, 0.620, 0.050, 1.0)
OUT_PATH = "//nlse_soliton_floor.glb"

x  = np.linspace(-L / 2, L / 2, N, endpoint=False)
# Wavenumbers for real FFT: fftfreq returns [-0.5,0.5) normalised, × 2π/L × N
kk = (2.0 * math.pi / L) * np.fft.fftfreq(N) * N

# ── Split-step Fourier integrator ───────────────────────────────
# Strang (2nd-order) splitting for i∂ψ/∂t + ψ_xx + 2|ψ|²ψ = 0:
#   Linear part:    L̂ψ = iψ_xx   → in Fourier: ψ̂_t = −ik²ψ̂  → exact propagator exp(−ik²dt)
#   Nonlinear part: N̂ψ = 2i|ψ|²ψ → |ψ| conserved → ψ(dt) = ψ(0)·exp(2i|ψ|²dt)
#
# Strang sequence per time step:
#   1. NL half-step dt/2: ψ *= exp(i|ψ|²dt)   [WHY: 2i|ψ|² × dt/2 → phase i|ψ|²dt]
#   2. Linear full step:  ψ̂ *= exp(−ik²dt)
#   3. NL half-step dt/2: ψ *= exp(i|ψ|²dt)
# Consecutive NL halves collapse: step-3 of n + step-1 of n+1 = full NL step.
# We record |ψ| RIGHT AFTER the linear step; since NL is pure phase,
# |ψ| is identical before and after step 3.

def _split_step(psi0: np.ndarray) -> np.ndarray:
    """Evolve ψ₀ for NT steps of DT, returning |ψ(x,t)| of shape (NT+1, N)."""
    lin    = np.exp(-1j * kk ** 2 * DT)
    psi    = psi0.astype(complex)
    frames = np.empty((NT + 1, N), dtype=np.float32)
    frames[0] = np.abs(psi)
    psi *= np.exp(1j * np.abs(psi) ** 2 * DT)   # initial NL half-step
    for n in range(NT):
        psi = np.fft.ifft(np.fft.fft(psi) * lin)
        frames[n + 1] = np.abs(psi)
        psi *= np.exp(2j * np.abs(psi) ** 2 * DT)   # combined NL (two halves)
    return frames


def _norm(field: np.ndarray) -> np.ndarray:
    """Normalise amplitude field to [0, 1] for uniform height range."""
    lo, hi = float(field.min()), float(field.max())
    return (field - lo) / (hi - lo) if hi > lo else np.zeros_like(field)


# ── Shape-key scenarios ─────────────────────────────────────────

def _basis_field() -> np.ndarray:
    """Two η=1 solitons moving toward each other at v = ±0.5.
    Elastic collision: solitons emerge unscathed with a phase shift —
    the hallmark of NLSE integrability (Zakharov & Shabat 1972).
    ψ₀ = sech(x+3)·e^{i(v/2)x} + sech(x-3)·e^{−i(v/2)x},  v = 0.5
    """
    v    = 0.5
    psi0 = (1.0 / np.cosh(x + 3.0)) * np.exp( 1j * (v / 2) * x) \
         + (1.0 / np.cosh(x - 3.0)) * np.exp(-1j * (v / 2) * x)
    return _norm(_split_step(psi0))


def _akhmediev_field() -> np.ndarray:
    """Modulational instability → Akhmediev-like breather.
    Start from ψ₀ = 1 + ε·cos(qx) with q = 2π/L (one spatial period).
    Mode q ≈ 0.524 < 2 → MI growth rate σ = q√(4−q²)/2 ≈ 0.51;
    breather cycle T = 2π/σ ≈ 12.3 ≈ total integration time.
    The envelope grows from background, peaks, and nearly recurs
    (Fermi–Pasta–Ulam–Tsingou recurrence).
    """
    q    = 2.0 * math.pi / L   # lowest unstable mode
    psi0 = np.ones(N, dtype=complex) + 0.04 * np.cos(q * x)
    return _norm(_split_step(psi0))


def _km_field() -> np.ndarray:
    """Elevated localised initial condition → KM-type periodic breathing.
    A sech-shaped bump of amplitude 0.70 on the unit background acts as
    a bound state that periodically focuses and defocuses; the structure
    is spatially localised and periodic in time, approximating the
    Kuznetsov–Ma breather (Kuznetsov 1977, Ma 1979).
    """
    psi0 = np.ones(N, dtype=complex) + 0.70 / np.cosh(0.7 * x)
    return _norm(_split_step(psi0))


def _peregrine_field() -> np.ndarray:
    """Exact Peregrine rogue-wave solution on an independent 128×128 grid.
    ψ_P(x,t) = e^{2it} · [1 − 4(1+2it) / (1 + 4x² + 4t²)]
    At (x,t)=(0,0): |ψ_P| = 3 (three times the background amplitude).
    As x or t → ∞: |ψ_P| → 1 (returns to the plane-wave background).
    Doubly localised in both x and t: the archetype of a 'rogue wave
    from nowhere', first derived by Peregrine (1983).
    x_P ∈ [−5, 5],  t_P ∈ [−4, 4] chosen to show the full rise and fall.
    """
    X = np.linspace(-5.0, 5.0, N)          # (N,) spatial
    T = np.linspace(-4.0, 4.0, N)          # (N,) temporal
    XX, TT = np.meshgrid(X, T, indexing='ij')   # (N, N)
    psi_P  = np.exp(2j * TT) * (1.0 - 4.0 * (1.0 + 2j * TT)
                                 / (1.0 + 4.0 * XX ** 2 + 4.0 * TT ** 2))
    field  = np.abs(psi_P).astype(np.float32)
    # Transpose so rows = time (t-axis vertical), cols = space (x-axis horizontal)
    return _norm(field.T)


# ── Mesh builder ─────────────────────────────────────────────────

def _build_mesh(field: np.ndarray) -> bpy.types.Object:
    """128×128 quad grid; rows = time axis, cols = space axis."""
    step  = 2.0 / (N - 1)
    verts = []
    for i in range(N):
        for j in range(N):
            verts.append((-1.0 + j * step, -1.0 + i * step,
                          float(field[i, j]) * Z_SCALE))
    faces = []
    for i in range(N - 1):
        for j in range(N - 1):
            a = i * N + j
            faces.append((a, a + 1, a + N + 1, a + N))
    mesh = bpy.data.meshes.new(OBJ_NAME)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(OBJ_NAME, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def _add_shape_key(obj: bpy.types.Object, name: str, field: np.ndarray) -> None:
    sk  = obj.shape_key_add(name=name, from_mix=False)
    cos = np.empty(N * N * 3, dtype=np.float32)
    obj.data.vertices.foreach_get("co", cos)
    cos[2::3] = field.ravel() * Z_SCALE    # update z only; x,y unchanged
    sk.data.foreach_set("co", cos)


def _add_color(obj: bpy.types.Object, field: np.ndarray) -> None:
    mesh = obj.data
    if "NLSE_Amp" not in mesh.color_attributes:
        mesh.color_attributes.new("NLSE_Amp", "FLOAT_COLOR", "POINT")
    attr  = mesh.color_attributes["NLSE_Amp"]
    flat  = field.ravel().astype(np.float32)          # (N²,)
    c_cob = np.array(COBALT[:3], dtype=np.float32)
    c_amb = np.array(AMBER[:3],  dtype=np.float32)
    rgb   = c_cob + flat[:, np.newaxis] * (c_amb - c_cob)  # (N², 3)
    alpha = np.ones((N * N, 1), dtype=np.float32)
    attr.data.foreach_set("color", np.hstack([rgb, alpha]).ravel())


def _setup_material(obj: bpy.types.Object) -> None:
    mat = bpy.data.materials.new("nlse_mat")
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out  = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    attr = nodes.new("ShaderNodeAttribute")
    attr.attribute_name = "NLSE_Amp"
    links.new(attr.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(bsdf.outputs["BSDF"],  out.inputs["Surface"])
    bsdf.inputs["Roughness"].default_value = 0.30
    bsdf.inputs["Metallic"].default_value  = 0.20
    obj.data.materials.append(mat)


def _export_glb(obj: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.gltf(
        filepath=bpy.path.abspath(OUT_PATH),
        use_selection=True,
        export_format="GLB",
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_image_format="WEBP",
        export_apply=True,
        export_attributes=True,
        export_morph=True,
    )


# ── Main ─────────────────────────────────────────────────────────

def run() -> None:
    for ob in bpy.data.objects:
        bpy.data.objects.remove(ob, do_unlink=True)

    h_basis = _basis_field()
    obj     = _build_mesh(h_basis)
    obj.shape_key_add(name="Basis", from_mix=False)

    _add_shape_key(obj, "SK_Akhmediev", _akhmediev_field())
    _add_shape_key(obj, "SK_KM",        _km_field())
    _add_shape_key(obj, "SK_Peregrine", _peregrine_field())

    _add_color(obj, h_basis)
    _setup_material(obj)
    _export_glb(obj)
    print(f"[nlse] exported → {bpy.path.abspath(OUT_PATH)}")


run()
