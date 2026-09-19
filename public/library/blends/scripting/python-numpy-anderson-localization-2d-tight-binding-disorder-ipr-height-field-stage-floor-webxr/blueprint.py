"""
Anderson Localisation — 2-D Tight-Binding with Diagonal Disorder
Philip W. Anderson (1958) "Absence of Diffusion in Certain Random Lattices"
Physical Review 109(5):1492–1505. DOI 10.1103/PhysRev.109.1492  (Public Domain)

TECHNIQUE
---------
The 2D Anderson model places a quantum particle on an N×N square lattice.
Electrons hop between nearest-neighbour sites with amplitude -T_HOP; each site
also carries a random on-site energy ε_i drawn uniformly from [-W/2, W/2].
Abrahams, Anderson, Licciardello & Ramakrishnan (1979) proved that in 2D all
states are Anderson-localised for ANY W > 0, in contrast to 3D where a
mobility edge separates extended and localised regimes.

Full exact diagonalisation via numpy.linalg.eigh yields all N² eigenvalues and
eigenvectors. The eigenstate nearest the band centre E = 0 (most
delocalised in the weak-disorder limit) is taken as the height field:
Z(i, j) = |ψ(i, j)|² / max(|ψ|²) × HEIGHT_SCALE.

The Inverse Participation Ratio IPR_k = Σ_i |ψ_k(i)|⁴ measures localisation:
  IPR → 1/N²   (extended, Bloch wave)
  IPR → 1      (perfectly localised, delta function)

Four shape keys show the same 64×64 lattice under increasing disorder strength,
each with an independent random realisation (different seed) so the viewer sees
a genuine cross-section of the disorder ensemble.

PARAMETERS — edit these constants; do not scatter magic numbers in the code.
"""

import bpy
import bmesh
import numpy as np

# ── lattice ────────────────────────────────────────────────────────────────────
N             = 64      # N×N lattice → N²=4 096 sites; Hamiltonian is 4096×4096
T_HOP         = 1.0     # nearest-neighbour hopping amplitude (sets energy scale)

# Disorder strengths for each shape key. Localisation length ξ/a ≈ exp(πT/W) in 2D.
W_BASIS  = 0.50   # Basis     : ξ/a ≈ 500 >> N=64 — looks extended
W_MED    = 2.00   # SK_Medium : ξ/a ≈ 5  — partially localised
W_STR    = 5.00   # SK_Strong : ξ/a ≈ 1.4 — clearly localised
W_MAXIPR = 8.00   # SK_MaxIPR : highest-IPR (most localised) state of the spectrum

SEED_BASIS  = 7919   # prime seeds → reproducible but independent realisations
SEED_MED    = 7927
SEED_STR    = 7933
SEED_MAXIPR = 7951

# ── geometry / export ─────────────────────────────────────────────────────────
WORLD_SCALE  = 2.0    # floor footprint, metres (−1..+1 in X and Y)
HEIGHT_SCALE = 0.25   # Z-height at peak |ψ|², metres
COBALT       = (0.020, 0.180, 0.780, 1.0)
AMBER        = (1.000, 0.750, 0.050, 1.0)
MESH_NAME    = "Anderson_Floor"
OBJ_NAME     = "anderson_localization_floor"
OUT_BLEND    = "//anderson_localization_floor.blend"
OUT_GLB      = "//anderson_localization_floor.glb"


# ── helpers ───────────────────────────────────────────────────────────────────

def build_hamiltonian(N, T_HOP, W, seed):
    """Dense N²×N² tight-binding Hamiltonian with random on-site disorder."""
    n2  = N * N
    rng = np.random.default_rng(seed)
    H   = np.zeros((n2, n2), dtype=np.float64)

    # Diagonal: uniform disorder ε_i ∈ [-W/2, W/2]
    np.fill_diagonal(H, rng.uniform(-W / 2.0, W / 2.0, n2))

    # Off-diagonal: hopping. Enumerate ALL directed bonds (each undirected bond
    # appears once as a→b and once as b→a, giving the correct symmetric matrix).
    idx = np.arange(n2)
    row = idx // N
    col = idx % N

    # x-direction bonds: site → right neighbour (periodic)
    bx = row * N + (col + 1) % N  # right neighbours; unique for each site
    H[idx, bx] -= T_HOP
    H[bx, idx] -= T_HOP

    # y-direction bonds: site → bottom neighbour (periodic)
    by = ((row + 1) % N) * N + col  # down neighbours; unique for each site
    H[idx, by] -= T_HOP
    H[by, idx] -= T_HOP

    return H


def diagonalise(H):
    """Return eigenvalues and normalised eigenvectors (columns) via LAPACK dsyevd."""
    # eigh exploits Hermitian symmetry → 2× faster and more accurate than eig.
    E, psi = np.linalg.eigh(H)
    return E, psi  # psi[:, k] = k-th eigenstate, already L²-normalised


def eigenstate_near_centre(E, psi):
    """Pick eigenvector closest to band centre E = 0."""
    k = int(np.argmin(np.abs(E)))
    return psi[:, k].reshape(N, N)  # (N, N) spatial wavefunction


def eigenstate_max_ipr(psi):
    """Pick eigenvector with highest IPR = Σ|ψ|⁴ (most localised)."""
    # Columns of psi are already L²-normalised, so IPR = Σ|ψ_k|⁴
    ipr = np.sum(psi ** 4, axis=0)  # shape (n2,)
    k   = int(np.argmax(ipr))
    return psi[:, k].reshape(N, N)


def wavefunction_to_z(psi2d):
    """Normalise |ψ|² to [0, 1] then scale to HEIGHT_SCALE metres."""
    amp = np.abs(psi2d) ** 2
    mx  = amp.max()
    if mx > 0:
        amp /= mx
    return amp * HEIGHT_SCALE


