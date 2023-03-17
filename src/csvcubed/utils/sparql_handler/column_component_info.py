"""
ColumnComponentInfo
-------------------

Provides access to mapping between CSV columns.
"""

from dataclasses import dataclass
from typing import Optional

from csvcubed.models.sparqlresults import ColumnDefinition, QubeComponentResult
from csvcubed.utils.qb.components import EndUserColumnType


@dataclass
class ColumnComponentInfo:
    """This class holds information for mapping between CSV columns"""

    component_type: EndUserColumnType
    component: Optional[QubeComponentResult]
    column_definition: ColumnDefinition
    # Either store the values in the class as a Dict or return them to the function it's calling
