import Link from "next/link";

import { buildInstructable } from "lib/tutorials/build";
import type { Entry } from "lib/writing";

const lk = "underline underline-offset-4 hover:text-pink-200";

const SLUG =
  "blender-tutorial-python-numpy-wigner-quasi-probability-distribution-1932-quantum-phase-space-fock-state-cat-state-squeezed-vacuum-stage-floor-webxr";

const TITLE =
  "Python numpy — Wigner Quasi-Probability Distribution Wigner 1932 Phys Rev 40:749 W(q,p)=(1/π)∫ψ*(q+y)ψ(q-y)exp(2ipy)dy Hudson 1974 W≥0⟺Gaussian Fock |n⟩ W_n=((-1)ⁿ/π)exp(-2r²)L_n(4r²) Schrödinger Cat α=2 Squeezed Vacuum σ_q=e^{-r}/√2 L_n Laguerre Polynomial 128×128=16384V 16129Q Basis(|0⟩ Gaussian)/SK_Fock1(|1⟩ negative centre)/SK_Fock5(|5⟩ five rings)/SK_Cat(|+α⟩+|-α⟩ interference fringes)/SK_Squeezed(r=1.2 ellipse) WQP_Phase FLOAT_COLOR Cobalt–Amber Phase-Space Negativity Stage Floor WebXR (Blender 5.1)";

const LEDE =
  "Eugene Wigner introduced his quasi-probability distribution in 1932 as a translation of quantum mechanics into the language of phase space — the (q,p) plane of classical mechanics. The Wigner function W(q,p) recovers the correct quantum marginals for both position and momentum, yet it can take negative values: wherever W < 0, the state has no classical probability interpretation, and that negativity is the unambiguous signature of quantum coherence. R.L. Hudson proved in 1974 that W ≥ 0 everywhere if and only if the wave function is Gaussian; every other pure state carries at least one negative region. This blueprint builds a 128 × 128 quad-mesh stage floor in Blender 5.1 whose height encodes W(q,p) for five quantum states — Fock ground state, first and fifth excited states, a Schrödinger cat superposition, and a squeezed vacuum — baked into shape keys and exported as a Draco-compressed GLB for WebXR.";

