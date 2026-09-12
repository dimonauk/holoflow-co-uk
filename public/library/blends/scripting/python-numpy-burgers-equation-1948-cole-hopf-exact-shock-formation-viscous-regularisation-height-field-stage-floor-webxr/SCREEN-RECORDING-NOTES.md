# Screen-Recording Notes — Burgers Equation Shock Floor

**OBS Studio / Windows Game Bar setup for `screen.mp4`**

## Before you start

1. Open Blender 5.1.
2. Load `burgers_shock_floor.blend` (built by `blueprint.py`).
3. Switch to the **Layout** workspace; select `burgers_shock_floor`.
4. Set viewport shading to **Material Preview** (Z → Material Preview).
5. Enable **Bloom** in Viewport Overlays → Render Properties → EEVEE bloom.

## OBS settings

| Setting | Value |
|---------|-------|
| Source | Window Capture → Blender |
| Resolution | 1920 × 1080 |
| Frame rate | 30 fps |
| Encoder | H.264 (software) |
| Bitrate | 8000 kbps |
| Audio | **Off** |
| Output file | `screen.mp4` |

## Shot list (≈ 60 seconds total)

| Time | Action |
|------|--------|
| 0–10 s | Top-down view of the **Basis** floor. Pan slowly to reveal the diagonal pre-shock region steepening toward the near-vertical ridge at x = 0, t ≈ 0.32. |
| 10–20 s | Tilt to a low-angle view (Numpad 1 + scroll). Orbit 90° to show the space-time structure — height is velocity, the ridge is the shock. |
| 20–30 s | In the Shape Keys panel (Properties → Object Data → Shape Keys), fade from **Basis** to **SK_HighNu** (ν = 0.100). Show how high viscosity diffuses the profile before a shock can form. |
| 30–40 s | Fade to **SK_LowNu** (ν = 0.005). Pause on the thin, near-vertical ridge — the viscous shock layer, δ ≈ 0.010. |
| 40–50 s | Fade to **SK_NWave** (u₀ = −sin 2πx). Two shocks form simultaneously; trace both ridges with the cursor. |
| 50–60 s | Return to **Basis**; zoom to the shock region. Trace the Rankine-Hugoniot jump: the shock is stationary because u⁺ = −u⁻. |

## Narration cues (for tutorial voiceover)

- **0–10 s**: "Every ridge on this floor is the same equation — Burgers' nonlinear wave steepening — at every moment frozen in time. Taller means faster; steeper means closer to breaking."
- **20–30 s**: "Raise viscosity to 0.1 and diffusion wins: the profile never reaches the critical slope. No shock forms — just a gentle hill that relaxes toward zero."
- **30–40 s**: "Drop viscosity to 0.005 and the shock sharpens to a wall just a few mesh cells wide. That width is δ ≈ 4ν/|Δu| — a balance between steepening and smoothing."
- **40–50 s**: "An N-wave initial condition produces two symmetric shocks that persist side by side — each governed by the same Rankine-Hugoniot jump condition."

## Output destination

Save the recording as:
```
public/library/videos/scripting/
  python-numpy-burgers-equation-1948-cole-hopf-exact-shock-formation-viscous-regularisation-height-field-stage-floor-webxr/
    screen.mp4
```
