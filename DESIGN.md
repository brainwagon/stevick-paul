# The Stevick-Paul Telescope — Design Notes

Collected from David Stevick's original pages (archived at
<https://spider.seds.org/scopes/dstevick/stevpaul.html>) and the associated design
manual and Folded Stevick-Paul writeup.

## Overview

The Stevick-Paul telescope (SPT) is an unobstructed, all-reflecting, tilted-component
telescope (TCT). It has aspects of the Mersenne telescope (two confocal paraboloids) and
of the Schmidt camera. Despite a superficial resemblance to a TCT, **all mirrors are
coaxial**; the unobstructed view comes from using the optics **off-axis**.

Its defining property: in axial form it is a paraboloid freed of **all third-order
aberrations except a gentle field curvature (Petzval curvature)**. Used off-axis it
therefore yields paraboloidal-quality images across the field.

- 4 optical surfaces minimum: paraboloidal primary, spherical convex secondary,
  spherical concave tertiary, plus a flat diagonal to extract the focus.
- All higher-order aberrations, distortion, image (focal-plane) tilt and field
  curvature are minor.

## History

- **1935 — Maurice Paul (France)** first described the system as a zero-power corrector
  for large astronomical telescopes: two spherical mirrors of *mating curve* with the
  concave tertiary nominally in contact with the paraboloidal primary. Because of the
  large central obstruction of that axial arrangement, Paul regarded it as of
  theoretical value only.
- **1960s — Dr. J.G. Baker** independently rediscovered it. He moved the two spherical
  mirrors farther from the primary (reducing their diameter and obstruction, a condition
  allowed by Paul's equations) and added an approximate fifth-order correction by
  *turning the edge* of the convex secondary. Such designs became known as
  **Baker-Paul three-mirror systems**.
- **1991 — David Stevick**, while raytracing TCTs to improve the Tri-Schiefspiegler,
  rediscovered the arrangement. He found that when the secondary–tertiary spacing equals
  the tertiary radius of curvature, all aberrations vanish (spot diagrams collapse to
  points). Dr. Richard Buchroeder confirmed the work and identified it as an off-axis
  form of the Paul system. Dr. Baker allowed the name **Stevick-Paul telescope** since
  Stevick's design does not use a turned edge.
- **Also:** German amateur **Michael Brunn** independently discovered it (unpublished)
  while exploring 4-mirror Tetra-Schiefs (US Patent 5,142,417); he set it aside for lack
  of back focal length for his binocular attachments.
- **1993** — A.L. Woods demonstrated a pioneering 6" f/12 SPT at the Chicago Astrofest.
- Prototype: 10" f/6.2 by Stevick (used existing paraboloidal primary; only two
  spherical mirrors had to be made).

## Optical configuration and layout rules

### Mirror roles
1. **Primary** — paraboloidal. Same f-ratio as the final instrument.
2. **Secondary** — convex, spherical, positioned just to the side of the entering beam
   (leaving room for a light baffle). Positioned **afocally**: it sends *parallel* light
   to the tertiary.
3. **Tertiary** — concave, spherical, of *mating curve* to the secondary. Positioned
   exactly **twice** as far to the side of the entering beam as the secondary, and at its
   own radius of curvature distant from the secondary. Receiving parallel light, it forms
   an image at its focus just as it would with starlight.
4. **Diagonal (flat)** — throws the focus out of the telescope at 90° to the
   secondary–tertiary beam. Introduces an even number of reflections (correcting the
   reverted image from the odd count of the three curved mirrors). Does not obstruct
   light.

### Key principle
The radius of the spherical mirrors is **0.4 × the radius of curvature of the primary**
(the "radius ratio" A = 0.4 is optimum). This ratio is found to be optimum but other
ratios are possible.

## Design equations