function Body() {
  return (
    <>
      <p>
        The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-bloch-sphere-qubit-rabi-precession-berry-phase-su2-pauli-poi-webxr"
        >
          Bloch sphere
        </Link>{" "}
        captures the state of a single qubit as a point on a unit sphere: pure
        states live on the surface, mixed states in the interior. The Wigner
        function is the complementary tool for{" "}
        <em>continuous-variable</em> quantum systems — harmonic oscillators,
        optical modes, motional states of trapped ions. Instead of a sphere, it
        maps every quantum state to a real function over the classical phase
        plane (q,p), where q and p represent position and momentum quadratures.
      </p>

      <h2>The quasi-probability W(q,p)</h2>

      <p>
        The defining formula (Wigner 1932, Eq. 5) in natural units ħ = 1:
      </p>

      <pre>{`W(q,p) = (1/π) ∫ ψ*(q+y) ψ(q-y) exp(2ipy) dy`}</pre>

      <p>
        This is the Fourier transform of the off-diagonal position-space
        density matrix ρ(q+y, q−y) with respect to y. It is real-valued for
        any physical state (pure or mixed), and it integrates to unity over
        all of phase space. The two marginals are exact:
      </p>

      <pre>{`∫ W(q,p) dp  = |ψ(q)|²     (position probability density)
∫ W(q,p) dq  = |φ(p)|²     (momentum probability density)`}</pre>

      <p>
        Unlike classical probability distributions, W is not constrained to
        be non-negative. Regions where W &lt; 0 encode quantum interference
        and have no classical analogue. They cannot be detected by measuring
        either q or p alone — the marginals are always positive — but they are
        accessible through joint quantum tomography.
      </p>

      <h2>Hudson's theorem: when does W stay positive?</h2>

      <p>
        In 1974 Robert Hudson proved a sharp characterisation:
      </p>

      <blockquote>
        <em>
          W(q,p) ≥ 0 for all (q,p) if and only if ψ is a Gaussian wave function.
        </em>
      </blockquote>

      <p>
        Gaussian states — coherent states, squeezed states, thermal states —
        are the only pure or mixed states with a genuine classical phase-space
        probability. Every Fock state |n ≥ 1⟩ violates Hudson's condition; so
        does every superposition of non-overlapping coherent states. The floor
        below makes the violation visible: amber colouring marks W &lt; 0 regions,
        cobalt marks W &gt; 0.
      </p>

      <h2>Fock states of the harmonic oscillator</h2>

      <p>
        For the quantum harmonic oscillator with Hamiltonian H = ½(p² + q²),
        the energy eigenstates |n⟩ have a closed-form Wigner function:
      </p>

      <pre>{`W_n(q,p) = ((-1)ⁿ / π) · exp(-2r²) · Lₙ(4r²)

where r² = q² + p²  and  Lₙ is the nth Laguerre polynomial`}</pre>

      <p>
        This follows from the matrix element of the displaced parity operator
        Π̂(q,p) = D†(q,p) (−1)^N̂ D(q,p) in the Fock basis (see Schleich 2001
        §3.3). The key observations:
      </p>

      <ul>
        <li>
          <strong>n = 0</strong>: W₀ = (2/π)·exp(−2r²) — a positive Gaussian.
          The ground state saturates Heisenberg&apos;s uncertainty relation with
          equal widths σ_q = σ_p = 1/√2. No negativity.
        </li>
        <li>
          <strong>n = 1</strong>: W₁ = (1/π)·(4r²−1)·exp(−2r²). Negative at
          the origin (where r &lt; 1/2), positive doughnut ring at r &gt; 1/2.
          The amber pit in the floor at r = 0 directly reads W &lt; 0.
        </li>
        <li>
          <strong>n = 5</strong>: W₅ = (1/π)·L₅(4r²)·exp(−2r²). The 5th
          Laguerre polynomial has five positive real zeros, so W₅ has five
          zero-crossings along any radial line, producing five concentric rings
          of alternating sign. The innermost sign is (−1)⁵ = −1 (amber).
        </li>
      </ul>

      <p>
        The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-gue-gaussian-unitary-ensemble-montgomery-1973-pair-correlation-sine-kernel-wigner-dyson-beta-family-stage-floor-webxr"
        >
          Wigner–Dyson level statistics
        </Link>{" "}
        (also named after Wigner) concern the eigenvalue spacing distribution of
        random matrices — a separate and later contribution. The Wigner function
        above is his 1932 phase-space construction.
      </p>

      <h2>Schrödinger cat state</h2>

      <p>
        A &ldquo;cat state&rdquo; is a superposition of two macroscopically
        distinct coherent states:
      </p>

      <pre>{`|ψ_cat⟩ = N (|+α⟩ + |−α⟩),   α = 2`}</pre>

      <p>
        where N = 1/√(2 + 2e^(−2α²)) is the normalisation. The Wigner function
        of this state is:
      </p>

      <pre>{`W_cat(q,p) = N²[ W_{+α}(q,p) + W_{−α}(q,p)
              + (2/π)·exp(−2(r²+α²)) · 2·cos(4pα) ]`}</pre>

      <p>
        The first two terms are Gaussian peaks centred at (q,p) = (±α, 0) — the
        classical locations of the two coherent components. The third term is the
        quantum interference: an oscillating function in p with spatial frequency
        4α/2π ≈ 1.27 per unit p for α = 2. These fringes:
      </p>

      <ul>
        <li>
          sit exactly between the two peaks, where neither classical component
          has support — they are purely non-local quantum interference
        </li>
        <li>
          are strongly negative between the crests, unlike the peaks which are
          purely positive
        </li>
        <li>
          decohere exponentially in time: the fringe amplitude decays as
          e^(−2α²·Γt) under environmental coupling, where Γ is the photon
          loss rate. Decoherence is fastest for large α ("more macroscopic")
        </li>
      </ul>

      <p>
        Compare with the{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-complex-ginzburg-landau-equation-1950-etd1-fourier-spectral-phase-defects-spiral-turbulence-stage-floor-webxr"
        >
          complex Ginzburg–Landau equation
        </Link>
        , where competing phases in a classical field produce spiral-wave
        interference. The cat-state fringes are the quantum analogue: interference
        between macroscopic wavepackets whose phase difference is 2α·p.
      </p>

      <h2>Squeezed vacuum</h2>

      <p>
        A squeezing operator S(ξ) with real squeeze parameter r deforms the
        vacuum ground state into an elliptical Gaussian:
      </p>

      <pre>{`W_sq(q,p) = (2/π) · exp(−2e^{2r}·q² − 2e^{−2r}·p²)

σ_q = e^{−r}/√2   (sub-vacuum noise in q)
σ_p = e^{+r}/√2   (super-vacuum noise in p)
σ_q · σ_p = 1/2   (Heisenberg saturated)`}</pre>

      <p>
        For r = 1.2 used here: σ_q ≈ 0.21 (compressed to 30% of vacuum),
        σ_p ≈ 2.33 (expanded to 330%). The floor shows a narrow ridge in q
        extended in p. Since the squeezed state is Gaussian, W ≥ 0 everywhere —
        no amber colouring. This contrasts sharply with SK_Fock1 and SK_Cat.
        Squeezed light at 10–15 dB below vacuum is the basis of the noise
        reduction in{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-gross-pitaevskii-bec-rotating-vortex-lattice-abrikosov-imaginary-time-split-operator-height-field-stage-floor-webxr"
        >
          quantum-enhanced interferometers
        </Link>{" "}
        (LIGO A+, Virgo, KAGRA).
      </p>

      <h2>Blueprint walkthrough</h2>

      <p>
        The blueprint uses SciPy&apos;s{" "}
        <code>scipy.special.eval_genlaguerre(n, 0, x)</code> to evaluate L_n(x)
        — the generalised Laguerre polynomial with α = 0, which equals the
        standard Laguerre polynomial. This avoids the numerical instability of
        the three-term recurrence at large n.
      </p>

      <pre>{`# Fock |n> Wigner function
def wigner_fock(n, Q, P):
    r2 = Q**2 + P**2
    return ((-1)**n / np.pi) * np.exp(-2*r2) * eval_genlaguerre(n, 0, 4*r2)

# Schrödinger cat |+alpha> + |-alpha>
def wigner_cat(alpha, Q, P):
    r2   = Q**2 + P**2
    norm = 1 / (2 + 2*np.exp(-2*alpha**2))
    W_p  = (2/np.pi) * np.exp(-2*((Q-alpha)**2 + P**2))
    W_m  = (2/np.pi) * np.exp(-2*((Q+alpha)**2 + P**2))
    W_i  = (2/np.pi) * np.exp(-2*(r2+alpha**2)) * 2*np.cos(4*P*alpha)
    return norm * (W_p + W_m + W_i)

# Squeezed vacuum with squeeze parameter r_sq
def wigner_squeezed(r_sq, Q, P):
    return (2/np.pi) * np.exp(
        -2*np.exp(2*r_sq)*Q**2 - 2*np.exp(-2*r_sq)*P**2
    )`}</pre>

      <p>
        The mesh construction uses <code>me.vertices.foreach_set</code> and{" "}
        <code>me.polygons.foreach_set</code> (direct data API, not{" "}
        <code>bpy.ops</code>) because operators require UI context that is
        absent in headless execution. The FLOAT_COLOR vertex attribute maps
        W &gt; 0 to cobalt and W &lt; 0 to amber through a linear blend at
        each vertex.
      </p>

      <h2>Troubleshooting</h2>

      <ul>
        <li>
          <strong>Fringes invisible in SK_Cat</strong>: the interference pattern
          has wavelength π/(2α) ≈ 0.39 units in p. Make sure the phase-space
          grid spans at least [−4, 4] in p and N ≥ 128; coarser grids
          under-resolve the fringes and produce aliasing.
        </li>
        <li>
          <strong>W_min/W_max look wrong</strong>: print the Python console
          output — the blueprint logs W_min and W_max for the Basis state.
          For |0⟩ expect W_max ≈ 0.637 (= 2/π) and W_min = 0 (no negativity).
          For |1⟩ expect W_min ≈ −0.318 (= −1/π at origin).
        </li>
        <li>
          <strong>Shape keys not exporting</strong>: the GLB export flag{" "}
          <code>export_morph=True</code> must be set. In the Blender GUI:
          File → Export → glTF 2.0 → Data → Mesh → Shape Keys ✓.
        </li>
        <li>
          <strong>scipy not found in Blender</strong>: install into Blender&apos;s
          Python with{" "}
          <code>
            /path/to/blender/python/bin/python -m pip install scipy
          </code>
          . As of Blender 4.2+ the Extensions Platform provides a SciPy wheel;
          in Blender 5.1 it is typically available from the bundled pip.
        </li>
      </ul>

      <h2>Further reading</h2>

      <p>
        The{" "}
        <Link
          className={lk}
          href="/tutorials/blender-tutorial-python-numpy-ssh-su-schrieffer-heeger-1979-zak-phase-topological-edge-states-spectral-flow-stage-floor-webxr"
        >
          SSH topological insulator
        </Link>{" "}
        entry shows a different use of the phase-space picture: the Zak phase
        is a Berry phase integrated around the 1D Brillouin zone — closely
        related to the symplectic structure that makes phase-space geometry
        so central to both classical and quantum mechanics.
      </p>
    </>
  );
}

export const entry: Entry = buildInstructable({
  slug: SLUG,
  title: TITLE,
  lede: LEDE,
  date: "2026-09-19",
  topic: "blender",
  Body,
});
