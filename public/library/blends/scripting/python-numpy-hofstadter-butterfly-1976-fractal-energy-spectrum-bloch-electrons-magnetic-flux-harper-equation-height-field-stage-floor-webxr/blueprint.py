"""
Blender 5.1 — Hofstadter Butterfly (Hofstadter 1976)
Fractal energy spectrum of 2D Bloch electrons in a transverse magnetic field.

Harper equation:  ψ_{n+1} + ψ_{n-1} + 2 cos(2π α n + k_y) ψ_n = E ψ_n
where α = p/q (magnetic flux per plaquette in units of h/e)

For rational α = p/q the Bloch Hamiltonian is a q×q matrix; its q eigenvalues
form q energy bands.  Sweeping α across [0,1] at all k-points traces out the
self-similar 'butterfly' fractal, first computed by Hofstadter 1976.

Topological content: each gap in the butterfly carries an integer Chern number
(TKNN invariant, Thouless–Kohmoto–Nightingale–den Nijs 1982) that equals the
Hall conductance in units of e²/h.  The 1/3-butterfly and 2/3-butterfly are
themselves perfect Hofstadter butterflies — the fractal is exact.

Visualisation: 128 × 128 height field where
  x-axis  → α ∈ [0, 1]   (normalised flux quanta)
  y-axis  → E ∈ [−4, 4]  (tight-binding energy bandwidth)
  z-value → log1p(spectral density) normalised to [0, 1]

Colour ramp: cobalt (no states) → amber (high density of states)
Four shape keys show the butterfly at different α windows and NNN hopping.

Licence: CC0 — Hofstadter 1976 PhysRevB 14:2239 PD(>40 yr); NumPy BSD-3.
Run inside Blender 5.1 Scripting workspace.
"""

import bpy
import numpy as np

# ── simulation parameters ────────────────────────────────────────────────────
N          = 128          # grid resolution: 128 α values × 128 energy bins
Q_MAX      = 50           # maximum denominator for rational approximation of α
N_K        = 24           # k-points per dimension (N_K² per α value)
E_MIN      = -4.0         # tight-binding lower band edge (t = 1)
E_MAX      =  4.0         # tight-binding upper band edge
Z_SCALE    = 0.50         # height of the tallest column
WORLD      = 4.0          # mesh world-space extent (−WORLD/2 … +WORLD/2)
OBJ_NAME   = "hofstadter_floor"


# ── rational approximation ────────────────────────────────────────────────────

def _best_pq(alpha: float, q_max: int) -> tuple[int, int]:
    """
    Continued-fraction best rational approximation p/q of alpha with q ≤ q_max.
    Uses the standard convergent recurrence, not the fractions module, so it
    works with arbitrary precision numpy floats and avoids import overhead.
    """
    if alpha <= 0.0:
        return 0, 1
    if alpha >= 1.0:
        return 1, 1

    # Continued fraction convergents
    h_prev, h_curr = 1, int(alpha)
    k_prev, k_curr = 0, 1
    remainder = alpha - int(alpha)

    for _ in range(40):
        if remainder < 1e-10:
            break
        a_next = int(1.0 / remainder)
        remainder = 1.0 / remainder - a_next
        h_next = a_next * h_curr + h_prev
        k_next = a_next * k_curr + k_prev
        if k_next > q_max:
            break
        h_prev, h_curr = h_curr, h_next
        k_prev, k_curr = k_curr, k_next

    return h_curr, k_curr


# ── Hofstadter Bloch Hamiltonian ──────────────────────────────────────────────

