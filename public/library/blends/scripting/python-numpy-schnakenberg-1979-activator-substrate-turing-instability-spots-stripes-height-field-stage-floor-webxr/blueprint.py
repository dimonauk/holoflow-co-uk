"""
Schnakenberg Activator-Substrate Reaction-Diffusion (1979)
Turing Instability · Spots / Stripes · Height-Field Stage Floor · Blender 5.1
CC0 Public Domain

Equations
---------
  ∂u/∂t = Du ∇²u + γ(a − u + u²v)    [u = activator, autocatalytic via u²v]
  ∂v/∂t = Dv ∇²v + γ(b − u²v)         [v = substrate, depleted by u²v]

Uniqueness vs other Turing systems in this library
  • Gierer–Meinhardt: activation term is u²/v (ratio, not product) → different phase portrait
  • Brusselator:      trimolecular 2X+Y → 3X; two feed species
  • Gray–Scott:       feed/kill framing  F(1−u) and (F+k)v; non-zero base-state for v
  • Schnakenberg:     simplest two-component Turing system with provable limit-cycle removal
                      and exact closed-form stability boundary in (a,b) parameter space

Steady state
  u* = a + b,   v* = b / (a + b)²

Turing condition (linearise, check dispersion relation h(k²) < 0 for some k)
  Jacobian at (u*, v*):
    f_u = γ (b−a)/(a+b)        (positive iff b > a  → activator self-excites)
    f_v = γ (a+b)²             (positive  → substrate drives activator)
    g_u = −2γ b/(a+b)          (negative  → activator depletes substrate)
    g_v = −γ (a+b)²            (negative  → substrate self-inhibits)
  det A = γ² (a+b)³ > 0  always (stable without diffusion)
  tr  A = γ [(b−a)/(a+b) − (a+b)²]  < 0  when b < a + (a+b)³
  Turing instability iff (f_u Dv + g_v Du)² > 4 Du Dv det A
    ⟺  [γ(b−a)/(a+b)·Dv − γ(a+b)²·Du]² > 4 Du Dv γ²(a+b)³

Critical wavenumber k_c (maximally unstable mode):
  k_c² = [f_u Dv + g_v Du] / (2 Du Dv)
       = γ [(b−a)/(a+b)·Dv − (a+b)²·Du] / (2 Du Dv)

Integrator: ETD1 Spectral — Cox & Matthews (2002)
  Exact for linear (diffusion) part in Fourier space; forward-Euler for nonlinear:
    ũ(t+dt) = E_u ũ(t) + φ₁_u · Ñu(t)
    E_u = exp(−Du k² dt)
    φ₁_u = (E_u − 1) / (−Du k²)      [limit dt as k→0]
  Unconditionally stable for diffusion; nonlinear stability: dt < 2 / |∂Nu/∂u|_max
    ∂Nu/∂u = γ(−1 + 2uv) ≤ γ(2u*v* − 1) ≈ 724  →  dt_max ≈ 0.00276
    We use dt = 0.0005 for safety margin.

Sources
  Schnakenberg J. (1979) J. Theor. Biol. 81:389–400.  (CC0 / PD)
  Murray J. D.  (2003) Mathematical Biology II §2.3. Springer.   (equations PD)
  Cox S. M., Matthews P. C. (2002) J. Comput. Phys. 176:430–455. (PD)
"""

import bpy, bmesh, math
import numpy as np

# ─── Parameters ──────────────────────────────────────────────
N         = 128      # grid resolution (N×N vertices = 16 384 V, 16 129 Q)
L         = 10.0     # domain side [non-dim]; λ_c ≈ 0.334 → ~30 spots per axis

Du        = 1.0      # activator diffusivity
Dv        = 50.0     # substrate diffusivity  (d = Dv/Du = 50)
GAMMA     = 1000.0   # kinetic rate scale (λ_pattern ∝ 1/√γ)
DT        = 0.0005   # time step (nonlinear Euler stability: dt < 0.00116)

