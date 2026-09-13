# Screen Recording Notes — FitzHugh-Nagumo Excitable Media

**Target file:** `screen.mp4`  
**Duration:** ≈ 90 s  |  **Resolution:** 1280 × 720  |  **FPS:** 30

---

## Steps (OBS Studio / Windows Game Bar)

1. **Open Blender 5.1.** Set the workspace to **Scripting** layout.

2. **Load `blueprint.py`** into the Text Editor.  
   Walk through the docstring and key sections in the recording:  
   - the `VARIANTS` dict (four excitable-media regimes)  
   - `_k2()` — how rfft2 wavenumber grid is constructed  
   - `_etd1_u()` / `_etd1_v()` — ETD1 exponential factors  
   - `_ic_s1s2()` — the S1+S2 cross-field protocol that seeds a free spiral tip  
   - `main()` — the shape-key loop  

3. **Run the script** (Alt+P or the ▶ button). The integration takes ≈ 30 s
   on a modern laptop (ETD1 is unconditionally stable at dt = 0.10; equivalent
   Euler would need dt < 0.0005, i.e. 200 × more steps).

4. Switch to **3D Viewport** in **Material Preview** mode (Viewport Shading → Material Preview).
   The `FHN_U_Volt` FLOAT_COLOR attribute drives the cobalt → amber gradient
   automatically via the `ShaderNodeAttribute` node.

5. **Cycle the shape keys** in the Properties panel → Object Data → Shape Keys:
   - Basis: trigger wave sweeping left-to-right
   - SK_Spiral: two-armed rotating spiral (S1+S2 protocol)
   - SK_Target: concentric target rings from a central pacemaker
   - SK_Reentry: single reentrant spiral from a line defect

6. In **Edit Mode** (Tab), scrub the viewport to show the height field relief.
   Point out that vertex Z = normalised u × 0.50 m — the wave front is a
   physical ridge on the floor mesh.

7. Back in the **Scripting** workspace, briefly show `record.py` and explain
   that it re-runs the S1+S2 spiral protocol, captures 8 snapshots, builds
   animated shape keys, and renders 360 frames to `viewport.mp4`.

8. **OBS settings:**
   - Source: Window Capture → Blender
   - Resolution: 1280 × 720, down-scaled from native if needed
   - Bitrate: 4000 kbps, CRF 23, H.264
   - Microphone: optional voice-over; narrate the ETD1 stability advantage

9. Export the recording as `screen.mp4` and save to:  
   `public/library/videos/scripting/python-numpy-fitzhugh-nagumo-1961-excitable-media-trigger-wave-spiral-height-field-stage-floor-webxr/`

---

## Key talking points

| Point | Script line | What to say |
|---|---|---|
| ETD1 vs Euler | `_etd1_u()` | Euler limit dt < 0.0005 here; ETD1 is unconditionally stable for diffusion |
| φ₁ formula | `np.expm1(Lu) / Lu` | Taylor-safe: `expm1` avoids cancellation when |z| ≪ 1 |
| S1+S2 protocol | `_ic_s1s2()` | Mimics cardiac defibrillation studies — second shock breaks the wavefront |
| Shape keys as morph targets | `_add_shape_key` | GLTF morph targets — sliders usable directly in Three.js / Babylon.js |
| Cobalt → amber colour | `_write_colour` | Resting state u ≈ −1.2 = cobalt; excited u ≈ +2 = amber |
