"""
Fisher-KPP Reaction-Diffusion Wavefront (Fisher 1937 / KPP 1937)
Pulled Wave · Bistable Allee Effect · Height-Field Stage Floor · Blender 5.1
CC0 Public Domain

Equation (monostable / KPP):
  ∂u/∂t = D ∇²u  +  r·u(1−u)

Equation (bistable / Allee):
  ∂u/∂t = D ∇²u  +  r·u(1−u)(u−θ)     θ ∈ (0, 0.5)

Fisher (1937 Ann. Eugen.) modelled advantageous gene spread.
Kolmogorov, Petrovsky & Piskunov (1937 Bull. Univ. Mosc.) proved
the minimum wavespeed  c* = 2√(D·r)  for KPP-type initial data.
The wave is "pulled": the front runs at the linearised speed because
the tip region u≈0 grows like e^{r·t} and outruns the bulk.
Bistable (Allee) case: f′(0)=−r·θ<0, so u=0 is stable; the wave
only propagates if the initial nucleus exceeds θ ("pushed" regime).

ETD1 split (Cox–Matthews 2002):
  Linear   L̂_k = −D k² + r        (absorbs linearised growth r·u)
  Nonlinear N(u) = −r u²           (KPP)
            N(u) = −r u²(1+θ−u)    (bistable, split at f′(0)=−r·θ·u shifted)
  û(t+dt) = exp(L̂ dt)·û  +  φ₁(L̂ dt)·N̂(t)·dt
  φ₁(z)   = (exp z − 1)/z          (Taylor-safe, → 1 as z → 0)

Blender mesh: N×N grid  →  16384 verts  16129 quads
Attribute: Fisher_U  FLOAT_COLOR POINT  cobalt(u=0) → amber(u=1)
WebXR export: Draco-6 / WebP / export_morph / export_colors / +Y-up

Shape keys
----------
  Basis     : D=0.5  r=1.0  t=30    c*≈1.414 px/tu  ring radius ≈42 px
  SK_FastR  : D=0.5  r=2.0  t=20    c*≈2.000 px/tu  ring radius ≈40 px
  SK_LowD   : D=0.1  r=1.0  t=60    c*≈0.632 px/tu  ring radius ≈38 px
  SK_Bistable: D=0.5 r=1.0  θ=0.30  t=60  pushed wave from IC peak=0.8
"""

import bpy, bmesh, numpy as np
from numpy.fft import rfft2, irfft2, fftfreq, rfftfreq

# ── Parameters ───────────────────────────────────────────────────────────────
N           = 128          # grid resolution (N×N = 16384 vertices)
DX          = 1.0          # grid spacing in "pixel" units
ZSCALE      = 0.45         # height extrusion (Blender metres)
WORLD_SCALE = 4.0          # floor span (metres)
OBJ_NAME    = "Fisher_KPP_Floor"
ATTR_NAME   = "Fisher_U"

COL_LO = (0.027, 0.141, 0.557, 1.0)   # cobalt  — u ≈ 0
COL_HI = (0.960, 0.620, 0.020, 1.0)   # amber   — u ≈ 1

# Precompute Fourier wavenumbers (shared across all runs)
kx = (2.0 * np.pi / DX) * fftfreq(N, d=1.0)          # shape (N,)
ky = (2.0 * np.pi / DX) * rfftfreq(N, d=1.0)          # shape (N//2+1,)
KX, KY = np.meshgrid(kx, ky, indexing="ij")
K2 = KX ** 2 + KY ** 2                                 # shape (N, N//2+1)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _initial_condition(cx=0.5, cy=0.5, spread=200.0, amp=0.8):
    """Gaussian nucleus centred at (cx,cy) in normalised [0,1]² coords."""
    x = np.linspace(0.0, 1.0, N, endpoint=False)
    X, Y = np.meshgrid(x, x, indexing="ij")
    return amp * np.exp(-spread * ((X - cx) ** 2 + (Y - cy) ** 2))


