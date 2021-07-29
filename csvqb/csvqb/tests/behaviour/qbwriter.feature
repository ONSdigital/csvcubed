Feature: Test outputting CSV-Ws with Qb flavouring.

  Scenario: A QbCube should generate appropriate DCAT Metadata
    Given a single-measure QbCube named "Some Qube"
    When the cube is serialised to CSV-W
    Then the file at "some-qube.csv" should exist
    And the file at "some-qube.csv-metadata.json" should exist
    And csvlint validation of all CSV-Ws should succeed
    And csv2rdf on all CSV-Ws should succeed
    And the RDF should contain
      """
        <file:/tmp/some-qube.csv#dataset> a <http://www.w3.org/ns/dcat#Dataset>;
          <http://purl.org/dc/terms/description> "Description"@en;
          <http://purl.org/dc/terms/license> <http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/>;
          <http://purl.org/dc/terms/creator> <https://www.gov.uk/government/organisations/office-for-national-statistics>;
          <http://purl.org/dc/terms/publisher> <https://www.gov.uk/government/organisations/office-for-national-statistics>;
          <http://purl.org/dc/terms/title> "Some Qube"@en;
          <http://www.w3.org/2000/01/rdf-schema#comment> "Summary"@en;
          <http://www.w3.org/2000/01/rdf-schema#label> "Some Qube"@en;
          <http://www.w3.org/ns/dcat#keyword> "Key word one"@en, "Key word two"@en;
          <http://www.w3.org/ns/dcat#landingPage> <http://example.org/landing-page>;
          <http://www.w3.org/ns/dcat#theme> <http://gss-data.org.uk/def/gdp#some-test-theme>;
          <http://www.w3.org/ns/dcat#contactPoint> <mailto:something@example.org>.
      """

   Scenario: A QbCube validate successfully where foreign key constraints are met.
    Given a single-measure QbCube named "Some Qube"
    When the cube is serialised to CSV-W
    Then the file at "a-code-list.csv-metadata.json" should exist
    And csvlint validation of "some-qube.csv-metadata.json" should succeed

  Scenario: A QbCube should fail to validate where foreign key constraints are not met.
    Given a single-measure QbCube named "Some Qube" with codes not defined in the code-list
    When the cube is serialised to CSV-W
    Then the file at "a-code-list.csv-metadata.json" should exist
    And csvlint validation of "some-qube.csv-metadata.json" should fail with "unmatched_foreign_key_reference"

  Scenario: A QbCube with existing dimensions should not do foreign key checks.
    Given a single-measure QbCube named "Some Qube" with existing dimensions
    When the cube is serialised to CSV-W
    Then csvlint validation of "some-qube.csv-metadata.json" should succeed
