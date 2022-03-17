import pytest
import numpy as np
from pandas import DataFrame
from pandas.util.testing import assert_frame_equal

from pathlib import Path

from csvcubed.cli.inspect.inspectsparqlmanager import (
    select_csvw_catalog_metadata,
    select_csvw_dsd_dataset_label_and_dsd_def_uri,
    select_qb_dataset_url,
)
from csvcubed.models.inspectsparqlresults import (
    DSDLabelURIResult,
)
from csvcubed.cli.inspect.inspectdatasetmanager import (
    DatasetMeasureType,
    DatasetUnitType,
    get_dataset_measure_type,
    get_dataset_observations_info,
    get_dataset_unit_type,
    get_measure_col_from_dsd,
    get_multi_measure_dataset_val_counts_info,
    get_single_measure_dataset_val_counts_info,
    get_single_measure_label_from_dsd,
    get_single_unit_label_from_dsd,
    get_unit_col_from_dsd,
    load_csv_to_dataframe,
)
from csvcubed.cli.inspect.metadataprocessor import MetadataProcessor
from csvcubed.models.inspectdataframeresults import (
    DatasetObservationsByMeasureUnitInfoResult,
    DatasetObservationsInfoResult,
)
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "cli" / "inspect"

_expected_dataframe = DataFrame(
    [
        {
            "Label": "All",
            "Notation": "all",
            "Parent Notation": "",
            "Sort Priority": 0,
            "Description": "",
        },
        {
            "Label": "Ready to Drink",
            "Notation": "ready-to-drink",
            "Parent Notation": "",
            "Sort Priority": 1,
            "Description": "",
        },
        {
            "Label": "Sparkling",
            "Notation": "sparkling",
            "Parent Notation": "",
            "Sort Priority": 2,
            "Description": "",
        },
        {
            "Label": "Still",
            "Notation": "still",
            "Parent Notation": "",
            "Sort Priority": 3,
            "Description": "",
        },
        {
            "Label": "UK",
            "Notation": "uk",
            "Parent Notation": "",
            "Sort Priority": 4,
            "Description": "",
        },
        {
            "Label": "UK Grain and Blend",
            "Notation": "uk-grain-and-blend",
            "Parent Notation": "",
            "Sort Priority": 5,
            "Description": "",
        },
        {
            "Label": "UK Potable",
            "Notation": "uk-potable",
            "Parent Notation": "",
            "Sort Priority": 6,
            "Description": "",
        },
        {
            "Label": "UK Registered",
            "Notation": "uk-registered",
            "Parent Notation": None,
            "Sort Priority": 7,
            "Description": "",
        },
        {
            "Label": "Uk Malt",
            "Notation": "uk-malt",
            "Parent Notation": "",
            "Sort Priority": 8,
            "Description": "",
        },
        {
            "Label": "UK Registered",
            "Notation": "uk-registered",
            "Parent Notation": "",
            "Sort Priority": 7,
            "Description": "",
        },
        {
            "Label": "Uk Malt",
            "Notation": "uk-malt",
            "Parent Notation": "",
            "Sort Priority": 8,
            "Description": "",
        },
    ]
).replace("", np.NAN)

_expected_by_measure_and_unit_val_counts_df_single_unit_single_measure = DataFrame(
    [{"Measure Type": "Measure Label", "Unit": "Unit Label", "Count": 286}]
).replace("", np.NAN)

_expected_by_measure_and_unit_val_counts_df_single_unit_multi_measure = DataFrame(
    [{"Measure Type": "Measure Label", "Unit": "Unit Label", 0: 41508}]
).replace("", np.NAN)

_expected_by_measure_and_unit_val_counts_df_multi_unit_single_measure = DataFrame(
    [{"Measure Type": "Measure Label", "Unit": "Unit Label", "Count": 41508}]
).replace("", np.NAN)

