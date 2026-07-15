from dataclasses import dataclass


@dataclass
class Strake:
    """Tank barrel strake — mirrors VB6 Strakes type."""

    used: int = 0
    name: str = ""
    num_iden_strakes: int = 1
    trim_strakes: float = 0.0
    grade: str = ""
    thick: float = 0.0
    width: float = 0.0
    weight_cucm: float = 0.0
    coil_length: float = 0.0
    price_kg: float = 0.0
    num_hours: float = 0.0
    rate_hour: float = 0.0
    volume_treat: int = 0
    waste: float = 0.0
    height: float = 0.0
    # Computed fields
    resultant_width: float = 0.0
    strake_area: float = 0.0
    coil_volume: float = 0.0
    volume: float = 0.0
    weight: float = 0.0
    steel_price: float = 0.0
    lab_price: float = 0.0
    res_height: float = 0.0
    res_vol: float = 0.0

    @property
    def is_active(self) -> bool:
        return self.used == 1
