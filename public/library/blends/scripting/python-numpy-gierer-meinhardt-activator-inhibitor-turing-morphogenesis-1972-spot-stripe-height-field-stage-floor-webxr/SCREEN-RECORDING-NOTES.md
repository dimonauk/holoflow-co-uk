# Screen Recording Notes — Gierer-Meinhardt Floor

**Target file:** `public/library/videos/scripting/python-numpy-gierer-meinhardt-activator-inhibitor-turing-morphogenesis-1972-spot-stripe-height-field-stage-floor-webxr/screen.mp4`

## Setup

| Setting | Value |
|---------|-------|
| Software | OBS Studio 30+ or Xbox Game Bar (Win 11) |
| Window capture | Blender — 3D Viewport (full-screen, numpad 0 = camera view) |
| Resolution | 1920 × 1080 |
| Frame rate | 30 fps |
| Audio | **Off** |
| Output format | MP4 / H.264, CRF 18–22 |

## Blender viewport setup before recording

1. Open the `.blend` file produced by `blueprint.py`.
2. Set **Viewport Shading** to **Material Preview** (press `Z` → *Material Preview*,
   or click the sphere icon in the top-right of the 3D viewport).
3. Press **Numpad 0** to enter camera view.
4. In **Overlays**, disable *Axes*, *Grid*, and *Statistics* for a clean view.
5. Confirm Eevee Next renderer is active (Properties → Render → Render Engine = EEVEE Next).
6. Enable **Bloom** in Eevee settings (threshold 0.60, intensity 0.40).

## Recording steps

1. Start OBS / Game Bar → *Window Capture* → select Blender.
2. Press **Start Recording**.
3. In Blender, play the timeline (Spacebar or `▶`).
   - The animation runs 300 frames (10 s) at 30 fps.
   - Shape keys morph: Basis spots → labyrinthine stripes → dense spots.
4. After frame 300, press **Stop Recording**.
5. Trim to exactly 10 s in your editor; save as `screen.mp4`.

## What to show

- **Seconds 0–2**: static Basis (isolated cobalt spots on amber field) — point out
  the characteristic spot spacing (Turing wavelength λ_c ≈ 10–14 grid units).
- **Seconds 2–5**: morph into SK_Labyrinthine — spots elongate and connect into
  stripes; narrate the lower ν creating wider inhibitor radius.
- **Seconds 5–7**: hold labyrinthine pattern — zoom slightly in the viewport.
- **Seconds 7–10**: morph to SK_Dense — denser activator peaks; higher ρ₀ seeds
  more nucleation centres.

## Tips

- If the floor looks too flat, nudge **Emission Strength** to 2.5 in the material.
- Viewport AA can be increased to 32× in Eevee Next for smoother colour gradients.
- If recording lags, lower resolution to 1280 × 720 while recording; upscale in post.
