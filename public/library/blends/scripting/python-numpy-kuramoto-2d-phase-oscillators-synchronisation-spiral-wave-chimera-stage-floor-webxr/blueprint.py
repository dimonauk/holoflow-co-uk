"""
2D Kuramoto Model — Coupled Phase Oscillators, Synchronisation Transition
Y. Kuramoto, "Self-entrainment of a population of coupled non-linear
oscillators," in Proceedings of the International Symposium on Mathematical
Problems in Theoretical Physics, Lecture Notes in Physics vol. 39, pp. 420–422,
Springer 1975. (Public Domain — >50 years)

TECHNIQUE
---------
An N×N grid of phase oscillators θ_{i,j} ∈ [0, 2π) evolves under:

    dθ_{i,j}/dt = ω_{i,j}  +  K Σ_{nn} sin(θ_nn − θ_{i,j})

where ω_{i,j} are natural frequencies drawn from a Lorentzian distribution
(half-width KAPPA), the sum runs over the four nearest neighbours (periodic
boundary conditions), K is the global coupling strength, and time is
integrated by forward Euler with DT = 0.05.

HEIGHT ENCODING: cos(θ) ∈ [−1, 1], shifted to [0, 1] and scaled by Z_SCALE.
When oscillators lock together the cosine landscape becomes smooth, slowly
rotating waves; when incoherent it churns like a turbulent height field.

COLOUR ENCODING: local order parameter r_{local} = |⟨exp(iθ)⟩_{5×5 box}|.
r_local ≈ 0 → cobalt (disordered); r_local ≈ 1 → amber (synchronised).
The local order map directly reveals chimera-like regions inside a single run.

FOUR SHAPE KEYS:
  Basis     K=1.2, KAPPA=0.3, t=300  — near-critical; spiral waves visible
  SK_LowK   K=0.3, KAPPA=0.3, t=300  — subcritical; turbulent incoherence
  SK_HighK  K=3.5, KAPPA=0.3, t=300  — supercritical; nearly locked, slow ripples
  SK_BroadW K=1.2, KAPPA=1.5, t=300  — wider frequency spread; harder to synchronise

WHY FORWARD EULER IS SAFE HERE: the Kuramoto ODE is bounded — |dθ/dt| ≤
|ω_max| + 4K regardless of θ. With DT=0.05, K=3.5, and ω_max ≈ 3KAPPA ≈ 4.5
(3-sigma Lorentzian tail), |dθ/dt|_max ≈ 18.5, giving a Lipschitz step
DT·L_max ≈ 0.93 — safely below the Euler stability limit of 2 for sin-type
nonlinearities. ETD1 gives no benefit here because the nonlinearity is not
stiff; the bottleneck is the 300-step × 4 shape-key simulation budget.

WHY LORENTZIAN NOT GAUSSIAN: the Lorentzian (Cauchy) distribution has the
analytical advantage that the Kuramoto order-parameter ODE ṙ=r(K/2-1/r)
closes exactly in the thermodynamic limit N→∞ for a Lorentzian distribution
of widths γ=KAPPA. Gaussian distributions require numerical quadrature.
"""

import bpy
import bmesh
import math
import numpy as np

# ── parameters ─────────────────────────────────────────────────────────────────
N           = 128      # grid size N×N
DT          = 0.05     # Euler time step (see stability note above)
N_STEPS     = 300      # integration steps per snapshot
SEED        = 42       # NumPy RNG seed

# shape-key configurations
K_BASIS     = 1.2      # near-critical coupling (Basis)
K_LOW       = 0.3      # subcritical (SK_LowK)
K_HIGH      = 3.5      # supercritical (SK_HighK)
K_BROAD     = 1.2      # broad-frequency run (SK_BroadW)
KAPPA       = 0.3      # Lorentzian half-width, basis + low + high
KAPPA_BROAD = 1.5      # wide frequency spread for SK_BroadW

# ── geometry ───────────────────────────────────────────────────────────────────
WORLD_SCALE = 4.0      # floor footprint ±WORLD_SCALE/2 (m)
Z_SCALE     = 0.35     # peak-to-trough height for cos(θ) field (m)
COBALT      = (0.027, 0.141, 0.557, 1.0)
AMBER       = (0.980, 0.620, 0.050, 1.0)
MESH_NAME   = "Kuramoto_Phase"
OBJ_NAME    = "kuramoto_phase_floor"
OUT_BLEND   = "//kuramoto_phase_floor.blend"
OUT_GLB     = "//kuramoto_phase_floor.glb"


# ── Kuramoto simulation ────────────────────────────────────────────────────────

