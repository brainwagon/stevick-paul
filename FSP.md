# The Folded Stevick-Paul (FSP)

How to build the **folded variant** of the Stevick-Paul telescope, with CAD drawings.
For the background geometry and equations see [`DESIGN.md`](DESIGN.md); for the
unfolded instrument and its exact raytrace see [`TRACE.md`](TRACE.md).

## 1. What it is

The FSP is the **same 3-mirror Paul core** — a paraboloidal primary plus two *mating
spheres* (a convex secondary and a concave tertiary) — with a **flat folding mirror
placed in the collimated beam between the secondary and the tertiary**. The order is:

**primary → secondary → folding flat → tertiary → focus**

The flat throws the secondary's collimated beam back across the tube to a tertiary that
sits *below* the incoming beam; the tertiary then sends its converging cone up past the
edge of the flat to a focus just behind and above the primary. The flat replaces the
standard SP's diagonal, so it is still four mirrors. This order is fixed by Novack's
drawing (legs labelled 32.8" primary–secondary, 31.7" secondary–flat, 22.7" flat–tertiary,
27.2" tertiary–focus) and by his text: a baffle sits "in the triangular area between the
secondary and the flat and runs parallel to the beam between the secondary and the flat".

| | Standard SP | Folded SP (FSP) |
|---|---|---|
| Radius ratio `A` | 0.40 (optimum) | 0.45 (Novack: 27.2/60 = 0.453) |
| Primary tilt `T1` | `C/N`, C ≈ 35.7 | larger: `C/N` with **C ≈ 43.85** (Novack's 8.77° fold at f/10) |
| Flat | diagonal in the tertiary's converging cone | fold flat in the collimated secondary→tertiary beam |
| Focus | beside the long tube | just behind/above the primary |
| Look | long tube / Schiefspiegler-like | compact box ~0.6 F1 long |

The C table in [`DESIGN.md`](DESIGN.md) is for A = 0.4 and a straight layout; the fold
needs a larger primary tilt so the tertiary can sit clear of the incoming beam. Novack's
drawing gives 2·T1 = 8.77° at f/10 (`T1 = 4.385°`), and with Stevick's equations
(`T2 = (1+A)/(2A)·T1`, `T3 = T2 − T1`, tertiary turning the chief ray by 2·T3) that one
number reproduces **every** point on his drawing to 0.01".

![Novack's 6" f/10 FSP regenerated from Stevick's equations](fsp_folded.png)

Raytraced, the regenerated 6" f/10 has an on-axis RMS spot of 0.58 µm (Airy radius
6.7 µm), with best focus at exactly his 27.2" — so the drawing is a real, corrected
design, not a sketch. With a full round 4" flat centred on the chief ray, the flat's
edge clips about 20% of the returning tertiary→focus cone (the used footprint on the
flat is ±1.40" and the returning cone passes 0.47" beyond it); that is why Novack
"chamfered off its hip".

## 2. CAD drawings — 8" f/12

Meridional layout of an 8" f/12 scaled from Novack's design (also `.svg` and `.dxf`):

![FSP 8" f/12 meridional layout](fsp_layout.png)

Files:
* `fsp_layout.png` / `fsp_layout.svg` / `fsp_layout.dxf` — 8" f/12 meridional layout
* `fsp_folded.png` — Novack's 6" f/10, regenerated (compare with his `fspdiagm.gif`)

## 3. Prescription — 8" f/12, A = 0.45

Scaled from Novack's 6" f/10: same `C = N·T1 = 43.85` (so the angles scale as 1/N, like
the beam geometry), same fold angle 29.36°, and the flat at the same fraction (31.7/54.4
= 58.3%) of the secondary–tertiary spacing. This is a reconstruction, not a prescription
Novack published. Coordinates are as drawn: x along the tube with light travelling +x,
primary vertex at the origin, y up. Angles are measured from +x.

| Surface | Diameter | Vertex (x, y) | Radius | Conic | Surface normal | Next leg |
|---------|----------|---------------|--------|-------|----------------|----------|
| Primary — paraboloid | 8.0" | (0.00, 0.00) | 192.0" | −1 | 176.35° (3.65° tilt) | 52.80" to secondary |
| Secondary — convex sphere | 4.25" | (−52.37, 6.72) | 86.4" | 0 | 178.58° (1.42° tilt) | 50.35" to flat |
| Folding flat | 4.0" | (−2.18, 10.64) | ∞ | — | −160.85° (19.15° from square to the tube) | 36.05" to tertiary |
| Tertiary — concave sphere | 5.75" (min 5.5") | (−32.13, −9.43) | 86.4" | 0 | 31.59° | 43.20" to focus |
| Focus | — | (5.52, 11.75) | — | — | nominal tilt 4·T3 ≈ 8.9° (eqn 6) | — |

