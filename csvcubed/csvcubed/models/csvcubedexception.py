from abc import ABC
from enum import Enum
from pathlib import Path

from csvcubed.models.errorurl import HasErrorUrl


class CsvcubedExceptionMsges(Enum):
    """
    Error messages for the exceptions thrown in csvcubed.
    """

    InputNotSupported = "The input CSV-W json-ld is not supported. The input should be a data cube or a code list"

    FailedToReadCsvwFileContent = (
        "An error occured while reading CSV-W content from file at {csvw_metadata_file_path}"
    )

    InvalidCsvwContent = "CSV-W content is invalid."

    FailedToLoadRDFGraph = "Failed to load the RDF graph from input"

    CsvToDataFrameLoadFailed = "Failed to load CSV dataset to dataframe"

    InvalidNumberOfRecords = "Expected {excepted_num_of_records} record(s), but found {num_of_records} record(s)"

    FailedToReadSparqlQuery = (
        "Failed to read sparql query from file at {sparql_file_path}"
    )

    FailedToLoadTableSchemaIntoRdfGraph = "Failed to load table schema '{table_schema_file}' into RDF graph"

    UnsupportedComponentPropertyType = "Property type {property_type} is not supported"

    FailedToConvertDataFrameToString = "Failed to convert dataframe to string"

    UnexpectedSparqlAskQueryResponseType = (
        "Unexpected ASK query response type {response_type}"
    )

    UnexpectedSparqlAskQueryResults = (
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

    InputNotSupported = "http://purl.org/csv-cubed/err/input-not-supported"

    FailedToReadCsvwFileContent = (
        "http://purl.org/csv-cubed/err/failed-to-read-csvw-file-content"
    )

    InvalidCsvwContent = "http://purl.org/csv-cubed/err/invalid-csvw-content"

    FailedToLoadRDFGraph = "http://purl.org/csv-cubed/err/rdf-graph-load-failed"

    CsvToDataFrameLoadFailed = (
        "http://purl.org/csv-cubed/err/csv-to-dataframe-load-failed"
    )

    InvalidNumberOfRecords = "http://purl.org/csv-cubed/err/invalid-num-of-records"

    FailedToReadSparqlQuery = (
        "http://purl.org/csv-cubed/err/failed-to-read-sparql-query"
    )

    FailedToLoadTableSchemaIntoRdfGraph = (
        "http://purl.org/csv-cubed/err/failed-to-load-table-schema-into-rdf-graph"
    )

    UnsupportedComponentPropertyType = (
        "http://purl.org/csv-cubed/err/unsupported-component-property-type"
    )

    FailedToConvertDataFrameToString = (
        "http://purl.org/csv-cubed/err/failed-to-convert-dataframe-to-string"
    )

    UnexpectedSparqlAskQueryResponseType = (
        "http://purl.org/csv-cubed/err/invalid-ask-query-response-type"
    )

    UnexpectedSparqlAskQueryResults = (
        "http://purl.org/csv-cubed/err/invalid-ask-query-results"
    )

    FeatureNotSupported = "http://purl.org/csv-cubed/err/feature-not-supported"

    ErrorProcessingDataFrameException = (
        "http://purl.org/csv-cubed/err/error-when-processing-dataframe"
    )


class CsvcubedException(Exception, HasErrorUrl, ABC):
    """Abstract class representing csvcubed exception model."""

    pass


class InputNotSupportedException(CsvcubedException):
    """Class representing the InputNotSupportedException model."""

    def __init__(self):
        super().__init__(CsvcubedExceptionMsges.InputNotSupported.value)

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.InputNotSupported.value


class FailedToReadCsvwFileContentException(CsvcubedException):
    """Class representing the FailedToReadCsvwFileContentException model."""

    def __init__(self, csvw_metadata_file_path: Path):
        super().__init__(
            CsvcubedExceptionMsges.FailedToReadCsvwFileContent.value.format(
                csvw_metadata_file_path=str(csvw_metadata_file_path)
            )
        )

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.FailedToReadCsvwFileContent.value


class InvalidCsvwContentException(CsvcubedException):
    """Class representing the InvalidCsvwContentException model."""

    def __init__(self):
        super().__init__(CsvcubedExceptionMsges.InvalidCsvwContent.value)

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.InvalidCsvwContent.value

class FailedToLoadRDFGraphException(CsvcubedException):
    """Class representing the FailedToLoadRDFGraphException model."""

    def __init__(self):
        super().__init__(f"{CsvcubedExceptionMsges.FailedToLoadRDFGraph.value}")

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.FailedToLoadRDFGraph.value


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

class FailedToLoadTableSchemaIntoRdfGraphException(CsvcubedException):
    """Class representing the FailedToLoadTableSchemaIntoRdfGraphException model."""

    def __init__(self, table_schema_file: str):
        super().__init__(
            CsvcubedExceptionMsges.FailedToLoadTableSchemaIntoRdfGraph.value.format(
                table_schema_file=table_schema_file
            )
        )

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.FailedToLoadTableSchemaIntoRdfGraph.value

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
            CsvcubedExceptionMsges.UnexpectedSparqlAskQueryResponseType.value.format(
                response_type=response_type
            )
        )

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.UnexpectedSparqlAskQueryResponseType.value


class UnexpectedSparqlAskQueryResultsException(CsvcubedException):
    """Class representing the UnexpectedSparqlAskQueryResultsException model."""

    def __init__(self, num_of_results: int):
        super().__init__(
            CsvcubedExceptionMsges.UnexpectedSparqlAskQueryResults.value.format(
                num_of_results=num_of_results
            )
        )

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.UnexpectedSparqlAskQueryResults.value


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
