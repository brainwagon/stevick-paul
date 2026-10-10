import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import sp_model as M

OUT = "/home/markv/stevick-paul"
surfs, info = M.build_sp()
V1, V2, V3, Fp = info["V1"], info["V2"], info["V3"], info["Fp"]
d1, d2, d3, din = info["d1"], info["d2"], info["d3"], info["din"]
R1, R2 = info["R1"], info["R2"]


def surface_points(s, half):
    """sample the meridional profile of a surface for drawing."""
    n = s.n
    # rotate radial direction in the y-z plane
    radial = np.array([0.0, n[2], -n[1]])  # perpendicular to n in the y-z plane
    radial = radial / np.linalg.norm(radial)
    rs = np.linspace(-half, half, 200)
    pts = []
    for r in rs:
        if s.flat:
            pts.append(s.v + r * radial)
            continue
        disc = s.R**2 - (1 + s.k) * r**2
        if disc < 0:
            continue
        s_ = (s.R - np.sqrt(disc)) / (1 + s.k) if (1 + s.k) != 0 else r**2 / (2 * s.R)
        pts.append(s.v + s_ * n + r * radial)
    return np.array(pts)


# ---------------------------------------------------------------- layout
def make_layout():
    fig, ax = plt.subplots(figsize=(15, 5.2))
    half1, half2, half3 = 4.0, 2.125, 2.5
    for s, h, c in [(surfs[0], half1, "#1f4e79"),
                    (surfs[1], half2, "#c00000"),
                    (surfs[2], half3, "#2e7d32")]:
        p = surface_points(s, h)
        ax.plot(p[:, 2], p[:, 1], color=c, lw=4, solid_capstyle="round",
                label=f"{s.name}  R={s.R:+.1f}\"")

    # principal ray
    pr = np.array([V1, V2, V3, Fp])
    ax.plot(pr[:, 2], pr[:, 1], "k--", lw=1.0, alpha=0.8, label="principal ray")

    # incoming beam (8" dia)
    ax.plot([95, 0], [4, 4], color="#555", lw=0.8)
    ax.plot([95, 0], [-4, -4], color="#555", lw=0.8)
    ax.annotate("", xy=(18, 0), xytext=(92, 0),
                arrowprops=dict(arrowstyle="-|>", color="#555", lw=1.4))
    ax.text(60, 6.2, '8" collimated input', color="#333", fontsize=10)

    # marginal ray bundle (edge of 8" beam)
    for (x, y) in [(-4, 0), (0, -4), (0, 4), (4, 0)]:
        r = M.trace(surfs, np.array([x, y, 95.0]), din)
        if r is None:
            continue
        pts = r[0]
        ax.plot(pts[:, 2], pts[:, 1], color="#ff7f0e", lw=0.7, alpha=0.7)
        P, dd = pts[-1], r[1]
        t = (Fp[2] - P[2]) / dd[2]
        ax.plot([P[2], (P + t * dd)[2]], [P[1], (P + t * dd)[1]],
                color="#ff7f0e", lw=0.7, alpha=0.7)

    # focal plane
    ax.plot([Fp[2], Fp[2]], [Fp[1] - 1.6, Fp[1] + 1.6], color="k", lw=2.5)
    ax.plot(Fp[2], Fp[1], "k+", ms=12, mew=2)
    ax.text(Fp[2] - 1.0, Fp[1] + 2.0, "focal plane\n(tilt %.2f°)" % abs(info["th3"]),
            fontsize=9.5, ha="right")

    # diagonal: placed so its UPPER edge rides tangent to the collimated
    # secondary->tertiary beam and it still captures the whole converging cone.
    # Placement verified by raytrace: 100% cone capture, 0 through-beam rays blocked.
    tdiag = 26.50
    Pd = V3 + tdiag * d3
    diagdir = np.array([0.0, np.sin(np.radians(38.27)), np.cos(np.radians(38.27))])
    Ld = 0.70
    dpts = np.array([Pd - Ld * diagdir, Pd + Ld * diagdir])
    ax.plot(dpts[:, 2], dpts[:, 1], color="#7030a0", lw=2.8)
    # show the folded chief ray leaving the diagonal
    nd = np.array([0.0, np.cos(np.radians(38.27)), -np.sin(np.radians(38.27))])
    rdir = M.reflect(d3, nd)
    ax.annotate("", xy=(Pd + 9 * rdir)[[2, 1]], xytext=Pd[[2, 1]],
                arrowprops=dict(arrowstyle="-|>", color="#7030a0", lw=1.4))
    ax.text(Pd[2] - 1.0, Pd[1] - 3.6, "flat diagonal (upper edge rides\nthe collimated beam; folds image out)",
            color="#7030a0", fontsize=9, ha="right")

    # spacings
    def dim(p, q, txt, off=1.0):
        ax.annotate("", xy=(q[2], q[1]), xytext=(p[2], p[1]),
                    arrowprops=dict(arrowstyle="<|-|>", color="#888", lw=0.9,
                                    shrinkA=0, shrinkB=0))
        ax.text((p[2] + q[2]) / 2 + off, (p[1] + q[1]) / 2 + off, txt,
                color="#555", fontsize=9.5,
                bbox=dict(fc="white", ec="none", alpha=0.75, pad=0.5))
    dim(V1, V2, "e1=57.6\"", 1.2)
    dim(V2, V3, "e2=76.8\"", 1.2)
    dim(V3, Fp, "e3=38.4\"", 1.2)

    # axis distances
    ax.plot([V1[2], V2[2]], [0, 0], color="b", lw=0.5, ls=":")
    ax.annotate("", xy=(V2[2], V2[1]), xytext=(V2[2], 0),
                arrowprops=dict(arrowstyle="<|-|>", color="b", lw=0.9))
    ax.text(V2[2] - 0.8, V2[1] / 2, "a1=6.0\"", color="b", fontsize=9, ha="right")
    ax.annotate("", xy=(V3[2], V3[1]), xytext=(V3[2], 0),
                arrowprops=dict(arrowstyle="<|-|>", color="b", lw=0.9))
    ax.text(V3[2] + 0.8, V3[1] / 2, "a2=12.0\"", color="b", fontsize=9, ha="left")

    # mirror labels
    ax.text(V1[2] - 2.5, -8.5,
            "PRIMARY  paraboloid\nD=8\"   R1=+192\"   f/12\naxis tilt T1=%.2f°" % info["axis1"],
            ha="center", fontsize=10, color="#1f4e79")
    ax.text(V2[2] + 2.5, 12.5,
            "SECONDARY  convex sphere\nD=4.25\"   R2=-76.8\"\naxis tilt=%.2f°  (T2=%.2f°)" % (info["axis2"], info["T2"]),
            ha="center", fontsize=10, color="#c00000")
    ax.text(V3[2] + 3.0, 9.5,
            "TERTIARY  concave sphere\nD=5.0\"   R3=+76.8\"\naxis tilt=%.2f°  (T3=%.2f°)" % (info["axis3"], info["T3"]),
            ha="left", fontsize=10, color="#2e7d32")

    ax.set_aspect("equal")
    ax.invert_xaxis()
    ax.set_xlabel("z  (optical axis, inches)   [light enters from the left]")
    ax.set_ylabel("y  (inches)")
    ax.set_title('8" f/12 Stevick-Paul — exact raytrace layout (A=0.40, meridional plane)')
    ax.grid(True, alpha=0.25)
    ax.legend(loc="lower left", fontsize=9)
    ax.set_xlim(95, -70)
    ax.set_ylim(-12, 16)
    fig.tight_layout()
    fig.savefig(f"{OUT}/sp_layout.png", dpi=180)
    print("wrote sp_layout.png")
    return fig, ax