def lorentzian_frequencies(rng: np.random.Generator, kappa: float) -> np.ndarray:
    """
    Draw N×N natural frequencies from a Lorentzian (Cauchy) distribution
    centred at 0 with half-width kappa.
    F(ω) = kappa / (π(ω²+kappa²))

    Why Cauchy.ppf not direct formula: numpy has no Cauchy RNG, but the
    inverse CDF of Cauchy(0, kappa) is kappa·tan(π(u−0.5)) for u∈(0,1).
    Clamp |ω|≤6·kappa to remove the catastrophic heavy-tail outliers that
    would dominate the height field and destabilise Euler for small DT.
    """
    u   = rng.uniform(0.0, 1.0, (N, N)).astype(np.float32)
    u   = np.clip(u, 0.001, 0.999)   # avoid tan(±π/2) = ±∞
    raw = kappa * np.tan(math.pi * (u - 0.5))
    return np.clip(raw, -6.0 * kappa, 6.0 * kappa).astype(np.float32)


def simulate(K: float, kappa: float, rng: np.random.Generator) -> np.ndarray:
    """
    Integrate N_STEPS Euler steps of the 2D Kuramoto model.
    Returns cos(θ) rescaled to [0, 1]: height = 0.5 + 0.5·cos(θ).

    Why cos(θ) not θ itself: θ is unbounded and grows monotonically for
    unsynchronised oscillators. cos(θ) is bounded, periodic, and maps
    phase differences onto a height field that makes synchronised regions
    (slow, smooth cosine waves) visually distinct from incoherent regions
    (rapidly churning, salt-and-pepper heights).
    """
    theta = rng.uniform(0.0, 2.0 * math.pi, (N, N)).astype(np.float32)
    omega = lorentzian_frequencies(rng, kappa)

    for _ in range(N_STEPS):
        # sin(θ_neighbour − θ_self) — numpy roll is O(N²) with minimal memory
        coupling = (
            np.sin(np.roll(theta, -1, axis=1) - theta) +   # east
            np.sin(np.roll(theta,  1, axis=1) - theta) +   # west
            np.sin(np.roll(theta, -1, axis=0) - theta) +   # north
            np.sin(np.roll(theta,  1, axis=0) - theta)     # south
        )
        theta += DT * (omega + K * coupling)

    return (0.5 + 0.5 * np.cos(theta)).astype(np.float32)


def local_order(height: np.ndarray, box: int = 5) -> np.ndarray:
    """
    Estimate local synchrony from the cos-field via a sliding-box mean.
    The order parameter r≈1 for flat (synchronised) regions and r≈0.5 for
    random-phase (incoherent) regions, because ⟨cos θ⟩²≈0 for uniform θ.

    We use the absolute deviation from 0.5: 2|height_mean − 0.5|,
    which is exactly the local mean |cos θ|, ranging 0 (incoherent) to 1
    (fully locked). This avoids the complex-exponential computation while
    capturing the same spatial synchrony structure.
    """
    from numpy.lib.stride_tricks import sliding_window_view
    pad    = box // 2
    padded = np.pad(height, pad, mode="wrap")
    windows = sliding_window_view(padded, (box, box))      # (N, N, box, box)
    local_mean = windows.mean(axis=(-2, -1))
    return np.clip(2.0 * np.abs(local_mean - 0.5), 0.0, 1.0).astype(np.float32)


# ── mesh helpers ───────────────────────────────────────────────────────────────

