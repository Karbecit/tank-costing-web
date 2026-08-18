# UI parity with Tank Costing v9.0.0

**v9 reference:** `C:\Projects\Tank Costing\App screen shots.docx` (17 desktop captures with section labels and UX notes; single quote throughout).

**Web reference:** `C:\Projects\Tank Costing\Website pages.docx` (4 web captures — Summary, Cones, Strakes ×2; same *Ladbroke Grove Wines 35kl…* cone/strake data entered manually; Summary tab still at defaults).

**Secondary v9 reference:** `C:\Projects\Tank Costing\Screen captures.docx` (12 v9 captures, mixed sample jobs — superseded for flow but retains Volume & Height report preview capture).

**Sample quote (all screenshots):** *Ladbroke Grove Wines — 35kl storage tank 3050diam 4800wall 316 stst* (`C:\Projects\Tank Costing\Ladbroke Grove Wines 35kl storage tank 3050diam 4800wall 316 stst 14-7-09.jma`; 6 tanks; Client rep Mark Johnson; Originator Andy Moldovan).

Legacy baseline for calculations and layout: `Old Program\Instal_6_2_1\TankCosting_6_2_1\` (8.2.1 source, closest to v9).

**New-doc flow:** One consistent quote walked screen-by-screen (Summary → Cones variants → Strakes → Components → tools/modals). Cleaner than the old mixed-job doc; adds cone-type detail, coil-picker context, and Multi Floor Sheets; omits Volume & Height report preview.

---

## Implementation order

1. Summary dashboard + gross profit (daily workflow)
2. Cones/Strakes calculated fields, coil picker, volume/height dropdowns, Volumes & Heights footer
3. Components dual-grid
4. Qty Coil Used, Multi Floor Sheets, Combo Tank, report previews
5. Pre-Set Values, Change Diameter, metadata polish

---

## High — daily costing workflow

| # | v9 screen | Gap | Web files / API |
|---|-----------|-----|-----------------|
| 1 | Main Summary | Single-screen dashboard: coil steel, volumes (@24°C/@4°C), components, labour grid, single/multi tank pricing, gross profit | `frontend/src/costing/app.js` (`renderSummary`, `renderTotals`); merge into one view |
| 2 | Main Summary | **Gross profit** $ and % (Sep 2022 formula) | `backend/app/calc/summary.py`; display in `renderTotals` / Summary |
| 3 | Main Summary | Add-on cost lines (Delivery FOT Berri, Tank Drawings, etc.) — single and multi tank | Data: `single_add_on`, `multi_add_on` in `state.js`, `schemas/costing.py`; **no UI** in `bindSummary` |
| 4 | Main Summary | Labour breakdown: hours/$ by Cones, Strakes, Components, Misc | Backend has `lab_cones_*`, `lab_strakes_*` in totals; not shown in UI |
| 5 | Main Summary | Coil steel subtotals: Cones/Floor, Strakes/Cavity, Misc, markup %, steel total | `renderTotals` shows aggregate steel only |
| 6 | Cones / Strakes | **Select Coil** picker (sheet steel grid: Grade, Thickness, Width, Price/kg) per row | `grade` in model; no picker in `renderCone` / `renderStrake` |
| 7 | Cones | **Cone geometry type:** Conical / Offset / Slope toggles change visible fields and calculations; Conical & Slope allow Height **or** Angle entry (other auto-adjusts) | Type **dropdown** + conditional fields in `renderCone`; height↔angle via checkbox — **no radio toggles**, no auto-recalc coupling |
| 8 | Cones / Strakes | **Volume/height treatment dropdown** per row (cone options include “within barrel (Combo)”; strake options include “Cavity wrap”) | **Implemented** (`VOLUME_TREAT_LABELS`, per-row select in `renderCone` / `renderStrake`); verify all 8 options match v9 labels |
| 9 | Components | Stock browse grid + tank components grid; hours, orientation, stock #; add/delete rows | `renderComponents` — search + list only |
| 10 | Cones / Strakes | Inline calculated fields: coil length, area, weight, price, hours | Partial (vol/height/steel on cones; minimal on strakes) |
| 11 | Cones / Strakes | **Volumes & Heights** footer grid (strake volumes, cone volumes, barrel/fluid heights) | Not present |

### Gross profit formula (v9 / 8.2.1)

From `Instal_6_2_1\...\Summary.bas`:

```
IntTot = ((PriceQuoted - SingleTankLessGST) + LabourTot + CompMarkupAmt) * NumTanks
         + (SteelMarkUpAmount * NumTanks)
