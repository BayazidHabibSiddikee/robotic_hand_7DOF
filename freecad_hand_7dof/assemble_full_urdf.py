"""Merge fetch_7dof.urdf (arm) + hand_7dof.urdf (hand) into fetch_7dof_with_hand.urdf.
Drops the stock gripper_link/fingers/grip_site (replaced by the hand),
keeps wrist_roll_link as the mount, appends the 8 hand joints, swaps the
stale gripper gazebo/ros2_control blocks for the 7-DOF hand versions.
Re-running this script reproduces urdf/fetch_7dof_with_hand.urdf.
"""
import xml.etree.ElementTree as ET
import os

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
# stale sim blocks for the removed gripper
for g in list(arm.findall("gazebo")):
    if g.get("reference") in {"gripper_link", "r_gripper_finger_link", "l_gripper_finger_link"}:
        arm.remove(g)
ros2 = arm.find("ros2_control")
if ros2 is not None:
    for j in list(ros2.findall("joint")):
        if j.get("name") in {"r_gripper_finger_joint", "l_gripper_finger_joint"}:
            ros2.remove(j)

for link in hand.findall("link"):
    arm.append(link)
for j in hand.findall("joint"):
    arm.append(j)

HAND_GAZEBO = ["hand_adapter_link", "hand_yaw_link", "hand_pitch_link",
               "hand_palm_link", "hand_knuckle_l_link", "hand_knuckle_r_link",
               "hand_finger_l_link", "hand_finger_r_link"]
HAND_LIMITS = {"hand_yaw_joint": ("-1.5708", "1.5708"),
               "hand_pitch_joint": ("-1.0472", "1.0472"),
               "hand_roll_joint": ("-0.6109", "0.6109"),
               "knuckle_spread_L_joint": ("0.0", "0.5236"),
               "knuckle_spread_R_joint": ("0.0", "0.5236"),
               "finger_L_prismatic_joint": ("0.0", "0.05"),
               "finger_R_prismatic_joint": ("0.0", "0.05")}
for name in HAND_GAZEBO:
    g = ET.SubElement(arm, "gazebo", attrib={"reference": name})
    ET.SubElement(g, "mu1").text = "1.0"
    ET.SubElement(g, "mu2").text = "1.0"
    ET.SubElement(g, "material").text = "Gazebo/White" if "yaw" in name or "pitch" in name or "palm" in name else "Gazebo/DarkGray"
if ros2 is not None:
    for name, (lo, hi) in HAND_LIMITS.items():
        j = ET.SubElement(ros2, "joint", attrib={"name": name})
        ci = ET.SubElement(j, "command_interface", attrib={"name": "position"})
        ET.SubElement(ci, "param", attrib={"name": "min"}).text = lo
        ET.SubElement(ci, "param", attrib={"name": "max"}).text = hi
        ET.SubElement(j, "state_interface", attrib={"name": "position"})
        ET.SubElement(j, "state_interface", attrib={"name": "velocity"})

ET.indent(arm, space="  ")
xml = ET.tostring(arm, encoding="unicode")
header = ("<!-- fetch_7dof_with_hand: stock Fetch 7-axis arm + 7-DOF FreeCAD hand (Option B).\n"
          "     Stock 2-finger gripper_link removed; hand mounts on wrist_roll_link.\n"
          "     NEW JOINTS: hand_yaw(H1), hand_pitch(H2), hand_roll(H3),\n"
          "     knuckle_spread_L/R(H4/H5), finger_L/R_prismatic(H6/H7, 0..0.05m).\n"
          "     Meshes: package://freecad_hand_7dof/meshes/*.stl + arm packages.\n"
          "     ros2_control in-URDF block + config/ros2_control.yaml both list H1..H7. -->\n")
with open(OUT, "w") as fh:
    fh.write('<?xml version="1.0"?>\n' + header + xml + "\n")
print("wrote", OUT)
t = ET.parse(OUT).getroot()
mov = [j for j in t.findall("joint") if j.get("type") in ("revolute", "prismatic", "continuous")]
print("movable joints:", len(mov), "=", [j.get("name") for j in mov])

