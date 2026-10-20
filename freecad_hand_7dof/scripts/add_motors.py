#!/usr/bin/env python3
"""Add motor + gearbox links to hand joints in full.sdf."""
import re

SDF_PATH = "/tmp/hand_gz/full.sdf"

with open(SDF_PATH, "r") as f:
    sdf = f.read()

# Fix 1: base_link static
old = "    <link name='base_link'>\n      <inertial>"
new = "    <link name='base_link'>\n      <static>true</static>\n      <inertial>"
assert sdf.count(old) == 1
sdf = sdf.replace(old, new, 1)
print("[fix] base_link: added <static>true</static>")

# Fix 2: model-level self_collide=false
old = "  <model name='fetch_7dof'>\n    <link name='base_link'>"
new = "  <model name='fetch_7dof'>\n    <self_collide>false</self_collide>\n    <link name='base_link'>"
assert sdf.count(old) == 1
sdf = sdf.replace(old, new, 1)
print("[fix] model: added <self_collide>false</self_collide>")

MOTORS = [
    ("hand_yaw_joint",        "hand_yaw_motor_link",        "hand_yaw_gearbox_link",        10.0, 0.150, 0.0225, 0.030, 0.200, 0.025, 0.040),
    ("hand_pitch_joint",      "hand_pitch_motor_link",      "hand_pitch_gearbox_link",      10.0, 0.150, 0.0225, 0.030, 0.200, 0.025, 0.040),
    ("hand_roll_joint",       "hand_roll_motor_link",       "hand_roll_gearbox_link",        8.0, 0.080, 0.0160, 0.040, 0.120, 0.019, 0.035),
    ("knuckle_spread_L_joint","knuckle_spread_L_motor_link","knuckle_spread_L_gearbox_link",  6.0, 0.050, 0.0110, 0.030, 0.080, 0.014, 0.025),
    ("knuckle_spread_R_joint","knuckle_spread_R_motor_link","knuckle_spread_R_gearbox_link",  6.0, 0.050, 0.0110, 0.030, 0.080, 0.014, 0.025),
    ("finger_L_prismatic_joint","finger_L_motor_link","finger_L_gearbox_link",              12.0, 0.040, 0.0100, 0.030, 0.060, 0.014, 0.025),
    ("finger_R_prismatic_joint","finger_R_motor_link","finger_R_gearbox_link",              12.0, 0.040, 0.0100, 0.030, 0.060, 0.014, 0.025),
]

def cyl_inertia(mass, radius, height):
    ixx = mass * (3.0 * radius**2 + height**2) / 12.0
    izz = mass * radius**2 / 2.0
    return ixx, izz

