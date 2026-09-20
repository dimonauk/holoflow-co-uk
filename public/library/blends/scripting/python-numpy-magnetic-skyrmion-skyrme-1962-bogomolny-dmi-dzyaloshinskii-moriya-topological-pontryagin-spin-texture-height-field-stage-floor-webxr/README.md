# Magnetic Skyrmion — Néel Type, Dzyaloshinskii–Moriya Interaction

**Blender 5.1 | Python + NumPy | Stage-floor height-field | WebXR GLB**

A magnetic skyrmion is a topological spin texture: a whirlpool of magnetisation
whose winding cannot be undone by any continuous deformation.  It is stabilised
by the antisymmetric Dzyaloshinskii–Moriya Interaction (DMI), which couples
to the chirality of spin gradients and selects a preferred handedness.

## Hamiltonian

```
H = −J Σ_{⟨ij⟩} m_i·m_j        (exchange, ferromagnetic J > 0)
    −D Σ_{⟨ij⟩} (m_i×m_j)·ê_ij  (Néel DMI — interfacial)
    −K Σ_i (m_iz)²               (easy-axis anisotropy)
    −B Σ_i m_iz                   (applied field, z-direction)
```

Parameters: J=1.0, D=0.35, K_BASE=0.08, B varies by scenario.

## Topological charge (Pontryagin index)

```
Q = (1/4π) ∫ m·(∂_x m × ∂_y m) d²x  ∈ ℤ
```

Computed on the lattice via the Berg–Lüscher solid-angle formula.
Q = −1 for a single skyrmion, Q = 0 for the ferromagnet and helical phase.

## Relaxation

Damped Landau-Lifshitz (LLG) with damping α = 0.10:
```
δm_i = α (H_eff,i − (m_i·H_eff,i) m_i),  then |m_i| ← 1
```

## Shape keys

| Key        | B     | K       | Init           | Q    | Description              |
|------------|-------|---------|----------------|------|--------------------------|
| Basis      | 0.42  | 0.08    | single skyrmion| −1   | isolated Néel skyrmion   |
| SK_Lattice | 0.18  | 0.04    | 3×3 skyrmions  | ≈ −9 | skyrmion crystal lattice |
| SK_Helical | 0.00  | 0.00    | helix          | 0    | stripe / helical phase   |
| SK_FM      | 0.80  | 0.08    | ferromagnet    | 0    | polarised ferromagnet    |

## Output files

- `skyrmion_floor.blend` — Blender scene with shape keys and material
- `skyrmion_floor.glb` — Draco-6 compressed, WebP textures, +Y up, morph targets

## Running

```bash
blender --background --python blueprint.py
blender --background skyrmion_floor.blend --python record.py
```

## Sources

- Skyrme THR (1962). "A unified field theory of mesons and baryons." *Nucl Phys* 31:556. Public Domain.
- Bogomol'ny EB (1976). "Stability of classical solutions." *Sov J Nucl Phys* 24(4):449. Public Domain.
- Berg B & Lüscher M (1981). "Definition and statistical distributions of a topological number in the lattice O(3) σ-model." *Nucl Phys B* 190(2):412–424.
- Mühlbauer S et al. (2009). "Skyrmion Lattice in a Chiral Magnet." *Science* 323:915. arXiv:0902.1968.
