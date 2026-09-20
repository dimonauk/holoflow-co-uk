import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-magnetic-skyrmion-skyrme-1962-bogomolny-dmi-dzyaloshinskii-moriya-topological-pontryagin-spin-texture-height-field-stage-floor-webxr";

const TITLE =
  "Python numpy — Magnetic Skyrmion: Skyrme (1962) / Bogomol’ny (1976) Néel-Type DMI, Dzyaloshinskii–Moriya Interaction, Topological Pontryagin Charge Q = −1, Spin-Texture Height-Field Stage Floor for WebXR (Blender 5.1)";

const LEDE =
  "A magnetic skyrmion is a whirlpool of magnetisation whose topology cannot be undone: the spin field wraps the unit sphere exactly once, giving a Pontryagin index Q = −1 that is preserved by any continuous deformation short of passing through a singularity. The stabilising mechanism is the Dzyaloshinskii–Moriya Interaction (DMI), an antisymmetric exchange that couples to the chirality of spin gradients and enforces a preferred handedness. This blueprint solves the 2-D classical Heisenberg model on a 128 × 128 lattice with Néel-type DMI via damped Landau–Lifshitz relaxation, computes Q with the Berg–Lüscher solid-angle formula, bakes the spin texture onto a height-field mesh with a colour-wheel attribute, and exports a Draco-compressed GLB with four shape keys spanning the full phase diagram: isolated skyrmion, skyrmion crystal, helical stripe phase, and polarised ferromagnet.";

