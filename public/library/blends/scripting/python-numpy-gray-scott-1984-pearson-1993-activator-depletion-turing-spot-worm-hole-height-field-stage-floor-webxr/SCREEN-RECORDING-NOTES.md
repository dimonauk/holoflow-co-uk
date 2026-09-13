# Screen Recording Notes — Gray–Scott Pattern Atlas

**Target file:** `public/library/videos/scripting/python-numpy-gray-scott-1984-pearson-1993-activator-depletion-turing-spot-worm-hole-height-field-stage-floor-webxr/screen.mp4`

## OBS Settings

| Setting | Value |
|---------|-------|
| Source | Window Capture → Blender 5.1 |
| Resolution | 1920 × 1080 |
| Frame rate | 30 fps |
| Audio | OFF |
| Output format | MP4 (H.264) |
| Bitrate | 8 000 kbps |

---

## What to record (≈ 6–8 min total)

### 1. Open the script (45 s)
Open `blueprint.py` in Blender's Text Editor panel.  
Scroll slowly through the header docstring. Point out:
- The two PDE lines: ∂u/∂t and ∂v/∂t — note the shared reaction term **uv²**
  appears with opposite signs, so mass is conserved *within the reaction*.
- The fixed-point formula `u* = F+k, v* = √[F(1−u*)/u*]` — explain why
  setting F+k near 0.10 puts the system in a low-u*, high-v* state ripe for
  Turing patterning.
- Why `DU = 0.16` must exceed `DV = 0.08` — short-range activation,
  long-range substrate depletion.

### 2. Parameter constants (45 s)
Scroll to the `PARAMS_*` constants. Show the four (F, k) coordinate pairs
on a hand-drawn or printed copy of Pearson's Fig. 2 (the famous twelve-region
phase diagram). Locate each point: ε, η, ζ, δ. Emphasise that changing F by
0.005 can cross a phase boundary and switch pattern topology entirely.

### 3. Run the simulation (live — 3–5 min)
Click **Run Script**. Leave the progress print lines visible in the Info panel.
While `SK_Worm` is integrating, talk through the explicit Euler step:
- "We're doing 10 000 time steps. Each step: compute `uv²` once, add diffusion
  for u and v separately, clip to [0, 1]. Simple, but it works because the
  CFL number is only 0.16."

### 4. Inspect the result (60 s)
Once the script finishes:
- Switch to **3D Viewport** in **Material Preview** shading.
- Rotate around the mesh to show the cobalt (substrate) / amber (activator) pattern.
- In the **Properties → Object Data → Shape Keys** panel, scrub the `SK_Worm`
  value from 0 → 1 to show the worm pattern morphing in live.
- Do the same for `SK_Hole` (inverted topology — amber becomes the background,
  cobalt holes appear) and `SK_Mitosis` (small bright spots from the central seed).

### 5. GLB export check (30 s)
In the Outliner, expand the mesh object and confirm:
- `GS_V` vertex colour attribute is present.
- Shape keys: Basis, SK_Worm, SK_Hole, SK_Mitosis.
  
Open the Blender Console and confirm the print: `Done — gray_scott_floor.blend + .glb written.`

### 6. Close-up pan (30 s)
Use the numpad to get a top-down orthographic view.
Pan slowly across the Basis (spots) pattern — the viewer should see the
characteristic hexagonal close-packing of amber spots on a cobalt background,
mirroring biological pigmentation patterns (zebrafish stripes, leopard spots).

---

## Timing summary

| Section | Duration |
|---------|----------|
| Script walkthrough | 1:30 |
| Run script (live) | 3:00–5:00 |
| Result inspection | 1:00 |
| GLB check | 0:30 |
| Close-up pan | 0:30 |
| **Total** | **6:30–8:30** |
