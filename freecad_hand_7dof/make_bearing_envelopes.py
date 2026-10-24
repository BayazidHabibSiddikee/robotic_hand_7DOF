"""Generate bearing envelope STLs for the V2 hand (numpy only).

No vendor CAD download needed: a shielded deep-groove bearing is modelled as a
steel annulus with the exact ID x OD x width. Good enough for fit checks,
collision geometry and inertia.

Run: python3 make_bearing_envelopes.py
"""
import numpy as np, struct, os

HERE = os.path.dirname(os.path.abspath(__file__))
MESH = os.path.join(HERE, "meshes")
os.makedirs(MESH, exist_ok=True)

# trade name: (ID, OD, width) in mm
BEARINGS = {
    "683ZZ": (3.0, 7.0, 3.0),
    "608ZZ": (8.0, 22.0, 7.0),
}


def annulus(r_out, r_in, h, n=48):
    """Hollow cylinder centred at origin, axis Z, dimensions in mm."""
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    c, s = np.cos(th), np.sin(th)
    z0, z1 = -h / 2, h / 2
    ob = np.stack([r_out * c, r_out * s, np.full(n, z0)], 1)
    ot = np.stack([r_out * c, r_out * s, np.full(n, z1)], 1)
    ib = np.stack([r_in * c, r_in * s, np.full(n, z0)], 1)
    it = np.stack([r_in * c, r_in * s, np.full(n, z1)], 1)
    v = np.vstack([ob, ot, ib, it])          # 0..3n
    F = []
    for i in range(n):
        j = (i + 1) % n
        # outer wall
        F += [(i, j, n + j), (i, n + j, n + i)]
        # inner wall (reverse winding so normals point inward)
        F += [(2 * n + i, 3 * n + i, 3 * n + j), (2 * n + i, 3 * n + j, 2 * n + j)]
        # bottom ring
        F += [(i, 2 * n + i, 2 * n + j), (i, 2 * n + j, j)]
        # top ring
        F += [(n + i, n + j, 3 * n + j), (n + i, 3 * n + j, 3 * n + i)]
    return v, np.array(F, int)


def write_stl(path, v, f):
    tri = np.asarray(v, float)[np.asarray(f, int)]
    e1, e2 = tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]
    n = np.cross(e1, e2)
    ln = np.linalg.norm(n, axis=1, keepdims=True)
    ln[ln == 0] = 1
    n = n / ln
    with open(path, "wb") as fh:
        fh.write(b"V2 hand bearing envelope".ljust(80, b"\0"))
        fh.write(struct.pack("<I", len(tri)))
        for i in range(len(tri)):
            fh.write(struct.pack("<12fH", *n[i], *tri[i, 0], *tri[i, 1], *tri[i, 2], 0))
    print(f"wrote {path} ({len(tri)} tris, {os.path.getsize(path)} bytes)")


for name, (id_mm, od_mm, w_mm) in BEARINGS.items():
    v, f = annulus(od_mm / 2, id_mm / 2, w_mm)
    write_stl(f"{MESH}/bearing_{name}.stl", v, f)
    # rough steel mass (7.85 g/cm^3) for the URDF inertial tag
    vol_mm3 = np.pi * (od_mm**2 - id_mm**2) / 4 * w_mm
    print(f"  {name}: {id_mm}x{od_mm}x{w_mm} mm  mass ~{vol_mm3*7.85e-3:.2f} g")

print("done ->", MESH)
