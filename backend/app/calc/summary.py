"""Summary totals — port of VB6 Summary.bas CalcSumTotals."""

from __future__ import annotations

from app.calc.constants import PI, SLOPE_SEL
from app.models.cone import Cone
from app.models.strake import Strake
from app.models.summary import SummaryInput, SummaryTotals

# Water density correction factors F0–F25 from Declarations.bas
_DENSITY_FACTORS: dict[int, float] = {
    0: 0.99982,
    1: 0.99989,
    2: 0.99994,
    3: 0.99998,
    4: 1.0,
    5: 1.0,
    6: 0.999999,
    7: 0.99996,
    8: 0.99991,
    9: 0.99985,
    10: 0.99977,
    11: 0.99968,
    12: 0.99958,
    13: 0.99946,
    14: 0.99933,
    15: 0.99919,
    16: 0.99903,
    17: 0.99886,
    18: 0.99868,
    19: 0.99849,
    20: 0.99829,
    21: 0.99808,
    22: 0.99786,
    23: 0.99762,
    24: 0.99738,
    25: 0.99713,
}


def _volume_treat_adds_height(treat: int) -> bool:
    return treat in (0, 1, 2)


def _volume_treat_subtracts_height(treat: int) -> bool:
    return treat in (3, 4, 5)


def _volume_treat_adds_vol(treat: int) -> bool:
    return treat in (0, 3, 6)


def _volume_treat_subtracts_vol(treat: int) -> bool:
    return treat in (1, 4, 7)


def calc_summary_totals(
    cones: list[Cone],
    strakes: list[Strake],
    summary: SummaryInput,
) -> SummaryTotals:
    """Port of CalcSumTotals — aggregates cones, strakes, and pricing."""
    totals = SummaryTotals()
    s = summary

    for cone in cones:
        if cone.cone_stat > 0:
            totals.cone_total += cone.steel_price
            totals.lab_cones_amt += cone.lab_price
            totals.lab_cones_hrs += cone.num_hours

    for strake in strakes:
        if strake.is_active:
            totals.strake_total += strake.steel_price * strake.num_iden_strakes
            totals.lab_strakes_amt += strake.lab_price * strake.num_iden_strakes
            totals.lab_strakes_hrs += strake.num_hours * strake.num_iden_strakes

    totals.steel_sub_tot = (
        totals.strake_total + totals.cone_total + s.coil_misc + s.floor_multi_tot
    )
    if totals.steel_sub_tot > 0:
        totals.steel_mark_up_amount = totals.steel_sub_tot / 100 * s.coil_mark_up_percent
    totals.steel_total = totals.steel_sub_tot + totals.steel_mark_up_amount

    if s.expan_diam > 0 and s.expan_height > 0:
        totals.expan_vol = PI * (s.expan_diam / 2) ** 2 * s.expan_height / 1_000_000
    else:
        totals.expan_vol = 0.0

    for strake in strakes:
        if not strake.is_active:
            continue
        treat = strake.volume_treat
        if _volume_treat_adds_height(treat):
            strake.res_height = strake.resultant_width * strake.num_iden_strakes
            totals.tot_strake_height += strake.res_height
        elif _volume_treat_subtracts_height(treat):
            strake.res_height = strake.resultant_width * strake.num_iden_strakes
            totals.tot_strake_height -= strake.res_height
        else:
            strake.res_height = 0.0

    for cone in cones:
        if cone.cone_stat <= 0:
            continue
        treat = cone.volume_treat
        if treat in (0, 1, 2):
            cone.res_height = cone.height
            totals.tot_cone_height += cone.height
        elif treat in (3, 4, 5):
            cone.res_height = -cone.height
            totals.tot_cone_height -= cone.height
        elif treat in (6, 7, 8):
            cone.res_height = cone.height
        else:
            cone.res_height = 0.0

    totals.res_barrel_height = totals.tot_strake_height
    for cone in cones:
        if cone.cone_stat == SLOPE_SEL:
            totals.res_barrel_height = totals.tot_strake_height - cone.skirt

    totals.tank_height = s.expan_height + totals.tot_cone_height + totals.res_barrel_height

    for strake in strakes:
        if not strake.is_active:
            continue
        treat = strake.volume_treat
        if _volume_treat_adds_vol(treat):
            strake.res_vol = strake.volume * strake.num_iden_strakes
            totals.strakes_vol += strake.res_vol
        elif _volume_treat_subtracts_vol(treat):
            strake.res_vol = strake.volume * strake.num_iden_strakes
            totals.strakes_vol -= strake.res_vol
        else:
            strake.res_vol = 0.0

    for cone in cones:
        if cone.cone_stat <= 0:
            continue
        treat = cone.volume_treat
        if treat in (0, 3, 6):
            cone.res_vol = cone.volume
            totals.cones_vol += cone.volume
        elif treat in (1, 4, 7):
            cone.res_vol = -cone.volume
            totals.cones_vol += cone.res_vol
        elif treat == 9:
            cone.res_vol = cone.volume
        elif treat == 10:
            cone.res_vol = -cone.volume
        else:
            cone.res_vol = 0.0

    totals.total_vol = totals.strakes_vol + totals.expan_vol + s.other_vol + totals.cones_vol

    totals.lab_misc_tot = s.lab_misc_hrs * s.lab_misc_rate
    totals.lab_tot_hours = (
        totals.lab_cones_hrs + totals.lab_strakes_hrs + s.lab_misc_hrs + s.lab_components_hrs
    )
    totals.labour_tot = (
        totals.lab_cones_amt
        + totals.lab_strakes_amt
        + totals.lab_misc_tot
        + s.lab_components_amt
    )

    sub_tot = s.components_price + sum(s.comp)
    if sub_tot > 0:
        totals.comp_markup_amt = sub_tot / 100 * s.comp_markup_percent
    totals.comp_tot_inc_markup = sub_tot + totals.comp_markup_amt

    totals.single_tank_steel = totals.steel_total
    totals.single_tank_comp = totals.comp_tot_inc_markup
    totals.single_tank_lab = totals.labour_tot
    totals.single_tank_less_gst = (
        totals.single_tank_steel
        + totals.single_tank_comp
        + totals.single_tank_lab
        + sum(s.single_add_on)
    )

    price_quoted = s.price_quoted if s.price_quoted > 0 else totals.single_tank_less_gst
    totals.single_tank_inc_gst = price_quoted * s.gst

    num_tanks = s.num_tanks if s.num_tanks > 0 else 1
    totals.multi_tanks_single = price_quoted
    totals.multi_tanks_price = num_tanks * totals.multi_tanks_single
    totals.multi_tanks_tot_less_gst = totals.multi_tanks_price + sum(s.multi_add_on)
    totals.multi_tanks_inc_gst = totals.multi_tanks_tot_less_gst * s.gst

    return totals


def temperature_correction_factor(temp_c: int) -> float:
    """Return 1/Factor(temp) used for volume correction display."""
    factor = _DENSITY_FACTORS.get(temp_c, 1.0)
    return 1.0 / factor
