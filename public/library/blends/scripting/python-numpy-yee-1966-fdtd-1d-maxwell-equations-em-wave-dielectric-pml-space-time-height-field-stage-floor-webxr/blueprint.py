"""
1D FDTD Maxwell Equations — Yee 1966 Staggered-Grid EM Wave Simulation
K. S. Yee, "Numerical solution of initial boundary value problems involving
Maxwell's equations in isotropic media," IEEE Trans. Antennas Propagat.
14(3):302–307, 1966. doi:10.1109/TAP.1966.1138693 (Public Domain — >50 years)

TECHNIQUE
---------
The Yee 1966 staggered-grid FDTD scheme solves Maxwell's equations for a 1D
TM wave (E along z, H along y, propagation along x) by interleaving field
updates at half-cell offsets in space and half-step offsets in time:

    H_y^{n+½}[j+½] = da[j] H_y^{n−½}[j+½]  −  db[j] (E_z^n[j+1] − E_z^n[j])
    E_z^{n+1}[j]   = ca[j] E_z^n[j]          +  cb[j] (H_y^{n+½}[j+½] − H_y^{n+½}[j−½])

The signs follow from Faraday (∂H_y/∂t = −(1/μ) ∂E_z/∂x) and Ampere
(∂E_z/∂t = +(1/ε) ∂H_y/∂x).  Coefficients (ca, cb, da, db) fold in both the
local permittivity ε_r and the CPML conductivity σ; they reduce to unity and
DT/DX in free space.  CFL stability requires DT ≤ DX/c_max; DT = 0.45
(CFL = 0.45) gives a comfortable margin with c = 1 in normalised units.

WHY STAGGERED GRID: aligning E at integer positions and H at half-integer
positions ensures that the finite-difference approximation to ∂E_z/∂x is
centred exactly at the H nodes and vice versa, making the scheme second-order
accurate in both space and time with no additional cross terms.

SPACE–TIME HEIGHT FIELD: each scenario stores NT_STORE = 128 E_z snapshots
at evenly spaced intervals across NT_RUN time steps.  The resulting
(128 time) × (128 space) matrix becomes a 128 × 128 quad-mesh stage floor:
x-axis = space, y-axis = time, height = 0.5·(1 + E_z/E_max).

COLOUR: |E_z| / E_max mapped cobalt → amber.  Cobalt = silent background;
amber = peak field amplitude.

FOUR SCENARIOS (shape keys):
  Basis       — free space, PEC hard walls; pulse splits into left/right copies
  SK_Dielectric — ε_r=4 half-space at x=64; Fresnel r=−⅓ t=⅔ visible
  SK_Cavity   — interior PEC walls at x=16, x=112; standing-wave resonance
  SK_PML      — 12-cell CPML absorbing layers; pulse absorbed with no echo
"""

import bpy
import bmesh
import math
import numpy as np

# ── parameters ─────────────────────────────────────────────────────────────────
NX          = 128       # spatial cells
NT_STORE    = 128       # snapshots → rows of height field
DT          = 0.45      # normalised time step (CFL = 0.45)
DX          = 1.0       # normalised spatial step
SOURCE_POS  = 20        # soft-source node (Basis / Dielectric / PML)
T0          = 40.0      # Gaussian source peak (time steps)
SIGMA_T     = 15.0      # source temporal half-width (time steps)
EPS_R_DIEL  = 4.0       # dielectric half-space permittivity
CAV_LEFT    = 16        # cavity PEC wall (left)
CAV_RIGHT   = 112       # cavity PEC wall (right)
CAV_SOURCE  = 40        # cavity source (offset from left wall for mode coupling)
PML_CELLS   = 12        # CPML layer depth (cells)
SIGMA_MAX   = 0.8       # peak CPML conductivity
NT_FREE     = 256       # steps: Basis / SK_Dielectric / SK_PML
NT_CAV      = 512       # steps: SK_Cavity (longer to show resonance build-up)

WORLD_SCALE = 4.0
Z_SCALE     = 0.35
COBALT      = (0.027, 0.141, 0.557, 1.0)
AMBER       = (0.980, 0.620, 0.050, 1.0)
MESH_NAME   = "FDTD_Efield"
OBJ_NAME    = "fdtd_field_floor"
OUT_BLEND   = "//fdtd_field_floor.blend"
OUT_GLB     = "//fdtd_field_floor.glb"


# ── CPML conductivity profiles ────────────────────────────────────────────────

