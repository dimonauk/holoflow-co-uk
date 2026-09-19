# Anderson Localisation — 2D Tight-Binding with Diagonal Disorder

**Blender 5.1 · Python · NumPy · CC0**

## Physics

Philip Anderson showed in 1958 that adding random impurities to an otherwise
perfect crystal can completely halt electron transport — even infinitesimally
small disorder is sufficient in 1D and 2D to pin every eigenstate. The
mechanism is wave interference: scattered amplitudes arriving via different
paths cancel destructively, forcing the wavefunction into an exponentially
decaying envelope rather than a propagating Bloch wave.

The Hamiltonian is:

```
H = −T Σ_{⟨ij⟩} c†_i c_j  +  Σ_i ε_i c†_i c_i
```

where:
- `T = 1.0`  — hopping amplitude (sets the energy scale; bandwidth B = 4T in 2D)
- `ε_i ∈ [−W/2, W/2]` — uniform on-site disorder
- `⟨ij⟩` — nearest-neighbour pairs on an N×N square lattice with periodic BCs

Exact diagonalisation via `numpy.linalg.eigh` yields all N² = 4 096 eigenstates.
The eigenstate nearest E = 0 (band centre) is visualised as a height field.

Localisation length in 2D (Thouless / scaling theory):

```
ξ/a ≈ exp(πT/W)     (mean-free-path argument for W ≪ B)
```

| Shape key  | W    | ξ/a (approx) | Character                         |
|------------|------|--------------|-----------------------------------|
| Basis      | 0.50 | ~500         | Quasi-extended (ξ ≫ N=64)        |
| SK_Medium  | 2.00 | ~5           | Partially localised               |
| SK_Strong  | 5.00 | ~1.9         | Clearly localised, visible peak   |
| SK_MaxIPR  | 8.00 | highest IPR  | Most localised state in spectrum  |

IPR (Inverse Participation Ratio) = Σ_i |ψ(i)|⁴:
- Extended Bloch wave: IPR ≈ 1/N² (weight spread over all sites)
- Localised: IPR → 1 (weight concentrated on a few sites)

## Running the blueprint

1. Open Blender 5.1. New **General** scene.
2. **Scripting** workspace → open `blueprint.py` (Text → Open).
3. Press **Alt+P** (Run Script). Console output:
   ```
   Anderson localisation: diagonalising W=0.50 …
   Anderson localisation: diagonalising W=2.00 …
   Anderson localisation: diagonalising W=5.00 …
   Anderson localisation: diagonalising W=8.00 for max-IPR …
   Saved  //.../anderson_localization_floor.blend
   Export //.../anderson_localization_floor.glb
   ```
4. Allow **2–5 minutes** (four 4096×4096 LAPACK symmetric eigenproblem
   decompositions; faster with MKL-linked NumPy).
5. In the **3D Viewport** (Material Preview shading): the cobalt–amber height
   field shows the quasi-extended W=0.50 eigenstate.
6. **Properties → Object Data → Shape Keys**: drag `SK_Strong` to 1.0 while
   `Basis` is at 0.0. The surface shrinks to a sharp amber spike — localisation.

## Outputs

| File | Description |
|---|---|
| `anderson_localization_floor.blend` | Blender scene with shape keys |
| `anderson_localization_floor.glb`   | Draco-6 compressed, WebXR-ready |
| `viewport.mp4` | Rendered disorder-progression animation (run `record.py`) |
| `screen.mp4`   | OBS screen recording (see `SCREEN-RECORDING-NOTES.md`) |

## Sources

1. Anderson PW (1958) "Absence of Diffusion in Certain Random Lattices"
   Physical Review 109(5):1492–1505. DOI 10.1103/PhysRev.109.1492. Public Domain.

2. Abrahams E, Anderson PW, Licciardello DC, Ramakrishnan TV (1979)
   "Scaling Theory of Localization: Absence of Quantum Diffusion in Two Dimensions"
   Physical Review Letters 42(10):673–676. DOI 10.1103/PhysRevLett.42.673. Public Domain.

3. NumPy (BSD-3-Clause). Harris et al. 2020 Nature 585:357–362. https://numpy.org
