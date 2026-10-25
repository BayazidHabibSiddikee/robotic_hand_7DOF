"""V2 hand mesh generator — anthropomorphic 5-finger hand, numpy only.

Generates per-link STLs for the V2 anthropomorphic hand:
  - hand_adapter_link.stl   wrist mount cylinder + flange
  - hand_palm_link.stl      palm plate with finger bosses
  - thumb_base_link.stl     CMC opposition plate (rotates about Z)
  - thumb_P_link.stl        thumb proximal phalanx
  - thumb_D_link.stl        thumb distal phalanx
  - {i,m,r,l}_P_link.stl    proximal phalanx (with MCP dome)
  - {i,m,r,l}_M_link.stl    middle phalanx
  - {i,m,r,l}_D_link.stl    distal phalanx + fingertip
  - {i,m,r,l}_K_link.stl    knuckle bracket (683ZZ pocket)

All dims in mm. URDF applies scale=0.001 when loading.
"""
import numpy as np, struct, os

HERE = os.path.dirname(os.path.abspath(__file__))
MESH_DIR = os.path.join(HERE, "meshes")
os.makedirs(MESH_DIR, exist_ok=True)


def box(w, h, d, cx=0.0, cy=0.0, cz=0.0):
    """Axis-aligned box. w=X, h=Z, d=Y."""
    cx, cy, cz = float(cx), float(cy), float(cz)
    hw, hh, hd = w/2, h/2, d/2
    v = np.array([
        [cx-hw,cy-hd,cz-hh],[cx+hw,cy-hd,cz-hh],
        [cx+hw,cy+hd,cz-hh],[cx-hw,cy+hd,cz-hh],
        [cx-hw,cy-hd,cz+hh],[cx+hw,cy-hd,cz+hh],
        [cx+hw,cy+hd,cz+hh],[cx-hw,cy+hd,cz+hh]], dtype=float)
    f = np.array([
        [0,1,2],[0,2,3],[4,6,5],[4,7,6],
        [0,4,5],[0,5,1],[1,5,6],[1,6,2],
        [2,6,7],[2,7,3],[3,7,4],[3,4,0]], dtype=int)
    return v, f


def cyl(r, h, n=32, axis="z", cx=0.0, cy=0.0, cz=0.0):
    """Cylinder. r=radius, h=height along chosen axis."""
    cx, cy, cz = float(cx), float(cy), float(cz)
    th = np.linspace(0, 2*np.pi, n, endpoint=False)
    c, s = np.cos(th), np.sin(th)
    z0, z1 = -h/2, h/2
    rb = np.stack([r*c, r*s, np.full(n, z0)], 1)
    rt = np.stack([r*c, r*s, np.full(n, z1)], 1)
    cb = np.array([0, 0, z0])
    ct = np.array([0, 0, z1])
    verts = np.vstack([rb, rt, cb[None], ct[None]]).astype(float)
    faces = []
    for i in range(n):
        j = (i+1) % n
        faces.extend([[i,j,n+j],[i,n+j,n+i]])
    faces.extend([[2*n, j, i] for i, j in zip(range(n), range(1, n+1))])
    faces.extend([[2*n+1, n+i, n+j] for i, j in zip(range(n), range(1, n+1))])
    if axis == "x":
        verts = verts[:, [2, 1, 0]]
    elif axis == "y":
        verts = verts[:, [0, 2, 1]]
    verts[:, 0] += cx; verts[:, 1] += cy; verts[:, 2] += cz
    return verts, np.array(faces, dtype=int)


