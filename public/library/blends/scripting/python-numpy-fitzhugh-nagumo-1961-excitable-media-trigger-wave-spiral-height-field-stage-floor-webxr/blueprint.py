"""
FitzHugh-Nagumo Excitable Media — Spirals, Trigger Waves, Target Patterns
Holoflow Studio · Blender 5.1 · CC0

TECHNIQUE
---------
The FitzHugh-Nagumo (FHN) model (FitzHugh 1961, Nagumo et al. 1962) reduces
the four-variable Hodgkin-Huxley nerve-impulse equations to two: a fast cubic
activator u (voltage-like) and a slow recovery variable v.  With spatial
diffusion of u only, the system self-organises into trigger waves, rotating
spirals, and target rings — the same reentrant dynamics seen in cardiac
arrhythmia.  ETD1 (Cox-Matthews 2002) exact-exponentiates the stiff diffusion
operator (dt = 0.10, vs Euler limit dt < 0.0005 at N=128) while FHN kinetics
and v-recovery are explicit, each stable at dt = 0.10.

OUTSIDE SOURCES
---------------
1. FitzHugh R. (1961). "Impulses and physiological states in theoretical
   models of nerve membrane." Biophys. J. 1(6):445-466.
   DOI: 10.1016/S0006-3495(61)86902-6  (PMC1366333, open access)
   Related project: NumPy (BSD-3)  https://github.com/numpy/numpy

2. Barkley D. (1991). "A model for fast computer simulation of waves in
   excitable media." Physica D 49:61-70.
   DOI: 10.1016/0167-2789(91)90194-E
   PD-equivalent equations; Barkley parameterisation bridges FHN to cardiac.
   Related project: SciPy (BSD-3)  https://github.com/scipy/scipy
"""

import bpy
import numpy as np

# ── PARAMETERS ────────────────────────────────────────────────────────────────
N       = 128       # grid side → N² verts, (N-1)² quads
DU      = 1.0       # voltage diffusion (v has no diffusion)
DT      = 0.10      # time step — ETD1 makes diffusion unconditionally stable
Z_SCALE = 0.50      # height amplitude (Blender units)

# FHN kinetics (FitzHugh 1961 original)
EPS   = 0.08        # slow-fast ratio: small = fast wave, slow recovery
A_KIN = 0.70        # recovery nullcline offset
B_KIN = 0.80        # recovery damping
IEXT  = 0.50        # applied current (sub-threshold; drives slow oscillation)

VARIANTS = {
    "Basis":      ("edge_pulse", 600),   # trigger wave front
    "SK_Spiral":  ("s1s2",      1200),   # two-armed spiral
    "SK_Target":  ("target",    1400),   # concentric target rings
    "SK_Reentry": ("reentry",    900),   # single reentrant spiral
}

MESH_NAME = "FHN_Voltage"
OBJ_NAME  = "FHN_Floor"
ATTR_NAME = "FHN_U_Volt"  # FLOAT_COLOR POINT (cobalt → amber)
U_MIN, U_MAX = -1.5, 2.1  # display range for normalisation


# ── SPECTRAL HELPERS ──────────────────────────────────────────────────────────
def _k2(n: int) -> np.ndarray:
    kx = np.fft.fftfreq(n, d=1.0 / n)
    ky = np.fft.rfftfreq(n, d=1.0 / n)
    KX, KY = np.meshgrid(kx, ky, indexing="ij")
    return (2.0 * np.pi / n) ** 2 * (KX**2 + KY**2)


def _etd1_u(k2: np.ndarray):
    """ETD1 for stiff diffusion of u: L_u(k) = -DU·|k|², N_u explicit."""
    Lu = -DU * k2 * DT
    return np.exp(Lu), np.where(np.abs(Lu) < 1e-12, 1.0, np.expm1(Lu) / Lu)


def _etd1_v():
    """Exact exponential for local v decay: L_v = -ε·B, N_v = ε(u+A)."""
    Lv = -EPS * B_KIN * DT
    return float(np.exp(Lv)), float(np.expm1(Lv) / Lv)


# ── INITIAL CONDITIONS ────────────────────────────────────────────────────────
def _ic_edge_pulse():
    u = np.full((N, N), -1.2)
    v = np.zeros((N, N))
    u[:10, :] = 2.0
    return u, v


