"""
2-D Navier-Stokes Turbulence — Vorticity-Streamfunction Pseudospectral
Kraichnan-Batchelor-Leith (1967) Inverse Energy Cascade — Blender 5.1

Physics summary
---------------
Vorticity transport (2D incompressible fluid):
    ∂ω/∂t + u·∇ω = ν∇²ω + f

Poisson (stream function, satisfies ∇·u = 0 automatically):
    ∇²ψ = -ω   →   ψ̂_k = -ω̂_k / k²   (k = 0 mode pinned to zero)

Velocity recovered from ψ:
    u = +∂ψ/∂y   →   û_k = +ik_y ψ̂_k = -ik_y ω̂_k / k²
    v = -∂ψ/∂x   →   v̂_k = -ik_x ψ̂_k = +ik_x ω̂_k / k²

Nonlinear term (pseudo-spectral, Orszag 2/3-rule dealiased):
    J(ψ,ω) = u(∂ω/∂x) + v(∂ω/∂y)  computed in physical space

Two inviscid conserved quantities unique to 2D:
    E = ½ ∫|u|² dA   kinetic energy — cascades UPSCALE to large eddies
    Z = ½ ∫ ω²  dA   enstrophy      — cascades DOWNSCALE to small scales

Kraichnan-Batchelor-Leith (1967) spectral predictions:
    E(k) ~ k^{-5/3}   k < k_f   inverse energy cascade (energy flows up)
    E(k) ~ k^{-3}     k > k_f   direct enstrophy cascade (enstrophy flows down)
    These exponents are both different from the 3D Kolmogorov k^{-5/3} cascade
    because enstrophy conservation, absent in 3D, constrains the spectral flux.
"""

import bpy
import numpy as np

# ── parameters ───────────────────────────────────────────────────────────────

N          = 128           # grid points per side; N² = 16 384 vertices
L          = 2.0 * np.pi   # periodic box side length (wavenumbers are integers)
NU         = 8e-4          # kinematic viscosity; small keeps Re = U·L/ν ≫ 1
DT         = 0.004         # time step; CFL ≈ U·DT/Δx < 0.3 for typical U ~ 1

K_FORCE    = 6             # injection wavenumber ring centroid
AMP_FORCE  = 0.7           # stochastic forcing amplitude per RK4 call

N_BURN     = 300           # burn-in steps discarded before Basis snapshot
N_SHORT    = 500           # Basis → SK_Cascade (inverse cascade beginning)
N_MEDIUM   = 800           # SK_Cascade → SK_Condensed (coherent dipoles form)
N_LONG     = 1000          # SK_Condensed → SK_Forced (saturated / condensed)

WORLD_SCALE = 4.0           # mesh half-width in Blender metres
Z_SCALE     = 0.38          # vorticity field normalised to this height range (m)

COBALT = (0.027, 0.159, 0.557, 1.0)   # negative ω  (cyclonic)
AMBER  = (0.980, 0.620, 0.050, 1.0)   # positive ω  (anticyclonic)

BLEND_OUT = "ns2d_turbulence_floor.blend"
GLB_OUT   = "ns2d_turbulence_floor.glb"

# ── spectral setup ────────────────────────────────────────────────────────────

def _setup(N, L):
    """Precompute wavenumber arrays and static masks for rfft2 layout."""
    # rfft2 shape: (N, N//2+1); kx runs all N integers, ky only the positive half
    kx = np.fft.fftfreq(N, d=L / (2.0 * np.pi * N))
    ky = np.fft.rfftfreq(N, d=L / (2.0 * np.pi * N))
    KX = kx[:, None]
    KY = ky[None, :]
    K2 = KX**2 + KY**2

    # Orszag 2/3-rule: discard modes |k| > N/3 to prevent aliasing of u·∇ω.
    # Without this, the quadratic product generates modes up to 4N/3 which fold
    # back as low-wavenumber errors and blow up the simulation within ~100 steps.
    kmax  = N // 3
    dm    = (np.abs(KX) < kmax) & (np.abs(KY) < kmax)

    k_mag = np.sqrt(K2)
    fm    = (k_mag >= K_FORCE - 0.5) & (k_mag <= K_FORCE + 0.5)
    return KX, KY, K2, dm, fm


