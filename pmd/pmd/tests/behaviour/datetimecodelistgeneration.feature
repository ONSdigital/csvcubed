Feature: Date/Time Code List Generation from CSV-W

  Scenario: Generation of Month code list from HMRC Overseas Trade Statistics
    Given the existing test-case files "hmrc-overseas-trade-statistics-cn8.*"
    And a CSV-qb "hmrc-overseas-trade-statistics-cn8.csv-metadata.json"
    When a date/time code lists is generated from the CSV-qb
    Then the file at "Month.csv-metadata.json" should exist
    And csvlint validation of "Month.csv-metadata.json" should succeed
    And csv2rdf on "Month.csv-metadata.json" should succeed
    And the RDF should contain
    """
      <http://gss-data.org.uk/data/gss_data/trade/hmrc-overseas-trade-statistics/hmrc-overseas-trade-statistics-cn8#scheme/period>
        a <http://publishmydata.com/pmdcat#ConceptScheme>, <http://www.w3.org/2004/02/skos/core#ConceptScheme>;
        <http://purl.org/dc/terms/title> "Month"@en;
        <http://www.w3.org/2000/01/rdf-schema#comment> "Month code list containing date/time concepts."@en;
        <http://www.w3.org/2000/01/rdf-schema#label> "Month"@en;
        <http://www.w3.org/2004/02/skos/core#hasTopConcept> <http://reference.data.gov.uk/id/month/2020-09>,
          <http://reference.data.gov.uk/id/month/2020-10>, <http://reference.data.gov.uk/id/month/2020-11>.

      <http://gss-data.org.uk/catalog/vocabularies> <http://www.w3.org/ns/dcat#record> <http://gss-data.org.uk/data/gss_data/trade/hmrc-overseas-trade-statistics/hmrc-overseas-trade-statistics-cn8#scheme/period/catalog-record> .

      <http://gss-data.org.uk/data/gss_data/trade/hmrc-overseas-trade-statistics/hmrc-overseas-trade-statistics-cn8#scheme/period/dataset>
        a <http://publishmydata.com/pmdcat#Dataset>, <http://www.w3.org/ns/dcat#Dataset>,
          <http://www.w3.org/ns/dcat#Resource>;
        <http://publishmydata.com/pmdcat#datasetContents> <http://gss-data.org.uk/data/gss_data/trade/hmrc-overseas-trade-statistics/hmrc-overseas-trade-statistics-cn8#scheme/period>;
        <http://publishmydata.com/pmdcat#graph> <http://gss-data.org.uk/data/gss_data/trade/hmrc-overseas-trade-statistics/hmrc-overseas-trade-statistics-cn8#scheme/period>;
        <http://publishmydata.com/pmdcat#metadataGraph> <http://gss-data.org.uk/data/gss_data/trade/hmrc-overseas-trade-statistics/hmrc-overseas-trade-statistics-cn8#scheme/period>;
        <http://purl.org/dc/terms/title> "Month"@en;
        <http://rdfs.org/ns/void#sparqlEndpoint> <https://staging.gss-data.org.uk/sparql>;
        <http://www.w3.org/2000/01/rdf-schema#comment> "Month code list containing date/time concepts."@en;
        <http://www.w3.org/2000/01/rdf-schema#label> "Month"@en .

      <http://gss-data.org.uk/data/gss_data/trade/hmrc-overseas-trade-statistics/hmrc-overseas-trade-statistics-cn8#scheme/period/catalog-record>
        a <http://www.w3.org/ns/dcat#CatalogRecord>;
        <http://publishmydata.com/pmdcat#metadataGraph> <http://gss-data.org.uk/data/gss_data/trade/hmrc-overseas-trade-statistics/hmrc-overseas-trade-statistics-cn8#scheme/period>;
        <http://purl.org/dc/terms/description> "Month code list containing date/time concepts."@en;
        <http://purl.org/dc/terms/title> "Month"@en;
        <http://www.w3.org/2000/01/rdf-schema#comment> "Month code list containing date/time concepts."@en;
        <http://www.w3.org/2000/01/rdf-schema#label> "Month"@en;
        <http://xmlns.com/foaf/0.1/primaryTopic> <http://gss-data.org.uk/data/gss_data/trade/hmrc-overseas-trade-statistics/hmrc-overseas-trade-statistics-cn8#scheme/period/dataset> .

      <http://reference.data.gov.uk/id/month/2020-09> a <http://www.w3.org/2004/02/skos/core#Concept>;
        <http://www.w3.org/2004/02/skos/core#inScheme> <http://gss-data.org.uk/data/gss_data/trade/hmrc-overseas-trade-statistics/hmrc-overseas-trade-statistics-cn8#scheme/period>;
        <http://www.w3.org/ns/ui#sortPriority> 0 .

      <http://reference.data.gov.uk/id/month/2020-10> a <http://www.w3.org/2004/02/skos/core#Concept>;
        <http://www.w3.org/2004/02/skos/core#inScheme> <http://gss-data.org.uk/data/gss_data/trade/hmrc-overseas-trade-statistics/hmrc-overseas-trade-statistics-cn8#scheme/period>;
        <http://www.w3.org/ns/ui#sortPriority> 1 .

      <http://reference.data.gov.uk/id/month/2020-11> a <http://www.w3.org/2004/02/skos/core#Concept>;
        <http://www.w3.org/2004/02/skos/core#inScheme> <http://gss-data.org.uk/data/gss_data/trade/hmrc-overseas-trade-statistics/hmrc-overseas-trade-statistics-cn8#scheme/period>;
        <http://www.w3.org/ns/ui#sortPriority> 2 .
    """
