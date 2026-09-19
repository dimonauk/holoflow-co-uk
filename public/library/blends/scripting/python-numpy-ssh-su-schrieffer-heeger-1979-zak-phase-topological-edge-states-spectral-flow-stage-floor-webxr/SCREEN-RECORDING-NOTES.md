# Screen Recording Notes — SSH Spectral-Flow Stage Floor

## Software
- OBS Studio 30+ or Windows Game Bar
- Blender 5.1 (viewport render or interactive session)

## Setup
1. Run `blueprint.py` inside Blender 5.1 (Scripting workspace → Run Script).
2. Switch to the 3D Viewport in **Material Preview** or **Rendered** shading.
3. Set viewport shading colour source to **Vertex** (or leave on Material — SSH_Eig attribute drives the shader).
4. Open the Shape Keys panel (Properties → Object Data → Shape Keys).
5. Resize Blender window to exactly 1920×1080 (or your native resolution).

## OBS Scene
- **Source**: Window Capture → Blender
- **Resolution**: 1920×1080 (crop to Blender window if needed)
- **Frame rate**: 30 fps
- **Audio**: OFF (no audio needed)
- **Output format**: MP4 / H.264

## What to capture (screen.mp4 — target 30–60 s)
1. Show the mesh in Material Preview shading with the cobalt–amber gradient visible.
2. In the Shape Keys panel, slowly scrub the **SK_Periodic** key from 0 → 1 → 0:
   - Observe: zero-energy amber modes disappear when periodic BC removes the boundary.
3. Scrub **SK_NNN** from 0 → 1 → 0:
   - Observe: amber threads shift slightly from the mid-gap z-level (edge-state energy lifts).
4. Scrub **SK_SymBreak** from 0 → 1 → 0:
   - Observe: amber threads merge into bulk — chiral symmetry broken, topological protection gone.
5. Return to Basis (SK_Periodic = SK_NNN = SK_SymBreak = 0).
6. Pan the camera around the mesh to show the 3D spectral-flow surface.

## Output path
`public/library/videos/scripting/python-numpy-ssh-su-schrieffer-heeger-1979-zak-phase-topological-edge-states-spectral-flow-stage-floor-webxr/screen.mp4`

## Tips
- The zero-mode threads look best with a slightly angled overhead view (azimuth ≈ 30°, elevation ≈ 55°).
- Use EEVEE for real-time playback; ambient occlusion adds depth to the band-gap valley.
- If scrubbing shape keys feels sluggish, lower the subdivision level is not needed — the mesh is exactly 128×128 quads and should be fast at any setting.