function Body() {
  return (
    <>
      <p>
        Skyrmions belong to a family of topological solitons that runs through
        this library. The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-xy-model-2d-berezinskii-kosterlitz-thouless-1971-1973-vortex-antivortex-unbinding-topological-phase-transition-height-field-stage-floor-webxr"
        >
          XY-model BKT vortices
        </Link>{" "}
        are point-like topological excitations in a 2-D planar spin system —
        their winding number is also an integer invariant, but the energy is
        only logarithmically confined. Skyrmions are two-dimensional analogues
        of the 3-D topological solitons Skyrme (1962) introduced to describe
        nucleons: finite-energy field configurations that wrap the target
        manifold S² once. In condensed matter, the target sphere is the unit
        sphere of magnetisation directions. The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-haldane-1988-chern-insulator-berry-curvature-topological-phase-diagram-honeycomb-height-field-stage-floor-webxr"
        >
          Haldane Chern insulator
        </Link>{" "}
        shares the same Pontryagin-index language: its momentum-space Bloch
        vector also wraps S² once per band, with a Chern number that counts
        the wrapping. And the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-ising-model-2d-metropolis-monte-carlo-onsager-exact-tc-ferromagnetic-domains-height-field-stage-floor-webxr"
        >
          2-D Ising ferromagnet
        </Link>{" "}
        provides the simplest example of symmetry breaking in the spin
        Hamiltonian that skyrmions live in: the applied-field term −B Σ m
        <sub>iz</sub> here plays the same role as the external field that
        tilts the Ising free energy.
      </p>

      <h2>The Hamiltonian</h2>

      <p>
        The 2-D classical Heisenberg model on a square lattice with unit-vector
        spins <strong>m</strong>
        <sub>i</sub> ∈ S²:
      </p>

      <pre>{`H = −J Σ_{⟨ij⟩} mᵢ·mⱼ          (ferromagnetic exchange, J > 0)
    −D Σ_{⟨ij⟩} (mᵢ×mⱼ)·ê_{ij}  (Néel DMI — interfacial symmetry)
    −K Σᵢ (mᵢz)²                  (easy-axis anisotropy, z-direction)
    −B Σᵢ mᵢz                     (applied field, z-direction)`}</pre>

      <p>
        Parameters in this blueprint: J = 1.0, D = 0.35, K_BASE = 0.08.
        The field B varies per shape key. The exchange term favours
        parallel alignment of neighbouring spins. The DMI term, introduced
        by Dzyaloshinskii (1958) on symmetry grounds and derived
        microscopically by Moriya (1960), is antisymmetric under spin exchange
        (m<sub>i</sub> ↔ m<sub>j</sub>) and couples to the bond direction ê
        <sub>ij</sub>. For Néel-type (interfacial) DMI the vector{" "}
        <strong>D</strong>
        <sub>ij</sub> = D r̂<sub>ij</sub> points along the bond, which favours
        a spin rotation in the radial plane — the signature of the Néel
        skyrmion texture.
      </p>

      <h2>Effective field and Néel DMI</h2>

      <p>
        The effective field at site i is H<sub>eff,i</sub> = −∂H/∂m<sub>i</sub>.
        For the exchange term this gives the lattice Laplacian. For the Néel
        DMI, computing the gradient via centred differences:
      </p>

      <pre>{`dx = (roll(m, −1, ax=0) − roll(m, +1, ax=0)) * 0.5  # ∂m/∂x
dy = (roll(m, −1, ax=1) − roll(m, +1, ax=1)) * 0.5  # ∂m/∂y

H_DMI[..., 0] += D *  dy[..., 2]          # from ŷ × ∂m/∂y
H_DMI[..., 1] -= D *  dx[..., 2]          # from x̂ × ∂m/∂x
H_DMI[..., 2] += D * (dx[..., 1] − dy[..., 0])`}</pre>

      <p>
        The sign pattern arises from the cross products x̂ × v = (0, −v
        <sub>z</sub>, v<sub>y</sub>) and ŷ × v = (v<sub>z</sub>, 0, −v
        <sub>x</sub>). This effective field points tangentially around a
        skyrmion core, enforcing the right-handed spin rotation. The helical
        period set by the ratio D/J is λ = 2π / arctan(D/J) ≈ 18.6 lattice
        sites for D = 0.35, J = 1.0 — well resolved on the 128-site grid.
      </p>

      <h2>Topological charge</h2>

      <p>
        The continuum Pontryagin index
      </p>

      <pre>{`Q = (1/4π) ∫ m·(∂_x m × ∂_y m) d²x  ∈ ℤ`}</pre>

      <p>
        is computed on the lattice via the Berg–Lüscher (1981) solid-angle
        formula. Divide the square lattice into triangles (two per plaquette).
        For each triangle with spin corners A, B, C, the solid angle subtended
        on the unit sphere is:
      </p>

      <pre>{`Ω = 2 arctan( A·(B×C) / (1 + A·B + B·C + C·A) )`}</pre>

      <p>
        Summing Ω over all triangles and dividing by 4π gives Q ∈ ℤ exactly,
        even on a discrete lattice, provided no plaquette contains a
        singularity (antiparallel spins in adjacent sites). For a single
        relaxed Néel skyrmion, Q = −1. For the 3×3 skyrmion crystal, Q ≈ −9.
        For the ferromagnet and helical phase, Q = 0.
      </p>

      <h2>Relaxation: damped Landau–Lifshitz</h2>

      <p>
        The blueprint uses gradient descent on S² — the overdamped limit of
        the Landau–Lifshitz–Gilbert equation:
      </p>

      <pre>{`δmᵢ = α (H_eff,i − (mᵢ·H_eff,i) mᵢ)   # tangential step
mᵢ ← mᵢ + δmᵢ
mᵢ ← mᵢ / |mᵢ|                           # renormalise to S²`}</pre>

      <p>
        The subtraction of the radial component (m<sub>i</sub>·H
        <sub>eff,i</sub>) m<sub>i</sub> projects the gradient onto the tangent
        plane of S² at m<sub>i</sub>, so each step stays on the sphere to
        first order in α. The renormalisation corrects the second-order
        drift. Damping α = 0.10 gives rapid convergence without oscillation.
        5 000 steps suffice for the single-skyrmion and ferromagnet scenarios;
        the skyrmion crystal uses 8 000 steps owing to the larger energy
        barrier between topological sectors.
      </p>

      <h2>Colour-wheel visualisation</h2>

      <p>
        The iconic skyrmion colour wheel encodes two independent angular
        degrees of freedom simultaneously:
      </p>

      <pre>{`φ = atan2(my, mx)          # in-plane azimuth → hue (0 to 2π)
θ = arccos(mz)             # polar angle      → brightness
  mz = −1 (core)  → cobalt
  mz = +1 (far field) → amber

colour = lerp(cobalt, amber, (mz + 1) / 2)
       + sin(θ) * (hue_ring from φ) * tint_fraction`}</pre>

      <p>
        The core of a Néel skyrmion points antiparallel to the applied field
        (m<sub>z</sub> = −1, cobalt blue); the far field is polarised along B
        (m<sub>z</sub> = +1, amber). Around the core the spins rotate radially
        outward — this is the Néel texture, as opposed to the Bloch skyrmion
        where spins rotate azimuthally. The radial rotation produces a colour
        wheel pattern: spins pointing +x appear red, +y green, −x cyan, −y
        purple, completing one full colour revolution around the core.
      </p>

      <h2>Shape keys</h2>

      <pre>{`Key        B     K       Init             Q    Description
─────────────────────────────────────────────────────────────
Basis      0.42  0.08    single skyrmion  −1   isolated Néel skyrmion
SK_Lattice 0.18  0.04    3×3 skyrmions    ≈−9  skyrmion crystal
SK_Helical 0.00  0.00    helix            0    stripe / helical phase
SK_FM      0.80  0.08    ferromagnet      0    polarised ferromagnet`}</pre>

      <p>
        The Basis state corresponds to the isolated skyrmion stabilised by the
        competition between the applied field (which wants the whole lattice
        polarised) and the DMI (which wants helical winding). At lower field
        and weaker anisotropy (SK_Lattice) multiple skyrmions can coexist in a
        triangular crystal — this is the skyrmion lattice phase first observed
        in MnSi by Mühlbauer et al. (2009). At zero field and zero anisotropy
        (SK_Helical) the DMI alone is responsible, producing a helical stripe
        pattern with period λ ≈ 18.6 sites. At high field (SK_FM) the
        ferromagnet wins and all spins align with B.
      </p>

      <h2>Blueprint walk-through</h2>

      <p>
        <strong>Step 1 — Initial conditions.</strong> Each scenario begins
        from an analytic initial state to guide convergence into the intended
        topological sector. The single skyrmion uses the exact Néel profile:
        θ(r) = 2 arctan(R/r) with a skyrmion of radius R = N/12 ≈ 10 sites
        placed at the lattice centre. The 3×3 crystal places nine such
        skyrmions on a square sublattice. The helical state initialises spins
        as m<sub>x</sub> = cos(q·x), m<sub>z</sub> = sin(q·x) with q =
        arctan(D/J). The ferromagnet starts uniform at m<sub>z</sub> = +1.
      </p>

      <p>
        <strong>Step 2 — Relaxation.</strong>{" "}
        <code>_relax(m, J, D, K, B)</code> iterates the damped LLG step. The
        effective field is computed entirely in NumPy via <code>np.roll</code>{" "}
        along each axis — no Python loop over lattice sites. The computation
        is O(N²) in memory and O(N²) per step, with the roll operations
        touching each array element a constant number of times.
      </p>

      <p>
        <strong>Step 3 — Topological charge.</strong>{" "}
        <code>_topological_Q(m)</code> computes Q using the Berg–Lüscher
        formula on all 2(N−1)² triangles of the lattice. The arctan formula
        is numerically stable even when spins are nearly antiparallel (the
        denominator 1 + A·B + B·C + C·A approaches zero, but arctan diverges
        gracefully). Q is printed to the console; it should read −1 (Basis),
        ≈−9 (SK_Lattice), 0 (SK_Helical), 0 (SK_FM).
      </p>

      <p>
        <strong>Step 4 — Colour attribute.</strong>{" "}
        <code>_spin_colour(m)</code> produces a 128×128×4 RGBA array by
        interpolating cobalt and amber by m<sub>z</sub>, then adding a
        hue-wheel tint proportional to sin(θ). The colour attribute is stored
        as FLOAT_COLOR domain POINT, which carries through the GLB export as a
        vertex colour morph target.
      </p>

      <p>
        <strong>Step 5 — Mesh and export.</strong> The 128 × 128 quad grid is
        built with <code>mesh.vertices.foreach_set</code> and polygon index
        arrays assembled via NumPy index arithmetic — no{" "}
        <code>bpy.ops.mesh</code> operators. Shape keys are added with{" "}
        <code>obj.shape_key_add(from_mix=False)</code> and populated via{" "}
        <code>sk.data.foreach_set("co", ...)</code>. The GLB is exported with
        Draco level 6, WebP textures, morph targets, and vertex colours.
      </p>

      <h2>Troubleshooting</h2>

      <p>
        <strong>Q prints 0 instead of −1 for Basis.</strong> The skyrmion
        collapsed to the ferromagnet during relaxation. This happens if B is
        too large or the initial skyrmion radius is too small. Reduce B from
        0.42 to 0.35, or increase the initial radius R from N/12 to N/8.
      </p>

      <p>
        <strong>SK_Lattice shows fewer than nine skyrmion cores.</strong> Some
        skyrmions annihilated during relaxation — the initial lattice spacing
        was too small. Increase the skyrmion spacing from N/3 to N/2.8 sites,
        or raise K slightly to stabilise individual skyrmions against merging.
      </p>

      <p>
        <strong>SK_Helical looks like the ferromagnet.</strong> The helical
        period λ = 2π/arctan(D/J) must fit within the lattice. For D = 0.35,
        J = 1.0, λ ≈ 18.6 sites, giving about 6.9 periods on 128 sites —
        comfortably resolved. If you reduce D to 0.10, λ grows to ≈ 63 sites
        and only two periods fit, which may look stripe-like rather than
        helical. Increase D or use a smaller grid for low-D exploration.
      </p>

      <p>
        <strong>The colour wheel looks monochrome.</strong> The tint fraction
        in <code>_spin_colour</code> is a blend parameter. If it is too small,
        only the cobalt–amber gradient is visible. Increase it from 0.35 to
        0.60 to enhance the azimuthal colour variation around the core. Note
        that the colour attribute drives the shader via a vertex-colour node;
        check that <em>Colour → Attribute</em> is enabled in Solid viewport
        mode.
      </p>

      <h2>Outside sources</h2>

      <p>
        <strong>Skyrme THR (1962).</strong> &ldquo;A unified field theory of
        mesons and baryons.&rdquo; <em>Nuclear Physics</em> 31:556–569.
        doi:10.1016/0029-5582(62)90775-7. Public Domain (over 60 years). The
        paper that introduced topological solitons in field theory; the
        condensed-matter community borrowed both the name and the Pontryagin
        index. Related work: Bogomol&apos;ny EB (1976), &ldquo;Stability of
        classical solutions,&rdquo; <em>Sov J Nucl Phys</em> 24(4):449 — the
        self-duality bound that sets the minimum energy of a topological
        soliton at each topological charge.
      </p>

      <p>
        <strong>Berg B &amp; Lüscher M (1981).</strong> &ldquo;Definition and
        statistical distributions of a topological number in the lattice O(3)
        σ-model.&rdquo; <em>Nuclear Physics B</em> 190(2):412–424. The
        solid-angle formula for the lattice Pontryagin index used in{" "}
        <code>_topological_Q</code> — exact for smooth configurations and
        numerically stable even near singularities.
      </p>

      <p>
        <strong>
          Mühlbauer S, Binz B, Jonietz F, Pfleiderer C, Rosch A, Neubauer A,
          Georgii R, Böni P (2009).
        </strong>{" "}
        &ldquo;Skyrmion Lattice in a Chiral Magnet.&rdquo; <em>Science</em>{" "}
        323:915–919.{" "}
        <a
          className={lk}
          href="https://arxiv.org/abs/0902.1968"
          target="_blank"
          rel="noopener noreferrer"
        >
          arXiv:0902.1968
        </a>
        . The first direct observation of a skyrmion lattice in a bulk chiral
        magnet (MnSi), using small-angle neutron scattering. Related work:
        Romming N et al. (2013) <em>Science</em> 341:636 — real-space imaging
        of individual skyrmions in Fe/Ir films by spin-polarised STM; and the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-gross-pitaevskii-bec-rotating-vortex-lattice-abrikosov-imaginary-time-stage-floor-webxr"
        >
          Gross–Pitaevskii rotating vortex lattice
        </Link>
        , which forms a triangular Abrikosov lattice by the same competition
        between topological density and inter-soliton repulsion.
      </p>
    </>
  );
}

export const blenderTutorialPythonNumpyMagneticSkyrmionSkyrme1962BogomolnyDmiDzyaloshinskiiMoriyaTopologicalPontryaginSpinTextureHeightFieldStageFloorWebxrEntry: Entry =
  buildInstructable({
    slug: SLUG,
    title: TITLE,
    lede: LEDE,
    body: <Body />,
    topics: ["blender", "python", "scripting", "physics", "topology", "magnetism", "stat-mech", "webxr"],
    blenderVersion: "5.1",
    publishedAt: "2026-09-20",
    libraryPath:
      "blends/scripting/python-numpy-magnetic-skyrmion-skyrme-1962-bogomolny-dmi-dzyaloshinskii-moriya-topological-pontryagin-spin-texture-height-field-stage-floor-webxr",
  });
