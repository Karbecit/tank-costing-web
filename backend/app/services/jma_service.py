"""Map parsed .jma data to web app costing payload."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.calc.constants import CONE_FIELDS, NUM_CONES, NUM_TYPE_STRAKES, STRAKE_FIELDS
from app.jma.reader import (
    _as_float,
    _as_int,
    _as_str,
    _read_tokens,
    _summary_offset,
    parse_cone_block,
    parse_strake_block,
    parse_summary_input,
)
from app.models.cone import Cone
from app.models.strake import Strake
from app.models.summary import SummaryInput

SUMMARY_FIELDS = 89
MAX_NUM_COMPS_IDX = 72
COMPANY_NAME_IDX = 12
QUOTE_NUM_IDX = 26
TANK_DESCRIPTION_IDX = 79
COMP_FIELDS = 9


def _summary_token(tokens: list[object], idx: int) -> object:
    return tokens[_summary_offset() + idx]


def parse_jma_components(tokens: list[object]) -> list[dict[str, Any]]:
    max_comps = _as_int(_summary_token(tokens, MAX_NUM_COMPS_IDX))
    if max_comps != 50:
        max_comps = 28
    base = _summary_offset() + SUMMARY_FIELDS
    selected: list[dict[str, Any]] = []
    for i in range(max_comps):
        off = base + i * COMP_FIELDS
        comp_type = _as_str(tokens[off])
        description = _as_str(tokens[off + 1])
        cost = _as_float(tokens[off + 3])
        stocknum = _as_str(tokens[off + 8])
        if not description and not comp_type and cost == 0:
            continue
        selected.append(
            {
                "stock_id": None,
                "type": comp_type,
                "description": description or comp_type,
                "cost": cost,
                "stock_num": stocknum,
            }
        )
    return selected


def cone_to_payload(cone: Cone) -> dict[str, Any]:
    return {
        "name": cone.name,
        "height_select": cone.height_select,
        "angle_select": cone.angle_select,
        "conic_select": cone.conic_select,
        "offset_select": cone.offset_select,
        "slope_select": cone.slope_select,
        "diam_large": cone.diam_large,
        "diam_small": cone.diam_small,
        "height": cone.height,
        "angle": cone.angle,
        "offset_amt": cone.offset_amt,
        "knuckle_rad": cone.knuckle_rad,
        "sand_height": cone.sand_height,
        "skirt": cone.skirt,
        "waste": cone.waste,
        "thick": cone.thick,
        "width": cone.width,
        "weight_cucm": cone.weight_cucm,
        "price_kg": cone.price_kg,
        "num_hours": cone.num_hours,
        "grade": cone.grade,
        "volume_treat": cone.volume_treat,
    }


def strake_to_payload(strake: Strake) -> dict[str, Any]:
    return {
        "used": strake.used,
        "name": strake.name,
        "num_iden_strakes": strake.num_iden_strakes,
        "trim_strakes": strake.trim_strakes,
        "grade": strake.grade,
        "thick": strake.thick,
        "width": strake.width,
        "weight_cucm": strake.weight_cucm,
        "coil_length": strake.coil_length,
        "price_kg": strake.price_kg,
        "num_hours": strake.num_hours,
        "rate_hour": strake.rate_hour,
        "volume_treat": strake.volume_treat,
    }


def summary_to_payload(summary) -> dict[str, Any]:
    return {
        "diam": summary.diam,
        "expan_diam": summary.expan_diam,
        "expan_height": summary.expan_height,
        "other_vol": summary.other_vol,
        "coil_mark_up_percent": summary.coil_mark_up_percent,
        "coil_misc": summary.coil_misc,
        "floor_multi_tot": summary.floor_multi_tot,
        "components_price": summary.components_price,
        "comp": list(summary.comp),
        "comp_markup_percent": summary.comp_markup_percent,
        "gst": summary.gst,
        "num_tanks": summary.num_tanks,
        "price_quoted": summary.price_quoted,
        "lab_misc_hrs": summary.lab_misc_hrs,
        "lab_misc_rate": summary.lab_misc_rate,
        "lab_components_hrs": summary.lab_components_hrs,
        "lab_components_amt": summary.lab_components_amt,
        "single_add_on": list(summary.single_add_on),
        "multi_add_on": list(summary.multi_add_on),
    }


def payload_to_models(
    payload: dict[str, Any],
) -> tuple[list[Cone], list[Strake], SummaryInput, float]:
    """Convert web JSON payload to calculation models."""
    cones = []
    for c in payload.get("cones", []):
        cones.append(
            Cone(
                name=str(c.get("name", "")),
                height_select=bool(c.get("height_select")),
                angle_select=bool(c.get("angle_select")),
                conic_select=int(c.get("conic_select", 0)),
                offset_select=int(c.get("offset_select", 0)),
                slope_select=int(c.get("slope_select", 0)),
                diam_large=float(c.get("diam_large", 0)),
                diam_small=float(c.get("diam_small", 0)),
                height=float(c.get("height", 0)),
                angle=float(c.get("angle", 0)),
                offset_amt=float(c.get("offset_amt", 0)),
                knuckle_rad=float(c.get("knuckle_rad", 0)),
                sand_height=float(c.get("sand_height", 0)),
                skirt=float(c.get("skirt", 0)),
                waste=float(c.get("waste", 0)),
                thick=float(c.get("thick", 0)),
                width=float(c.get("width", 0)),
                weight_cucm=float(c.get("weight_cucm", 8166)),
                price_kg=float(c.get("price_kg", 0)),
                num_hours=float(c.get("num_hours", 0)),
                grade=str(c.get("grade", "")),
                volume_treat=int(c.get("volume_treat", 0)),
            )
        )
    strakes = []
    for s in payload.get("strakes", []):
        strakes.append(
            Strake(
                used=int(s.get("used", 0)),
                name=str(s.get("name", "")),
                num_iden_strakes=int(s.get("num_iden_strakes", 1)),
                trim_strakes=float(s.get("trim_strakes", 0)),
                grade=str(s.get("grade", "")),
                thick=float(s.get("thick", 0)),
                width=float(s.get("width", 0)),
                weight_cucm=float(s.get("weight_cucm", 8166)),
                coil_length=float(s.get("coil_length", 0)),
                price_kg=float(s.get("price_kg", 0)),
                num_hours=float(s.get("num_hours", 0)),
                rate_hour=float(s.get("rate_hour", 0)),
                volume_treat=int(s.get("volume_treat", 0)),
            )
        )
    sd = payload.get("summary", {})
    summary = SummaryInput(
        diam=float(sd.get("diam", 0)),
        expan_diam=float(sd.get("expan_diam", 0)),
        expan_height=float(sd.get("expan_height", 0)),
        other_vol=float(sd.get("other_vol", 0)),
        coil_mark_up_percent=float(sd.get("coil_mark_up_percent", 0)),
        coil_misc=float(sd.get("coil_misc", 0)),
        floor_multi_tot=float(sd.get("floor_multi_tot", 0)),
        components_price=float(sd.get("components_price", 0)),
        comp=[float(x) for x in sd.get("comp", [0, 0, 0, 0])],
        comp_markup_percent=float(sd.get("comp_markup_percent", 0)),
        gst=float(sd.get("gst", 1.1)),
        num_tanks=int(sd.get("num_tanks", 1)),
        price_quoted=float(sd.get("price_quoted", 0)),
        lab_misc_hrs=float(sd.get("lab_misc_hrs", 0)),
        lab_misc_rate=float(sd.get("lab_misc_rate", 0)),
        lab_components_hrs=float(sd.get("lab_components_hrs", 0)),
        lab_components_amt=float(sd.get("lab_components_amt", 0)),
        single_add_on=[float(x) for x in sd.get("single_add_on", [0, 0, 0])],
        multi_add_on=[float(x) for x in sd.get("multi_add_on", [0, 0, 0])],
    )
    rate = float(payload.get("cones_rate_per_hour", 55))
    return cones, strakes, summary, rate


def jma_file_to_payload(path: Path | str) -> dict[str, Any]:
    """Parse a .jma file into a web costing payload dict."""
    path = Path(path)
    tokens = _read_tokens(path)
    cones = [parse_cone_block(tokens, i * CONE_FIELDS) for i in range(NUM_CONES)]
    strake_offset = NUM_CONES * CONE_FIELDS
    strakes = [
        parse_strake_block(tokens, strake_offset + i * STRAKE_FIELDS)
        for i in range(NUM_TYPE_STRAKES)
    ]
    summary = parse_summary_input(tokens)
    components = parse_jma_components(tokens)

    title = _as_str(_summary_token(tokens, TANK_DESCRIPTION_IDX)) or "Imported costing"
    quote_ref = _as_str(_summary_token(tokens, QUOTE_NUM_IDX))
    company_name = _as_str(_summary_token(tokens, COMPANY_NAME_IDX))

    lab_cones_hrs = _as_float(_summary_token(tokens, 31))
    lab_cones_amt = _as_float(_summary_token(tokens, 30))
    cones_rate = lab_cones_amt / lab_cones_hrs if lab_cones_hrs else 55.0

    if components and summary.components_price == 0:
        summary.components_price = sum(c["cost"] for c in components)

    return {
        "version": 1,
        "title": title,
        "quote_ref": quote_ref,
        "company_name": company_name,
        "cones_rate_per_hour": cones_rate,
        "selected_components": components,
        "summary": summary_to_payload(summary),
        "cones": [cone_to_payload(c) for c in cones],
        "strakes": [strake_to_payload(s) for s in strakes],
    }


def jma_bytes_to_payload(content: bytes) -> dict[str, Any]:
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".jma", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    try:
        return jma_file_to_payload(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)
