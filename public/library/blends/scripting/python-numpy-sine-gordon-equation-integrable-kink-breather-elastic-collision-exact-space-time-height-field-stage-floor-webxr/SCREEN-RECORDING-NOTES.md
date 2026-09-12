# Screen Recording Notes — Sine-Gordon Stage Floor

These notes are for recording `screen.mp4` using OBS Studio or Windows Game Bar
whilst running the blueprint and record scripts inside Blender 5.1.

---

## Setup

| Setting | Value |
|---------|-------|
| Source | Window Capture → Blender |
| Resolution | 1920 × 1080 |
| Frame rate | 30 fps |
| Audio | Off (silent walkthrough) |
| Output format | MP4 / H.264 |
| Hotkey — Start | F9 (or your chosen OBS hotkey) |
| Hotkey — Stop | F9 |

---

## Suggested recording flow

### Phase 1 — Script execution (≈ 3 min)

1. Open a fresh Blender scene.
2. Switch to the Scripting workspace.
3. Open `blueprint.py` in the text editor (Text → Open → browse to this folder).
4. Hit **Run Script**. The sine-Gordon stage floor builds in the viewport.
5. Let the camera slowly orbit around the finished mesh while the four shape keys
   are visible in the Properties → Object Data → Shape Keys panel.
6. Scrub the shape-key Value slider manually: Basis → SK_Breather → SK_Collision
   → SK_TwoKink. Pause at each to let the viewer read the geometry.

### Phase 2 — Shape key walk-through (≈ 90 s)

For each shape key, switch to it and describe briefly what is visible on screen:

- **Basis (single kink, v = 0.65):** A ridge sweeping diagonally from bottom-left
  to top-right. The ridge angle encodes velocity. Cobalt on the left vacuum,
  amber on the right.
- **SK_Breather (ω = 0.50):** A waist-shaped dip in the floor's centre — the
  oscillating energy packet leaves a symmetric butterfly imprint in space-time.
- **SK_Collision (kink + antikink, elastic):** Two ridges meeting at the origin,
  then continuing outward — a perfect "X" shape showing the elastic pass-through.
  The outgoing ridges are offset from the incoming ones by the phase shift Δ.
- **SK_TwoKink (two kinks, v₁ = 0.80, v₂ = 0.30):** Two parallel ridges, one
  steeper than the other. Eventually the faster kink catches the slower one;
  after the interaction they swap positions but not speeds.

### Phase 3 — record.py render (background, no screen recording needed)

Run `record.py` with the blend file loaded to produce `viewport.mp4`.
This is a background render and does not need to be screen-captured.

---

## Tips

- Enable **Overlays → Statistics** to show vertex count (16 384 V, 16 129 Q) in
  the top-left of the viewport.
- Set the viewport shading to **Material Preview** so the emission colours show.
- Rotate to a three-quarter elevated angle (Numpad 5 → Perspective, then
  Numpad 4 twice + Numpad 8 twice) for a clear space-time view.
- A dark HDRI or plain black World colour makes the emission glow pop.