Derived: F1 = 96", F2 = −43.2", F3 = 43.2"; `T1 = 3.654°`, `T2 = 5.887°`, `T3 = 2.233°`.
Angles between the arriving and leaving chief ray at each mirror (as Novack labels
them): primary **7.31°**, secondary **11.77°**, flat **29.36°**, tertiary **4.47°**.
Chief-ray directions: primary→secondary 172.69°, secondary→flat 4.47°, flat→tertiary
−146.17°, tertiary→focus 29.36°. Mirror diameters from DESIGN.md eqns 1–2 with a 0.75"
field (Novack's sizes imply 0.6–0.75").

Raytrace (`fsp_outputs.py`): on-axis RMS **0.38 µm** (Airy radius 8.05 µm at 550 nm).
All 1,793 sampled pupil rays land on every mirror in turn and no beam passes through any
other mirror. Smallest edge clearances to a foreign beam: secondary 0.59" (incoming
beam), flat 0.53" (returning tertiary→focus cone), tertiary 3.50", primary 4.69". At 8"
f/12 a round 4" flat needs no chamfer.

## 4. Reference: Novack's 6" f/10, as drawn

| Surface | Diameter | Radius | Conic | Next leg |
|---------|----------|--------|-------|----------|
| Primary — paraboloid | 6.0" | 120.0" (FL 60") | −1 | 32.8" |
| Secondary — convex sphere | 3.12" | 54.4" (FL 27.2") | 0 | 31.7" to flat |
| Folding flat | 4.0" | ∞ | — | 22.7" to tertiary |
| Tertiary — concave sphere | 4.25" | 54.4" (FL 27.2") | 0 | 27.2" to focus |

Angles at the mirrors: 8.77°, 14.04°, 29.36°, 5.29°. Stevick's equations with
T1 = 4.385° give 8.77°, 14.06°, 29.36° (chosen), 5.29°; vertices at (−32.42, 5.00)
secondary, (−0.85, 7.92) flat, (−19.53, −4.98) tertiary, focus (4.18, 8.35).

## 5. Construction sequence

1. **Make the paraboloidal primary** first, to the same f-ratio as the finished
   telescope (its f-ratio is preserved). At **f/15 the primary may be left spherical**
   — Novack's recommended simplification for the FSP.
2. **Make the two mating spheres together.** Grind the concave (tertiary) and convex
   (secondary) so they share the same radius `R = A·R1` (86.4" for the 8" f/12). Finish
   the **concave tertiary first** — it is testable like any Newtonian mirror — and use it
   as the **test plate** for the convex secondary (contact/interference test).
3. **Measure the actual radii**, then recompute `e1`, `e2`, `e3` and the tilts from the
   real numbers before making anything else.
4. **Draw the layout full-scale** (this is mandatory). Lay in the mirror centers from the
   spacings and axis distances, bisect the principal-ray angles, and draw the mirror
   surfaces perpendicular to the bisectors. Locate the **folding flat** and the focus —
   see §6.
5. **Make the flat.** A good flat can be made by the Ritchey-Common test against the
   spherical primary (the method Novack used).
6. **Build the structure** with tip/tilt on all mirrors and longitudinal adjustment on
   the primary–secondary spacing (the only spacing that matters much). Blacken all mirror
   edges and chamfer/blacken the flat's hip so it doubles as a baffle.
7. **Coat and collimate** — see [`BUILD_NOTES.md`](BUILD_NOTES.md); alignment is
   geometric (no star-test procedure).

## 6. Placing the folding flat (the critical step)

The flat sits in the **collimated** beam from the secondary, so its position along that
beam does not affect focus — only where the tertiary ends up. Novack put it 58% of the
way from secondary to tertiary, near the primary end of the tube, and turned the beam
through 29.36° back down across the tube. Then:

* the tertiary lands below the incoming beam (3.5" clear at 8" f/12), on the far side of
  the tube from the secondary;
* the flat→tertiary and tertiary→focus legs cross the incoming beam in free air (beams
  crossing beams is harmless; only mirrors obstruct);
* the tertiary→focus cone passes just beside the flat's edge on its way to the focus
  behind the primary. This is the tight clearance: 0.53" at 8" f/12, 0.47" at 6" f/10
  (where Novack chamfered the flat's hip). Re-check it on the full-scale drawing.

Keep `flat→tertiary + secondary→flat = e2 = R3` exactly: that spacing is part of the
Paul correction.

## 7. Notes and trade-offs

* **A = 0.45**: slightly less focal-plane tilt per unit T3 than A = 0.40, but the fold
  needs a larger primary tilt, so the net focal-plane tilt (≈ 8.9° at 8" f/12) is about the same as the standard SP's 9.0°.
* **Focal plane is still tilted** (≈4·T3 ≈ 8.9° at 8" f/12) and gently curved; tilt the
  eyepiece/sensor to match. Not a wide-field imaging telescope.
* **At f/15 the primary can be spherical**, which removes the only parabolizing step.
* **Four reflections** → use enhanced coatings (~0.85 transmission).
* The fold makes the tube a **compact box** about 0.6·F1 long; the focus is at the
  closed (primary) end, above the primary.

## 8. Reproduce

```bash
python3 fsp_outputs.py        # writes fsp_layout.{png,svg,dxf} and fsp_folded.png
```

Uses the raytracer in [`sp_model.py`](sp_model.py).

## 9. References

* R. Novack, "A New Telescope Design: Folded Stevick-Paul Four-Mirror F10 Reflecting
  Telescope," AmSky/SEDS archive:
  <https://web.archive.org/web/20050309051430/http://www.amsky.com/atm/telescopes/spscopes/spt.html>
* D. Stevick, "The Stevick-Paul Off-Axis Reflecting Telescope," *ATMJ* Issue 3, pp. 4–9
  (1993).
