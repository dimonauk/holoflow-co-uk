"""
FitzHugh-Nagumo Excitable Media — Viewport Recording Script
Blender 5.1 | CC0 | Holoflow Studio 2026-09-13

Outputs: public/library/videos/scripting/
         python-numpy-fitzhugh-nagumo-1961-excitable-media-trigger-wave-spiral-height-field-stage-floor-webxr/
         viewport.mp4  (12 s, 30 fps, 360 frames)

Strategy: integrate the S1+S2 spiral protocol and capture 8 snapshots
at evenly-spaced intervals (steps 0 → 1200 × dt).  Each snapshot becomes
a shape key; the animation morphs through them showing spontaneous spiral
arm formation from a broken wave front.
"""

import bpy
import numpy as np

# ── CONSTANTS (must match blueprint.py) ──────────────────────────────────────
N, DU, DT, Z_SCALE = 128, 1.0, 0.10, 0.50
EPS, A_KIN, B_KIN, IEXT = 0.08, 0.70, 0.80, 0.50
U_MIN, U_MAX = -1.5, 2.1
MESH_NAME       = "FHN_Viewport"
ATTR_NAME       = "FHN_U_Volt"
STEPS_TOTAL     = 1200
N_SNAPS         = 8                     # baseline + 7 further snapshots
STEPS_PER_SNAP  = STEPS_TOTAL // (N_SNAPS - 1)   # 171 steps between each
FRAMES_PER_SNAP = 45                    # 8 × 45 = 360 = 12 s @ 30 fps
OUTPUT_PATH = (
    "//../../videos/scripting/"
    "python-numpy-fitzhugh-nagumo-1961-excitable-media-trigger-wave-"
    "spiral-height-field-stage-floor-webxr/viewport"
)


# ── SPECTRAL HELPERS ──────────────────────────────────────────────────────────
def _k2(n: int) -> np.ndarray:
    kx = np.fft.fftfreq(n, d=1.0 / n)
    ky = np.fft.rfftfreq(n, d=1.0 / n)
    KX, KY = np.meshgrid(kx, ky, indexing="ij")
    return (2.0 * np.pi / n) ** 2 * (KX ** 2 + KY ** 2)


def _etd1_u(k2: np.ndarray):
    Lu = -DU * k2 * DT
    return np.exp(Lu), np.where(np.abs(Lu) < 1e-12, 1.0, np.expm1(Lu) / Lu)


def _etd1_v():
    Lv = -EPS * B_KIN * DT
    return float(np.exp(Lv)), float(np.expm1(Lv) / Lv)


def _norm(u: np.ndarray) -> np.ndarray:
    return np.clip((u - U_MIN) / (U_MAX - U_MIN), 0.0, 1.0)


