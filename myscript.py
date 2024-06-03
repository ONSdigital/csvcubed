from pathlib import Path

from csvcubed.cli.inspectcsvw.inspect import inspect

inspect(
    Path(
        "tests/test-cases/cli/inspect/multi-theme-and-keywords/aged-16-to-64-years-level-3-or-above-qualifications.csv-metadata.json"
    )
)

# cube, errs = build_csvw(
#     Path("out/test_cases/data.csv"), Path("out/test_cases/data.json")
# )

# g = rdflib.ConjunctiveGraph()
# g.parse("out/some-title.csv-metadata.json")
# # g.serialize("some-title.ttl", format="turtle")
# # results = select_data_set_dsd_and_csv_url(g)
# results = select_csvw_catalog_metadata(g)
# print()


# rdf_mgr = CsvWRdfManager(
#     Path(
#         "tests/test-cases/cli/inspect/pivoted-multi-measure-dataset/qb-id-10003.csv-metadata.json"
#     )
# )
# dc_repo = DataCubeRepository(rdf_mgr.csvw_repository)
# metadata_printer = MetadataPrinter(dc_repo)
# dc_repo.get_cube_identifiers_for_data_set()
# uri_helper = UriHelper(cube)
# dsd_helper = DsdToRdfModelsHelper(cube, uri_helper)
# dsd_helper.generate_data_structure_definitions()
print()
