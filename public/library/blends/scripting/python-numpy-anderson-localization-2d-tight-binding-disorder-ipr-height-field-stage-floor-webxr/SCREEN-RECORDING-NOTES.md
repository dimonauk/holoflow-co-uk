# Screen Recording Notes — Anderson Localisation

Target file: `public/library/videos/scripting/python-numpy-anderson-localization-2d-tight-binding-disorder-ipr-height-field-stage-floor-webxr/screen.mp4`

## OBS / Windows Game Bar settings

| Setting | Value |
|---|---|
| Window source | Blender 5.1 |
| Resolution | 1920 × 1080 |
| Frame rate | 30 fps |
| Audio | Off |
| Output format | MP4 / H.264 |

## Recording sequence

1. Open Blender 5.1. Load `anderson_localization_floor.blend` (File → Open).
2. Switch to **3D Viewport** in **Material Preview** shading (Z → Material Preview).
3. In the **Properties** panel → **Object Data** → **Shape Keys**, make sure
   all shape keys are at value 0.0 except Basis at 1.0. The cobalt–amber height
   field should be visible with gentle hills — this is the W=0.50 quasi-extended
   eigenstate.
4. **Start recording.**
5. Slowly drag `SK_Medium` (W=2.0) from 0.0 to 1.0 and `Basis` from 1.0 to 0.0
   over about 2 seconds. The height field contracts — localisation is setting in.
6. Continue: drag `SK_Strong` (W=5.0) to 1.0, `SK_Medium` back to 0.0. A sharp
   amber spike appears — the wavefunction is now clearly localised to a few sites.
7. Drag `SK_MaxIPR` (W=8.0) to 1.0 while returning `SK_Strong` to 0.0. The spike
   becomes even more concentrated — highest IPR in the spectrum.
8. Return slowly to Basis. **Stop recording.**
9. Trim to ~10–15 seconds in your editor. Export to `screen.mp4` at 1920 × 1080.

## Notes

- Use **Numpad 7** (Top Ortho) or **Numpad 0** (camera) for a clean overhead shot.
- The colour attribute "Col" is cobalt (|ψ|² = 0) → amber (|ψ|² = peak).
- In Material Preview mode the vertex colours render without a Cycles bake — no
  extra setup needed.
- Transition slowly (2–3 s per key) so viewers can see the qualitative change:
  spread-out quantum wave → concentrated localised state.
- Total target duration: 10–15 seconds.