def _make_etd1(D, r, dt):
    """Return (exp_L, phi1) for the monostable KPP linear operator L̂_k = -D·k² + r.

    WHY split at r: absorbing the linearised growth into L makes N = -r·u²
    purely quadratic, so the nonlinear CFL is trivially dt·r ≪ 1.
    """
    L = -D * K2 + r                    # L̂_k at every (kx,ky)
    Ldt = L * dt
    exp_L = np.exp(Ldt)
    # φ₁(z) = (e^z − 1)/z; Taylor-expand near z=0 for numerical safety
    phi1 = np.where(np.abs(Ldt) > 1e-10, np.expm1(Ldt) / Ldt, 1.0 + Ldt / 2.0)
    return exp_L, phi1


def _make_etd1_bistable(D, r, theta, dt):
    """ETD1 split for bistable: L̂_k = −D·k² − r·θ  (f′(0) = −r·θ < 0).

    N(u) = r·u²·(1 + θ − u)  (obtained by subtracting f′(0)·u from f(u)).
    WHY: keeps L̂ negative at large k (stable diffusion) while correctly
    capturing the Allee saddle at u = θ in the nonlinear part.
    """
    L = -D * K2 - r * theta
    Ldt = L * dt
    exp_L = np.exp(Ldt)
    phi1 = np.where(np.abs(Ldt) > 1e-10, np.expm1(Ldt) / Ldt, 1.0 + Ldt / 2.0)
    return exp_L, phi1


def _run_kpp(D, r, dt, n_steps):
    """Integrate monostable KPP to t = n_steps · dt."""
    u = _initial_condition()
    exp_L, phi1 = _make_etd1(D, r, dt)
    u_hat = rfft2(u)
    for _ in range(n_steps):
        N_u = -r * u * u                            # nonlinear term N(u) = −r·u²
        u_hat = exp_L * u_hat + phi1 * rfft2(N_u) * dt
        u = np.clip(irfft2(u_hat, s=(N, N)), 0.0, 1.0)
    return u


def _run_bistable(D, r, theta, dt, n_steps):
    """Integrate bistable (Allee) FKPP: f(u)=r·u(1−u)(u−θ)."""
    u = _initial_condition(amp=0.80)               # IC peak must exceed θ to propagate
    exp_L, phi1 = _make_etd1_bistable(D, r, theta, dt)
    u_hat = rfft2(u)
    for _ in range(n_steps):
        N_u = r * u * u * (1.0 + theta - u)       # N(u) after bistable ETD1 split
        u_hat = exp_L * u_hat + phi1 * rfft2(N_u) * dt
        u = np.clip(irfft2(u_hat, s=(N, N)), 0.0, 1.0)
    return u


# ── Blender construction ──────────────────────────────────────────────────────

def _build_base_mesh(u_basis):
    """Create N×N quad grid, set vertex Z to u_basis, add Fisher_U colour attribute."""
    # Remove stale object
    if OBJ_NAME in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[OBJ_NAME], do_unlink=True)

    me = bpy.data.meshes.new(OBJ_NAME)
    verts, faces, uvs = [], [], []
    cell = WORLD_SCALE / (N - 1)

    u_norm = (u_basis - u_basis.min()) / (u_basis.ptp() + 1e-12)

    for i in range(N):
        for j in range(N):
            x = i * cell - WORLD_SCALE * 0.5
            y = j * cell - WORLD_SCALE * 0.5
            z = float(u_norm[i, j]) * ZSCALE
            verts.append((x, y, z))

    for i in range(N - 1):
        for j in range(N - 1):
            v0 = i * N + j
            faces.append((v0, v0 + 1, v0 + N + 1, v0 + N))

    me.from_pydata(verts, [], faces)
    me.update()

    # Vertex colour attribute (FLOAT_COLOR stores linear-light values)
    attr = me.attributes.new(ATTR_NAME, "FLOAT_COLOR", "POINT")
    flat = u_norm.ravel()
    colours = [
        (
            COL_LO[0] + (COL_HI[0] - COL_LO[0]) * t,
            COL_LO[1] + (COL_HI[1] - COL_LO[1]) * t,
            COL_LO[2] + (COL_HI[2] - COL_LO[2]) * t,
            1.0,
        )
        for t in flat
    ]
    attr.data.foreach_set("color", [c for rgba in colours for c in rgba])

    obj = bpy.data.objects.new(OBJ_NAME, me)
    bpy.context.scene.collection.objects.link(obj)
    obj["holoflow:facet"] = True
    obj["holoflow:category"] = "stage-floor"
    return obj, me, u_norm


