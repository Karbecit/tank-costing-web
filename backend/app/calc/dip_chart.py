"""Dip chart calculation — single-tank (calc1DipChart port)."""

from __future__ import annotations

import math
from dataclasses import dataclass

from app.calc.constants import CONIC_SEL, OFFSET_SEL, PI, SLOPE_SEL
from app.models.cone import Cone
from app.models.summary import SummaryInput, SummaryTotals


@dataclass
class DipRow:
    mm: int
    space_litres: float
    remain_litres: float
    place: str


def _round_vb(n: float) -> int:
    whole = int(n)
    return whole + 1 if n - whole >= 0.5 else whole


def _dip_point_up_cone(
    s_dim: float,
    l_dim: float,
    height: int,
    pre_volume: float,
    tank_volume: float,
    top_of_tank: bool,
    element: str,
    chart: list[DipRow],
) -> float:
    if height <= 0:
        return pre_volume
    diam_inc = (l_dim - s_dim) / height if height else 0
    a2 = s_dim
    start = 0 if top_of_tank else len(chart)
    for step in range(1, int(height) + 1):
        a2 += diam_inc
        area1 = PI * ((s_dim / 2) ** 2)
        area2 = PI * ((a2 / 2) ** 2)
        space = pre_volume + (
            step / 300 * ((area1 + area2) + math.sqrt(area1 * area2)) / 10000
        )
        chart.append(
            DipRow(
                mm=start + step,
                space_litres=space,
                remain_litres=tank_volume - space,
                place=element,
            )
        )
    return chart[-1].space_litres if chart else pre_volume


def _dip_cylinder(
    cyl_diam: float,
    height: int,
    pre_volume: float,
    tank_volume: float,
    top_of_tank: bool,
    element: str,
    chart: list[DipRow],
) -> float:
    if height <= 0:
        return pre_volume
    start = 0 if top_of_tank else len(chart)
    drum_rad = cyl_diam / 2
    for step in range(1, int(height) + 1):
        space = pre_volume + (PI * (drum_rad**2) * step / 1_000_000)
        chart.append(
            DipRow(
                mm=start + step,
                space_litres=space,
                remain_litres=tank_volume - space,
                place=element,
            )
        )
    return chart[-1].space_litres


def _dip_int_slope(
    cyl_diam: float,
    height: int,
    pre_volume: float,
    tank_volume: float,
    element: str,
    cone: Cone,
    chart: list[DipRow],
) -> float:
    if height <= 0:
        return pre_volume
    h = height
    if h < (h / 2) + cone.sand_height:
        h = int((h / 2) + cone.sand_height)
    knuckle_var = cone.knuck_vol / h if h else 0
    sand_vol = ((PI * (cyl_diam / 2) ** 2) / 3) * cone.sand_height / 1_000_000
    sand_vol = sand_vol / h if h else 0
    vol_per_mm = (PI * ((cyl_diam / 2) ** 2) / 1_000_000)
    start = len(chart)
    for step in range(1, h + 1):
        space = pre_volume + (vol_per_mm * step / 2) - (knuckle_var * step) - (sand_vol * step)
        place = f"{element.strip()} + Sand" if cone.sand_height > 0 else element
        chart.append(
            DipRow(
                mm=start + step,
                space_litres=space,
                remain_litres=tank_volume - space,
                place=place,
            )
        )
    return chart[-1].space_litres if chart else pre_volume


def _dip_point_down_cone(
    s_dim: float,
    l_dim: float,
    height: int,
    pre_volume: float,
    tank_volume: float,
    element: str,
    chart: list[DipRow],
) -> float:
    if height <= 0:
        return pre_volume
    diam_inc = (l_dim - s_dim) / height
    a2 = 0.0
    start = len(chart)
    for step in range(1, height + 1):
        a2 += diam_inc
        area1 = PI * ((l_dim / 2) ** 2)
        area2 = PI * ((l_dim - a2) / 2) ** 2
        space = pre_volume + (
            step / 300 * ((area1 + area2) + math.sqrt(area1 * area2)) / 10000
        )
        chart.append(
            DipRow(
                mm=start + step,
                space_litres=space,
                remain_litres=tank_volume - space,
                place=element,
            )
        )
    return chart[-1].space_litres if chart else pre_volume


