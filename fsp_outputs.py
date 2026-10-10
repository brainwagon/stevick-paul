"""
Folded Stevick-Paul (FSP) -- figures and checks.

Novack's arrangement (fspdiagm.gif, and his note that a baffle "runs parallel to
the beam between the secondary and the flat"):

    primary -> secondary -> FOLDING FLAT -> tertiary -> focus

The flat sits in the *collimated* secondary->tertiary beam; the tertiary sends the
converging cone back past the flat's lower edge to a focus behind the primary.

`sp_model.build_fsp()` reproduces Novack's 6" f/10 drawing to 0.01" from
Stevick's equations with T1 = 4.385 deg.  Two 8" f/12 layouts are built:

  scaled  -- Novack's proportions (C = N*T1 = 43.85, flat 58.3% of the way from
             secondary to tertiary, 29.36 deg fold).  The tertiary->focus cone
             grazes the flat, so the flat is limited to 4" and the field edge is
             vignetted.
  clear   -- larger primary tilt (C = 52), flat at 55%, 26 deg fold: the whole
             0.75" field passes with the flat sized for it.

Mirrors are modelled as solid discs (thickness = diameter / 6); a ray is lost if it
misses a mirror it should hit or passes through any other mirror's glass.

Writes fsp_folded.png (Novack 6" f/10), fsp8_scaled.{png,svg,dxf},
fsp8_clear.{png,svg,dxf}, fsp8_spots.png and fsp8_flat_zoom.png.
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon
import sp_model as M

OUT = "/home/markv/stevick-paul"
FIELD_R = 0.375       # design field radius at the focus, inches (0.75" field, 0.45 deg)
THICK = 1 / 6         # mirror thickness / diameter
LAM_UM = 0.55
COLS = ["#1f4e79", "#c00000", "#7030a0", "#2e7d32"]
NAMES = ["primary", "secondary", "flat", "tertiary"]

LAYOUTS = {
    "scaled": dict(title="8\" f/12 scaled from Novack (C = 43.85)",
                   kw=dict(N=12, D=8, A=0.45, C=43.85),
                   diam=[8.0, 4.25, 4.0, 5.75]),
    "clear": dict(title="8\" f/12 clear-field (C = 52)",
                  kw=dict(N=12, D=8, A=0.45, C=52.0, flat_frac=0.55, fold_deg=26.0),
                  diam=[8.0, 4.25, 5.25, 5.75]),
}
for L in LAYOUTS.values():
    L["s"], L["I"] = M.build_fsp(**L["kw"])
nov, NI = M.build_fsp(N=10, D=6, A=27.2 / 60)
NOV_DIAM = [6.0, 3.12, 4.0, 4.25]
FIELDS = [(0.0, 0.0), (0.0, FIELD_R), (0.0, -FIELD_R), (FIELD_R, 0.0)]
FIELD_LABELS = ["on-axis", f"+{FIELD_R}\" meridional", f"−{FIELD_R}\" meridional",
                f"{FIELD_R}\" sagittal"]


def X(p):
    """drawing coordinates: light enters from the left (+z to the left), y up."""
    return -p[2], p[1]


# ---------------------------------------------------------------- raytracing
def field_dir(I, fx, fy):
    """incoming direction for a field point (fx, fy) inches at the focus."""
    return M.unit(np.array([fx / I["F1"], fy / I["F1"], -1.0]))


def trace_rays(s, I, fx=0.0, fy=0.0, n=16):
    """points [start, P, S, flat, T, focus] (N, 6, 3) and final directions (N, 3)."""
    din = field_dir(I, fx, fy)
    P, Dv = [], []
    for x, y in M.pupil_rays(I["D"], n):
        p = np.array([x, y, 0.0]) - 150 * din; d = din; pts = [p]
        for su in s:
            _, p, N = su.intersect(p, d)
            d = M.reflect(d, N); pts.append(p)
        pts.append(p + I["e3"] * d)
        P.append(pts); Dv.append(d)
    return np.array(P), np.array(Dv)


def _arrivals(I):
    return [I["din"], I["d1"], I["d2"], I["d3"]]


def _slab(su, I, j, P, k, t):
    """sample segment k of every ray; return depth into mirror j's glass and radius."""
    b = su.n * np.sign(_arrivals(I)[j] @ su.n)     # into the glass
    Q = P[:, k, None, :] + t[None, :, None] * (P[:, k + 1] - P[:, k])[:, None, :] - su.v
    sb = Q @ b
    return sb, np.linalg.norm(Q - sb[..., None] * b, axis=2)


