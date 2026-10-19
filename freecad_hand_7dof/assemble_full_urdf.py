"""Merge fetch_7dof.urdf (arm) + hand_7dof.urdf (hand) into fetch_7dof_with_hand.urdf.
Drops the stock gripper_link/fingers/grip_site (replaced by the hand),
keeps wrist_roll_link as the mount, appends the 8 hand joints,
adds <mesh> search hint + hand ros2_control block as comment.
"""
import xml.etree.ElementTree as ET, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
ARM = "/home/bayazid/Documents/robotic_hand_7DOF/fetch_7dof_description/urdf/fetch_7dof.urdf"
HAND = os.path.join(HERE, "urdf/hand_7dof.urdf")
OUT = os.path.join(HERE, "urdf/fetch_7dof_with_hand.urdf")

arm = ET.parse(ARM).getroot()
hand = ET.parse(HAND).getroot()

DROP_LINKS = {"gripper_link", "r_gripper_finger_link", "l_gripper_finger_link", "grip_site_link"}
DROP_JOINTS = {"gripper_axis", "r_gripper_finger_joint", "l_gripper_finger_joint", "grip_site_joint"}
for link in list(arm.findall("link")):
    if link.get("name") in DROP_LINKS:
        arm.remove(link)
for j in list(arm.findall("joint")):
    if j.get("name") in DROP_JOINTS:
        arm.remove(j)
for link in hand.findall("link"):
    arm.append(link)
for j in hand.findall("joint"):
    if j.get("name") != "hand_mount_fixed":
        # keep mount too but re-parent is already wrist_roll_link; include it
        pass
    arm.append(j)

ET.indent(arm, space="  ")
xml = ET.tostring(arm, encoding="unicode")
header = ("<!-- fetch_7dof_with_hand: stock Fetch 7-axis arm + 7-DOF FreeCAD hand (Option B).\n"
          "     Stock 2-finger gripper_link removed; hand mounts on wrist_roll_link.\n"
          "     NEW JOINTS: hand_yaw(H1), hand_pitch(H2), hand_roll(H3),\n"
          "     knuckle_spread_L/R(H4/H5), finger_L/R_prismatic(H6/H7, 0..0.05m).\n"
          "     Meshes: package://freecad_hand_7dof/meshes/*.stl + arm packages.\n"
          "     ros2_control: extend config with hand_position_controller on H1..H5;\n"
          "     H6/H7 reuse gripper_joint_trajectory_controller limits. -->\n")
with open(OUT, "w") as fh:
    fh.write('<?xml version="1.0"?>\n' + header + xml + "\n")
print("wrote", OUT)
# quick count
t = ET.parse(OUT).getroot()
mov = [j for j in t.findall("joint") if j.get("type") in ("revolute", "prismatic", "continuous")]
print("movable joints:", len(mov), "=", [j.get("name") for j in mov])
