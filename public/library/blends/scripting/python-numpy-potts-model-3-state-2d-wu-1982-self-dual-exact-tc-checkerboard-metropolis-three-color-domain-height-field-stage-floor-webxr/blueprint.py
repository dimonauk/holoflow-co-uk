"""
Blender 5.1 — 3-State Potts Model, 2D square lattice (Wu 1982 review)
Exact critical temperature: Tc = J / ln(1 + √3) ≈ 0.9950 J/k_B
Checkerboard Metropolis: simultaneous vectorised updates of even/odd sites.

H = −J Σ_{⟨ij⟩} δ(σᵢ, σⱼ)    σᵢ ∈ {0, 1, 2}

Critical exponents (c = 4/5 CFT, Nienhuis 1982 PRL 49:1062):
  β = 1/9  ≈ 0.111   M ~ |T − Tc|^β   below Tc
  ν = 5/6  ≈ 0.833   ξ ~ |T − Tc|^{−ν}
  η = 4/15 ≈ 0.267   G(r) ~ r^{−(d−2+η)}   at Tc

Licence: CC0 — Potts 1952 PD (>70 yr); Wu 1982 equations CC0; NumPy BSD-3.
Run inside Blender 5.1 Scripting workspace.
"""

import bpy
import numpy as np

# ── simulation constants ─────────────────────────────────────────────────────
N        = 128                              # lattice edge → 16384 vertices
Q        = 3                               # Potts states
J        = 1.0                             # coupling (energy scale)
T_C      = J / np.log(1.0 + np.sqrt(Q))   # ≈ 0.9950 J/k_B (Wu 1982)
T_COLD   = 0.50 * T_C    # quasi-ordered, large three-color domains
T_CRIT   = 1.00 * T_C    # critical point, algebraic G(r) ~ r^{−(1−η)}
T_HOT1   = 1.50 * T_C    # above Tc, short-range order only
T_HIGH   = 3.00 * T_C    # fully disordered, equal populations
N_EQUIL  = 6_000          # equilibration sweeps
SEED     = 0x50545453     # "PTTS"
Z_SCALE  = 0.45           # height range [0, Z_SCALE]


def _nn_delta_sum(sigma, new_s):
    """
    Per-site: (neighbours matching new_s) − (neighbours matching sigma).
    ΔE = −J × result; negative ΔE means lower energy → accept unconditionally.
    Periodic (toroidal) boundaries via np.roll.
    """
    nbs = [np.roll(sigma, d, a) for d, a in ((-1, 1), (1, 1), (-1, 0), (1, 0))]
    m_new = sum((nb == new_s) for nb in nbs).astype(np.float32)
    m_old = sum((nb == sigma) for nb in nbs).astype(np.float32)
    return m_new - m_old


def run_potts(T, n_sweeps, rng, sigma_init=None):
    """
    Checkerboard Metropolis for q-state Potts.  Sites on the same parity
    sublattice are conditionally independent given the opposite sublattice
    (all their neighbours lie on the other sublattice), so N²/2 accept/reject
    decisions may be made in parallel each half-sweep — O(N²) per sweep.
    """
    sigma = (sigma_init.copy() if sigma_init is not None
             else rng.integers(0, Q, (N, N), dtype=np.int8))
    ii, jj = np.mgrid[0:N, 0:N]
    masks  = [(ii + jj) % 2 == 0, (ii + jj) % 2 == 1]
    inv_T  = 1.0 / T

    for _ in range(n_sweeps):
        for mask in masks:
            new_s  = rng.integers(0, Q, (N, N), dtype=np.int8)
            dE     = -J * _nn_delta_sum(sigma, new_s)
            accept = (dE <= 0.0) | (
                rng.random((N, N), dtype=np.float32) < np.exp(-dE * inv_T))
            sigma[mask & accept] = new_s[mask & accept]

    return sigma


def _norm(sigma):
    """Map σ ∈ {0,1,2} → [0, 1]: 0→0.0, 1→0.5, 2→1.0."""
    return sigma.astype(np.float32) / (Q - 1)


