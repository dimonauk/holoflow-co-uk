"""
Gray–Scott Reaction-Diffusion: Pearson 1993 Pattern Atlas
==========================================================
TECHNIQUE (2–3 sentences):
  Gray–Scott is a two-component activator-depletion system in which autocatalytic
  species v converts substrate u into more v at rate uv², while u is continuously
  replenished from a reservoir (feed rate F) and v is removed (kill rate k).
  Because the substrate diffuses twice as fast as the activator (Du = 0.16,
  Dv = 0.08), the system undergoes a Turing instability producing stationary
  spatial patterns — spots, worms, holes — whose type is wholly determined by
  the (F, k) parameter pair. Pearson (1993 Science 261:189–192) mapped twelve
  distinct pattern classes across this plane, including the now-famous
  self-replicating spots he termed "mitosis".

MATHEMATICS:
  ∂u/∂t = Du∇²u − uv² + F(1 − u)
  ∂v/∂t = Dv∇²v + uv² − (F + k)v

  Nontrivial fixed point: u* = F+k,  v* = √[F(1−u*)/u*].
  (Requires F+k < 1; at typical params u* ≈ 0.10, v* ≈ 0.35.)
  Turing instability: linearise around (u*, v*), compute Jacobian J.
  Patterns emerge when diffusion-driven instability satisfies:
    tr(J) < 0,  det(J) > 0,  but  det(J − D k²) = 0  for some k² > 0.
  WHY Du > Dv required: long-range substrate suppression, short-range activation.
  Critical wavenumber k_c² ≈ √[det(J)/(Du·Dv)].

NUMERICAL METHOD — Explicit Euler with periodic 5-point Laplacian:
  L[f]_{i,j} = f_{i+1,j} + f_{i-1,j} + f_{i,j+1} + f_{i,j-1} − 4f_{i,j}
  u ← u + dt·(Du·L[u] − uv² + F(1−u))
  v ← v + dt·(Dv·L[v] + uv² − (F+k)v)

  WHY explicit Euler over spectral: reaction coupling uv² is bilinear in
  both unknowns — a spectral implicit scheme would require solving a
  coupled nonlinear system each step. Explicit Euler costs one Laplacian
  evaluation per species per step. At Du=0.16, dx=1, dt=1: CFL ratio
  Du·dt/dx² = 0.16 < 0.25 (4-neighbour stability bound). ✓

SOURCES (permissive):
  Pearson JE 1993 Science 261(5118):189–192 doi:10.1126/science.261.5118.189
    — pattern atlas (mathematical results, public domain)
  Gray P & Scott SK 1984 Chem Eng Sci 39(6):1087–1097
    doi:10.1016/0009-2509(84)87017-7 — reaction scheme (equations, public domain)
  NumPy — BSD-3-Clause  https://numpy.org  github.com/numpy/numpy
  pmneila/jsexp — MIT   https://github.com/pmneila/jsexp
"""

import bpy, numpy as np, pathlib, mathutils

# ── Named constants ────────────────────────────────────────────────────────────
N            = 128       # grid resolution N×N
WORLD_SCALE  = 4.0       # mesh half-width (metres)
HEIGHT_SCALE = 0.80      # v → z amplitude (v=0.50 → z=+0.40 m)
DU           = 0.16      # substrate diffusivity — MUST exceed DV for Turing
DV           = 0.08      # activator diffusivity  Du/Dv = 2
DT           = 1.0       # explicit Euler step (CFL = Du/dx² = 0.16 < 0.25)

# Pearson (1993) Fig. 2 parameter coordinates  (F, k, n_steps)
PARAMS_BASIS   = (0.037, 0.060, 10_000)   # ε-region: isolated spots (symmetric)
PARAMS_WORM    = (0.060, 0.062, 10_000)   # η-region: labyrinthine worms / mazes
PARAMS_HOLE    = (0.039, 0.058, 12_000)   # ζ-region: active holes on u-background
PARAMS_MITOSIS = (0.028, 0.054,  8_000)   # δ-region: self-replicating spot division

