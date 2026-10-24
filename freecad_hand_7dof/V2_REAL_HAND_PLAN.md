# V2 — Real anthropomorphic 7-actuator hand (shopping + CAD request list)

This replaces the v1 "boxes and cylinders on a stack of motor links" model.
Nothing here is code yet — it is the **parts / CAD list I need from you** before
I rebuild the FreeCAD + URDF model.

---

## 1. What is actually wrong with v1

| # | Problem | Consequence |
|---|---------|-------------|
| 1 | 5 of the 7 DOF are wrist yaw/pitch/roll; only 2 are fingers | It is a parallel gripper on a 3-DOF wrist, not a hand |
| 2 | Chain is `link → motor_link → gearbox_link → joint` on every joint | 7 motors + 7 gearboxes in series ≈ 300 mm long, 21 links, looks like stacked cylinders |
| 3 | Fingers are 30×20×80 mm boxes standing on the knuckle at x=105 | No phalanges, no joints, wrong direction |
| 4 | Palm 120×100×18 mm / 250 g, finger 80 g | Too heavy and too big for a hand; distal inertia is huge |
| 5 | Every `<inertia>` is `1e-4` / `2e-5` placeholder | Gazebo/MuJoCo dynamics are meaningless |
| 6 | Mesh units inconsistent: `build_meshes.py` writes **metres**, URDF applies `scale=0.001` (expects **mm**) | Re-running the documented build makes the hand 1000× too small |
| 7 | `<transmission>` uses ROS 1 `hardware_interface/PositionJointInterface` | Ignored by ROS 2 / ros2_control |
| 8 | Gazebo plugin `libgazebo_ros_joint_position_controller.so` + 7 plugins with the same `name` | Gazebo Classic plugin, invalid in gz-sim; duplicate plugin names |

**V2 fixes all 8**: real hand kinematics, motors moved into a forearm pod and
tendon-coupled to the fingers, computed inertia, correct ROS 2 control blocks.

---

## 2. V2 target: 7 actuators, 5 fingers, 17 joints

```
                      ┌──────────── palm (fixed to Fetch wrist) ────────────┐
 thumb: CMC-oppose ── CMC-flex ── MCP ── IP          (A1, A2)
 index:  MCP-flex ── PIP ── DIP                       (A3)
 middle: MCP-flex ── PIP ── DIP                       (A4)
 ring:   MCP-flex ── PIP ── DIP                       (A5)
 little: MCP-flex ── PIP ── DIP                       (A6)
 palm arch / index abduction                          (A7)
```

| Actuator | Drives | Kinematic joints | Notes |
|----------|--------|------------------|-------|
| A1 | thumb opposition | CMC ab/ad | separate axis, gives tripod pinch |
| A2 | thumb flexion | CMC flex + MCP + IP | underactuated tendon |
| A3 | index | MCP + PIP + DIP | underactuated, spring return |
| A4 | middle | MCP + PIP + DIP | underactuated, spring return |
| A5 | ring | MCP + PIP + DIP | underactuated, spring return |
| A6 | little | MCP + PIP + DIP | underactuated, spring return |
| A7 | palm arch / index abduction | 1 | makes the palm conform, helps wide grasps |

- **7 independent actuators = "7 DOF"**, 17 physical joints (standard
  underactuated-hand definition, same as Yale OpenHand / DexHand).
- Motors live in a **forearm pod behind the wrist**, not in the fingers:
  hand itself ≈ 350–450 g, pod ≈ 400–500 g.
- Fingers: 3D-printed phalanges, Ø3 mm dowel + **683ZZ** bearings (one size
  everywhere), Dyneema tendon on the palm side, extension springs for return.
- Thumb: 2 driven axes + 1 coupled, opposed to the fingers.
- Direct bolt-on to `wrist_roll_link` at the existing `gripper_axis` origin
  (0.16645 0 0), same as v1, so the arm URDF is unchanged.

If the rubric demands **7 independently position-controlled joints** instead of
7 actuators, say so — then the design becomes 1 wrist yaw + 6 finger joints and
the hand is less anthropomorphic. This is the main decision I need from you.

---

## 3. Actuator choice (pick one)