def _dip_invert_cone(
    s_dim: float,
    l_dim: float,
    height: int,
    element: str,
    tank_volume: float,
    chart: list[DipRow],
) -> None:
    if height <= 0 or not chart:
        return
    h = int(height)
    diam_inc = (l_dim - s_dim) / h
    place_start = len(chart) - h
    a2 = s_dim
    for inc in range(h):
        a2 += diam_inc
        idx = place_start + inc
        if idx < 0 or idx >= len(chart):
            continue
        area1 = PI * ((s_dim / 2) ** 2)
        area2 = PI * ((a2 / 2) ** 2)
        exist = chart[idx].space_litres
        new_space = exist - (inc / 300 * ((area1 + area2) + math.sqrt(area1 * area2)) / 10000)
        chart[idx].space_litres = new_space
        chart[idx].place = f"{chart[idx].place.strip()}/{element}"
        chart[idx].remain_litres = tank_volume - new_space


def calc_single_dip_chart(
    cones: list[Cone],
    summary: SummaryInput,
    totals: SummaryTotals,
    *,
    top_cone: int = 0,
    bottom_cone: int = 2,
    invert_cone: int = 2,
    increment: int = 10,
) -> dict:
    """Single-tank dip chart (VB6 calc1DipChart)."""
    if increment <= 0:
        increment = 10
    tc = top_cone
    bc = bottom_cone
    inv = invert_cone
    chart: list[DipRow] = []
    tank_vol = totals.total_vol

    carry = _dip_cylinder(
        summary.expan_diam,
        _round_vb(summary.expan_height),
        0,
        tank_vol,
        True,
        "Expansion Chamber",
        chart,
    )
    top = cones[tc]
    carry = _dip_point_up_cone(
        top.diam_small,
        top.diam_large - top.knuckle_red_width,
        _round_vb(top.height - top.knuck_add_height),
        carry,
        tank_vol,
        False,
        "Top Cone",
        chart,
    )
    carry = _dip_point_up_cone(
        top.diam_large - top.knuckle_red_width,
        top.diam_large,
        _round_vb(top.knuck_add_height),
        carry,
        tank_vol,
        False,
        "Knuckle",
        chart,
    )

    bc_cone = cones[bc]
    if bc_cone.cone_stat in (CONIC_SEL, OFFSET_SEL):
        barrel_h = _round_vb(totals.tot_strake_height)
    else:
        barrel_h = _round_vb(totals.tot_strake_height - bc_cone.skirt - bc_cone.height)
    carry = _dip_cylinder(bc_cone.diam_large, barrel_h, carry, tank_vol, False, "Barrel", chart)

    if bc_cone.cone_stat == SLOPE_SEL:
        carry = _dip_int_slope(
            bc_cone.diam_large,
            _round_vb(bc_cone.height),
            carry,
            tank_vol,
            bc_cone.name or "Bottom",
            bc_cone,
            chart,
        )
    else:
        carry = _dip_point_down_cone(
            bc_cone.diam_large - bc_cone.knuckle_red_width,
            bc_cone.diam_large,
            _round_vb(bc_cone.knuck_add_height),
            carry,
            tank_vol,
            "Knuckle",
            chart,
        )
        carry = _dip_point_down_cone(
            bc_cone.diam_small,
            bc_cone.diam_large - bc_cone.knuckle_red_width,
            _round_vb(bc_cone.height - bc_cone.knuck_add_height),
            carry,
            tank_vol,
            "Bottom Cone",
            chart,
        )

    inv_cone = cones[inv]
    _dip_invert_cone(
        inv_cone.diam_small,
        inv_cone.diam_large,
        _round_vb(inv_cone.height),
        "Invert Cone",
        tank_vol,
        chart,
    )

    midway = len(chart)
    sampled = []
    acc = 0
    inc_acc = 0
    for row in chart[:midway]:
        inc_acc += 1
        if inc_acc >= increment:
            acc += 1
            sampled.append({
                "mm_from_top": row.mm,
                "space_litres": round(row.space_litres, 1),
                "litres_in_tank": round(row.remain_litres, 1),
                "section": row.place,
            })
            inc_acc = 0

    return {
        "mode": "single",
        "increment_mm": increment,
        "total_volume_litres": round(tank_vol, 1),
        "tank_height_mm": round(totals.tank_height, 1),
        "rows": sampled,
    }