def build_cpml_sigma() -> tuple[np.ndarray, np.ndarray]:
    """
    Parabolic CPML conductivity: σ = σ_max · (dist_from_boundary/PML_CELLS)²
    The matching condition σ_H/μ = σ_E/ε requires σ_H = σ_E in free space,
    so the same profile is used for both arrays (evaluated at staggered nodes).
    """
    sigma_e = np.zeros(NX, dtype=np.float64)
    sigma_h = np.zeros(NX - 1, dtype=np.float64)
    for i in range(PML_CELLS):
        dist_e = (PML_CELLS - i) / PML_CELLS          # E at integer position
        dist_h = (PML_CELLS - i - 0.5) / PML_CELLS    # H at half-integer
        sigma_e[i]           = SIGMA_MAX * dist_e ** 2
        sigma_e[NX - 1 - i]  = SIGMA_MAX * dist_e ** 2
        sigma_h[i]           = SIGMA_MAX * max(0.0, dist_h) ** 2
        sigma_h[NX - 2 - i]  = SIGMA_MAX * max(0.0, dist_h) ** 2
    return sigma_e, sigma_h


def build_coeffs(
    eps_r:   np.ndarray,   # [NX]
    sigma_e: np.ndarray,   # [NX]
    sigma_h: np.ndarray,   # [NX-1]
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """CPML update coefficients (Taflove & Hagness 2005, eqs 7.61–7.64)."""
    # E coefficients absorb both ε_r and CPML conductivity
    denom_e = 2.0 * eps_r + sigma_e * DT
    ca = (2.0 * eps_r - sigma_e * DT) / denom_e   # [NX]
    cb = (2.0 * DT / DX) / denom_e                # [NX]
    # H coefficients (μ = 1 everywhere in normalised units)
    denom_h = 2.0 + sigma_h * DT
    da = (2.0 - sigma_h * DT) / denom_h           # [NX-1]
    db = (2.0 * DT / DX) / denom_h                # [NX-1]
    return ca, cb, da, db


# ── 1D FDTD engine ────────────────────────────────────────────────────────────

def run_fdtd(
    eps_r:      np.ndarray,
    sigma_e:    np.ndarray,
    sigma_h:    np.ndarray,
    source_pos: int,
    nt_run:     int,
    pec_nodes:  list | None = None,
) -> np.ndarray:
    """
    Simulate 1D FDTD; return (NT_STORE, NX) E_z snapshot array.
    Domain boundaries Ez[0] and Ez[NX-1] are PEC by construction (always 0).
    Additional interior PEC walls can be enforced via pec_nodes.
    """
    ca, cb, da, db = build_coeffs(eps_r, sigma_e, sigma_h)
    Ez = np.zeros(NX, dtype=np.float64)
    Hy = np.zeros(NX - 1, dtype=np.float64)

    store_every = max(1, nt_run // NT_STORE)
    snaps       = np.zeros((NT_STORE, NX), dtype=np.float64)
    snap_idx    = 0

    for t in range(nt_run):
        # H update — Faraday's law: ΔH_y = −(DT/DX) ΔE_z across each cell
        Hy = da * Hy - db * (Ez[1:] - Ez[:-1])

        # Soft source injection into E_z (adds to, not replaces, field value)
        Ez[source_pos] += math.exp(-0.5 * ((t - T0) / SIGMA_T) ** 2)

        # E update — Ampere's law: ΔE_z = +(DT/DX/ε) ΔH_y across each edge
        # Ez[0] and Ez[NX-1] stay at zero (PEC domain walls)
        Ez[1:-1] = ca[1:-1] * Ez[1:-1] + cb[1:-1] * (Hy[1:] - Hy[:-1])

        # Interior PEC walls (e.g. cavity end-caps)
        if pec_nodes:
            for j in pec_nodes:
                Ez[j] = 0.0

        if t % store_every == 0 and snap_idx < NT_STORE:
            snaps[snap_idx] = Ez.copy()
            snap_idx += 1

    return snaps


# ── scenario runners ──────────────────────────────────────────────────────────

def sim_free_space() -> np.ndarray:
    eps_r   = np.ones(NX)
    sigma_e = np.zeros(NX)
    sigma_h = np.zeros(NX - 1)
    return run_fdtd(eps_r, sigma_e, sigma_h, SOURCE_POS, NT_FREE)


def sim_dielectric() -> np.ndarray:
    """Right half-space (x ≥ 64) has ε_r = 4; Fresnel r = −⅓, t = ⅔."""
    eps_r           = np.ones(NX)
    eps_r[NX // 2:] = EPS_R_DIEL
    return run_fdtd(eps_r, np.zeros(NX), np.zeros(NX - 1), SOURCE_POS, NT_FREE)


def sim_cavity() -> np.ndarray:
    """Standing-wave resonance between PEC walls at CAV_LEFT and CAV_RIGHT."""
    eps_r = np.ones(NX)
    return run_fdtd(
        eps_r, np.zeros(NX), np.zeros(NX - 1),
        CAV_SOURCE, NT_CAV,
        pec_nodes=[CAV_LEFT, CAV_RIGHT],
    )


def sim_pml() -> np.ndarray:
    """CPML absorbing boundaries; no reflected echo from domain edges."""
    eps_r            = np.ones(NX)
    sigma_e, sigma_h = build_cpml_sigma()
    return run_fdtd(eps_r, sigma_e, sigma_h, SOURCE_POS, NT_FREE)


# ── mesh builder ──────────────────────────────────────────────────────────────

def normalise(field: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    e_max = np.max(np.abs(field))
    if e_max < 1e-30:
        return np.full_like(field, 0.5), np.zeros_like(field)
    height = 0.5 + 0.5 * field / e_max    # [-e_max, e_max] → [0, 1]
    colour = np.abs(field) / e_max
    return height.astype(np.float32), colour.astype(np.float32)


def build_mesh(
    basis_field:  np.ndarray,
    shape_fields: list,
) -> bpy.types.Object:
    h_basis, c_basis = normalise(basis_field)

    me = bpy.data.meshes.new(MESH_NAME)
    ob = bpy.data.objects.new(OBJ_NAME, me)
    bpy.context.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob

    bm = bmesh.new()
    cell_w = WORLD_SCALE / (NX - 1)
    cell_h = WORLD_SCALE / (NT_STORE - 1)
    x_off  = -WORLD_SCALE / 2.0
    y_off  = -WORLD_SCALE / 2.0

    # Rows = time (j), Columns = space (i)
    verts = []
    for j in range(NT_STORE):
        for i in range(NX):
            verts.append(bm.verts.new((
                x_off + i * cell_w,
                y_off + j * cell_h,
                float(h_basis[j, i]) * Z_SCALE,
            )))
    bm.verts.ensure_lookup_table()

    for j in range(NT_STORE - 1):
        for i in range(NX - 1):
            bm.faces.new((
                verts[ j      * NX + i    ],
                verts[ j      * NX + i + 1],
                verts[(j + 1) * NX + i + 1],
                verts[(j + 1) * NX + i    ],
            ))

    bm.to_mesh(me)
    bm.free()

    # Vertex colour (cobalt → amber by field amplitude)
    col_attr = me.attributes.new("Col", "FLOAT_COLOR", "POINT")
    flat = c_basis.ravel()
    colours = []
    for v in flat:
        colours.extend([
            COBALT[0] + v * (AMBER[0] - COBALT[0]),
            COBALT[1] + v * (AMBER[1] - COBALT[1]),
            COBALT[2] + v * (AMBER[2] - COBALT[2]),
            1.0,
        ])
    col_attr.data.foreach_set("color", colours)

    # Basis shape key (mesh already at correct z values)
    ob.shape_key_add(name="Basis", from_mix=False)

    # Additional shape keys
    for sk_name, sk_field in shape_fields:
        sk    = ob.shape_key_add(name=sk_name, from_mix=False)
        h_sk, _ = normalise(sk_field)
        coords = []
        for j in range(NT_STORE):
            for i in range(NX):
                coords.extend([
                    x_off + i * cell_w,
                    y_off + j * cell_h,
                    float(h_sk[j, i]) * Z_SCALE,
                ])
        sk.data.foreach_set("co", coords)

    # Material
    mat   = bpy.data.materials.new(MESH_NAME + "_mat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    attr  = nodes.new("ShaderNodeAttribute")
    attr.attribute_name = "Col"
    bsdf  = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Emission Strength"].default_value = 1.4
    out   = nodes.new("ShaderNodeOutputMaterial")
    links.new(attr.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(attr.outputs["Color"], bsdf.inputs["Emission Color"])
    links.new(bsdf.outputs["BSDF"],  out.inputs["Surface"])
    ob.data.materials.append(mat)

    ob["holoflow:facet"]    = True
    ob["holoflow:category"] = "stage-floor"
    ob.location             = (0, 0, 0)
    return ob


# ── GLB export ────────────────────────────────────────────────────────────────

def export_glb(ob: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.gltf(
        filepath                             = bpy.path.abspath(OUT_GLB),
        export_format                        = "GLB",
        use_selection                        = True,
        export_draco_mesh_compression_enable = True,
        export_draco_mesh_compression_level  = 6,
        export_image_format                  = "WEBP",
        export_morph                         = True,
        export_colors                        = True,
        export_yup                           = True,
    )
    print(f"[FDTD] GLB → {OUT_GLB}")


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)

    print("[FDTD 1D Yee] Basis — free space…")
    f_basis = sim_free_space()

    print("[FDTD 1D Yee] SK_Dielectric — ε_r=4 half-space…")
    f_diel  = sim_dielectric()

    print("[FDTD 1D Yee] SK_Cavity — resonant cavity…")
    f_cav   = sim_cavity()

    print("[FDTD 1D Yee] SK_PML — CPML absorbing boundaries…")
    f_pml   = sim_pml()

    ob = build_mesh(
        basis_field  = f_basis,
        shape_fields = [
            ("SK_Dielectric", f_diel),
            ("SK_Cavity",     f_cav),
            ("SK_PML",        f_pml),
        ],
    )

    bpy.ops.wm.save_as_mainfile(filepath=bpy.path.abspath(OUT_BLEND))
    print(f"[FDTD] blend → {OUT_BLEND}")
    export_glb(ob)
    print("[FDTD] blueprint complete — blend + glb saved.")


if __name__ == "__main__":
    main()
