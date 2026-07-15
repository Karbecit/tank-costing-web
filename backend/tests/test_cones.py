from pathlib import Path

import pytest

from app.calc.cones import calc_cone_height, calculate_cone, sand_height
from app.calc.constants import CONIC_SEL, OFFSET_SEL, SLOPE_SEL
from app.jma.reader import load_jma, load_jma_cones, load_jma_tank_diam
from app.models.cone import Cone, ConeCalcContext

# Legacy sample costings (sibling folder to tank-costing-web)
LEGACY_COSTINGS = (
    Path(__file__).resolve().parents[3]
    / "Old Program"
    / "Code"
    / "Costings"
)

PETTAVEL = LEGACY_COSTINGS / "Pettavel 1350 Lit stackable tank 1200 diam 1500 wall 20-7-0.jma"
STORAGE_5KL = (
    LEGACY_COSTINGS
    / (
        "A JMA Engineering ( Stock ) 5 KL storage tank 1600 diam 2400 wall "
        "2.5 deg floor 304st on Plinth 10-5-11.jma"
    )
)

REL = 1e-3  # 0.1% — matches VB6 double precision in saved .jma files


def _input_cone(stored: Cone) -> Cone:
    """Strip computed fields so we recalculate from geometry inputs only."""
    c = Cone(
        name=stored.name,
        height_select=stored.height_select,
        angle_select=stored.angle_select,
        conic_select=stored.conic_select,
        offset_select=stored.offset_select,
        slope_select=stored.slope_select,
        diam_large=stored.diam_large,
        diam_small=stored.diam_small,
        height=stored.height if stored.height_select else 0.0,
        angle=stored.angle if stored.angle_select else 0.0,
        offset_amt=stored.offset_amt,
        knuckle_rad=stored.knuckle_rad,
        sand_height=stored.sand_height,
        skirt=stored.skirt,
        waste=stored.waste,
        thick=stored.thick,
        width=stored.width,
        weight_cucm=stored.weight_cucm,
        price_kg=stored.price_kg,
        num_hours=stored.num_hours,
        grade=stored.grade,
        volume_treat=stored.volume_treat,
    )
    # Height/angle mode: keep the driving dimension from file
    if stored.height_select:
        c.height = stored.height
    if stored.angle_select:
        c.angle = stored.angle
    return c


@pytest.fixture
def legacy_available() -> bool:
    return PETTAVEL.is_file() and STORAGE_5KL.is_file()


def test_sand_height_small_tank():
    assert sand_height(1200) == pytest.approx(12.0)


def test_sand_height_large_tank():
    assert sand_height(5000) == pytest.approx(5000 / 66.6, rel=REL)


def test_calc_cone_height_pettavel_top_cone():
    """Top conical cone — angle-selected, 10° slope, 30 mm knuckle."""
    cone = Cone(
        conic_select=1,
        diam_large=1200,
        diam_small=450,
        knuckle_rad=30,
        angle=10,
        angle_select=True,
    )
    height = calc_cone_height(cone, 10)
    assert height == pytest.approx(91.2956067092219, rel=REL)


@pytest.mark.skipif(not PETTAVEL.is_file(), reason="Legacy Pettavel .jma not found")
class TestPettavelJma:
    def test_load_tank_diam(self):
        assert load_jma_tank_diam(PETTAVEL) == pytest.approx(1200)

    def test_top_cone_volume(self):
        cones, diam = load_jma(PETTAVEL)
        stored = cones[0]
        assert stored.cone_stat == CONIC_SEL

        ctx = ConeCalcContext(tank_diam=diam)
        result = calculate_cone(_input_cone(stored), ctx)

        assert result.height == pytest.approx(stored.height, rel=REL)
        assert result.volume == pytest.approx(stored.volume, rel=REL)
        assert result.length == pytest.approx(stored.length, rel=REL)
        assert result.surface_area == pytest.approx(stored.surface_area, rel=REL)
        assert result.knuck_vol == pytest.approx(stored.knuck_vol, rel=REL)


@pytest.mark.skipif(not STORAGE_5KL.is_file(), reason="Legacy 5 KL .jma not found")
class TestStorage5KlJma:
    def test_offset_top_cone(self):
        cones, diam = load_jma(STORAGE_5KL)
        stored = cones[0]
        assert stored.cone_stat == OFFSET_SEL

        ctx = ConeCalcContext(tank_diam=diam)
        result = calculate_cone(_input_cone(stored), ctx)

        assert result.volume == pytest.approx(stored.volume, rel=REL)
        assert result.length == pytest.approx(stored.length, rel=REL)
        assert result.min_angle == pytest.approx(stored.min_angle, rel=REL)
        assert result.max_angle == pytest.approx(stored.max_angle, rel=REL)

    def test_slope_bottom_floor(self):
        cones, diam = load_jma(STORAGE_5KL)
        stored = cones[3]
        assert stored.cone_stat == SLOPE_SEL
        assert stored.name.strip().lower().startswith("bottom floor")

        ctx = ConeCalcContext(tank_diam=diam)
        result = calculate_cone(_input_cone(stored), ctx)

        assert result.height == pytest.approx(stored.height, rel=REL)
        assert result.knuck_vol == pytest.approx(stored.knuck_vol, rel=REL)
        assert result.length == pytest.approx(stored.length, rel=REL)
        assert result.surface_area == pytest.approx(stored.surface_area, rel=REL)
        # Volume includes skirt contribution — compare to stored value
        assert result.volume == pytest.approx(stored.volume, rel=REL)


@pytest.mark.parametrize(
    "filename",
    [
        PETTAVEL.name,
        STORAGE_5KL.name,
    ],
)
def test_jma_cone_count(filename: str):
    path = LEGACY_COSTINGS / filename
    if not path.is_file():
        pytest.skip(f"{filename} not available")
    cones = load_jma_cones(path)
    assert len(cones) == 5