def _build_mesh(sigma):
    """Build 128×128 plane mesh from spin configuration."""
    field = _norm(sigma)
    ii    = np.repeat(np.arange(N), N)
    jj    = np.tile(np.arange(N), N)
    xs    = (jj / (N - 1)) - 0.5
    ys    = (ii / (N - 1)) - 0.5
    zs    = field.ravel() * Z_SCALE
    verts = list(zip(xs.tolist(), ys.tolist(), zs.tolist()))
    faces = [(i * N + j, i * N + j + 1, (i + 1) * N + j + 1, (i + 1) * N + j)
             for i in range(N - 1) for j in range(N - 1)]
    mesh = bpy.data.meshes.new("potts3_floor")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return mesh


def _set_colour(mesh, sigma):
    """Write FLOAT_COLOR attribute 'Potts3_State' per vertex."""
    field = _norm(sigma).ravel()
    attr  = mesh.color_attributes.get("Potts3_State")
    if attr is None:
        attr = mesh.color_attributes.new("Potts3_State", "FLOAT_COLOR", "POINT")
    rgba = np.zeros(len(field) * 4, dtype=np.float32)
    rgba[0::4] = field
    rgba[1::4] = field
    rgba[2::4] = field
    rgba[3::4] = 1.0
    attr.data.foreach_set("color", rgba)


def _add_sk(obj, sigma, name):
    """Append a shape key with heights from sigma."""
    sk    = obj.shape_key_add(name=name, from_mix=False)
    field = _norm(sigma)
    ii    = np.repeat(np.arange(N, dtype=np.float32), N)
    jj    = np.tile(np.arange(N, dtype=np.float32), N)
    xs    = (jj / (N - 1)) - 0.5
    ys    = (ii / (N - 1)) - 0.5
    zs    = field.ravel() * Z_SCALE
    co    = np.column_stack([xs, ys, zs]).ravel().astype(np.float64)
    sk.data.foreach_set("co", co)


def _build_material(obj):
    """
    Attribute-driven emission: cobalt (σ=0, 0.0) → teal (σ=1, 0.5) → amber (σ=2, 1.0).
    Three-stop colour ramp makes each Potts state a distinct hue.
    """
    mat = bpy.data.materials.new("Potts3Mat")
    mat.use_nodes = True
    nt  = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = "Potts3_State"
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color    = (0.07, 0.24, 0.62, 1.0)  # cobalt
    ramp.color_ramp.elements.new(0.5)
    ramp.color_ramp.elements[1].color    = (0.00, 0.62, 0.55, 1.0)  # teal
    ramp.color_ramp.elements[2].color    = (1.00, 0.64, 0.00, 1.0)  # amber
    emit = nt.nodes.new("ShaderNodeEmission")
    emit.inputs["Strength"].default_value = 2.0
    out  = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(attr.outputs["Fac"],        ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"],      emit.inputs["Color"])
    nt.links.new(emit.outputs["Emission"],   out.inputs["Surface"])
    obj.data.materials.append(mat)


def main():
    rng = np.random.default_rng(SEED)
    print(f"[Potts3] Tc = {T_C:.4f} J/k_B")

    print(f"[Potts3] Basis  T={T_COLD:.4f}")
    s_cold = run_potts(T_COLD, N_EQUIL, rng)

    mesh = _build_mesh(s_cold)
    _set_colour(mesh, s_cold)
    obj  = bpy.data.objects.new("potts3_floor", mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.shape_key_add(name="Basis", from_mix=False)

    for name, T in [("SK_Critical", T_CRIT),
                    ("SK_HotCrit",  T_HOT1),
                    ("SK_HighT",    T_HIGH)]:
        print(f"[Potts3] {name}  T={T:.4f}")
        _add_sk(obj, run_potts(T, N_EQUIL, rng), name)

    _build_material(obj)
    print("[DONE] Object 'potts3_floor' created.")


main()