def _ic_s1s2():
    """S1+S2 cross-field protocol: creates a free spiral tip."""
    u, v = _ic_edge_pulse()
    E_u, phi1_u = _etd1_u(_k2(N))
    E_v, phi1_v = _etd1_v()
    u_h = np.fft.rfft2(u)
    for _ in range(300):               # let S1 wave propagate across
        Nu  = u - u**3 / 3.0 - v + IEXT
        u_h = E_u * u_h + phi1_u * np.fft.rfft2(Nu) * DT
        u   = np.clip(np.fft.irfft2(u_h, s=(N, N)), -2.5, 2.5)
        u_h = np.fft.rfft2(u)
        v   = E_v * v + phi1_v * (EPS * (u + A_KIN)) * DT
    u[:, : N // 2] = 2.0              # S2 stimulus on bottom half
    v[:, : N // 2] = 0.0
    return u, v


def _ic_target():
    u = np.full((N, N), -1.2)
    v = np.zeros((N, N))
    c, r = N // 2, 5
    u[c - r: c + r, c - r: c + r] = 2.0
    return u, v


def _ic_reentry():
    """Top-half active + top-right refractory → single spiral tip."""
    u = np.full((N, N), -1.2)
    v = np.zeros((N, N))
    u[: N // 2, :] = 2.0
    v[: N // 2, N // 2:] = 1.0
    return u, v


IC_MAP = {"edge_pulse": _ic_edge_pulse, "s1s2": _ic_s1s2,
          "target": _ic_target, "reentry": _ic_reentry}


# ── INTEGRATION ───────────────────────────────────────────────────────────────
def _run(u, v, steps, E_u, phi1_u, E_v, phi1_v):
    """ETD1 loop: diffusion exact, kinetics and v-coupling explicit."""
    u_h = np.fft.rfft2(u)
    for _ in range(steps):
        Nu  = u - u**3 / 3.0 - v + IEXT
        u_h = E_u * u_h + phi1_u * np.fft.rfft2(Nu) * DT
        u   = np.clip(np.fft.irfft2(u_h, s=(N, N)), -2.5, 2.5)
        u_h = np.fft.rfft2(u)
        v   = E_v * v + phi1_v * (EPS * (u + A_KIN)) * DT
    return u, v


# ── MESH + ATTR ───────────────────────────────────────────────────────────────
def _norm(u: np.ndarray) -> np.ndarray:
    return np.clip((u - U_MIN) / (U_MAX - U_MIN), 0.0, 1.0)


def _build_mesh(u: np.ndarray) -> bpy.types.Object:
    t = _norm(u)
    verts, faces = [], []
    for i in range(N):
        for j in range(N):
            verts.append(((i / (N - 1)) * 2 - 1,
                          (j / (N - 1)) * 2 - 1,
                          float(t[i, j]) * Z_SCALE))
    for i in range(N - 1):
        for j in range(N - 1):
            a = i * N + j
            faces.append((a, a + 1, a + N + 1, a + N))
    mesh = bpy.data.meshes.new(MESH_NAME)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(OBJ_NAME, mesh)
    bpy.context.collection.objects.link(obj)
    obj["holoflow:facet"] = True
    return obj


def _write_colour(mesh: bpy.types.Mesh, u: np.ndarray) -> None:
    if ATTR_NAME not in mesh.attributes:
        mesh.attributes.new(ATTR_NAME, "FLOAT_COLOR", "POINT")
    t = _norm(u).ravel(order="C").astype(np.float32)
    rgba = np.stack([t * 1.00 + (1 - t) * 0.03,
                     t * 0.65 + (1 - t) * 0.14,
                     t * 0.00 + (1 - t) * 0.56,
                     np.ones_like(t)], axis=1).ravel()
    mesh.attributes[ATTR_NAME].data.foreach_set("color", rgba.tolist())


def _add_shape_key(obj, u: np.ndarray, name: str) -> None:
    t  = _norm(u)
    sk = obj.shape_key_add(name=name, from_mix=False)
    coords = np.empty(N * N * 3, dtype=np.float32)
    for idx in range(N * N):
        i, j = divmod(idx, N)
        coords[idx * 3: idx * 3 + 3] = [
            (i / (N - 1)) * 2 - 1,
            (j / (N - 1)) * 2 - 1,
            float(t[i, j]) * Z_SCALE,
        ]
    sk.data.foreach_set("co", coords.tolist())


def _material(obj) -> None:
    mat = bpy.data.materials.new("FHN_Mat")
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out  = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    attr = nodes.new("ShaderNodeAttribute")
    attr.attribute_name = ATTR_NAME
    bsdf.inputs["Metallic"].default_value  = 0.20
    bsdf.inputs["Roughness"].default_value = 0.30
    bsdf.inputs["Emission Strength"].default_value = 1.6
    links.new(attr.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(attr.outputs["Color"], bsdf.inputs["Emission Color"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    obj.data.materials.append(mat)


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main() -> None:
    for o in list(bpy.context.scene.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    k2_arr      = _k2(N)
    E_u, phi1_u = _etd1_u(k2_arr)
    E_v, phi1_v = _etd1_v()
    obj          = None

    for sk_name, (ic_key, steps) in VARIANTS.items():
        u, v = IC_MAP[ic_key]()
        u, v = _run(u, v, steps, E_u, phi1_u, E_v, phi1_v)
        if sk_name == "Basis":
            obj = _build_mesh(u)
            _write_colour(obj.data, u)
            obj.shape_key_add(name="Basis", from_mix=False)
        else:
            _add_shape_key(obj, u, sk_name)

    _material(obj)
    print(f"[FHN] {N}×{N}={N*N}V  {(N-1)**2}Q  obj={obj.name}")


main()