GpPercent = (100 / (PriceQuoted * NumTanks)) * IntTot   [when PriceQuoted > 0]
```

Port to `backend/app/calc/summary.py` and expose on calculate response.

---

## Medium — sub-screens and tools

| # | v9 screen (doc image) | Gap | Likely location |
|---|----------------------|-----|-----------------|
| 12 | Summary + Qty Coil Used | Steel roll usage table (single + batch) | New modal + calc/report module |
| 13 | Summary + Multi Floor Sheets | **Additional coil / floor sheets** (Cones & Floors menu); up to 6 extra coil rows with Select coil | New modal; not previously indexed |
| 14 | Summary + Combo Tank | Combo volume modal; prerequisite for full dip chart | New modal; `backend/app/calc/dip_chart.py` (single-tank only today) |
| 15 | Summary + Dip Chart | Excel / text file export; Single vs Combo tank toggle; increment size | `renderPanel` dip tab; new export endpoints |
| 16 | Summary + Change Diameter | Recalc circumference/area from new diameter | New tool on Summary |
| 17 | Summary + Pre-Set Values | Default markups, GST, labour, cone/strake names, add-on labels, temp compensation, screen/text size | Admin or app settings; `settings_store.py` |
| 18 | Main Summary | Client rep, Contact date, Originator, Checked by, Costing Status, Record of Changes | `schemas/costing.py`, `bindSummary` |
| 19 | Report preview | Volume & Height, Coil Steel, Components, Labour, Combo Tank reports | Beyond PDF quote (`pdf_service.py`); **only in old doc** |
| 20 | Main Summary | Total volume @ 24°C and @ 4°C | `temperature_correction_factor` in `summary.py`; not in UI |
| 21 | Main Summary | Full multi-tank panel (batch totals, multi add-ons) | `num_tanks` input exists; panel incomplete |

---

## Low — polish

| # | Gap | Notes |
|---|-----|-------|
| 22 | Tab navigation vs v9 menu + Return to Summary | Acceptable web pattern; optional layout pass |
| 23 | Red “Not Saved” / green “File Saved” indicator | Status line only today |
| 24 | Last saved footer (date/time/user/computer) | Server save message only |
| 25 | SandBuildup, skirt, intermediate cone naming, max/min angle | `sand_height` in model; partial cone rows |
| 26 | Non-stock components text area on Summary | Not present |
| 27 | Information density | v9 is one dense window; web is sparse tabs — largest perceived gap |

---

## Screenshot index (`App screen shots.docx`)

All from *Ladbroke Grove Wines 35kl…* unless noted. Doc section labels in **bold**; screen title from app window where different.

| # | Doc label | Screen | Type | Key fields / notes |
|---|-----------|--------|------|-------------------|
| 1 | **Summary** | Main Summary | Base | Company, rep, originator, coil steel breakdown, volumes @24°C/@4°C, labour, components, add-ons, single/multi pricing, gross profit 11.78%, menu bar |
| 2 | **Cones** | Tops & Bottoms (Cones) | Base | Top cone (Offset), bottom floor (Slope), inline calc columns, Volumes & Heights footer |
| 3 | **Conical** | Top cone row | Detail crop | Conical checked; Height/Angle, Diam Wide/Narrow, knuckle, Select Coil dropdown |
| 4 | **Offset** | Top cone row | Detail crop | Offset checked; Max/Min Angle, Offset field |
| 5 | **Slope** | Top cone row | Detail crop | Slope checked; Skirt, SandBuildup; Height or Angle entry |
| 6 | *(caption)* | Sheet steel selection | Modal | Grade/Thickness/Width/PriceKg grid; Accept/Close |
| 7 | *(caption)* | Cone volume/height dropdown | Control | 8 options (+/− Volume/Height, Combo within barrel, slope reduces barrel) |
| 8 | **Strakes** | Strakes | Base | 5 populated rows (316 + 304 cavity), Select Coil buttons, Volumes & Heights footer |
| 9 | *(caption)* | Sheet steel selection | Modal | Same picker from Strakes page |
| 10 | *(caption)* | Strake volume/height dropdown | Control | 8 options incl. Cavity wrap No volume, No Height |
| 11 | **Components** | Components | Base | Stock grid + Tank Components grid; Add/Delete row; orientation, stock # |
| 12 | **Qty Coil Used** | Quantity of roll steel used | Modal | Single tank + 6 tanks tables (Grade, Length, Weight, Cost) |
| 13 | **Additional Coil (Floors)** | Multi Floor Sheets | Modal | Up to 6 extra coil rows; Select coil / Clear per row |
| 14 | **Setup Cones** *(doc label)* | Combo Tank Volume Calculation | Modal | Top/bottom tank cone selectors, swept arm, volume totals; Dip Chart button |
| 15 | **Dip chart calculation** | Dip Chart Calculation | Modal | Single/Combo toggle, component heights/volumes, dip table, Excel/text export |
| 16 | **Set Pre-Set values** | Set Pre-set values | Modal | Markups, GST, labour, cone/strake names, add-on labels, temp compensation |
| 17 | **Change Tank diameter** | Tank Diameter | Modal | Diameter → Circumferance & Area; shown at new-quote entry |

**Not in new doc (still in old `Screen captures.docx`):** Volume & Height report preview; standalone multi-cone/mixed-grades crop (partially covered by images 3–5).

---

## Web screenshot index (`Website pages.docx`)

385 KB; 4 images. Labels from `word/document.xml`. Cone/strake values match the Ladbroke Grove job; Summary tab shows default/new-job fields (not imported).

| # | Doc label | Tab | File | Key content |
|---|-----------|-----|------|-------------|
| 1 | **Summary** | Summary | `image1.png` | Job title “Untitled costing”, diam 3050, expan 450×300, markup 25%, GST 1.1, **num tanks 1**, components 0 — input form only; no steel/labour/pricing dashboard |
| 2 | **Cones** | Cones | `image2.png` | Cone 1 Top cone (**Offset**, angle 11°), Cone 4 Bottom floor (**Slope**, 2.5°, vol treat 7); Cones 2–3, 5 = None; volume-treatment dropdowns; inline Vol/Height/Steel after Calculate |
| 3 | **Strakes first half of page** | Strakes | `image3.png` | Strakes 1–3 used (1200 mm wide, 2 / 1.6 / 2 mm); coil length 9582; price/kg 6.5–6.6 |
| 4 | **Strakes, second half of page** | Strakes | `image4.png` | Strake 4 used; Strake 5 **Cavity Jacket** (900 mm, 0.8 mm, vol treat 8); Strakes 6–7 unused |

**UX note in doc:** *“Strakes and Cones instead of having multiple sections for each perhaps the user can add as necessary.”* — future layout consideration; not implemented.

---

## Side-by-side: Summary, Cones, Strakes

Same sample job where data was entered. **Gaps visible** = high-priority items obvious in the web screenshot (vs v9 image 1–2, 8 in `App screen shots.docx`).

### Summary

| Area | v9 (`App screen shots` #1) | Web (`Website pages` #1) | Gap # |
|------|---------------------------|--------------------------|-------|
| Layout | Single dense dashboard | Sparse input grid on Summary tab; totals on separate **Totals** tab | 1, 27 |
| Metadata | Company, Client rep, Originator, Contact date, Costing status | Job title, quote ref, customer combobox only | 18 |
| Coil steel | Cones/Floor, Strakes/Cavity, Misc, markup %, steel total | Not on Summary | 5 |
| Volumes | Total @ 24°C and @ 4°C | Not on Summary (basic volume on Totals tab only) | 20 |
| Labour | Hours/$ by Cones, Strakes, Components, Misc | Cones rate + misc hrs/rate inputs only; no breakdown | 4 |
| Components & add-ons | Component total; Delivery FOT, Drawings, etc. | Components price field (0 in screenshot); no add-on lines | 3 |
| Pricing | Single tank $18,850; multi × 6; gross profit **11.78%** | Price quoted field; no multi-tank panel; no gross profit | 2, 21 |
| Batch | **6 tanks** | **1 tank** in screenshot (JMA has 6) | 21 |

**Gaps visible in web screenshot:** 1, 2, 3, 4, 5, 18, 20, 21, 27.

### Cones

| Area | v9 (#2, 3–7) | Web (#2) | Gap # |
|------|--------------|----------|-------|
| Layout | Horizontal grid, one row per cone/floor | Vertical card per cone (all 5 slots always shown) | 27 |
| Active rows | Top cone Offset + bottom floor Slope | Same geometry/types and values | — |
| Type UI | Conical / Offset / Slope **radio toggles** | **Type dropdown**; fields show/hide by type | 7 (partial) |
| Select Coil | Button → sheet steel grid (Grade, Thk, Width, Price/kg) | Manual thick/width/price/kg; **no grade**, no picker | 6 |
| Inline calcs | Coil length, area, weight, price, hours columns | Vol, Height, Steel only (post-Calculate) | 10 (partial) |
| Volume treat | Per-row dropdown (8 options) | Per-row dropdown present (e.g. floor = “7: − Volume, no height”) | 8 ✓ |
| Footer | **Volumes & Heights** grid (strake/cone/barrel/fluid) | Absent | 11 |

**Gaps visible in web screenshot:** 6, 7 (partial), 10 (partial), 11, 27.

### Strakes

| Area | v9 (#8, 9–10) | Web (#3–4) | Gap # |
|------|---------------|------------|-------|
| Layout | Compact grid, 5 populated rows | 8 vertical cards; 5 used (incl. Cavity Jacket) | 27 |
| Select Coil | Per-row button + grade column | No picker; **no grade field** in UI | 6 |
| Cavity row | 304 cavity wrap; vol treat “Cavity wrap” | Strake 5 Cavity Jacket; vol treat **8: No volume, no height** | 8 ✓ |
| Inline calcs | Length, area, weight, price, hours | Vol, Steel only (post-Calculate) | 10 (partial) |
| Footer | **Volumes & Heights** grid | Absent | 11 |

**Gaps visible in web screenshot:** 6, 10 (partial), 11, 27.

---

## Validation

**Sample `.jma` path:** `C:\Projects\Tank Costing\Ladbroke Grove Wines 35kl storage tank 3050diam 4800wall 316 stst 14-7-09.jma` (20,996 bytes; parent of `tank-costing-web/`). Not copied into the repo — tests use `Old Program\Code\Costings\` for other samples; document this path for QA.

### JMA import / calculate (2026-07-26)

| Step | Result |
|------|--------|
| Cones / strakes parse (`load_jma_cones`, `load_jma_strakes`) | **OK** — diam 3050; top Offset + bottom Slope match screenshots |
| Full import (`jma_file_to_payload`, `/api/jma/parse`) | **OK** (fixed 2026-07-26) — v9 address/contact strings in early summary slots treated as 0 for numeric fields |
| Stored totals from file (`parse_summary_stored_totals`) | **OK** |
| Recalculate (cones + strakes + manual summary indices) | **OK** — matches stored totals (see below) |

**Key totals (stored in .jma = web recalc):**

| Metric | Value |
|--------|------:|
| Total volume (L) | 35,304.51 |
| Strakes volume (L) | 35,069.60 |
| Cones volume (L) | 187.20 |
| Cones steel ($) | 2,383.68 |
| Strakes steel ($) | 4,891.53 |
| Steel subtotal ($) | 7,275.22 |
| Steel markup ($) | 1,818.80 |
| Steel total ($) | 9,094.02 |
| Labour total ($) | 5,850.00 |
| Single tank ex GST ($) | 21,829.02 |
| Price quoted (6 tanks) | 18,850 |
| Num tanks | 6 |
| Components price ($) | 2,654 |

**Blocker for end-to-end QA:** resolved — use **Load .jma** with the sample path above for Summary/Cones/Strakes QA.

For each closed parity item:

1. Load sample `.jma` (path above) after import fix
2. Compare calculate output in v9 exe vs web API
3. Capture web screenshot and add to `Website pages.docx` or parity doc with label
