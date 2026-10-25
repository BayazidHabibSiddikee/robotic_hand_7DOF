import FreeCAD as App
import Part
import math

print("Starting arm build...")
doc = App.newDocument("arm_7dof")

# STEP 1: Base plate
print("Step 1: Base plate")
base_shape = Part.makeBox(80, 80, 10)
base_feat = doc.addObject("Part::Feature", "BasePlate")
base_feat.Shape = Part.Solid(base_shape)
base_feat.Placement = App.Placement(App.Vector(0, 0, -5), App.Rotation())
print("  Created BasePlate")

# STEP 2: Define joint chain
joints = [
    ("J1", 'Z', 50, 0),
    ("J2", 'Y', 45, 0),
    ("J3", 'Z', 75, 0),
    ("J4", 'Y', 75, 0),
    ("J5", 'Z', 65, 0),
    ("J6", 'Y', 65, 0),
    ("J7", 'Z', 45, 0),
]

current_pos = App.Vector(0, 0, 10)
current_rot = App.Rotation()

for name, axis, offset, rot_deg in joints:
    if axis == 'Z':
        joint_rot = App.Rotation(App.Vector(0, 0, 1), math.radians(rot_deg))
    else:
        joint_rot = App.Rotation(App.Vector(0, 1, 0), math.radians(rot_deg))
    
    current_rot = joint_rot * current_rot
    move_vec = current_rot.multVec(App.Vector(0, 0, offset))
    current_pos = current_pos + move_vec
    
    servo_shape = Part.makeBox(25, 37, 45)
    servo_feat = doc.addObject("Part::Feature", f"Servo_{name}")
    servo_feat.Shape = Part.Solid(servo_shape)
    servo_center = current_pos - current_rot.multVec(App.Vector(0, 0, 22.5))
    servo_feat.Placement = App.Placement(servo_center, current_rot)
    
    horn_shape = Part.makeCylinder(5, 10)
    horn_feat = doc.addObject("Part::Feature", f"Horn_{name}")
    horn_feat.Shape = Part.Solid(horn_shape)
    horn_pos = current_pos + current_rot.multVec(App.Vector(0, 0, 27.5))
    horn_feat.Placement = App.Placement(horn_pos, current_rot)
    
    print(f"  {name}: pos=({current_pos.x:.1f}, {current_pos.y:.1f}, {current_pos.z:.1f})")

end_shape = Part.makeBox(30, 30, 10)
end_feat = doc.addObject("Part::Feature", "EndEffector")
end_feat.Shape = Part.Solid(end_shape)
end_feat.Placement = App.Placement(current_pos, current_rot)

doc.saveAs("/tmp/arm_7dof.FCStd")
print(f"\nSaved to /tmp/arm_7dof.FCStd")
print(f"Total objects: {len(doc.Objects)}")
