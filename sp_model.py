"""
Stevick-Paul 8" f/12 -- exact raytrace model.

Geometry reconstructed from David Stevick's design manual (ATMJ #3, 1993;
archived SEDS/AmSky pages) and refined by exact raytracing.

Coordinates (meridional plane): z = telescope axis, y = the "walk" direction,
x = sagittal (out of plane).  Incoming collimated light travels in -z and is
centred on the primary vertex.  All mirror axes lie in the y-z plane, so the
system is symmetric under x -> -x.

Surface convention (general conic of revolution):
    vertex V, axis unit vector n (points toward the centre of curvature),
    signed radius R, conic constant k.  Sag along +n: r^2 = 2 R s - (1+k) s^2.
"""

import numpy as np

def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


class Sur:
    def __init__(self, v, n, R, k=0.0, flat=False, name=""):
        self.v = np.asarray(v, float)
        n = np.asarray(n, float)
        self.n = n / np.linalg.norm(n)
        self.R = float(R)
        self.k = float(k)
        self.flat = flat
        self.name = name

    def intersect(self, P, d):
        P = np.asarray(P, float); d = np.asarray(d, float)
        if self.flat:
            den = np.dot(d, self.n)
            if abs(den) < 1e-12:
                return None
            t = np.dot(self.v - P, self.n) / den
            if t <= 1e-9:
                return None
            return t, P + t * d, self.n
        q = P - self.v
        s0 = np.dot(q, self.n)
        rv0 = q - s0 * self.n
        dn = np.dot(d, self.n)
        dtr = d - dn * self.n
        A = np.dot(dtr, dtr); B = 2 * np.dot(rv0, dtr); C = np.dot(rv0, rv0)
        a = A + (1 + self.k) * dn * dn
        b = B - (2 * self.R * dn - 2 * (1 + self.k) * s0 * dn)
        c = C - 2 * self.R * s0 + (1 + self.k) * s0 * s0
        ts = []
        if abs(a) < 1e-15:
            if abs(b) > 1e-18:
                ts.append(-c / b)
        else:
            disc = b * b - 4 * a * c
            if disc < 0:
                return None
            sq = np.sqrt(disc)
            ts += [(-b - sq) / (2 * a), (-b + sq) / (2 * a)]
        ts = [t for t in ts if t > 1e-9]
        if not ts:
            return None
        t = min(ts)
        X = P + t * d
        ss = X - self.v
        salong = np.dot(ss, self.n)
        rvec = ss - salong * self.n
        r = np.linalg.norm(rvec)
        if r > 1e-12:
            radial = rvec / r
            sp = r / np.sqrt(self.R * self.R - (1 + self.k) * r * r)
            N = self.n - sp * radial
            N = N / np.linalg.norm(N)
        else:
            N = self.n
        return t, X, N


def reflect(d, N):
    return d - 2 * np.dot(d, N) * N


def _axis(a, b):
    """unit axis pointing toward the centre of curvature (forced +z-ish)."""
    u = unit(a - b)
    return u if u[2] > 0 else -u