SEED         = 42
NOISE_AMP    = 0.05     # symmetry-breaking noise amplitude
COL_LOW      = (0.030, 0.200, 0.780, 1.0)  # cobalt  (v≈0, substrate-rich)
COL_HIGH     = (0.980, 0.620, 0.050, 1.0)  # amber   (v>0, activator-rich)
ATTR_NAME    = "GS_V"
OBJ_NAME     = "gray_scott_floor"
BLEND_NAME   = "gray_scott_floor.blend"
GLB_NAME     = "gray_scott_floor.glb"


# ── Physics helpers ────────────────────────────────────────────────────────────

def _lap(field: np.ndarray) -> np.ndarray:
    """
    Periodic 5-point Laplacian on N×N grid, dx = dy = 1.
    numpy.roll performs O(1) index wrapping with no data copy.
    WHY 5-point over 9-point: Gray-Scott patterns develop at
    wavelengths >> 1 cell; extra stencil terms are negligible and
    slow the inner loop by ~40%.
    """
    return (
        np.roll(field,  1, 0) + np.roll(field, -1, 0) +
        np.roll(field,  1, 1) + np.roll(field, -1, 1) - 4.0 * field
    )


def _init(f_val: float, seed_off: int) -> tuple:
    """
    IC: u = 1 everywhere, v = 0 everywhere, with a central patch
    plus weak white noise. Seed square size scales with F: low-F
    mitosis needs a small nucleus (4×4) so early divisions are visible;
    higher-F spot/worm params use a larger (20×20) seed.
    """
    rng = np.random.default_rng(SEED + seed_off)
    u   = np.ones( (N, N), dtype=np.float64)
    v   = np.zeros((N, N), dtype=np.float64)
    hw  = 4 if f_val < 0.035 else 10      # half-width of seed square
    cx  = N // 2
    u[cx-hw:cx+hw, cx-hw:cx+hw] = 0.50
    v[cx-hw:cx+hw, cx-hw:cx+hw] = 0.25
    u  += rng.uniform(-NOISE_AMP, NOISE_AMP, (N, N))
    v  += rng.uniform(-NOISE_AMP, NOISE_AMP, (N, N))
    np.clip(u, 0.0, 1.0, out=u)
    np.clip(v, 0.0, 1.0, out=v)
    return u, v


def _simulate(f_val: float, k_val: float, n_steps: int, seed_off: int = 0) -> np.ndarray:
    """
    Explicit Euler Gray–Scott. Returns activator field v at t = n_steps·dt.
    In-place updates avoid repeated allocation; clip after each step guards
    against rare numerical overshoot near sharp reaction fronts.
    """
    u, v = _init(f_val, seed_off)
    fk   = f_val + k_val
    for _ in range(n_steps):
        uvv = u * v * v              # shared reaction term — compute once
        u  += DT * (DU * _lap(u) - uvv + f_val * (1.0 - u))
        v  += DT * (DV * _lap(v) + uvv - fk * v)
        np.clip(u, 0.0, 1.0, out=u)
        np.clip(v, 0.0, 1.0, out=v)
    return v


# ── Mesh builders ──────────────────────────────────────────────────────────────

def _build_mesh(v_field: np.ndarray):
    """
    N×N quad mesh in the XZ plane (rotated to floor after).
    Vertex z = v * HEIGHT_SCALE.  CCW quads when viewed from +Y.
    """
    xs   = np.linspace(-WORLD_SCALE, WORLD_SCALE, N)
    verts, faces = [], []
    for i in range(N):
        for j in range(N):
            verts.append((xs[j], xs[i], float(v_field[i, j]) * HEIGHT_SCALE))
    for i in range(N - 1):
        for j in range(N - 1):
            a = i * N + j
            faces.append((a, a + 1, a + N + 1, a + N))

    me  = bpy.data.meshes.new(OBJ_NAME)
    obj = bpy.data.objects.new(OBJ_NAME, me)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    me.from_pydata(verts, [], faces)
    me.update()
    obj.shape_key_add(name="Basis", from_mix=False)

    # FLOAT_COLOR attribute — cobalt→amber gradient from basis v field
    attr = me.color_attributes.new(ATTR_NAME, "FLOAT_COLOR", "POINT")
    flat = v_field.ravel()
    rgba = []
    for val in flat:
        t = min(float(val) * 2.0, 1.0)   # amplify: v≈0.5 → full amber
        rgba.extend([
            COL_LOW[0] + t * (COL_HIGH[0] - COL_LOW[0]),
            COL_LOW[1] + t * (COL_HIGH[1] - COL_LOW[1]),
            COL_LOW[2] + t * (COL_HIGH[2] - COL_LOW[2]),
            1.0,
        ])
    attr.data.foreach_set("color", rgba)
    return obj, me


