"""
Hofstadter Butterfly — Bloch Electron in Rational Magnetic Flux
Douglas Hofstadter (1976) "Energy levels and wave functions of Bloch electrons
in rational and irrational magnetic fields."
Physical Review B 14(6):2239–2249. DOI 10.1103/PhysRevB.14.2239  (Public Domain)

TECHNIQUE
---------
A 2D square lattice electron in a perpendicular magnetic field Φ acquires
Peierls phases on y-direction hops. In the Landau gauge Aₓ=0, Aᵧ=Φx, and
after a Bloch ansatz along x, the Schrödinger equation collapses to the Harper
(1955) 1D recurrence on a q-site unit cell (α = p/q rational):

    Harper matrix H_Harper (q×q, cyclic tridiagonal):
      H[n,n]   = 2 cos(2π n α)        ← Peierls phase from Φ = p/q Φ₀
      H[n,n±1] = 1                     ← hopping amplitude t=1 (energy unit)
      H[0,q−1] = H[q−1,0] = 1         ← periodic BC (k_x Bloch phase absorbed)

The q eigenvalues of H_Harper lie in the tight-binding bandwidth [−4, 4].
Iterating over ALL rationals p/q with q ≤ Q_MAX (Farey sequence, gcd(p,q)=1,
0 ≤ p ≤ q) and accumulating eigenvalue counts into a 2D histogram over
(α, E) ∈ [0,1] × [−4.2, 4.2] produces the famous butterfly figure.

WHY LOG SCALING: a few α values (small q, e.g. α=1/2, 1/3) contribute many
coincident eigenvalues; log₁₀(1 + count) avoids those sparse peaks drowning
the intricate fractal substructure at large q.

PARAMETERS — edit here, not scattered through the body.
"""

import bpy
import bmesh
import math
import numpy as np

# ── spectrum sampling ──────────────────────────────────────────────────────────
N          = 128      # grid resolution (N×N height-field vertices)
Q_MAX_BASIS  = 100    # max flux-denominator for Basis shape key
Q_MAX_COARSE =  30    # coarser: shows main wings without fine branches
Q_MAX_DENSE  = 200    # denser: exposes fractal sub-bands (slower build)
E_MIN, E_MAX = -4.2, 4.2   # energy window (bandwidth ±4 + 5% margin)

# ── geometry ───────────────────────────────────────────────────────────────────
WORLD_SCALE = 4.0     # floor footprint ±WORLD_SCALE/2 in X and Y (metres)
Z_SCALE     = 0.35    # max peak height (metres)
COBALT      = (0.027, 0.141, 0.557, 1.0)
AMBER       = (0.980, 0.620, 0.050, 1.0)
MESH_NAME   = "Hofstadter_Butterfly"
OBJ_NAME    = "hofstadter_butterfly_floor"
OUT_BLEND   = "//hofstadter_butterfly_floor.blend"
OUT_GLB     = "//hofstadter_butterfly_floor.glb"


# ── core physics ───────────────────────────────────────────────────────────────

def harper_eigenvalues(p: int, q: int) -> np.ndarray:
    """
    Compute q eigenvalues of the q×q cyclic Harper matrix for flux α = p/q.
    Why eigvalsh not eig: H is real symmetric → LAPACK dsyev, ~3× faster.
    Why the cosine on the diagonal: Peierls substitution shifts site n energy
    by 2t cos(2π n p/q) once we fix the Bloch phase along x to 0.
    """
    n = np.arange(q, dtype=np.float64)
    diag = 2.0 * np.cos(2.0 * np.pi * n * p / q)
    off  = np.ones(q - 1)
    H = np.diag(diag) + np.diag(off, 1) + np.diag(off, -1)
    H[0, q - 1] = 1.0   # wrap: cyclic tridiagonal ≡ Bloch BC at k_y=0
    H[q - 1, 0] = 1.0
    return np.linalg.eigvalsh(H)


