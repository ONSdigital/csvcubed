"""
ColumnComponentInfo
-------------------

Will be filled out
"""

from dataclasses import dataclass
from typing import Optional

from csvcubed.models.sparqlresults import ColumnDefinition, QubeComponentResult
from csvcubed.utils.qb.components import EndUserColumnType


@dataclass
class ColumnComponentInfo:
    """Needs to be filled in"""

    component_type: EndUserColumnType
    component: Optional[QubeComponentResult]
    column_definition: ColumnDefinition
    # Either store the values in the class as a Dict or return them to the function it's calling