def transmitted(s, I, P, diam, ns=500):
    """True for rays that land on every mirror and pass through no mirror's glass."""
    ok = np.ones(len(P), bool)
    t = np.linspace(0, 1, ns)
    for j, su in enumerate(s):
        r = diam[j] / 2
        off = P[:, j + 1] - su.v
        rho = np.linalg.norm(off - (off @ su.n)[:, None] * su.n, axis=1)
        ok &= rho <= r + (0.02 if j == 0 else 0)   # tilted primary is the stop
        for k in range(5):
            if k in (j, j + 1):
                continue
            sb, rr = _slab(su, I, j, P, k, t)
            ok &= ~(((sb >= -0.05) & (sb <= diam[j] * THICK) & (rr <= r)).any(1))
    return ok


def clearances(s, I, diam, ns=800):
    """Smallest gap (inches) between each mirror's solid disc and any foreign beam,
    over the on-axis and field-edge beams; negative = the glass is in the beam."""
    gaps = [1e9] * 4
    t = np.linspace(0, 1, ns)
    for fx, fy in FIELDS:
        P, _ = trace_rays(s, I, fx, fy, n=10)
        for j, su in enumerate(s):
            for k in range(5):
                if k in (j, j + 1):
                    continue
                sb, rr = _slab(su, I, j, P, k, t)
                m = (sb >= -0.05) & (sb <= diam[j] * THICK)
                if m.any():
                    gaps[j] = min(gaps[j], (rr[m] - diam[j] / 2).min())
    return gaps


def best_point(P, Dv):
    """least-squares point closest to all rays."""
    A_ = np.zeros((3, 3)); b = np.zeros(3)
    for p, d in zip(P, Dv):
        Mx = np.eye(3) - np.outer(d, d); A_ += Mx; b += Mx @ p
    return np.linalg.solve(A_, b)


def image_plane(s, I):
    """Plane through the best-focus points of the field (incl. the mirror image of
    the sagittal point).  Returns origin, normal, and its tilt to the on-axis chief
    ray in degrees."""
    pts = []
    for fx, fy in FIELDS + [(-FIELD_R, 0.0)]:
        P, Dv = trace_rays(s, I, fx, fy, n=14)
        pts.append(best_point(P[:, 4], Dv))
    pts = np.array(pts)
    nrm = np.linalg.svd(pts - pts.mean(0))[2][-1]
    if nrm @ I["d4"] < 0:
        nrm = -nrm
    tilt = np.degrees(np.arccos(np.clip(nrm @ I["d4"], -1, 1)))
    return pts[0], nrm, tilt


def spots(s, I, diam):
    """spot (inches, centred) of the transmitted rays on the fitted image plane."""
    O, nrm, tilt = image_plane(s, I)
    ux = np.array([1.0, 0, 0]); uy = M.unit(np.cross(nrm, ux))
    out = []
    for fx, fy in FIELDS:
        P, Dv = trace_rays(s, I, fx, fy, n=22)
        ok = transmitted(s, I, P, diam)
        T = P[:, 4]
        t = ((O - T) @ nrm) / (Dv @ nrm)
        H = T + t[:, None] * Dv - O
        xy = np.c_[H @ ux, H @ uy][ok]
        xy -= xy.mean(0)
        out.append((xy, np.sqrt((xy ** 2).sum(1).mean()), ok.mean()))
    return out, tilt


# ---------------------------------------------------------------- drawing
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


def glass_outline(su, diam, I, j):
    """meridional outline of the mirror blank: the face plus a flat back."""
    face = surface_points(su, diam / 2)
    b = su.n * np.sign(_arrivals(I)[j] @ su.n)
    radial = np.cross(su.n, [1.0, 0, 0]); radial /= np.linalg.norm(radial)
    back = [su.v + r * radial + diam * THICK * b for r in (diam / 2, -diam / 2)]
    return np.array([X(p) for p in list(face) + back])


def angle_between(u, v):
    return np.degrees(np.arccos(np.clip(u @ v, -1, 1)))


def chief_path(I):
    return np.array([I[k] for k in ["V1", "V2", "VF", "V3", "Fp"]])


