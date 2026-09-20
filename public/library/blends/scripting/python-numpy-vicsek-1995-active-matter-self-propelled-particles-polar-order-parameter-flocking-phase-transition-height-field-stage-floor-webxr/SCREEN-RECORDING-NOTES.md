# Screen-Recording Notes — Vicsek Active-Matter Flocking

These notes guide you through capturing `screen.mp4` for this library entry.
`viewport.mp4` is generated automatically by `record.py`; `screen.mp4` shows
the live Blender scripting session so viewers can follow every step.

## Capture settings

| Setting | Value |
|---|---|
| Source | Window capture — Blender (fullscreen or maximised) |
| Resolution | 1920 × 1080 |
| Frame rate | 30 fps |
| Audio | Off (no mic required) |
| Output | `screen.mp4` |

## OBS Studio

1. **Sources → + → Window Capture** → select the Blender window.
2. Right-click canvas → **Transform → Fit to Screen**.
3. Output settings: MP4 · H.264 · CRF 22.
4. **Start Recording**.

## Windows Game Bar (Win + G)

1. Open Blender, press **Win + G** → Record button.
2. Confirm the capture target is Blender.
3. Press **Win + Alt + R** to begin.

## What to show (target: 8–12 minutes)

1. **File → New → General** — blank scene.
2. Switch to the **Scripting** workspace (top tab row).
3. **New** → paste `blueprint.py` in full.
4. Walk through the key sections:
   - Top docstring: Vicsek 1995 model, η-noise convention, phase transition.
   - `_step()`: why `np.bincount` beats `np.add.at` for cell-list accumulation;
     the 9-roll 3×3 neighbourhood sum; arctan2 alignment update.
   - `run_vicsek()`: burn-in rationale (N_SETTLE = 2000 to reach steady state);
     accumulation over N_COLLECT = 60 snapshots; Gaussian smoothing.
   - Four shape keys: Basis (η=0.10 ordered), SK_Bands (η=0.28 bands),
     SK_Crit (η=0.36 near-critical), SK_Dis (η=0.70 disordered).
5. **Run Script** (▶). Console prints progress and ✓ on completion.
6. Switch to the **Layout** workspace; select `vicsek_floor`.
7. Open **Properties → Object Data → Shape Keys**.
   Drag each value slider 0 → 1:
   - Basis:    near-flat amber plateau (high, uniform order).
   - SK_Bands: stripes — amber bands crossing a cobalt sea.
   - SK_Crit:  patchy medium surface (large-fluctuation regime).
   - SK_Dis:   flat cobalt floor (Φ ≈ 0, completely disordered).
8. Check **Properties → Object Data → Color Attributes** — show `Vicsek_Order`.
9. Press **Numpad 7** (top view) while cycling shape keys; note the stripe
   orientation in SK_Bands relative to the mean flock direction.
10. **File → Export → glTF 2.0** — confirm Draco compression + morph targets.

## Stop and trim

Cut the Blender loading screen at the start and any pauses longer than 8 s.
Save output as `screen.mp4` in:

```
public/library/videos/scripting/
  python-numpy-vicsek-1995-active-matter-self-propelled-particles-polar-order-parameter-flocking-phase-transition-height-field-stage-floor-webxr/
    screen.mp4
```
