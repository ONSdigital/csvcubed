"""
CSV Dataset
-----------

Utilities for CSV Datasets
"""

from enum import Enum


class CanonicalShapeRequiredCols(Enum):
    """
    The type uris of component properties.
    """

    Measure = "Measure"
    """ Measure column """

    Unit = "Unit"
    """ Unit (of measure) column """