def draw(ax, s, I, diam, rays=True, dims=True, fs=9.5, glass=True):
    for j, (su, dm, c) in enumerate(zip(s, diam, COLS)):
        if glass:
            ax.add_patch(Polygon(glass_outline(su, dm, I, j), closed=True, fc=c, ec=c,
                                 alpha=0.25, lw=0.5))
        p = np.array([X(q) for q in surface_points(su, dm / 2)])
        ax.plot(p[:, 0], p[:, 1], color=c, lw=3, solid_capstyle="butt")
    R = I["D"] / 2
    xin = -I["V2"][2] - 12
    ax.plot([xin, 0], [R, R], color="#777", lw=0.8)
    ax.plot([xin, 0], [-R, -R], color="#777", lw=0.8)
    ax.plot([xin + 4, xin + 4], [-R - 1, R + 1], color="#444", lw=1.2, ls=(0, (6, 3)))
    ax.text(xin + 4, -R - 2.2, "aperture", ha="center", fontsize=fs)
    if rays:
        fields = [(0.0, "#ff7f0e")] + ([(FIELD_R, "#2ca02c"), (-FIELD_R, "#1f77b4")] if glass else [])
        for fy, col in fields:
            din = field_dir(I, 0.0, fy)
            for y in (-R, R):
                pts, d = M.trace(s, np.array([0.0, y, 0.0]) - 150 * din, din)
                pts = list(pts) + [pts[-1] + I["e3"] * d]
                good = transmitted(s, I, np.array([pts]), diam)[0] if glass else True
                p = np.array([X(q) for q in pts[1:]])
                ax.plot(p[:, 0], p[:, 1], color=col, lw=0.6, alpha=0.8, ls="-" if good else ":")
    cp = chief_path(I)
    pts = np.array([X(q) for q in cp])
    ax.annotate("", xy=(0, 0), xytext=(xin, 0),
                arrowprops=dict(arrowstyle="-|>", color="k", lw=1.2))
    for p, q in zip(pts[:-1], pts[1:]):
        ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="-|>", color="k", lw=1.1))
    if dims:
        for p, q in zip(cp[:-1], cp[1:]):
            m = (np.array(X(p)) + np.array(X(q))) / 2
            ax.text(m[0], m[1] + 0.4, f'{np.linalg.norm(q - p):.1f}"', ha="center",
                    fontsize=fs, bbox=dict(fc="white", ec="none", alpha=0.8, pad=0.4))
        # angle between the arriving and leaving legs at each mirror, as Novack labels them
        dirs = [I["din"], I["d1"], I["d2"], I["d3"], I["d4"]]
        for j, p in enumerate(cp[:4]):
            a = 180 - angle_between(dirs[j], dirs[j + 1])
            ox = {0: (-3.5, -1.5), 1: (5, -1.0), 2: (-6, -1.2), 3: (2.5, -0.6)}[j]
            xy = np.array(X(p))
            ax.text(xy[0] + ox[0] * I["D"] / 8, xy[1] + ox[1] * I["D"] / 8,
                    f"{a:.2f}°", fontsize=fs, color="#333")


def labels(ax, I, diam, fs=10):
    sp = I["R2"] / 2
    txt = [f'Primary paraboloid\n{diam[0]:.0f}" dia., {I["F1"]:.0f}" FL',
           f'Secondary convex sphere\n{diam[1]:.2f}" dia., {sp:.1f}" FL',
           f'Folding flat\n{diam[2]:.2f}" dia.',
           f'Tertiary concave sphere\n{diam[3]:.2f}" dia., {sp:.1f}" FL']
    off = [(2.6, -3.3), (0, 2.6), (0, 2.6), (0, -3.0)]
    for k, t, c, (ox, oy) in zip(["V1", "V2", "VF", "V3"], txt, COLS, off):
        x, y = X(I[k])
        ax.text(x + ox * I["D"] / 6, y + oy * I["D"] / 6, t, color=c, fontsize=fs,
                ha="center", va="center")
    x, y = X(I["Fp"])
    ax.text(x + 1.0, y, "focus", fontsize=fs, va="center")


def make_layout(key):
    L = LAYOUTS[key]; s, I, diam = L["s"], L["I"], L["diam"]
    fig, ax = plt.subplots(figsize=(14, 7.2))
    draw(ax, s, I, diam)
    labels(ax, I, diam)
    ax.set_aspect("equal"); ax.grid(True, alpha=0.25)
    ax.set_xlim(-70, 14); ax.set_ylim(-17, 21)
    ax.set_xlabel("inches (primary vertex at origin; light enters from the left)")
    ax.set_ylabel("inches")
    ax.set_title(f'Folded Stevick-Paul, {L["title"]}: T1 = {I["T1"]:.3f}°\n'
                 "primary → secondary → folding flat → tertiary → focus;  chief ray black, "
                 f"edge rays orange on-axis, green/blue ±{FIELD_R}\" field (dotted = lost)")
    fig.tight_layout(); fig.savefig(f"{OUT}/fsp8_{key}.png", dpi=150)
    plt.close(fig); print(f"wrote fsp8_{key}.png")