# ── right-hand side ───────────────────────────────────────────────────────────

def _rhs(wh, KX, KY, K2, dm, fm, amp, rng):
    """
    ∂ω̂/∂t = −Ĵ(ψ,ω) − ν k² ω̂ + f̂

    The dealiasing mask dm is applied to every spectral field BEFORE irfft2
    so that the nonlinear product in physical space stays within the resolved
    wavenumber range. Applied again after fft2(J) to clean up rounding aliases.
    """
    with np.errstate(divide="ignore", invalid="ignore"):
        ph = np.where(K2 > 0, -wh / K2, 0.0)   # Poisson solve: ψ̂ = -ω̂/k²

    # velocity and vorticity-gradient spectra, dealiased before physical-space step
    u_h  = ( 1j * KY * ph) * dm
    v_h  = (-1j * KX * ph) * dm
    wx_h = ( 1j * KX * wh) * dm
    wy_h = ( 1j * KY * wh) * dm

    u  = np.fft.irfft2(u_h,  s=(N, N))
    v  = np.fft.irfft2(v_h,  s=(N, N))
    wx = np.fft.irfft2(wx_h, s=(N, N))
    wy = np.fft.irfft2(wy_h, s=(N, N))

    # Jacobian in physical space → spectral → dealias
    jh = np.fft.rfft2(u * wx + v * wy) * dm

    # delta-correlated stochastic forcing: random phase on the forcing ring,
    # amplitude normalised by band area so energy injection is resolution-independent
    phi = rng.uniform(0.0, 2.0 * np.pi, fm.shape)
    fh  = amp * fm * np.exp(1j * phi) / max(float(fm.sum()), 1.0)

    return -jh - NU * K2 * wh + fh


def _rk4(wh, KX, KY, K2, dm, fm, rng):
    """Classical 4th-order Runge-Kutta step for the spectral vorticity."""
    k1 = _rhs(wh,              KX, KY, K2, dm, fm, AMP_FORCE, rng)
    k2 = _rhs(wh + 0.5*DT*k1, KX, KY, K2, dm, fm, AMP_FORCE, rng)
    k3 = _rhs(wh + 0.5*DT*k2, KX, KY, K2, dm, fm, AMP_FORCE, rng)
    k4 = _rhs(wh +     DT*k3, KX, KY, K2, dm, fm, AMP_FORCE, rng)
    return wh + (DT / 6.0) * (k1 + 2.0*k2 + 2.0*k3 + k4)


def integrate(n_steps, wh, KX, KY, K2, dm, fm, seed):
    """Advance vorticity field n_steps; return (physical ω, updated ω̂)."""
    rng = np.random.default_rng(seed)
    for _ in range(n_steps):
        wh = _rk4(wh, KX, KY, K2, dm, fm, rng)
    return np.fft.irfft2(wh, s=(N, N)), wh


# ── mesh helpers ──────────────────────────────────────────────────────────────

def _norm(omega):
    lo, hi = omega.min(), omega.max()
    return (omega - lo) / max(hi - lo, 1e-12)


def _z_field(omega):
    return _norm(omega) * Z_SCALE


def _vertex_colors(omega):
    t = _norm(omega).ravel()
    rgba = np.zeros((len(t), 4))
    for c in range(4):
        rgba[:, c] = COBALT[c] + t * (AMBER[c] - COBALT[c])
    return rgba.ravel().tolist()


