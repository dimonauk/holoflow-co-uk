"""
Talbot Effect (1836) — Near-Field Self-Imaging, Fractional Talbot, Gauss-Sum Height-Field
H. F. Talbot 1836 / M. V. Berry & S. Klein 1996 · Blender 5.1 · bpy direct-data API
─────────────────────────────────────────────────────────────────────────────────────────

Paraxial scalar diffraction from a periodic amplitude grating of period d.
In the Fresnel (near-field) approximation the field at distance z is:

    U(x, z) = Σ_{n=-N}^{N}  c_n · exp(2πinx/d) · exp(−iπn²λz/d²)

where c_n are the Fourier coefficients of the grating transmittance.
The Talbot length z_T = 2d²/λ is the propagation distance after which
the phase exp(−iπn²λz_T/d²) = exp(−2πin²) = 1 for all integers n,
restoring the original field exactly — the self-imaging condition.

At z = (p/q)·z_T, Berry & Klein (1996) showed that I(x,z) decomposes
into q copies of the grating shifted by multiples of d/q, with Gauss-sum
phase weights.  At irrational z/z_T, I is a fractal measure of Hausdorff
dimension 3/2 — the Talbot carpet.

Four shape keys sample distinct grating profiles by changing c_n:

  Basis      binary amplitude grating (square wave, 50% duty cycle)
  SK_Sine    sinusoidal amplitude grating (single harmonic N=1)
  SK_Blazed  blazed / sawtooth amplitude grating (N_HARM harmonics)
  SK_Phase   binary π-phase grating (amplitude uniform, ±1 phase)

The intensity carpet I(x,z) on a 128×128 grid is used as the Z coordinate
after log1p normalisation, producing the Talbot carpet as a stage-floor mesh.
"""

import sys
import numpy as np

# ── guard: runs only inside Blender ──────────────────────────────────────────
try:
    import bpy
    from mathutils import Matrix
except ModuleNotFoundError:
    print("Run this script inside Blender (Scripting workspace ▶ Run Script).")
    sys.exit(1)

# ── named constants ───────────────────────────────────────────────────────────
GRATING_PERIOD = 1.0          # d  (normalised; sets length scale)
WAVELENGTH     = 0.05         # λ/d = 1/20 → z_T = 2d²/λ = 40
Z_TALBOT       = 2.0 * GRATING_PERIOD**2 / WAVELENGTH   # 40.0
Z_MAX          = 2.0 * Z_TALBOT                          # show 2 Talbot lengths
N_HARM         = 20           # Fourier harmonics retained (±N_HARM)
GRID_N         = 128          # vertices per axis: 128×128 = 16 384V / 16 129Q
WORLD          = 4.0          # half-size of mesh in Blender world units
ZSCALE         = 0.38         # height-field amplitude (Blender units)
OBJ_NAME       = "Talbot_Floor"
ATTR_NAME      = "TC_Intensity"
COBALT         = (0.027, 0.159, 0.408, 1.0)
AMBER          = (0.980, 0.620, 0.050, 1.0)

# ── Fourier coefficients ──────────────────────────────────────────────────────

def _fourier_coeffs(grating: str, n: np.ndarray) -> np.ndarray:
    """Complex Fourier coefficients c_n for the given grating profile."""
    n_safe = np.where(n == 0, 1, n).astype(np.float64)  # avoid /0 at n=0
    cn = np.zeros(len(n), dtype=np.complex128)

    if grating == "binary":
        # t(x) = 1 for 0 ≤ x < d/2 else 0  (50% duty cycle)
        # c_n = sin(nπ/2) / (nπ) for n≠0; c_0 = 0.5
        # np.sinc(n/2) = sin(nπ/2)/(nπ/2), so c_n = np.sinc(n/2)/2
        cn = (np.sinc(n / 2.0) / 2.0).astype(np.complex128)

    elif grating == "sinusoidal":
        # t(x) = (1 + cos(2πx/d))/2 — only harmonics 0 and ±1 are nonzero
        cn[n == 0]             = 0.5
        cn[np.abs(n) == 1]     = 0.25

    elif grating == "blazed":
        # t(x) = x/d − floor(x/d)  (sawtooth 0→1, mean = 0.5)
        # c_0 = 0.5; c_n = i/(2πn) for n≠0
        cn[n == 0]    = 0.5 + 0j
        nz = n != 0
        cn[nz]        = 1j / (2.0 * np.pi * n_safe[nz])

    elif grating == "phase":
        # t(x) = +1 for 0 ≤ x < d/2 else −1  (binary ±1 phase grating)
        # c_0 = 0; c_n = 2/(iπn) for odd n; 0 for even n
        odd = (n != 0) & (np.abs(n) % 2 == 1)
        cn[odd] = 2.0 / (1j * np.pi * n_safe[odd])

    return cn