def build_height_field_mesh(name: str) -> bpy.types.Object:
    """
    N×N vertex quad-grid, all z=0 initially. BMesh direct API avoids the
    bpy.ops.mesh.primitive_grid_add matrix-context dependency.
    """
    mesh = bpy.data.meshes.new(name)
    bm   = bmesh.new()

    step  = WORLD_SCALE / (N - 1)
    verts = []
    for j in range(N):
        for i in range(N):
            x =  i * step - WORLD_SCALE / 2
            y =  j * step - WORLD_SCALE / 2
            verts.append(bm.verts.new((x, y, 0.0)))

    bm.verts.ensure_lookup_table()
    for j in range(N - 1):
        for i in range(N - 1):
            a = verts[j * N + i]
            b = verts[j * N + i + 1]
            c = verts[(j + 1) * N + i + 1]
            d = verts[(j + 1) * N + i]
            bm.faces.new((a, b, c, d))

    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(OBJ_NAME, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def apply_shape_key(obj: bpy.types.Object, name: str,
                    height: np.ndarray) -> None:
    """height ∈ [0, 1]; vertex z = height × Z_SCALE."""
    sk  = obj.shape_key_add(name=name, from_mix=False)
    pts = sk.data
    for j in range(N):
        for i in range(N):
            pts[j * N + i].co.z = float(height[j, i]) * Z_SCALE


def apply_colour_attribute(obj: bpy.types.Object,
                           order: np.ndarray) -> None:
    """
    FLOAT_COLOR vertex attribute. order ∈ [0, 1]: cobalt=incoherent, amber=locked.
    """
    mesh = obj.data
    if "Col" in mesh.color_attributes:
        mesh.color_attributes.remove(mesh.color_attributes["Col"])
    attr = mesh.color_attributes.new("Col", type="FLOAT_COLOR", domain="POINT")
    for j in range(N):
        for i in range(N):
            t = float(order[j, i])
            r = COBALT[0] + t * (AMBER[0] - COBALT[0])
            g = COBALT[1] + t * (AMBER[1] - COBALT[1])
            b = COBALT[2] + t * (AMBER[2] - COBALT[2])
            attr.data[j * N + i].color = (r, g, b, 1.0)


def apply_material(obj: bpy.types.Object) -> None:
    """Vertex-colour MixShader: Principled BSDF + Emission driven by Col."""
    mat = bpy.data.materials.new("Kuramoto_Height")
    mat.use_nodes = True
    nt  = mat.node_tree
    nt.nodes.clear()

    out   = nt.nodes.new("ShaderNodeOutputMaterial")
    mix   = nt.nodes.new("ShaderNodeMixShader")
    bsdf  = nt.nodes.new("ShaderNodeBsdfPrincipled")
    emit  = nt.nodes.new("ShaderNodeEmission")
    attr  = nt.nodes.new("ShaderNodeAttribute")
    gamma = nt.nodes.new("ShaderNodeGamma")

    attr.attribute_name               = "Col"
    bsdf.inputs["Metallic"].default_value    = 0.5
    bsdf.inputs["Roughness"].default_value   = 0.35
    emit.inputs["Strength"].default_value    = 1.5
    gamma.inputs["Gamma"].default_value      = 0.45

    nt.links.new(attr.outputs["Color"],    gamma.inputs["Color"])
    nt.links.new(gamma.outputs["Color"],   bsdf.inputs["Base Color"])
    nt.links.new(gamma.outputs["Color"],   emit.inputs["Color"])
    nt.links.new(attr.outputs["Fac"],      mix.inputs["Fac"])
    nt.links.new(bsdf.outputs["BSDF"],     mix.inputs[1])
    nt.links.new(emit.outputs["Emission"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"],    out.inputs["Surface"])

    obj.data.materials.append(mat)
    obj.data.color_attributes.active_color = obj.data.color_attributes["Col"]


def set_holoflow_props(obj: bpy.types.Object) -> None:
    obj["holoflow:facet"]    = True
    obj["holoflow:category"] = "stage-floor"


def apply_transforms_and_orient(obj: bpy.types.Object) -> None:
    """Rotate −90° around X then apply — matches glTF +Y-up convention."""
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    obj.rotation_euler[0] = -math.pi / 2
    bpy.ops.object.transform_apply(rotation=True)


def export_glb(path: str) -> None:
    bpy.ops.export_scene.gltf(
        filepath                             = path,
        export_format                        = "GLB",
        export_draco_mesh_compression_enable = True,
        export_draco_mesh_compression_level  = 6,
        export_image_format                  = "WEBP",
        export_morph                         = True,
        export_colors                        = True,
        use_selection                        = False,
    )


# ── main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    bpy.ops.wm.read_homefile(app_template="")
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    rng = np.random.default_rng(SEED)

    print("[Kuramoto] simulating Basis  K=1.2  KAPPA=0.3 …")
    h_basis  = simulate(K_BASIS, KAPPA,       rng)
    ord_basis = local_order(h_basis)

    print("[Kuramoto] simulating SK_LowK  K=0.3  KAPPA=0.3 …")
    h_low    = simulate(K_LOW,   KAPPA,       rng)

    print("[Kuramoto] simulating SK_HighK K=3.5  KAPPA=0.3 …")
    h_high   = simulate(K_HIGH,  KAPPA,       rng)

    print("[Kuramoto] simulating SK_BroadW K=1.2 KAPPA=1.5 …")
    h_broad  = simulate(K_BROAD, KAPPA_BROAD, rng)

    obj = build_height_field_mesh(MESH_NAME)

    # shape-key Basis must be added first; subsequent keys are offsets from it
    obj.shape_key_add(name="Basis",     from_mix=False)
    apply_shape_key(obj, "Basis",     h_basis)
    apply_shape_key(obj, "SK_LowK",   h_low)
    apply_shape_key(obj, "SK_HighK",  h_high)
    apply_shape_key(obj, "SK_BroadW", h_broad)

    apply_colour_attribute(obj, ord_basis)
    apply_material(obj)
    set_holoflow_props(obj)
    apply_transforms_and_orient(obj)

    bpy.ops.wm.save_as_mainfile(filepath=bpy.path.abspath(OUT_BLEND))
    export_glb(bpy.path.abspath(OUT_GLB))
    print("[Kuramoto] blueprint complete — blend + glb saved.")


if __name__ == "__main__":
    main()