def butterfly_density(q_max: int,
                      alpha_range: tuple = (0.0, 1.0),
                      e_range: tuple = None) -> np.ndarray:
    """
    Accumulate the Hofstadter butterfly into an N×N density histogram.

    q_max      : largest denominator in the Farey sequence (controls density)
    alpha_range: (α_min, α_max) — use (0.4, 0.6) to zoom the centre
    e_range    : (E_min, E_max) — defaults to module-level E_MIN/E_MAX

    Returns log₁₀(1 + count) grid, shape (N, N), row=E bin, col=α bin.
    """
    if e_range is None:
        e_range = (E_MIN, E_MAX)

    grid = np.zeros((N, N), dtype=np.float64)
    a0, a1 = alpha_range
    e0, e1 = e_range

    # Precompute bin edges for fast clip-and-floor indexing
    inv_da = N / (a1 - a0)
    inv_de = N / (e1 - e0)

    for q in range(1, q_max + 1):
        for p in range(0, q + 1):
            if math.gcd(p, q) != 1:
                continue
            alpha = p / q
            if not (a0 <= alpha <= a1):
                continue

            eigs = harper_eigenvalues(p, q)

            # α column index (same for all eigenvalues of this Harper matrix)
            ia = int((alpha - a0) * inv_da)
            ia = min(ia, N - 1)

            # E row indices (vectorised)
            ie = ((eigs - e0) * inv_de).astype(np.int32)
            mask = (ie >= 0) & (ie < N)
            np.add.at(grid, (ie[mask], ia), 1)

    # log-compress so sparse high-multiplicity lines don't swamp fine structure
    return np.log10(1.0 + grid)


# ── mesh helpers ───────────────────────────────────────────────────────────────

def build_floor_mesh(bm: bmesh.types.BMesh, z_grid: np.ndarray) -> None:
    """
    Lay down N×N vertices on a WORLD_SCALE × WORLD_SCALE plane.
    z_grid[row, col] maps to vertex at (x=col, y=row) in grid space.
    Vertex ordering: col-major (x varies fastest) matches the colour assign below.
    """
    half = WORLD_SCALE / 2.0
    xs   = np.linspace(-half, half, N)
    ys   = np.linspace(-half, half, N)
    verts = []
    for row in range(N):
        for col in range(N):
            verts.append(bm.verts.new((xs[col], ys[row], float(z_grid[row, col]))))
    bm.verts.ensure_lookup_table()

    # CCW quad faces (as viewed from +Z)
    for row in range(N - 1):
        for col in range(N - 1):
            i = row * N + col
            bm.faces.new([verts[i], verts[i+1], verts[i+N+1], verts[i+N]])


def assign_colour_attribute(mesh, z_norm: np.ndarray) -> None:
    """
    Per-vertex FLOAT_COLOR attribute 'Col' — Cobalt→Amber ramp driven by
    normalised height. Why FLOAT_COLOR: keeps HDR headroom for Emission nodes.
    """
    attr = mesh.color_attributes.new(name="Col",
                                     type="FLOAT_COLOR",
                                     domain="POINT")
    z_max  = z_norm.max() if z_norm.max() > 0 else 1.0
    flat   = z_norm.ravel()           # row-major, matches vertex order above
    for i, t in enumerate(flat / z_max):
        r = COBALT[0] + t * (AMBER[0] - COBALT[0])
        g = COBALT[1] + t * (AMBER[1] - COBALT[1])
        b = COBALT[2] + t * (AMBER[2] - COBALT[2])
        attr.data[i].color = (r, g, b, 1.0)


def add_shape_key(obj, z_grid: np.ndarray, name: str) -> None:
    """Add a shape key by overwriting vertex Z coords from z_grid."""
    sk = obj.shape_key_add(name=name, from_mix=False)
    flat = z_grid.ravel()
    for i, v in enumerate(sk.data):
        co = list(v.co)
        co[2] = float(flat[i])
        v.co = co


