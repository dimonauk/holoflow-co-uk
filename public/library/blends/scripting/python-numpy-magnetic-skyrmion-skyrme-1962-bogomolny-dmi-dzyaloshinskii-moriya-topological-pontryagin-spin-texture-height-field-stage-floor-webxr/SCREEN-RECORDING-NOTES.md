# Screen Recording Notes — Magnetic Skyrmion

**Tool**: OBS Studio (or Windows Game Bar)
**Source**: Window Capture → Blender 5.1
**Resolution**: 1920 × 1080 @ 30 fps
**Output**: `public/library/videos/scripting/<slug>/screen.mp4`
**Audio**: Off

## Workflow to record

1. Run `blueprint.py` in Blender's Text Editor (or `blender --background --python blueprint.py`) to generate `skyrmion_floor.blend` and `skyrmion_floor.glb`.
2. Open `skyrmion_floor.blend` in Blender.
3. Switch to **Solid** viewport shading so the colour attribute is visible.
   - Enable **Colour → Attribute** in Solid mode overlay.
4. In the **Properties → Object Data → Shape Keys** panel, drag the **SK_Lattice** value from 0 → 1 to show the skyrmion crystal.
5. Start OBS recording.
6. Slowly sweep through shape keys in this order:
   - **Basis** (single skyrmion) → **SK_Lattice** (crystal) → **SK_Helical** (stripes) → **SK_FM** (flat) → back to **Basis**
   - Spend 8–10 seconds on each shape key so the viewer can appreciate the structure.
7. Stop OBS. Trim to ≤ 60 seconds. Export as H.264 MP4.
8. Save to `public/library/videos/scripting/<slug>/screen.mp4`.

## What to show on camera

- The **colour wheel** pattern on the single skyrmion (cobalt core, amber background, rainbow ring)
- The **triangular lattice** in SK_Lattice — nine cobalt cores arranged in a 3×3 grid
- The **stripe pattern** in SK_Helical — alternating cobalt/amber bands (~7 periods)
- The **flat amber surface** in SK_FM — topologically trivial ferromagnet

## Talking points

- The core of a Néel skyrmion points antiparallel to the applied field (mz = −1, cobalt)
- The azimuthal colour variation around the core reflects the radial spin orientation — the signature of the Dzyaloshinskii–Moriya interaction
- The topological charge Q = −1 for a single skyrmion means the spin texture wraps the unit sphere exactly once — it cannot be continuously deformed to the ferromagnet without passing through a singularity
