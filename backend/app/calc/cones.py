"""
Cone calculation engine — port of VB6 Cones.bas (GetConicScreenData, CalcConeHeight)
and batch_plot.bas (CalcTank for offset cones).
"""

from __future__ import annotations

import math
from copy import deepcopy

from app.calc.constants import (
    CONIC_SEL,
    FAC,
    OFFSET_SEL,
    PI,
    SANDHIGH1,
    SANDHIGH2,
    SLOPE_SEL,
    SQCIRC,
)
from app.models.cone import Cone, ConeCalcContext


def sand_height(tank_diam: float) -> float:
    """Port of Cones.bas SandHeight — sand fill height for sloped floors."""
    if tank_diam <= 0:
        return 0.0
    if tank_diam <= 4000:
        return tank_diam / SANDHIGH1
    return tank_diam / SANDHIGH2


def _apply_knuckle_at_angle(cone: Cone, ang: float) -> float:
    """
    Port of CalcConeHeight — updates knuckle fields on *cone* and returns total height.
    """
    ang_rad = ang * PI / 180
    cone.knuckle_red_width = (cone.knuckle_rad - (cone.knuckle_rad * math.sin(ang_rad))) * 2
    cone.knuck_add_height = cone.knuckle_rad * math.cos(ang_rad)
    if cone.knuckle_rad == 0:
        cone.knuck_add_height = 0.0

    cone_eff_width = cone.diam_large - cone.knuckle_red_width - cone.diam_small
    knuck_circum = PI * (cone.knuckle_rad * 2)

    if ang >= 90:
        cone.knuckle_length = 0.0
    else:
        cone.knuckle_length = knuck_circum / (360 / (90 - ang))

    a_rad_large = cone.diam_large / 2
    a_rad_small = (cone.diam_large - cone.knuckle_red_width) / 2
    cone.knuck_vol = (
        PI
        * cone.knuck_add_height
        / 300
        * ((a_rad_large**2) + (a_rad_large * a_rad_small) + (a_rad_small**2))
        / 10000
    )
    cone.knuckle_area = (
        PI * (a_rad_large + a_rad_large + (cone.knuckle_red_width / 2)) * cone.knuckle_length
    )

    cone_only_height = math.tan(ang_rad) * (cone_eff_width / 2)
    return cone.knuck_add_height + cone_only_height


def calc_cone_height(cone: Cone, ang: float) -> float:
    """Public wrapper matching VB6 CalcConeHeight signature."""
    return _apply_knuckle_at_angle(cone, ang)


def _solve_angle_from_height(cone: Cone) -> float:
    """Iterative angle search — VB6 uses 0.01° steps."""
    ang = 0.0
    while _apply_knuckle_at_angle(cone, ang) < cone.height:
        ang += 0.01
        if ang >= 90:
            break
    return ang


def calc_offset_angles(cone: Cone) -> None:
    """
    Port of batch_plot.bas CalcTank — sets min_angle and max_angle on offset cones.
    """
    if cone.diam_large <= 0:
        return

    tank_rad = cone.diam_large / 2
    cone.offset_cl_amt = tank_rad - (cone.offset_amt + (cone.diam_small / 2))

    ang = 0.0
    min_exp_dim = 0.0
    min_aa = 0.0
    min_b = 0.0
    min_a = 0.0
    min_effect_knuck_width = 0.0
    min_effect_knuck_height = 0.0

    while True:
        ang += 0.001
        if cone.knuckle_rad == 0:
            min_knuck_aa = 0.0
        else:
            min_knuck_aa = ang
        min_knuck_c = cone.knuckle_rad
        min_effect_knuck_width = cone.knuckle_rad - (min_knuck_c * math.sin(min_knuck_aa * FAC))
        min_effect_knuck_height = min_knuck_c * math.cos(min_knuck_aa * FAC)
        min_aa = ang
        min_b = cone.diam_large - cone.offset_amt - cone.diam_small - min_effect_knuck_width
        min_a = min_b * math.tan(min_aa * FAC)
        min_exp_dim = min_a + min_effect_knuck_height
        if ang >= 90 or min_exp_dim >= cone.height:
            break

    max_aa = 0.0
    max_effect_knuck_width = 0.0
    max_effect_knuck_height = 0.0

    while True:
        max_aa += 0.001
        max_knuck_c = cone.knuckle_rad
        if cone.knuckle_rad == 0:
            max_knuck_aa = 0.0
        else:
            max_knuck_aa = max_aa
        max_effect_knuck_width = cone.knuckle_rad - (max_knuck_c * math.sin(max_knuck_aa * FAC))
        max_effect_knuck_height = max_knuck_c * math.cos(max_knuck_aa * FAC)

        if cone.offset_cl_amt == 0:
            max_b = min_b
            max_a = min_a
            max_effect_knuck_width = min_effect_knuck_width
            max_effect_knuck_height = min_effect_knuck_height
            break

        max_b = cone.offset_amt - max_effect_knuck_width
        max_a = max_b * math.tan(max_aa * FAC)
        max_exp_dim = max_a + max_effect_knuck_height
        if max_aa >= 90 or max_exp_dim >= min_exp_dim:
            break

    cone.max_angle = max_aa
    cone.min_angle = min_aa


