# Screen Recording Notes — Allen–Cahn Stage Floor

**Target file:** `public/library/videos/scripting/python-numpy-allen-cahn-phase-field-mean-curvature-motion-allen-cahn-1979-stage-floor-webxr/screen.mp4`

## OBS Settings

| Setting | Value |
|---|---|
| Source | Window Capture → Blender 5.1 |
| Resolution | 1920 × 1080 |
| Frame rate | 30 fps |
| Audio | OFF (no mic) |
| Output format | MP4 (H.264) |
| Bitrate | 8 000 kbps |

---

## What to record (≈ 5–7 min total)

### 1. Open the script (30 s)
Open **blueprint.py** in Blender's Text Editor (top-right panel area).  
Scroll slowly through the header docstring — point out:
- The Allen–Cahn equation block and the `F′(φ) = φ³ − φ` driving force.
- The ETD1 coefficients section; explain why `expm1` is used instead of `exp(z)-1`.

### 2. Named constants (30 s)
Highlight the constants block at the top of `main()`:
- `EPS_BASIS = 0.020` vs `EPS_FINE = 0.012` — show how interface thickness scales.
- `STEPS_COARSE = 600` — demonstrate that 600 × 0.10 dt = t = 60 time units.

### 3. Run the script (1–2 min)
Press **Alt+R** or click **Run Script**.  
Watch the Python console: the final print shows the φ range and vertex count.  
The mesh appears in the 3D viewport — a bumpy terrain of cobalt valleys and amber peaks.

### 4. Shape key preview (2 min)
In Properties → Object Data → Shape Keys, scrub each key from 0 → 1:
- **Basis** (default): fine-scale blobs from t = 10.
- **SK_Coarsened**: fewer, larger domains at t = 70. Note the sharp interfaces.
- **SK_Fine**: ε = 0.012 — fractal-looking, many tiny domains.
- **SK_Broad**: ε = 0.040 — wide, smooth transition zones.

Point out: SK_Coarsened vs SK_Fine shows the ε effect on interface width.

### 5. Vertex colour overlay (30 s)
Switch viewport shading to **Solid → Colour → Attribute**, set attribute to `AC_Phase`.  
The phase field appears: cobalt for φ = −1, amber for φ = +1, gradient at the interfaces.

### 6. Export GLB (30 s)
Show the exported `allen_cahn_floor.glb` path in the info bar.  
Optionally open the GLB in the Holoflow WebXR viewer to confirm it loads as a stage floor.

### 7. Quick Eevee frame (30 s)
Press **F12** to render a single frame. The lit stage floor shows depth in the domain topology.

---

## Recommended narration beats

- "Allen–Cahn is the conservation-free cousin of Cahn–Hilliard — the total amount of each phase can change."
- "Every interface traces a line of zero mean curvature in the final equilibrium."
- "ETD1 treats the stiff linear part exactly — the high-frequency modes decay without a stability constraint."
- "Watch SK_Coarsened: small blobs shrink; large ones remain. That is motion by curvature."
- "Changing ε from 0.020 to 0.012 halves the interface width and reveals a finer internal structure."
