from datetime import datetime
from typing import List, Optional, NewType, Set, TypeVar, Type, Any, Callable
import pandas as pd
from dateutil import parser


from csvqb.utils.dict import get_from_dict_ensure_exists, get_with_func_or_none
from csvqb.models.validationerror import ValidationError
from .columns import CsvColumn
from .qb.columns import QbColumn
from .qb.components.component import QbComponent
from .qb.components.measure import QbMultiMeasureTypes
from .qb.components.observedvalue import QbObservationValue, QbSingleMeasureObservationValue, \
    QbMultiMeasureObservationValue


URI = NewType('URI', str)
ComponentType = TypeVar("ComponentType", bound=QbComponent)


class CubeMetadata:
    base_uri: str
    dataset_identifier: str

    title: str
    summary: Optional[str]
    description: Optional[str]
    creator: Optional[URI]
    publisher: Optional[URI]
    issued: Optional[datetime]
    # modified: datetime # Should modified be in here or be automatically updated by the script?
    themes: List[str]
    keywords: List[str]
    landing_page: Optional[URI]
    license: Optional[URI]
    public_contact_point: Optional[URI]

    def __init__(self, config: dict = {}):
        self.base_uri = get_from_dict_ensure_exists(config, "baseUri")  # todo: check
        self.dataset_identifier = get_from_dict_ensure_exists(config, "datasetIdentifier")  # todo: check

        self.title = get_from_dict_ensure_exists(config, "title")
        self.summary = config.get("summary")
        self.description = config.get("description")
        self.creator = get_with_func_or_none(config, "creator", URI)
        self.publisher = get_with_func_or_none(config, "publisher", URI)
        self.issued = get_with_func_or_none(config, "published", parser.parse)
        self.themes = config.get("families", [])
        self.keywords = config.get("keywords", [])
        self.landing_page = config.get("landingPage")
        self.license = config.get("license")
        self.public_contact_point = config.get("contactUri")

    def validate(self) -> List[ValidationError]:
        raise Exception("Not implemented yet.")


class Cube:
    metadata: CubeMetadata
    columns: List[CsvColumn]
    data: Optional[pd.DataFrame]

    def __init__(self,
                 metadata: CubeMetadata,
                 data: Optional[pd.DataFrame] = None,
                 columns: List[CsvColumn] = []):
        self.metadata = metadata
        self.data = data
        self.columns = columns

    def validate(self) -> List[ValidationError]:
        # self.metadata.validate() # todo: uncomment this when implemented
        return self._validate_columns()

    def _validate_columns(self) -> List[ValidationError]:
        # todo: If no columns are defined give a warning?
        errors = self._validate_columns_unique_and_in_data()
        errors += self._validate_observation_value_constraints()

        return errors

    def _validate_observation_value_constraints(self) -> List[ValidationError]:
        errors: List[ValidationError] = []
        observed_value_columns = self.get_columns_of_type(QbObservationValue)
        # assert validation specific to csv-qb
        # we only currently support one shape of multi-measure input. And that leaves us with oen
        if len(observed_value_columns) != 1:
            errors.append(
                ValidationError(f"Found {len(observed_value_columns)} observation value columns. Expected 1."))
        else:
            single_measure_obs_val_columns = self.get_columns_of_type(QbSingleMeasureObservationValue)
            multi_measure_obs_val_columns = self.get_columns_of_type(QbMultiMeasureObservationValue)
            if len(single_measure_obs_val_columns) == 1:
                pass
            elif len(multi_measure_obs_val_columns) == 1:
                multi_measure_types_columns = self.get_columns_of_type(QbMultiMeasureTypes)
                if len(multi_measure_types_columns) == 0:
                    errors.append(ValidationError(
                        f"Cube is defined as multi-measure but measure type column has not been specified."
                    ))
                elif len(multi_measure_types_columns) > 1:
                    errors.append(ValidationError("Multiple measure type columns have been defined."))

        return errors

    def _validate_columns_unique_and_in_data(self):
        errors: List[ValidationError] = []
        existing_col_titles: Set[str] = set()
        for col in self.columns:
            if col.csv_column_title in existing_col_titles:
                errors.append(ValidationError(f"Duplicate column title '{col.csv_column_title}'"))

            column_data = None
            if self.data is not None:
                if col.csv_column_title not in self.data.columns:
                    errors.append(ValidationError(f"Column '{col.csv_column_title}' not found in data provided."))
                column_data = self.data[column_data]

            errors += col.validate(column_data)
        return errors

    def get_columns_of_type(self, t: Type[ComponentType]) -> List[CsvColumn[ComponentType]]:
        return [c for c in self.columns if isinstance(c, QbColumn) and isinstance(c.component, t)]
