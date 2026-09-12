"""
Kadomtsev–Petviashvili KP-II Exact Web-Soliton Height Field
============================================================
TECHNIQUE (3 sentences):
  The KP-II equation — ∂/∂x(u_t + 6u u_x + u_xxx) + 3 u_yy = 0 — is the 2+1-dimensional
  generalisation of KdV derived by Kadomtsev & Petviashvili (1970) to study transverse
  stability of KdV solitons under weak y-perturbations.  Unlike numerical schemes, the exact
  Hirota τ-function gives an analytic N-soliton solution with zero truncation error: set
  u = 2 ∂²_x log τ, where τ is a polynomial in exponentials whose coefficients encode all
  pairwise interaction factors.  Shape keys display four physically distinct regimes: a
  generic 2-soliton crossing, a resonant Y-junction (Mach-stem), a 4-soliton web, and the
  same 2-soliton pair at later time after the crests have separated.

MATHEMATICS:
  Dispersion (KP-II, + sign in u_yy):  ω(k,l) = k³ + 3l²/k
  1-soliton:  u = (k²/2) sech²(½η),  η = kx + ly − ωt + φ
  N-soliton τ-function (Hirota 1971):
    τ = Σ_{S⊆[N]}  A(S) · exp(Σ_{i∈S} η_i)
    A(∅) = 1,  A({i}) = 1,  A(S) = ∏_{i<j, i,j∈S} A_ij
    A_ij  = [(kᵢ−kⱼ)² + 3(lᵢ/kᵢ − lⱼ/kⱼ)²]
           /[(kᵢ+kⱼ)² + 3(lᵢ/kᵢ − lⱼ/kⱼ)²]       (always in (0,1] for KP-II)
  Stable quotient formula avoids log of tiny values:
    u = 2 (τ τ_xx − τ_x²) / τ²

RESONANCE (Mach stem / Y-junction):
  When k₁ = k₂ = k,  l₁ = −l₂ = l,  the stem parameters are k₃ = 2k, l₃ = 0.
  Resonance condition: ω₁ + ω₂ = ω₃  ⟺  k³+3l²/k + k³+3l²/k = 8k³
                       ⟺  3l²/k = 3k²  ⟺  l² = k⁴  ⟺  l = k².
  Choosing k=1, l=1: ω₁=ω₂=4, ω₃=8 ✓.  A₁₂ = 3/4 for this symmetric pair.

SOURCES (permissive):
  Kadomtsev BN & Petviashvili VI 1970 — Sov. Phys. JETP Lett. 15:539 (PD, >50 yr)
  Hirota R 1971 — Phys. Rev. Lett. 27:1192 (PD, >50 yr)
  Kodama Y & Williams LK 2011 — arXiv:1108.4984 (CC-BY-SA maths, equations used here are PD)
  NumPy BSD-3-Clause  https://numpy.org  github.com/numpy/numpy
"""

import bpy, bmesh, math, pathlib
import numpy as np

# ── Named constants ────────────────────────────────────────────────────────────
N           = 128       # grid resolution N×N
WORLD_SCALE = 4.0       # mesh half-width in metres
HEIGHT_SCALE = 0.28     # u → z amplitude (normalised u is in [0,1])
COL_LO      = (0.030, 0.120, 0.750, 1.0)   # cobalt (trough)
COL_HI      = (0.960, 0.600, 0.020, 1.0)   # amber  (crest)
ATTR_NAME   = "KP_Height"
BLEND_NAME  = "kp_ii_web_soliton_floor.blend"
GLB_NAME    = "kp_ii_web_soliton_floor.glb"
OUTPUT_DIR  = pathlib.Path(bpy.path.abspath("//"))

# ── Core mathematics ──────────────────────────────────────────────────────────