Let:
- `D` = primary diameter
- `d` = diameter of the *clear* field
- `A` = radius ratio = (r.o.c. of spherical mirrors) / (r.o.c. of primary), normally 0.4
- `F1`, `F2`, `F3` = focal lengths of primary, secondary, tertiary (`F2` negative)
- `R3` = tertiary radius of curvature

**Mirror diameters**
- Eqn 1 — Secondary diameter: `A·D + (1 − A)·d`
- Eqn 2 — Tertiary diameter:  `A·D + (3 − A)·d`

**Central beam diameter** (same at secondary and tertiary)
- Eqn 13 — `A·D`

**Mirror tilts** (primary tilt determines all others)

- Eqn 3 — Primary tilt: `T1 = C / N`, where `N` = primary f-ratio and `C` is taken
  from the table below (values are empirically derived to assure freedom from stray
  light, valid for radius ratio 0.4 only).

  | Primary dia. | C     |
  |--------------|-------|
  | 4.25"        | 37.08 |
  | 6"           | 36.24 |
  | 8"           | 35.67 |
  | 10"          | 35.29 |
  | 12.5"        | 34.97 |
  | 16"          | 34.67 |

- Eqn 4 — Secondary tilt: `T2 = k·T1`, with `k = (1 + A) / (2A)`. For A = 0.4, `k = 1.75`.
- Eqn 5 — Tertiary tilt: `T3 = T2 − T1`
- Eqn 6 — Focal-plane tilt ≈ `4·T3`
- Eqn 14 — Diagonal tilt: `T4 = 45° − T3` (measured against the principal ray through
  the diagonal center).

Equations 4–6 are valid for all radius ratios; the Eqn 3 `C` table is valid for A = 0.4.

**Spacings** (note `F2` is negative)
- Eqn 7 — Primary–secondary: `e1 = F1 + F2`
- Eqn 8 — Secondary–tertiary: `e2 = R3`
- Eqn 9 — Tertiary–focal plane: `e3 = F3`

**Axis distances** (offsets between mirror centers)
- Eqn 10 — First axis distance: `a1 = sin(2·T1)·e1`
- Eqn 11 — Second axis distance: `a2 = 2·a1`
- Eqn 12 — Third axis distance: `a3 = a1/2`

## Field / image quality constraints

- **f-ratio:** Diffraction-limited performance possible down to about **f/5.6**, but
  **focal-plane tilt** increases as f-ratio decreases. Stevick restricts designs to
  **f/10 or longer**, keeping image anamorphism under 2% and focal-plane tilt under 10°.
- The prototype 10" f/6.2 works only if the eyepiece is square (fat f/6 cone won't
  tolerate a tilted eyepiece); top/bottom of field go out of focus. Shallower cones allow
  the eyepiece to be tilted to match the focal plane.
- **Radius ratio tradeoffs:**
  - `A < 0.4` → more compact (down to ~0.33, below which increasing primary–secondary
    spacing lengthens the instrument again), smaller primary tilt, smaller spherical
    mirrors, but a more steeply tilted focal plane.
  - `A > 0.4` → longer, larger primary tilt, larger spherical mirrors, less steeply
    tilted focal plane.
- With the preferred A = 0.4, the eyepiece falls close to the balance point, in a
  convenient viewing position with a short arc of travel.
- **Spherical aberration tolerance** is the same as a Newtonian of the same primary
  f-ratio (the primary f-ratio is preserved in the final system). Therefore any long-
  focus primary that could be left spherical in a Newtonian may also be left spherical
  here (e.g. an f/15 design can use a spherical primary).

## Design field / clear field table

The clear field is the diameter over which the design is fully illuminated; the design
field has a ½-magnitude loss at its edge. Smaller telescopes use a downsized design field
so they retain enough free cone.

| Primary size | Design field diam. | Clear field diam. |
|--------------|--------------------|-------------------|
| 4.25"        | 1/2"               | 0.28"             |
| 6"           | 3/4"               | 0.45"             |
| 8"           | 1"                 | 0.62"             |
| 10"          | 1"                 | 0.50"             |
| 12.5"        | 1"                 | 0.36"             |
| 16"          | 1"                 | 0.18"             |