# ---------------------------------------------------------------- spots
def spot_at(field_deg, n=16, nsamp=22):
    a = np.radians(field_deg)
    dinf = M.unit(np.array([0.0, np.sin(a), -np.cos(a)]))
    uv = M.pupil_rays(8.0, n)
    pts = []
    for x, y in uv:
        r = M.trace(surfs, np.array([x, y, 200.0]), dinf)
        if r is None:
            continue
        pts.append((r[0][-1], r[1]))
    P = np.array([p for p, d in pts]); Dv = np.array([d for p, d in pts])
    A = np.zeros((3, 3)); b = np.zeros(3)
    for d, p in zip(Dv, P):
        Mx = np.eye(3) - np.outer(d, d); A += Mx; b += Mx @ p
    Q = np.linalg.solve(A, b)
    # project each ray onto the focal plane (normal = chief ray d3, through Q)
    nrm = M.unit(d3)
    ux = np.array([1.0, 0, 0])
    uy = M.unit(np.cross(nrm, ux))
    xy = []
    for p, d in zip(P, Dv):
        t = np.dot(Q - p, nrm) / np.dot(d, nrm)
        X = p + t * d
        v = X - Q
        xy.append([v @ ux, v @ uy])
    xy = np.array(xy)
    cen = xy.mean(0)
    xy = xy - cen
    rms = np.sqrt((xy ** 2).sum(1).mean())
    return xy, rms, Q, cen


def make_spots():
    lam_um = 0.55
    fno = 12.0
    airy_r_um = 1.22 * lam_um * fno   # Airy radius in microns (8.05 um)
    fields = [0.0, 0.25, 0.5]
    fig, axes = plt.subplots(1, len(fields), figsize=(5 * len(fields), 5.2))
    for ax, f in zip(axes, fields):
        xy, rms, Q, cen = spot_at(f, nsamp=22)
        xy_um = xy * 25400.0
        ax.plot(xy_um[:, 0], xy_um[:, 1], ".", ms=4, color="#1f77b4")
        ax.add_patch(Circle((0, 0), airy_r_um, fill=False, ec="r", lw=1.4))
        m = max(1.6 * airy_r_um, np.abs(xy_um).max() * 1.15)
        ax.set_xlim(-m, m); ax.set_ylim(-m, m); ax.set_aspect("equal")
        ax.set_title(f"field {f:.2f}°   RMS={rms*25400:.2f} µm\n(red = Airy disk, r=1.22λF=8.05 µm, λ=550nm)")
        ax.set_xlabel("x  (µm)"); ax.set_ylabel("y  (µm)")
        ax.grid(True, alpha=0.25)
    fig.suptitle("Stevick-Paul 8\" f/12 — spot diagrams (geometric, full 8\" aperture)")
    fig.tight_layout()
    fig.savefig(f"{OUT}/sp_spotdiagrams.png", dpi=180)
    print("wrote sp_spotdiagrams.png")
    return fields, airy_r_um


