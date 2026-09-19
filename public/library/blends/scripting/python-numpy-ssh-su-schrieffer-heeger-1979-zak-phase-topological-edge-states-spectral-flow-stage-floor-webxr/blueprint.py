"""
SSH Model — Su–Schrieffer–Heeger 1979  (Spectral-Flow Stage Floor)
===================================================================
TECHNIQUE:
  The SSH model is a 1D tight-binding chain with two sites per unit cell
  (A and B sublattice) and alternating intracell (t₁) and intercell (t₂)
  hopping amplitudes.  When t₂ > t₁ the chain enters a topological phase
  characterised by a Zak phase of π and two symmetry-protected zero-energy
  edge states localised at open-chain boundaries — the paradigmatic example
  of bulk–edge correspondence.  This blueprint scans t₂ from 0.15 to 2.5
  (with t₁ = 1 fixed), diagonalises the 128-site Hamiltonian at each step,
  and maps the resulting spectral flow onto a 128×128 height-field stage floor.

MATHEMATICS:
  H = Σ_n [t₁(c†_{nA}c_{nB} + h.c.) + t₂(c†_{n+1,A}c_{nB} + h.c.)]
  Bloch Hamiltonian: h(k) = d(k)·σ
    d(k) = (t₁ + t₂ cos k,  t₂ sin k,  0)
  Bands: E±(k) = ±|d(k)| = ±√(t₁² + t₂² + 2t₁t₂ cos k)
  Band gap: Δ = 2|t₁ − t₂|  at k = π  (closes at t₂ = t₁)
  Zak phase: γ = ∮_{BZ} ⟨u_k|i∂_k|u_k⟩ dk
    γ = 0   if t₁ > t₂  (trivial — d-vector does not wind origin)
    γ = π   if t₂ > t₁  (topological — d-vector winds once)
  Winding number: ν = θ(t₂ − t₁) ∈ {0, 1}
  Edge state (open BC, topological phase):
    ψ_L(n) ∝ (−t₁/t₂)^n on A sites  (left edge, exact E = 0)
    ψ_R(n) ∝ (−t₁/t₂)^(N−1−n) on B sites  (right edge)
    Localisation length: ξ = 1 / |ln(t₁/t₂)| unit cells

NUMERICAL METHOD — direct diagonalisation with numpy.linalg.eigh:
  Each 128×128 real symmetric matrix is diagonalised in O(N²) for the
  tridiagonal case (LAPACK dsbtrd + dsbev internally).  128 calls total;
  each takes < 1 ms on any modern CPU.
  WHY eigh over eig: eigh exploits symmetry (H = H^T), guarantees real
  eigenvalues, and returns eigenvectors sorted ascending — no post-sort needed.

MESH:
  128 rows (parameter axis, t₂ increasing) × 128 columns (eigenstate index,
  ascending energy).  z = normalised eigenvalue.  Vertex colour = edge weight
  (cobalt: bulk state; amber: edge/topological state, w > 0.33).

SHAPE KEYS:
  Basis      open BC — zero modes thread gap for t₂ > t₁
  SK_Periodic periodic BC — zero modes absent, gap closes cleanly at t₂ = t₁
  SK_NNN     open + t₃ = 0.30 (NNN hopping breaks sublattice symmetry)
  SK_SymBreak open + δ = 0.40 staggered onsite (chiral symmetry broken, edge states gapped)

SOURCES (permissive):
  Su WP, Schrieffer JR, Heeger AJ (1979) Phys Rev Lett 42:1698–1701
    — original SSH chain, equations public domain (>40 yr, academic)
  Zak J (1989) Phys Rev Lett 62:2747–2750
    — Zak/Berry phase for Bloch bands, public domain
  Asbóth JK, Oroszlány L, Pályi A (2016) arXiv:1509.02295  CC-BY 4.0
    "A Short Course on Topological Insulators"
    GitHub: https://github.com/topocm/topocm_content  (CC0)
  NumPy — BSD-3-Clause  https://numpy.org
"""

import bpy, numpy as np, mathutils

# ── Named constants ──────────────────────────────────────────────────────────
N_CELLS      = 64          # unit cells  (A+B pairs)
N_SITES      = 128         # total sites = 2 × N_CELLS
T1           = 1.0         # intracell hopping (fixed)
T2_MIN       = 0.15        # parameter scan start
T2_MAX       = 2.50        # parameter scan end
N_PARAM      = N_SITES     # 128 parameter rows
T3_NNN       = 0.30        # NNN hopping for SK_NNN (same sublattice)
DELTA_SYM    = 0.40        # staggered onsite for SK_SymBreak (±δ on A/B)
WORLD_SCALE  = 4.0         # mesh half-width (m)
HEIGHT_SCALE = 0.70        # energy → z amplitude (m)
E_CLIP       = 3.60        # clip energy for normalisation (≥ T1 + T2_MAX)
OBJ_NAME     = "ssh_spectrum_floor"
ATTR_NAME    = "SSH_Eig"   # vertex colour attribute
COBALT       = (0.030, 0.140, 0.560)
AMBER        = (1.000, 0.650, 0.000)


