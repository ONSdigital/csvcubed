from abc import ABC
from enum import Enum
from pathlib import Path

from csvcubed.models.errorurl import HasErrorUrl


class CsvcubedExceptionMsges(Enum):
    """
    Error messages for the exceptions thrown in csvcubed.
    """

    JsonldNotSupported = "The input csvw json-ld is not supported"

    InputTypeUnknown = "The input type is unknown"

    RDFGraphCannotBeNone = "RDF graph cannot be none"

    CsvToDataFrameLoadFailed = "Failed to load csv to dataframe"

    InvalidNumberOfRecords = "Expected {excepted_num_of_records} record(s), but found {num_of_records} record(s)"

    FailedToReadSparqlQuery = (
        "Failed to read sparql query from file at {sparql_file_path}"
    )

    InvalidCSVFilePath = "Currently, inspect cli only suports CSVs with local file paths. CSVs from HTTP urls are not yet supported"

    FailedToLoadTableSchemaIntoRDFGraph = "An error occured while loading table schema '{table_schema_file}' into rdf graph"

    FailedToParseJSONldtoRDFGraph = "An error occured while parsing CSV-W JSON-LD to RDF graph ({csvw_metadata_file_path})"

    UnsupportedComponentPropertyType = "Property type {property_type} is not supported"

    FailedToConvertDataFrameToString = "Failed to convert dataframe to string"

    UnexpectedSparqlASKQueryResponseType = (
        "Unexpected ASK query response type {response_type}"
    )

    UnexpectedSparqlASKQueryResults = (
        "Unexpected number of results for ASK query {num_of_results}"
    )

    FeatureNotSupported = "This feature is not yet supported: {explanation}"

    ErrorProcessingDataFrameException = (
        "An error occurred when performing {operation} operation on dataframe"
    )


class CsvcubedExceptionUrls(Enum):
    """
    Urls for the exceptions thrown in csvcubed.
    """

    JsonldNotSupported = "http://purl.org/csv-cubed/err/jsonld-not-supported"

    InputTypeUnknown = "http://purl.org/csv-cubed/err/input-type-unknown"

    RDFGraphCannotBeNone = "http://purl.org/csv-cubed/err/rdf-graph-none"

    CsvToDataFrameLoadFailed = (
        "http://purl.org/csv-cubed/err/csv-to-dataframe-load-failed"
    )

    InvalidNumberOfRecords = "http://purl.org/csv-cubed/err/invalid-num-of-records"

    FailedToReadSparqlQuery = (
        "http://purl.org/csv-cubed/err/failed-read-sparql_query-from-file"
    )

    InvalidCSVFilePath = "http://purl.org/csv-cubed/err/invalid-csv-file-path"

    FailedToLoadTableSchemaIntoRDFGraph = (
        "http://purl.org/csv-cubed/err/failed-to-load-table-schema-into-rdf-graph"
    )

    FailedToParseJSONldtoRDFGraph = (
        "http://purl.org/csv-cubed/err/failed-to-parse-json-ld-to-rdf-graph"
    )

    UnsupportedComponentPropertyType = (
        "http://purl.org/csv-cubed/err/unsupported-component-property-type"
    )

    FailedToConvertDataFrameToString = (
        "http://purl.org/csv-cubed/err/failed-to-convert-dataframe-to-string"
    )

    UnexpectedSparqlASKQueryResponseType = (
        "http://purl.org/csv-cubed/err/invalid-ask-query-response-type"
    )

    UnexpectedSparqlASKQueryResults = (
        "http://purl.org/csv-cubed/err/invalid-ask-query-results"
    )

    FeatureNotSupported = "http://purl.org/csv-cubed/err/feature-not-supported"

    ErrorProcessingDataFrameException = (
        "http://purl.org/csv-cubed/err/error-when-processing-dataframe"
    )


class CsvcubedException(Exception, HasErrorUrl, ABC):
    """Abstract class representing csvcubed exception model."""

    pass


class JsonldNotSupportedException(CsvcubedException):
    """Class representing the JsonldNotSupportedException model."""

    def __init__(self):
        super().__init__(CsvcubedExceptionMsges.JsonldNotSupported.value)

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.JsonldNotSupported.value


class InputTypeIsUnknownException(CsvcubedException):
    """Class representing the InputTypeIsUnknownException model."""

    def __init__(self):
        super().__init__(CsvcubedExceptionMsges.InputTypeUnknown.value)

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.InputTypeUnknown.value


class RDFGraphCannotBeNoneException(CsvcubedException):
    """Class representing the RDFGraphCannotBeNoneException model."""

    def __init__(self):
        super().__init__(f"{CsvcubedExceptionMsges.RDFGraphCannotBeNone.value}")

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.RDFGraphCannotBeNone.value


