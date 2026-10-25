"""Generate hand_7dof.FCStd using FreeCAD's native API with anatomical positioning.
Run: freecad --console --macro freecad_hand_7dof/generate_fcstd.py
"""
import os
import FreeCAD
import Mesh

MESH_DIR = "/home/sword/Documents/Robotics/robotic_hand_7DOF/freecad_hand_7dof/meshes"
OUT = "/home/sword/Documents/Robotics/robotic_hand_7DOF/freecad_hand_7DOF/freecad_hand_7dof/hand_7dof.FCStd"
OUT = "/home/sword/Documents/Robotics/robotic_hand_7DOF/freecad_hand_7dof/hand_7dof.FCStd"

doc = FreeCAD.newDocument("HandV2")
grp = doc.addObject("App::DocumentObjectGroup", "HandV2")

# Coordinate system (mm): X=forward(palm length), Y=left/right, Z=up
# Palm surface is at Z=20 (palm plate is 18mm thick, sitting on Z=0→18)
# Fingers attach at X≈130 (palm front edge), Y varies per finger
# Curled pose: each phalanx Z increases to simulate flexion angle

POSITIONS = {
    # Adapter (wrist mount, behind palm)
    "hand_adapter_link": (0,     0,   20),

    # Palm plate (flat, extending from wrist)
    "hand_palm_link":    (65,    0,   20),

    # Thumb (on -Y side, opposing fingers — angled ~45° from palm)
    "thumb_base_link":   (110,  -45,  20),
    "thumb_P_link":      (100,  -55,  55),
    "thumb_D_link":      ( 85,  -62,  75),

    # Index finger (Y=-21, curled with fingers pointing up+back)
    "index_K_link":      (130,  -21,  20),
    "index_P_link":      (130,  -21,  50),
    "index_M_link":      (128,  -21,  80),
    "index_D_link":      (124,  -21,  100),

    # Middle finger (Y=-7, longest finger)
    "middle_K_link":     (130,   -7,  20),
    "middle_P_link":     (130,   -7,  55),
    "middle_M_link":     (128,   -7,  88),
    "middle_D_link":     (124,   -7,  110),

    # Ring finger (Y=7)
    "ring_K_link":       (130,    7,  20),
    "ring_P_link":       (130,    7,  50),
    "ring_M_link":       (128,    7,  78),
    "ring_D_link":       (124,    7,  98),

    # Little finger (Y=21, shortest)
    "little_K_link":     (130,   21,  20),
    "little_P_link":     (130,   21,  45),
    "little_M_link":     (128,   21,  68),
    "little_D_link":     (124,   21,  84),
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