def _harper_matrix(q: int, p: int, kx: float, ky: float) -> np.ndarray:
    """
    q × q Bloch Hamiltonian H(k_x, k_y) for flux α = p/q.

    Landau-gauge convention: Peierls phase on y-hops = 2π α m,
    Bloch phase exp(±i q k_x) at the magnetic-unit-cell boundary.

    Diagonal:   H_{m,m} = 2 cos(2π α m + k_y)       [y-hopping contribution]
    Off-diag:   H_{m,m±1} = 1                          [x-hopping, open chain]
    Boundary:   H_{0,q-1} = exp(−i q k_x)              [closed chain, Bloch]
                H_{q-1,0} = exp(+i q k_x)
    """
    alpha = p / q if q > 0 else 0.0
    H = np.zeros((q, q), dtype=complex)
    for m in range(q):
        H[m, m] = 2.0 * np.cos(2.0 * np.pi * alpha * m + ky)
    for m in range(q - 1):
        H[m, m + 1] = 1.0
        H[m + 1, m] = 1.0
    phase = np.exp(1j * q * kx)
    H[0, q - 1] = np.conj(phase)   # exp(−i q k_x)
    H[q - 1, 0] = phase             # exp(+i q k_x)
    return H


def _harper_matrix_nnn(q: int, p: int, kx: float, ky: float,
                        t2: float = 0.3) -> np.ndarray:
    """
    Hofstadter Hamiltonian with next-nearest-neighbour (NNN) hopping t2.

    NNN adds diagonal hops in x (H_{m,m±2}) and a doubled Peierls phase
    contribution to the diagonal (y-NNN):
        H_{m,m} += 2 t2 cos(4π α m + 2 k_y)   [y-NNN]
        H_{m,m±2} += t2                         [x-NNN]

    NNN breaks particle-hole symmetry (E → −E no longer maps spectrum to
    itself), shifting the butterfly and asymmetrically warping each wing.
    """
    H = _harper_matrix(q, p, kx, ky)
    alpha = p / q if q > 0 else 0.0
    for m in range(q):
        H[m, m] += 2.0 * t2 * np.cos(4.0 * np.pi * alpha * m + 2.0 * ky)
    for m in range(q - 2):
        H[m, m + 2] += t2
        H[m + 2, m] += t2
    # NNN periodic boundaries
    phase2 = np.exp(1j * q * kx)
    if q >= 2:
        H[0, q - 2] += t2 * np.conj(phase2)
        H[q - 2, 0] += t2 * phase2
        H[1, q - 1] += t2 * np.conj(phase2)
        H[q - 1, 1] += t2 * phase2
    return H


# ── spectral density computation ──────────────────────────────────────────────

def _compute_density(alpha_vals: np.ndarray,
                     e_min: float, e_max: float, n_e: int,
                     n_k: int, q_max: int,
                     nnn: bool = False, t2: float = 0.3) -> np.ndarray:
    """
    Returns density[n_alpha, n_e]: number of eigenvalues per (α, E) cell.

    For each α we find p/q, build the q×q Harper matrix at n_k² k-points,
    diagonalise each, and bin the q eigenvalues into energy slots.
    The nested k-loops are the computational bottleneck; n_k = 24 gives
    576 diagonalisations per α value.  At q_max = 50 and n_alpha = 128
    this is ~35 k diagonalisations total, completing in a few seconds.
    """
    n_alpha = len(alpha_vals)
    density = np.zeros((n_alpha, n_e), dtype=np.float32)
    de = (e_max - e_min) / n_e
    kx_vals = np.linspace(0.0, 2.0 * np.pi, n_k, endpoint=False)
    ky_vals = np.linspace(0.0, 2.0 * np.pi, n_k, endpoint=False)

    for i, alpha in enumerate(alpha_vals):
        p, q = _best_pq(alpha, q_max)
        for kx in kx_vals:
            for ky in ky_vals:
                if nnn:
                    H = _harper_matrix_nnn(q, p, kx / max(q, 1), ky, t2)
                else:
                    H = _harper_matrix(q, p, kx / max(q, 1), ky)
                evals = np.linalg.eigh(H)[0]  # sorted real eigenvalues
                for e in evals:
                    j = int((e - e_min) / de)
                    if 0 <= j < n_e:
                        density[i, j] += 1.0

    return density