def annulus(r_out, r_in, h, n=32, cx=0.0, cy=0.0, cz=0.0, axis="z"):
    """Hollow cylinder (bearing envelope)."""
    cx, cy, cz = float(cx), float(cy), float(cz)
    th = np.linspace(0, 2*np.pi, n, endpoint=False)
    c, s = np.cos(th), np.sin(th)
    z0, z1 = -h/2, h/2
    ob = np.stack([r_out*c, r_out*s, np.full(n, z0)], 1)
    ot = np.stack([r_out*c, r_out*s, np.full(n, z1)], 1)
    ib = np.stack([r_in*c, r_in*s, np.full(n, z0)], 1)
    it = np.stack([r_in*c, r_in*s, np.full(n, z1)], 1)
    verts = np.vstack([ob, ot, ib, it]).astype(float)
    faces = []
    for i in range(n):
        j = (i+1) % n
        faces.extend([[i,j,n+j],[i,n+j,n+i]])
        faces.extend([[2*n+i,3*n+i,3*n+j],[2*n+i,3*n+j,2*n+j]])
        faces.extend([[i,2*n+i,2*n+j],[i,2*n+j,j]])
        faces.extend([[n+i,n+j,3*n+j],[n+i,3*n+j,3*n+i]])
    if axis == "x":
        verts = verts[:, [2, 1, 0]]
    elif axis == "y":
        verts = verts[:, [0, 2, 1]]
    verts[:, 0] += cx; verts[:, 1] += cy; verts[:, 2] += cz
    return verts, np.array(faces, dtype=int)


def hemi_dome(r, axis="x", cap_dir="pos", n_seg=20, n_ring=6):
    """Hemispherical dome surface. axis='x' opens along ±X.
    cap_dir='pos' → cap at +axis end, 'neg' → cap at -axis end."""
    th = np.linspace(0, 2*np.pi, n_seg, endpoint=False)
    phi_vals = np.linspace(0, np.pi/2, n_ring + 1)
    all_v = []
    all_f = []
    vi = 0
    for pi, phi in enumerate(phi_vals):
        rr = r * np.sin(phi)
        zz = r * np.cos(phi)
        ring = np.zeros((n_seg, 3), dtype=float)
        if axis == "x":
            xp =  zz if cap_dir == "pos" else -zz
            ring[:, 0] = xp
            ring[:, 1] = rr * np.cos(th)
            ring[:, 2] = rr * np.sin(th)
        elif axis == "y":
            yp =  zz if cap_dir == "pos" else -zz
            ring[:, 0] = rr * np.cos(th)
            ring[:, 1] = yp
            ring[:, 2] = rr * np.sin(th)
        else:
            zp =  zz if cap_dir == "pos" else -zz
            ring[:, 0] = rr * np.cos(th)
            ring[:, 1] = rr * np.sin(th)
            ring[:, 2] = zp
        all_v.append(ring)
        if pi > 0:
            prev_vi = vi - n_seg
            for k in range(n_seg):
                kk = (k+1) % n_seg
                all_f.extend([[prev_vi+k, prev_vi+kk, vi+kk],
                              [prev_vi+k, vi+kk, vi+k]])
        vi += n_seg
    # Cap at pole
    pole = np.zeros((1, 3), dtype=float)
    if axis == "x":  pole[0, 0] =  r if cap_dir=="pos" else -r
    elif axis == "y": pole[0, 1] =  r if cap_dir=="pos" else -r
    else:            pole[0, 2] =  r if cap_dir=="pos" else -r
    all_v.append(pole)
    eq_vi = (len(phi_vals) - 1) * n_seg
    for k in range(n_seg):
        kk = (k+1) % n_seg
        all_f.extend([[len(all_v)-1, eq_vi+kk, eq_vi+k]])
    return np.vstack(all_v), np.array(all_f, dtype=int)


def write_stl(path, verts, faces, label="V2 hand"):
    tri = np.asarray(verts, dtype=float)[np.asarray(faces, dtype=int)]
    e1 = tri[:, 1] - tri[:, 0]
    e2 = tri[:, 2] - tri[:, 0]
    norms = np.cross(e1, e2)
    lens = np.linalg.norm(norms, axis=1, keepdims=True)
    lens[lens == 0] = 1
    norms = norms / lens
    header = label.encode().ljust(80, b"\0")[:80]
    with open(path, "wb") as fh:
        fh.write(header)
        fh.write(struct.pack("<I", len(tri)))
        for i in range(len(tri)):
            fh.write(struct.pack("<12fH", *norms[i],
                                 *tri[i, 0], *tri[i, 1], *tri[i, 2], 0))
    sz = os.path.getsize(path)
    print(f"  {os.path.basename(path):32s} {len(tri):5d} tris  {sz/1024:6.1f} KB")