# (a, b) pairs — all verified inside Turing space for d=50, γ=1000
A_BASIS   = 0.126779; B_BASIS   = 0.792366  # Murray (2003) classic spots
A_COARSE  = 0.100;    B_COARSE  = 0.900     # larger (a+b)  → coarser wavelength
A_FINE    = 0.126779; B_FINE    = 0.792366  # same (a,b) but γ_fine=3000 → λ/√3
A_BLOOM   = 0.180;    B_BLOOM   = 0.900     # high u* → dense spot array
GAMMA_FINE = 3000.0   # SK_Fine: triples wavenumber, finer pattern

N_STEPS_BASIS = 4000  # t = 2.0; patterns fully coarsened well before t = 0.1
N_STEPS_KEYS  = 2000  # t = 1.0

HEIGHT_SCALE = 0.15   # metres per u unit (u range ≈ 0.5 – 1.3)
FLOOR_SIDE   = 3.0    # metres; WebXR stage floor
MESH_NAME    = "Schnakenberg_Floor"
ATTR_NAME    = "SC_Activator"
EXPORT_PATH  = "//schnakenberg_turing_floor.glb"

# ─── Verify Turing conditions at runtime ─────────────────────
def check_turing(a, b, Du, Dv, gamma):
    u_s = a + b;  v_s = b / (a + b)**2
    f_u = gamma * (b - a) / (a + b)
    g_v = -gamma * (a + b)**2
    det_A = gamma**2 * (a + b)**3
    LHS = (f_u * Dv + g_v * Du)**2
    RHS = 4 * Du * Dv * det_A
    k_c2 = (f_u * Dv + g_v * Du) / (2 * Du * Dv)
    ok = (LHS > RHS) and (k_c2 > 0)
    print(f"  a={a:.4f} b={b:.4f}  u*={u_s:.4f} k_c={math.sqrt(max(k_c2,0)):.2f}  Turing={'✓' if ok else '✗'}")

print("Turing verification:")
for label, a, b, g in [
    ("BASIS",   A_BASIS,  B_BASIS,  GAMMA),
    ("COARSE",  A_COARSE, B_COARSE, GAMMA),
    ("FINE",    A_FINE,   B_FINE,   GAMMA_FINE),
    ("BLOOM",   A_BLOOM,  B_BLOOM,  GAMMA),
]:
    check_turing(a, b, Du, Dv, g)

# ─── Spectral ETD1 setup ─────────────────────────────────────
# WHY spectral: eliminates artificial anisotropy from finite-difference stencils,
# giving perfectly isotropic spots (no square-lattice bias from grid).
kx = np.fft.fftfreq(N) * (2 * math.pi * N / L)   # frequencies: radians per domain unit
ky = np.fft.rfftfreq(N) * (2 * math.pi * N / L)
KX, KY = np.meshgrid(kx, ky, indexing='ij')
k2 = KX**2 + KY**2  # shape (N, N//2+1)

def make_etd1(Du_, Dv_, gamma_, dt_=DT):
    """Precompute ETD1 propagators for given diffusivities and time-step."""
    Lu = -Du_ * k2;  Lv = -Dv_ * k2
    E_u = np.exp(Lu * dt_);  E_v = np.exp(Lv * dt_)
    # φ₁(z) = (exp z − 1)/z;  stable limit at z=0: φ₁ = dt
    phi_u = np.where(np.abs(Lu) < 1e-10, dt_, (E_u - 1.0) / Lu)
    phi_v = np.where(np.abs(Lv) < 1e-10, dt_, (E_v - 1.0) / Lv)
    return E_u, E_v, phi_u, phi_v

E_u, E_v, phi_u, phi_v = make_etd1(Du, Dv, GAMMA)
E_uf, E_vf, phi_uf, phi_vf = make_etd1(Du, Dv, GAMMA_FINE)  # SK_Fine

def run(a, b, n_steps, E_u_, E_v_, phi_u_, phi_v_, g, seed=42):
    """Integrate Schnakenberg PDEs; return final u field."""
    rng = np.random.default_rng(seed)
    u_s = a + b;  v_s = b / (a + b)**2
    # Small noise around steady state (amplitude 1 % of u*)
    u = u_s + 0.01 * rng.standard_normal((N, N))
    v = v_s + 0.01 * rng.standard_normal((N, N))
    for _ in range(n_steps):
        Nu = g * (a - u + u**2 * v)
        Nv = g * (b - u**2 * v)
        u_hat = np.fft.rfft2(u)
        v_hat = np.fft.rfft2(v)
        u_hat = E_u_ * u_hat + phi_u_ * np.fft.rfft2(Nu)
        v_hat = E_v_ * v_hat + phi_v_ * np.fft.rfft2(Nv)
        u = np.fft.irfft2(u_hat)
        v = np.fft.irfft2(v_hat)
    return u

