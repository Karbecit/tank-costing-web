"""
Parser for JMA Tank Costing save files (VB6 sequential Input # format).

Each field is written on its own line. Booleans appear as #TRUE# / #FALSE#.
"""

from __future__ import annotations

import re
from pathlib import Path

from app.calc.constants import (
    CONE_FIELDS,
    NUM_CONES,
    NUM_TYPE_STRAKES,
    STRAKE_FIELDS,
)
from app.jma.summary_fields import SUMMARY_FIELD
from app.models.cone import Cone
from app.models.strake import Strake
from app.models.summary import SummaryInput, SummaryTotals

_BOOL_RE = re.compile(r"^#(?P<val>TRUE|FALSE)#$", re.IGNORECASE)
_QUOTED_RE = re.compile(r'^"(?P<val>.*)"$')


def _parse_token(line: str) -> str | float | bool:
    stripped = line.strip()
    if not stripped:
        raise ValueError("Empty line in JMA file")

    bool_match = _BOOL_RE.match(stripped)
    if bool_match:
        return bool_match.group("val").upper() == "TRUE"

    quoted = _QUOTED_RE.match(stripped)
    if quoted:
        return quoted.group("val")

    try:
        if "." in stripped or "e" in stripped.lower():
            return float(stripped)
        return int(stripped)
    except ValueError:
        return stripped


def _read_tokens(path: Path) -> list[str | float | bool]:
    tokens: list[str | float | bool] = []
    with path.open(encoding="latin-1") as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                continue
            tokens.append(_parse_token(line))
    return tokens


def _as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).upper() in ("TRUE", "1", "#TRUE#")


def _as_float(value: object) -> float:
    if isinstance(value, bool):
        return float(value)
    if value == "" or value is None:
        return 0.0
    return float(value)  # type: ignore[arg-type]


def _as_int(value: object) -> int:
    return int(float(value))  # type: ignore[arg-type]


def _as_str(value: object) -> str:
    return str(value).strip()


def parse_cone_block(tokens: list[object], index: int) -> Cone:
    """Parse one cone's 40 fields starting at tokens[index]."""
    t = tokens[index : index + CONE_FIELDS]
    if len(t) < CONE_FIELDS:
        raise ValueError(f"Expected {CONE_FIELDS} cone fields, got {len(t)}")

    cone = Cone(
        angle=_as_float(t[0]),
        angle_select=_as_bool(t[1]),
        coil_length=_as_float(t[2]),
        coil_volume=_as_float(t[3]),
        conic_select=_as_int(t[4]),
        diam_large=_as_float(t[5]),
        diam_small=_as_float(t[6]),
        grade=_as_str(t[7]),
        height=_as_float(t[8]),
        height_select=_as_bool(t[9]),
        knuck_add_height=_as_float(t[10]),
        knuckle_red_width=_as_float(t[11]),
        knuckle_rad=_as_float(t[12]),
        knuck_vol=_as_float(t[13]),
        lab_price=_as_float(t[14]),
        length=_as_float(t[15]),
        max_angle=_as_float(t[16]),
        min_angle=_as_float(t[17]),
        name=_as_str(t[18]),
        num_hours=_as_float(t[19]),
        offset_amt=_as_float(t[20]),
        offset_select=_as_int(t[21]),
        price_kg=_as_float(t[22]),
        sand_height=_as_float(t[23]),
        # t[24-26] ResHeight, ResSkirtHeight, ResVol — not stored on Cone model yet
        skirt=_as_float(t[27]),
        skirt_vol=_as_float(t[28]),
        slope_select=_as_int(t[29]),
        steel_price=_as_float(t[30]),
        surface_area=_as_float(t[31]),
        tank_area=_as_float(t[32]),
        thick=_as_float(t[33]),
        volume=_as_float(t[34]),
        volume_treat=_as_int(t[35]),
        waste=_as_float(t[36]),
        weight=_as_float(t[37]),
        weight_cucm=_as_float(t[38]),
        width=_as_float(t[39]),
    )
    return cone


def parse_strake_block(tokens: list[object], index: int) -> Strake:
    """Parse one strake's 24 fields starting at tokens[index]."""
    t = tokens[index : index + STRAKE_FIELDS]
    if len(t) < STRAKE_FIELDS:
        raise ValueError(f"Expected {STRAKE_FIELDS} strake fields, got {len(t)}")

    return Strake(
        coil_length=_as_float(t[0]),
        coil_volume=_as_float(t[1]),
        grade=_as_str(t[2]),
        height=_as_float(t[3]),
        lab_price=_as_float(t[4]),
        name=_as_str(t[5]),
        num_hours=_as_float(t[6]),
        num_iden_strakes=_as_int(t[7]),
        price_kg=_as_float(t[8]),
        rate_hour=_as_float(t[9]),
        res_height=_as_float(t[10]),
        resultant_width=_as_float(t[11]),
        res_vol=_as_float(t[12]),
        steel_price=_as_float(t[13]),
        strake_area=_as_float(t[14]),
        thick=_as_float(t[15]),
        trim_strakes=_as_float(t[16]),
        used=_as_int(t[17]),
        volume=_as_float(t[18]),
        volume_treat=_as_int(t[19]),
        waste=_as_float(t[20]),
        weight=_as_float(t[21]),
        weight_cucm=_as_float(t[22]),
        width=_as_float(t[23]),
    )