_expected_by_measure_and_unit_val_counts_df_multi_unit_multi_measure = DataFrame(
    [
        {"Measure Type": "alcohol-duty-receipts", "Unit": "gbp-million", 0: 314},
        {"Measure Type": "beer-duty-receipts", "Unit": "gbp-million", 0: 314},
        {"Measure Type": "cider-duty-receipts", "Unit": "gbp-million", 0: 314},
        {"Measure Type": "clearances", "Unit": "hectolitres", 0: 4710},
        {"Measure Type": "clearances", "Unit": "hectolitres-of-alcohol", 0: 942},
        {"Measure Type": "clearances", "Unit": "thousand-hectolitres", 0: 1256},
        {"Measure Type": "clearances-of-alcohol", "Unit": "hectolitres", 0: 942},
        {
            "Measure Type": "clearances-of-alcohol",
            "Unit": "thousand-hectolitres",
            0: 314,
        },
        {
            "Measure Type": "production-volume",
            "Unit": "thousand-hectolitres",
            0: 314,
        },
        {
            "Measure Type": "production-volume-alcohol",
            "Unit": "hectolitres",
            0: 314,
        },
        {
            "Measure Type": "production-volume-alcohol",
            "Unit": "thousand-hectolitres",
            0: 314,
        },
        {"Measure Type": "spirits-duty-receipts", "Unit": "gbp-million", 0: 314},
        {"Measure Type": "wine-duty-receipts", "Unit": "gbp-million", 0: 314},
    ]
).replace("", np.NAN)


def test_load_csv_to_dataframe_success():
    """
    Should load the csv to dataframe successfully.
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    dataset = load_csv_to_dataframe(csvw_metadata_json_path, "csv_file.csv")

    assert dataset is not None
    assert len(dataset.index) == 11
    assert_frame_equal(dataset, _expected_dataframe)


def test_load_csv_to_dataframe_error():
    """
    Should error when loading csv to dataframe.
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"

    with pytest.raises(Exception):
        load_csv_to_dataframe(csvw_metadata_json_path, "missing_csv_file.csv")


def test_get_dataset_measure_type_single_measure():
    """
    # TODO Add single measure csvw to test cases folder.
    Should return `DatasetMeasureType.SINGLE_MEASURE`.
    """

    csvw_metadata_json_path = (
        _test_case_base_dir
        / "multi-unit_single-measure"
        / "final-uk-greenhouse-gas-emissions-national-statistics-1990-to-2019.csv-metadata.json"
    )
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    result: DSDLabelURIResult = select_csvw_dsd_dataset_label_and_dsd_def_uri(
        csvw_metadata_rdf_graph
    )

    measure_type = get_dataset_measure_type(
        csvw_metadata_rdf_graph, result.dsd_uri, csvw_metadata_json_path
    )

    assert measure_type == DatasetMeasureType.SINGLE_MEASURE


def test_get_dataset_measure_type_multi_measure():
    """
    Should return `DatasetMeasureType.MULTI_MEASURE`.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "multi-unit_multi-measure"
        / "alcohol-bulletin.csv-metadata.json"
    )
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    result: DSDLabelURIResult = select_csvw_dsd_dataset_label_and_dsd_def_uri(
        csvw_metadata_rdf_graph
    )

    measure_type = get_dataset_measure_type(
        csvw_metadata_rdf_graph, result.dsd_uri, csvw_metadata_json_path
    )

    assert measure_type == DatasetMeasureType.MULTI_MEASURE


def test_get_dataset_unit_type_single_unit():
    """
    Should return `DatasetUnitType.SINGLE_UNIT`.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "single-unit_single-measure"
        / "energy-trends-uk-total-energy.csv-metadata.json"
    )
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()
    dataset_uri = select_csvw_catalog_metadata(csvw_metadata_rdf_graph).dataset_uri
    dataset_url = select_qb_dataset_url(
        csvw_metadata_rdf_graph, dataset_uri
    ).dataset_url

    dataset: DataFrame = load_csv_to_dataframe(
        csvw_metadata_json_path, Path(dataset_url)
    )

    unit_type = get_dataset_unit_type(dataset)

    assert unit_type == DatasetUnitType.SINGLE_UNIT