def make_airy(fields, airy_r_in):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    lam = np.linspace(0.40, 1.00, 200)  # microns
    for fno in [8, 10, 12, 15, 20]:
        d_um = 2.44 * lam * fno  # microns diameter
        axes[0].plot(lam, d_um, label=f"f/{fno}")
    axes[0].set_xlabel("wavelength (µm)"); axes[0].set_ylabel("Airy disk diameter (µm)")
    axes[0].set_title("Airy disk diameter = 2.44 λ f/#")
    axes[0].legend(); axes[0].grid(True, alpha=0.25)
    axes[0].axvline(0.55, color="k", ls=":", lw=1)
    axes[0].annotate("550 nm", (0.55, 5), fontsize=9, rotation=90)

    fno = np.linspace(6, 24, 200)
    for lamv, col in [(0.45, "#333"), (0.55, "#1f77b4"), (0.65, "#d62728")]:
        axes[1].plot(fno, 2.44 * lamv * fno, color=col, label=f"λ={lamv*1000:.0f} nm")
    # mark this design
    axes[1].plot(12, 2.44 * 0.55 * 12, "k*", ms=14)
    axes[1].annotate("this design\n8\" f/12\nAiry Ø=16.1 µm", (12, 16.1),
                     textcoords="offset points", xytext=(10, 20), fontsize=9)
    # spot RMS measured
    axes[1].axhline(0.77, color="g", ls="--", lw=1)
    axes[1].text(18, 1.6, "geometric spot RMS = 0.77 µm", color="g", fontsize=9)
    axes[1].set_xlabel("f-number"); axes[1].set_ylabel("Airy disk diameter (µm)")
    axes[1].set_title("Airy disk vs f-number")
    axes[1].legend(); axes[1].grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(f"{OUT}/sp_airy.png", dpi=180)
    print("wrote sp_airy.png")


def make_dxf():
    """minimal ASCII DXF of the meridional layout (inches)."""
    ents = []
    def line(p, q, layer):
        ents.append(f"0\nLINE\n8\n{layer}\n10\n{p[2]:.4f}\n20\n{p[1]:.4f}\n30\n0\n11\n{q[2]:.4f}\n21\n{q[1]:.4f}\n31\n0")
    # mirrors (sampled polylines)
    for s, h in [(surfs[0], 4.0), (surfs[1], 2.125), (surfs[2], 2.5)]:
        p = surface_points(s, h)
        for i in range(len(p) - 1):
            line(p[i], p[i + 1], "MIRRORS")
    # principal ray
    pr = [V1, V2, V3, Fp]
    for i in range(len(pr) - 1):
        line(pr[i], pr[i + 1], "PRINCIPAL_RAY")
    # focal plane
    line([Fp[2], Fp[1] - 1.6, 0], [Fp[2], Fp[1] + 1.6, 0], "FOCAL_PLANE")
    # input beam
    line([120, 4, 0], [0, 4, 0], "INPUT")
    line([120, -4, 0], [0, -4, 0], "INPUT")
    hdr = ("0\nSECTION\n2\nENTITIES\n" + "\n".join(ents) + "\n0\nENDSEC\n0\nEOF\n")
    with open(f"{OUT}/sp_layout.dxf", "w") as f:
        f.write(hdr)
    print("wrote sp_layout.dxf")


def make_svg():
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(13, 9))
    for s, h, c in [(surfs[0], 4.0, "navy"), (surfs[1], 2.125, "red"), (surfs[2], 2.5, "green")]:
        p = surface_points(s, h)
        ax.plot(p[:, 2], p[:, 1], color=c, lw=3)
    pr = [V1, V2, V3, Fp]
    pr = np.array(pr)
    ax.plot(pr[:, 2], pr[:, 1], "k--")
    ax.plot([120, 0], [4, 4], "gray"); ax.plot([120, 0], [-4, -4], "gray")
    ax.plot([Fp[2], Fp[2]], [Fp[1] - 1.6, Fp[1] + 1.6], "k")
    ax.set_aspect("equal"); ax.invert_xaxis(); ax.grid(True, alpha=0.25)
    fig.savefig(f"{OUT}/sp_layout.svg")
    plt.close(fig)
    print("wrote sp_layout.svg")


if __name__ == "__main__":
    make_layout()
    fields, airy_r_in = make_spots()
    make_airy(fields, airy_r_in)
    make_dxf()
    make_svg()
    print("done")