def _summary_offset() -> int:
    return NUM_CONES * CONE_FIELDS + NUM_TYPE_STRAKES * STRAKE_FIELDS


def _summary_token(tokens: list[object], field: str) -> object:
    return tokens[_summary_offset() + SUMMARY_FIELD[field]]


def parse_summary_input(tokens: list[object]) -> SummaryInput:
    """Parse summary input fields needed for recalculation."""
    return SummaryInput(
        diam=_as_float(_summary_token(tokens, "diam")),
        expan_diam=_as_float(_summary_token(tokens, "expan_diam")),
        expan_height=_as_float(_summary_token(tokens, "expan_height")),
        other_vol=_as_float(_summary_token(tokens, "other_vol")),
        coil_mark_up_percent=_as_float(tokens[_summary_offset() + 6]),
        coil_misc=_as_float(tokens[_summary_offset() + 7]),
        floor_multi_tot=_as_float(tokens[_summary_offset() + 5]),
        components_price=_as_float(_summary_token(tokens, "components_price")),
        comp=[
            _as_float(_summary_token(tokens, "comp_0")),
            _as_float(_summary_token(tokens, "comp_1")),
            _as_float(_summary_token(tokens, "comp_2")),
            _as_float(_summary_token(tokens, "comp_3")),
        ],
        comp_markup_percent=_as_float(_summary_token(tokens, "comp_markup_percent")),
        gst=_as_float(_summary_token(tokens, "gst")),
        num_tanks=_as_int(_summary_token(tokens, "num_tanks")),
        price_quoted=_as_float(_summary_token(tokens, "price_quoted")),
        lab_misc_hrs=_as_float(_summary_token(tokens, "lab_misc_hrs")),
        lab_misc_rate=_as_float(_summary_token(tokens, "lab_misc_rate")),
        lab_components_hrs=_as_float(tokens[_summary_offset() + 85]),
        lab_components_amt=_as_float(tokens[_summary_offset() + 86]),
        single_add_on=[
            _as_float(_summary_token(tokens, "single_add_on_0")),
            _as_float(_summary_token(tokens, "single_add_on_1")),
            _as_float(_summary_token(tokens, "single_add_on_2")),
        ],
        multi_add_on=[
            _as_float(_summary_token(tokens, "multi_add_on_0")),
            _as_float(_summary_token(tokens, "multi_add_on_1")),
            _as_float(_summary_token(tokens, "multi_add_on_2")),
        ],
    )


def _steel_totals_base(tokens: list[object]) -> int:
    """Index of SteelKgTotal — immediately after MAXNUMCOMPS in the .jma file."""
    start = _summary_offset()
    # SingleTankSteel is the last field before MAXNUMCOMPS (offset +72 in current format)
    return start + 73


def parse_summary_stored_totals(tokens: list[object]) -> SummaryTotals:
    """Read persisted summary totals from a .jma file for test comparison."""
    base = _steel_totals_base(tokens)
    return SummaryTotals(
        steel_sub_tot=_as_float(tokens[base + 2]),
        steel_mark_up_amount=_as_float(tokens[base + 1]),
        steel_total=_as_float(tokens[base + 3]),
        strakes_vol=_as_float(tokens[base + 4]),
        strake_total=_as_float(tokens[base + 5]),
        total_vol=_as_float(tokens[base + 8]),
        tot_cone_height=_as_float(tokens[base + 9]),
        tot_strake_height=_as_float(tokens[base + 10]),
        cones_vol=_as_float(_summary_token(tokens, "cones_vol")),
        cone_total=_as_float(_summary_token(tokens, "cone_total")),
        expan_vol=_as_float(_summary_token(tokens, "expan_vol")),
    )


def load_jma_strakes(path: Path | str) -> list[Strake]:
    tokens = _read_tokens(Path(path))
    offset = NUM_CONES * CONE_FIELDS
    return [parse_strake_block(tokens, offset + i * STRAKE_FIELDS) for i in range(NUM_TYPE_STRAKES)]


def load_jma_cones(path: Path | str) -> list[Cone]:
    """Load all five cone records from a .jma file."""
    tokens = _read_tokens(Path(path))
    cones: list[Cone] = []
    offset = 0
    for _ in range(NUM_CONES):
        cones.append(parse_cone_block(tokens, offset))
        offset += CONE_FIELDS
    return cones


def load_jma_tank_diam(path: Path | str) -> float:
    """Read Summ.Diam from a .jma file."""
    tokens = _read_tokens(Path(path))
    return _as_float(_summary_token(tokens, "diam"))


def load_jma_full(path: Path | str) -> tuple[list[Cone], list[Strake], SummaryInput, SummaryTotals]:
    """Load cones, strakes, summary inputs, and stored totals from a .jma file."""
    path = Path(path)
    tokens = _read_tokens(path)
    cones = [parse_cone_block(tokens, i * CONE_FIELDS) for i in range(NUM_CONES)]
    strake_offset = NUM_CONES * CONE_FIELDS
    strakes = [
        parse_strake_block(tokens, strake_offset + i * STRAKE_FIELDS)
        for i in range(NUM_TYPE_STRAKES)
    ]
    return (
        cones,
        strakes,
        parse_summary_input(tokens),
        parse_summary_stored_totals(tokens),
    )


def load_jma(path: Path | str) -> tuple[list[Cone], float]:
    """Load cones and tank diameter from a .jma costing file."""
    path = Path(path)
    return load_jma_cones(path), load_jma_tank_diam(path)
