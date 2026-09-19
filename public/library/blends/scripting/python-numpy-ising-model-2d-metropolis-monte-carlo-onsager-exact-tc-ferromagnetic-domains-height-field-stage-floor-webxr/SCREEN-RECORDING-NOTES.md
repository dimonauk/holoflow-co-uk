# Screen Recording Notes — Ising Model Monte Carlo Floor

## Software
OBS Studio (any recent version) or Windows Game Bar (Win+G).

## Settings
| Setting | Value |
|---|---|
| Source | Window Capture → Blender |
| Resolution | 1920 × 1080 |
| Frame rate | 30 fps |
| Audio | Off (capture silent) |
| Output format | MP4 / H.264 |
| Output file | `public/library/videos/scripting/python-numpy-ising-model-2d-metropolis-monte-carlo-onsager-exact-tc-ferromagnetic-domains-height-field-stage-floor-webxr/screen.mp4` |

## What to capture

1. **Open Blender 5.1** and run `blueprint.py` from the Scripting workspace.
   - Show the terminal output confirming `⟨m⟩ cold ≈ +0.97` (strong ferromagnet)
   - and `⟨m⟩ crit ≈ ±0.05` (near-zero at Tc).

2. **Show the 3D Viewport** in Solid mode with Vertex Colour.
   - Pan around the cold Basis mesh — large cobalt/amber domains, flat-topped
     up-spin islands.

3. **Shape Key panel** — scrub through SK_Critical, SK_Hot, SK_Quench.
   - SK_Critical: fractal percolation clusters, no clean domain boundaries.
   - SK_Hot: salt-and-pepper noise, height nearly uniform.
   - SK_Quench: large domains separated by visible height steps — the quench
     from T→∞ froze a coarsening pattern before it could fully order.

4. **Run record.py** — show the render starting (output window or progress bar).

5. **Crop** to 15–20 seconds for the final tutorial clip.

## Checklist
- [ ] Blender window fills the capture frame (no desktop chrome visible)
- [ ] Viewport shows Vertex Colour mode (press `Z` → Solid → Colour = Vertex)
- [ ] All four shape keys visible in Properties → Object Data → Shape Keys panel
- [ ] Console shows Tc line: `Tc = 2.2692`
