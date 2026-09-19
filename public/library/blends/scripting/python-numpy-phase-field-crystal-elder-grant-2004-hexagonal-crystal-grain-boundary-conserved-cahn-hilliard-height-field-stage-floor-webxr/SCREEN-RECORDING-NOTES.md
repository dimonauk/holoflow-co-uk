# Screen Recording Notes — Phase-Field Crystal (PFC) Model

Target file: `public/library/videos/scripting/<slug>/screen.mp4`

## Software

| Platform | Recommended |
|---|---|
| Windows 11 | Xbox Game Bar (Win + G) or OBS Studio |
| macOS | OBS Studio or built-in Screenshot.app |
| Linux | OBS Studio |

## OBS Settings

| Setting | Value |
|---|---|
| Source | Window Capture → Blender 5.1 |
| Base resolution | 1920 × 1080 |
| Output resolution | 1920 × 1080 |
| FPS | 30 |
| Audio | Disabled |
| Output format | MP4 |
| Video encoder | x264 CRF 18 or NVENC Quality |

## What to record (approx. 5 minutes)

1. **Open Blender 5.1.** New General file.

2. **Switch a pane to Scripting workspace.** Open `blueprint.py`.

3. **Walk the docstring** — explain the three key ideas:
   - The `(1+∇²)²` operator in the free energy F selects a single
     preferred wavenumber k₀=1, creating a periodic crystal.
   - The ∇² in the dynamics makes it a conserved (Model B) equation,
     so total density ψ̄ is preserved throughout time — contrast this
     with the Allen–Cahn equation which is non-conserved.
   - The ETD1 Fourier integrator handles the linear part exactly with
     no CFL restriction on the time step.

4. **Show the PARAMETERS block** — highlight R_BASIS, PSI_BASIS, DT,
   and T_BASIS. Explain the phase diagram briefly: r controls whether
   the system wants to be ordered (r < 0) or disordered (r > 0);
   PSI_MEAN is the conserved total density.

5. **Run the script** (Alt+P). The console shows four progress lines —
   one for each shape key simulation. Total runtime: 2–6 min depending
   on machine.

6. **After completion** — switch to 3-D Viewport. Orbit the mesh.
   - The surface is a sea of hexagonal bumps: the triangular crystal
     lattice viewed as a density field. Point out that the spacing is
     about 7.3 "pixels" — the natural lattice parameter a₀ = 4π/√3.
   - Colour: cobalt troughs (ψ low between atoms) → amber peaks (ψ
     high at atom cores).

7. **Shape keys tour** — Properties → Mesh Data → Shape Keys:
   - Drag **SK_GrainBnd** to 1.0. The crystal now has a roughly
     vertical band where two grain orientations meet — a grain boundary.
     This arises naturally from two sub-domains nucleating independently.
   - Drag to 0 → **SK_Stripe** to 1.0. The hexagonal lattice gives way
     to parallel stripes — the lamellar phase that appears at lower
     mean density. One fewer degree of freedom: only one wavevector
     rather than three.
   - Drag to 0 → **SK_Coexist** to 1.0. Partial crystallisation: some
     regions have formed a crystal (regular bumps) while others remain
     disordered. This is what you see during early-stage nucleation.

8. **GLB export** — show File → Export → glTF 2.0, point out Draco-6
   and the morph-targets checkbox. blueprint.py already exported it.

## File naming

Rename OBS output to `screen.mp4` and place alongside `viewport.mp4`
in `public/library/videos/scripting/<slug>/`.
