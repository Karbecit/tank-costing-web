"""Write VB6 sequential .jma files from web costing payloads."""

from __future__ import annotations

import io
from datetime import date, datetime
from pathlib import Path
from typing import Any

from app.calc.costing import calculate_costing
from app.models.cone import Cone
from app.models.strake import Strake
from app.services.jma_service import payload_to_models

NUM_COMPONENTS = 50
COMP_FIELDS = 9
SUMMARY_FIELDS = 89
NUM_HEADINGS = 30


def _fmt(value: Any) -> str:
    if isinstance(value, bool):
        return "#TRUE#" if value else "#FALSE#"
    if isinstance(value, str):
        escaped = value.replace('"', '""')
        return f'"{escaped}"'
    if isinstance(value, datetime):
        return f"#{value.strftime('%Y-%m-%d %H:%M:%S')}#"
    if isinstance(value, date):
        return f"#{value.isoformat()}#"
    if value is None:
        return '""'
    if isinstance(value, float):
        return repr(float(value))
    return str(value)


def _cone_tokens(cone: Cone) -> list[Any]:
    return [
        cone.angle,
        cone.angle_select,
        cone.coil_length,
        cone.coil_volume,
        cone.conic_select,
        cone.diam_large,
        cone.diam_small,
        cone.grade,
        cone.height,
        cone.height_select,
        cone.knuck_add_height,
        cone.knuckle_red_width,
        cone.knuckle_rad,
        cone.knuck_vol,
        cone.lab_price,
        cone.length,
        cone.min_angle,
        cone.max_angle,
        cone.name,
        cone.num_hours,
        cone.offset_amt,
        cone.offset_select,
        cone.price_kg,
        cone.sand_height,
        cone.res_height,
        0,  # ResSkirtHeight
        cone.res_vol,
        cone.skirt,
        cone.skirt_vol,
        cone.slope_select,
        cone.steel_price,
        cone.surface_area,
        cone.tank_area,
        cone.thick,
        cone.volume,
        cone.volume_treat,
        cone.waste,
        cone.weight,
        cone.weight_cucm,
        cone.width,
    ]


def _strake_tokens(strake: Strake) -> list[Any]:
    return [
        strake.coil_length,
        strake.coil_volume,
        strake.grade,
        strake.height,
        strake.lab_price,
        strake.name,
        strake.num_hours,
        strake.num_iden_strakes,
        strake.price_kg,
        strake.rate_hour,
        strake.res_height,
        strake.resultant_width,
        strake.res_vol,
        strake.steel_price,
        strake.strake_area,
        strake.thick,
        strake.trim_strakes,
        strake.used,
        strake.volume,
        strake.volume_treat,
        strake.waste,
        strake.weight,
        strake.weight_cucm,
        strake.width,
    ]


def _empty_tail_tokens() -> list[Any]:
    tokens: list[Any] = []
    # Frep (15 + 62 survey pairs)
    tokens.extend([0, ""] + [""] * 13)
    for _ in range(NUM_HEADINGS + 1):
        tokens.extend(["", ""])
    # Per
    tokens.extend(["", "", "", ""])
    # StraPlot 0-7
    for _ in range(8):
        tokens.extend(["", 0, 0, 0, 0, 0])
    # Notes block
    tokens.extend([0, 0, "", "", "", "", "", 0, 0, 0, 0, 0])
    tokens.extend([0, 0, 0])
    # Contacts 0-3
    for _ in range(4):
        tokens.extend(["", "", "", "", ""])
    tokens.append(0)  # StraPlot(9).Used
    # Used 1-40
    for _ in range(40):
        tokens.extend(["", 0, 0, 0, 0, 0, 0, 0])
    tokens.append(0)  # FileLocked
    # Duplex + FState
    tokens.extend([22, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 10, 0, 0, 0, 0, 0])
    tokens.extend([0, 0, True])
    return tokens


