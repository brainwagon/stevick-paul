# Building an 8" Stevick-Paul — Notes for the Workshop

Companion to `DESIGN.md`. Aimed at an instructor advising a student who wants an
8" Stevick-Paul (SP) rather than the usual Newtonian.

---

## 1. Should this student build it?

**Verdict:** an 8" SP is an *advanced* project — several times the work of an 8"
Newtonian, with one genuinely hard step (the convex secondary) and one skill that
Newtonians never teach (off-axis tilted alignment). It is an excellent **second or
third** telescope and a poor **first** telescope.

Quick scorecard:

| | 8" Newtonian | 8" Stevick-Paul |
|---|---|---|
| Precision surfaces | 1 powered + 1 flat | 2 powered + 1 powered + 1 flat |
| Convex surface to test | no | **yes (hardest step)** |
| Central obstruction | ~16–25% | none |
| Alignment | star test, well documented | geometric, no standard procedure |
| Build support/kits/parts | enormous | a handful of instruments, none |
| Typical build time (first timer) | weeks–months | months–years, high risk |

Decision guide:
- **First mirror / first scope →** steer to an 8" f/6–f/8 Newtonian. Build the SP as a
  follow-on.
- **Experienced, motivated, wants the challenge →** build the SP, ideally **folded,
  f/12–f/15, A = 0.4–0.45, spherical primary** (see §2 and §5).

---

## 2. Concrete prescriptions (8", radius ratio A = 0.4)

