Feature: Testing the csvw command group in the CLI

  Scenario: The `pmdify` command should remove DCAT metadata from the CSV-W it is processing.
    Given the existing test-case files "dcatcli/*"
    When the pmdutils command CLI is run with "dcat pmdify single-measure-bulletin.csv-metadata.json http://base-uri http://data-graph-uri http://catalog-metadata-graph-uri"
    Then the CLI should succeed
    And csvlint validation of "single-measure-bulletin.csv-metadata.json" should succeed
    And csv2rdf on "single-measure-bulletin.csv-metadata.json" should succeed
    And the RDF should not contain any instances of "http://www.w3.org/ns/dcat#Dataset"
    And the RDF should contain
    """
      <http://base-uri/single-measure-bulletin.csv#dataset> a <http://purl.org/linked-data/cube#DataSet>.
    """

  Scenario: The `pmdify` command should create a separate N-Quads file containing pmd-style catalog metadata.
    Given the existing test-case files "dcatcli/*"
    When the pmdutils command CLI is run with "dcat pmdify single-measure-bulletin.csv-metadata.json http://base-uri http://data-graph-uri http://catalog-metadata-graph-uri"
    Then the CLI should succeed
    And the file at "single-measure-bulletin.csv-metadata.json.nq" should exist
    Given the N-Quads contained in "single-measure-bulletin.csv-metadata.json.nq"
    Then the RDF should contain
    """
      @prefix dcat: <http://www.w3.org/ns/dcat#> .
      @prefix dct: <http://purl.org/dc/terms/> .
      @prefix pmdcat: <http://publishmydata.com/pmdcat#> .
      @prefix void: <http://rdfs.org/ns/void#> .
      @prefix foaf: <http://xmlns.com/foaf/0.1/> .
      @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
      @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

      <http://gss-data.org.uk/catalog/datasets> dcat:record <http://base-uri/single-measure-bulletin.csv#dataset-catalog-record> .

      <http://base-uri/single-measure-bulletin.csv#dataset-catalog-entry> a pmdcat:Dataset;
          rdfs:label "single-measure-bottles-bulletin"@en;
          pmdcat:datasetContents <http://base-uri/single-measure-bulletin.csv#dataset>;
          pmdcat:graph <http://data-graph-uri>;
          pmdcat:metadataGraph <http://catalog-metadata-graph-uri>;
          dct:creator <https://www.gov.uk/government/organisations/hm-revenue-customs>;
          dct:description "All bulletins provide details on percentage of one litre or less bottles. This information is provided on a yearly basis."@en;
          dct:identifier "single-measure-bottles-bulletin";
          dct:issued "2019-02-28T00:00:00"^^xsd:dateTime;
          dct:modified "2019-02-28T00:00:00"^^xsd:dateTime;
          dct:publisher <https://www.gov.uk/government/organisations/hm-revenue-customs>;
          dct:title "single-measure-bottles-bulletin"@en;
          void:sparqlEndpoint <https://staging.gss-data.org.uk/sparql>;
          dcat:keyword "keyword1"@en, "keyword2"@en;
          dcat:landingPage <https://www.gov.uk/government/statistics/bottles-bulletin>;
          dcat:theme <http://gss-data.org.uk/def/gdp#Trade>.

      <http://base-uri/single-measure-bulletin.csv#dataset-catalog-record> a dcat:CatalogRecord;
          rdfs:label "single-measure-bottles-bulletin"@en;
          pmdcat:metadataGraph <http://catalog-metadata-graph-uri>;
          dct:description "All bulletins provide details on percentage of one litre or less bottles. This information is provided on a yearly basis."@en;
          dct:title "single-measure-bottles-bulletin"@en;
          foaf:primaryTopic <http://base-uri/single-measure-bulletin.csv#dataset-catalog-entry> .

      # the qb:Dataset needs to be a pmdcat:Dataset too since it's referenced by a catalog record.
      <http://base-uri/single-measure-bulletin.csv#dataset> a <http://publishmydata.com/pmdcat#DataCube>.
    """

  Scenario: The `pmdify` command should add the `pmdcat:Dataset` type to `qb:DataSet`s
    Given the existing test-case files "dcatcli/*"
    When the pmdutils command CLI is run with "dcat pmdify single-measure-bulletin.csv-metadata.json http://base-uri http://data-graph-uri http://catalog-metadata-graph-uri"
    Then the CLI should succeed
    And the file at "single-measure-bulletin.csv-metadata.json.nq" should exist
    Given the N-Quads contained in "single-measure-bulletin.csv-metadata.json.nq"
    Then the RDF should contain
    """
      <http://base-uri/single-measure-bulletin.csv#dataset> a <http://publishmydata.com/pmdcat#DataCube>.
    """

  Scenario: The `pmdify` command should add the `pmdcat:ConceptScheme` type to `skos:ConceptScheme`s
    Given the existing test-case files "dcatcli/*"
    When the pmdutils command CLI is run with "dcat pmdify period.csv-metadata.json http://base-uri http://data-graph-uri http://catalog-metadata-graph-uri"
    Then the CLI should succeed
    And the file at "period.csv-metadata.json.nq" should exist
    Given the N-Quads contained in "period.csv-metadata.json.nq"
    Then the RDF should contain
    """
      <http://base-uri/period.csv#scheme/period> a <http://publishmydata.com/pmdcat#ConceptScheme>.
    """


   Scenario: The `pmdify` command should insert `qb:DataSet`s into the datasets catalogue.
    Given the existing test-case files "dcatcli/*"
    When the pmdutils command CLI is run with "dcat pmdify single-measure-bulletin.csv-metadata.json http://base-uri http://data-graph-uri http://catalog-metadata-graph-uri"
    Then the CLI should succeed
    And the file at "single-measure-bulletin.csv-metadata.json.nq" should exist
    Given the N-Quads contained in "single-measure-bulletin.csv-metadata.json.nq"
    Then the RDF should contain
    """
      @prefix dcat: <http://www.w3.org/ns/dcat#> .

      <http://gss-data.org.uk/catalog/datasets> dcat:record <http://base-uri/single-measure-bulletin.csv#dataset-catalog-record> .
     """

  Scenario: The `pmdify` command should insert `skos:ConceptSchemes`s into the vocabularies catalogue.
    Given the existing test-case files "dcatcli/*"
    When the pmdutils command CLI is run with "dcat pmdify period.csv-metadata.json http://base-uri http://data-graph-uri http://catalog-metadata-graph-uri"
    Then the CLI should succeed
    And the file at "period.csv-metadata.json.nq" should exist
    Given the N-Quads contained in "period.csv-metadata.json.nq"
    Then the RDF should contain
    """
      @prefix dcat: <http://www.w3.org/ns/dcat#> .

      <http://gss-data.org.uk/catalog/vocabularies> dcat:record <http://base-uri/period.csv#scheme/period-catalog-record> .
     """

  Scenario: The `pmdify` command should work on legacy code-list `itis-industry.csv`
    Given the existing test-case files "dcatcli/*"
    When the pmdutils command CLI is run with "dcat pmdify itis-industry.csv-metadata.json http://base-uri http://data-graph-uri http://catalog-metadata-graph-uri"
    Then the CLI should succeed
    And csvlint validation of "itis-industry.csv-metadata.json" should succeed
    And csv2rdf on "itis-industry.csv-metadata.json" should succeed
    And the RDF should not contain any instances of "http://www.w3.org/ns/dcat#Dataset"
    And the RDF should contain
    """
      <http://gss-data.org.uk/data/gss_data/trade/ons-international-trade-in-services#scheme/itis-industry> a <http://publishmydata.com/pmdcat#ConceptScheme>.
    """
    Given the N-Quads contained in "itis-industry.csv-metadata.json.nq"
    Then the RDF should contain
    """
      @prefix dcat: <http://www.w3.org/ns/dcat#>.
      @prefix foaf: <http://xmlns.com/foaf/0.1/>.

      <http://gss-data.org.uk/data/gss_data/trade/ons-international-trade-in-services#scheme/itis-industry/dataset-catalog-record> a dcat:CatalogRecord;
        foaf:primaryTopic <http://gss-data.org.uk/data/gss_data/trade/ons-international-trade-in-services#scheme/itis-industry/dataset-catalog-entry>.

      <http://gss-data.org.uk/catalog/vocabularies> dcat:record <http://gss-data.org.uk/data/gss_data/trade/ons-international-trade-in-services#scheme/itis-industry/dataset-catalog-record>.

      <http://gss-data.org.uk/data/gss_data/trade/ons-international-trade-in-services#scheme/itis-industry/dataset-catalog-entry> a dcat:Dataset.
    """
    # Ensuring there is only one catalog record
    And the ask query should return false
    """
      PREFIX dcat: <http://www.w3.org/ns/dcat#>

      ASK
      WHERE {
        ?catalogRecord a dcat:CatalogRecord.
      }
      HAVING (COUNT(DISTINCT ?catalogRecord) != 1)
    """
    # Ensuring there is only one catalog entry
    And the ask query should return false
    """
      PREFIX dcat: <http://www.w3.org/ns/dcat#>
      PREFIX foaf: <http://xmlns.com/foaf/0.1/>

      ASK
      WHERE {
          ?catalogEntry a dcat:Dataset.
      }
      HAVING (COUNT(DISTINCT ?catalogEntry) != 1)
    """