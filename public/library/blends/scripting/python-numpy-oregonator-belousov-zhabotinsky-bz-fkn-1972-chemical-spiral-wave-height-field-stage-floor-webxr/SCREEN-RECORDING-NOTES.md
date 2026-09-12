# Screen Recording Notes — BZ Oregonator Floor

## Software
OBS Studio 30+ or Windows Game Bar (`Win + G`).

## Setup

| Setting          | Value                            |
|------------------|----------------------------------|
| Source           | Window Capture → Blender 5.1     |
| Resolution       | 1920 × 1080                      |
| Frame rate       | 30 fps                           |
| Output format    | MP4 / H.264                      |
| Audio            | Off (no narration required)      |

## Output path
Save to:
```
public/library/videos/scripting/
python-numpy-oregonator-belousov-zhabotinsky-bz-fkn-1972-chemical-spiral-wave-height-field-stage-floor-webxr/
screen.mp4
```

## Shot list (approx. 90 seconds)

1. **Open & explain** (0–15 s)  
   Show the `.blend` freshly opened. Viewport in Material Preview mode.
   Rotate slightly so height relief is visible.

2. **Spiral Basis** (15–30 s)  
   Select the `bz_oregonator_floor` object. In Properties → Object Data → Shape Keys,
   click **Basis**. Orbit the viewport 360° at low elevation to show the four spiral arms.

3. **SK_Fast morphed in** (30–50 s)  
   Drag `SK_Fast` value from 0 → 1. Watch the spiral arms compress.
   Explain: ε halved → oscillation twice as fast → wavelength halved.

4. **SK_Rings** (50–65 s)  
   Set SK_Fast → 0, drag SK_Rings → 1.
   Show the concentric target rings from the pacemaker IC.

5. **SK_Meander** (65–80 s)  
   Set SK_Rings → 0, drag SK_Meander → 1.
   Show the turbulent breakup pattern (higher f, random IC).

6. **GLB round-trip** (80–90 s)  
   Open `bz_oregonator_floor.glb` in a WebXR viewer or Three.js preview.
   Optionally show morph-target slider working in browser.

## Tips
- Use Solid shading with **Vertex Colour** display mode to show the cobalt-amber colour.
- Or Material Preview with HDRI for nicer lighting.
- Disable overlays (View menu) for a cleaner shot.
