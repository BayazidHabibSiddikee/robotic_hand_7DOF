"""Generate hand_7dof.FCStd using FreeCAD's native API with proper positioning.
Run: freecad --console --macro freecad_hand_7dof/generate_fcstd.py
"""
import os
import FreeCAD
import Mesh

MESH_DIR = "/home/sword/Documents/Robotics/robotic_hand_7DOF/freecad_hand_7dof/meshes"
OUT = "/home/sword/Documents/Robotics/robotic_hand_7DOF/freecad_hand_7dof/hand_7dof.FCStd"

doc = FreeCAD.newDocument("HandV2")
grp = doc.addObject("App::DocumentObjectGroup", "HandV2")

# Part names → (x, y, z) position in mm (FreeCAD uses mm by default)
# Coordinate system: X=forward(palm direction), Y=left/right, Z=up
POSITIONS = {
    # Wrist adapter
    "hand_adapter_link":      (0,     0,    0),
    # Palm: centered at X=65mm from adapter, Z=20mm (palm thickness center)
    "hand_palm_link":         (65,    0,    20),
    # Thumb (on -Y side, angled slightly)
    "thumb_base_link":        (115,   -35,  20),
    "thumb_P_link":           (115,   -35,  55),
    "thumb_D_link":           (135,   -35,  80),
    # Fingers (on +Y side, positioned along palm front edge)
    "index_K_link":           (130,   -20,  20),
    "index_P_link":           (130,   -20,  52),
    "index_M_link":           (130,   -20,  82),
    "index_D_link":           (130,   -20,  106),
    "middle_K_link":          (130,   -6,   20),
    "middle_P_link":          (130,   -6,   54),
    "middle_M_link":          (130,   -6,   86),
    "middle_D_link":          (130,   -6,   112),
    "ring_K_link":            (130,   8,    20),
    "ring_P_link":            (130,   8,    52),
    "ring_M_link":            (130,   8,    82),
    "ring_D_link":            (130,   8,    104),
    "little_K_link":          (130,   22,   20),
    "little_P_link":          (130,   22,   48),
    "little_M_link":          (130,   22,   74),
    "little_D_link":          (130,   22,   94),
}

stl_files = sorted(f for f in os.listdir(MESH_DIR) if f.endswith(".stl"))
print(f"Loading {len(stl_files)} STLs...")

loaded = 0
for fname in stl_files:
    path = os.path.join(MESH_DIR, fname)
    name = os.path.splitext(fname)[0]
    try:
        mesh_obj = doc.addObject("Mesh::Feature", name)
        mesh = Mesh.Mesh(path)
        mesh_obj.Mesh = mesh
        grp.addObject(mesh_obj)
        # Position
        if name in POSITIONS:
            px, py, pz = POSITIONS[name]
            mesh_obj.Placement = FreeCAD.Placement(
                FreeCAD.Vector(px, py, pz), FreeCAD.Rotation())
        loaded += 1
        print(f"  OK: {name}")
    except Exception as e:
        print(f"  FAIL: {name}: {e}")

doc.recompute()
doc.saveAs(OUT)
print(f"\nSaved: {OUT} ({loaded}/{len(stl_files)} meshes)")
