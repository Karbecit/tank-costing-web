from dataclasses import dataclass, field


@dataclass
class SummaryInput:
    """Summary-level inputs needed for totals — mirrors key VB6 Summary fields."""

    diam: float = 0.0
    expan_diam: float = 0.0
    expan_height: float = 0.0
    other_vol: float = 0.0
    coil_mark_up_percent: float = 0.0
    coil_misc: float = 0.0
    floor_multi_tot: float = 0.0
    components_price: float = 0.0
    comp: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])
    comp_markup_percent: float = 0.0
    gst: float = 1.1
    num_tanks: int = 1
    price_quoted: float = 0.0
    lab_misc_hrs: float = 0.0
    lab_misc_rate: float = 0.0
    lab_components_hrs: float = 0.0
    lab_components_amt: float = 0.0
    single_add_on: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    multi_add_on: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    temp_comp: int = 4
    res_barrel_height: float = 0.0


@dataclass
class SummaryTotals:
    """Computed summary totals from CalcSumTotals."""

    cone_total: float = 0.0
    strake_total: float = 0.0
    lab_cones_amt: float = 0.0
    lab_cones_hrs: float = 0.0
    lab_strakes_amt: float = 0.0
    lab_strakes_hrs: float = 0.0
    steel_sub_tot: float = 0.0
    steel_mark_up_amount: float = 0.0
    steel_total: float = 0.0
    expan_vol: float = 0.0
    tot_strake_height: float = 0.0
    tot_cone_height: float = 0.0
    res_barrel_height: float = 0.0
    tank_height: float = 0.0
    strakes_vol: float = 0.0
    cones_vol: float = 0.0
    total_vol: float = 0.0
    lab_misc_tot: float = 0.0
    labour_tot: float = 0.0
    lab_tot_hours: float = 0.0
    comp_markup_amt: float = 0.0
    comp_tot_inc_markup: float = 0.0
    single_tank_steel: float = 0.0
    single_tank_comp: float = 0.0
    single_tank_lab: float = 0.0
    single_tank_less_gst: float = 0.0
    single_tank_inc_gst: float = 0.0
    multi_tanks_single: float = 0.0
    multi_tanks_price: float = 0.0
    multi_tanks_tot_less_gst: float = 0.0
    multi_tanks_inc_gst: float = 0.0
