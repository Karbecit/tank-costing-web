from dataclasses import dataclass, field

from app.calc.constants import CONIC_SEL, NONE_SEL, OFFSET_SEL, SLOPE_SEL


@dataclass
class Cone:
    """Tank cone / floor segment — mirrors VB6 ConicalCone type."""

    name: str = ""
    height_select: bool = False
    angle_select: bool = False
    conic_select: int = 0
    offset_select: int = 0
    slope_select: int = 0
    diam_large: float = 0.0
    diam_small: float = 0.0
    height: float = 0.0
    angle: float = 0.0
    min_angle: float = 0.0
    max_angle: float = 0.0
    offset_amt: float = 0.0
    knuckle_rad: float = 0.0
    sand_height: float = 0.0
    skirt: float = 0.0
    waste: float = 0.0
    thick: float = 0.0
    width: float = 0.0
    weight_cucm: float = 0.0
    price_kg: float = 0.0
    num_hours: float = 0.0
    grade: str = ""
    volume_treat: int = 0
    # Computed / persisted fields (populated by calculate_cone or loaded from .jma)
    cone_stat: int = field(default=NONE_SEL, init=False)
    tank_area: float = 0.0
    knuck_add_height: float = 0.0
    knuckle_red_width: float = 0.0
    knuckle_length: float = 0.0
    knuck_vol: float = 0.0
    knuckle_area: float = 0.0
    length: float = 0.0
    area: float = 0.0
    surface_area: float = 0.0
    volume: float = 0.0
    coil_length: float = 0.0
    coil_volume: float = 0.0
    weight: float = 0.0
    steel_price: float = 0.0
    skirt_vol: float = 0.0
    lab_price: float = 0.0
    offset_cl_amt: float = 0.0
    res_height: float = 0.0
    res_vol: float = 0.0

    def __post_init__(self) -> None:
        self.cone_stat = self._derive_cone_stat()

    def _derive_cone_stat(self) -> int:
        if self.conic_select == 1:
            return CONIC_SEL
        if self.offset_select == 1:
            return OFFSET_SEL
        if self.slope_select == 1:
            return SLOPE_SEL
        if self.conic_select == 0 and self.offset_select == 0 and self.slope_select == 0:
            return NONE_SEL
        return NONE_SEL

    @property
    def is_active(self) -> bool:
        return self.cone_stat in (CONIC_SEL, OFFSET_SEL, SLOPE_SEL)


@dataclass
class ConeCalcContext:
    """Inputs that come from the tank summary rather than the cone record."""

    tank_diam: float = 0.0
    cones_rate_per_hour: float = 0.0