# ── Hamiltonian builders ─────────────────────────────────────────────────────

def _h_open(t2: float) -> np.ndarray:
    """128×128 tridiagonal SSH Hamiltonian, open boundary conditions."""
    H = np.zeros((N_SITES, N_SITES))
    for n in range(N_CELLS):
        a, b = 2*n, 2*n + 1
        H[a, b] = H[b, a] = T1
        if n < N_CELLS - 1:
            # intercell bond: last B of cell n → first A of cell n+1
            H[b, b+1] = H[b+1, b] = t2
    return H


def _h_periodic(t2: float) -> np.ndarray:
    """Close the SSH chain with a periodic intercell bond (site N−1 → site 0)."""
    H = _h_open(t2)
    H[N_SITES-1, 0] = H[0, N_SITES-1] = t2
    return H


def _h_nnn(t2: float) -> np.ndarray:
    """SSH + next-nearest-neighbour hopping t₃ on both sublattices.
    Connects same-sublattice sites (A↔A, B↔B) two sites apart.
    WHY: breaks the sublattice/chiral symmetry {H, Γ}=0 while preserving
    inversion, so it shifts edge-state energy away from exactly zero."""
    H = _h_open(t2)
    for i in range(N_SITES - 2):
        H[i, i+2] = H[i+2, i] = T3_NNN
    return H


def _h_sym_break(t2: float) -> np.ndarray:
    """SSH + staggered onsite energy ±δ (A sites +δ, B sites −δ).
    WHY: this directly gaps the chiral-symmetric edge states because the
    onsite term Σ_n δ(c†_{nA}c_{nA} − c†_{nB}c_{nB}) does not commute with
    the chiral operator Γ = diag(+1,−1,+1,−1,...), so topological
    protection is lifted and the zero modes acquire energy ≈ ±δ."""
    H = _h_open(t2)
    for n in range(N_CELLS):
        H[2*n,   2*n  ] = +DELTA_SYM
        H[2*n+1, 2*n+1] = -DELTA_SYM
    return H


# ── Spectral flow scan ───────────────────────────────────────────────────────

def _scan(ham_fn) -> tuple:
    """
    Sweep t₂ from T2_MIN to T2_MAX in N_PARAM steps.
    Returns:
      E  — shape (N_PARAM, N_SITES), energy eigenvalues sorted ascending
      W  — shape (N_PARAM, N_SITES), edge weight for each eigenstate
    Edge weight = total probability on the 4 boundary sites (2 per edge).
    WHY 4 sites: the two edge states span 2 sites each in the topological
    phase; summing over both ensures the weight is near 1.0 for edge states
    regardless of their exact decay profile.
    """
    t2_vals = np.linspace(T2_MIN, T2_MAX, N_PARAM)
    E = np.empty((N_PARAM, N_SITES))
    W = np.empty((N_PARAM, N_SITES))
    for i, t2 in enumerate(t2_vals):
        evals, evecs = np.linalg.eigh(ham_fn(t2))
        E[i] = evals
        W[i] = evecs[0]**2 + evecs[1]**2 + evecs[-2]**2 + evecs[-1]**2
    return E, W


def _norm_z(E: np.ndarray) -> np.ndarray:
    """Map E ∈ [−E_CLIP, +E_CLIP] → z ∈ [0, HEIGHT_SCALE].
    The mid-gap region (E ≈ 0) maps to z ≈ HEIGHT_SCALE/2."""
    return (np.clip(E, -E_CLIP, E_CLIP) + E_CLIP) / (2.0 * E_CLIP) * HEIGHT_SCALE


def _edge_col(W: np.ndarray) -> np.ndarray:
    """Edge weight W → RGB.  W = 0 → cobalt; W ≥ 0.33 → full amber."""
    t  = np.clip(W * 3.0, 0.0, 1.0)[..., np.newaxis]   # scalar → (N,N,1)
    c0 = np.array(COBALT, dtype=np.float32)
    c1 = np.array(AMBER,  dtype=np.float32)
    return (c0 + t * (c1 - c0)).astype(np.float32)       # (N_PARAM, N_SITES, 3)


# ── Mesh construction ────────────────────────────────────────────────────────

