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

    FailedToLoadTableSchemaIntoRDFGraph = (
        "An error occured while loading table schema json into rdf graph"
    )

    FailedToParseJSONldtoRDFGraph = (
        "An error occured while parsing csvw json-ld to rdf graph"
    )

    UnsupportedComponentPropertyType = "Property type {property_type} is not supported"

    FailedToConvertDataFrameToString = "Failed to convert dataframe to string"

    UnexpectedSparqlASKQueryResponseType = (
        "Unexpected ASK query response type {response_type}"
    )

    UnexpectedSparqlASKQueryResults = (
        "Unexpected number of results for ASK query {num_of_results}"
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


class CsvcubedException(Exception, HasErrorUrl, ABC):
    """Abstract class representing csvcubed exception model."""

    pass


class JsonldNotSupportedException(CsvcubedException):
    """Class representing the JsonldNotSupportedException model."""

    def __init__(self):
        super().__init__(
            f"{CsvcubedExceptionMsges.JsonldNotSupported.value}: {self.get_error_url()}"
        )

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.JsonldNotSupported.value


class InputTypeIsUnknownException(Exception):
    """Class representing the InputTypeIsUnknownException model."""

    def __init__(self):
        super().__init__(
            f"{CsvcubedExceptionMsges.InputTypeUnknown.value}: {self.get_error_url()}"
        )

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.InputTypeUnknown.value


class RDFGraphCannotBeNoneException(Exception):
    """Class representing the RDFGraphCannotBeNoneException model."""

    def __init__(self):
        super().__init__(
            f"{CsvcubedExceptionMsges.RDFGraphCannotBeNone.value}: {self.get_error_url()}"
        )

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.RDFGraphCannotBeNone.value


class CsvToDataFrameLoadFailedException(Exception):
    """Class representing the CsvToDataFrameLoadFailedException model."""

    def __init__(self):
        super().__init__(
            f"{CsvcubedExceptionMsges.CsvToDataFrameLoadFailed.value}: {self.get_error_url()}"
        )

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.CsvToDataFrameLoadFailed.value


class InvalidNumberOfRecordsException(Exception):
    """Class representing the InvalidNumberOfRecordsException model."""

    def __init__(self, excepted_num_of_records: int, num_of_records: int):
        super().__init__(
            f"{CsvcubedExceptionMsges.InvalidNumberOfRecords.value}: {self.get_error_url()}".format(
                excepted_num_of_records=excepted_num_of_records,
                num_of_records=num_of_records,
            )
        )

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.InvalidNumberOfRecords.value


class FailedToReadSparqlQueryException(Exception):
    """Class representing the FailedToReadSparqlQueryException model."""

    def __init__(self, sparql_file_path: Path):
        super().__init__(
            f"{CsvcubedExceptionMsges.FailedToReadSparqlQuery.value}: {self.get_error_url()}".format(
                sparql_file_path=str(sparql_file_path),
            )
        )

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.FailedToReadSparqlQuery.value


class InvalidCsvFilePathException(Exception):
    """Class representing the InvalidCsvFilePathException model."""

    def __init__(self):
        super().__init__(
            f"{CsvcubedExceptionMsges.InvalidCSVFilePath.value}: {self.get_error_url()}"
        )

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.InvalidCSVFilePath.value


class FailedToLoadTableSchemaIntoRDFGraphException(Exception):
    """Class representing the FailedToLoadTableSchemaIntoRDFGraphException model."""

    def __init__(self):
        super().__init__(
            f"{CsvcubedExceptionMsges.FailedToLoadTableSchemaIntoRDFGraph.value}: {self.get_error_url()}"
        )

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.FailedToLoadTableSchemaIntoRDFGraph.value


class FailedToParseJSONldtoRDFGraphException(Exception):
    """Class representing the FailedToParseJSONldtoRDFGraphException model."""

    def __init__(self):
        super().__init__(
            f"{CsvcubedExceptionMsges.FailedToParseJSONldtoRDFGraph.value}: {self.get_error_url()}"
        )

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.FailedToParseJSONldtoRDFGraph.value


class UnsupportedComponentPropertyTypeException(Exception):
    """Class representing the UnsupportedComponentPropertyType model."""

    def __init__(self, property_type: str):
        super().__init__(
            f"{CsvcubedExceptionMsges.UnsupportedComponentPropertyType.value}: {self.get_error_url()}".format(
                property_type=property_type
            )
        )

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.UnsupportedComponentPropertyType.value


class FailedToConvertDataFrameToStringException(Exception):
    """Class representing the FailedToConvertDataFrameToStringException model."""

    def __init__(self):
        super().__init__(
            f"{CsvcubedExceptionMsges.FailedToConvertDataFrameToString.value}: {self.get_error_url()}"
        )

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.FailedToConvertDataFrameToString.value


class UnexpectedSparqlASKQueryResponseTypeException(Exception):
    """Class representing the UnexpectedSparqlASKQueryResponseTypeException model."""

    def __init__(self, response_type: type):
        super().__init__(
            f"{CsvcubedExceptionMsges.UnexpectedSparqlASKQueryResponseType.value}: {self.get_error_url()}".format(
                response_type=response_type
            )
        )

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.UnexpectedSparqlASKQueryResponseType.value


class UnexpectedSparqlASKQueryResultsException(Exception):
    """Class representing the UnexpectedSparqlASKQueryResultsException model."""

    def __init__(self, num_of_results: int):
        super().__init__(
            f"{CsvcubedExceptionMsges.UnexpectedSparqlASKQueryResults.value}: {self.get_error_url()}".format(
                num_of_results=num_of_results
            )
        )

    @classmethod
    def get_error_url(cls) -> str:
        return CsvcubedExceptionUrls.UnexpectedSparqlASKQueryResults.value