def make_novack():
    fig, ax = plt.subplots(figsize=(12, 6.6))
    draw(ax, nov, NI, NOV_DIAM, fs=10, glass=False)
    labels(ax, NI, NOV_DIAM)
    ax.set_aspect("equal"); ax.grid(True, alpha=0.25)
    ax.set_xlim(-46, 10); ax.set_ylim(-12, 14)
    ax.set_xlabel("inches (primary vertex at origin)")
    ax.set_title('Novack\'s 6" f/10 FSP, regenerated from Stevick\'s equations (T1 = 4.385°, A = 27.2/60)\n'
                 'matches his drawing: legs 32.8 / 31.7 / 22.7 / 27.2", angles 8.77° / 14.04° / 29.36° / 5.29°')
    fig.tight_layout(); fig.savefig(f"{OUT}/fsp_folded.png", dpi=160)
    plt.close(fig); print("wrote fsp_folded.png")


def make_flat_zoom(gaps):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.4))
    for ax, key in zip(axes, ["scaled", "clear"]):
        L = LAYOUTS[key]; s, I, diam = L["s"], L["I"], L["diam"]
        for fy, col in [(0.0, "#ff7f0e"), (FIELD_R, "#2ca02c"), (-FIELD_R, "#1f77b4")]:
            P, _ = trace_rays(s, I, 0.0, fy, n=8)
            P = P[np.abs(P[:, 0, 0]) < 1e-9]           # meridional fan
            ok = transmitted(s, I, P, diam)
            for pts, good in zip(P, ok):
                seg = np.array([X(q) for q in pts[2:4]])
                ax.plot(seg[:, 0], seg[:, 1], color="#aaa", lw=0.5)
                seg = np.array([X(q) for q in pts[4:6]])
                ax.plot(seg[:, 0], seg[:, 1], color=col, lw=0.8, ls="-" if good else ":")
        ax.add_patch(Polygon(glass_outline(s[2], diam[2], I, 2), closed=True, fc=COLS[2],
                             ec=COLS[2], alpha=0.35))
        ax.plot(*X(I["Fp"]), "k+", ms=12)
        c = np.array(X(I["VF"]))
        ax.set_xlim(c[0] - 7, c[0] + 10); ax.set_ylim(c[1] - 5.5, c[1] + 3.5)
        ax.set_aspect("equal"); ax.grid(alpha=0.3)
        ax.set_title(f'{L["title"]}\n{diam[2]:.2f}" flat, {diam[2] * THICK:.2f}" thick; '
                     f"glass-to-beam gap {gaps[key][2]:+.2f}\"")
    fig.suptitle("Tertiary → focus beam past the folding flat: orange on-axis, green/blue "
                 f"±{FIELD_R}\" meridional field; dotted = ray lost; grey = secondary → flat beam")
    fig.tight_layout(); fig.savefig(f"{OUT}/fsp8_flat_zoom.png", dpi=140)
    plt.close(fig); print("wrote fsp8_flat_zoom.png")


def make_spots(results):
    airy = 1.22 * LAM_UM * 12
    fig, axes = plt.subplots(2, 4, figsize=(17, 9.2))
    for row, key in zip(axes, ["scaled", "clear"]):
        sp, tilt = results[key]
        for ax, (xy, rms, frac), lab in zip(row, sp, FIELD_LABELS):
            um = xy * 25400
            ax.plot(um[:, 0], um[:, 1], ".", ms=3, color="#1f77b4")
            ax.add_patch(Circle((0, 0), airy, fill=False, ec="r", lw=1.4))
            m = 1.6 * airy
            ax.set_xlim(-m, m); ax.set_ylim(-m, m); ax.set_aspect("equal")
            ax.grid(True, alpha=0.25)
            ax.set_title(f"{lab}\nRMS {rms * 25400:.2f} µm, {100 * frac:.0f}% of light passes",
                         fontsize=10)
            ax.set_xlabel("sagittal (µm)")
        row[0].set_ylabel(f'{LAYOUTS[key]["title"]}\nimage plane tilted {tilt:.1f}°\nmeridional (µm)')
    fig.suptitle('Folded Stevick-Paul 8" f/12 — geometric spots on the best-fit tilted image plane '
                 f"(red = Airy disk, r = 1.22 λ N = {airy:.2f} µm at 550 nm)")
    fig.tight_layout(); fig.savefig(f"{OUT}/fsp8_spots.png", dpi=150)
    plt.close(fig); print("wrote fsp8_spots.png")