def _add_sk(obj, v_field: np.ndarray, name: str):
    """Add a shape key updating only vertex z from the new v field."""
    sk = obj.shape_key_add(name=name, from_mix=False)
    for i in range(N):
        for j in range(N):
            sk.data[i * N + j].co[2] = float(v_field[i, j]) * HEIGHT_SCALE


# ── Material ──────────────────────────────────────────────────────────────────

def _add_material(obj):
    """Emission + Principled driven by GS_V vertex colour attribute."""
    mat   = bpy.data.materials.new("GrayScott_Mat")
    mat.use_nodes = True
    nt    = mat.node_tree
    nt.nodes.clear()
    attr  = nt.nodes.new("ShaderNodeAttribute"); attr.attribute_name = ATTR_NAME
    prin  = nt.nodes.new("ShaderNodeBsdfPrincipled")
    emit  = nt.nodes.new("ShaderNodeEmission");  emit.inputs["Strength"].default_value = 1.6
    mix   = nt.nodes.new("ShaderNodeMixShader"); mix.inputs["Fac"].default_value = 0.35
    out   = nt.nodes.new("ShaderNodeOutputMaterial")
    prin.inputs["Metallic"].default_value  = 0.10
    prin.inputs["Roughness"].default_value = 0.30
    lk    = nt.links.new
    lk(attr.outputs["Color"], prin.inputs["Base Color"])
    lk(attr.outputs["Color"], emit.inputs["Color"])
    lk(emit.outputs["Emission"], mix.inputs[1])
    lk(prin.outputs["BSDF"],     mix.inputs[2])
    lk(mix.outputs["Shader"],    out.inputs["Surface"])
    obj.data.materials.append(mat)


# ── Export ────────────────────────────────────────────────────────────────────

def _export_glb(path: str):
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


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    F_b, k_b, n_b = PARAMS_BASIS
    F_w, k_w, n_w = PARAMS_WORM
    F_h, k_h, n_h = PARAMS_HOLE
    F_m, k_m, n_m = PARAMS_MITOSIS

    print(f"[GS] Basis   spots   F={F_b} k={k_b} n={n_b:,}")
    v_basis   = _simulate(F_b, k_b, n_b, seed_off=0)
    print(f"[GS] SK_Worm worms   F={F_w} k={k_w} n={n_w:,}")
    v_worm    = _simulate(F_w, k_w, n_w, seed_off=1)
    print(f"[GS] SK_Hole holes   F={F_h} k={k_h} n={n_h:,}")
    v_hole    = _simulate(F_h, k_h, n_h, seed_off=2)
    print(f"[GS] SK_Mitosis      F={F_m} k={k_m} n={n_m:,}")
    v_mitosis = _simulate(F_m, k_m, n_m, seed_off=3)

    obj, me = _build_mesh(v_basis)
    _add_sk(obj, v_worm,    "SK_Worm")
    _add_sk(obj, v_hole,    "SK_Hole")
    _add_sk(obj, v_mitosis, "SK_Mitosis")
    _add_material(obj)

    # Rotate to +Y-up floor plane (holoflow exporter convention)
    obj.rotation_euler = mathutils.Euler((-1.5707963, 0, 0), "XYZ")
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(rotation=True)

    obj["holoflow:facet"]    = True
    obj["holoflow:category"] = "stage-floor"

    bpy.ops.wm.save_as_mainfile(filepath=f"//{BLEND_NAME}")
    _export_glb(f"//{GLB_NAME}")
    print(f"[GS] Done — {BLEND_NAME} + {GLB_NAME} written.")


if __name__ == "__main__":
    main()