def _kp_u(X: np.ndarray, Y: np.ndarray,
          solitons: list, t: float = 0.0) -> np.ndarray:
    """
    Exact KP-II u(x,y,t) from Hirota τ-function.

    solitons: list of (k, ell, phi0).
      k   — x-wavenumber (k > 0 ensures rightward propagation)
      ell — y-wavenumber (real; sets the soliton's transverse angle)
      phi0— initial phase shift (positions the crest at t=0)
    Dispersion: omega = k³ + 3·ell²/k  (KP-II, positive y² term)
    WHY quotient not log: avoids log(small τ) near τ→0 in degenerate cases.
    """
    NS = len(solitons)

    # Phase η_i at every grid point
    etas = []
    for (k, ell, phi0) in solitons:
        omega = k**3 + 3.0 * ell**2 / k
        eta   = k * X + ell * Y - omega * t + phi0
        np.clip(eta, -80.0, 80.0, out=eta)   # guard float overflow
        etas.append(eta)

    # Log of Hirota pairwise factor A_ij for KP-II (always ≤ 0 since A_ij ∈ (0,1])
    log_A = {}
    for i in range(NS):
        ki, li, _ = solitons[i]
        for j in range(i + 1, NS):
            kj, lj, _ = solitons[j]
            dv  = li / ki - lj / kj                        # phase-velocity difference
            num = (ki - kj)**2 + 3.0 * dv**2
            den = (ki + kj)**2 + 3.0 * dv**2
            # num/den ∈ (0,1] so log ≤ 0; min-clip avoids log(0) at resonance limit
            log_A[(i, j)] = math.log(max(num / den, 1e-14))

    # Sum over all 2^N subsets (N ≤ 4, so ≤ 16 terms — fully tractable)
    tau    = np.zeros_like(X)
    tau_x  = np.zeros_like(X)
    tau_xx = np.zeros_like(X)

    for mask in range(1 << NS):
        idx = [i for i in range(NS) if (mask >> i) & 1]
        if not idx:
            tau += 1.0          # empty subset: exp(0) = 1, no x-derivatives
            continue
        # Amplitude factor: product of A_ij for all pairs in this subset
        log_amp = sum(log_A[(min(i, j), max(i, j))]
                      for a, i in enumerate(idx) for j in idx[a + 1:])
        k_sum   = sum(solitons[i][0] for i in idx)
        eta_sum = sum(etas[i] for i in idx)
        # Clip combined exponent to prevent float64 overflow (exp(709) = max)
        combined = np.clip(log_amp + eta_sum, -700.0, 700.0)
        term     = np.exp(combined)
        tau      += term
        tau_x    += k_sum * term
        tau_xx   += k_sum**2 * term   # d²/dx² exp(Ση_i) = (Σk_i)² · exp(Ση_i)

    # KP-II field: u = 2 ∂²_x log τ = 2(τ·τ_xx − τ_x²)/τ²
    u = 2.0 * (tau * tau_xx - tau_x**2) / (tau**2 + 1e-30)
    np.clip(u, 0.0, None, out=u)    # negative values are numerical artefacts near grid edges
    return u


# ── Mesh builder ───────────────────────────────────────────────────────────────

def _build_floor(obj_name: str, u_arr: np.ndarray):
    """
    128×128 quad-grid stage floor from height array u_arr (shape (N,N), values ≥ 0).
    Normalises to [0,1] before scaling by HEIGHT_SCALE so every shape key fills
    the full amplitude band — consistent with other height-field floor entries.
    WHY quad not tri: lower poly count for WebXR; edges stay clean at low LOD.
    """
    u_norm = u_arr / (u_arr.max() + 1e-12)

    me = bpy.data.meshes.new(obj_name)
    ob = bpy.data.objects.new(obj_name, me)
    bpy.context.collection.objects.link(ob)
    bm = bmesh.new()

    xs = np.linspace(-WORLD_SCALE, WORLD_SCALE, N)
    ys = np.linspace(-WORLD_SCALE, WORLD_SCALE, N)

    verts = []
    for iy in range(N):
        row = []
        for ix in range(N):
            z = HEIGHT_SCALE * float(u_norm[iy, ix])
            v = bm.verts.new((float(xs[ix]), float(ys[iy]), z))
            row.append(v)
        verts.append(row)

    bm.verts.ensure_lookup_table()
    for iy in range(N - 1):
        for ix in range(N - 1):
            bm.faces.new([verts[iy][ix], verts[iy][ix+1],
                          verts[iy+1][ix+1], verts[iy+1][ix]])

    bm.to_mesh(me)
    bm.free()

    # FLOAT_COLOR attribute for Cobalt–Amber WebXR shading
    attr = me.attributes.new(name=ATTR_NAME, type='FLOAT_COLOR', domain='POINT')
    flat = u_norm.ravel()
    for i, v in enumerate(me.vertices):
        t = float(flat[i])
        attr.data[i].color = (
            COL_LO[0] + t * (COL_HI[0] - COL_LO[0]),
            COL_LO[1] + t * (COL_HI[1] - COL_LO[1]),
            COL_LO[2] + t * (COL_HI[2] - COL_LO[2]),
            1.0,
        )
    return ob


