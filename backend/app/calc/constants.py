"""Constants ported from VB6 Declarations.bas and PlotDeclarations.bas."""

import math

PI = math.pi
FAC = PI / 180  # degrees to radians (VB6 Fac)

NUM_CONES = 5
NUM_TYPE_STRAKES = 8
CONE_FIELDS = 40
STRAKE_FIELDS = 24

# Cone selection states (Declarations.bas)
NONE_SEL = 0
CONIC_SEL = 1
OFFSET_SEL = 2
SLOPE_SEL = 4
INIT_SEL = 5

# Slope / sand helpers (PlotDeclarations.bas, Declarations.bas)
SQCIRC = 0.7853981
SANDHIGH1 = 100.0  # 10 mm/m for tanks <= 4 m diameter
SANDHIGH2 = 66.6  # 15 mm/m for tanks > 4 m diameter

SUMMARY_FIELDS_BEFORE_DIAM = 20  # kept for reference; use SUMMARY_FIELD in jma/summary_fields.py