def build_mesh(omega):
    """Construct N×N height-field quad mesh from vorticity snapshot."""
    xs = np.linspace(-WORLD_SCALE, WORLD_SCALE, N)
    ys = np.linspace(-WORLD_SCALE, WORLD_SCALE, N)
    xx, yy = np.meshgrid(xs, ys, indexing="ij")
    zz = _z_field(omega)

    verts = np.column_stack([xx.ravel(), yy.ravel(), zz.ravel()]).tolist()
    # CCW quad: corner order matters for consistent face normals (all pointing +Z)
    faces = [
        (ix*N+iy, ix*N+iy+N, ix*N+iy+N+1, ix*N+iy+1)
        for ix in range(N-1) for iy in range(N-1)
    ]
    mesh = bpy.data.meshes.new("NS2D_Turb")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new("NS2D_Turb", mesh)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    obj["holoflow:category"] = "stage-floor"
    obj["holoflow:facet"]    = True      # flat-shaded — preserves faceted cel look

    # −90° about X → +Y up for Holoflow WebXR exporter (+Y-up convention)
    obj.rotation_euler[0] = -np.pi / 2
    bpy.ops.object.transform_apply(rotation=True)
    return obj


def set_color_attr(obj, omega):
    mesh = obj.data
    if "NS2D_Vort" not in mesh.attributes:
        mesh.attributes.new("NS2D_Vort", type="FLOAT_COLOR", domain="POINT")
    mesh.attributes["NS2D_Vort"].data.foreach_set("color", _vertex_colors(omega))


def add_shape_key(obj, omega, name):
    """Append a shape key that carries the Z-height of a vorticity snapshot."""
    sk  = obj.shape_key_add(name=name, from_mix=False)
    zz  = _z_field(omega).ravel()
    cos = [0.0] * (3 * len(obj.data.vertices))
    for i, v in enumerate(obj.data.vertices):
        cos[3*i]   = v.co.x
        cos[3*i+1] = v.co.y
        cos[3*i+2] = float(zz[i])
    sk.data.foreach_set("co", cos)


def add_shader(obj):
    """Attribute shader: NS2D_Vort FLOAT_COLOR → base colour + emission."""
    mat = bpy.data.materials.new("NS2D_Turb_Mat")
    mat.use_nodes = True
    nt  = mat.node_tree
    nt.nodes.clear()

    out  = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    att  = nt.nodes.new("ShaderNodeAttribute")
    att.attribute_name = "NS2D_Vort"

    nt.links.new(att.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(att.outputs["Color"], bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = 1.6
    bsdf.inputs["Roughness"].default_value = 0.65
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    out.location  = (400, 0)
    bsdf.location = (100, 0)
    att.location  = (-250, 0)
    obj.data.materials.append(mat)


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    KX, KY, K2, dm, fm = _setup(N, L)

    # initialise vorticity: low-amplitude energy on the forcing ring
    rng0 = np.random.default_rng(7)
    ph0  = rng0.uniform(0.0, 2.0 * np.pi, fm.shape)
    wh   = 0.1 * fm * np.exp(1j * ph0)

    # burn-in: let the forward enstrophy cascade fill small scales
    omega_b, wh = integrate(N_BURN,   wh, KX, KY, K2, dm, fm, seed=10)

    obj = build_mesh(omega_b)
    set_color_attr(obj, omega_b)
    obj.shape_key_add(name="Basis", from_mix=False)
    add_shader(obj)

    omega_cas, wh = integrate(N_SHORT,  wh, KX, KY, K2, dm, fm, seed=20)
    add_shape_key(obj, omega_cas, "SK_Cascade")

    omega_con, wh = integrate(N_MEDIUM, wh, KX, KY, K2, dm, fm, seed=30)
    add_shape_key(obj, omega_con, "SK_Condensed")

    omega_frc, wh = integrate(N_LONG,   wh, KX, KY, K2, dm, fm, seed=40)
    add_shape_key(obj, omega_frc, "SK_Forced")

    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)

    bpy.ops.export_scene.gltf(
        filepath        = GLB_OUT,
        export_format   = "GLB",
        export_draco_mesh_compression_enable = True,
        export_draco_mesh_compression_level  = 6,
        export_image_format = "WEBP",
        export_morph    = True,
        export_colors   = True,
    )
    print(f"NS2D: {N*N} vertices  {(N-1)*(N-1)} quads  4 shape keys.")


main()