# ── intensity carpet ──────────────────────────────────────────────────────────

def carpet_for(grating: str) -> np.ndarray:
    """Return (GRID_N, GRID_N) log1p-normalised intensity I(x, z)."""
    n  = np.arange(-N_HARM, N_HARM + 1, dtype=np.float64)   # (2N+1,)
    cn = _fourier_coeffs(grating, n)                          # (2N+1,) complex

    x = np.linspace(0.0, GRATING_PERIOD, GRID_N, endpoint=False)   # (GRID_N,)
    z = np.linspace(0.0, Z_MAX,          GRID_N)                    # (GRID_N,)

    # Spatial modes: x_modes[i, k] = exp(2πi·n[k]·x[i]/d)
    x_modes = np.exp(2j * np.pi * n[None, :] * (x[:, None] / GRATING_PERIOD))

    # Propagation phases: z_modes[j, k] = exp(−iπ·n[k]²·λ·z[j]/d²)
    #                    = exp(−2πi·n[k]²·z[j]/z_T)
    z_modes = np.exp(-2j * np.pi * n[None, :]**2 * (z[:, None] / Z_TALBOT))

    # Weighted spatial modes: (cn · x_modes) has shape (GRID_N, 2N+1)
    cx_modes = cn[None, :] * x_modes

    # U[i,j] = Σ_k cx_modes[i,k] · z_modes[j,k]  ← matrix multiply
    U         = cx_modes @ z_modes.T         # (GRID_N_x, GRID_N_z), complex
    intensity = np.abs(U) ** 2               # real, ≥ 0

    raw = np.log1p(intensity)
    mx  = raw.max()
    return (raw / mx) if mx > 0.0 else raw


# ── mesh helpers ──────────────────────────────────────────────────────────────

def _verts_faces(density: np.ndarray):
    N = GRID_N
    xs = np.linspace(-WORLD, WORLD, N)
    ys = np.linspace(-WORLD, WORLD, N)
    XG, YG = np.meshgrid(xs, ys, indexing="ij")  # (N,N) each
    ZG = density * ZSCALE
    verts = list(zip(XG.ravel(), YG.ravel(), ZG.ravel()))
    faces = []
    for r in range(N - 1):
        for c in range(N - 1):
            a = r * N + c
            faces.append((a, a + 1, a + N + 1, a + N))
    return verts, faces


def _make_mesh(name: str, verts, faces) -> bpy.types.Object:
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    return ob


def _add_shape_key(ob: bpy.types.Object, sk_name: str, density: np.ndarray):
    N = GRID_N
    xs = np.linspace(-WORLD, WORLD, N)
    ys = np.linspace(-WORLD, WORLD, N)
    XG, YG = np.meshgrid(xs, ys, indexing="ij")
    ZG = density * ZSCALE
    sk = ob.shape_key_add(name=sk_name, from_mix=False)
    for r in range(N):
        for c in range(N):
            idx = r * N + c
            sk.data[idx].co = (float(XG[r, c]), float(YG[r, c]), float(ZG[r, c]))