def _normalise(density: np.ndarray) -> np.ndarray:
    """log1p normalisation: compresses dynamic range while preserving zero."""
    d = np.log1p(density)
    mx = d.max()
    return d / mx if mx > 0 else d


# ── mesh builders ─────────────────────────────────────────────────────────────

def _make_grid(density: np.ndarray) -> tuple[list, list]:
    """
    Build flat vertex list and face list for a 128 × 128 height-field mesh.

    Vertices are laid out in row-major order: index = row * N + col.
    Quads are wound CCW when viewed from above (+Z): order
    (i*N+j, i*N+j+1, (i+1)*N+j+1, (i+1)*N+j).
    """
    n_alpha, n_e = density.shape
    half = WORLD / 2.0
    xs = np.linspace(-half, half, n_alpha)   # x ↔ α
    ys = np.linspace(-half, half, n_e)       # y ↔ E
    Z  = Z_SCALE * _normalise(density)       # height field

    verts, faces = [], []
    for i in range(n_alpha):
        for j in range(n_e):
            verts.append((xs[i], ys[j], float(Z[i, j])))

    for i in range(n_alpha - 1):
        for j in range(n_e - 1):
            a = i * n_e + j
            b = a + 1
            c = (i + 1) * n_e + j + 1
            d = (i + 1) * n_e + j
            faces.append((a, b, c, d))

    return verts, faces


def _apply_shape_key(ob: bpy.types.Object, name: str,
                     density: np.ndarray) -> None:
    """Write per-vertex Z from density into a new shape key."""
    Z = Z_SCALE * _normalise(density)
    n_alpha, n_e = density.shape
    key_block = ob.shape_key_add(name=name, from_mix=False)

    coords = np.empty(len(ob.data.vertices) * 3, dtype=np.float32)
    ob.data.vertices.foreach_get("co", coords)
    coords = coords.reshape(-1, 3)

    # Overwrite only Z; X and Y stay identical to the Basis
    for i in range(n_alpha):
        for j in range(n_e):
            idx = i * n_e + j
            coords[idx, 2] = float(Z[i, j])

    key_block.data.foreach_set("co", coords.ravel())


# ── material ──────────────────────────────────────────────────────────────────

def _build_material(ob: bpy.types.Object) -> None:
    """
    Node material: vertex colour attribute HF_Density drives a cobalt→amber
    colour ramp.  MixShader blends Principled BSDF with Emission so the floor
    glows in WebXR ambient light.
    """
    mat = bpy.data.materials.new("HofstadterMat")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    attr  = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = "HF_Density"
    attr.location = (-600, 0)

    ramp  = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.color_space = "LINEAR"
    ramp.location = (-400, 0)
    el = ramp.color_ramp.elements
    el[0].position = 0.0;  el[0].color = (0.027, 0.159, 0.408, 1.0)  # cobalt
    el[1].position = 1.0;  el[1].color = (0.980, 0.620, 0.050, 1.0)  # amber

    princ = nt.nodes.new("ShaderNodeBsdfPrincipled")
    princ.location = (-100, 80)

    emit  = nt.nodes.new("ShaderNodeEmission")
    emit.inputs["Strength"].default_value = 1.6
    emit.location = (-100, -80)

    mix   = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs["Fac"].default_value = 0.35
    mix.location = (150, 0)

    out   = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (350, 0)

    nt.links.new(attr.outputs["Color"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], princ.inputs["Base Color"])
    nt.links.new(ramp.outputs["Color"], emit.inputs["Color"])
    nt.links.new(princ.outputs["BSDF"], mix.inputs[1])
    nt.links.new(emit.outputs["Emission"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])

    ob.data.materials.append(mat)


