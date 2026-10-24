# vendor/ — drop downloaded COTS CAD here

This folder is git-ignored. Put vendor `.step` / `.stp` files and datasheets
here, mirroring the layout below, so the FreeCAD rebuild can reference them.

```
vendor/
  actuators/     STS3215.step | XL330-M288-T.stp | XC330.stp
  bearings/      683ZZ.step  684ZZ.step  685ZZ.step  608ZZ.step
  fasteners/     M2x8_SHCS.step  M3x12_SHCS.step  ...
  electronics/   URT1.pdf  U2D2.pdf  PSU.pdf
  reference/     LEAP/  DexHand/  OpenHandT42/
```

Rules:
- Prefer STEP over STL for anything that gets mounted.
- Keep only shell + mounting holes + output shaft; delete internal windings,
  rotors, screws.
- If no STEP exists, put the dimensioned drawing PDF in the same folder.
- Never commit this folder; it is large and vendor-licensed.

See `../V2_REAL_HAND_PLAN.md` for the full shopping list.
