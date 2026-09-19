# Screen Recording Notes — 1D FDTD Maxwell / Yee 1966

## OBS / Game Bar setup

| Setting | Value |
|---|---|
| Capture source | Window — Blender |
| Resolution | 1920 × 1080 |
| Frame rate | 30 fps |
| Audio | Off |
| Output format | MP4 / H.264 |
| Output file | `screen.mp4` (same folder as this file) |

## What to record (~4–6 minutes)

### 1. Run the blueprint (1–2 min)

1. Open Blender 5.1. New file → delete the default cube.
2. Switch to the **Scripting** workspace.
3. Open `blueprint.py`.
4. Press **Run Script** (or Alt+P inside the text editor).
5. Console shows four simulation runs printing progress lines.
6. Script finishes: `[FDTD] blueprint complete — blend + glb saved.`

### 2. Inspect the space–time height field (1 min)

1. Switch to **Layout** workspace.
2. Select `fdtd_field_floor` in the Outliner.
3. Press **Z** → **Rendered** shading.
4. Go to **Properties → Data → Shape Keys** and scrub each key from 0 to 1:
   - **Basis**: diagonal amber streaks (wave-fronts) bouncing off PEC walls
   - **SK_Dielectric**: bright incident strip on left, dimmer transmitted strip
     on right (slower in ε_r=4 medium), weak reflected echo going left
   - **SK_Cavity**: bright vertical amber bands — standing-wave antinodes
   - **SK_PML**: clean triangular wave packet, no reflections at the edges

### 3. Orbit the mesh (30 s)

1. Use middle-mouse drag to orbit around the floor.
2. Show the height profile from a low angle: the space–time "X" pattern of
   the bouncing pulses in Basis is clearly visible as ridges.

### 4. Explain the x/y axes on camera (30 s)

- x-axis (left → right): spatial position along the 1D waveguide (128 cells)
- y-axis (bottom → top): time advancing forward (128 snapshots)
- Height / colour: E_z field amplitude (cobalt = quiet, amber = peak)

### 5. Run record.py (optional, 30 s)

1. Open `record.py` in the Scripting workspace.
2. Press **Run Script**.
3. Blender renders 150 frames to `viewport.mp4` — show the render progress bar.

## Tips

- Zoom in on the Basis shape key and tilt the view to show the "chevron"
  pattern of the two reflected pulses — this is the most photogenic moment.
- For the SK_Cavity key, zoom out slightly so the full standing-wave pattern
  (horizontal colour banding) is visible across the whole mesh.
- The SK_PML key is most striking in side view: the wave packet completely
  disappears at both edges with no trailing echo.