class CsvToDataFrameLoadFailedException(CsvcubedException):
    """Class representing the CsvToDataFrameLoadFailedException model."""

    def __init__(self):
        super().__init__(CsvcubedExceptionMsges.CsvToDataFrameLoadFailed.value)

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.CsvToDataFrameLoadFailed.value


class InvalidNumberOfRecordsException(CsvcubedException):
    """Class representing the InvalidNumberOfRecordsException model."""

    def __init__(self, excepted_num_of_records: int, num_of_records: int):
        super().__init__(
            CsvcubedExceptionMsges.InvalidNumberOfRecords.value.format(
                excepted_num_of_records=excepted_num_of_records,
                num_of_records=num_of_records,
            )
        )

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.InvalidNumberOfRecords.value


class FailedToReadSparqlQueryException(CsvcubedException):
    """Class representing the FailedToReadSparqlQueryException model."""

    def __init__(self, sparql_file_path: Path):
        super().__init__(
            CsvcubedExceptionMsges.FailedToReadSparqlQuery.value.format(
                sparql_file_path=str(sparql_file_path),
            )
        )

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.FailedToReadSparqlQuery.value


class InvalidCsvFilePathException(CsvcubedException):
    """Class representing the InvalidCsvFilePathException model."""

    def __init__(self):
        super().__init__(CsvcubedExceptionMsges.InvalidCSVFilePath.value)

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.InvalidCSVFilePath.value


class FailedToLoadTableSchemaIntoRDFGraphException(CsvcubedException):
    """Class representing the FailedToLoadTableSchemaIntoRDFGraphException model."""

    def __init__(self, table_schema_file: str):
        super().__init__(
            CsvcubedExceptionMsges.FailedToLoadTableSchemaIntoRDFGraph.value.format(
                table_schema_file=table_schema_file
            )
        )

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.FailedToLoadTableSchemaIntoRDFGraph.value


class FailedToParseJSONldtoRDFGraphException(CsvcubedException):
    """Class representing the FailedToParseJSONldtoRDFGraphException model."""

    def __init__(self, csvw_metadata_file_path: Path):
        super().__init__(
            CsvcubedExceptionMsges.FailedToParseJSONldtoRDFGraph.value.format(
                csvw_metadata_file_path=str(csvw_metadata_file_path)
            )
        )

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.FailedToParseJSONldtoRDFGraph.value


class UnsupportedComponentPropertyTypeException(CsvcubedException):
    """Class representing the UnsupportedComponentPropertyType model."""

    def __init__(self, property_type: str):
        super().__init__(
            CsvcubedExceptionMsges.UnsupportedComponentPropertyType.value.format(
                property_type=property_type
            )
        )

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.UnsupportedComponentPropertyType.value


class FailedToConvertDataFrameToStringException(CsvcubedException):
    """Class representing the FailedToConvertDataFrameToStringException model."""

    def __init__(self):
        super().__init__(CsvcubedExceptionMsges.FailedToConvertDataFrameToString.value)

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.FailedToConvertDataFrameToString.value


class UnexpectedSparqlAskQueryResponseTypeException(CsvcubedException):
    """Class representing the UnexpectedSparqlAskQueryResponseTypeException model."""

    def __init__(self, response_type: type):
        super().__init__(
            CsvcubedExceptionMsges.UnexpectedSparqlASKQueryResponseType.value.format(
                response_type=response_type
            )
        )

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.UnexpectedSparqlASKQueryResponseType.value


class UnexpectedSparqlASKQueryResultsException(CsvcubedException):
    """Class representing the UnexpectedSparqlASKQueryResultsException model."""

    def __init__(self, num_of_results: int):
        super().__init__(
            CsvcubedExceptionMsges.UnexpectedSparqlASKQueryResults.value.format(
                num_of_results=num_of_results
            )
        )

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.UnexpectedSparqlASKQueryResults.value


class FeatureNotSupportedException(CsvcubedException):
    """Class representing the FeatureNotSupportedException model."""

    def __init__(self, explanation: str):
        super().__init__(
            CsvcubedExceptionMsges.FeatureNotSupported.value.format(
                explanation=explanation
            )
        )

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.FeatureNotSupported.value


class ErrorProcessingDataFrameException(CsvcubedException):
    """Class representing the FeatureNotSupportedException model."""

    def __init__(self, operation: str):
        super().__init__(
            CsvcubedExceptionMsges.ErrorProcessingDataFrameException.value.format(
                operation=operation
            )
        )

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.ErrorProcessingDataFrameException.value
