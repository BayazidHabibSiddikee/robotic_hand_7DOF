"""Build 7-DOF hand meshes with NUMPY ONLY (no trimesh/OCC needed).
Generates binary STL files into meshes/ for the FreeCAD + URDF hand.
Run: /home/bayazid/micromamba/envs/rosenv/bin/python build_meshes.py
"""
import numpy as np, struct, os
HERE = os.path.dirname(os.path.abspath(__file__))
MESH = os.path.join(HERE, "meshes")
os.makedirs(MESH, exist_ok=True)

def box(w, h, d):
    w, h, d = w/2, h/2, d/2
    v = np.array([[-w,-h,-d],[w,-h,-d],[w,h,-d],[-w,h,-d],
                  [-w,-h,d],[w,-h,d],[w,h,d],[-w,h,d]], float)
    f = [(0,1,2),(0,2,3),(4,6,5),(4,7,6),(0,4,5),(0,5,1),
         (1,5,6),(1,6,2),(2,6,7),(2,7,3),(3,7,4),(3,4,0)]
    return v, np.array(f, int)

def cyl(r, h, n=24, axis="z"):
    th = np.linspace(0, 2*np.pi, n, endpoint=False)
    ring_b = np.stack([r*np.cos(th), r*np.sin(th), np.full(n, -h/2)], 1)
    ring_t = ring_b.copy(); ring_t[:, 2] = h/2
    cb = np.array([0, 0, -h/2]); ct = np.array([0, 0, h/2])
    v = np.vstack([ring_b, ring_t, cb[None, :], ct[None, :]])
    F = []
    for i in range(n):
        j = (i+1) % n
        F.append((i, j, n+j)); F.append((i, n+j, n+i))  # side
        F.append((2*n, j, i)); F.append((2*n+1, n+i, n+j))  # caps
    v2 = v.copy()
    if axis == "x":  # z -> x
        v2 = v[:, [2, 1, 0]] * np.array([1, 1, 1])
        # rotate: (x,y,z)->(z,y,x) maps z-axis to x-axis
    elif axis == "y":
        v2 = v[:, [0, 2, 1]] * np.array([1, 1, 1])
    return v2, np.array(F, int)

def translate(v, t):
    return v + np.array(t, float)

def write_stl(path, v, f):
    v = np.asarray(v, float); f = np.asarray(f, int)
    tri = v[f]  # (N,3,3)
    e1 = tri[:, 1]-tri[:, 0]; e2 = tri[:, 2]-tri[:, 0]
    n = np.cross(e1, e2)
    ln = np.linalg.norm(n, axis=1, keepdims=True); ln[ln == 0] = 1
    n = n/ln
    with open(path, "wb") as fh:
        fh.write(b"7DOF hand Binary STL" + b"\0"*(80-20))
        fh.write(struct.pack("<I", len(tri)))
        for i in range(len(tri)):
            fh.write(struct.pack("<12fH", *n[i], *tri[i, 0], *tri[i, 1], *tri[i, 2], 0))
    print(f"wrote {path} ({len(tri)} tris)")

# --- Parts (metres). X = forward along arm, Y = left/right, Z = up ---
# 1. wrist adapter: short cylinder along X + flange box (mounts to wrist_roll tip)
v1, f1 = cyl(0.025, 0.03, 28, axis="x")
v2, f2 = box(0.02, 0.07, 0.07)
v2 = translate(v2, (0.022, 0, 0))
v = np.vstack([v1, v2]); f = np.vstack([f1, f2+len(v1)])
write_stl(f"{MESH}/hand_adapter_link.stl", v, f)

# 2. yaw housing (H1 child): rounded box
v, f = box(0.05, 0.075, 0.045)
write_stl(f"{MESH}/hand_yaw_link.stl", v, f)

# 3. pitch housing (H2 child)
v, f = box(0.045, 0.065, 0.04)
write_stl(f"{MESH}/hand_pitch_link.stl", v, f)

# 4. palm plate (H3 child): main palm 120 x 100 x 18 mm + cable ridge
v1, f1 = box(0.12, 0.10, 0.018)
v1 = translate(v1, (0.045, 0, 0))
v2, f2 = box(0.03, 0.06, 0.012)
v2 = translate(v2, (-0.005, 0, 0.014))
v = np.vstack([v1, v2]); f = np.vstack([f1, f2+len(v1)])
write_stl(f"{MESH}/hand_palm_link.stl", v, f)

# 5/6. knuckle spreaders L/R (H4/H5 children): 20x20x30mm blocks with pivot boss
for side, name in [(-1, "hand_knuckle_l_link"), (1, "hand_knuckle_r_link")]:
    v1, f1 = box(0.035, 0.022, 0.03)
    v1 = translate(v1, (0.012, 0, 0))
    v2, f2 = cyl(0.011, 0.032, 20, axis="z")
    v2 = translate(v2, (-0.005, 0, 0))
    v = np.vstack([v1, v2]); f = np.vstack([f1, f2+len(v1)])
    write_stl(f"{MESH}/{name}.stl", v, f)

print("ALL MESHES DONE ->", MESH)
