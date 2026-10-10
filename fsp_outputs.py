"""
Folded Stevick-Paul (FSP) -- figures.

Novack's arrangement (fspdiagm.gif, and his note that a baffle "runs parallel to
the beam between the secondary and the flat"):

    primary -> secondary -> FOLDING FLAT -> tertiary -> focus

The flat sits in the *collimated* secondary->tertiary beam and throws it back
across the tube to a tertiary below the incoming beam; the tertiary sends the
converging cone up past the flat's edge to a focus just behind the primary.

`sp_model.build_fsp()` reproduces Novack's 6" f/10 drawing to 0.01" from
Stevick's equations with T1 = 4.385 deg.  This script draws that reproduction,
plus an 8" f/12 scaled from it (same C = N*T1, same flat position fraction and
fold angle), and checks the 8" by raytrace for clearance.

Writes fsp_layout.{png,svg,dxf} (8" f/12) and fsp_folded.png (Novack's 6" f/10).
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sp_model as M

OUT = "/home/markv/stevick-paul"
FIELD = 0.75          # design field diameter, inches (Novack's mirror sizes imply ~0.6-0.75")

nov, NI = M.build_fsp(N=10, D=6, A=27.2 / 60)          # Novack 6" f/10 as drawn
s, I = M.build_fsp(N=12, D=8, A=0.45)                   # 8" f/12 scaled from it
A, D = I["A"], I["D"]
# mirror diameters (DESIGN.md eqns 1-2); flat = 4" like Novack's
DIAM = [D, A * D + (1 - A) * FIELD, 4.0, A * D + (3 - A) * FIELD]
DIAM = [D, np.ceil(DIAM[1] * 4) / 4, 4.0, np.ceil(DIAM[3] * 4) / 4]
COLS = ["#1f4e79", "#c00000", "#7030a0", "#2e7d32"]
NAMES = ["PRIMARY", "SECONDARY", "FOLDING FLAT", "TERTIARY"]


def X(p):
    """drawing coordinates: light enters from the left (+z to the left), y up."""
    return -p[2], p[1]


def surface_points(su, half, n=100):
    radial = np.cross(su.n, [1.0, 0, 0]); radial /= np.linalg.norm(radial)
    pts = []
    for r in np.linspace(-half, half, n):
        if su.flat:
            pts.append(su.v + r * radial); continue
        disc = su.R**2 - (1 + su.k) * r**2
        ss = (su.R - np.sqrt(disc)) / (1 + su.k) if su.k != -1 else r**2 / (2 * su.R)
        pts.append(su.v + ss * su.n + r * radial)
    return np.array(pts)


def trace_full(surfs, info, x, y, field_deg=0.0):
    a = np.radians(field_deg)
    d = M.unit(np.array([0.0, np.sin(a), -np.cos(a)]))
    pts = [np.array([x, y, 0.0]) - 150 * d]
    for su in surfs:
        r = su.intersect(pts[-1], d)
        if r is None:
            return None
        pts.append(r[1]); d = M.reflect(d, r[2])
    pts.append(pts[-1] + info["e3"] * d)
    return np.array(pts), d


def spot_rms(surfs, info, field_deg=0.0):
    """RMS (inches) on a plane normal to the chief ray, best focus along it."""
    P, Dv = [], []
    for x, y in M.pupil_rays(info["D"], 20):
        r = trace_full(surfs, info, x, y, field_deg)
        P.append(r[0][-2]); Dv.append(r[1])
    P, Dv = np.array(P), np.array(Dv)
    c = Dv.mean(0); c /= np.linalg.norm(c)
    e = np.cross(c, [1.0, 0, 0]); e /= np.linalg.norm(e)
    best = (1e9, 0)
    for t0 in np.linspace(info["e3"] - 2, info["e3"] + 2, 801):
        O = info["V3"] + t0 * c
        t = ((O - P) @ c) / (Dv @ c); h = P + t[:, None] * Dv
        q = np.c_[(h - O)[:, 0], (h - O) @ e]
        best = min(best, (np.sqrt(((q - q.mean(0)) ** 2).sum(1).mean()), t0))
    return best


def verify(surfs, info, diam):
    """Every sampled pupil ray must land inside each mirror in turn, and no beam
    segment may pass through any other mirror's disc.  Returns the smallest
    clearance (inches, in each mirror's plane) between a mirror's edge and a
    foreign beam."""
    rays = [trace_full(surfs, info, x, y) for x, y in M.pupil_rays(info["D"], 24)]
    worst = {}
    for j, su in enumerate(surfs):
        half = diam[j] / 2
        for pts, _ in rays:
            off = pts[j + 1] - su.v; off -= (off @ su.n) * su.n
            # the tilted primary is the stop: the input cylinder's projection onto it
            # overhangs the rim by ~0.01"; ignore that
            slack = 0.02 if j == 0 else 1e-6
            if np.linalg.norm(off) > half + slack:
                raise RuntimeError(f"{NAMES[j]} too small: ray lands {np.linalg.norm(off):.3f}\" out")
            for k in range(len(pts) - 1):
                if k in (j, j + 1):
                    continue
                a, b = pts[k], pts[k + 1]
                den = (b - a) @ su.n
                if abs(den) < 1e-12:
                    continue
                t = ((su.v - a) @ su.n) / den
                if 0 < t < 1:
                    off = a + t * (b - a) - su.v
                    gap = np.linalg.norm(off - (off @ su.n) * su.n) - half
                    if gap <= 0:
                        raise RuntimeError(f"{NAMES[j]} obstructs beam segment {k}")
                    worst[NAMES[j]] = min(worst.get(NAMES[j], 1e9), gap)
    return len(rays), worst


nrays, gaps = verify(s, I, DIAM)
rms0, _ = spot_rms(s, I)
print(f"8\" f/12: {nrays} pupil rays, all captured, no obstruction; edge clearances:",
      ", ".join(f"{k} {v:.2f}\"" for k, v in gaps.items()))
print(f"8\" f/12 on-axis RMS {rms0 * 25400:.2f} um (Airy {1.22 * 0.55 * 12:.2f} um)")
nrms, _ = spot_rms(nov, NI)
print(f"Novack 6\" f/10 reproduction on-axis RMS {nrms * 25400:.2f} um (Airy {1.22 * 0.55 * 10:.2f} um)")
for k in ["V1", "V2", "VF", "V3", "Fp"]:
    print(f"  8in {k}: drawing (x, y) = ({X(I[k])[0]:7.2f}, {X(I[k])[1]:6.2f})")


def chief_path(info):
    return np.array([info[k] for k in ["V1", "V2", "VF", "V3", "Fp"]])


def angle_between(u, v):
    return np.degrees(np.arccos(np.clip(u @ v, -1, 1)))


def draw(ax, surfs, info, diam, rays=True, dims=True, fs=9.5):
    for su, dm, c in zip(surfs, diam, COLS):
        p = np.array([X(q) for q in surface_points(su, dm / 2)])
        ax.plot(p[:, 0], p[:, 1], color=c, lw=4, solid_capstyle="butt")
    R = info["D"] / 2
    xin = -info["V2"][2] - 12
    ax.plot([xin, 0], [R, R], color="#777", lw=0.8)
    ax.plot([xin, 0], [-R, -R], color="#777", lw=0.8)
    ax.plot([xin + 4, xin + 4], [-R - 1, R + 1], color="#444", lw=1.2, ls=(0, (6, 3)))
    ax.text(xin + 4, -R - 2.2, "aperture", ha="center", fontsize=fs)
    if rays:
        for y in (-R, R):
            r = trace_full(surfs, info, 0.0, y)
            p = np.array([X(q) for q in r[0][1:]])
            ax.plot(p[:, 0], p[:, 1], color="#ff7f0e", lw=0.7, alpha=0.8)
    cp = chief_path(info)
    pts = np.array([X(q) for q in cp])
    ax.annotate("", xy=(0, 0), xytext=(xin, 0),
                arrowprops=dict(arrowstyle="-|>", color="k", lw=1.2))
    for p, q in zip(pts[:-1], pts[1:]):
        ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="-|>", color="k", lw=1.1))
    # focal plane, tilted ~4*T3 to the chief ray (nominal), drawn short
    d4 = info["d4"]; tilt = np.radians(4 * info["T3"])
    nrm = np.array([0.0, -d4[2], d4[1]])
    tan = np.cos(tilt) * nrm + np.sin(tilt) * d4
    fp = np.array([X(info["Fp"] + h * tan) for h in (-0.6, 0.6)])
    ax.plot(fp[:, 0], fp[:, 1], color="k", lw=2.5)
    if dims:
        legs = [("e1", cp[0], cp[1]), ("", cp[1], cp[2]), ("", cp[2], cp[3]), ("e3", cp[3], cp[4])]
        for lab, p, q in legs:
            m = (np.array(X(p)) + np.array(X(q))) / 2
            ax.text(m[0], m[1] + 0.4, f'{np.linalg.norm(q - p):.1f}"', ha="center",
                    fontsize=fs, bbox=dict(fc="white", ec="none", alpha=0.8, pad=0.4))
        # angle between the arriving and leaving legs at each mirror, as Novack labels them
        dirs = [info["din"], info["d1"], info["d2"], info["d3"], info["d4"]]
        for j, p in enumerate(cp[:4]):
            a = 180 - angle_between(dirs[j], dirs[j + 1])
            ox = {0: (-3.5, -1.5), 1: (5, -1.0), 2: (-6, -1.2), 3: (2.5, -0.6)}[j]
            xy = np.array(X(p))
            ax.text(xy[0] + ox[0] * info["D"] / 8, xy[1] + ox[1] * info["D"] / 8,
                    f"{a:.2f}°", fontsize=fs, color="#333")


def labels(ax, info, diam, fs=10):
    sp = info["R2"] / 2
    txt = [f'Primary paraboloid\n{diam[0]:.0f}" dia., {info["F1"]:.0f}" FL',
           f'Secondary convex sphere\n{diam[1]:.2f}" dia., {sp:.1f}" FL',
           f'Folding flat\n{diam[2]:.0f}" dia.',
           f'Tertiary concave sphere\n{diam[3]:.2f}" dia., {sp:.1f}" FL']
    off = [(2.6, -3.3), (0, 2.6), (0, 2.6), (0, -3.0)]
    for k, t, c, (ox, oy) in zip(["V1", "V2", "VF", "V3"], txt, COLS, off):
        x, y = X(info[k])
        ax.text(x + ox * info["D"] / 6, y + oy * info["D"] / 6, t, color=c, fontsize=fs,
                ha="center", va="center")
    x, y = X(info["Fp"])
    ax.text(x + 1.0, y, "focus", fontsize=fs, va="center")


def make_layout():
    fig, ax = plt.subplots(figsize=(14, 7.2))
    draw(ax, s, I, DIAM)
    labels(ax, I, DIAM)
    ax.set_aspect("equal"); ax.grid(True, alpha=0.25)
    ax.set_xlim(-70, 14); ax.set_ylim(-17, 20)
    ax.set_xlabel("inches (primary vertex at origin; light enters from the left)")
    ax.set_ylabel("inches")
    ax.set_title(f'Folded Stevick-Paul, 8" f/12, A = {A:.2f} — scaled from Novack\'s 6" f/10\n'
                 "primary → secondary → folding flat → tertiary → focus  "
                 "(chief ray black, marginal rays orange)")
    fig.tight_layout(); fig.savefig(f"{OUT}/fsp_layout.png", dpi=160)
    plt.close(fig); print("wrote fsp_layout.png")


def make_novack():
    nd = [6.0, 3.12, 4.0, 4.25]
    fig, ax = plt.subplots(figsize=(12, 6.6))
    draw(ax, nov, NI, nd, fs=10)
    labels(ax, NI, nd)
    ax.set_aspect("equal"); ax.grid(True, alpha=0.25)
    ax.set_xlim(-46, 10); ax.set_ylim(-12, 14)
    ax.set_xlabel("inches (primary vertex at origin)")
    ax.set_title('Novack\'s 6" f/10 FSP, regenerated from Stevick\'s equations (T1 = 4.385°, A = 27.2/60)\n'
                 'matches his drawing: legs 32.8 / 31.7 / 22.7 / 27.2", angles 8.77° / 14.04° / 29.36° / 5.29°')
    fig.tight_layout(); fig.savefig(f"{OUT}/fsp_folded.png", dpi=160)
    plt.close(fig); print("wrote fsp_folded.png")


def make_svg():
    fig, ax = plt.subplots(figsize=(14, 7.2))
    draw(ax, s, I, DIAM, rays=True, dims=False)
    ax.set_aspect("equal"); ax.set_xlim(-70, 14); ax.set_ylim(-17, 20); ax.grid(True, alpha=0.25)
    svg = Path(f"{OUT}/fsp_layout.svg"); fig.savefig(svg); plt.close(fig)
    svg.write_text("\n".join(l.rstrip() for l in svg.read_text().splitlines()) + "\n")
    print("wrote fsp_layout.svg")


def make_dxf():
    ents = []
    def line(p, q, layer):
        (x0, y0), (x1, y1) = X(p), X(q)
        ents.append(f"0\nLINE\n8\n{layer}\n10\n{x0:.4f}\n20\n{y0:.4f}\n30\n0\n"
                    f"11\n{x1:.4f}\n21\n{y1:.4f}\n31\n0")
    for su, dm, nm in zip(s, DIAM, ["PRIMARY", "SECONDARY", "FOLDING_FLAT", "TERTIARY"]):
        p = surface_points(su, dm / 2)
        for a, b in zip(p[:-1], p[1:]):
            line(a, b, nm)
    cp = chief_path(I)
    for a, b in zip(cp[:-1], cp[1:]):
        line(a, b, "PRINCIPAL_RAY")
    with open(f"{OUT}/fsp_layout.dxf", "w") as f:
        f.write("0\nSECTION\n2\nENTITIES\n" + "\n".join(ents) + "\n0\nENDSEC\n0\nEOF\n")
    print("wrote fsp_layout.dxf")


if __name__ == "__main__":
    make_layout()
    make_novack()
    make_svg()
    make_dxf()