Both use: primary diameter D = 8", clear field d = 0.62", central beam diameter
A·D = 3.2". Minimum secondary diameter 3.57" (use a 4.25" blank); minimum tertiary
4.81" (use a 5" blank). Axis distances are **a1 = 6", a2 = 12", a3 = 3"** in both
designs (for A = 0.4, 8", a1 is essentially independent of f-ratio).

### 8" f/12 (recommended all-round)

| Mirror | Diameter | Radius | Figure | Tilt | Spacing to next surface |
|--------|----------|--------|--------|------|-------------------------|
| Primary | 8.0" | 192.0" | **paraboloid** | 2.97° | e1 = 57.6" |
| Secondary | 4.25" (3.57 min) | −76.8" | spherical, **convex** | 5.20° | e2 = 76.8" |
| Tertiary | 5.0" (4.81 min) | 76.8" | spherical, concave | 2.23° | e3 = 38.4" to focus |
| Diagonal | 1⅝" minor axis | flat | flat | 42.77° | residual cone to focus |
| Focal plane | 1.0" design field | — | — | tilt ≈ 8.9° | — |

Derived: k = 1.75; T1 = C/N with C = 35.67; T2 = k·T1; T3 = T2 − T1; T4 = 45° − T3;
fp tilt ≈ 4·T3. Exact raytraced tilt runs ~0.2° above the formula.

### 8" f/15 (easiest optics, longest tube)

| Mirror | Diameter | Radius | Figure | Tilt | Spacing to next surface |
|--------|----------|--------|--------|------|-------------------------|
| Primary | 8.0" | 240.0" | **sphere OK** | 2.38° | e1 = 72.0" |
| Secondary | 4.25" (3.57 min) | −96.0" | spherical, convex | 4.16° | e2 = 96.0" |
| Tertiary | 5.0" (4.81 min) | 96.0" | spherical, concave | 1.78° | e3 = 48.0" to focus |
| Diagonal | 1⅝" minor axis | flat | flat | 43.22° | residual cone to focus |
| Focal plane | 1.0" design field | — | — | tilt ≈ 7.1° | — |

**f/12 vs f/15 tradeoff:** f/15 removes the need to parabolize the primary and gives a
flatter, more forgiving focal plane, at the cost of a longer instrument and larger
spherical-mirror radii (bigger blanks, longer grinding strokes). f/12 is more compact
and usable; you pay with a (small) parabolizing job and a slightly steeper field.

**Fold option:** following Novack's FSP, the flat can fold the light and *eliminate the
separate diagonal*, giving a compact package. Novack judged a **folded f/12–f/15 with
three spheres the easiest off-axis scope that can actually be made** at reasonable
speed.

---

## 3. Why the Stevick-Paul cannot be scaled to faster focal ratios

The blockage is **not** aberration correction (that is the design's whole strength,
perfect to third order) — it is the **tilt of the focal plane**, which is intrinsic to
using the Paul system off-axis and which grows as the cone gets faster.

1. **Focal-plane tilt scales as 1 / f-number.** From the design equations
   (A = 0.4, 8"): T1 = C/N, T2 = 1.75·T1, T3 = 0.75·T1, and fp tilt ≈ 4·T3 ≈ 3C/N ≈
   **107/N degrees**. So:

   | f/# | Primary tilt T1 | Focal-plane tilt (≈3C/N) |
   |-----|-----------------|--------------------------|
   | f/15 | 2.38° | ~7.1° |
   | f/12 | 2.97° | ~8.9° |
   | f/10 | 3.57° | ~10.7° |
   | f/8  | 4.46° | ~13.4° |
   | f/6  | 5.95° | ~17.8° |
   | f/5.6| 6.37° | ~19.1° |

   Stevick deliberately caps designs at **f/10**, keeping focal-plane tilt under 10°.

2. **Eyepieces can't tolerate a steeply tilted image in a fast cone.** A fast cone has
   only a small depth of focus, so a tilted focal plane smears the field unless the
   eyepiece itself is tilted by the same angle. At large tilt angles the eyepiece's own
   aberrations and the field/exit-pupil mismatch degrade the view. On the f/6.2
   prototype the eyepiece had to be kept square, and even then the top and bottom of
   the field were out of focus — which is exactly why Stevick recommends f/10+.

3. **Image anamorphism** (differential magnification across the tilted field) also grows
   with tilt. Stevick keeps it under 2%, which again forces a slow f-ratio.

4. **Field curvature becomes relatively worse as f/ratio drops.** The one residual
   third-order aberration — a gently curved Petzval surface — is fixed in absolute terms
   by the mirror radii. As the cone gets faster the depth of focus shrinks, so the same
   curvature eats a larger fraction of the sharp zone.

5. **The only escape is refractive correction.** An image-tilting / field-flattening
   lens lets you go faster, but adds glass, alignment, and chromatic issues to an
   otherwise all-reflecting design. As Novack put it, unless you use an image-tilting
   lens, **the fastest practical SP for visual use is about f/10.** (f/5.6 is quoted as
   the diffraction-limited floor, purely theoretical for visual use.)

Note the primary tilt and mirror diameters do *not* force slowness — radii actually
*shrink* with f-ratio. The f-ratio floor is entirely the tilted, fast focal plane versus
the eyepiece.

---

## 4. Optical performance vs conventional 8" Newtonians

Assume a well-made SP at f/12 and a good 8" Newtonian at f/6–f/8 with a ~16–25%
secondary obstruction.

**Where the SP wins**
- **No central obstruction → better contrast.** A ~20% obstruction pushes energy into
  the diffraction rings and lowers mid-spatial-frequency MTF by roughly 10–15%. For
  low-contrast planetary detail the unobstructed SP is genuinely better, and there is no
  spider diffraction spike.
- **Third-order perfection.** All Seidel aberrations (spherical, coma, astigmatism,
  distortion) go to zero except Petzval curvature. Within its usable field the SP is
  free of the coma that limits a fast Newtonian's off-axis image (an f/6 Newtonian's
  diffraction-limited field is only a few arcminutes; f/8 is better but still comatic).
- **Perfectly achromatic** (all-reflecting), same as a Newtonian.

**Where the Newtonian wins**
- **Flat, untilted, normally-oriented focal plane.** No eyepiece tilt, no anamorphism.
- **Light throughput.** 4 reflections vs 2: with 96% enhanced coatings, ~0.85 vs ~0.92
  transmission; with standard ~89% aluminum, ~0.63 vs ~0.79. The SP gives away roughly
  7–16% of its light to the extra two reflections, and each surface is another
  thermal/alignment liability.
- **Usable field.** The SP is *designed* with ~½-magnitude vignetting at the field edge
  and a tunnel-vision diagonal nestling the beam; a Newtonian with a properly sized
  secondary has an unvignetted field.
- **Practicality, cost, robustness, support.** A ~4 ft f/6 Newt tube on a Dob mount
  versus a 4-mirror tilted train at ~8 ft (f/12) focal length. Newtonians win massively
  on cost, time, thermal stability, and the availability of help.

**Tie**
- On-axis sharpness: both reach the diffraction limit when well made. At 8" aperture the
  SP's theoretical advantages over a *good* Newtonian are real but modest and mostly
  show up as contrast on planets and coma-free imaging over a wider (but vignetted and
  tilted) field.

**Bottom line for the student:** the SP is optically elegant and does deliver the
unobstructed, coma-free image, but at 8" the payoff over a careful slow Newtonian is
incremental while the build cost, risk, light loss, and field compromises are large. Its
real draw is the design itself and the challenge — not a decisive performance win at
this aperture.

---

## 5. Milestone checklist / project plan

**Phase 0 — Design & layout**
- [ ] Choose f/ratio (start f/12, A = 0.4). Record target numbers from §2.
- [ ] Raytrace / verify with a tilted-component program (Stevick's *Spot* / *WinSpot*,
      or a modern TCT raytracer). Confirm focal-plane tilt and free cone.
- [ ] Make a **full-scale drawing** on paper: mirror centers, principal-ray path, mirror
      surfaces at right angles to bisected ray angles, tick marks for clear-field
      diameters. (Stevick considers this mandatory — the diagonal placement and free
      cone are *measured off the drawing*.)
- [ ] Decide: standard 4-mirror vs folded (FSP). Decide make-vs-buy per mirror.

**Phase 1 — Primary**
- [ ] Grind/polish 8" f/12 primary to 192" r.o.c.
- [ ] f/12 → parabolize (correction is tiny; shadows are soft — use a narrow slit).
- [ ] f/15 → may be left spherical (verify SA within Rayleigh limit).
- [ ] Test (Foucault / Ronchi). Note: SA tolerance equals a Newtonian of the same
      f-ratio.

**Phase 2 — Concave tertiary FIRST**
- [ ] Grind/polish the 5" concave sphere to r.o.c. 76.8" (f/12) or 96" (f/15).
- [ ] Null/test it as a sphere (it is testable exactly like a Newtonian mirror).
- [ ] This becomes the **test plate** for the secondary — do it before the convex.

**Phase 3 — Convex secondary (the hard step)**
- [ ] Grind the 4.25" convex to the *mating* radius.
- [ ] Polish against the finished tertiary as a **test plate**; bring it in until it
      shows **straight fringes** (Newton's-ring / interference test). This requires a
      monochromatic source and careful contact testing.
- [ ] Cross-check: both surfaces must be the same radius and both good spheres.

**Phase 4 — Diagonal flat**
- [ ] Make/obtain a flat, 1⅝" minor axis (major-axis/1.4). Ritchey-Common against the
      spherical primary is an amateur-proven route.

**Phase 5 — Structure & mirror cells**
- [ ] Build tube/structure holding mirrors at the spacings (e1, e2, e3), tilts (T1–T3),
      and axis offsets (a1 = 6", a2 = 12", a3 = 3").
- [ ] Provide **tip/tilt on every mirror** (the tilts lock to the primary tilt, so you
      need independent adjusters).
- [ ] Decide exit: across the parallel secondary–tertiary beam (42.77° diagonal), out the
      side panel (diagonal on its side, focuser near the altitude axis), or folded.

**Phase 6 — Baffling**
- [ ] Fit a light baffle around the primary's converging cone, sized to just pass the
      central (3.2") beam, fitting the notches where light paths cross.
- [ ] Blacken mirror edges; baffle the diagonal; verify no ray reaches within 1" of field
      center (⇒ 2" stray-light-free field).

**Phase 7 — Coating**
- [ ] Coat all surfaces (96% enhanced recommended — 4 reflections make throughput matter).
      Blacken edges after coating.

**Phase 8 — Assembly, alignment, first light**
- [ ] Assemble to the full-scale drawing; set tilts and offsets geometrically.
- [ ] Focus test: verify the focal plane tilt; tilt the eyepiece holder to match
      (~8.9° at f/12), or accept center-only sharpness at higher tilt.
- [ ] Star test; check edge-of-field vignetting (~½ mag by design).

**Phase 9 — Document & iterate**
- [ ] Record the as-built prescription and any deviations (ground radii rarely hit
      target — recompute tilts/spacings from the actual primary r.o.c., as Stevick did
      when his 8" came out f/11.75 instead of f/12).

---

## 6. Tooling & testing summary

- **Required:** full-scale drawing surface, spherometer, Foucault/Ronchi tester with a
  narrow slit, monochromatic source (or laser) for the convex/concave contact test, an
  interference/contact test setup for the mating spheres, and a way to measure tilt
  angles precisely (protractor/levels/fixtures).
- **No standard collimation tool applies.** You align to geometry, not to a defocused
  star; the fixed tilt relationships mean the primary tilt is the master.
- **Testing the convex is the single biggest risk** and the reason to finish the concave
  tertiary first.

## 7. Risk register & fallbacks

| Risk | Mitigation / fallback |
|------|-----------------------|
| Convex secondary can't be tested/matched | Finish concave tertiary first; use it as test plate; fall back to buying a custom convex sphere |
| Primary misses target r.o.c. | Recompute all tilts/spacings from actual value (normal, expected) |
| Focal-plane tilt too harsh at chosen f/# | Move to a longer f/# (f/12 → f/15) or add an image-tilting lens |
| Alignment never converges | Build rigid, draw-first, tip/tilt everywhere; consider the folded layout for compactness |
| Diagonal shadows the collimated beam | The flat must ride tangent between the collimated and converging beams (only a fraction of an inch of clearance) — derive its position from the full-scale drawing and check clearance. See `TRACE.md` §5 |
| Cost/time overrun | Buy the primary; reduce aperture; build a Newtonian first |

## 8. References

- D. Stevick, "The Stevick-Paul Off-Axis Reflecting Telescope," *ATMJ* Issue 3,
  pp. 4–9 (1993).
- D. Stevick's design pages (archived): <https://spider.seds.org/scopes/dstevick/stevpaul.html>
  (theory, design procedures, system layout) and `folded.html` / `fsp.html`
  (Novack's folded f/10).
- See `DESIGN.md` in this directory for the full equation set and source notes.
