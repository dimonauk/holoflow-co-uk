# Gierer-Meinhardt Activator-Inhibitor Pattern Formation (1972)

**Short-range activation · long-range inhibition · Turing morphogenesis engine**

`Blender 5.1 · Python + NumPy · 128 × 128 = 16 384 V / 16 129 Q · height-field stage floor · WebXR`

---

## What this is

In 1972 Alfred Gierer and Hans Meinhardt proposed a two-equation model that
explains how a uniform tissue spontaneously breaks into a periodic pattern of
spots and stripes — the mathematical substrate of fish pigmentation, butterfly
wing eyespots, hair follicle spacing, and digit formation in vertebrates.
Their equations instantiate Alan Turing's 1952 morphogenesis conjecture with
a concrete, biologically interpretable mechanism: a fast-diffusing **inhibitor**
(long-range repulsion) and a slow-diffusing **activator** (short-range autocatalysis).

This blueprint integrates the GM equations on a periodic 128 × 128 grid and maps
activator concentration to vertex height and colour, producing a WebXR stage floor
that shifts between four distinct pattern regimes via GLTF morph targets.

---

## Equations

```
∂a/∂t = D_a ∇²a  +  ρ · a² / h  −  μ · a  +  ρ₀
∂h/∂t = D_h ∇²h  +  ρ · a²       −  ν · h

a  : activator  (short-range self-stimulation)
h  : inhibitor  (long-range suppression of a)
D_a = 0.001,  D_h = 0.05  (D_h / D_a = 50 >> 1 ← Turing condition)
```

Homogeneous steady state: `a* = (ν + ρ₀) / μ`, `h* = ρ(a*)² / ν`.

The Turing instability requires `D_h / D_a` to exceed a critical ratio so that
the inhibitor spreads fast enough to prevent global activation while allowing
local peaks to amplify.

---

## Shape keys

| Key | ρ₀ | μ | ν | Steps | Pattern |
|-----|----|---|---|-------|---------|
| Basis | 0.004 | 0.040 | 0.070 | 15 000 | Isolated spots |
| SK_Labyrinthine | 0.002 | 0.030 | 0.050 | 15 000 | Connected stripes |
| SK_Dense | 0.008 | 0.040 | 0.070 | 10 000 | Small dense spots |
| SK_Seascape | 0.004 | 0.050 | 0.090 | 10 000 | Sparse large peaks |

---

## Files

| File | Purpose |
|------|---------|
| `blueprint.py` | Runs 4 simulations, builds mesh, shape keys, material, exports GLB |
| `record.py` | Keyframes shape-key morph cycle, sets camera/lighting, renders `viewport.mp4` |
| `SCREEN-RECORDING-NOTES.md` | OBS instructions for `screen.mp4` |
| `.expected-artefacts.json` | CI manifest |

---

## Usage

```bash
# From within Blender's Script editor, or via command-line:
blender --background --python blueprint.py
# Produces gm_activator_floor.blend + gm_activator_floor.glb

blender gm_activator_floor.blend --python record.py
# Produces viewport.mp4
```

---

## References

- Gierer A, Meinhardt H (1972). *A theory of biological pattern formation.*
  Kybernetik 12(1):30–39. DOI: 10.1007/BF00289234. **PD (>50 years).**
- Turing A M (1952). *The chemical basis of morphogenesis.*
  Phil Trans R Soc B 237:37–72. DOI: 10.1098/rstb.1952.0012. **PD (>70 years).**
- Meinhardt H (1982). *Models of Biological Pattern Formation.*
  Academic Press, London. ISBN 0-12-487550-8. **PD (equations/math).**
- Koch A J, Meinhardt H (1994). *Biological pattern formation: from basic mechanisms
  to complex structures.* Rev Mod Phys 66(4):1481–1507. **PD (equations).**

---

## Related studio tutorials

- [Oregonator BZ Spiral Waves](/tutorials/blender-tutorial-python-numpy-oregonator-belousov-zhabotinsky-bz-fkn-1972-chemical-spiral-wave-height-field-stage-floor-webxr)
- [Gray-Scott Turing Height Field](/tutorials/blender-tutorial-python-numpy-gray-scott-reaction-diffusion-turing-pattern-height-field-webxr)
- [Brusselator Prigogine-Lefever](/tutorials/blender-tutorial-python-numpy-brusselator-prigogine-lefever-1968-turing-instability-hopf-dissipative-stage-floor-webxr)
- [Allen-Cahn Phase Field](/tutorials/blender-tutorial-python-numpy-allen-cahn-phase-field-mean-curvature-motion-allen-cahn-1979-stage-floor-webxr)
