# Screen Recording Notes — Hofstadter Butterfly Floor

**Target file:** `screen.mp4`
**Destination:** `public/library/videos/scripting/python-numpy-hofstadter-butterfly-1976-fractal-energy-spectrum-bloch-electrons-magnetic-flux-harper-equation-height-field-stage-floor-webxr/screen.mp4`

---

## OBS / Game Bar setup

| Setting | Value |
|---|---|
| Source | Window Capture → Blender 5.1 |
| Resolution | 1920 × 1080 |
| Frame rate | 30 fps |
| Audio | Disabled |
| Format | MP4 / H.264 |
| Output path | see Destination above |

---

## Recording steps

1. **Open Blender 5.1.** Close the splash screen.
2. Open the Scripting workspace (`+ → Scripting`).
3. Open `blueprint.py` and press **Run Script**.
   Watch the terminal for `[DONE] Object 'hofstadter_floor' created`.
   *Note: blueprint.py runs ~35k matrix diagonalisations; expect 30–90 seconds.*
4. Switch to the **3D Viewport**. Press `Numpad 5` (orthographic), `Numpad 7` (top), then tumble to a 3/4 perspective with Middle Mouse Drag.
5. You should see the cobalt–amber butterfly height field — zero-DOS gaps appear as flat cobalt trenches; high-DOS bands rise as amber peaks.
6. **Start OBS recording.**
7. In the Properties panel → Object Data → Shape Keys, scrub through the four shape keys:
   - **Basis** — full Hofstadter butterfly α ∈ [0,1]: the complete self-similar fractal
   - **SK_Half** — left half α ∈ [0, 0.5] zoomed: the butterfly has reflection symmetry α → 1−α, so this half reveals every sub-butterfly
   - **SK_Zoom** — α ∈ [0.25, 0.50] zoomed into the 1/3-sub-butterfly: the fractal self-similarity at higher resolution
   - **SK_NNN** — next-nearest-neighbour hopping t₂ = 0.3: particle-hole symmetry E → −E broken; the butterfly warps asymmetrically
8. Hold each shape key at 1.0 for ~5 seconds, then crossfade to the next.
9. **Stop OBS recording.** Trim to ~60 seconds.

---

## What the viewer should see

- **Basis**: The iconic Hofstadter butterfly — branching vertical "ribs" of high DOS (amber) separated by cobalt fractal gaps. At α = 1/2 the gap at E = 0 is widest; at α = 1/3 and 2/3 narrower gaps open, each containing a perfect sub-butterfly.
- **SK_Half**: The left half magnified — now you can see the sub-butterfly at α ≈ 1/4 clearly, and the fine structure near α = 0 (where bands collapse to the bare cosine band ε(k) = 2cos k).
- **SK_Zoom**: The region [0.25, 0.50] × [−4, 4]. The 1/3-butterfly visible in Basis now fills the full grid; the sub-butterflies *within* it become visible. This demonstrates exact self-similarity: the butterfly repeats at every scale.
- **SK_NNN**: The entire landscape shifts upward (NNN adds 2t₂cos(2k_y) to the diagonal, breaking E → −E). The butterfly becomes asymmetric: lower band less dispersive, upper band pushed wider.

---

## Tips

- Solid shading with **Colour** overlay (Object Properties → Viewport Display) makes the cobalt–amber gradient most vivid.
- If the floor looks uniformly dark, check **Emission Strength ≥ 1.6** in HofstadterMat.
- The **SK_Zoom** key is the visually richest for demonstrating self-similarity — spend extra time here.
- Rotate the viewport 90° around Z to orient the butterfly so α runs left–right and energy runs into the screen.
