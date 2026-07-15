from pydantic import BaseModel, Field

from app.models.cone import Cone


class ConeInputSchema(BaseModel):
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
    offset_amt: float = 0.0
    knuckle_rad: float = 0.0
    sand_height: float = 0.0
    skirt: float = 0.0
    waste: float = 0.0
    thick: float = 0.0
    width: float = 0.0
    weight_cucm: float = Field(0.0, alias="weight_cucm")
    price_kg: float = 0.0
    num_hours: float = 0.0
    grade: str = ""
    volume_treat: int = 0

    model_config = {"populate_by_name": True}

    def to_cone(self) -> Cone:
        return Cone(**self.model_dump(by_alias=False))


class ConeCalcRequest(BaseModel):
    cone: ConeInputSchema
    tank_diam: float = Field(..., gt=0, description="Tank barrel diameter (mm)")
    cones_rate_per_hour: float = Field(0.0, ge=0)


class ConeResultSchema(BaseModel):
    name: str
    cone_stat: int
    diam_large: float
    diam_small: float
    height: float
    angle: float
    min_angle: float
    max_angle: float
    length: float
    volume: float
    area: float
    surface_area: float
    knuck_vol: float
    knuckle_rad: float
    tank_area: float
    weight: float
    steel_price: float
    coil_length: float

    @classmethod
    def from_cone(cls, cone: Cone) -> "ConeResultSchema":
        return cls(
            name=cone.name.strip(),
            cone_stat=cone.cone_stat,
            diam_large=cone.diam_large,
            diam_small=cone.diam_small,
            height=cone.height,
            angle=cone.angle,
            min_angle=cone.min_angle,
            max_angle=cone.max_angle,
            length=cone.length,
            volume=cone.volume,
            area=cone.area,
            surface_area=cone.surface_area,
            knuck_vol=cone.knuck_vol,
            knuckle_rad=cone.knuckle_rad,
            tank_area=cone.tank_area,
            weight=cone.weight,
            steel_price=cone.steel_price,
            coil_length=cone.coil_length,
        )
