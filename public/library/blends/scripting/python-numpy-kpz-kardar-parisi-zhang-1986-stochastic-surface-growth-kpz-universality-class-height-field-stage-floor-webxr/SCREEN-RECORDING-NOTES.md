# Screen Recording Notes — KPZ Growth Floor

**Target file:** `public/library/videos/scripting/python-numpy-kpz-kardar-parisi-zhang-1986-stochastic-surface-growth-kpz-universality-class-height-field-stage-floor-webxr/screen.mp4`

## OBS Settings

| Setting | Value |
|---|---|
| Source | Window Capture → Blender 5.1 |
| Resolution | 1920 × 1080 |
| Frame rate | 30 fps |
| Audio | OFF (no mic) |
| Output format | MP4 (H.264) |
| Bitrate | 8 000 kbps |

---

## What to record (≈ 6–8 min total)

### 1. Open the script (45 s)
Open **blueprint.py** in Blender's Text Editor.  
Scroll through the header docstring, pointing out:
- The KPZ equation: `∂h/∂t = ν∇²h + (λ/2)|∇h|² + η(x,t)`.
- The three terms: surface tension (smooths), tilt (KPZ nonlinearity), noise (roughens).
- The Hopf–Cole transformation that maps KPZ to a multiplicative noise heat equation in 1D.

### 2. Named constants (45 s)
Highlight the constants block:
- `LAM_BASIS = 1.0` vs `LAM_STRONG = 2.0` — explain that λ controls how much slope accelerates growth.
- `NOISE_D = 0.30` — the noise temperature.
- `STEPS_LONG = 240` at `DT = 0.05` → t = 12 time units.
- Mention `SEED = 137` means all four shape-key runs start from the **same** random seed, so differences are physics not luck.

### 3. Run the script (1–2 min)
Press **Alt+R** or click **Run Script**.  
Watch the Python console output: it prints the KPZ vs EW normalised width values.  
Notice: KPZ width > EW width (same t, same noise). This is the signature of the nonlinear term widening the interface.

### 4. Basis shape key in viewport (30 s)
The mesh appears: a rough, randomly textured floor, cobalt valleys and amber ridges.  
Switch to **Solid → Colour → Attribute → KPZ_Height** to see the height field as colour.

### 5. Shape key comparisons (2 min)
Go to Properties → Object Data → Shape Keys. Scrub each key from 0 → 1:
- **Basis** (λ=1.0, t=3): fine-grained texture, symmetric hills and valleys.
- **SK_Long** (λ=1.0, t=12): same λ, longer time — surface is coarser, grooves deeper.
  - Notice the **asymmetry**: peaks are narrower/sharper than valleys. This is the KPZ skew
    (Tracy–Widom GUE distribution in 1D; in 2D still non-Gaussian).
- **SK_EW** (λ=0, t=12): same t as SK_Long but **no KPZ nonlinearity**.
  - Smoother, more isotropic, peaks and valleys are roughly symmetric.
  - The EW limit is a purely diffusive interface — Gaussian fluctuations.
- **SK_Strong** (λ=2.0, t=12): strong KPZ coupling — pronounced directional ridges,
  much steeper grooves than SK_Long.

**Key visual lesson:** comparing SK_Long vs SK_EW is a direct visualisation of what the
(λ/2)|∇h|² nonlinear term adds to surface growth.

### 6. Vertex colour overlay (30 s)
Keep SK_Long active (value = 1). Switch shading to **Solid → Colour → Attribute**.  
The cobalt–amber topology shows the long-time KPZ surface.  
Compare with SK_EW active: the EW surface looks more homogeneous, fewer extreme peaks.

### 7. Export GLB (30 s)
The `.glb` exports automatically when `blueprint.py` runs. Show the file path in the info bar.  
Open the GLB in the Holoflow WebXR viewer to confirm it renders as a stage floor.

### 8. Quick Eevee render (30 s)
Press **F12**. The lit mesh shows the 3D relief of the KPZ surface.  
Optionally press numpad 1/7 to compare top and side views, showing the asymmetric height distribution.

---

## Recommended narration beats

- "The linear ν∇²h term is like surface tension — it flattens bumps. On its own it gives the Edwards–Wilkinson interface."
- "The (λ/2)|∇h|² term measures how steeply the surface slopes. Where there is slope, there is faster growth. That is the KPZ nonlinearity."
- "Compare SK_Long vs SK_EW: same noise, same time, different λ. The KPZ surface is rougher and asymmetric — peaks are spikier than valleys."
- "In 1D, KPZ is exactly solvable via the Hopf–Cole transformation. The height fluctuations follow the Tracy–Widom GUE distribution, famously also appearing in random matrix theory."
- "In 2D there are only numerical and RG estimates: roughness exponent α ≈ 0.38, growth exponent β ≈ 0.24."
