import logging
import re
from dataclasses import dataclass, field
from typing import Optional, List

from csvcubed.models.cube import (
    ExistingQbUnit,
    QbUnit,
    NewQbUnit,
    QbColumn,
    QbObservationValue,
    QbCube,
    QbAttribute,
    QbMultiUnits,
    QbDimension,
    NewQbMeasure,
    ExistingQbMeasure,
    ExistingQbDimension,
    NewQbDimension,
    ExistingQbAttribute,
    NewQbAttribute,
    CsvColumn,
    QbCodeList,
    ExistingQbCodeList,
    NewQbCodeList,
    NewQbCodeListInCsvW,
    QbMeasure,
    QbMultiMeasureDimension,
)
from csvcubed.utils.qb.cube import get_columns_of_dsd_type
from csvcubed.utils.uri import csvw_column_name_safe, uri_safe
from csvcubed.writers.urihelpers.qbcube import QbNewUriHelper
from csvcubed.writers.urihelpers.skoscodelist import SkosCodeListNewUriHelper
from csvcubed.writers.urihelpers.skoscodelistconstants import SCHEMA_URI_IDENTIFIER

_logger = logging.getLogger(__name__)


@dataclass
class QbUriHelper:
    cube: QbCube
    _new_uri_helper: QbNewUriHelper = field(init=False)

    def __post_init__(self):
        _logger.debug("Initialising %s", QbUriHelper.__name__)
        self._new_uri_helper = QbNewUriHelper(self.cube)

    def get_dataset_uri(self) -> str:
        return self._new_uri_helper.get_dataset_uri()

    def get_slice_key_across_measures_uri(self) -> str:
        return self._new_uri_helper.get_slice_key_across_measures_uri()

    def get_structure_uri(self) -> str:
        return self._new_uri_helper.get_structure_uri()

    def get_component_uri(self, component_identifier: str) -> str:
        return self._new_uri_helper.get_component_uri(component_identifier)

    def get_class_uri(self, class_identifier: str) -> str:
        return self._new_uri_helper.get_class_uri(class_identifier)

    def get_void_dataset_dependency_uri(self, identifier: str) -> str:
        return self._new_uri_helper.get_void_dataset_dependency_uri(identifier)

    def get_build_activity_uri(self) -> str:
        return self._new_uri_helper.get_build_activity_uri()

    def get_new_attribute_value_uri(
        self, attribute_identifier: str, attribute_value_identifier: str
    ) -> str:
        return self._new_uri_helper.get_attribute_value_uri(
            attribute_identifier, attribute_value_identifier
        )

    def get_dimension_uri(self, dimension: QbDimension) -> str:
        if isinstance(dimension, NewQbDimension):
            dimension_uri = self._new_uri_helper.get_dimension_uri(
                dimension.uri_safe_identifier
            )
            _logger.debug(
                "The dimension is a new dimension with uri '%s'",
                dimension_uri,
            )
            return dimension_uri
        elif isinstance(dimension, ExistingQbDimension):
            dimension_uri = dimension.dimension_uri
            _logger.debug(
                "The dimension is an existing dimension with uri '%s'",
                dimension_uri,
            )
            return dimension_uri
        else:
            raise TypeError(f"Unmatched {QbDimension.__name__} type {type(dimension)}")

    def get_measure_uri(self, measure: QbMeasure) -> str:
        if isinstance(measure, NewQbMeasure):
            measure_uri = self._new_uri_helper.get_measure_uri(
                measure.uri_safe_identifier
            )
            _logger.debug(
                "The measure is a new dimension with uri '%s'",
                measure_uri,
            )
            return measure_uri
        elif isinstance(measure, ExistingQbMeasure):
            measure_uri = measure.measure_uri
            _logger.debug(
                "The measure is an existing dimension with uri '%s'",
                measure_uri,
            )
            return measure_uri
        else:
            raise TypeError(f"Unmatched {QbMeasure.__name__} type {type(measure)}")

    def get_unit_uri(self, unit: QbUnit) -> str:
        if isinstance(unit, ExistingQbUnit):
            return unit.unit_uri
        elif isinstance(unit, NewQbUnit):
            return self._new_uri_helper.get_unit_uri(unit.uri_safe_identifier)
        else:
            raise TypeError(f"Unmatched unit type {type(unit)}")

    def get_attribute_uri(self, attribute: QbAttribute) -> str:
        if isinstance(attribute, NewQbAttribute):
            _logger.debug("The attribute is a new attribute")
            attribute_uri = self._new_uri_helper.get_attribute_uri(
                attribute.uri_safe_identifier
            )
            _logger.debug(
                "The attribute is a new attribute with uri '%s'",
                attribute_uri,
            )
            return attribute_uri
        elif isinstance(attribute, ExistingQbAttribute):
            attribute_uri = attribute.attribute_uri
            _logger.debug(
                "The attribute is an existing attribute with uri '%s'",
                attribute_uri,
            )
            return attribute_uri
        else:
            raise TypeError(f"Unmatched {QbAttribute.__name__} type {type(attribute)}")

    def get_about_url(self) -> str:
        about_url_template = (
            self._get_pivoted_cube_slice_uri()
            if self.cube.is_pivoted_shape
            else self._get_observation_uri_for_standard_shape_data_set()
        )

        _logger.debug("About url template is %s", about_url_template)
        return about_url_template

    def get_about_url_for_csvw_col_in_pivoted_shape_cube(
        self, column: QbColumn
    ) -> Optional[str]:
        obs_val_cols = get_columns_of_dsd_type(self.cube, QbObservationValue)
        is_single_measure = len(obs_val_cols) == 1
        _logger.debug(
            "Getting about url for column with title '%s'", column.csv_column_title
        )

        obs_val_col: Optional[QbColumn[QbObservationValue]]
        # If the column represents a QbObservationValue, then simply assign the obs_val_column to this column.
        if isinstance(column.structural_definition, QbObservationValue):
            _logger.debug("Column is a observation value column")
            obs_val_col = column
        elif isinstance(column.structural_definition, QbAttribute):
            # If the column represents an attribute, set the valueUrl using the _get_observation_value_col_for_title
            # function
            _logger.debug("Column is a an attribute column")
            col_title = column.structural_definition.get_observed_value_col_title()
            obs_val_col = self._get_obs_val_col_for_col_title(
                col_title, obs_val_cols, is_single_measure
            )
        # If the column represents units, set the valueUrl using the _get_observation_value_col_for_title function
        elif isinstance(column.structural_definition, QbMultiUnits):
            _logger.debug("Column is a a multi-unit column")
            col_title = column.structural_definition.observed_value_col_title
            obs_val_col = self._get_obs_val_col_for_col_title(
                col_title, obs_val_cols, is_single_measure
            )
        else:
            obs_val_col = None

        return (
            self._get_observation_uri_for_pivoted_shape_data_set(obs_val_col)
            if obs_val_col is not None
            else None
        )

    @staticmethod
    def get_column_uri_template_fragment(
        column: CsvColumn, escape_value: bool = False
    ) -> str:
        if escape_value:
            return "{" + csvw_column_name_safe(column.uri_safe_identifier) + "}"

        return "{+" + csvw_column_name_safe(column.uri_safe_identifier) + "}"

    def _get_observation_value_col_for_title(
        self, col_title: str
    ) -> QbColumn[QbObservationValue]:
        """
        Gets the matching observation value column for the given attributes/units column (if there is one).
        """
        _logger.debug(
            "Getting the matching observation value column for the column with title '%s'",
            col_title,
        )

        obs_value_columns = get_columns_of_dsd_type(self.cube, QbObservationValue)
        obs_columns_for_column = [
            obs_col
            for obs_col in obs_value_columns
            if col_title == obs_col.csv_column_title
        ]

        num_of_obs_val_cols = len(obs_columns_for_column)
        _logger.debug(
            "Found %d observation value column(s) for the column with title '%s'",
            num_of_obs_val_cols,
            col_title,
        )
        if num_of_obs_val_cols != 1:
            raise Exception(
                f'Could not find one observation value column. Found {num_of_obs_val_cols} for title: "{col_title}".'
            )
        return obs_columns_for_column[0]

    def _get_obs_val_col_for_col_title(
        self,
        col_title: Optional[str],
        obs_val_cols: List[QbColumn[QbObservationValue]],
        is_single_measure: bool,
    ) -> Optional[QbColumn[QbObservationValue]]:
        _logger.debug(
            "Getting observation value column for column title '%s'", col_title
        )
        obs_val_col: Optional[QbColumn[QbObservationValue]] = None

        if is_single_measure:
            obs_val_col = obs_val_cols[0]
            _logger.debug("The cube is a single measure cube.")
        else:
            _logger.debug("The cube is a multi measure cube.")
            if col_title is not None:
                obs_val_col = self._get_observation_value_col_for_title(col_title)

        if obs_val_col is not None:
            _logger.debug(
                "Observation value column for column title '%s' is '%s'",
                col_title,
                obs_val_col.csv_column_title,
            )

        return obs_val_col

    def _get_observation_uri_for_pivoted_shape_data_set(
        self, obs_val_column: QbColumn[QbObservationValue]
    ) -> str:
        """
        Provide the obervation uri for the pivoted shape data set
        """
        _logger.debug(
            "Getting observation uri for the observation value column with title '%s'",
            obs_val_column.csv_column_title,
        )

        dimension_columns_templates: List[str] = []
        for c in self.cube.columns:
            if isinstance(c, QbColumn):
                if isinstance(c.structural_definition, QbDimension):
                    col_template_uri = c.uri_safe_identifier
                    _logger.debug(
                        "Detected a dimension column in the cube, hence setting the column template uri '%s'",
                        col_template_uri,
                    )
                    dimension_columns_templates.append(
                        f"{{{csvw_column_name_safe(col_template_uri)}}}"
                    )

        obs_val_measure = obs_val_column.structural_definition.measure
        assert obs_val_measure is not None
        _logger.debug("Observation value column has a measure")

        if isinstance(obs_val_measure, NewQbMeasure):
            measure_id = obs_val_measure.uri_safe_identifier
            _logger.debug("The measure is a new measure with id '%s'", measure_id)
        elif isinstance(obs_val_measure, ExistingQbMeasure):
            # Yes, this is absolutely nasty, but what else can we do?
            measure_id = uri_safe(obs_val_measure.measure_uri)
            _logger.debug("The measure is an existing measure with id '%s'", measure_id)
        else:
            raise TypeError(f"Unhandled QbMeasure type {type(obs_val_measure)}")

        return self._new_uri_helper.get_observation_uri(
            dimension_columns_templates, measure_id
        )

    def _get_pivoted_cube_slice_uri(self) -> str:
        # TODO: Dimensions are currently appended in the order in which the appear in the cube.
        #       We may want to alter this in the future so that the ordering is from
        #       least entropic dimension -> most entropic.
        #       E.g. http://base-uri/observations/male/1996/all-males-1996

        dimension_columns_templates: List[str] = [
            f"{{{csvw_column_name_safe(c.uri_safe_identifier)}}}"
            for c in get_columns_of_dsd_type(self.cube, QbDimension)
        ]
        _logger.debug(
            "The cube has %d dimension column templates",
            len(dimension_columns_templates),
        )

        return self._new_uri_helper.get_slice_across_measures_uri(
            dimension_columns_templates
        )

    _legacy_external_code_list_pattern = re.compile("^(.*)/concept-scheme/(.*)$")
    _legacy_dataset_local_code_list_pattern = re.compile("^(.*)#scheme/(.*)$")
    _csvcubed_code_list_pattern = re.compile(
        "^(.*)#" + re.escape(SCHEMA_URI_IDENTIFIER) + "$"
    )

    def _get_default_value_uri_for_code_list_concepts(
        self, column: CsvColumn, code_list: QbCodeList
    ) -> str:
        column_uri_fragment = self.get_column_uri_template_fragment(column)

        if isinstance(code_list, ExistingQbCodeList):
            legacy_external_match = self._legacy_external_code_list_pattern.match(
                code_list.concept_scheme_uri
            )
            legacy_local_match = self._legacy_dataset_local_code_list_pattern.match(
                code_list.concept_scheme_uri
            )
            csvcubed_match = self._csvcubed_code_list_pattern.match(
                code_list.concept_scheme_uri
            )
            if legacy_external_match:
                _logger.debug(
                    "Existing concept scheme URI %s matches legacy family/global style.",
                    code_list.concept_scheme_uri,
                )
                m: re.Match = legacy_external_match
                # ConceptScheme URI:
                # http://gss-data.org.uk/def/concept-scheme/{code-list-name}
                # Concept URI:
                # http://gss-data.org.uk/def/concept-scheme/{code-list-name}/{notation}
                return f"{m.group(1)}/concept-scheme/{m.group(2)}/{column_uri_fragment}"
            elif legacy_local_match:
                _logger.debug(
                    "Existing concept scheme URI %s matches legacy dataset-local style.",
                    code_list.concept_scheme_uri,
                )
                m: re.Match = legacy_local_match
                # ConceptScheme URI:
                # http://gss-data.org.uk/data/gss_data/{family-name}/{dataset-root-name}#scheme/{code-list-name}
                # Concept URI:
                # http://gss-data.org.uk/data/gss_data/{family-name}/{dataset-root-name}#concept/{code-list-name}/{notation}
                return f"{m.group(1)}#concept/{m.group(2)}/{column_uri_fragment}"
            elif csvcubed_match:
                _logger.debug(
                    "Existing concept scheme URI %s matches csvcubed style.",
                    code_list.concept_scheme_uri,
                )
                m: re.Match = csvcubed_match
                # ConceptScheme URI:
                # {code-list-uri}#code-list
                # Concept URI:
                # {code-list-uri}#{notation}
                return f"{m.group(1)}#{column_uri_fragment}"
            else:
                _logger.warning(
                    "Existing code list URI %s does not match expected any known convention.",
                    code_list.concept_scheme_uri,
                )
                # Unexpected code-list URI. Does not match expected conventions.
                return column_uri_fragment
        elif isinstance(code_list, NewQbCodeList):
            _logger.debug(
                "valueUrl defined by new dataset-local code list %s",
                code_list.metadata.title,
            )
            return SkosCodeListNewUriHelper(
                code_list, self.cube.uri_style
            ).get_concept_uri(column_uri_fragment)
        elif isinstance(code_list, NewQbCodeListInCsvW):
            _logger.debug(
                "valueUrl defined by legacy dataset-local code list %s",
                code_list.concept_scheme_uri,
            )
            return re.sub(
                r"\{.?notation\}", column_uri_fragment, code_list.concept_template_uri
            )
        else:
            raise TypeError(f"Unhandled codelist type {type(code_list)}")

    def _get_observation_uri_for_standard_shape_data_set(self) -> str:
        dimension_columns_templates: List[str] = []
        multi_measure_col_template: Optional[str] = None

        for c in self.cube.columns:
            if isinstance(c, QbColumn):
                if isinstance(c.structural_definition, QbDimension):
                    dimension_columns_templates.append(
                        f"{{{csvw_column_name_safe(c.uri_safe_identifier)}}}"
                    )
                elif isinstance(c.structural_definition, QbMultiMeasureDimension):
                    multi_measure_col_template = (
                        f"{{{csvw_column_name_safe(c.uri_safe_identifier)}}}"
                    )
        return self._new_uri_helper.get_observation_uri(
            dimension_columns_templates, multi_measure_col_template
        )