def _apply_colour(ob: bpy.types.Object, density: np.ndarray):
    me = ob.data
    attr = me.color_attributes.new(name=ATTR_NAME, type="FLOAT_COLOR", domain="POINT")
    n_verts = GRID_N * GRID_N
    t = density.ravel()
    cols = np.empty(n_verts * 4, dtype=np.float32)
    cols[0::4] = COBALT[0] + (AMBER[0] - COBALT[0]) * t
    cols[1::4] = COBALT[1] + (AMBER[1] - COBALT[1]) * t
    cols[2::4] = COBALT[2] + (AMBER[2] - COBALT[2]) * t
    cols[3::4] = 1.0
    attr.data.foreach_set("color", cols)


def _add_material(ob: bpy.types.Object):
    mat = bpy.data.materials.new(name=f"{OBJ_NAME}_Mat")
    mat.use_nodes = True
    nt  = mat.node_tree
    nt.nodes.clear()
    attr_n   = nt.nodes.new("ShaderNodeAttribute")
    attr_n.attribute_name = ATTR_NAME
    attr_n.location = (-400, 0)
    bsdf_n   = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf_n.location = (-100, 0)
    bsdf_n.inputs["Metallic"].default_value    = 0.35
    bsdf_n.inputs["Roughness"].default_value   = 0.22
    emit_n   = nt.nodes.new("ShaderNodeEmission")
    emit_n.location = (-100, -200)
    emit_n.inputs["Strength"].default_value = 1.6
    mix_n    = nt.nodes.new("ShaderNodeMixShader")
    mix_n.inputs["Fac"].default_value = 0.35
    mix_n.location = (200, 0)
    out_n    = nt.nodes.new("ShaderNodeOutputMaterial")
    out_n.location = (450, 0)
    links = nt.links
    links.new(attr_n.outputs["Color"], bsdf_n.inputs["Base Color"])
    links.new(attr_n.outputs["Color"], emit_n.inputs["Color"])
    links.new(bsdf_n.outputs["BSDF"],  mix_n.inputs[1])
    links.new(emit_n.outputs["Emission"], mix_n.inputs[2])
    links.new(mix_n.outputs["Shader"], out_n.inputs["Surface"])
    ob.data.materials.append(mat)


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    # Remove previous run if present
    if OBJ_NAME in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[OBJ_NAME], do_unlink=True)

    # ── Basis: binary amplitude grating ──────────────────────────────────────
    print(f"[Talbot] Computing Basis (binary grating) …")
    d_basis = carpet_for("binary")
    verts, faces = _verts_faces(d_basis)
    ob = _make_mesh(OBJ_NAME, verts, faces)
    ob.shape_key_add(name="Basis", from_mix=False)
    _apply_colour(ob, d_basis)
    _add_material(ob)

    # ── Shape keys ────────────────────────────────────────────────────────────
    for sk_name, grating in [
        ("SK_Sine",   "sinusoidal"),
        ("SK_Blazed", "blazed"),
        ("SK_Phase",  "phase"),
    ]:
        print(f"[Talbot] Computing {sk_name} ({grating} grating) …")
        _add_shape_key(ob, sk_name, carpet_for(grating))

    # ── Custom properties for Holoflow ────────────────────────────────────────
    ob["holoflow:facet"]    = True
    ob["holoflow:category"] = "stage-floor"

    # ── Y-up WebXR orientation ────────────────────────────────────────────────
    ob.data.transform(Matrix.Rotation(3.141592653589793 / 2.0, 4, "X"))
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.transform_apply(rotation=True)

    # ── Save .blend ───────────────────────────────────────────────────────────
    blend_path = bpy.path.abspath("//talbot_floor.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    # ── Export .glb ───────────────────────────────────────────────────────────
    glb_path = bpy.path.abspath("//talbot_floor.glb")
    bpy.ops.export_scene.gltf(
        filepath            = glb_path,
        export_format       = "GLB",
        export_draco_mesh_compression_enable = True,
        export_draco_mesh_compression_level  = 6,
        export_image_format = "WEBP",
        export_morph        = True,
        export_colors       = True,
    )
    n_v = GRID_N * GRID_N
    n_q = (GRID_N - 1) * (GRID_N - 1)
    print(f"[Talbot] Done — '{OBJ_NAME}' {n_v}V {n_q}Q")
    print(f"[Talbot] GLB: {glb_path}")


main()
