# Screen Recording Notes — KPZ Stage Floor
## `screen.mp4` via OBS Studio or Windows Game Bar

These notes are for Dimona to capture `screen.mp4` — the human-operated
Blender session recording to pair with the auto-rendered `viewport.mp4`.

---

## Setup (do once)

**OBS Studio (recommended)**

1. Add a *Window Capture* source → select `Blender` window.
2. Set canvas resolution to **1920 × 1080**.
3. Output settings: MP4 · H.264 · CRF 18 · 30 fps · **no audio**.
4. Output file: name it `screen.mp4` and place it at  
   `public/library/videos/scripting/python-numpy-kpz-kardar-parisi-zhang-1986-stochastic-surface-growth-universality-height-field-stage-floor-webxr/screen.mp4`

**Windows Game Bar (Xbox Game Bar)**  
Win + G → Capture → Start recording (Win + Alt + R).  
Move the file to the path above and rename it `screen.mp4`.

---

## What to record (approx. 3–5 min)

### 1 — Open the file
- Open Blender 5.1.
- File → Open → navigate to `kpz_floor.blend`.

### 2 — Narrate the mesh
- In the viewport, zoom out to see the full stage floor.
- Switch to Material Preview (Z → Material Preview) to see the cobalt–amber colouring.
- Point out: "This is the Edwards–Wilkinson limit — the surface looks like gentle,
  correlated hills. There's no sharp ridging yet."

### 3 — Activate the KPZ shape key
- Select the `KPZ_Floor` object → Properties → Object Data → Shape Keys.
- Set `SK_KPZ` value to 1.0 (slide slowly from 0 to 1).
- Point out: "As the KPZ nonlinearity switches on, watch the crests sharpen.
  The tilted-surface growth term breaks up–down symmetry."

### 4 — Show the strong-noise variant
- Reset `SK_KPZ` to 0, set `SK_Strong` to 1.
- Point out: "Doubling the noise amplitude (σ=2) amplifies the roughness
  without changing the universality class — it just accelerates the dynamics."

### 5 — Show the long-run morphology
- Reset all to 0, set `SK_Long` to 1.
- Point out: "After 1000 steps (t=20) the pattern coarsens: fewer but deeper
  channels, consistent with KPZ's β ≈ 0.24 scaling law."

### 6 — Inspect the attribute
- Vertex Paint mode or Spreadsheet editor → show `KPZ_Height` attribute.
- Return to Object mode, briefly look at the node material (MixShader chain).

### 7 — Run the blueprint (optional but ideal)
- Scripting workspace → open `blueprint.py` → Run Script.
- Let the viewer see it generate the mesh from scratch (~10 s in Blender 5.1).
- Switch back to 3D viewport to reveal the result.

---

## Editing tips

- Keep all four shape-key demonstrations in one continuous take if possible.
- No need to narrate the code line by line — showing the result is enough.
- A slow zoom across the long-run surface (SK_Long) makes a good outro shot.
