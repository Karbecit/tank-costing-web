"""Full costing calculation — cones, strakes, and summary totals."""

from __future__ import annotations

from dataclasses import dataclass

from app.calc.cones import calculate_cone
from app.calc.strakes import calculate_strake
from app.calc.summary import calc_summary_totals
from app.models.cone import Cone, ConeCalcContext
from app.models.strake import Strake
from app.models.summary import SummaryInput, SummaryTotals


@dataclass
class CostingResult:
    cones: list[Cone]
    strakes: list[Strake]
    totals: SummaryTotals


def calculate_costing(
    cones: list[Cone],
    strakes: list[Strake],
    summary: SummaryInput,
    cones_rate_per_hour: float = 0.0,
) -> CostingResult:
    """Recalculate all cones, strakes, and summary totals."""
    tank_diam = summary.diam
    ctx = ConeCalcContext(tank_diam=tank_diam, cones_rate_per_hour=cones_rate_per_hour)

    calc_cones = [calculate_cone(c, ctx) for c in cones]
    calc_strakes = [calculate_strake(s, tank_diam) for s in strakes]
    totals = calc_summary_totals(calc_cones, calc_strakes, summary)

    return CostingResult(cones=calc_cones, strakes=calc_strakes, totals=totals)
