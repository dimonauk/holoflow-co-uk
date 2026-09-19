# Screen Recording Notes — 3-State Potts Model Floor

**Target file:** `screen.mp4`
**Destination:** `public/library/videos/scripting/python-numpy-potts-model-3-state-2d-wu-1982-self-dual-exact-tc-checkerboard-metropolis-three-color-domain-height-field-stage-floor-webxr/screen.mp4`

---

## OBS / Game Bar setup

| Setting | Value |
|---|---|
| Source | Window Capture → Blender 5.1 |
| Resolution | 1920 × 1080 |
| Frame rate | 30 fps |
| Audio | Disabled |
| Format | MP4 / H.264 |
| Output path | see Destination above |

---

## Recording steps

1. **Open Blender 5.1.** Close the splash screen.
2. Open the Scripting workspace (`+ → Scripting`).
3. Open `blueprint.py` and press **Run Script**.
   Watch the terminal for `[DONE] Object 'potts3_floor' created`.
4. Switch to the **3D Viewport**. Press `Numpad 5` (orthographic), `Numpad 7` (top), then tumble to a 3/4 perspective with Middle Mouse Drag.
5. You should see the cobalt–teal–amber terrace-style height field.
6. **Start OBS recording.**
7. In the Properties panel → Object Data → Shape Keys, scrub through the four shape keys one by one:
   - **Basis** (T = 0.50 Tc ≈ 0.498 J/k_B) — large flat domains of cobalt, teal, or amber with sharp domain walls
   - **SK_Critical** (T = Tc ≈ 0.995 J/k_B) — fractal mosaic with three-color domain boundaries at all scales
   - **SK_HotCrit** (T = 1.50 Tc ≈ 1.493 J/k_B) — patchy, domains dissolved, short-range clusters only
   - **SK_HighT** (T = 3.00 Tc ≈ 2.985 J/k_B) — fully disordered salt-and-pepper of all three states
8. Hold each shape key at 1.0 for ~5 seconds, then crossfade to the next.
9. **Stop OBS recording.** Trim to ~60 seconds.

---

## What the viewer should see

- **Below Tc**: Three distinct terraced height levels (cobalt plateau, teal plateau, amber plateau) separated by sharp walls. Domain size grows as T falls below Tc.
- **At Tc**: The classic critical mosaic — fractal boundaries between all three states, no characteristic domain size, power-law correlations G(r) ~ r^{−4/15}. This is the `c = 4/5` CFT fixed point.
- **Above Tc (1.5×)**: Domains break up, short-range clusters of each state remaining.
- **High-T**: Each site independently and randomly picks a state; equal populations of cobalt, teal, amber.

---

## Tips

- Solid shading with the **Colour** attribute overlay makes the three-state mosaic most visible.
- If the floor looks dark, check **Emission Strength ≥ 2.0** in the Potts3Mat material.
- The shape-key slider lives at **Properties → Object Data Properties → Shape Keys → Value** (not the top Influence slider).
- The `SK_Critical` shape key is the visually richest — spend extra time here.