for (joint_name, motor_link, gearbox_link, gear_ratio,
     motor_mass, motor_r, motor_h,
     gearbox_mass, gearbox_r, gearbox_h) in MOTORS:

    m = re.search(r"<joint name='%s' type='(\w+)'>.*?</joint>" % re.escape(joint_name), sdf, re.DOTALL)
    if not m:
        print("[warn] joint %s not found, skipping" % joint_name)
        continue
    joint_block = m.group(0)

    pose_match = re.search(r"<pose(?:\s+relative_to='([\w:]+)')?>([^<]+)</pose>", joint_block)
    parent_match = re.search(r"<parent>([\w:]+)</parent>", joint_block)
    child_match = re.search(r"<child>([\w:]+)</child>", joint_block)

    old_rel_to = pose_match.group(1) or parent_match.group(1)
    old_pose = pose_match.group(2).strip()
    old_parent = parent_match.group(1)
    old_child = child_match.group(1)

    m_ixx, m_izz = cyl_inertia(motor_mass, motor_r, motor_h)
    g_ixx, g_izz = cyl_inertia(gearbox_mass, gearbox_r, gearbox_h)

    def link_xml(name, pose_rel, pose_val, mass, ixx, izz, radius, height, color):
        return (
            "    <link name='" + name + "'>\n" +
            "      <pose relative_to='" + pose_rel + "'>" + pose_val + "</pose>\n" +
            "      <inertial>\n" +
            "        <pose>0 0 0 0 0 0</pose>\n" +
            "        <mass>" + str(mass) + "</mass>\n" +
            "        <inertia>\n" +
            "          <ixx>" + format(ixx, '.10f') + "</ixx>\n" +
            "          <ixy>0</ixy>\n" +
            "          <ixz>0</ixz>\n" +
            "          <iyy>" + format(ixx, '.10f') + "</iyy>\n" +
            "          <iyz>0</iyz>\n" +
            "          <izz>" + format(izz, '.10f') + "</izz>\n" +
            "        </inertia>\n" +
            "      </inertial>\n" +
            "      <collision name='" + name + "_collision'>\n" +
            "        <pose>0 0 0 0 0 0</pose>\n" +
            "        <geometry>\n" +
            "          <cylinder>\n" +
            "            <length>" + str(height) + "</length>\n" +
            "            <radius>" + str(radius) + "</radius>\n" +
            "          </cylinder>\n" +
            "        </geometry>\n" +
            "      </collision>\n" +
            "      <visual name='" + name + "_visual'>\n" +
            "        <pose>0 0 0 0 0 0</pose>\n" +
            "        <geometry>\n" +
            "          <cylinder>\n" +
            "            <length>" + str(height) + "</length>\n" +
            "            <radius>" + str(radius) + "</radius>\n" +
            "          </cylinder>\n" +
            "        </geometry>\n" +
            "        <material>\n" +
            "          <script>\n" +
            "            <name>Gazebo/" + color + "</name>\n" +
            "            <uri>file://media/materials/scripts/gazebo.material</uri>\n" +
            "          </script>\n" +
            "          <diffuse>0.2 0.2 0.2 1</diffuse>\n" +
            "          <ambient>0.2 0.2 0.2 1</ambient>\n" +
            "        </material>\n" +
            "      </visual>\n" +
            "    </link>\n"
        )

    motor_link_xml = link_xml(motor_link, old_rel_to, old_pose, motor_mass, m_ixx, m_izz, motor_r, motor_h, "DarkGray")
    gearbox_link_xml = link_xml(gearbox_link, motor_link, "0 0 0 0 0 0", gearbox_mass, g_ixx, g_izz, gearbox_r, gearbox_h, "Black")

    fixed_joint_motor_xml = (
        "    <joint name='" + motor_link + "_to_motor' type='fixed'>\n" +
        "      <pose>0 0 0 0 0 0</pose>\n" +
        "      <parent>" + old_parent + "</parent>\n" +
        "      <child>" + motor_link + "</child>\n" +
        "    </joint>\n"
    )

    fixed_joint_gear_xml = (
        "    <joint name='" + gearbox_link + "_to_gearbox' type='fixed'>\n" +
        "      <pose>0 0 0 0 0 0</pose>\n" +
        "      <parent>" + motor_link + "</parent>\n" +
        "      <child>" + gearbox_link + "</child>\n" +
        "    </joint>\n"
    )

    new_joint = joint_block.replace(
        pose_match.group(0),
        "<pose relative_to='" + gearbox_link + "'>0 0 0 0 0 0</pose>"
    )
    new_joint = new_joint.replace(
        "<parent>" + old_parent + "</parent>",
        "<parent>" + gearbox_link + "</parent>"
    )

    replacement = motor_link_xml + gearbox_link_xml + fixed_joint_motor_xml + fixed_joint_gear_xml + new_joint
    sdf = sdf.replace(joint_block, replacement, 1)
    print("[motor+gear] %s: motor=%s gearbox=%s ratio=%.1f" % (joint_name, motor_link, gearbox_link, gear_ratio))

with open(SDF_PATH, "w") as f:
    f.write(sdf)
print("Done.")