def test_get_dataset_unit_type_multi_unit():
    """
    Should return `DatasetUnitType.MULTI_UNIT`.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "multi-unit_multi-measure"
        / "alcohol-bulletin.csv-metadata.json"
    )
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()
    dataset_uri = select_csvw_catalog_metadata(csvw_metadata_rdf_graph).dataset_uri
    dataset_url = select_qb_dataset_url(
        csvw_metadata_rdf_graph, dataset_uri
    ).dataset_url

    dataset: DataFrame = load_csv_to_dataframe(
        csvw_metadata_json_path, Path(dataset_url)
    )

    unit_type = get_dataset_unit_type(dataset)

    assert unit_type == DatasetUnitType.MULTI_UNIT


def test_get_measure_col_from_dsd():
    """
    Should return the correct measure column name.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "multi-unit_multi-measure"
        / "alcohol-bulletin.csv-metadata.json"
    )
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    result: DSDLabelURIResult = select_csvw_dsd_dataset_label_and_dsd_def_uri(
        csvw_metadata_rdf_graph
    )

    measure_col = get_measure_col_from_dsd(
        csvw_metadata_rdf_graph, result.dsd_uri, csvw_metadata_json_path
    )

    assert measure_col == "Measure Type"


def test_get_unit_col_from_dsd():
    """
    Should return the correct unit column name.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "multi-unit_multi-measure"
        / "alcohol-bulletin.csv-metadata.json"
    )
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    result: DSDLabelURIResult = select_csvw_dsd_dataset_label_and_dsd_def_uri(
        csvw_metadata_rdf_graph
    )

    unit_col = get_unit_col_from_dsd(
        csvw_metadata_rdf_graph, result.dsd_uri, csvw_metadata_json_path
    )

    assert unit_col == "Unit"


def test_get_single_measure_label_from_dsd():
    """
    Should return the correct measure label.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "single-unit_single-measure"
        / "energy-trends-uk-total-energy.csv-metadata.json"
    )

    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    result: DSDLabelURIResult = select_csvw_dsd_dataset_label_and_dsd_def_uri(
        csvw_metadata_rdf_graph
    )

    measure_label = get_single_measure_label_from_dsd(
        csvw_metadata_rdf_graph, result.dsd_uri, csvw_metadata_json_path
    )

    assert measure_label == ""


def test_get_single_unit_label_from_dsd():
    """
    Should return the correct unit label.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "single-unit_multi-measure"
        / "final-uk-greenhouse-gas-emissions-national-statistics-1990-to-2020.csv-metadata.json"
    )

    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    result: DSDLabelURIResult = select_csvw_dsd_dataset_label_and_dsd_def_uri(
        csvw_metadata_rdf_graph
    )

    unit_label = get_single_unit_label_from_dsd(
        csvw_metadata_rdf_graph, result.dsd_uri, csvw_metadata_json_path
    )

    assert unit_label == ""


def test_get_single_unit_single_measure_dataset_val_counts_info():
    """
    Should produce expected `DatasetObservationsByMeasureUnitInfoResult`.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "single-unit_single-measure"
        / "energy-trends-uk-total-energy.csv-metadata.json"
    )
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()
    dataset_uri = select_csvw_catalog_metadata(csvw_metadata_rdf_graph).dataset_uri
    dataset_url = select_qb_dataset_url(
        csvw_metadata_rdf_graph, dataset_uri
    ).dataset_url
    dataset: DataFrame = load_csv_to_dataframe(
        csvw_metadata_json_path, Path(dataset_url)
    )

    result: DatasetObservationsByMeasureUnitInfoResult = (
        get_single_measure_dataset_val_counts_info(
            dataset, "Measure Type", "Unit", "Measure Label", "Unit Label"
        )
    )

    assert result is not None
    assert_frame_equal(
        result.by_measure_and_unit_val_counts_df,
        _expected_by_measure_and_unit_val_counts_df_single_unit_single_measure,
    )


