import os
import FreeCAD
import Mesh

MESH_DIR = "/home/sword/Documents/Robotics/robotic_hand_7DOF/freecad_hand_7dof/meshes"
OUT = "/home/sword/Documents/Robotics/robotic_hand_7DOF/freecad_hand_7dof/hand_7dof.FCStd"

doc = FreeCAD.newDocument("HandV2")
grp = doc.addObject("App::DocumentObjectGroup", "HandV2")

stl_files = sorted(f for f in os.listdir(MESH_DIR) if f.endswith(".stl"))
print(f"Loading {len(stl_files)} STLs...")

for fname in stl_files:
    path = os.path.join(MESH_DIR, fname)
    name = os.path.splitext(fname)[0]
    try:
        mesh_obj = doc.addObject("Mesh::Feature", name)
        mesh = Mesh.Mesh(path)
        mesh_obj.Mesh = mesh
        grp.addObject(mesh_obj)
        print(f"  OK: {name}")
    except Exception as e:
        print(f"  FAIL: {name}: {e}")

doc.recompute()
doc.saveAs(OUT)
print(f"\nSaved: {OUT}")
