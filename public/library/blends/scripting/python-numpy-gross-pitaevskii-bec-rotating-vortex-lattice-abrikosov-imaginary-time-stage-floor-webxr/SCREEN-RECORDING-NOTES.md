# Screen Recording Notes — GPE BEC Vortex Lattice

**Target file**: `public/library/videos/scripting/<slug>/screen.mp4`

## Prerequisites

1. Run `blueprint.py` in Blender 5.1 Scripting workspace.  
   Confirm `gpe_bec_vortex.blend` and `gpe_bec_vortex.glb` appear beside the script.
2. Switch to the **Layout** workspace. The height-field mesh should be visible.

## OBS / Game Bar settings

| Setting         | Value                                    |
|-----------------|------------------------------------------|
| Source          | Window Capture → Blender 5.1            |
| Resolution      | 1920 × 1080 (match Blender window)       |
| Frame rate      | 30 fps                                   |
| Audio           | Off                                      |
| Output format   | MP4 (H.264, CRF 18 or "High Quality")   |
| Output file     | `screen.mp4`                             |

## Blender viewport prep

1. Press `Numpad 5` → toggle **Orthographic**.
2. Press `Numpad 7` → top-down view; press again or `Numpad 1` → front-tilted (15° from top looks best).
3. Press `Z` → **Rendered** shading (or Material Preview `Alt+Z`).  
   Verify cobalt vortex cores and amber plateau are visible.
4. Open **Properties** → Object Data Properties → Shape Keys.  
   Set SK_Hex7 Value = 1.0 to preview the Abrikosov lattice.
5. Press `H` to hide the properties panel if it occludes the mesh.
6. Frame the mesh with `Numpad .` (focus on selection).

## Recording sequence (~60 s, keep only best 10–15 s)

| Timestamp | Action                                                        |
|-----------|---------------------------------------------------------------|
| 0–5 s     | Show Basis (SK_Hex7=0) — smooth Thomas-Fermi plateau          |
| 5–15 s    | Drag SK_Hex7 Value slider 0 → 1 slowly in Shape Keys panel   |
| 15–25 s   | Hold at SK_Hex7=1 — seven cobalt dimples visible, hexagonal   |
| 25–30 s   | Orbit camera 360° around the lattice (middle-mouse drag)      |
| 30–40 s   | Set SK_Hex7=0, SK_Hex19=1 — denser 19-vortex lattice          |
| 40–50 s   | Orbit + zoom in to show individual vortex cores               |
| 50–60 s   | Return to top-down view; fade all SK back to Basis            |

## Trim and export

Cut to ~12 s showing: Basis → SK_Hex7 morph → orbit → SK_Hex19.  
Export as `screen.mp4` with H.264, 1920×1080 @ 30 fps.  
Place next to `viewport.mp4` in the videos/scripting/… directory.

## Voiceover cues (optional)

- "The smooth hill is the Thomas-Fermi ground state with no rotation."
- "As we turn up the angular velocity, vortices nucleate from the surface and
  arrange into the triangular Abrikosov lattice."
- "Each cobalt well is a quantum of circulation — a topological defect where
  the superfluid density vanishes and the phase winds by exactly 2π."
- "At higher rotation, the lattice densifies. The vortex spacing scales as the
  inverse square root of the rotation rate."
