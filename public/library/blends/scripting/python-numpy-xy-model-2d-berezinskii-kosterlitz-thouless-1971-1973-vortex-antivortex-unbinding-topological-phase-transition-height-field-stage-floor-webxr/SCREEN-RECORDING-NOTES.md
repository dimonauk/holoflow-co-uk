# Screen Recording Notes — XY Model BKT Floor

**Target file:** `screen.mp4`  
**Destination:** `public/library/videos/scripting/python-numpy-xy-model-2d-berezinskii-kosterlitz-thouless-1971-1973-vortex-antivortex-unbinding-topological-phase-transition-height-field-stage-floor-webxr/screen.mp4`

---

## OBS / Game Bar setup

| Setting | Value |
|---|---|
| Source | Window Capture → Blender 5.1 |
| Resolution | 1920 × 1080 |
| Frame rate | 30 fps |
| Audio | Disabled (no mic, no desktop audio) |
| Format | MP4 / H.264 |
| Output path | see Destination above |

---

## Recording steps

1. **Open Blender 5.1.** Close the splash screen.
2. Open the Scripting workspace (`+ → Scripting`).
3. Open `blueprint.py` and press **Run Script**.  
   Watch the terminal for `[DONE] Object 'xy_bkt_floor' created`.
4. Switch to the **3D Viewport**.  Press `Numpad 5` (orthographic), then `Numpad 1` (front), then `Numpad 0` (camera).
5. Tumble to a 3/4 perspective: `Middle Mouse Drag`.  
   You should see the cobalt-amber height-field plane.
6. **Start OBS recording.**
7. In the Properties panel → Object Data → Shape Keys, scrub through the four shape keys one by one:
   - **Basis** (T = 0.36 J/k_B) — nearly flat, large spin waves
   - **SK_BKT** (T = 0.89 J/k_B) — rippled surface, vortex halos visible as amber spots on cobalt
   - **SK_Unbound** (T = 1.07 J/k_B) — noisy, more vortex peaks scattered across the field
   - **SK_HighT** (T = 2.23 J/k_B) — fully disordered, random salt-and-pepper height map
8. Hold each shape key value at 1.0 for ~5 seconds, then smoothly drag the slider to 0 while dragging the next shape key to 1.
9. **Stop OBS recording.**  Trim to ~60 seconds if needed.

---

## What the viewer should see

- **Below BKT**: The cosine-phase field is nearly smooth with gentle undulations — long spin-wave fluctuations but no free vortices.  Only a handful of tightly bound vortex-antivortex pairs, visible as tiny paired cobalt/amber bumps separated by ~1–2 lattice sites.
- **At BKT**: Characteristic ripples with a power-law texture.  Vortex pairs have grown to ~5–10 lattice spacings; the surface looks like gently crumpled foil.
- **Above BKT**: Free vortices scatter across the field, each a sharp peak or trough, surrounded by radiating phase wings.  The background becomes noisier.
- **High-T**: Completely disordered; the cosine field is essentially white noise mapped to height.

---

## Tips

- Shadeless (solid) shading with the **Colour** attribute overlay makes shape keys pop; HDRI or Eevee bloom makes the amber emission glow.
- If the object appears dark, ensure **Emission Strength ≥ 1.8** in the material (set in blueprint.py).
- The shape-key slider lives at **Properties → Object Data Properties → Shape Keys**.  Drag the `Value` slider, NOT the `Influence` slider at the top.
