# McMaster-Carr cheat sheet (hand v2)

## First: you do **not** need to buy anything from McMaster to continue

For the CAD rebuild I need exactly **one vendor file**:

| # | Part | Why | Where |
|---|------|-----|-------|
| 1 | Motor (STS3215 **or** XL330-M288-T) | palm + forearm envelope | §3 of `V2_REAL_HAND_PLAN.md` |
| 2 | Servo horn / output spline (25T or H101) | tendon spool interface | usually included with the motor |

**Bearings are no longer a download.** 683ZZ and 608ZZ are simple annuli; I
model them in FreeCAD from `ID × OD × width`. Same for M2/M3 screws, dowel
pins, springs, PTFE tube, inserts and silicone. Do not shop for any of those
yet — this is a later, separate purchase.

---

## Why McMaster feels impossible

It is a **filter catalog**, not a search catalog. 595,000 SKUs, and the search
box is keyword-based, so "bearing" returns thousands of rows. Two rules fix it:

1. **Type the trade number or the full size, never the generic word.**
   `683ZZ` · `M3 x 12 socket head` · `heat-set insert M3` · `PTFE tube 2mm`
2. **Then use the left rail, in this order:**
   `System of Measurement` → `primary size` → `secondary size` → `material` / `finish`.
   Stop when the result count at the top is **1–3 rows**.

Ignore the "Brand" filter. McMaster is the brand; that filter is noise.

Part numbers are **per variant** (length, finish, pack size). A number copied
from a blog is only valid for that exact variant.

---

## Buy at McMaster (only where tolerance matters)

| # | Part | Search box | Filters → exact pick | Qty |
|---|------|-----------|----------------------|-----|
| 1 | Dowel pin Ø3 × 12 mm | `metric dowel pins` | Metric · 3 mm · 12 mm · 18-8 SS · standard (m6) · chamfered | 20 |
| 2 | Dowel pin Ø4 × 20 mm | `metric dowel pins` | Metric · 4 mm · 20 mm · 18-8 SS · standard (m6) | 10 |
| 3 | PTFE tube 2 mm OD × 1 mm ID | `PTFE tubing` | 1 mm ID · 2 mm OD · white · semi-rigid · 5 ft | 1 |
| 4 | Extension spring ~0.5 N/mm | `extension springs` | Metric · 3 mm OD · 0.4 mm wire · 15 mm free length · rate nearest 0.5 N/mm | 12 |
| 5 | Heat-set insert M2 | `heat-set inserts` | For plastic · heat installed · M2 · 4 mm long | 50 |
| 6 | Heat-set insert M3 | `heat-set inserts` | For plastic · heat installed · M3 · 5.7 mm long | 50 |
| 7 | Shaft collar Ø3 / Ø4 | `shaft collars` | 3 mm bore · one-piece clamp · ~8 mm OD | 10 |
| 8 | Silicone sheet 1 mm, 30A | `silicone rubber sheets` | 1 mm thick · 30A durometer · 300 × 300 mm | 1 |

**Dowel pin tolerance:** "standard" metric dowel pins are m6 (slightly
oversize), which gives a light press into a 3.00 mm reamed/printed hole and a
secure fit in the bearing inner race. If you want a slip fit, pick
"undersized" instead.

---

## Do **not** buy at McMaster

| Item | McMaster reality | Buy instead |
|------|------------------|-------------|
| 683ZZ/684ZZ/685ZZ/608ZZ bearings | often $6–12 **each**; you need 44 | Amazon/AliExpress "miniature bearing assortment" 10-packs, ~$15 total |
| M2/M2.5/M3 socket screws | sold in boxes, one SKU per length, 6 lengths needed | 500-piece metric screw assortment kit, ~$20 |
| Springs | per-pack, expensive | spring assortment kit, ~$10 |
| Dyneema / Spectra tendon | not stocked as small braid | 30 lb braided fishing line, ~$8 |
| Silicone sheet | expensive | Amazon 1 mm silicone sheet, ~$10 |

You will spend ~$120 at McMaster for what costs ~$40 in kits, and you will
still be missing lengths.

---

## If you do want bearings at McMaster: don't

Their metric range literally skips the sizes a hand needs:

```
3×7×3  →  3×10×4  →  4×13×5  →  5×16×5  →  6×19×6 ...
```

- `683ZZ` (3×7×3) exists — around $5–6.
- `684ZZ` (4×9×4) — **not in the metric sealed range**.
- `685ZZ` (5×11×5) — **not in the metric sealed range**.
- `MR85ZZ` (5×8×2.5) — **not in the metric sealed range**.
- `608ZZ` (8×22×7) exists — around $18 each, sealed.

The metric sealed list ends at 3×10×4 as its smallest, and the shielded list is
limited too. Don't hunt for the missing sizes; the kit is cheaper either way.

| Bearing | Size | Qty | Search term |
|---------|------|-----|-------------|
| 683ZZ | 3 × 7 × 3 mm, shielded | 30 | `683ZZ bearing 30pcs` |
| 608ZZ | 8 × 22 × 7 mm, shielded | 4 | `608ZZ bearing 10pcs` |

---

## Verified McMaster numbers (public Yale OpenHand BOM)

These numbers are real and resolve on McMaster. They are **imperial**, so use
them only if you switch the design to imperial pins/screws — or as sanity
anchors for the category and variant layout.

| Part | McMaster # |
|------|-----------|
| M2 × 5 mm socket head cap screw | 91290A012 |
| M2.5 × 8 mm socket head cap screw | 91292A012 |
| M2.5 × 5 mm socket head cap screw | 92290A055 |
| Ø1/8" × 1-1/4" steel dowel pin | 98381A477 |
| Ø1/8" × 5/8" steel dowel pin | 98381A472 |
| Ø1/4" × 1-1/4" steel dowel pin | 98381A544 |
| Ø1/4" × 1-3/4" steel dowel pin | 98381A548 |
| 4-40 heat-set insert | 93365A120 |
| Extension spring, 0.188" OD × 3/4" × 0.016" wire | 9654K955 |
| Torsion spring, 0.340" OD × 0.028" wire | 9271K605 |
| Nylon pulley, 3/8" OD × 1/8" wide | 3434T31 |

The M2/M2.5 families above are the right anchor if you want metric screws:
open `https://www.mcmaster.com/91290A012/` and change the length in the table —
the part number updates per length. Same for `91292A012`.

---

## Shipping note

McMaster ships mainly in the US/Canada and selected international destinations.
If it will not ship to you, nothing in this design depends on McMaster: any
bearing with the **same ID × OD × width** works (the trade number `683ZZ` is an
international standard). Buy the kits locally/AliExpress and download the STEP
from the bearing maker or from McMaster's public CAD page.

---

## What to send me now

Drop this in `freecad_hand_7dof/vendor/`:

```
vendor/
  actuators/   <motor>.step        ← the only file I need
```

If the STEP will not download, a screenshot of the **dimensioned drawing**
(any view showing length × width × height and the output shaft) in the same
folder is enough. Then I can start the V2 palm and finger geometry.

For reference, here is the size cross-reference so the names stop blurring:

| Trade name | ID × OD × width | Common use |
|------------|-----------------|------------|
| 683ZZ | 3 × 7 × 3 mm | finger joints (our main bearing) |
| 684ZZ | 4 × 9 × 4 mm | not used — McMaster doesn't stock it |
| 685ZZ | 5 × 11 × 5 mm | not used |
| MR85ZZ | 5 × 8 × 2.5 mm | not used |
| 608ZZ | 8 × 22 × 7 mm | wrist / spool shaft |