Clear-field values should be considered minimums; instruments above 8" or with long
f-ratios may support up to the design field while retaining enough free cone.

## The diagonal mirror / baffling

- The focal plane lies *inside* the system of mirrors; the flat diagonal throws it clear.
- If the diagonal is placed to catch all light for a 1" field while not infringing the
  field rays between secondary and tertiary (upper position), insufficient residual cone
  remains to get the focus free. Increasing all tilts would lengthen the cone but worsen
  focal-plane tilt.
- **Solution:** nestle the diagonal against the central beam between secondary and
  tertiary (middle position) — it intrudes into the lower edge of the field but is clear
  at center and upper field — then slide it along the central beam toward the tertiary
  (lowest position) until it catches only enough of the top-edge rays to produce a
  **½-magnitude vignetting loss**.
- **Residual cone** = length of cone the diagonal can field.
- **Free cone** = the part of the residual cone on the observer's side of the parallel
  secondary–tertiary beam. Stevick looks for **at least 4 inches** of free cone (less
  requires a low-profile focuser).
- Diagonal **minor axis** = major axis / 1.4.
- An alternative is to send light out the *side panel* (focuser near the altitude axis,
  nearly stationary eyepiece); the diagonal then sits on its side against the parallel
  beam.
- **Exact raytraced placement (8" f/12):** the flat's upper edge rides tangent to the
  collimated secondary→tertiary beam and it captures the whole converging cone — centre
  at **26.5" from the tertiary**, surface **38.3° from the axis**, half-length **0.70"**
  (raytrace-verified: 100% cone capture, 0 rays blocked in any through-beam). This
  supersedes the approximate `T4 = 45−T3 = 42.77°` for construction; see `TRACE.md` §5.
- **Light baffle:** surrounds the converging cone from the primary, fitting into the
  notches where light paths cross. Sized to just pass the central beam intact, so
  vignetting technically begins immediately off-center but blocks <10% of light at the
  field edge. The diagonal's vignetting dominates.
- Primary tilt is chosen ~1" larger than the obscuration-free minimum to allow an
  effective baffle; by raytracing the light just clearing the baffle, Stevick ensures it
  approaches no closer than 1" to field center, giving a 2" diameter stray-light-free
  field (protects even 2" O.D. eyepieces).

## Worked designs

### Example A — Stevick's own 8" f/11.75 (from the Design Procedures)

Target was 8" f/12 (f.l. 96"); ground primary came out at 94" f.l. → f/11.75.

Primary r.o.c. = 188" → spherical-mirror curve = 0.4 × 188 = **75.2" radius**.

| Mirror | Diam. | Radius | Figure | Tilt (deg) | Dist. to next surface |
|--------|-------|--------|--------|------------|-----------------------|
| pri.   | 8"    | 188    | para   | 3.04       | 56.4                  |
| sec.   | 4.25" | −75.2  | sph    | 5.32       | 75.2                  |
| tert.  | 5"    | 75.2   | sph    | 2.28       | 28.75                 |
| diag.  | 1.63" | flat   | flat   | 42.72      | 8.85                  |
| f.p.   | 1"    | —      | —      | 9.1        | —                     |

- `k = 1.75` at A = 0.4 → T2 = 1.75 × 3.04 = 5.32°; T3 = 5.32 − 3.04 = 2.28°.
- Focal-plane tilt (Eqn 6) = 9.12° (raytrace exact value 9.07°).
- Axis distances: a1 = sin(2·3.04)·56.4 = 5.974" → rounded to **6"**; a2 = **12"**; a3 = **3"**.
- Central beam diameter = A·D = 3.2".
- Minimum mirror diameters (clear field 0.62"): secondary = 3.572", tertiary = 4.812"
  → uses standard 4.25" and 5" blanks.
- Diagonal minor axis ≈ 1.6" → specified next standard size 1-5/8".
- Diagonal–tertiary separation along principal ray = 28.75"; residual cone 8.85";
  nearly 5" of free cone available.

### Example B — A.L. Woods' 6" f/12

Pioneering SPT; primary left **spherical** (f/12 long enough). Displayed publicly at
Astrofest 1993.

### Example C — Bob Novack's Folded Stevick-Paul (FSP), 6" f/10

- Radius ratio **A = 0.45** (slightly higher than 0.4 → slightly less focal-plane tilt).
- Uses the flat to **fold** the light path, making the design more compact and
  **eliminating the separate diagonal mirror** (still 4 mirrors: primary, secondary,
  tertiary, folding flat). The flat sits in the **collimated beam between secondary and
  tertiary** (primary → secondary → flat → tertiary → focus), and the primary tilt is
  larger than the A = 0.4 table gives (2·T1 = 8.77° at f/10). See [`FSP.md`](FSP.md).
- Functions essentially the same as the standard SPT. An **f/15** version can use a
  spherical primary.
- Aberration balance: on/off-axis astigmatism and coma cancelled by mirror locations and
  tilts; spherical aberration is removed by the primary, put back by the secondary, and
  finally removed by the tertiary. Remaining distortion, image tilt and field curvature
  are minor.
- Building notes: primary parabolized (soft Foucault shadows — used a very narrow slit);
  secondary & tertiary interferometrically compared after nulling the concave; flat via
  Ritchey-Common against the spherical primary; all four mirrors given 96% enhanced
  coating. Baffled between entering beam and secondary with black-velvet-covered plate;
  plain black baffle in the triangular area between secondary and flat.
- Bob's summary: for purely *visual* use without an image-tilting lens, the fastest
  practical SP is about **f/10**; f/10–f/15 is still fast relative to most TCTs. A folded
  f/12–f/15 with three spheres may be the easiest off-axis scope to make at reasonable
  speed (avoids very long radii).

## Related / reference designs

- **Mersenne telescope** — two confocal paraboloids (SPT shares this aspect).
- **Paul system (1935)** — zero-power corrector; concave tertiary nominally contacted
  to the paraboloidal primary; large obstruction.
- **Baker-Paul three-mirror system** — moved spheres farther from primary; turned edge on
  the convex secondary for 5th-order correction.
- **Tetra-Schiefspiegler (Michael Brunn)** — US Patent 5,142,417; where Brunn
  independently found the arrangement.

## Key reference

- D. Stevick, "The Stevick-Paul Off-Axis Reflecting Telescope," *Amateur Telescope
  Makers Journal (ATMJ)*, Issue 3, pp. 4–9 (1993).

## Exact raytrace companion

`TRACE.md` + the figures and code in this directory contain an **exact raytrace** of the
8" f/12 version (A = 0.40): CAD layout (`sp_layout.png`/`.svg`/`.dxf`), spot diagrams at
0.00°/0.25°/0.50° field (`sp_spotdiagrams.png`), and Airy-disk plots (`sp_airy.png`).
Key verified results:

- Principal-ray angles: **2·T1 = 5.945°**, **2·T3 = 4.459°**, **9.000°** out of the
  tertiary (= the focal-plane tilt). All spacings at design values (57.6/76.8/38.4").
- **Diffraction limited**: geometric spot RMS 0.77 µm on-axis, rising only to ~1.06 µm at
  1° field, versus the 8.05 µm Airy radius (λ=550 nm, f/12).
- Physical mirror-axis tilts: primary +2.97°, secondary +0.74°, tertiary −6.73°
  (near-retro fold — these differ from Stevick's T1/T2/T3, which are kink half-angles).
- Diagonal clearance checked by raytrace: the flat threads between the collimated
  secondary→tertiary beam and the converging cone without blocking either (see `TRACE.md`
  §5). A naive cartesian placement obstructed ~10% of the collimated beam.
