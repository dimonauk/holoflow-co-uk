# Gray–Scott Reaction-Diffusion — Pearson 1993 Pattern Atlas

**Topic:** Activator-depletion Turing instability · Blender 5.1 scripting + NumPy  
**Licence:** Mathematical content CC0 / NumPy BSD-3-Clause / pmneila/jsexp MIT  
**Grid:** 128 × 128 = 16 384 vertices · 16 129 quads  
**Shape keys:** Basis (spots) · SK_Worm · SK_Hole · SK_Mitosis

---

## What this produces

A height-field stage floor mesh whose cobalt–amber gradient encodes the
activator concentration v(x, y) from the Gray–Scott reaction-diffusion system.
Four shape keys sweep through Pearson's (F, k) phase diagram:

| Key | F | k | Pearson region | Pattern |
|-----|------|-------|--------------|---------|
| Basis | 0.037 | 0.060 | ε | Symmetric isolated spots |
| SK_Worm | 0.060 | 0.062 | η | Labyrinthine worms / mazes |
| SK_Hole | 0.039 | 0.058 | ζ | Active holes in substrate background |
| SK_Mitosis | 0.028 | 0.054 | δ | Self-replicating spot division |

---

## How to run

1. Open Blender 5.1 · switch to Scripting workspace
2. Open `blueprint.py` in the Text Editor
3. Click **Run Script**  (≈ 2–4 min per shape key on a modern CPU)
4. Saved files: `gray_scott_floor.blend` · `gray_scott_floor.glb`

To render the viewport animation:
```bash
blender gray_scott_floor.blend --python record.py
```

---

## Parameters explained

| Constant | Value | Why |
|----------|-------|-----|
| `DU` | 0.16 | Substrate diffusivity — **must** exceed `DV` for Turing instability |
| `DV` | 0.08 | Activator diffusivity — Du/Dv = 2 (much smaller than Schnakenberg's 50) |
| `DT` | 1.0 | CFL = Du·dt/dx² = 0.16 < 0.25 (explicit Euler stable) |
| `HEIGHT_SCALE` | 0.80 | Maps v ∈ [0, 0.5] → z ∈ [0, 0.4 m] |

### Why Du/Dv = 2 (not 50 like Schnakenberg)?

Gray–Scott uses an *activator-depletion* topology: the reaction removes
substrate u rather than a separate inhibitor. Turing's mathematical condition
requires Du > Dv, but the required ratio is much smaller than in
activator-inhibitor schemes. The rich Pearson diagram arises because the feed
rate F and kill rate k can independently tune the nontrivial fixed point and
the growth/decay balance, giving twelve qualitatively distinct attractors.

### Failure modes

- **Blank mesh (v = 0 everywhere)**: F+k ≥ 1 — the trivial steady state is
  globally stable. Reduce F or k to re-enter the Turing region.
- **Numerical explosion**: increase DT above ~2.0 and the 5-point Laplacian
  becomes unstable. Keep DT ≤ 1.5.
- **Patterns don't develop**: n_steps too small for the chosen (F, k). Low-F
  mitosis can need 12 000+ steps; worms converge faster (~5 000).
- **Self-replicating spots don't split**: noise amplitude too high — the initial
  seed must dominate. Set NOISE_AMP = 0.01 and HW to 4.

---

## Cross-references

### Studio tutorials
- [Schnakenberg 1979 — Activator-Substrate Turing Instability](/tutorials/blender-tutorial-python-numpy-schnakenberg-1979-activator-substrate-turing-instability-spots-stripes-height-field-stage-floor-webxr)
- [Gierer-Meinhardt 1972 — Activator-Inhibitor Morphogenesis](/tutorials/blender-tutorial-python-numpy-gierer-meinhardt-activator-inhibitor-turing-morphogenesis-1972-spot-stripe-height-field-stage-floor-webxr)
- [FitzHugh-Nagumo 1961 — Excitable Media, Trigger Waves](/tutorials/blender-tutorial-python-numpy-fitzhugh-nagumo-1961-excitable-media-trigger-wave-spiral-height-field-stage-floor-webxr)

### Outside sources
1. **Pearson JE** (1993). "Complex Patterns in a Simple System."
   *Science* 261(5118):189–192.  doi:[10.1126/science.261.5118.189](https://doi.org/10.1126/science.261.5118.189)
   — the authoritative parameter atlas (equations public domain).
2. **Gray P & Scott SK** (1984). "Autocatalytic Reactions in the Isothermal,
   Continuous Stirred Tank Reactor." *Chem Eng Sci* 39(6):1087–1097.
   doi:[10.1016/0009-2509(84)87017-7](https://doi.org/10.1016/0009-2509(84)87017-7)
   — original reaction scheme (equations public domain).
3. **pmneila/jsexp** (MIT) — interactive JavaScript Gray-Scott explorer by
   Pablo Muñoz Fernández: <https://github.com/pmneila/jsexp>
