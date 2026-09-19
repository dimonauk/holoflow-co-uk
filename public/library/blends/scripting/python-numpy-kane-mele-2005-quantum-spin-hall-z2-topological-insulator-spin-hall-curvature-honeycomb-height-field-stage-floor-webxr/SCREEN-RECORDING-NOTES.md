# Screen Recording Notes — Kane-Mele QSH Floor

## Software
OBS Studio 30+ or Windows Game Bar (`Win+G`).

## Blender setup before recording
1. Run `blueprint.py` via Blender's Text Editor → Run Script.
2. Confirm `kane_mele_floor` object appears in the viewport.
3. Switch to **Rendered** viewport shading (Eevee Next).
4. Set viewport resolution to **1920 × 1080** via View → Viewport Render Image
   or drag the viewport to fill the full monitor.

## OBS settings
| Setting | Value |
|---|---|
| Source | Window Capture → Blender |
| Resolution | 1920 × 1080 |
| Frame rate | 30 fps |
| Format | MP4 (H.264) |
| Bitrate | 8000 kbps |
| Audio | **Off** |

## What to record
1. (~0–5 s) Show the **Basis** floor from a high-angle view — two amber peaks (K and K′) symmetric and equal height, cobalt valleys between.
2. (~5–12 s) Orbit slowly around the mesh. Pause to show both amber peaks face-on, then rotate to a grazing angle that shows the height difference.
3. (~12–20 s) In the Properties panel, click **Object Data → Shape Keys** and drag **SK_StrongSOC** value from 0 to 1 (stronger SOC → sharper, taller peaks).
4. (~20–30 s) Drag **SK_NearCrit** to 1 — one peak begins to collapse (system approaching the topological phase boundary |M| = M_c).
5. (~30–40 s) Drag **SK_Trivial** to 1 — both peaks collapse entirely, the floor flattens (trivial insulator, ν = 0).
6. (~40–45 s) Reset all shape keys to 0, return to Basis — two equal amber peaks restored.

## Output file
Save to: `public/library/videos/scripting/kane-mele-2005-quantum-spin-hall-z2-topological-insulator/screen.mp4`

## Notes
- The EQUAL amplitude of both K and K′ peaks (unlike Haldane where M≠0 breaks the symmetry) is the visual signature of TRS and the QSH phase. Frame it clearly in at least one shot.
- The SK_NearCrit key shows the gap closing at ONE Dirac point first — a key pedagogical moment. Slow down the scrub here.
