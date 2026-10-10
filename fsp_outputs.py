"""
Folded Stevick-Paul (FSP) -- figures.

FSP = the same 3-mirror Paul core (paraboloid primary + two mating spheres) with a
*flat folding mirror* in the converging beam that folds the path and extracts the
focus, compacting the tube.  Radius ratio A = 0.45 (Novack), vs 0.40 for the
standard SP; the higher A slightly reduces the focal-plane tilt.

Uses sp_model for the raytracer.  Writes fsp_layout.{png,svg,dxf} and
fsp_folded.png into /home/markv/stevick-paul.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sp_model as M

OUT = "/home/markv/stevick-paul"

# ---- FSP core: 8" f/12, A = 0.45 (th3 = -4*T3 = the null found by raytrace) ----
A = 0.45
s, info = M.build_sp(N=12.0, D=8.0, A=A, C=35.67, tilt3_deg=-7.25)
V1, V2, V3, Fp = info["V1"], info["V2"], info["V3"], info["Fp"]
d1, d2, d3, din = info["d1"], info["d2"], info["d3"], info["din"]


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


# fold the beam to +y (roughly 90 deg to the collimated sec-tert beam)
out = np.array([0.0, 0.997, 0.0777]); out /= np.linalg.norm(out)
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
print(f"flat surface angle from axis = {fold_angle:.2f} deg")


def make_layout():
    fig, ax = plt.subplots(figsize=(15, 5.6))
    cols = ["#1f4e79", "#c00000", "#2e7d32"]
    labs = ["Primary (paraboloid)", "Secondary (convex sphere)", "Tertiary (concave sphere)"]
    for su, h, c, lb in [(s[0], 4.0, cols[0], labs[0]),
                         (s[1], 2.125, cols[1], labs[1]),
                         (s[2], 2.5, cols[2], labs[2])]:
        p = surface_points(su, h)
        ax.plot(p[:, 2], p[:, 1], color=c, lw=4, solid_capstyle="round",
                label=f"{lb}  R={su.R:+.1f}\"")
    pr = np.array([V1, V2, V3, Fp])
    ax.plot(pr[:, 2], pr[:, 1], "k--", lw=1.0, alpha=0.8, label="principal ray")
    # input
    ax.plot([95, 0], [4, 4], color="#555", lw=0.8)
    ax.plot([95, 0], [-4, -4], color="#555", lw=0.8)
    ax.annotate("", xy=(18, 0), xytext=(92, 0),
                arrowprops=dict(arrowstyle="-|>", color="#555", lw=1.4))
    ax.text(60, 6.2, '8" collimated input', color="#333", fontsize=10)
    # marginal bundle
    for x, y in [(-4, 0), (0, -4), (0, 4), (4, 0)]:
        r = M.trace(s, np.array([x, y, 95.0]), din)
        if not r:
            continue
        pts = r[0]
        ax.plot(pts[:, 2], pts[:, 1], color="#ff7f0e", lw=0.7, alpha=0.7)
        P, dd = pts[-1], r[1]
        tt = -((P - Pflat) @ nd) / (dd @ nd)
        if tt > 0:
            X = P + tt * dd
            ax.plot([P[2], X[2]], [P[1], X[1]], color="#ff7f0e", lw=0.7, alpha=0.7)
    # focal plane (perpendicular to input) at the folded focus
    Final = Pflat + ((-(Pflat - Fp) @ nd) / (d3 @ nd)) * d3
    Foc = Pflat + False if False else Fp
    # focus after fold: the cone focuses identically; mark the design focus location
    ax.plot([Fp[2], Fp[2]], [Fp[1] - 1.6, Fp[1] + 1.6], color="k", lw=2.5)
    ax.plot(Fp[2], Fp[1], "k+", ms=12, mew=2)
    ax.text(Fp[2] - 1.0, Fp[1] + 2.6, "focal plane\n(tilt %.2f°)" % abs(info["th3"]),
            fontsize=9.5, ha="right")
    # folding flat
    dpts = np.array([Pflat - Lmax * u, Pflat + Lmax * u])
    ax.plot(dpts[:, 2], dpts[:, 1], color="#7030a0", lw=3.0)
    rdir = M.reflect(d3, nd)
    ax.annotate("", xy=(Pflat + 12 * rdir)[[2, 1]], xytext=Pflat[[2, 1]],
                arrowprops=dict(arrowstyle="-|>", color="#7030a0", lw=1.5))
    ax.text(Pflat[2] + 1.5, Pflat[1] - 2.2,
            "FOLDING FLAT\n%.1f° to axis" % fold_angle,
            color="#7030a0", fontsize=9, ha="left")
    # spacings
    def dim(p, q, txt, off=1.2):
        ax.annotate("", xy=(q[2], q[1]), xytext=(p[2], p[1]),
                    arrowprops=dict(arrowstyle="<|-|>", color="#888", lw=0.9))
        ax.text((p[2] + q[2]) / 2 + off, (p[1] + q[1]) / 2 + off, txt, color="#555",
                fontsize=9.5, bbox=dict(fc="white", ec="none", alpha=0.75, pad=0.5))
    dim(V1, V2, 'e1=%.1f"' % info["e1"])
    dim(V2, V3, 'e2=%.1f"' % info["e2"])
    dim(V3, Fp, 'e3=%.1f"' % info["e3"])
    # labels
    ax.text(V1[2] - 2.5, -8.5, "PRIMARY  paraboloid\nD=8\"  R1=+192\"  f/12\naxis tilt T1=%.2f°" % info["axis1"],
            ha="center", fontsize=10, color="#1f4e79")
    ax.text(V2[2] + 2.5, 12.5, "SECONDARY  convex sphere\nD=%.2f\"  R2=-86.4\"\naxis tilt=%.2f°" % (3.05, info["axis2"]),
            ha="center", fontsize=10, color="#c00000")
    ax.text(V3[2] + 3.0, 9.5, "TERTIARY  concave sphere\nD=5.0\"  R3=+86.4\"\naxis tilt=%.2f°" % info["axis3"],
            ha="left", fontsize=10, color="#2e7d32")
    ax.set_aspect("equal"); ax.invert_xaxis()
    ax.set_xlabel("z (optical axis, inches)  [light enters from the left]")
    ax.set_ylabel("y (inches)")
    ax.set_title('Folded Stevick-Paul (FSP) — 8" f/12, A=0.45, exact raytrace layout')
    ax.grid(True, alpha=0.25); ax.legend(loc="lower left", fontsize=9)
    ax.set_xlim(95, -55); ax.set_ylim(-13, 16)
    fig.tight_layout(); fig.savefig(f"{OUT}/fsp_layout.png", dpi=180)
    print("wrote fsp_layout.png")


def make_folded_schematic():
    """Simple box diagram showing the folded light path (side view)."""
    fig, ax = plt.subplots(figsize=(12, 4.6))
    # schematic tube outline (not to scale) showing the 4 bounce path + fold
    ax.plot([0, 0, 40, 40, 0], [0, 9, 9, 0, 0], color="#999", lw=1.5)
    # incoming
    ax.annotate("", xy=(8, 1.4), xytext=(0.4, 1.4), arrowprops=dict(arrowstyle="-|>", lw=1.5))
    ax.text(0.6, 1.9, "in", fontsize=10)
    # primary at right end (concave)
    ax.plot([38.6, 38.6], [0.5, 3], color="#1f4e79", lw=5)
    ax.text(38.8, 3.2, "1° primary", fontsize=9, color="#1f4e79")
    # to secondary at left top (convex)
    ax.annotate("", xy=(4, 7.6), xytext=(38.6, 2), arrowprops=dict(arrowstyle="-|>", lw=1.2))
    ax.plot([3.4, 3.4], [6.2, 8.4], color="#c00000", lw=4)
    ax.text(0.4, 8.6, "2° secondary", fontsize=9, color="#c00000")
    # to tertiary near bottom middle
    ax.annotate("", xy=(19, 1.4), xytext=(3.4, 6.6), arrowprops=dict(arrowstyle="-|>", lw=1.2))
    ax.plot([18.4, 19.6], [0.6, 2.6], color="#2e7d32", lw=4)
    ax.text(15.5, 0.15, "3° tertiary", fontsize=9, color="#2e7d32")
    # to folding flat upper right
    ax.annotate("", xy=(33, 8.2), xytext=(19, 2), arrowprops=dict(arrowstyle="-|>", lw=1.2))
    ax.plot([32.2, 33.8], [7.2, 9.0], color="#7030a0", lw=4)
    ax.text(31, 9.3, "4° folding flat", fontsize=9, color="#7030a0")
    # fold out to focus
    ax.annotate("", xy=(40, 5.2), xytext=(33, 8.4), arrowprops=dict(arrowstyle="-|>", lw=1.2, color="#7030a0"))
    ax.plot(40, 5.2, "k+", ms=12, mew=2); ax.text(40.3, 5.0, "focus\n(side)", fontsize=9)
    ax.set_xlim(-1, 46); ax.set_ylim(-1, 10); ax.axis("off")
    ax.set_title("Folded SP — schematic light path (not to scale): 4 mirrors, focus folded to the side")
    fig.tight_layout(); fig.savefig(f"{OUT}/fsp_folded.png", dpi=180)
    print("wrote fsp_folded.png")


def make_svg():
    fig, ax = plt.subplots(figsize=(15, 5.6))
    for su, h, c in [(s[0], 4.0, "navy"), (s[1], 2.125, "red"), (s[2], 2.5, "green")]:
        p = surface_points(su, h)
        ax.plot(p[:, 2], p[:, 1], color=c, lw=3)
    pr = np.array([V1, V2, V3, Fp]); ax.plot(pr[:, 2], pr[:, 1], "k--")
    ax.plot([95, 0], [4, 4], "gray"); ax.plot([95, 0], [-4, -4], "gray")
    dpts = np.array([Pflat - Lmax * u, Pflat + Lmax * u])
    ax.plot(dpts[:, 2], dpts[:, 1], color="purple", lw=3)
    ax.plot([Fp[2], Fp[2]], [Fp[1] - 1.6, Fp[1] + 1.6], "k")
    ax.set_aspect("equal"); ax.invert_xaxis(); ax.grid(True, alpha=0.25)
    fig.savefig(f"{OUT}/fsp_layout.svg"); plt.close(fig); print("wrote fsp_layout.svg")


def make_dxf():
    ents = []
    def line(p, q, layer):
        ents.append(f"0\nLINE\n8\n{layer}\n10\n{p[2]:.4f}\n20\n{p[1]:.4f}\n30\n0\n11\n{q[2]:.4f}\n21\n{q[1]:.4f}\n31\n0")
    for su, h in [(s[0], 4.0), (s[1], 2.125), (s[2], 2.5)]:
        p = surface_points(su, h)
        for i in range(len(p) - 1):
            line(p[i], p[i + 1], "MIRRORS")
    pr = [V1, V2, V3, Fp]
    for i in range(len(pr) - 1):
        line(pr[i], pr[i + 1], "PRINCIPAL_RAY")
    line([Fp[2], Fp[1] - 1.6, 0], [Fp[2], Fp[1] + 1.6, 0], "FOCAL_PLANE")
    dpts = np.array([Pflat - Lmax * u, Pflat + Lmax * u])
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