# ── SIMULATION ────────────────────────────────────────────────────────────────
def simulate_snapshots() -> list[np.ndarray]:
    """
    S1+S2 cross-field spiral protocol.
    Returns N_SNAPS snapshots of the activator field u.
    """
    u = np.full((N, N), -1.2)
    v = np.zeros((N, N))
    u[:10, :] = 2.0                     # S1 edge stimulus

    k2_arr      = _k2(N)
    E_u, phi1_u = _etd1_u(k2_arr)
    E_v, phi1_v = _etd1_v()

    # Propagate S1 wave across the domain
    u_h = np.fft.rfft2(u)
    for _ in range(300):
        Nu  = u - u ** 3 / 3.0 - v + IEXT
        u_h = E_u * u_h + phi1_u * np.fft.rfft2(Nu) * DT
        u   = np.clip(np.fft.irfft2(u_h, s=(N, N)), -2.5, 2.5)
        u_h = np.fft.rfft2(u)
        v   = E_v * v + phi1_v * (EPS * (u + A_KIN)) * DT

    u[:, : N // 2] = 2.0               # S2 stimulus — creates free spiral tip
    v[:, : N // 2] = 0.0
    snaps = [u.copy()]

    u_h = np.fft.rfft2(u)
    for _ in range(N_SNAPS - 1):
        for __ in range(STEPS_PER_SNAP):
            Nu  = u - u ** 3 / 3.0 - v + IEXT
            u_h = E_u * u_h + phi1_u * np.fft.rfft2(Nu) * DT
            u   = np.clip(np.fft.irfft2(u_h, s=(N, N)), -2.5, 2.5)
            u_h = np.fft.rfft2(u)
            v   = E_v * v + phi1_v * (EPS * (u + A_KIN)) * DT
        snaps.append(u.copy())

    return snaps


# ── MESH + ANIMATION ──────────────────────────────────────────────────────────
def build_animated_mesh(snaps: list[np.ndarray]) -> bpy.types.Object:
    t0    = _norm(snaps[0])
    verts = [((i / (N - 1)) * 2 - 1, (j / (N - 1)) * 2 - 1, float(t0[i, j]) * Z_SCALE)
             for i in range(N) for j in range(N)]
    faces = []
    for i in range(N - 1):
        for j in range(N - 1):
            a = i * N + j
            faces.append((a, a + 1, a + N + 1, a + N))

    me = bpy.data.meshes.new(MESH_NAME)
    me.from_pydata(verts, [], faces)
    me.update()
    obj = bpy.data.objects.new(MESH_NAME, me)
    bpy.context.scene.collection.objects.link(obj)

    # Write initial vertex colour
    me.attributes.new(ATTR_NAME, "FLOAT_COLOR", "POINT")
    t_flat = t0.ravel(order="C").astype(np.float32)
    rgba   = np.stack([t_flat * 1.00 + (1 - t_flat) * 0.03,
                       t_flat * 0.65 + (1 - t_flat) * 0.14,
                       t_flat * 0.00 + (1 - t_flat) * 0.56,
                       np.ones_like(t_flat)], axis=1).ravel()
    me.attributes[ATTR_NAME].data.foreach_set("color", rgba.tolist())

    # Shape keys
    obj.shape_key_add(name="Basis", from_mix=False)
    for s_idx, snap in enumerate(snaps[1:], start=1):
        t  = _norm(snap)
        sk = obj.shape_key_add(name=f"T{s_idx * STEPS_PER_SNAP}", from_mix=False)
        buf = np.empty(N * N * 3, dtype=np.float32)
        idx_map = np.arange(N * N)
        ii, jj  = np.divmod(idx_map, N)
        buf[0::3] = (ii / (N - 1)) * 2 - 1
        buf[1::3] = (jj / (N - 1)) * 2 - 1
        buf[2::3] = t.ravel(order="C") * Z_SCALE
        sk.data.foreach_set("co", buf.tolist())

    # Animate: each key is active for FRAMES_PER_SNAP frames
    for s_idx in range(1, N_SNAPS):
        kb      = obj.data.shape_keys.key_blocks[s_idx]
        start_f = (s_idx - 1) * FRAMES_PER_SNAP + 1
        end_f   =  s_idx      * FRAMES_PER_SNAP
        kb.value = 0.0;  kb.keyframe_insert("value", frame=max(1, start_f - 1))
        kb.value = 1.0;  kb.keyframe_insert("value", frame=start_f)
        kb.value = 1.0;  kb.keyframe_insert("value", frame=end_f)
        kb.value = 0.0;  kb.keyframe_insert("value", frame=end_f + 1)

    return obj


# ── SCENE DRESSING ────────────────────────────────────────────────────────────
def setup_scene(obj: bpy.types.Object) -> None:
    bpy.ops.object.camera_add(location=(0.0, -2.8, 1.6))
    cam = bpy.context.object
    cam.rotation_euler = (1.15, 0.0, 0.0)
    bpy.context.scene.camera = cam

    bpy.ops.object.light_add(type="AREA", location=(1.5, -1.5, 3.0))
    bpy.context.object.data.energy = 180
    bpy.context.object.data.size   = 2.5

    mat  = bpy.data.materials.new("FHN_Rec_Mat")
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out  = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    attr = nodes.new("ShaderNodeAttribute")
    attr.attribute_name = ATTR_NAME
    bsdf.inputs["Metallic"].default_value         = 0.20
    bsdf.inputs["Roughness"].default_value        = 0.30
    bsdf.inputs["Emission Strength"].default_value = 1.6
    links.new(attr.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(attr.outputs["Color"], bsdf.inputs["Emission Color"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    obj.data.materials.append(mat)


def configure_render() -> None:
    sc = bpy.context.scene
    sc.frame_start = 1
    sc.frame_end   = N_SNAPS * FRAMES_PER_SNAP
    sc.render.fps   = 30
    sc.render.engine = "BLENDER_EEVEE_NEXT"
    sc.render.image_settings.file_format       = "FFMPEG"
    sc.render.ffmpeg.format                     = "MPEG4"
    sc.render.ffmpeg.codec                      = "H264"
    sc.render.ffmpeg.constant_rate_factor       = "MEDIUM"
    sc.render.filepath    = OUTPUT_PATH
    sc.render.resolution_x = 1280
    sc.render.resolution_y = 720


# ── ENTRY POINT ───────────────────────────────────────────────────────────────
def main() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    print("Simulating FHN spiral (S1+S2 protocol) …")
    snaps = simulate_snapshots()
    print(f"   {len(snaps)} snapshots captured.")

    obj = build_animated_mesh(snaps)
    setup_scene(obj)
    configure_render()
    bpy.ops.render.render(animation=True)
    print("viewport.mp4 written.")


main()
