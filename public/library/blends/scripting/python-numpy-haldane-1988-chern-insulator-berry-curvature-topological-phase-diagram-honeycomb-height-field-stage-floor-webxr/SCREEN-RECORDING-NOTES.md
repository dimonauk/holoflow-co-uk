# Screen Recording Notes — Haldane Berry Curvature Floor

**Target**: `screen.mp4`  Resolution: 1920×1080  FPS: 30  Audio: OFF

## OBS Setup

1. Source → Window Capture → Blender 5.1
2. Canvas: 1920×1080
3. Output: MP4 / H.264 / CRF 18
4. Audio track: disabled

## What to capture

Open `haldane_floor.blend` in Blender. Switch to **Material Preview** or
**Rendered** viewport. Show each shape key morph manually:

1. **Basis (C=+1)**: scrub `SK_PhiPi4` to 0. Show the two amber curvature
   peaks at K and K′ — these are the topological fingerprint, the BZ solid
   angle concentrating at the Dirac points.

2. **SK_PhiPi4 (weaker)**: ramp SK_PhiPi4 → 1. The peaks shrink as the
   NNN phase φ decreases from π/2 to π/4, reducing sin φ from 1 to 0.707.

3. **SK_NearCrit (approaching transition)**: ramp SK_NearCrit → 1. One peak
   begins to shrink as M approaches M_c = 3√3 t₂. This asymmetry is the
   precursor to the topological phase transition.

4. **SK_Trivial (C=0)**: ramp SK_Trivial → 1. The floor is nearly flat — no
   net Berry curvature, Chern number = 0.

5. Pan the camera around the floor to show depth. Zoom into a curvature peak
   in the Basis state to show the sharp concentration at K/K′.

## Tips

- Use the timeline scrubber to move smoothly between shape keys
- Enable **Bloom** in EEVEE for the amber glow on peaks
- 5–10 seconds per state is sufficient; total screen.mp4 ≈ 60–90 s
