# Screen-Recording Notes — GUE β-Family Spacing Surface

## Software
OBS Studio (v30+) or Windows Game Bar (`Win+G`).

## Scene setup
- Window source: **Blender 5.1** (title bar "gue_spacing_floor.blend")
- Resolution: **1920×1080**
- Frame rate: **30 fps**
- Audio: **off** (uncheck microphone and desktop audio)
- Bitrate: 8 000 kbps (CBR) for clean colour gradients

## Output
Save as: `public/library/videos/scripting/python-numpy-gue-gaussian-unitary-ensemble-montgomery-1973-pair-correlation-sine-kernel-wigner-dyson-beta-family-stage-floor-webxr/screen.mp4`

## What to capture (in order)

1. **Open the file** — File → Open → `gue_spacing_floor.blend`. Pause 2 s on
   the loaded scene showing the Basis β-family surface from the default
   isometric view. The cobalt–amber gradient (cobalt front/bottom = Rayleigh
   β≈0, amber back/top = GSE β=4) should be clearly visible.

2. **Rotate to a 3/4 view** — Numpad `5` (toggle ortho/persp), then drag to
   show the ridge that shifts rightward and narrows as β increases. The peak
   at s≈0.55 (GOE, amber) is lower and wider than the peak at s≈0.93 (GUE)
   and s≈1.31 (GSE). Pause 3 s.

3. **Shape Keys panel** — Properties → Object Data (mesh icon) → Shape Keys.
   Select each key in turn and scrub the Value slider 0→1:
   - **Basis → SK_GOE**: surface collapses to a single ridge (GOE P(s))
   - **SK_GOE → SK_MC**: ridge dissolves into the Monte Carlo scatter cloud;
     individual matrix fluctuations are visible but the overall bell follows
     the GUE analytic curve
   - **SK_MC → SK_Poisson**: cloud reorganises into the flat exponential decay
     from left to right — contrast with the GUE bell (peak ≠ s=0)
   Capture each transition over ~3 s.

4. **Colour explanation pan** — zoom into the front-left corner (β≈0 Rayleigh
   end, cobalt) and slowly pan to the back-right corner (β=4 GSE, amber),
   pausing to show the peak position shifting right. Voiceover or on-screen
   text: "Each row is a different symmetry class β."

5. **Close-up of the GUE row** — scrub to β=2 (middle of y-axis). The row at
   y=50% shows the classic (32/π²)s²·exp(−4s²/π) bell. Compare with the
   β=1 (GOE) row at y=25% and β=4 (GSE) at y=100%.

6. **Zoom to MC cloud** — select SK_MC, value=1. Rotate to top-down view
   (Numpad 7). The scatter cloud should show GUE-shaped density: sparse near
   s=0 (level repulsion), peak near s≈0.9, tail toward s=3–4.

7. **Final hold** — return to Basis, isometric view. Hold 3 s. Stop recording.

## Total duration
~60–90 s of raw footage. Trim to 30–45 s for the tutorial page `screen.mp4`.

## Tips
- Use Blender's **Viewport Shading → Material Preview** (Z key → Material) to
  show the cobalt–amber colour attribute correctly. Solid mode does not show
  colour attributes unless Colour = Vertex Colour is selected in the overlays.
- If the mesh appears too flat, select the object, go to Object Data → Shape
  Keys, ensure Basis is selected, and verify that Z_SCALE = 0.40 in the script.
  The surface should have ~40 cm peak-to-valley range at WORLD_SCALE = 4 m.
