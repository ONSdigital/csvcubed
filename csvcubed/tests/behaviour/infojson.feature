Feature: info.json loader with serialisation
  Testing the info.json loader together with serialisation to CSV-W


  Scenario: Using the info.json config loader, a single-measure csv can be correctly serialised and converted to the correct RDF
    Given the existing test-case file "configloaders/single-measure-info-json-test-files/single-measure-data.csv"
    And the existing test-case file "configloaders/single-measure-info-json-test-files/single-measure-info.json"
    And we load a cube using the info.json from "configloaders/single-measure-info-json-test-files/single-measure-info.json" with CSV from "configloaders/single-measure-info-json-test-files/single-measure-data.csv"
    Then the CSVqb should pass all validations
    When the cube is serialised to CSV-W
    Then csvlint validation of "single-measure-bulletin.csv-metadata.json" should succeed
    Then csv2rdf on all CSV-Ws should succeed
    And the RDF should pass "skos, qb" SPARQL tests
    And the RDF should contain
    """
    @prefix qb: <http://purl.org/linked-data/cube#>.
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
    @prefix : <file:/tmp/single-measure-bulletin.csv#>.
    @prefix dimension: <file:/tmp/single-measure-bulletin.csv#dimension/>.
    @prefix attribute: <file:/tmp/single-measure-bulletin.csv#attribute/>.
    @prefix markervalues: <file:/tmp/single-measure-bulletin.csv#attribute/marker/>.
    @prefix component:<file:/tmp/single-measure-bulletin.csv#component/>.
    @prefix measure: <file:/tmp/single-measure-bulletin.csv#measure/>.
    :dataset a qb:DataSet;
               qb:structure :structure.
    :structure qb:component component:period, component:one-litre-and-less, component:unit, component:marker.
    component:period qb:dimension dimension:period.
    dimension:period a qb:DimensionProperty.
    component:one-litre-and-less qb:measure measure:one-litre-and-less.
    measure:one-litre-and-less a qb:MeasureProperty.
    component:marker qb:attribute attribute:marker.
    markervalues:provisional a rdfs:Resource.
    component:unit qb:attribute <http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure>.
    """

  Scenario: Using the info.json config loader, a multi-measure csv can be correctly serialised and converted to the correct RDF
    Given the existing test-case file "configloaders/multi-measure-info-json-test-files/multi-measure-data.csv"
    And the existing test-case file "configloaders/multi-measure-info-json-test-files/multi-measure-info.json"
    And we load a cube using the info.json from "configloaders/multi-measure-info-json-test-files/multi-measure-info.json" with CSV from "configloaders/multi-measure-info-json-test-files/multi-measure-data.csv"
    Then the CSVqb should pass all validations
    When the cube is serialised to CSV-W
    Then csvlint validation of "multi-measure-bulletin.csv-metadata.json" should succeed
    And csv2rdf on all CSV-Ws should succeed
    And some additional turtle is appended to the resulting RDF
    """
      @prefix qb: <http://purl.org/linked-data/cube#>.
      @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
      <http://gss-data.org.uk/def/x/number-of-bottles> a qb:MeasureProperty;
        rdfs:label "Number of bottles"@en.
      <http://gss-data.org.uk/def/x/more-than-one-litre> a qb:MeasureProperty;
        rdfs:label "Number of bottles more th an one litre"@en.
      <http://gss-data.org.uk/def/x/one-litre-and-less> a qb:MeasureProperty;
        rdfs:label "Number of bottles one litre and less"@en.
    """
    And the RDF should pass "skos, qb" SPARQL tests
    And the RDF should contain
    """
      @prefix qb: <http://purl.org/linked-data/cube#>.
      @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
      @prefix : <file:/tmp/multi-measure-bulletin.csv#>.
      @prefix dimension: <file:/tmp/multi-measure-bulletin.csv#dimension/>.
      @prefix component: <file:/tmp/multi-measure-bulletin.csv#component/>.
      @prefix measure: <http://gss-data.org.uk/def/x/>.
      :dataset a qb:DataSet;
               qb:structure :structure.
      :structure qb:component component:period, component:one-litre-and-less, component:more-than-one-litre,
                              component:number-of-bottles, component:unit.
      component:period qb:dimension dimension:period.
      dimension:period a qb:DimensionProperty.
      component:one-litre-and-less qb:measure measure:one-litre-and-less.
      component:more-than-one-litre qb:measure measure:more-than-one-litre.
      component:number-of-bottles qb:measure measure:number-of-bottles.
      component:unit qb:attribute <http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure>.
    """

  Scenario: Schema validation should not output errors when an info.json has a correct schema.
    Given the existing test-case file "configloaders/single-measure-info-json-test-files/single-measure-data.csv"
    And the existing test-case file "configloaders/info-json-schema-validation-error-test-files/single-measure-with-no-errors-info.json"
    When we load a cube using the info.json from "configloaders/info-json-schema-validation-error-test-files/single-measure-with-no-errors-info.json" with CSV from "configloaders/single-measure-info-json-test-files/single-measure-data.csv"
    Then there are no JSON schema validation errors

  Scenario: Schema validation should output errors when an info.json has an invalid schema.
    Given the existing test-case file "configloaders/single-measure-info-json-test-files/single-measure-data.csv"
    And the existing test-case file "configloaders/info-json-schema-validation-error-test-files/single-measure-with-errors-info.json"
    When we load a cube using the info.json from "configloaders/info-json-schema-validation-error-test-files/single-measure-with-errors-info.json" with CSV from "configloaders/single-measure-info-json-test-files/single-measure-data.csv"
    Then there is the following JSON schema validation error
    """
      125 is not of type 'string'
    """

  Scenario: A date-time code-list can be automatically generated for a `http://reference.data.gov.uk/id/...` period using the info.json v1.0 syntax
    Given the existing test-case file "configloaders/datetime-codelist/info.json"
    And the existing test-case file "configloaders/datetime-codelist/observations.csv"
    When we load a cube using the info.json from "configloaders/datetime-codelist/info.json" with CSV from "configloaders/datetime-codelist/observations.csv"
    Then the CSVqb should pass all validations
    When the cube is serialised to CSV-W
    Then csvlint validation of all CSV-Ws should succeed
    And csv2rdf on all CSV-Ws should succeed
    And the RDF should contain
    """
    <file:/tmp/single-measure-bulletin.csv#structure> <http://purl.org/linked-data/cube#component> <file:/tmp/single-measure-bulletin.csv#component/period>.
    <file:/tmp/single-measure-bulletin.csv#component/period>  <http://purl.org/linked-data/cube#componentProperty> <file:/tmp/single-measure-bulletin.csv#dimension/period>.
    <file:/tmp/single-measure-bulletin.csv#dimension/period>
        <http://purl.org/linked-data/cube#codeList> <file:/tmp/period.csv#code-list>;
        <http://www.w3.org/2000/01/rdf-schema#subPropertyOf> <http://purl.org/linked-data/sdmx/2009/dimension#refPeriod>.
    <file:/tmp/single-measure-bulletin.csv#obs/2021> <file:/tmp/single-measure-bulletin.csv#dimension/period> <file:/tmp/period.csv#2021>.
    <file:/tmp/period.csv#code-list> a <http://www.w3.org/2004/02/skos/core#ConceptScheme>.
    <file:/tmp/period.csv#2021> a <http://www.w3.org/2004/02/skos/core#Concept>;
      <http://www.w3.org/2000/01/rdf-schema#label> "2021";
      <http://www.w3.org/2002/07/owl#sameAs> <http://reference.data.gov.uk/id/year/2021>;
      <http://www.w3.org/2004/02/skos/core#inScheme> <file:/tmp/period.csv#code-list>;
      <http://www.w3.org/2004/02/skos/core#notation> "2021".
    """

  Scenario: A date-time code-list can be automatically generated for a `http://reference.data.gov.uk/id/...` period using the info.json v1.1 syntax
    Given the existing test-case file "configloaders/datetime-codelist/info.1.json"
    And the existing test-case file "configloaders/datetime-codelist/observations.csv"
    When we load a cube using the info.json from "configloaders/datetime-codelist/info.1.json" with CSV from "configloaders/datetime-codelist/observations.csv"
    Then the CSVqb should pass all validations
    When the cube is serialised to CSV-W
    Then csvlint validation of all CSV-Ws should succeed
    And csv2rdf on all CSV-Ws should succeed
    And the RDF should contain
    """
    <file:/tmp/single-measure-bulletin.csv#structure> <http://purl.org/linked-data/cube#component> <file:/tmp/single-measure-bulletin.csv#component/period>.
    <file:/tmp/single-measure-bulletin.csv#component/period>  <http://purl.org/linked-data/cube#componentProperty> <file:/tmp/single-measure-bulletin.csv#dimension/period>.
    <file:/tmp/single-measure-bulletin.csv#dimension/period>
        <http://purl.org/linked-data/cube#codeList> <file:/tmp/period.csv#code-list>;
        <http://www.w3.org/2000/01/rdf-schema#subPropertyOf> <http://purl.org/linked-data/sdmx/2009/dimension#refPeriod>.
    <file:/tmp/single-measure-bulletin.csv#obs/2021> <file:/tmp/single-measure-bulletin.csv#dimension/period> <file:/tmp/period.csv#2021>.
    <file:/tmp/period.csv#code-list> a <http://www.w3.org/2004/02/skos/core#ConceptScheme>.
    <file:/tmp/period.csv#2021> a <http://www.w3.org/2004/02/skos/core#Concept>;
      <http://www.w3.org/2000/01/rdf-schema#label> "2021";
      <http://www.w3.org/2002/07/owl#sameAs> <http://reference.data.gov.uk/id/year/2021>;
      <http://www.w3.org/2004/02/skos/core#inScheme> <file:/tmp/period.csv#code-list>;
      <http://www.w3.org/2004/02/skos/core#notation> "2021".
    """