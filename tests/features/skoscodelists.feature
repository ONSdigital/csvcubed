Feature: Test outputting CSV-Ws containing `SKOS:ConceptScheme`s.

  Scenario: A basic code list can be serialised to a valid CSV-W described in SKOS.
    Given a NewQbCodeList named "Basic Code-list"
    When the code list is serialised to CSV-W
    Then the file at "basic-code-list.csv" should exist
    And the file at "basic-code-list.csv-metadata.json" should exist
    And the file at "basic-code-list.table.json" should exist
    And csvlint validation of "basic-code-list.csv-metadata.json" should succeed
    And csv2rdf on "basic-code-list.csv-metadata.json" should succeed
    And the RDF should pass "skos" SPARQL tests
    And the RDF should contain
      """
        @prefix basicCodeList: <file:/tmp/basic-code-list.csv#>.

        basicCodeList:code-list a <http://www.w3.org/2004/02/skos/core#ConceptScheme>,
          <http://www.w3.org/ns/dcat#Dataset>, <http://www.w3.org/ns/dcat#Resource>;
        <http://purl.org/dc/terms/license> <http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/>;
        <http://purl.org/dc/terms/publisher> <https://www.gov.uk/government/organisations/office-for-national-statistics>;
        <http://purl.org/dc/terms/creator> <https://www.gov.uk/government/organisations/office-for-national-statistics>;
        <http://purl.org/dc/terms/title> "Basic Code-list"@en;
        <http://www.w3.org/2000/01/rdf-schema#label> "Basic Code-list"@en;
        <http://www.w3.org/2000/01/rdf-schema#comment> "Summary"@en;
        <http://purl.org/dc/terms/description> "Description"@en;
        <http://www.w3.org/ns/dcat#keyword> "Key word one"@en, "Key word two"@en;
        <http://www.w3.org/ns/dcat#landingPage> <http://example.org/landing-page>;
        <http://www.w3.org/ns/dcat#theme> <http://gss-data.org.uk/def/gdp#some-test-theme>;
        <http://www.w3.org/ns/dcat#contactPoint> <mailto:something@example.org>.

        basicCodeList:1st-concept a <http://www.w3.org/2004/02/skos/core#Concept>;
        <http://www.w3.org/2000/01/rdf-schema#comment> "This is the first concept.";
        <http://www.w3.org/2000/01/rdf-schema#label> "First Concept";
        <http://www.w3.org/2004/02/skos/core#inScheme> basicCodeList:code-list;
        <http://www.w3.org/2004/02/skos/core#notation> "1st-concept";
        <http://www.w3.org/ns/ui#sortPriority> 0 .

        basicCodeList:second-concept a <http://www.w3.org/2004/02/skos/core#Concept>;
        <http://www.w3.org/2000/01/rdf-schema#label> "Second Concept";
        <http://www.w3.org/2004/02/skos/core#broader> basicCodeList:1st-concept;
        <http://www.w3.org/2004/02/skos/core#inScheme> basicCodeList:code-list;
        <http://www.w3.org/2004/02/skos/core#notation> "second-concept";
        <http://www.w3.org/ns/ui#sortPriority> 20 .
      """

  Scenario: A code list with duplicate notations fails validation.
    Given a NewQbCodeList named "Contains Duplicates" containing duplicates
    When the code list is serialised to CSV-W
    Then csvlint validation of "contains-duplicates.csv-metadata.json" should fail with "duplicate_key"

   Scenario: A composite code list can be serialised to a valid CSV-W described in SKOS.
    Given a CompositeQbCodeList named "Composite Code List"
    When the code list is serialised to CSV-W
    Then the file at "composite-code-list.csv" should exist
    And the file at "composite-code-list.csv-metadata.json" should exist
    And the file at "composite-code-list.table.json" should exist
    And csvlint validation of all CSV-Ws should succeed
    And csv2rdf on all CSV-Ws should succeed
    And the RDF should pass "skos" SPARQL tests
    And the RDF should contain
      """
        @prefix compositeCodeList: <file:/tmp/composite-code-list.csv#>.

        compositeCodeList:code-list a <http://www.w3.org/2004/02/skos/core#ConceptScheme>,
          <http://www.w3.org/ns/dcat#Dataset>, <http://www.w3.org/ns/dcat#Resource>;
        <http://purl.org/dc/terms/license> <http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/>;
        <http://purl.org/dc/terms/publisher> <https://www.gov.uk/government/organisations/office-for-national-statistics>;
        <http://purl.org/dc/terms/creator> <https://www.gov.uk/government/organisations/office-for-national-statistics>;
        <http://purl.org/dc/terms/title> "Composite Code List"@en;
        <http://www.w3.org/2000/01/rdf-schema#label> "Composite Code List"@en;
        <http://www.w3.org/2000/01/rdf-schema#comment> "Summary"@en;
        <http://purl.org/dc/terms/description> "Description"@en;
        <http://www.w3.org/ns/dcat#keyword> "Key word one"@en, "Key word two"@en;
        <http://www.w3.org/ns/dcat#landingPage> <http://example.org/landing-page>;
        <http://www.w3.org/ns/dcat#theme> <http://gss-data.org.uk/def/gdp#some-test-theme>;
        <http://www.w3.org/ns/dcat#contactPoint> <mailto:something@example.org>;
        <http://rdf-vocabulary.ddialliance.org/xkos#variant>
            <http://data.europa.eu/nuts/scheme/2016>,
            <http://gss-data.org.uk/def/concept-scheme/geography-hierarchy/administrative>.

        compositeCodeList:wales a <http://www.w3.org/2004/02/skos/core#Concept>;
        <http://www.w3.org/2002/07/owl#sameAs> <http://data.europa.eu/nuts/code/UKL>;
        <http://www.w3.org/2000/01/rdf-schema#label> "Wales";
        <http://www.w3.org/2004/02/skos/core#notation> "wales";
        <http://www.w3.org/2004/02/skos/core#inScheme> compositeCodeList:code-list;
        <http://www.w3.org/ns/ui#sortPriority> 0.

        compositeCodeList:scotland a <http://www.w3.org/2004/02/skos/core#Concept>;
        <http://www.w3.org/2002/07/owl#sameAs> <http://data.europa.eu/nuts/code/UKM>;
        <http://www.w3.org/2000/01/rdf-schema#label> "Scotland";
        <http://www.w3.org/2004/02/skos/core#notation> "scotland";
        <http://www.w3.org/2004/02/skos/core#inScheme> compositeCodeList:code-list;
        <http://www.w3.org/ns/ui#sortPriority> 1.

        compositeCodeList:england a <http://www.w3.org/2004/02/skos/core#Concept>;
        <http://www.w3.org/2002/07/owl#sameAs> <http://statistics.data.gov.uk/id/statistical-geography/E92000001>;
        <http://www.w3.org/2000/01/rdf-schema#label> "England";
        <http://www.w3.org/2004/02/skos/core#notation> "england";
        <http://www.w3.org/2004/02/skos/core#inScheme> compositeCodeList:code-list;
        <http://www.w3.org/ns/ui#sortPriority> 2.

      """