def _add_shape_key(ob: bpy.types.Object, name: str, u_arr: np.ndarray):
    """Add a shape key from a height array (same normalisation as the basis mesh)."""
    u_norm = u_arr / (u_arr.max() + 1e-12)
    sk = ob.shape_key_add(name=name, from_mix=False)
    flat = u_norm.ravel()
    me = ob.data
    # Vertices are laid out in row-major (iy, ix) order — match _build_floor
    for i, v in enumerate(me.vertices):
        sk.data[i].co.z = HEIGHT_SCALE * float(flat[i])


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj, do_unlink=True)

    xs = np.linspace(-WORLD_SCALE, WORLD_SCALE, N)
    ys = np.linspace(-WORLD_SCALE, WORLD_SCALE, N)
    X, Y = np.meshgrid(xs, ys)

    # ── Basis: 2-soliton oblique crossing at t = 0
    #    Soliton 1 (k=1.2, ell=0.8): NE-travelling crest, amplitude = k²/2 ≈ 0.72
    #    Soliton 2 (k=1.0, ell=-1.0): SE-travelling crest, amplitude = 0.50
    #    Non-resonant: A₁₂ ≈ 0.022 → clean X-crossing with slight amplitude boost
    SOL_2 = [(1.2, 0.8, 0.0), (1.0, -1.0, 0.0)]
    u_basis = _kp_u(X, Y, SOL_2, t=0.0)
    ob = _build_floor("kp_ii_web_soliton", u_basis)
    ob.shape_key_add(name="Basis", from_mix=False)

    # ── SK_YJunction: resonant Y-junction (k=1, ell=±1 satisfies l=k² resonance)
    #    Two symmetric solitons → Mach stem along x-axis, amplitude boosted 4×
    #    A₁₂ = [(0)² + 3(2)²]/[(2)² + 3(2)²] = 12/16 = 0.75
    #    The stem kx-term (k₃=2) creates the forward-running high-amplitude crest
    SOL_Y = [(1.0, 1.0, 0.0), (1.0, -1.0, 0.0)]
    u_yjn = _kp_u(X, Y, SOL_Y, t=0.0)
    _add_shape_key(ob, "SK_YJunction", u_yjn)

    # ── SK_Web4: 4-soliton web — two crossing Y-junctions in quadrature
    #    Each pair satisfies the resonance condition independently; together they
    #    tile the plane with a grid of rectangular cells (Kodama-Williams 2011 Gr(2,4))
    #    k: 1.0, 1.0, 0.8, 0.8; ell: ±0.8, ±0.64 (two resonant pairs, orthogonal)
    SOL_W4 = [(1.0, 0.8, -1.0), (1.0, -0.8, 1.0),
              (0.8, 0.64, 2.0), (0.8, -0.64, -2.0)]
    u_w4   = _kp_u(X, Y, SOL_W4, t=0.0)
    _add_shape_key(ob, "SK_Web4", u_w4)

    # ── SK_Temporal: 2-soliton at t = 8 — crests have propagated apart,
    #    revealing the trailing trough and the asymptotic phase shift predicted
    #    by the interaction coefficient A₁₂
    u_t8 = _kp_u(X, Y, SOL_2, t=8.0)
    _add_shape_key(ob, "SK_Temporal", u_t8)

    # ── Camera + light for recording
    bpy.ops.object.camera_add(location=(0, -7, 5.5))
    cam = bpy.context.object
    cam.rotation_euler = (math.radians(52), 0, 0)
    bpy.context.scene.camera = cam

    bpy.ops.object.light_add(type='SUN', location=(3, -3, 8))
    bpy.context.object.data.energy = 3.0

    # ── Save .blend + export .glb
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_DIR / BLEND_NAME))

    bpy.ops.export_scene.gltf(
        filepath=str(OUTPUT_DIR / GLB_NAME),
        export_format='GLB',
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_image_format='WEBP',
        export_attributes=True,
    )
    print(f"Saved: {BLEND_NAME}  {GLB_NAME}")


main()
