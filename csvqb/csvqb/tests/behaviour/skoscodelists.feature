Feature: Test outputting CSV-Ws containing `SKOS:ConceptScheme`s.

  Scenario: A basic code list can be serialised to a valid CSV-W described in SKOS.
    Given a NewQbCodeList named "Basic Code-list"
    When the code list is serialised to CSV-W
    Then the file at "basic-code-list.csv" should exist
    And the file at "basic-code-list.csv-metadata.json" should exist
    And csvlint validation of "basic-code-list.csv-metadata.json" should succeed
    And csv2rdf on "basic-code-list.csv-metadata.json" should succeed
    And the RDF should pass "skos" SPARQL tests
    And the RDF should contain
      """
          @prefix : <file:/tmp/basic-code-list.csv#>.
          @prefix concept: <file:/tmp/basic-code-list.csv#concept/>.

          :scheme a <http://www.w3.org/2004/02/skos/core#ConceptScheme>,
            <http://www.w3.org/ns/dcat#Dataset>, <http://www.w3.org/ns/dcat#Resource>;
          <http://purl.org/dc/terms/license> <http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/>;
          <http://purl.org/dc/terms/publisher> <https://www.gov.uk/government/organisations/office-for-national-statistics>;
          <http://purl.org/dc/terms/title> "Basic Code-list"@en;
          <http://www.w3.org/2000/01/rdf-schema#label> "Basic Code-list"@en;
          <http://www.w3.org/2000/01/rdf-schema#comment> "Summary"@en;
          <http://purl.org/dc/terms/description> "Description"@en;
          <http://www.w3.org/2000/01/rdf-schema#seeAlso> :scheme;
          <http://www.w3.org/ns/dcat#keyword> "Key word one"@en, "Key word two"@en;
          <http://www.w3.org/ns/dcat#landingPage> <http://example.org/landing-page>;
          <http://www.w3.org/ns/dcat#theme> <http://gss-data.org.uk/def/gdp#some-test-theme> .

        concept:1st-concept <http://www.w3.org/2000/01/rdf-schema#comment> "This is the first concept.";
          <http://www.w3.org/2000/01/rdf-schema#label> "First Concept";
          <http://www.w3.org/2004/02/skos/core#inScheme> <file:/tmp/basic-code-list.csv#scheme>;
          <http://www.w3.org/2004/02/skos/core#notation> "1st-concept";
          <http://www.w3.org/ns/ui#sortPriority> 0 .

        concept:second-concept <http://www.w3.org/2000/01/rdf-schema#label> "Second Concept";
          <http://www.w3.org/2004/02/skos/core#broader> concept:1st-concept;
          <http://www.w3.org/2004/02/skos/core#inScheme> <file:/tmp/basic-code-list.csv#scheme>;
          <http://www.w3.org/2004/02/skos/core#notation> "second-concept";
          <http://www.w3.org/ns/ui#sortPriority> 20 .
      """