# ── Part builders ─────────────────────────────────────────────────────────────

def make_adapter():
    """Wrist adapter: Ø50mm cylinder along X + 70×70×20mm flange."""
    cv, cf = cyl(25.0, 30.0, n=28, axis="x")
    fv, ff = box(20.0, 70.0, 70.0, cx=40, cy=0, cz=0)
    verts = np.vstack([cv, fv])
    faces = np.vstack([cf, ff + len(cv)])
    return verts, faces


def make_palm():
    """Palm plate 130×70×18 mm + 5 finger bosses + cable ridge."""
    PL, PW, PT = 130.0, 70.0, 18.0
    pv, pf = box(PL, PW, PT, cx=PL/2, cy=0, cz=PT/2)
    verts, faces = [pv], [pf]
    off = len(pv)

    boss_x = PL - 32
    for y in [-28.0, -14.0, 0.0, 14.0, 26.0]:
        bv, bf = box(22.0, 14.0, 8.0, cx=boss_x+11, cy=y, cz=PT+4.0)
        verts.append(bv); faces.append(bf + off); off += len(bv)

    rv, rf = box(18.0, PW-6, 5.0, cx=9, cy=0, cz=PT+2.5)
    verts.append(rv); faces.append(rf + off); off += len(rv)

    return np.vstack(verts), np.vstack(faces)


def make_thumb_base():
    """CMC base 24×22×8 mm with 683ZZ bearing seat."""
    W, D, T = 24.0, 22.0, 8.0
    pv, pf = box(W, D, T, cx=W/2, cy=D/2, cz=T/2)
    sv, sf = annulus(3.5, 1.5, T+2, n=24, cx=W/2, cy=D/2, cz=T/2, axis="x")
    verts = np.vstack([pv, sv])
    faces = np.vstack([pf, sf + len(pv)])
    return verts, faces


def make_proximal(length, width, thickness, dome_r):
    """Proximal phalanx: shaft + hemisphere on +X (MCP side)."""
    sv, sf = box(length, width, thickness, cx=length/2, cy=0, cz=thickness/2)
    dv, df = hemi_dome(dome_r, axis="x", cap_dir="pos", n_seg=18, n_ring=5)
    nv = len(sv)
    dv[:, 0] += length
    dv[:, 1] *= width / (2*dome_r) if dome_r > 0 else 1
    dv[:, 2] *= thickness / (2*dome_r) if dome_r > 0 else 1
    dv[:, 2] += thickness/2
    df = df + nv
    verts = np.vstack([sv, dv])
    faces = np.vstack([sf, df])
    return verts, faces


def make_middle(length, width, thickness, r_top, r_bot):
    """Middle phalanx: shaft + domes on both ends."""
    sv, sf = box(length, width, thickness, cx=length/2, cy=0, cz=thickness/2)
    nv_s = len(sv)

    # +X dome (PIP)
    dtv, dtf = hemi_dome(r_top, axis="x", cap_dir="pos", n_seg=16, n_ring=5)
    dtv[:, 0] += length
    dtv[:, 1] *= width / (2*r_top) if r_top > 0 else 1
    dtv[:, 2] *= thickness / (2*r_top) if r_top > 0 else 1
    dtv[:, 2] += thickness/2
    dtf = dtf + nv_s
    nv_dt = len(dtv)

    # -X dome (MCP)
    dbv, dbf = hemi_dome(r_bot, axis="x", cap_dir="neg", n_seg=16, n_ring=5)
    dbv[:, 1] *= width / (2*r_bot) if r_bot > 0 else 1
    dbv[:, 2] *= thickness / (2*r_bot) if r_bot > 0 else 1
    dbv[:, 2] += thickness/2
    dbf = dbf + nv_s + nv_dt

    verts = np.vstack([sv, dtv, dbv])
    faces = np.vstack([sf, dtf, dbf])
    return verts, faces