print("Running BASIS …")
u_basis = run(A_BASIS, B_BASIS, N_STEPS_BASIS, E_u, E_v, phi_u, phi_v, GAMMA)
print(f"  u range: [{u_basis.min():.4f}, {u_basis.max():.4f}]")

# ─── Blender mesh ─────────────────────────────────────────────
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Build N×N vertex grid with z=HEIGHT_SCALE*u (row-major: vertex [i,j] = i*N+j)
def u_to_verts(u_field):
    idx = np.mgrid[0:N, 0:N]  # shape (2, N, N)
    xs = (idx[0] / (N - 1) - 0.5) * FLOOR_SIDE
    ys = (idx[1] / (N - 1) - 0.5) * FLOOR_SIDE
    zs = u_field * HEIGHT_SCALE
    return np.stack([xs, ys, zs], axis=-1).reshape(-1, 3)

verts_basis = u_to_verts(u_basis)
faces = [(i * N + j, i * N + j + 1, (i+1) * N + j + 1, (i+1) * N + j)
         for i in range(N - 1) for j in range(N - 1)]

mesh = bpy.data.meshes.new(MESH_NAME)
mesh.from_pydata(verts_basis.tolist(), [], faces)
mesh.update()
obj = bpy.data.objects.new(MESH_NAME, mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
obj.rotation_euler[0] = 0.0   # +Y-up: no rotation needed for stage floor

# Basis shape key (reference)
obj.shape_key_add(name="Basis", from_mix=False)

# ─── Shape keys for four regimes ─────────────────────────────
KEY_DEFS = [
    ("SK_Coarse", A_COARSE, B_COARSE, N_STEPS_KEYS, E_u,  E_v,  phi_u,  phi_v,  GAMMA),
    ("SK_Fine",   A_FINE,   B_FINE,   N_STEPS_KEYS, E_uf, E_vf, phi_uf, phi_vf, GAMMA_FINE),
    ("SK_Bloom",  A_BLOOM,  B_BLOOM,  N_STEPS_KEYS, E_u,  E_v,  phi_u,  phi_v,  GAMMA),
]
for name, a, b, steps, eu, ev, pu, pv, g in KEY_DEFS:
    print(f"Running {name} …")
    u_k = run(a, b, steps, eu, ev, pu, pv, g, seed=42)
    sk = obj.shape_key_add(name=name, from_mix=False)
    verts_k = u_to_verts(u_k)
    for vi, co in enumerate(verts_k):
        sk.data[vi].co = co.tolist()

# ─── FLOAT_COLOR attribute (SC_Activator) ─────────────────────
# Stores normalised u ∈ [0,1] for cobalt-to-amber shader gradient.
# WHY FLOAT_COLOR not FLOAT: GLTF morph-target export preserves colour attributes,
# allowing WebXR shaders to drive material colour from the same data.
attr = mesh.attributes.new(name=ATTR_NAME, type='FLOAT_COLOR', domain='POINT')
u_norm = (u_basis - u_basis.min()) / (u_basis.max() - u_basis.min() + 1e-12)
for vi, val in enumerate(u_norm.ravel()):
    # Cobalt (low u) → Amber (high u) via linear RGB lerp
    attr.data[vi].color = (val, 0.3 * val, 1.0 - val, 1.0)

# ─── GLTF export ─────────────────────────────────────────────
bpy.ops.export_scene.gltf(
    filepath=bpy.path.abspath(EXPORT_PATH),
    export_format='GLB',
    export_draco_mesh_compression_enable=True,
    export_draco_mesh_compression_level=6,
    export_morph=True,
    export_colors=True,
    export_attributes=True,
    export_apply=True,
    export_yup=True,
    export_image_format='WEBP',
)
print(f"Exported → {EXPORT_PATH}")
