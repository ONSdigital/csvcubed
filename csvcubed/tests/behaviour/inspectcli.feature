# Feature: Testing inspect cli (WIP).

#     Scenario: inspect cli should produce printable for a valid dataset json-ld input
#         Given the existing test-case file "cli/inspect/dataset.csv-metadata.json"
#         When loading the existing Metadata File "cli/inspect/dataset.csv-metadata.json"
#         And the Metadata File is converted to a pdf graph
#         And the Metadata File type Printable is generated
#         Then the Output should be
#             """
#             Type: This file is a data cube.
#             """