def test_get_single_unit_multi_measure_dataset_val_counts_info():
    """
    Should produce expected `DatasetObservationsByMeasureUnitInfoResult`.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "single-unit_multi-measure"
        / "final-uk-greenhouse-gas-emissions-national-statistics-1990-to-2020.csv-metadata.json"
    )
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()
    dataset_uri = select_csvw_catalog_metadata(csvw_metadata_rdf_graph).dataset_uri
    dataset_url = select_qb_dataset_url(
        csvw_metadata_rdf_graph, dataset_uri
    ).dataset_url
    dataset: DataFrame = load_csv_to_dataframe(
        csvw_metadata_json_path, Path(dataset_url)
    )

    result: DatasetObservationsByMeasureUnitInfoResult = (
        get_multi_measure_dataset_val_counts_info(dataset, "Measure", "Unit")
    )

    assert result is not None
    assert_frame_equal(
        result.by_measure_and_unit_val_counts_df,
        _expected_by_measure_and_unit_val_counts_df_single_unit_multi_measure,
    )


def test_get_multi_unit_single_measure_dataset_val_counts_info():
    """
    Should produce expected `DatasetObservationsByMeasureUnitInfoResult`.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "multi-unit_single-measure"
        / "final-uk-greenhouse-gas-emissions-national-statistics-1990-to-2019.csv-metadata.json"
    )
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()
    dataset_uri = select_csvw_catalog_metadata(csvw_metadata_rdf_graph).dataset_uri
    dataset_url = select_qb_dataset_url(
        csvw_metadata_rdf_graph, dataset_uri
    ).dataset_url
    dataset: DataFrame = load_csv_to_dataframe(
        csvw_metadata_json_path, Path(dataset_url)
    )

    result: DatasetObservationsByMeasureUnitInfoResult = (
        get_single_measure_dataset_val_counts_info(
            dataset, "Measure Type", "Unit", "Measure Label", "Unit Label"
        )
    )

    assert result is not None
    assert_frame_equal(
        result.by_measure_and_unit_val_counts_df,
        _expected_by_measure_and_unit_val_counts_df_multi_unit_single_measure,
    )


def test_get_multi_unit_multi_measure_dataset_val_counts_info():
    """
    Should produce expected `DatasetObservationsByMeasureUnitInfoResult`.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "multi-unit_multi-measure"
        / "alcohol-bulletin.csv-metadata.json"
    )
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()
    dataset_uri = select_csvw_catalog_metadata(csvw_metadata_rdf_graph).dataset_uri
    dataset_url = select_qb_dataset_url(
        csvw_metadata_rdf_graph, dataset_uri
    ).dataset_url
    dataset: DataFrame = load_csv_to_dataframe(
        csvw_metadata_json_path, Path(dataset_url)
    )

    result: DatasetObservationsByMeasureUnitInfoResult = (
        get_multi_measure_dataset_val_counts_info(dataset, "Measure Type", "Unit")
    )

    assert result is not None
    assert_frame_equal(
        result.by_measure_and_unit_val_counts_df,
        _expected_by_measure_and_unit_val_counts_df_multi_unit_multi_measure,
    )


def test_get_dataset_observations_info():
    """
    Should produce the expected `DatasetObservationsInfoResult`.
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    dataset = load_csv_to_dataframe(csvw_metadata_json_path, "csv_file.csv")

    result: DatasetObservationsInfoResult = get_dataset_observations_info(dataset)

    assert result.num_of_observations == 11
    assert result.num_of_duplicates == 2
    assert_frame_equal(result.dataset_head, _expected_dataframe.head(n=10))
    assert_frame_equal(result.dataset_tail, _expected_dataframe.tail(n=10))
