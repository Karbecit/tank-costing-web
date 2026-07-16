from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.auth.dependencies import CurrentUser, get_current_user, require_role
from app.calc.cones import calculate_cone
from app.calc.costing import calculate_costing
from app.calc.dip_chart import calc_single_dip_chart
from app.calc.strakes import calculate_strake
from app.models.cone import ConeCalcContext
from app.schemas.cone import ConeCalcRequest, ConeResultSchema
from app.schemas.costing import (
    CostingCalcRequest,
    CostingCalcResponse,
    StrakeCalcRequest,
    StrakeResultSchema,
    SummaryTotalsSchema,
)
from app.services.jma_service import payload_to_models

router = APIRouter(prefix="/api/calc", tags=["calculations"])
_user = Annotated[CurrentUser, Depends(get_current_user)]
_editor = Annotated[CurrentUser, Depends(require_role("editor"))]


class DipChartRequest(BaseModel):
    payload: dict
    increment_mm: int = Field(10, ge=1, le=100)
    top_cone: int = Field(0, ge=0, le=4)
    bottom_cone: int = Field(2, ge=0, le=4)
    invert_cone: int = Field(2, ge=0, le=4)


@router.post("/cone", response_model=ConeResultSchema)
def calc_cone(body: ConeCalcRequest, _user: _editor):
    """Calculate cone geometry, volume, and steel from input dimensions."""
    ctx = ConeCalcContext(
        tank_diam=body.tank_diam,
        cones_rate_per_hour=body.cones_rate_per_hour,
    )
    result = calculate_cone(body.cone.to_cone(), ctx)
    return ConeResultSchema.from_cone(result)


@router.post("/strake", response_model=StrakeResultSchema)
def calc_strake(body: StrakeCalcRequest, _user: _editor):
    """Calculate strake volume and steel from input dimensions."""
    result = calculate_strake(body.strake.to_strake(), body.tank_diam)
    return StrakeResultSchema.from_strake(result)


@router.post("/costing", response_model=CostingCalcResponse)
def calc_full_costing(body: CostingCalcRequest, _user: _editor):
    """Calculate all cones, strakes, and summary totals for a tank costing."""
    result = calculate_costing(
        [c.to_cone() for c in body.cones],
        [s.to_strake() for s in body.strakes],
        body.summary.to_summary(),
        cones_rate_per_hour=body.cones_rate_per_hour,
    )
    return CostingCalcResponse(
        cones=[ConeResultSchema.from_cone(c) for c in result.cones],
        strakes=[StrakeResultSchema.from_strake(s) for s in result.strakes],
        totals=SummaryTotalsSchema.from_totals(result.totals),
    )


@router.post("/dip-chart")
def calc_dip_chart(body: DipChartRequest, _user: _user):
    """Single-tank dip chart table (mm from top → litres)."""
    cones, strakes, summary, rate = payload_to_models(body.payload)
    result = calculate_costing(cones, strakes, summary, cones_rate_per_hour=rate)
    return calc_single_dip_chart(
        result.cones,
        summary,
        result.totals,
        top_cone=body.top_cone,
        bottom_cone=body.bottom_cone,
        invert_cone=body.invert_cone,
        increment=body.increment_mm,
    )
