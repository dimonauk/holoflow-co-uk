# Screen-Recording Notes — φ⁴ Kink-Antikink Floor

## What you are recording

The space-time collision carpet of two topological kinks in φ⁴ field theory.
The horizontal axis is space, the vertical (depth) axis is time, and the height
encodes the scalar field value φ: deep cobalt = vacuum (φ = −1), amber ridge
= kink interior (φ ≈ +1).

Shape key to demonstrate on camera in this order:

1. **Basis** (v = 0.10) — both kinks captured into a bion (oscillating bound state).
   The two ridges meet near the front of the floor and never separate; the centre
   vibrates with a Lorentz-contracted kink mass frequency ω ≈ √8/3 ≈ 1.63.

2. **SK_TwoBounce** (v = 0.193) — inside the two-bounce resonance window.
   The ridges meet, reflect, meet again, then escape to infinity.  Look for the
   characteristic "W" trace where the worldlines touch twice before diverging.

3. **SK_Escape** (v = 0.40) — well above v_c ≈ 0.260.  Single-pass collision,
   then both kinks continue outward leaving a central radiation burst that
   decays as an amber-teal halo.

4. Cycle back to **Basis** so viewers see the contrast.

---

## OBS settings

| Setting | Value |
|---|---|
| Source | Window capture → Blender |
| Resolution | 1920 × 1080 |
| Frame rate | 30 fps |
| Audio | Disabled |
| Output | Screen-recording-notes target: `screen.mp4` |

## Steps

1. Open `phi4_kink_floor.blend` in Blender 5.1.
2. Switch to the **Layout** workspace; select `phi4_kink_floor`.
3. In the **Object Properties → Shape Keys** panel, set all keys to 0 then
   slowly move Basis → 1. The bion pattern appears.
4. Start OBS recording.
5. Crossfade to SK_TwoBounce over ~3 seconds; pause to let viewers study
   the double-bounce trace.
6. Crossfade to SK_Escape over ~3 seconds; pause on the clean escape + radiation.
7. Optional: rotate the viewport with middle-mouse to show the height variation
   from a low angle.
8. Stop OBS.  Trim to ≤ 90 seconds.  Export as `screen.mp4` (H.264, CRF 23).

## Where to save

```
public/library/videos/scripting/
python-numpy-phi4-kink-antikink-collision-resonance-windows-campbell-1983-
space-time-height-field-stage-floor-webxr/
  screen.mp4
  viewport.mp4   ← produced by record.py, already there
```
