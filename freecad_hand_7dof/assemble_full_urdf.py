"""Merge fetch_7dof.urdf (arm) + hand_7dof.urdf (V2 hand) into fetch_7dof_with_hand.urdf.

V2 hand: 5-finger anthropomorphic hand with 7 actuated + 7 mimic joints (14 total).
Drops the stock gripper_link/fingers/grip_site (replaced by the V2 hand).
Keeps wrist_roll_link as the mount; appends all hand links and joints.
Re-running this script reproduces urdf/fetch_7dof_with_hand.urdf.
"""
import xml.etree.ElementTree as ET
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ARM = os.path.join(REPO, "fetch_7dof_description", "urdf", "fetch_7dof.urdf")
HAND = os.path.join(HERE, "urdf/hand_7dof.urdf")
OUT = os.path.join(HERE, "urdf/fetch_7dof_with_hand.urdf")

arm = ET.parse(ARM).getroot()
hand = ET.parse(HAND).getroot()

# Drop stock gripper
DROP_LINKS = {"gripper_link", "r_gripper_finger_link", "l_gripper_finger_link",
              "grip_site_link", "hand_mount_link"}
DROP_JOINTS = {"gripper_axis", "r_gripper_finger_joint", "l_gripper_finger_joint",
               "grip_site_joint", "hand_adapter_fixed_joint", "hand_mount_fixed"}
for link in list(arm.findall("link")):
    if link.get("name") in DROP_LINKS:
        arm.remove(link)
for j in list(arm.findall("joint")):
    if j.get("name") in DROP_JOINTS:
        arm.remove(j)
# stale sim blocks
for g in list(arm.findall("gazebo")):
    if g.get("reference") in {"gripper_link", "r_gripper_finger_link",
                                "l_gripper_finger_link"}:
        arm.remove(g)
ros2 = arm.find("ros2_control")
if ros2 is not None:
    for j in list(ros2.findall("joint")):
        if j.get("name") in {"r_gripper_finger_joint", "l_gripper_finger_joint"}:
            ros2.remove(j)

# Append all hand links and joints
for link in hand.findall("link"):
    arm.append(link)
for j in hand.findall("joint"):
    arm.append(j)

# Add gazebo friction + material tags for all hand links
HAND_LINKS = [
    "hand_adapter_link", "hand_palm_link", "hand_pod_link",
    "thumb_base_link", "thumb_P_link", "thumb_D_link",
    "index_K_link", "index_P_link", "index_M_link", "index_D_link",
    "middle_K_link", "middle_P_link", "middle_M_link", "middle_D_link",
    "ring_K_link",  "ring_P_link",  "ring_M_link",  "ring_D_link",
    "little_K_link","little_P_link","little_M_link","little_D_link",
]
HAND_MATERIALS = {
    "hand_adapter_link": "Gazebo/DarkGray",
    "hand_palm_link":    "Gazebo/White",
    "hand_pod_link":     "Gazebo/Black",
    "thumb_base_link":   "Gazebo/DarkGray",
    "thumb_P_link":      "Gazebo/White",
    "thumb_D_link":      "Gazebo/White",
}
for name in HAND_LINKS:
    g = ET.SubElement(arm, "gazebo", attrib={"reference": name})
    ET.SubElement(g, "mu1").text = "1.0"
    ET.SubElement(g, "mu2").text = "1.0"
    mat = ET.SubElement(g, "material")
    mat.text = HAND_MATERIALS.get(name, "Gazebo/DarkGray")
    ET.SubElement(g, "selfCollide").text = "false"

# Merge ros2_control: add hand joints to existing controller or create new
HAND_ACTUATED_JOINTS = [
    "thumb_cmcmc_joint", "thumb_mcp_joint",
    "index_mcp_joint", "middle_mcp_joint",
    "ring_mcp_joint", "little_mcp_joint",
]
if ros2 is not None:
    # Check if hand controller already exists
    hand_ctrl = None
    for j in ros2.findall("joint"):
        pass  # just need ros2 block
    for joint_name in HAND_ACTUATED_JOINTS:
        existing = ros2.find(f".//joint[@name='{joint_name}']")
        if existing is None:
            j_elem = ET.SubElement(ros2, "joint", attrib={"name": joint_name})
            ci = ET.SubElement(j_elem, "command_interface", attrib={"name": "position"})
            ET.SubElement(ci, "param", attrib={"name": "min"}).text = "0.0"
            ET.SubElement(ci, "param", attrib={"name": "max"}).text = "1.5708"
            ET.SubElement(j_elem, "state_interface", attrib={"name": "position"})
            ET.SubElement(j_elem, "state_interface", attrib={"name": "velocity"})

ET.indent(arm, space="  ")
xml = ET.tostring(arm, encoding="unicode")
header = ("<!-- fetch_7dof_with_hand: stock Fetch 7-axis arm + V2 5-finger anthropomorphic hand.\n"
          "     Stock gripper removed; V2 hand has 7 actuated + 7 mimic joints (14 total).\n"
          "     Actuated: thumb_CMC, thumb_MCP, index/MCP/Ring/Little_MCP.\n"
          "     Mimic: PIP (0.85×MCP), DIP (0.6×PIP) per finger.\n"
          "     Meshes: package://freecad_hand_7dof/meshes/*.stl (scale=0.001 → m).\n"
          "     ros2_control in-URDF block for 7 actuated joints. -->\n")
with open(OUT, "w") as fh:
    fh.write('<?xml version="1.0"?>\n' + header + xml + "\n")
print("wrote", OUT)
t = ET.parse(OUT).getroot()
mov = [j for j in t.findall("joint") if j.get("type") in ("revolute", "prismatic", "continuous")]
print("movable joints:", len(mov), "=", [j.get("name") for j in mov])