| | Feetech STS3215 | Dynamixel XL330-M288-T | Dynamixel XC330-T288-T |
|---|---|---|---|
| Voltage | 12 V | 5 V | 12 V |
| Stall / rated torque | 2.94 / 0.98 N·m | 0.52 / ~0.10 N·m | ~0.65 N·m |
| Mass / size | 55 g, 45.2×24.7×35 mm | 18 g, 20×34×26 mm | 28 g, same case |
| Feedback | pos, speed, load, V, T | pos, vel, **current**, V, T | same |
| Control | TTL half-duplex UART | TTL, ROS 2-native | TTL, ROS 2-native |
| Price (approx) | $15–20 AliExpress, $31 RobotShop | $23.90 Robotis | ~$90 |
| Official STEP | ✗ (GrabCAD / model envelope) | ✓ Robotis download | ✓ same file |
| Verdict | **best torque per $, best for a strong hand** | **best integration + compact, weaker** | strong + compact, expensive |

**My recommendation:** 7× **STS3215** for the hand + 1× **STS3215** spare, and
model the envelope from the drawing (45.2 × 24.7 × 35 mm, 25T/Ø5.9 mm horn).
If you want an all-Dynamixel, ROS 2-native build with official CAD, take
7× **XL330-M288-T**.

Torque sanity check (6 mm tendon spool):
- STS3215: 2.94 N·m stall → ~490 N tendon → ~20–30 N fingertip at stall.
- XL330: 0.52 N·m stall → ~86 N tendon → ~5–6 N fingertip at stall.
A power grasp of a 1 kg bottle needs ~10–15 N per finger, so STS3215 is the
safer choice.

### Why not the industrial servos on McMaster?

The "DC Servomotors" aisle (NEMA 23/34, part numbers like `5082N11`,
`5151N111`) is **CNC/industrial automation**, not robotics. Those are *bare
motors + a separate drive*:

| | NEMA 23 `5082N11` | Feetech STS3215 |
|---|---|---|
| Peak / continuous torque | 1.13 / 0.35 N·m | **2.94 / 0.98 N·m** |
| Voltage | 340 V DC | 12 V |
| Mass | ~1 kg (frame class) | **55 g** |
| Driver | external, $1,013.88 | integrated |
| Cords | $434.52 + $212.15 | included |
| Cost per joint | **~$3,239** | **~$16** |
| 7 joints | ~$22,700, ~7 kg | ~$112, ~0.4 kg |

The $16 servo has ~2.6× the peak torque, 2.8× the continuous torque, 1/18 the
mass and 1/200 the cost. A NEMA 23 hand would also exceed the Fetch arm's
payload before it gripped anything. **Nothing in this build comes from
McMaster's motor aisle.** McMaster is for pins, tubing, inserts and springs.

### Controller / power (buy with the motors)

| For | Part | Qty | Approx |
|-----|------|-----|--------|
| STS3215 | Feetech **URT-1** USB-TTL adapter (or Waveshare Bus Servo Adapter A) | 1 | $8–15 |
| STS3215 | 12 V 10 A DC supply, XT30/XT60 | 1 | $20 |
| XL330 | Robotis **U2D2** | 1 | $32 |
| XL330 | Robotis **Power Hub** + XT30 pigtail, or DIY harness | 1 | $19+$9 |
| XL330 | 5 V 10 A supply | 1 | $20 |
| Both | JST EH 3-pin cables (spare), USB-C cable | 10 | $15 |

---

## 4. Full BOM

### 4.1 Actuation
| Item | Qty | Where | Notes |
|------|-----|-------|-------|
| STS3215 servo (or XL330-M288-T) | 7 + 1 spare | Feetech / AliExpress / Robotis | see §3 |
| Servo horns (25T) + M3 screws | 8 | with servo | tendon spool bolts to horn |
| URT-1 / U2D2 + power hub | 1 | Feetech / Robotis | |

### 4.2 Bearings & pins (finger joints)
| Item | Size | Qty | Where |
|------|------|-----|-------|
| Ball bearing 683ZZ | 3×7×3 mm | 30 | every finger joint (MCP/PIP/DIP/thumb) — one 30-pack |
| Ball bearing 608ZZ | 8×22×7 mm | 4 | wrist adapter + tendon spool shaft — one 10-pack |

> **Do not buy 684ZZ (4×9×4), 685ZZ (5×11×5) or MR85ZZ (5×8×2.5).**
> McMaster's metric **sealed** range jumps 3×7×3 → 3×10×4 → 4×13×5 → 5×16×5
> and does not carry those three. Even if a shielded variant exists elsewhere,
> a 30-pack of 683ZZ costs less than two McMaster bearings. The design uses
> **683ZZ everywhere** plus **608ZZ** at the wrist, so two packs cover the hand.
| Dowel pin Ø3 × 12/16 mm | | 20 | McMaster 98381A… family |
| Dowel pin Ø4 × 20 mm | | 10 | |
| Shaft collar Ø3 / Ø4 | | 10 | tendon pulleys |