def make_distal(length, width, thickness):
    """Distal phalanx: shaft + rounded fingertip."""
    sv, sf = box(length, width, thickness, cx=length/2, cy=0, cz=thickness/2)
    tip_r = min(width, thickness) / 2
    tv, tf = hemi_dome(tip_r, axis="x", cap_dir="pos", n_seg=14, n_ring=4)
    nv = len(sv)
    tv[:, 0] += length
    tv[:, 1] *= width / (2*tip_r) if tip_r > 0 else 1
    tv[:, 2] *= thickness / (2*tip_r) if tip_r > 0 else 1
    tv[:, 2] += thickness/2
    tf = tf + nv
    verts = np.vstack([sv, tv])
    faces = np.vstack([sf, tf])
    return verts, faces


def make_knuckle(width, thickness):
    """Knuckle bracket with 683ZZ bearing pocket."""
    bv, bf = box(8.0, width+4, thickness+4, cx=4, cy=0, cz=(thickness+4)/2)
    sv, sf = annulus(3.5, 1.5, thickness+6, n=20,
                     cx=4, cy=0, cz=(thickness+4)/2, axis="x")
    verts = np.vstack([bv, sv])
    faces = np.vstack([bf, sf + len(bv)])
    return verts, faces


# ── Finger configs ────────────────────────────────────────────────────────────

FINGERS = {
    "index":  dict(P=(26,10,8,5.5),  M=(20,8,7,4.5,5.5),  D=(16,7,6),  K=(10,8)),
    "middle": dict(P=(28,10,8,5.5),  M=(22,8,7,4.5,5.5),  D=(17,7,6),  K=(10,8)),
    "ring":   dict(P=(26,9,7,5.0),   M=(20,7,6,4.0,5.0),  D=(15,6,5),  K=(9,7)),
    "little": dict(P=(22,8,6,4.5),   M=(16,6,5,3.5,4.5),  D=(13,5,4),  K=(8,6)),
}


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=== V2 Hand Mesh Generator ===\n")

    print("[adapter]")
    v, f = make_adapter()
    write_stl(f"{MESH_DIR}/hand_adapter_link.stl", v, f, "V2 Adapter")

    print("[palm]")
    v, f = make_palm()
    write_stl(f"{MESH_DIR}/hand_palm_link.stl", v, f, "V2 Palm")

    print("[thumb_base]")
    v, f = make_thumb_base()
    write_stl(f"{MESH_DIR}/thumb_base_link.stl", v, f, "V2 Thumb Base")

    print("[thumb]")
    v, f = make_proximal(22, 16, 10, 6.0)
    write_stl(f"{MESH_DIR}/thumb_P_link.stl", v, f, "V2 Thumb Proximal")
    v, f = make_distal(16, 14, 9)
    write_stl(f"{MESH_DIR}/thumb_D_link.stl", v, f, "V2 Thumb Distal")

    for name, cfg in FINGERS.items():
        pL,pW,pH,pdR = cfg["P"]
        mL,mW,mT,mdR,mpR = cfg["M"]
        dL,dW,dT = cfg["D"]
        kW,kT = cfg["K"]
        print(f"  [{name}]")
        v, f = make_proximal(pL, pW, pH, pdR)
        write_stl(f"{MESH_DIR}/{name}_P_link.stl", v, f, f"V2 {name.title()} Proximal")
        v, f = make_middle(mL, mW, mT, mdR, mpR)
        write_stl(f"{MESH_DIR}/{name}_M_link.stl", v, f, f"V2 {name.title()} Middle")
        v, f = make_distal(dL, dW, dT)
        write_stl(f"{MESH_DIR}/{name}_D_link.stl", v, f, f"V2 {name.title()} Distal")
        v, f = make_knuckle(kW, kT)
        write_stl(f"{MESH_DIR}/{name}_K_link.stl", v, f, f"V2 {name.title()} Knuckle")

    print("[bearings]")
    for bname, (id_mm, od_mm, w_mm) in [("683ZZ",(3.0,7.0,3.0)),("608ZZ",(8.0,22.0,7.0))]:
        v, f = annulus(od_mm/2, id_mm/2, w_mm, n=32)
        write_stl(f"{MESH_DIR}/bearing_{bname}.stl", v, f, f"V2 Bearing {bname}")

    count = len(os.listdir(MESH_DIR))
    print(f"\n=== Done — {count} STL files in {MESH_DIR} ===")


if __name__ == "__main__":
    main()
