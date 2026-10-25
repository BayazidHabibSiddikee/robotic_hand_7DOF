"""Generate hand_7dof.FCStd using FreeCAD's native API.
Run: freecad --console --macro generate_fcstd.py
"""
import os, sys
import FreeCAD
import Mesh
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
MESH_DIR = os.path.join(HERE, "meshes")
OUT = os.path.join(HERE, "hand_7dof.FCStd")

doc = FreeCAD.newDocument("HandV2")
grp = doc.addObject("App::DocumentObjectGroup", "HandV2")

stl_files = sorted(f for f in os.listdir(MESH_DIR) if f.endswith(".stl"))
print(f"Loading {len(stl_files)} STLs...")

for i, fname in enumerate(stl_files):
    path = os.path.join(MESH_DIR, fname)
    name = os.path.splitext(fname)[0]
    try:
        # Import mesh from STL
        mesh_obj = doc.addObject("Mesh::Feature", name)
        mesh = Mesh.Mesh(path)
        mesh_obj.Mesh = mesh
        grp.addObject(mesh_obj)
        print(f"  OK: {name}")
    except Exception as e:
        print(f"  FAIL: {name} — {e}")

# Position parts approximately (for visual clarity, not URDF accuracy)
# The URDF handles actual joint transforms
positions = {
    "hand_adapter_link":      (0, 0, 0),
    "hand_palm_link":         (0.13, 0, 0.018),
    "thumb_base_link":        (0.115, -0.032, 0.027),
    "thumb_P_link":           (0.14, -0.025, 0.027),
    "thumb_D_link":           (0.165, -0.025, 0.027),
    "index_K_link":           (0.12, -0.015, 0.027),
    "index_P_link":           (0.146, -0.015, 0.027),
    "index_M_link":           (0.172, -0.015, 0.027),
    "index_D_link":           (0.192, -0.015, 0.027),
    "middle_K_link":          (0.12, 0, 0.027),
    "middle_P_link":          (0.148, 0, 0.027),
    "middle_M_link":          (0.178, 0, 0.027),
    "middle_D_link":          (0.201, 0, 0.027),
    "ring_K_link":            (0.12, 0.015, 0.027),
    "ring_P_link":            (0.146, 0.015, 0.027),
    "ring_M_link":            (0.172, 0.015, 0.027),
    "ring_D_link":            (0.192, 0.015, 0.027),
    "little_K_link":          (0.12, 0.030, 0.027),
    "little_P_link":          (0.142, 0.030, 0.027),
    "little_M_link":          (0.162, 0.030, 0.027),
    "little_D_link":          (0.179, 0.030, 0.027),
}

for obj in grp.Group:
    name = obj.Name
    if name in positions:
        x, y, z = positions[name]
        obj.Placement = FreeCAD.Placement(FreeCAD.Vector(x, y, z), FreeCAD.Rotation())

doc.recompute()
doc.saveAs(OUT)
print(f"\nSaved to {OUT}")
print(f"Total objects: {len(doc.Objects)}")
