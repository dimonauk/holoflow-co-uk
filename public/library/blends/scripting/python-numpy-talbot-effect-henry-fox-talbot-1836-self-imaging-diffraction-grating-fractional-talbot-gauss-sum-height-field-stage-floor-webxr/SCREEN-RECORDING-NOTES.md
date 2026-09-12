# Screen-Recording Notes — Talbot Effect (1836) Floor

**Target file:**
`public/library/videos/scripting/python-numpy-talbot-effect-henry-fox-talbot-1836-self-imaging-diffraction-grating-fractional-talbot-gauss-sum-height-field-stage-floor-webxr/screen.mp4`

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
| Output file | `screen.mp4` (rename to slug path above after recording) |

---

## Recording sequence

### Part A — Script execution (~30 s)

1. Start recording.
2. Press **Run Script** (▶) in the Blender text editor.
3. Keep the **Info** bar and **System Console** visible to capture:
   ```
   [Talbot] Computing Basis (binary grating) …
   [Talbot] Computing SK_Sine (sinusoidal grating) …
   [Talbot] Computing SK_Blazed (blazed grating) …
   [Talbot] Computing SK_Phase (phase grating) …
   [Talbot] Done — 'Talbot_Floor' 16384V 16129Q
   ```
4. Do not move the mouse during computation.

### Part B — Shape key sweep (~3 min)

1. Switch to the **Layout** workspace.
2. Select `Talbot_Floor` in the Outliner.
3. Open **Object Data Properties → Shape Keys**.
4. Slowly drag each shape key slider 0 → 1 → 0 (hold extremes for 3–4 s):

   | Transition | What to point out |
   |------------|-------------------|
   | Basis → SK_Sine | Many harmonics collapse to one: complex carpet becomes simple two-band pattern |
   | SK_Sine → SK_Blazed | Sawtooth adds phase asymmetry; odd+even harmonics → richer carpet |
   | SK_Blazed → SK_Phase | Phase grating: amplitude is flat at grating plane (z=0) but complex carpet appears at z=z_T/4 |
   | SK_Phase → Basis | Return to the classic binary Talbot carpet |

### Part C — Viewport colour and shading (~1 min)

1. Set viewport shading to **Material Preview** (sphere icon).
2. Orbit to show the cobalt–amber `TC_Intensity` gradient:
   - **Cobalt** = intensity minima (dark bands, destructive interference)
   - **Amber** = intensity maxima (bright self-image bands)
3. Toggle to **Rendered** mode to show emission material.

### Part D — Numpad views (~30 s)

| Numpad key | View | Purpose |
|------------|------|---------|
| **7** | Top (orthographic) | Shows the Talbot carpet as a 2D fringe pattern — pure x-z view |
| **1** | Front | Shows Z height variation: bright self-images rise as peaks |
| **5** | Toggle ortho/persp | Compare how perspective distorts the carpet pattern |
| **4 / 6** | Rotate left / right | Orbit to show relief from different azimuths |

### Part E — GLB in File Browser (~20 s)

1. Open the **File Browser** workspace.
2. Navigate to the blend file directory and show `talbot_floor.glb`.

---

## Stop recording

Stop OBS recording → rename output to `screen.mp4` → move to target path above.

---

## Tips

- **System Console** (Window → Toggle System Console on Windows, or terminal on
  macOS/Linux) shows the four `[Talbot]` progress lines during Part A.
- If the carpet looks flat, ensure the active shape key is at value 1.0 (not 0.0).
- For Part C press **Z** to open the pie menu for quick shading switches.
- The **binary carpet** (Basis) shows the richest structure — spend extra time
  here demonstrating z_T and z_T/2 self-images in the height field.
