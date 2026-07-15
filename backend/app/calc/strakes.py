"""Strake calculation engine — port of VB6 Strakes.bas CalcStrakes."""

from __future__ import annotations

from copy import deepcopy

from app.calc.constants import PI
from app.models.strake import Strake


def calculate_strake(strake: Strake, tank_diam: float) -> Strake:
    """
    Calculate strake geometry, volume, and steel pricing.
    Port of CalcStrakes without UI side-effects.
    """
    result = deepcopy(strake)
    if not result.is_active or tank_diam <= 0:
        return result

    circum = PI * tank_diam
    result.resultant_width = result.width - result.trim_strakes
    if result.coil_length == 0:
        result.coil_length = circum

    result.strake_area = result.coil_length * result.resultant_width / 10000
    result.coil_volume = result.strake_area * result.thick / 10
    result.volume = (PI * (tank_diam / 2) ** 2) * result.resultant_width / 1_000_000

    if result.coil_volume > 0:
        result.weight = result.weight_cucm / (1 / result.coil_volume) / 10000
        result.steel_price = result.weight * result.price_kg

    result.lab_price = result.num_hours * result.rate_hour
    return result
