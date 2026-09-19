# Screen Recording Notes — Kuramoto Phase Oscillator Model

## OBS / Game Bar setup

| Setting | Value |
|---|---|
| Capture source | Window — Blender |
| Resolution | 1920 × 1080 |
| Frame rate | 30 fps |
| Audio | Off |
| Output format | MP4 / H.264 |
| Output file | `screen.mp4` (same folder as this file) |

## What to record (~3–5 minutes)

### 1. Run the blueprint (1 min)

1. Open Blender 5.1. New file → delete the default cube.
2. Switch to the **Scripting** workspace.
3. Open `blueprint.py`.
4. Press **Run Script** (or Alt+P inside the text editor).
5. Watch the console — four simulation runs print progress lines.
6. Script finishes: `[Kuramoto] blueprint complete — blend + glb saved.`

### 2. Inspect the mesh (30 s)

1. Switch to **Layout** workspace.
2. Select `kuramoto_phase_floor` in the Outliner.
3. In the **Properties** panel → **Data** tab → scroll to **Shape Keys**.
4. Slowly scrub each shape key value from 0 to 1:
   - **Basis** (K=1.2): swirling spiral-wave landscape
   - **SK_LowK** (K=0.3): rough, turbulent, no coherent structure
   - **SK_HighK** (K=3.5): nearly flat, smooth rolling waves — synchronised
   - **SK_BroadW** (K=1.2, wide ω): more fragmented than Basis

### 3. Shader and colour (30 s)

1. Press **Z** → select **Material Preview** or **Rendered** shading.
2. Rotate the view to show the cobalt-to-amber gradient:
   - cobalt = disordered regions (low local order parameter)
   - amber = synchronised clusters (high local order parameter)
3. Pan slowly across the Basis landscape to show spiral arms.

### 4. Run record.py (30 s — optional)

1. Open `record.py` in the Scripting workspace.
2. Press **Run Script**.
3. Blender renders 150 frames to `viewport.mp4` — show the render progress.

## Tips

- Set Blender's **Viewport Shading** to **Rendered** before recording step 3.
- Zoom in on the shape-key spiral pattern for the thumbnail moment.
- The near-critical Basis key (K=1.2) produces the most photogenic spirals.
