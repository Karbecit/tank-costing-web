"""Tests for strake and summary calculation engines."""

from pathlib import Path

import pytest

from app.calc.costing import calculate_costing
from app.calc.strakes import calculate_strake
from app.jma.reader import load_jma_full, load_jma_strakes
from app.models.cone import Cone
from app.models.strake import Strake

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

REL = 1e-3


def _input_cone(stored: Cone) -> Cone:
    c = Cone(
        name=stored.name,
        height_select=stored.height_select,
        angle_select=stored.angle_select,
        conic_select=stored.conic_select,
        offset_select=stored.offset_select,
        slope_select=stored.slope_select,
        diam_large=stored.diam_large,
        diam_small=stored.diam_small,
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
    if stored.height_select:
        c.height = stored.height
    if stored.angle_select:
        c.angle = stored.angle
    return c


def _input_strake(stored: Strake) -> Strake:
    return Strake(
        used=stored.used,
        name=stored.name,
        num_iden_strakes=stored.num_iden_strakes,
        trim_strakes=stored.trim_strakes,
        grade=stored.grade,
        thick=stored.thick,
        width=stored.width,
        weight_cucm=stored.weight_cucm,
        coil_length=stored.coil_length,
        price_kg=stored.price_kg,
        num_hours=stored.num_hours,
        rate_hour=stored.rate_hour,
        volume_treat=stored.volume_treat,
    )


@pytest.mark.skipif(not PETTAVEL.is_file(), reason="Legacy Pettavel .jma not found")
class TestPettavelStrakes:
    def test_top_strake(self):
        strakes = load_jma_strakes(PETTAVEL)
        stored = strakes[0]
        assert stored.is_active

        result = calculate_strake(_input_strake(stored), 1200)

        assert result.volume == pytest.approx(stored.volume, rel=REL)
        assert result.steel_price == pytest.approx(stored.steel_price, rel=REL)
        assert result.strake_area == pytest.approx(stored.strake_area, rel=REL)
        assert result.weight == pytest.approx(stored.weight, rel=REL)


@pytest.mark.skipif(not PETTAVEL.is_file(), reason="Legacy Pettavel .jma not found")
class TestPettavelFullCosting:
    def test_summary_totals(self):
        cones, strakes, summary, stored = load_jma_full(PETTAVEL)
        result = calculate_costing(
            [_input_cone(c) for c in cones],
            [_input_strake(s) for s in strakes],
            summary,
        )
        t = result.totals

        assert t.total_vol == pytest.approx(stored.total_vol, rel=REL)
        assert t.cones_vol == pytest.approx(stored.cones_vol, rel=REL)
        assert t.strakes_vol == pytest.approx(stored.strakes_vol, rel=REL)
        assert t.tot_cone_height == pytest.approx(stored.tot_cone_height, rel=REL)
        assert t.tot_strake_height == pytest.approx(stored.tot_strake_height, rel=REL)
        assert t.strake_total == pytest.approx(stored.strake_total, rel=REL)
        assert t.cone_total == pytest.approx(stored.cone_total, rel=REL)
        assert t.steel_total == pytest.approx(stored.steel_total, rel=REL)


@pytest.mark.skipif(not STORAGE_5KL.is_file(), reason="Legacy 5 KL .jma not found")
class TestStorage5KlFullCosting:
    def test_summary_volumes(self):
        cones, strakes, summary, stored = load_jma_full(STORAGE_5KL)
        result = calculate_costing(
            [_input_cone(c) for c in cones],
            [_input_strake(s) for s in strakes],
            summary,
        )
        t = result.totals

        assert t.total_vol == pytest.approx(stored.total_vol, rel=REL)
        assert t.tot_strake_height == pytest.approx(stored.tot_strake_height, rel=REL)
