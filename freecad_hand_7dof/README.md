# 7-DOF Robotic Hand (FreeCAD) — mounts on Fetch wrist

Staged clone of https://github.com/BayazidHabibSiddikee/robotic_hand_7DOF
(`fetch_7dof_description/` = 7-axis Fetch-style arm + 2-finger parallel gripper).
This adds `freecad_hand_7dof/` = a **7-DOF hand** built to your choice:

> **Option B: keep Fetch 2-finger gripper + add 5 wrist/palm DOF = 7 total.**

## The 7 DOF

| # | Joint | Type | Axis | Limits | Purpose |
|---|-------|------|------|--------|---------|
| H1 | `hand_yaw_joint` | revolute | Z | ±90° | wrist yaw |
| H2 | `hand_pitch_joint` | revolute | Y | ±60° | wrist pitch |
| H3 | `hand_roll_joint` | revolute | X | ±35° | palm roll |
| H4 | `knuckle_spread_L_joint` | revolute | Z | 0–30° | left finger spread |
| H5 | `knuckle_spread_R_joint` | revolute | Z | 0–30° | right finger spread |
| H6 | `finger_L_prismatic_joint` | prismatic | −Y | 0–50 mm | left finger close (Fetch-compatible) |
| H7 | `finger_R_prismatic_joint` | prismatic | +Y | 0–50 mm | right finger close (Fetch-compatible) |

Mount: `hand_mount_fixed` bolts the adapter to the Fetch `wrist_roll_link`
at the stock `gripper_axis` origin (0.16645 0 0), so the original
`gripper_link` is replaced by this hand — no arm changes needed.

## Files

```
freecad_hand_7dof/
  hand_7dof_macro.FCMacro   # parametric FreeCAD macro (Part workbench) — THE FreeCAD build
  hand_7dof.FCStd           # native FreeCAD doc (opens directly, meshes as parts)
  build_meshes.py           # numpy-only STL generator -> meshes/
  make_fcstd.py             # packs meshes into hand_7dof.FCStd (no FreeCAD install needed)
  meshes/*.stl              # 6 collision/visual shells (fingers reuse Fetch boxes in URDF)
  urdf/hand_7dof.urdf       # hand-only URDF (7 DOF, validated)
  urdf/fetch_7dof_with_hand.urdf  # arm + hand combined (drop-in Gazebo replacement)
  assemble_full_urdf.py     # merges fetch_7dof.urdf + hand_7dof.urdf
```

## Open in FreeCAD (GUI)

FreeCAD is not installed on this box (no `apt` FreeCAD on Ubuntu 26.04,
no sudo here). Install one of:

```bash
sudo snap install freecad            # simplest on Ubuntu
# or
micromamba create -n cad -c conda-forge freecad && micromamba activate cad
```

Then:

1. Open `freecad_hand_7dof/hand_7dof.FCStd` — all 6 shells appear as parts.
2. Or Macro → Macros → paste `hand_7dof_macro.FCMacro` → Execute to rebuild
   parametrically (edit `PARAMS` for palm/finger sizes, re-export STL to `meshes/`).
3. STLs also slice directly (Cura/Prusa): palm 120×100×18 mm, fingers 30×20×80 mm.

## Regenerate

```bash
/home/bayazid/micromamba/envs/rosenv/bin/python freecad_hand_7dof/build_meshes.py
/home/bayazid/micromamba/envs/rosenv/bin/python freecad_hand_7dof/make_fcstd.py
/home/bayazid/micromamba/envs/rosenv/bin/python freecad_hand_7dof/assemble_full_urdf.py
```

## ROS 2 / Gazebo

`urdf/fetch_7dof_with_hand.urdf` = stock arm with the 2-finger `gripper_link`
replaced by the hand chain; `ros2_control.yaml` gains
`hand_position_controller` (H1–H5) while H6/H7 reuse the existing
`gripper_joint_trajectory_controller` limits (0–0.05 m).
Point your launch's `urdf_file` at it — clock/bridge setup is unchanged.
