from fastapi import APIRouter

from app.calc.cones import calculate_cone
from app.calc.costing import calculate_costing
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

router = APIRouter(prefix="/api/calc", tags=["calculations"])


@router.post("/cone", response_model=ConeResultSchema)
def calc_cone(body: ConeCalcRequest):
    """Calculate cone geometry, volume, and steel from input dimensions."""
    ctx = ConeCalcContext(
        tank_diam=body.tank_diam,
        cones_rate_per_hour=body.cones_rate_per_hour,
    )
    result = calculate_cone(body.cone.to_cone(), ctx)
    return ConeResultSchema.from_cone(result)


@router.post("/strake", response_model=StrakeResultSchema)
def calc_strake(body: StrakeCalcRequest):
    """Calculate strake volume and steel from input dimensions."""
    result = calculate_strake(body.strake.to_strake(), body.tank_diam)
    return StrakeResultSchema.from_strake(result)


@router.post("/costing", response_model=CostingCalcResponse)
def calc_full_costing(body: CostingCalcRequest):
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