def _paint_vertex_colour(ob: bpy.types.Object, density: np.ndarray) -> None:
    """Write normalised spectral density as a Float Color vertex attribute."""
    mesh = ob.data
    if "HF_Density" not in mesh.color_attributes:
        mesh.color_attributes.new("HF_Density", "FLOAT_COLOR", "POINT")
    attr = mesh.color_attributes["HF_Density"]
    Z = _normalise(density).ravel()
    n = len(Z)
    data = np.empty(n * 4, dtype=np.float32)
    data[0::4] = Z;  data[1::4] = Z;  data[2::4] = Z;  data[3::4] = 1.0
    attr.data.foreach_set("color", data)


# ── scene assembly ────────────────────────────────────────────────────────────

def main() -> None:
    # ── 1. clear scene ────────────────────────────────────────────────────────
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    # ── 2. compute basis density: full butterfly ──────────────────────────────
    print("[hofstadter] Computing Basis (full butterfly) …")
    alphas_full = np.linspace(0.0, 1.0, N, endpoint=False) + 0.5 / N
    density_basis = _compute_density(
        alphas_full, E_MIN, E_MAX, N, N_K, Q_MAX, nnn=False)
    print("[hofstadter] Basis done.")

    # ── 3. compute SK_Half: α ∈ [0, 0.5] zoomed to full grid ─────────────────
    print("[hofstadter] Computing SK_Half …")
    alphas_half = np.linspace(0.0, 0.5, N, endpoint=False) + 0.25 / N
    density_half = _compute_density(
        alphas_half, E_MIN, E_MAX, N, N_K, Q_MAX, nnn=False)
    print("[hofstadter] SK_Half done.")

    # ── 4. compute SK_Zoom: α ∈ [0.25, 0.50] — the 1/3-sub-butterfly ─────────
    print("[hofstadter] Computing SK_Zoom (1/3 sub-butterfly) …")
    alphas_zoom = np.linspace(0.25, 0.5, N, endpoint=False) + 0.125 / N
    density_zoom = _compute_density(
        alphas_zoom, E_MIN, E_MAX, N, N_K, Q_MAX, nnn=False)
    print("[hofstadter] SK_Zoom done.")

    # ── 5. compute SK_NNN: full butterfly with t₂ = 0.3 NNN hopping ──────────
    print("[hofstadter] Computing SK_NNN (NNN t2=0.3) …")
    density_nnn = _compute_density(
        alphas_full, E_MIN, E_MAX, N, N_K, Q_MAX, nnn=True, t2=0.3)
    print("[hofstadter] SK_NNN done.")

    # ── 6. build mesh from basis density ─────────────────────────────────────
    verts, faces = _make_grid(density_basis)
    mesh = bpy.data.meshes.new(OBJ_NAME)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    ob = bpy.data.objects.new(OBJ_NAME, mesh)
    bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob

    # ── 7. vertex colour for material ─────────────────────────────────────────
    _paint_vertex_colour(ob, density_basis)

    # ── 8. material ───────────────────────────────────────────────────────────
    _build_material(ob)

    # ── 9. shape keys ─────────────────────────────────────────────────────────
    ob.shape_key_add(name="Basis", from_mix=False)
    _apply_shape_key(ob, "SK_Half", density_half)
    _apply_shape_key(ob, "SK_Zoom", density_zoom)
    _apply_shape_key(ob, "SK_NNN",  density_nnn)

    # ── 10. holoflow metadata ─────────────────────────────────────────────────
    ob["holoflow:facet"]    = True
    ob["holoflow:category"] = "stage-floor"

    # ── 11. orientation → +Y up, apply transforms, export GLB ────────────────
    ob.rotation_euler[0] = -np.pi / 2.0
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

    glb_path = bpy.path.abspath("//hofstadter_floor.glb")
    bpy.ops.export_scene.gltf(
        filepath      = glb_path,
        use_selection = True,
        export_draco_mesh_compression_enable = True,
        export_draco_mesh_compression_level  = 6,
        export_image_format = "WEBP",
        export_morph        = True,
        export_colors       = True,
    )
    print(f"[DONE] Object '{OBJ_NAME}' created, GLB → {glb_path}")


if __name__ == "__main__":
    main()
