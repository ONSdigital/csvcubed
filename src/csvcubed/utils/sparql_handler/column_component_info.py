"""
ColumnComponentInfo
-------------------

Contains the `ColumnComponentInfo` class which relates CSV Columns back to their qube-config.json
style column types and the underlying RDF Data Cube DataStructureDefinition Components.
"""

from dataclasses import dataclass
from typing import Optional

from csvcubed.models.sparqlresults import ColumnDefinition, QubeComponentResult
from csvcubed.utils.qb.components import EndUserColumnType


@dataclass
class ColumnComponentInfo:
    """
    Relates CSV Columns back to their qube-config.json style column types and the underlying RDF Data Cube
      DataStructureDefinition Components.
    """

    column_definition: ColumnDefinition
    column_type: EndUserColumnType
    component: Optional[QubeComponentResult]
    """
    The component may be None in situations such as:
        * The column is marked as `suppressed`,
        * The column is an observations column in a standard shape cube. 
    """