def _build_mesh(z_grid: np.ndarray, col_grid: np.ndarray) -> bpy.types.Object:
    """
    Build 128×128 quad grid.
    x-axis = eigenstate index (col),  y-axis = t₂/t₁ parameter (row),
    z      = normalised energy.
    """
    xs = np.linspace(-WORLD_SCALE, WORLD_SCALE, N_SITES)   # eigenstate axis
    ys = np.linspace(-WORLD_SCALE, WORLD_SCALE, N_PARAM)   # parameter axis

    verts, faces = [], []
    for i in range(N_PARAM):
        for j in range(N_SITES):
            verts.append((float(xs[j]), float(ys[i]), float(z_grid[i, j])))
    for i in range(N_PARAM - 1):
        for j in range(N_SITES - 1):
            a = i * N_SITES + j
            faces.append((a, a+1, a+N_SITES+1, a+N_SITES))  # CCW

    me  = bpy.data.meshes.new(OBJ_NAME)
    obj = bpy.data.objects.new(OBJ_NAME, me)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    me.from_pydata(verts, [], faces)
    me.update()
    obj.shape_key_add(name="Basis", from_mix=False)

    attr = me.color_attributes.new(ATTR_NAME, "FLOAT_COLOR", "POINT")
    flat = col_grid.reshape(-1, 3)
    rgba = []
    for r, g, b in flat:
        rgba.extend([float(r), float(g), float(b), 1.0])
    attr.data.foreach_set("color", rgba)

    return obj


def _add_sk(obj: bpy.types.Object, z_grid: np.ndarray, name: str) -> None:
    """Add shape key; update only z-coordinate from new spectral scan."""
    sk = obj.shape_key_add(name=name, from_mix=False)
    for i in range(N_PARAM):
        for j in range(N_SITES):
            sk.data[i * N_SITES + j].co[2] = float(z_grid[i, j])


# ── Material ─────────────────────────────────────────────────────────────────

def _add_material(obj: bpy.types.Object) -> None:
    mat  = bpy.data.materials.new("SSH_Spec_Mat")
    mat.use_nodes = True
    nt   = mat.node_tree
    nt.nodes.clear()
    attr = nt.nodes.new("ShaderNodeAttribute");  attr.attribute_name = ATTR_NAME
    prin = nt.nodes.new("ShaderNodeBsdfPrincipled")
    emit = nt.nodes.new("ShaderNodeEmission");   emit.inputs["Strength"].default_value = 1.5
    mix  = nt.nodes.new("ShaderNodeMixShader");  mix.inputs["Fac"].default_value = 0.30
    out  = nt.nodes.new("ShaderNodeOutputMaterial")
    prin.inputs["Metallic"].default_value  = 0.15
    prin.inputs["Roughness"].default_value = 0.30
    lk = nt.links.new
    lk(attr.outputs["Color"], prin.inputs["Base Color"])
    lk(attr.outputs["Color"], emit.inputs["Color"])
    lk(emit.outputs["Emission"], mix.inputs[1])
    lk(prin.outputs["BSDF"],     mix.inputs[2])
    lk(mix.outputs["Shader"],    out.inputs["Surface"])
    obj.data.materials.append(mat)


# ── Export ───────────────────────────────────────────────────────────────────

def _export_glb(path: str) -> None:
    for o in bpy.context.scene.objects:
        o.select_set(o.name == OBJ_NAME)
    bpy.ops.export_scene.gltf(
        filepath=path, export_format="GLB", use_selection=True,
        export_yup=True, export_apply=True,
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_image_format="WEBP",
        export_morph=True, export_colors=True,
    )


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    import pathlib
    here = pathlib.Path(__file__).parent

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    print("[SSH] scanning open BC (basis) …")
    E_open, W_open = _scan(_h_open)

    print("[SSH] scanning periodic BC …")
    E_per, _       = _scan(_h_periodic)

    print("[SSH] scanning NNN hopping …")
    E_nnn, _       = _scan(_h_nnn)

    print("[SSH] scanning symmetry-broken …")
    E_sym, _       = _scan(_h_sym_break)

    obj = _build_mesh(_norm_z(E_open), _edge_col(W_open))
    _add_sk(obj, _norm_z(E_per), "SK_Periodic")
    _add_sk(obj, _norm_z(E_nnn), "SK_NNN")
    _add_sk(obj, _norm_z(E_sym), "SK_SymBreak")
    _add_material(obj)

    # rotate to +Y-up stage floor (holoflow exporter convention)
    obj.rotation_euler = mathutils.Euler((-1.5707963, 0, 0), "XYZ")
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(rotation=True)

    obj["holoflow:facet"]    = True
    obj["holoflow:category"] = "stage-floor"

    bpy.ops.wm.save_as_mainfile(filepath=str(here / "ssh_spectrum_floor.blend"))
    _export_glb(str(here / "ssh_spectrum_floor.glb"))
    print("[SSH] done — ssh_spectrum_floor.blend + .glb written.")


main()
