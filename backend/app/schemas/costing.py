from pydantic import BaseModel, Field

from app.models.strake import Strake
from app.models.summary import SummaryInput, SummaryTotals
from app.schemas.cone import ConeInputSchema, ConeResultSchema


class StrakeInputSchema(BaseModel):
    used: int = 0
    name: str = ""
    num_iden_strakes: int = 1
    trim_strakes: float = 0.0
    grade: str = ""
    thick: float = 0.0
    width: float = 0.0
    weight_cucm: float = Field(0.0, alias="weight_cucm")
    coil_length: float = 0.0
    price_kg: float = 0.0
    num_hours: float = 0.0
    rate_hour: float = 0.0
    volume_treat: int = 0

    model_config = {"populate_by_name": True}

    def to_strake(self) -> Strake:
        return Strake(**self.model_dump(by_alias=False))


class StrakeCalcRequest(BaseModel):
    strake: StrakeInputSchema
    tank_diam: float = Field(..., gt=0)


class StrakeResultSchema(BaseModel):
    name: str
    volume: float
    strake_area: float
    coil_volume: float
    weight: float
    steel_price: float
    lab_price: float
    resultant_width: float

    @classmethod
    def from_strake(cls, strake: Strake) -> "StrakeResultSchema":
        return cls(
            name=strake.name.strip(),
            volume=strake.volume,
            strake_area=strake.strake_area,
            coil_volume=strake.coil_volume,
            weight=strake.weight,
            steel_price=strake.steel_price,
            lab_price=strake.lab_price,
            resultant_width=strake.resultant_width,
        )


class SummaryInputSchema(BaseModel):
    diam: float = Field(..., gt=0)
    expan_diam: float = 0.0
    expan_height: float = 0.0
    other_vol: float = 0.0
    coil_mark_up_percent: float = 0.0
    coil_misc: float = 0.0
    floor_multi_tot: float = 0.0
    components_price: float = 0.0
    comp: list[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])
    comp_markup_percent: float = 0.0
    gst: float = 1.1
    num_tanks: int = 1
    price_quoted: float = 0.0
    lab_misc_hrs: float = 0.0
    lab_misc_rate: float = 0.0
    lab_components_hrs: float = 0.0
    lab_components_amt: float = 0.0
    single_add_on: list[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    multi_add_on: list[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])

    def to_summary(self) -> SummaryInput:
        return SummaryInput(**self.model_dump())


class CostingCalcRequest(BaseModel):
    cones: list[ConeInputSchema]
    strakes: list[StrakeInputSchema]
    summary: SummaryInputSchema
    cones_rate_per_hour: float = Field(0.0, ge=0)


class SummaryTotalsSchema(BaseModel):
    cone_total: float
    strake_total: float
    steel_sub_tot: float
    steel_mark_up_amount: float
    steel_total: float
    expan_vol: float
    tot_strake_height: float
    tot_cone_height: float
    tank_height: float
    strakes_vol: float
    cones_vol: float
    total_vol: float
    labour_tot: float
    comp_tot_inc_markup: float
    single_tank_less_gst: float
    single_tank_inc_gst: float

    @classmethod
    def from_totals(cls, totals: SummaryTotals) -> "SummaryTotalsSchema":
        return cls(
            cone_total=totals.cone_total,
            strake_total=totals.strake_total,
            steel_sub_tot=totals.steel_sub_tot,
            steel_mark_up_amount=totals.steel_mark_up_amount,
            steel_total=totals.steel_total,
            expan_vol=totals.expan_vol,
            tot_strake_height=totals.tot_strake_height,
            tot_cone_height=totals.tot_cone_height,
            tank_height=totals.tank_height,
            strakes_vol=totals.strakes_vol,
            cones_vol=totals.cones_vol,
            total_vol=totals.total_vol,
            labour_tot=totals.labour_tot,
            comp_tot_inc_markup=totals.comp_tot_inc_markup,
            single_tank_less_gst=totals.single_tank_less_gst,
            single_tank_inc_gst=totals.single_tank_inc_gst,
        )


class CostingCalcResponse(BaseModel):
    cones: list[ConeResultSchema]
    strakes: list[StrakeResultSchema]
    totals: SummaryTotalsSchema