def make_svg(key):
    L = LAYOUTS[key]
    fig, ax = plt.subplots(figsize=(14, 7.2))
    draw(ax, L["s"], L["I"], L["diam"], dims=False)
    ax.set_aspect("equal"); ax.set_xlim(-70, 14); ax.set_ylim(-17, 21); ax.grid(True, alpha=0.25)
    svg = Path(f"{OUT}/fsp8_{key}.svg"); fig.savefig(svg); plt.close(fig)
    svg.write_text("\n".join(l.rstrip() for l in svg.read_text().splitlines()) + "\n")
    print(f"wrote fsp8_{key}.svg")


def make_dxf(key):
    L = LAYOUTS[key]; s, I, diam = L["s"], L["I"], L["diam"]
    ents = []
    def line(p, q, layer):
        ents.append(f"0\nLINE\n8\n{layer}\n10\n{p[0]:.4f}\n20\n{p[1]:.4f}\n30\n0\n"
                    f"11\n{q[0]:.4f}\n21\n{q[1]:.4f}\n31\n0")
    for j, (su, dm, nm) in enumerate(zip(s, diam, ["PRIMARY", "SECONDARY", "FOLDING_FLAT", "TERTIARY"])):
        p = glass_outline(su, dm, I, j)
        for a, b in zip(p, np.roll(p, -1, axis=0)):
            line(a, b, nm)
    cp = [X(q) for q in chief_path(I)]
    for a, b in zip(cp[:-1], cp[1:]):
        line(a, b, "PRINCIPAL_RAY")
    with open(f"{OUT}/fsp8_{key}.dxf", "w") as f:
        f.write("0\nSECTION\n2\nENTITIES\n" + "\n".join(ents) + "\n0\nENDSEC\n0\nEOF\n")
    print(f"wrote fsp8_{key}.dxf")


def report(key):
    L = LAYOUTS[key]; s, I, diam = L["s"], L["I"], L["diam"]
    print(f"== {L['title']}")
    print(f"   T1 {I['T1']:.3f}  T2 {I['T2']:.3f}  T3 {I['T3']:.3f}  4*T3 {4 * I['T3']:.2f}")
    print(f"   legs: P-S {I['e1']:.2f}  S-flat {I['eSF']:.2f}  flat-T {I['eFT']:.2f}  T-focus {I['e3']:.2f}")
    dirs = [I["din"], I["d1"], I["d2"], I["d3"], I["d4"]]
    print("   angles between legs: " + "  ".join(
        f"{n} {180 - angle_between(dirs[j], dirs[j + 1]):.2f}" for j, n in enumerate(NAMES)))
    for su, nm in zip(s, NAMES):
        a = np.degrees(np.arctan2(su.n[1], -su.n[2]))
        print(f"   {nm:9} vertex ({X(su.v)[0]:7.2f}, {X(su.v)[1]:6.2f})  normal {a:8.2f} deg")
    print(f"   focus ({X(I['Fp'])[0]:.2f}, {X(I['Fp'])[1]:.2f})")
    g = clearances(s, I, diam)
    print("   glass-to-beam gaps: " + "  ".join(f"{n} {v:+.2f}" for n, v in zip(NAMES, g)))
    sp, tilt = spots(s, I, diam)
    print(f"   image plane tilt {tilt:.2f} deg; " + "  ".join(
        f"{lab}: {r * 25400:.2f} um {100 * f:.0f}%" for (xy, r, f), lab in zip(sp, FIELD_LABELS)))
    return g, (sp, tilt)


if __name__ == "__main__":
    results, gaps = {}, {}
    for key in LAYOUTS:
        gaps[key], results[key] = report(key)
    if min(gaps["clear"]) <= 0:
        raise RuntimeError("clear-field layout: a mirror's glass is in a beam")
    make_novack()
    for key in LAYOUTS:
        make_layout(key); make_svg(key); make_dxf(key)
    make_flat_zoom(gaps)
    make_spots(results)