### 4.3 Fasteners
| Item | Qty | Notes |
|------|-----|-------|
| M2×4 / 6 / 8 / 10 SHCS | 100 each | servo horns, phalanges |
| M2.5×6 / 8 SHCS | 50 each | |
| M3×8 / 12 / 16 SHCS | 50 each | palm, adapter, forearm |
| M2 / M3 heat-set inserts (ruthex or generic) | 50 each | printed parts |
| M2 / M3 washers | 100 each | |

### 4.4 Transmission & soft parts
| Item | Spec | Qty | Notes |
|------|------|-----|-------|
| Dyneema / Spectra braid | 0.6–0.8 mm, 25–40 lb | 30 m | **not** nylon; low stretch |
| PTFE tube | 2 mm OD × 1 mm ID | 2 m | tendon guide, forearm → finger |
| Extension spring | ~0.5 N/mm, 3×10×15 mm | 12 | finger return |
| Torsion spring (optional) | 0.34 in OD | 6 | alternative return |
| Silicone sheet 1–2 mm (Shore 30A) | 100×100 mm | 2 | fingertip pads |
| TPU 95A filament | 250 g | 1 | soft pads / cable guides |
| PETG / PA-CF filament | 1 kg | 1 | structural phalanges |

### 4.5 Optional sensing (recommended for the "real" demo)
| Item | Qty | Why |
|------|-----|-----|
| FSR402 or RP-C7.6 force sensor | 5 | fingertip contact |
| AS5600 magnetic encoder + Ø6 diametric magnet | 5 | only if you use raw DC motors |
| BNO085 IMU | 1 | palm orientation |
| INA226 current monitor | 1 | grasp force from motor current |

---

## 5. Reference designs to download (read before we model)

These are **references**, not files to copy into the repo. Licenses differ.

1. **LEAP Hand v1** — 16 DOF, 4 fingers, 16× XL330/XC330, STL + STEP + full BOM.
   <https://v1.leaphand.com/leap_cad> · <https://v1.leaphand.com/parts>
   Best reference for Dynamixel finger joints and brackets. CC BY-NC-SA.
2. **DexHand v1** — 5 fingers, 16 micro servos, forearm, tendon routing, assembly
   videos, ~$300 BOM. <https://github.com/TheRobotStudio/V1.0-Dexhand>
   Best reference for a complete printable hand + forearm. CC BY-NC-SA.
3. **DexHand 021 URDF** — 19 DOF, MuJoCo-ready, clean joint names.
   <https://github.com/DexRobot/dexrobot_urdf>
4. **Yale OpenHand T42** — underactuated tendon fingers, STEP/STL, McMaster BOM.
   <https://github.com/grablab/openhand-hardware/tree/master/model%20t42>
   Best reference for the underactuation + return-spring layout.
5. **InMoov hand** — simplest tendon hand, huge community.
   <https://inmoov.fr/>

Download into `freecad_hand_7dof/vendor/reference/` (git-ignored).

---

## 6. Where to put the files you download

```
freecad_hand_7dof/vendor/
  actuators/     STS3215.step | XL330-M288-T.stp | XC330.stp
  bearings/      683ZZ.step  684ZZ.step  685ZZ.step  608ZZ.step
  fasteners/     M2x8_SHCS.step  M3x12_SHCS.step  ...
  electronics/   URT1.pdf  U2D2.pdf  PSU.pdf
  reference/     LEAP/  DexHand/  OpenHandT42/
```

If a part has no STEP, drop the **dimensioned drawing (PDF)** instead — I can
model the envelope from it. Do not drop full vendor assemblies with internal
windings; we only need shell + mounting holes + output shaft.

---

## 7. What happens after you send the files

1. I rebuild the palm + 5 fingers as real phalanges with joint pins, bearings,
   tendon channels and spring pockets in `hand_7dof_macro.FCMacro`.
2. I compute mass/CoM/inertia per link from material density (PETG/PLA/AL).
3. I export visual + convex collision meshes, and write a new
   `urdf/hand_7dof.urdf` with 7 actuated joints (17 kinematic joints) and
   `<ros2_control>` + gz-sim blocks that actually load.
4. I add a tendon/underactuation model (`mimic` joints + `armature`, `damping`,
   `friction`) so Gazebo/MuJoCo behaves like the real hand.
5. Only then do we print, assemble, and tune.
