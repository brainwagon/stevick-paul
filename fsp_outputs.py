"""
Folded Stevick-Paul (FSP) -- figures.

FSP = the same 3-mirror Paul core (paraboloid primary + two mating spheres) with a
*flat folding mirror* in the converging beam that sends the final leg back toward
the primary-side focus. Radius ratio A = 0.45 (Novack), vs 0.40 for the standard SP.

Uses sp_model for the raytracer.  Writes fsp_layout.{png,svg,dxf} and
fsp_folded.png into /home/markv/stevick-paul.
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sp_model as M

OUT = "/home/markv/stevick-paul"

# ---- Reconstructed 8" f/12 FSP core, based on Novack's 6" f/10 design ----
A = 0.45
s, info = M.build_sp(N=12.0, D=8.0, A=A, C=35.67, tilt3_deg=-7.25)
V1, V2, V3, Fp = info["V1"], info["V2"], info["V3"], info["Fp"]
d3, din = info["d3"], info["din"]


def surface_points(su, half):
    n = su.n
    radial = np.array([0.0, n[2], -n[1]])
    radial = radial / np.linalg.norm(radial)
    pts = []
    for r in np.linspace(-half, half, 200):
        if su.flat:
            pts.append(su.v + r * radial); continue
        disc = su.R**2 - (1 + su.k) * r**2
        if disc < 0:
            continue
        ss = (su.R - np.sqrt(disc)) / (1 + su.k) if (1 + su.k) != 0 else r**2 / (2 * su.R)
        pts.append(su.v + ss * n + r * radial)
    return np.array(pts)


# ---- place the folding flat: upper edge tangent to the collimated beam,
#      capturing the whole converging cone (same method as the standard SP) ----
segs = []
for x, y in M.pupil_rays(8.0, 12):
    r = M.trace(s, np.array([x, y, 120.0]), din)
    if r:
        segs.append(r[0])


def env_st_lower(z):
    ys = []
    for pts in segs:
        A_, B_ = pts[2], pts[3]
        if (A_[2] - z) * (B_[2] - z) <= 0 and abs(B_[2] - A_[2]) > 1e-9:
            t = (z - A_[2]) / (B_[2] - A_[2]); ys.append(A_[1] + t * (B_[1] - A_[1]))
    return min(ys) if ys else None


# fold the beam back toward the primary-side package (roughly -y)
out = np.array([0.0, -0.997, 0.0777]); out /= np.linalg.norm(out)
nd = out - d3; nd /= np.linalg.norm(nd)         # flat normal
u = np.array([0.0, -nd[2], nd[1]]); u /= np.linalg.norm(u)
if u[1] < 0:
    u = -u
cone = []
for x, y in M.pupil_rays(8.0, 12):
    r = M.trace(s, np.array([x, y, 120.0]), din)
    if r:
        cone.append((r[0][-1], r[1]))

best = None
for t in np.arange(18, 40, 0.25):
    Pd = V3 + t * d3
    Lmax = 0.0
    for Lv in np.linspace(0, 3, 301):
        P = Pd + Lv * u
        e = env_st_lower(P[2])
        if e is None or P[1] > e:
            break
        Lmax = Lv
    if Lmax < 0.4:
        continue
    hit = 0
    for P, dd in cone:
        if abs(dd @ nd) < 1e-12:
            continue
        tt = -((P - Pd) @ nd) / (dd @ nd)
        if tt < 0:
            continue
        X = P + tt * dd
        if abs((X - Pd) @ u) <= Lmax:
            hit += 1
    frac = hit / len(cone)
    if best is None or frac > best[1]:
        best = (t, frac, Lmax, Pd.copy(), hit)
tflat, frac, Lmax, Pflat, hit = best
print(f"folding flat: t={tflat:.2f}\" from tertiary, capture={frac*100:.1f}%, half-len={Lmax:.2f}\"")
fold_angle = np.degrees(np.arctan2(u[1], u[2]))
fold_angle = (fold_angle + 90) % 180 - 90  # mirror-plane angle is modulo 180°
print(f"flat surface angle from axis = {fold_angle:.2f} deg")
flat_minor = 2.0
flat_major = 1.4 * flat_minor
flat_upper = Lmax
flat_lower = flat_upper - flat_major
flat_center = Pflat + (flat_lower + flat_upper) / 2 * u
print(f"flat center (y,z)=({flat_center[1]:.3f}, {flat_center[2]:.3f})")
Ffold = Pflat + M.reflect(Fp - Pflat, nd)
image_normal = M.reflect(np.array([0.0, 0.0, 1.0]), nd)
image_tangent = np.array([0.0, -image_normal[2], image_normal[1]])


def folded_ray(P, direction):
    """Intersect a tertiary ray with the flat and then the reflected image plane."""
    den = direction @ nd
    if abs(den) < 1e-12:
        return None
    t = ((Pflat - P) @ nd) / den
    if t <= 0:
        return None
    hit_point = P + t * direction
    reflected = M.reflect(direction, nd)
    den_image = reflected @ image_normal
    if abs(den_image) < 1e-12:
        return None
    t_image = ((Ffold - hit_point) @ image_normal) / den_image
    if t_image <= 0:
        return None
    return hit_point, hit_point + t_image * reflected


def verify_flat_clearance():
    """Check sampled pupil rays against the flat before and after the tertiary."""
    upstream_hits = [0, 0, 0]
    downstream_misses = 0
    downstream_mirror_hits = [0, 0, 0]
    valid = 0
    for x, y in M.pupil_rays(8.0, 24):
        ray = M.trace(s, np.array([x, y, 120.0]), din)
        if not ray:
            continue
        points, direction = ray
        valid += 1
        for j in range(3):
            p, q = points[j], points[j + 1]
            segment = q - p
            den = segment @ nd
            if abs(den) < 1e-12:
                continue
            t = ((Pflat - p) @ nd) / den
            if 0.0 <= t <= 1.0:
                along_flat = (p + t * segment - Pflat) @ u
                intersection = p + t * segment
                if (flat_lower <= along_flat <= flat_upper
                        and abs(intersection[0]) <= flat_minor / 2):
                    upstream_hits[j] += 1
        folded = folded_ray(points[-1], direction)
        if folded is None:
            downstream_misses += 1
        else:
            along_flat = (folded[0] - Pflat) @ u
            if (not flat_lower <= along_flat <= flat_upper
                    or abs(folded[0][0]) > flat_minor / 2):
                downstream_misses += 1
            else:
                hit_point, image_point = folded
                outgoing = M.reflect(direction, nd)
                image_distance = np.linalg.norm(image_point - hit_point)
                apertures = [4.0, 2.125, 2.625]
                for j, surface in enumerate(s):
                    mirror_hit = surface.intersect(hit_point, outgoing)
                    if mirror_hit and mirror_hit[0] < image_distance:
                        offset = mirror_hit[1] - surface.v
                        offset -= (offset @ surface.n) * surface.n
                        if np.linalg.norm(offset) <= apertures[j]:
                            downstream_mirror_hits[j] += 1
    if any(upstream_hits) or downstream_misses or any(downstream_mirror_hits):
        raise RuntimeError(
            f"folding-flat clearance failed: upstream={upstream_hits}, "
            f"misses={downstream_misses}, postfold mirror hits={downstream_mirror_hits}"
        )
    print(f"clearance check: {valid} pupil rays; 2\"-minor flat; no obstructions; all captured")


verify_flat_clearance()


def make_layout():
    fig, ax = plt.subplots(figsize=(15, 5.6))
    cols = ["#1f4e79", "#c00000", "#2e7d32"]
    labs = ["Primary (paraboloid)", "Secondary (convex sphere)", "Tertiary (concave sphere)"]
    for su, h, c, lb in [(s[0], 4.0, cols[0], labs[0]),
                         (s[1], 2.125, cols[1], labs[1]),
                         (s[2], 2.625, cols[2], labs[2])]:
        p = surface_points(su, h)
        ax.plot(p[:, 2], p[:, 1], color=c, lw=4, solid_capstyle="round",
                label=f"{lb}  R={su.R:+.1f}\"")
    pr = np.array([V1, V2, V3, Pflat, Ffold])
    ax.plot(pr[:, 2], pr[:, 1], "k--", lw=1.2, alpha=0.85, label="folded principal ray")
    # input
    ax.plot([95, 0], [4, 4], color="#555", lw=0.8)
    ax.plot([95, 0], [-4, -4], color="#555", lw=0.8)
    ax.annotate("", xy=(0, 0), xytext=(92, 0),
                arrowprops=dict(arrowstyle="-|>", color="#555", lw=1.4))
    ax.text(60, 6.2, '8" collimated input', color="#333", fontsize=10)
    # marginal bundle
    for x, y in [(-4, 0), (0, -4), (0, 4), (4, 0)]:
        r = M.trace(s, np.array([x, y, 95.0]), din)
        if not r:
            continue
        pts = r[0]
        ax.plot(pts[:, 2], pts[:, 1], color="#ff7f0e", lw=0.7, alpha=0.7)
        folded = folded_ray(pts[-1], r[1])
        if folded:
            X, Q = folded
            ax.plot([pts[-1, 2], X[2]], [pts[-1, 1], X[1]],
                    color="#ff7f0e", lw=0.7, alpha=0.7)
            ax.plot([X[2], Q[2]], [X[1], Q[1]],
                    color="#ff7f0e", lw=0.7, alpha=0.7)
    image_ends = np.array([Ffold - 0.5 * image_tangent, Ffold + 0.5 * image_tangent])
    ax.plot(image_ends[:, 2], image_ends[:, 1], color="k", lw=2.5)
    ax.plot(Ffold[2], Ffold[1], "k+", ms=12, mew=2)
    ax.text(Ffold[2] - 10.0, Ffold[1] + 1.0,
            "image plane\n7.25° to chief ray",
            fontsize=9.5, ha="left")
    # folding flat
    dpts = np.array([Pflat + flat_lower * u, Pflat + flat_upper * u])
    ax.plot(dpts[:, 2], dpts[:, 1], color="#7030a0", lw=3.0)
    rdir = M.reflect(d3, nd)
    ax.annotate("", xy=(Pflat + 12 * rdir)[[2, 1]], xytext=Pflat[[2, 1]],
                arrowprops=dict(arrowstyle="-|>", color="#7030a0", lw=1.5))
    ax.text(Pflat[2] - 11.0, Pflat[1] - 2.5,
            "FOLDING FLAT\n%.1f° to axis\n%.1f\" from tertiary" % (fold_angle, tflat),
            color="#7030a0", fontsize=9, ha="left")
    # spacings
    def dim(p, q, txt, off=1.2):
        ax.annotate("", xy=(q[2], q[1]), xytext=(p[2], p[1]),
                    arrowprops=dict(arrowstyle="<|-|>", color="#888", lw=0.9))
        ax.text((p[2] + q[2]) / 2 + off, (p[1] + q[1]) / 2 + off, txt, color="#555",
                fontsize=9.5, bbox=dict(fc="white", ec="none", alpha=0.75, pad=0.5))
    dim(V1, V2, 'e1=%.1f"' % info["e1"])
    dim(V2, V3, 'e2=%.1f"' % info["e2"])
    ax.text(7.5, 2.2, 'e3=%.1f" total optical path' % info["e3"], color="#555",
            fontsize=9.5, bbox=dict(fc="white", ec="none", alpha=0.75, pad=0.5))
    # labels
    ax.text(V1[2] - 2.5, -8.5, "PRIMARY  paraboloid\nD=8\"  R1=+192\"  f/12\naxis tilt T1=%.2f°" % info["axis1"],
            ha="center", fontsize=10, color="#1f4e79")
    ax.text(V2[2] + 2.5, 12.5, "SECONDARY  convex sphere\nD=4.25\"  R2=-86.4\"\naxis tilt=%.2f°" % info["axis2"],
            ha="center", fontsize=10, color="#c00000")
    ax.text(V3[2] + 3.0, 9.5, "TERTIARY  concave sphere\nD=5.25\"  R3=+86.4\"\naxis tilt=%.2f°" % info["axis3"],
            ha="left", fontsize=10, color="#2e7d32")
    ax.set_aspect("equal"); ax.invert_xaxis()
    ax.set_xlabel("z (optical axis, inches)  [light enters from the left]")
    ax.set_ylabel("y (inches)")
    ax.set_title('Folded Stevick-Paul (FSP) — reconstructed 8" f/12 ray layout, A=0.45')
    ax.grid(True, alpha=0.25); ax.legend(loc="lower left", fontsize=9)
    ax.set_xlim(95, -55); ax.set_ylim(-13, 22)
    fig.tight_layout(); fig.savefig(f"{OUT}/fsp_layout.png", dpi=180)
    print("wrote fsp_layout.png")


def make_folded_schematic():
    """Simplified, geometrically faithful drawing of the complete folded chief ray."""
    fig, ax = plt.subplots(figsize=(12, 5.2))
    colors = ["#1f4e79", "#c00000", "#2e7d32"]
    halves = [4.0, 2.125, 2.625]
    for su, half, color in zip(s, halves, colors):
        p = surface_points(su, half)
        ax.plot(p[:, 2], p[:, 1], color=color, lw=3.0)
    ax.text(V1[2] + 2.0, -7.0, "PRIMARY", color=colors[0], fontsize=9, ha="center")
    ax.text(V2[2] + 2.0, V2[1] + 5.0, "SECONDARY", color=colors[1], fontsize=9, ha="center")
    ax.text(V3[2] - 2.0, V3[1] + 5.0, "TERTIARY", color=colors[2], fontsize=9, ha="center")
    ax.plot([95, 0], [4, 4], color="#777", lw=0.8)
    ax.plot([95, 0], [-4, -4], color="#777", lw=0.8)
    ax.annotate("", xy=(0, 0), xytext=(92, 0),
                arrowprops=dict(arrowstyle="-|>", color="#555", lw=1.4))
    ax.text(67, 1.5, "incoming light", color="#555", fontsize=9)
    path = np.array([V1, V2, V3, Pflat, Ffold])
    for p, q in zip(path[:-1], path[1:]):
        ax.annotate("", xy=(q[2], q[1]), xytext=(p[2], p[1]),
                    arrowprops=dict(arrowstyle="-|>", color="#222", lw=1.6))
    flat_ends = np.array([Pflat + flat_lower * u, Pflat + flat_upper * u])
    ax.plot(flat_ends[:, 2], flat_ends[:, 1], color="#7030a0", lw=4)
    plane_ends = np.array([Ffold - 0.5 * image_tangent, Ffold + 0.5 * image_tangent])
    ax.plot(plane_ends[:, 2], plane_ends[:, 1], color="black", lw=2.0)
    ax.plot(Ffold[2], Ffold[1], "k+", ms=11, mew=2)
    ax.text(Pflat[2] - 9, Pflat[1] - 3.0, "FOLDING FLAT", color="#7030a0", fontsize=9)
    ax.text(Ffold[2] - 14, Ffold[1] + 1.2, "folded focus", fontsize=9)
    ax.set_aspect("equal")
    ax.invert_xaxis()
    ax.set_xlim(95, -45)
    ax.set_ylim(-12, 20)
    ax.set_xlabel("z (inches; incoming light from left)")
    ax.set_ylabel("y (inches)")
    ax.grid(True, alpha=0.2)
    ax.set_title("Folded Stevick-Paul — primary → secondary → tertiary → flat → focus")
    fig.tight_layout(); fig.savefig(f"{OUT}/fsp_folded.png", dpi=180)
    print("wrote fsp_folded.png")


def make_svg():
    fig, ax = plt.subplots(figsize=(15, 5.6))
    for su, h, c in [(s[0], 4.0, "navy"), (s[1], 2.125, "red"), (s[2], 2.625, "green")]:
        p = surface_points(su, h)
        ax.plot(p[:, 2], p[:, 1], color=c, lw=3)
    pr = np.array([V1, V2, V3, Pflat, Ffold]); ax.plot(pr[:, 2], pr[:, 1], "k--")
    ax.plot([95, 0], [4, 4], "gray"); ax.plot([95, 0], [-4, -4], "gray")
    dpts = np.array([Pflat + flat_lower * u, Pflat + flat_upper * u])
    ax.plot(dpts[:, 2], dpts[:, 1], color="purple", lw=3)
    plane_ends = np.array([Ffold - 0.5 * image_tangent, Ffold + 0.5 * image_tangent])
    ax.plot(plane_ends[:, 2], plane_ends[:, 1], "k")
    ax.set_aspect("equal"); ax.invert_xaxis(); ax.grid(True, alpha=0.25)
    svg_path = Path(f"{OUT}/fsp_layout.svg")
    fig.savefig(svg_path)
    plt.close(fig)
    svg_path.write_text("\n".join(line.rstrip() for line in svg_path.read_text().splitlines()) + "\n")
    print("wrote fsp_layout.svg")


def make_dxf():
    ents = []
    def line(p, q, layer):
        ents.append(f"0\nLINE\n8\n{layer}\n10\n{p[2]:.4f}\n20\n{p[1]:.4f}\n30\n0\n11\n{q[2]:.4f}\n21\n{q[1]:.4f}\n31\n0")
    for su, h in [(s[0], 4.0), (s[1], 2.125), (s[2], 2.625)]:
        p = surface_points(su, h)
        for i in range(len(p) - 1):
            line(p[i], p[i + 1], "MIRRORS")
    pr = [V1, V2, V3, Pflat, Ffold]
    for i in range(len(pr) - 1):
        line(pr[i], pr[i + 1], "PRINCIPAL_RAY")
    plane_ends = np.array([Ffold - 0.5 * image_tangent, Ffold + 0.5 * image_tangent])
    line(plane_ends[0], plane_ends[1], "FOCAL_PLANE")
    dpts = np.array([Pflat + flat_lower * u, Pflat + flat_upper * u])
    line(dpts[0], dpts[1], "FOLDING_FLAT")
    with open(f"{OUT}/fsp_layout.dxf", "w") as f:
        f.write("0\nSECTION\n2\nENTITIES\n" + "\n".join(ents) + "\n0\nENDSEC\n0\nEOF\n")
    print("wrote fsp_layout.dxf")


if __name__ == "__main__":
    make_layout()
    make_folded_schematic()
    make_svg()
    make_dxf()
    print("done")
