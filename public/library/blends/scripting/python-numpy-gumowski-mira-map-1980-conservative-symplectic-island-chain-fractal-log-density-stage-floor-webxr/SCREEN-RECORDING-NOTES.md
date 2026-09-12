# Screen-Recording Notes — Gumowski–Mira Map (1980)

**Target file:**
`public/library/videos/scripting/python-numpy-gumowski-mira-map-1980-conservative-symplectic-island-chain-fractal-log-density-stage-floor-webxr/screen.mp4`

---

## Setup

1. Open Blender 5.1.
2. Open the **Scripting** workspace.
3. Load `blueprint.py` in the text editor panel.
4. Open OBS Studio (or Xbox Game Bar on Windows).

---

## OBS scene configuration

| Setting | Value |
|---------|-------|
| Source | Window capture → Blender |
| Resolution | 1920 × 1080 |
| Frame rate | 30 fps |
| Audio | **Off** (mute mic and desktop audio entirely) |
| Output format | MP4 / H.264, CRF 18 |
| Output file | `screen.mp4` (rename to the slug path above after recording) |

---

## Recording sequence

### Part A — Script execution (~40 s)

1. Start recording.
2. Press **Run Script** (▶) in the Blender text editor.
3. Keep the **Info** bar and **System Console** visible so viewers see the
   four progress lines:
   ```
   [GumowskiMira] Computing Basis (μ=−0.496) …
   [GumowskiMira] Computing SK_Ring (μ=−0.12) …
   [GumowskiMira] Computing SK_Web (μ=−0.45) …
   [GumowskiMira] Computing SK_Fish (μ=0.008) …
   [GumowskiMira] Done — 'GumowskiMira_Floor' 16384V 16129Q
   ```
4. Do **not** move the mouse during computation — viewers should see the
   console updating naturally without distracting cursor movement.

### Part B — Shape key sweep (~3 min)

1. Switch to the **Layout** workspace.
2. Select `GumowskiMira_Floor` in the Outliner.
3. Open **Object Data Properties** → **Shape Keys** in the Properties panel.
4. Slowly drag each shape key slider from 0 → 1 → 0 (hold each extreme for
   3–4 seconds):

   | Transition | What to point out |
   |------------|-------------------|
   | Basis → SK_Ring | Island chains morph to concentric rings; note the symmetric "flower" topology |
   | SK_Ring → SK_Web | Rings fragment into a denser web; chaotic regions grow |
   | SK_Web → SK_Fish | Web collapses to a single large central elliptic island |
   | SK_Fish → Basis | Return to the full galaxy structure |

### Part C — Viewport colour and shading (~1 min)

1. Set viewport shading to **Material Preview** (sphere icon, top-right of 3D viewport).
2. Orbit the camera to show the cobalt–amber `GM_Density` gradient:
   - Cobalt = sparse phase-space cells (chaotic sea between islands)
   - Amber = dense cells (KAM tori, fixed-point neighbourhoods)
3. Briefly toggle **Rendered** mode to show the emission material.

### Part D — Numpad views (~30 s)

| Numpad key | View | Purpose |
|------------|------|---------|
| **7** | Top (orthographic) | Classic Poincaré-section view — shows the full island chain structure without perspective distortion |
| **1** | Front | Shows Z height variation across the density field |
| **5** | Toggle ortho/persp | Comparison of how perspective affects the appearance |
| **4 / 6** | Rotate left / right | Slow orbit to show the height relief from different angles |

### Part E — GLB in File Browser (~20 s)

1. Open the **File Browser** workspace.
2. Navigate to the blend file directory to show `gumowski_mira_floor.glb` has
   been written — confirms the export step ran.

---

## Stop recording

Stop the OBS recording.  In OBS: **Stop Recording** → rename the output file to
`screen.mp4` → move it to the target path above.

---

## Tips

- Blender's **System Console** (Window → Toggle System Console on Windows,
  or launch from terminal on macOS/Linux) shows print statements in real time —
  worth keeping visible during Part A.
- If the shape key panel isn't visible, check **Properties** → **Object Data**
  (the green triangle icon) → expand **Shape Keys**.
- For Part C, pressing **Z** opens the pie menu for quick shading switches.
