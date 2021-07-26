Feature: Test outputting CSV-Ws containing `SKOS:ConceptScheme`s.

  Scenario: A Single-measure QbCube should generate appropriate DCAT Metadata
    Given a single-measure QbCube named "Some Qube"
    When the cube is serialised to CSV-W
    Then the file at "some-qube.csv" should exist
    And the file at "some-qube.csv-metadata.json" should exist
    And csvlint validation of all CSV-Ws should succeed
    And csv2rdf on all CSV-Ws should succeed
    And the RDF should pass "all" SPARQL tests
#    And the RDF should contain
#      """
#      """