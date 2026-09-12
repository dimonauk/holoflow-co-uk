# Screen Recording Notes — KP-II Web Soliton Stage Floor

## OBS / Windows Game Bar Setup

| Setting         | Value                              |
|-----------------|------------------------------------|
| Window source   | Blender (full application window)  |
| Resolution      | 1920 × 1080                        |
| Frame rate      | 30 fps                             |
| Audio           | Off (no narration track needed)    |
| Output format   | MP4 / H.264                        |
| Output file     | `screen.mp4` → place in this folder|

## What to record (~60–90 seconds)

1. **Open Blender 5.1** with `kp_ii_web_soliton_floor.blend` already loaded.
2. **Show the Scripting workspace** — scroll through `blueprint.py` at a readable
   pace; pause on the `_kp_u()` function (the Hirota τ calculation) and the
   `_build_floor()` call.
3. **Switch to 3D Viewport** in solid shading.  Orbit around the mesh with
   middle-mouse so the soliton ridges are visible from a 45° angle.
4. **Open the Shape Key panel** (Properties → Object Data → Shape Keys).
   - Select `SK_YJunction` and slowly drag the Value slider from 0 → 1.
   - Select `SK_Web4` and show the 4-soliton grid lattice.
   - Select `SK_Temporal` to show the crests after they have propagated.
5. **Switch to Material Preview** (HDRI lighting) so the Cobalt–Amber attribute
   colour is visible.  Orbit once more.
6. **Stop recording.**

## Viewport compositor tip

If Blender 5.1's Viewport Compositor is enabled (Overlay menu → Compositor),
enable a subtle *Glare → Bloom* pass at 0.15 threshold to make the crest peaks
glow amber — it photographs the wave pattern well for thumbnail purposes.

## file destination

Copy the finished `screen.mp4` to:
```
public/library/videos/scripting/
python-numpy-kadomtsev-petviashvili-kp-ii-1970-exact-web-soliton-hirota-tau-stage-floor-webxr/
screen.mp4
```