def build_floor_mesh(bm, z_grid, name):
    """Populate a BMesh with an N×N quad grid at heights z_grid (N×N array).

    Vertices are laid out in row-major order: vert index = row*N + col.
    Holoflow convention: +Y-up at export, faces outward (normals +Z).
    """
    spacing = WORLD_SCALE / (N - 1)
    half    = WORLD_SCALE / 2.0

    verts = []
    for row in range(N):
        for col in range(N):
            x = col * spacing - half
            y = row * spacing - half
            z = float(z_grid[row, col])
            verts.append(bm.verts.new((x, y, z)))

    bm.verts.ensure_lookup_table()

    for row in range(N - 1):
        for col in range(N - 1):
            v0 = verts[row * N + col]
            v1 = verts[row * N + col + 1]
            v2 = verts[(row + 1) * N + col + 1]
            v3 = verts[(row + 1) * N + col]
            bm.faces.new((v0, v1, v2, v3))

    bm.normal_update()


def assign_colour_attribute(mesh, z_grid):
    """Store FLOAT_COLOR attribute 'Col' mapped cobalt → amber by |ψ|² height."""
    col_attr = mesh.color_attributes.new(
        name="Col", type="FLOAT_COLOR", domain="POINT"
    )
    flat = z_grid.ravel() / HEIGHT_SCALE  # re-normalise to [0, 1]
    c_data = col_attr.data
    for i in range(N * N):
        t = float(flat[i])
        c_data[i].color = (
            COBALT[0] + t * (AMBER[0] - COBALT[0]),
            COBALT[1] + t * (AMBER[1] - COBALT[1]),
            COBALT[2] + t * (AMBER[2] - COBALT[2]),
            1.0,
        )


def add_shape_key(obj, z_grid, key_name):
    """Add a shape key with vertex positions derived from z_grid."""
    sk = obj.shape_key_add(name=key_name, from_mix=False)
    spacing = WORLD_SCALE / (N - 1)
    half    = WORLD_SCALE / 2.0
    data    = sk.data
    for row in range(N):
        for col in range(N):
            idx = row * N + col
            data[idx].co[0] = col * spacing - half
            data[idx].co[1] = row * spacing - half
            data[idx].co[2] = float(z_grid[row, col])


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    print("Anderson localisation: diagonalising W=%.2f …" % W_BASIS)
    H_b = build_hamiltonian(N, T_HOP, W_BASIS,  SEED_BASIS)
    E_b, psi_b = diagonalise(H_b)
    z_basis  = wavefunction_to_z(eigenstate_near_centre(E_b, psi_b))

    print("Anderson localisation: diagonalising W=%.2f …" % W_MED)
    H_m = build_hamiltonian(N, T_HOP, W_MED,    SEED_MED)
    E_m, psi_m = diagonalise(H_m)
    z_med    = wavefunction_to_z(eigenstate_near_centre(E_m, psi_m))

    print("Anderson localisation: diagonalising W=%.2f …" % W_STR)
    H_s = build_hamiltonian(N, T_HOP, W_STR,    SEED_STR)
    E_s, psi_s = diagonalise(H_s)
    z_strong = wavefunction_to_z(eigenstate_near_centre(E_s, psi_s))

    print("Anderson localisation: diagonalising W=%.2f for max-IPR …" % W_MAXIPR)
    H_x = build_hamiltonian(N, T_HOP, W_MAXIPR, SEED_MAXIPR)
    _, psi_x = diagonalise(H_x)
    z_maxipr = wavefunction_to_z(eigenstate_max_ipr(psi_x))

    # ── build mesh ────────────────────────────────────────────────────────────
    bpy.ops.wm.read_homefile(use_empty=True)
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    bm = bmesh.new()
    build_floor_mesh(bm, z_basis, MESH_NAME)

    mesh = bpy.data.meshes.new(MESH_NAME)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(OBJ_NAME, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    assign_colour_attribute(mesh, z_basis)

    # Shape keys
    obj.shape_key_add(name="Basis", from_mix=False)  # keys the existing geometry
    add_shape_key(obj, z_med,    "SK_Medium")         # W=2.0 partial localisation
    add_shape_key(obj, z_strong, "SK_Strong")         # W=5.0 clear localisation
    add_shape_key(obj, z_maxipr, "SK_MaxIPR")         # W=8.0 highest-IPR state

    # Material (Vertex Color)
    mat = bpy.data.materials.new("Anderson_VC")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out   = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf  = nt.nodes.new("ShaderNodeBsdfPrincipled")
    vcol  = nt.nodes.new("ShaderNodeVertexColor")
    vcol.layer_name = "Col"
    nt.links.new(vcol.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(bsdf.outputs["BSDF"],  out.inputs["Surface"])
    bsdf.inputs["Roughness"].default_value  = 0.6
    bsdf.inputs["Metallic"].default_value   = 0.1
    mesh.materials.append(mat)

    # Apply transforms before export (Holoflow convention)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Save .blend
    blend_path = bpy.path.abspath(OUT_BLEND)
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print("Saved  " + blend_path)

    # Export .glb (Draco level 6, no cameras/lights, +Y up)
    glb_path = bpy.path.abspath(OUT_GLB)
    bpy.ops.export_scene.gltf(
        filepath          = glb_path,
        export_format     = "GLB",
        use_selection     = False,
        export_draco_mesh_compression_enable = True,
        export_draco_mesh_compression_level  = 6,
        export_yup        = True,
        export_cameras    = False,
        export_lights     = False,
        export_morph      = True,
        export_colors     = True,
    )
    print("Export " + glb_path)


main()