def build_sp(N=12.0, D=8.0, A=0.4, C=35.67, tilt3_deg=None):
    """Build an 8" f/12 Stevick-Paul.  Returns (surfaces, dict)."""
    F1 = N * D
    R1 = 2 * F1
    R2 = A * R1
    F2 = -R2 / 2
    F3 = R2 / 2
    T1 = np.radians(C / N)
    T2 = (1 + A) / (2 * A) * T1
    T3 = T2 - T1
    e1 = F1 + F2
    e2 = R2
    e3 = F3

    th1 = 2 * T1                      # principal ray: primary -> secondary
    th2 = 2 * T3                      # principal ray: secondary -> tertiary
    th3 = np.radians(tilt3_deg if tilt3_deg is not None else -9.0)  # tertiary -> focus (= focal-plane tilt)

    din = np.array([0.0, 0.0, -1.0])
    d1 = np.array([0.0, np.sin(th1),  np.cos(th1)])
    d2 = np.array([0.0, np.sin(th2), -np.cos(th2)])
    d3 = np.array([0.0, np.sin(th3),  np.cos(th3)])

    V1 = np.array([0.0, 0.0, 0.0])
    V2 = V1 + e1 * d1
    V3 = V2 + e2 * d2
    Fp = V3 + e3 * d3

    s1 = Sur(V1, _axis(din, d1),  R1, k=-1, name="Primary (paraboloid)")
    s2 = Sur(V2, _axis(d1, d2),   R2, k=0,  name="Secondary (convex sphere)")
    s3 = Sur(V3, _axis(d2, d3),   R2, k=0,  name="Tertiary (concave sphere)")

    info = dict(N=N, D=D, A=A, C=C,
                F1=F1, R1=R1, R2=R2, F2=F2, F3=F3,
                T1=np.degrees(T1), T2=np.degrees(T2), T3=np.degrees(T3),
                e1=e1, e2=e2, e3=e3,
                th1=np.degrees(th1), th2=np.degrees(th2), th3=np.degrees(th3),
                V1=V1, V2=V2, V3=V3, Fp=Fp,
                d1=d1, d2=d2, d3=d3, din=din,
                a1=V2[1], a2=V3[1],
                axis1=np.degrees(np.arctan2(s1.n[1], s1.n[2])),
                axis2=np.degrees(np.arctan2(s2.n[1], s2.n[2])),
                axis3=np.degrees(np.arctan2(s3.n[1], s3.n[2])))
    return [s1, s2, s3], info


def trace(surfs, P0, d0):
    P = np.asarray(P0, float)
    d = unit(d0)
    pts = [P.copy()]
    for s in surfs:
        r = s.intersect(P, d)
        if r is None:
            return None
        t, P, N = r
        pts.append(P.copy())
        d = unit(reflect(d, N))
    return np.array(pts), d


def pupil_rays(D=8.0, n=16):
    """hexapolar/grid pupil samples of radius D/2."""
    R = D / 2
    pts = []
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            x = i * R / n
            y = j * R / n
            if x * x + y * y <= R * R + 1e-9:
                pts.append((x, y))
    return np.array(pts)


def field_rays(field_deg, D=8.0, n=16):
    """rays for a field point: incoming tilt of field_deg in the meridional (y) plane."""
    a = np.radians(field_deg)
    din = unit(np.array([0.0, np.sin(a), -np.cos(a)]))
    uv = pupil_rays(D, n)
    return uv, din


def best_focus(surfs, uv, din, zlo=-10, zhi=40):
    pts = []
    for (x, y) in uv:
        r = trace(surfs, np.array([x, y, 200.0]), din)
        if r is None:
            continue
        pts.append((r[0][-1], r[1]))
    P = np.array([p for p, d in pts])
    Dv = np.array([d for p, d in pts])
    best = (1e18, None, None)
    for zf in np.linspace(zlo, zhi, 1201):
        t = (zf - P[:, 2]) / Dv[:, 2]
        h = P + t[:, None] * Dv
        c = h[:, :2].mean(0)
        v = np.sqrt(((h[:, :2] - c) ** 2).sum(1).mean())
        if v < best[0]:
            best = (v, zf, c.copy())
    return best, (P, Dv)


if __name__ == "__main__":
    surfs, info = build_sp()
    for k in ["N", "D", "A", "R1", "R2", "F1", "F2", "F3", "e1", "e2", "e3",
              "T1", "T2", "T3", "th1", "th2", "th3", "a1", "a2",
              "axis1", "axis2", "axis3"]:
        print(f"{k:8} {info[k]:.5f}")
    print("V2", info["V2"], "V3", info["V3"], "Fp", info["Fp"])
    uv, din = field_rays(0.0)
    (rms, zf, c), _ = best_focus(surfs, uv, din)
    print(f"on-axis RMS = {rms*25400:.4f} um at z={zf:.3f}")