def build_jma_tokens(
    payload: dict[str, Any],
    *,
    title: str,
    quote_ref: str | None = None,
    company_name: str = "",
) -> list[Any]:
    cones, strakes, summary, rate = payload_to_models(payload)
    result = calculate_costing(cones, strakes, summary, cones_rate_per_hour=rate)
    totals = result.totals
    calc_cones = result.cones
    calc_strakes = result.strakes

    tokens: list[Any] = []
    for cone in calc_cones:
        tokens.extend(_cone_tokens(cone))
    for strake in calc_strakes:
        tokens.extend(_strake_tokens(strake))

    s = summary
    summary_block: list[Any] = [
        "", "", "",  # Addontxt
        "", "",  # addresses
        s.floor_multi_tot,
        s.coil_mark_up_percent,
        s.coil_misc,
        s.comp[0], s.comp[1], s.comp[2], s.comp[3],
        company_name,
        totals.comp_markup_amt,
        s.comp_markup_percent,
        s.components_price,
        totals.comp_tot_inc_markup,
        len(payload.get("selected_components") or []),
        totals.cones_vol,
        totals.cone_total,
        s.diam,
        s.expan_diam,
        s.expan_height,
        totals.expan_vol,
        "",  # Fax
        s.gst,
        quote_ref or "",
        "",  # JMAClientRep
        "",  # JMAContactDate
        "",  # QuoteNote
        totals.lab_cones_amt,
        totals.lab_cones_hrs,
        s.lab_misc_hrs,
        s.lab_misc_rate,
        "",  # LabMiscText
        totals.lab_misc_tot,
        totals.labour_tot,
        totals.labour_tot,
        totals.lab_strakes_amt,
        totals.lab_strakes_hrs,
        totals.labour_tot,
        totals.lab_tot_hours,
        s.multi_add_on[0], s.multi_add_on[1], s.multi_add_on[2],
        "", "", "",  # MultiAddOntxt
        totals.multi_tanks_inc_gst,
        totals.multi_tanks_price,
        totals.multi_tanks_single,
        totals.multi_tanks_tot_less_gst,
        0, 0, 0, 0,  # NonStock
        s.num_tanks,
        s.other_vol,
        0,  # CostingStatus
        s.price_quoted,
        0,  # Protection
        totals.res_barrel_height,
        date.today(),
        datetime.now().replace(microsecond=0),
        s.single_add_on[0], s.single_add_on[1], s.single_add_on[2],
        totals.single_tank_comp,
        totals.single_tank_inc_gst,
        totals.single_tank_lab,
        totals.single_tank_less_gst,
        totals.single_tank_steel,
        NUM_COMPONENTS,
        0,  # SteelKgTotal placeholder
        totals.steel_mark_up_amount,
        totals.steel_sub_tot,
        totals.steel_total,
        totals.strakes_vol,
        totals.strake_total,
        title,
        "",
        totals.total_vol,
        totals.tot_cone_height,
        totals.tot_strake_height,
        "",
        s.lab_components_hrs,
        s.lab_components_amt,
        "",
        0,  # ClientIDNum
    ]
    if len(summary_block) != SUMMARY_FIELDS:
        raise ValueError(f"Summary block must be {SUMMARY_FIELDS} fields, got {len(summary_block)}")
    tokens.extend(summary_block)

    components = payload.get("selected_components") or []
    for i in range(NUM_COMPONENTS):
        if i < len(components):
            c = components[i]
            tokens.extend([
                c.get("type") or "",
                c.get("description") or "",
                "",
                float(c.get("cost") or 0),
                "",
                "",
                "",
                0,
                c.get("stock_num") or "",
            ])
        else:
            tokens.extend([""] * COMP_FIELDS)

    tokens.extend(_empty_tail_tokens())
    return tokens


def write_jma_bytes(
    payload: dict[str, Any],
    *,
    title: str,
    quote_ref: str | None = None,
    company_name: str = "",
) -> bytes:
    tokens = build_jma_tokens(
        payload, title=title, quote_ref=quote_ref, company_name=company_name
    )
    buf = io.StringIO()
    for token in tokens:
        buf.write(_fmt(token))
        buf.write("\r\n")
    return buf.getvalue().encode("latin-1", errors="replace")


def write_jma_file(
    path: Path | str,
    payload: dict[str, Any],
    *,
    title: str,
    quote_ref: str | None = None,
    company_name: str = "",
) -> None:
    data = write_jma_bytes(
        payload, title=title, quote_ref=quote_ref, company_name=company_name
    )
    Path(path).write_bytes(data)