def _add_shape_key(me, obj, u_field, key_name):
    """Append a shape key from a 2D numpy field u_field ∈ [0,1]."""
    u_norm = (u_field - u_field.min()) / (u_field.ptp() + 1e-12)
    if obj.data.shape_keys is None:
        obj.shape_key_add(name="Basis", from_mix=False)
    sk = obj.shape_key_add(name=key_name, from_mix=False)
    coords = []
    cell = WORLD_SCALE / (N - 1)
    for i in range(N):
        for j in range(N):
            x = i * cell - WORLD_SCALE * 0.5
            y = j * cell - WORLD_SCALE * 0.5
            z = float(u_norm[i, j]) * ZSCALE
            coords.extend([x, y, z])
    sk.data.foreach_set("co", coords)


def _add_material(obj):
    """Emit + Principled via Fisher_U vertex colour."""
    mat = bpy.data.materials.new("Fisher_KPP_Mat")
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()

    attr  = nodes.new("ShaderNodeAttribute");  attr.attribute_name = ATTR_NAME
    prin  = nodes.new("ShaderNodeBsdfPrincipled")
    emit  = nodes.new("ShaderNodeEmission");   emit.inputs["Strength"].default_value = 1.4
    mix   = nodes.new("ShaderNodeMixShader");  mix.inputs["Fac"].default_value = 0.35
    out   = nodes.new("ShaderNodeOutputMaterial")

    prin.inputs["Metallic"].default_value   = 0.15
    prin.inputs["Roughness"].default_value  = 0.35

    links.new(attr.outputs["Color"], prin.inputs["Base Color"])
    links.new(attr.outputs["Color"], emit.inputs["Color"])
    links.new(emit.outputs["Emission"],  mix.inputs[1])
    links.new(prin.outputs["BSDF"],      mix.inputs[2])
    links.new(mix.outputs["Shader"],     out.inputs["Surface"])
    obj.data.materials.append(mat)


def _export_glb(path):
    """Export +Y-up, Draco-6, WebP, with morph targets and vertex colours."""
    for obj in bpy.context.scene.objects:
        obj.select_set(obj.name == OBJ_NAME)
    bpy.ops.export_scene.gltf(
        filepath=path,
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=True,
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_image_format="WEBP",
        export_morph=True,
        export_colors=True,
    )


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    print("[Fisher-KPP] Running Basis (monostable, D=0.5 r=1.0 t=30)…")
    u_basis   = _run_kpp(D=0.5, r=1.0, dt=0.10, n_steps=300)

    print("[Fisher-KPP] Running SK_FastR (r=2.0, t=20)…")
    u_fastr   = _run_kpp(D=0.5, r=2.0, dt=0.10, n_steps=200)

    print("[Fisher-KPP] Running SK_LowD (D=0.1, t=60)…")
    u_lowd    = _run_kpp(D=0.1, r=1.0, dt=0.10, n_steps=600)

    print("[Fisher-KPP] Running SK_Bistable (θ=0.30, t=60)…")
    u_bist    = _run_bistable(D=0.5, r=1.0, theta=0.30, dt=0.10, n_steps=600)

    obj, me, _ = _build_base_mesh(u_basis)
    _add_shape_key(me, obj, u_fastr,  "SK_FastR")
    _add_shape_key(me, obj, u_lowd,   "SK_LowD")
    _add_shape_key(me, obj, u_bist,   "SK_Bistable")
    _add_material(obj)

    # Rotate to +Y-up floor convention
    import mathutils
    obj.rotation_euler = mathutils.Euler((-1.5707963, 0, 0), "XYZ")
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(rotation=True)

    bpy.ops.wm.save_as_mainfile(filepath="//fisher_kpp_floor.blend")
    _export_glb("//fisher_kpp_floor.glb")
    print("[Fisher-KPP] Done. fisher_kpp_floor.blend + .glb written.")


if __name__ == "__main__":
    main()