def _calc_conic_or_offset(cone: Cone, ang: float) -> None:
    """Volume, length, area for conical and offset cones."""
    if cone.height_select:
        cone.angle = _solve_angle_from_height(cone)
        ang = cone.angle
    elif cone.angle_select:
        cone.height = _apply_knuckle_at_angle(cone, cone.angle)
        ang = cone.angle

    cone_only_width = cone.diam_large - cone.knuckle_red_width
    a_rad_large = (cone.diam_large - cone.knuckle_red_width) / 2
    a_rad_small = cone.diam_small / 2
    cone_rat_width = (cone_only_width - cone.diam_small) / 2

    if cone.angle > 0:
        cone_only_length = math.sqrt((cone.height**2) + (cone_rat_width**2))
    elif ang == 0:
        cone_only_length = cone_only_width / 2
    else:
        cone_only_length = 0.0

    if cone.height < cone.knuck_add_height:
        cone_only_height = cone.height
    else:
        cone_only_height = cone.height - cone.knuck_add_height

    cone_only_vol = (
        PI
        * cone_only_height
        / 300
        * ((a_rad_large**2) + (a_rad_large * a_rad_small) + (a_rad_small**2))
        / 10000
    )

    cone.length = cone_only_length + cone.knuckle_length
    cone.area = (
        (PI * ((a_rad_large / 2) + (a_rad_small / 2)) * cone_only_length) + cone.knuckle_area
    ) / 1000
    cone.surface_area = ((cone.waste + cone.diam_large) ** 2) / 1000
    cone.volume = cone_only_vol + cone.knuck_vol
    cone.skirt = 0.0


def _calc_slope(cone: Cone, ctx: ConeCalcContext) -> None:
    """Sloped tank floor — port of SLOPE_SEL branch in GetConicScreenData."""
    cone.knuck_add_height = 0.0
    tank_diam = ctx.tank_diam

    if tank_diam > 0:
        cone.tank_area = ((cone.diam_large / 2) ** 2) * PI / 1000
        rad_b = tank_diam / 2 / 1000
        rad_a = rad_b - (cone.knuckle_rad / 1000)
        outer_vol = PI * (rad_b**2) * cone.knuckle_rad
        inner_vol = PI * (rad_a**2) * cone.knuckle_rad
        knuck_seg_vol = outer_vol - inner_vol
        cone.knuck_vol = knuck_seg_vol * (1 - SQCIRC)
    else:
        cone.tank_area = 0.0

    if cone.angle_select:
        cone.height = (cone.diam_large - (cone.knuckle_rad * 2)) * math.tan(cone.angle * PI / 180)
    elif cone.height_select:
        denom = cone.diam_large - (cone.knuckle_rad * 2)
        if denom != 0:
            cone.angle = math.atan(cone.height / denom) * 180 / PI

    sand_vol = 0.0
    if cone.sand_height > 0:
        sand_vol = (PI * (((cone.diam_large / 2) ** 2) * cone.sand_height) / 3) / 1_000_000

    if cone.tank_area > 0:
        cone.skirt_vol = cone.skirt * cone.tank_area / 1000
        cone.volume = (
            (cone.height * cone.tank_area) / 2 / 1000 + cone.knuck_vol + cone.skirt_vol + sand_vol
        )
        cone.length = math.sqrt((cone.diam_large**2) + (cone.height**2))
        cone.area = PI * (cone.length / 2) * (cone.diam_large / 2) / 1000
        cone.surface_area = ((cone.waste + cone.length) * (cone.waste + cone.diam_large)) / 1000


def _calc_steel_pricing(cone: Cone, ctx: ConeCalcContext) -> None:
    """Labour and steel pricing — common tail of GetConicScreenData."""
    cone.lab_price = ctx.cones_rate_per_hour * cone.num_hours
    if cone.width > 0:
        cone.coil_length = cone.surface_area / cone.width * 1000
    if cone.thick > 0:
        cone.coil_volume = cone.surface_area * cone.thick / 1000
    if cone.weight_cucm > 0 and cone.coil_volume > 0:
        cone.weight = cone.weight_cucm / (1 / cone.coil_volume) / 1000
    cone.steel_price = cone.weight * cone.price_kg


def calculate_cone(cone: Cone, ctx: ConeCalcContext) -> Cone:
    """
    Run full cone calculation. Returns a new Cone with computed fields filled in.
    Input geometry fields on *cone* are preserved; derived fields are recalculated.
    """
    result = deepcopy(cone)
    result.cone_stat = result._derive_cone_stat()

    if result.diam_large <= 0 and ctx.tank_diam > 0:
        result.diam_large = ctx.tank_diam

    if result.diam_large > 0:
        result.tank_area = ((result.diam_large / 2) ** 2) * PI / 1000
    else:
        result.tank_area = 0.0

    if result.offset_amt >= ctx.tank_diam or result.offset_amt <= 0:
        result.offset_amt = 1.0

    if result.cone_stat in (CONIC_SEL, OFFSET_SEL):
        if result.offset_select:
            result.height_select = True

        ang = result.angle
        _calc_conic_or_offset(result, ang)

        if result.cone_stat == OFFSET_SEL:
            calc_offset_angles(result)

    elif result.cone_stat == SLOPE_SEL:
        _calc_slope(result, ctx)

    _calc_steel_pricing(result, ctx)
    return result