# ── main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    print("Hofstadter butterfly: computing spectra …")

    # Basis: standard butterfly, Q_MAX=100
    z_basis   = butterfly_density(Q_MAX_BASIS)
    z_basis  /= z_basis.max() or 1.0
    z_basis  *= Z_SCALE

    # SK_Coarse: Q_MAX=30 — broad wing structure without branch detail
    print("  SK_Coarse (q≤30) …")
    z_coarse  = butterfly_density(Q_MAX_COARSE)
    z_coarse /= z_coarse.max() or 1.0
    z_coarse *= Z_SCALE

    # SK_Dense: Q_MAX=200 — sub-bands of sub-bands exposed
    print("  SK_Dense (q≤200) …")
    z_dense   = butterfly_density(Q_MAX_DENSE)
    z_dense  /= z_dense.max() or 1.0
    z_dense  *= Z_SCALE

    # SK_Central: α∈[0.4, 0.6] zoomed — self-similar Cantor structure visible
    # Why this range: the butterfly has C₂ symmetry about α=0.5; zooming
    # [0.4, 0.6] shows the fractal gaps of the central wing at full resolution.
    print("  SK_Central (α∈[0.4,0.6], q≤150) …")
    z_central  = butterfly_density(150, alpha_range=(0.4, 0.6))
    z_central /= z_central.max() or 1.0
    z_central *= Z_SCALE

    # ── build scene ──────────────────────────────────────────────────────────
    bpy.ops.wm.read_homefile(use_empty=True)
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    bm = bmesh.new()
    build_floor_mesh(bm, z_basis)

    mesh = bpy.data.meshes.new(MESH_NAME)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(OBJ_NAME, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Colour from Basis height (static, same for all shape keys by convention)
    assign_colour_attribute(mesh, z_basis)

    # Shape keys (Basis first, then alternatives)
    obj.shape_key_add(name="Basis",      from_mix=False)
    add_shape_key(obj, z_coarse,  "SK_Coarse")
    add_shape_key(obj, z_dense,   "SK_Dense")
    add_shape_key(obj, z_central, "SK_Central")

    # Material: vertex-colour → Principled BSDF + gentle Emission
    mat  = bpy.data.materials.new("Hofstadter_VC")
    mat.use_nodes = True
    nt   = mat.node_tree
    nt.nodes.clear()
    out  = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    emit = nt.nodes.new("ShaderNodeEmission")
    mix  = nt.nodes.new("ShaderNodeMixShader")
    vcol = nt.nodes.new("ShaderNodeVertexColor")
    vcol.layer_name = "Col"
    bsdf.inputs["Roughness"].default_value  = 0.30
    bsdf.inputs["Metallic"].default_value   = 0.15
    emit.inputs["Strength"].default_value   = 1.6
    mix.inputs["Fac"].default_value         = 0.35
    nt.links.new(vcol.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(vcol.outputs["Color"], emit.inputs["Color"])
    nt.links.new(bsdf.outputs["BSDF"],  mix.inputs[1])
    nt.links.new(emit.outputs["Emission"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"],  out.inputs["Surface"])
    mesh.materials.append(mat)

    # Holoflow metadata
    obj["holoflow:category"] = "stage-floor"
    obj["holoflow:facet"]    = True

    # Rotate −90° around X so the floor lies flat (+Y up export convention)
    import mathutils
    obj.rotation_euler[0] = -math.pi / 2.0
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Save .blend
    blend_path = bpy.path.abspath(OUT_BLEND)
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print("Saved  " + blend_path)

    # Export .glb (Draco 6, WebP textures, +Y up, morph targets)
    glb_path = bpy.path.abspath(OUT_GLB)
    bpy.ops.export_scene.gltf(
        filepath    = glb_path,
        export_format = "GLB",
        use_selection = False,
        export_draco_mesh_compression_enable = True,
        export_draco_mesh_compression_level  = 6,
        export_yup      = True,
        export_cameras  = False,
        export_lights   = False,
        export_morph    = True,
        export_colors   = True,
    )
    print("Export " + glb_path)


main()
