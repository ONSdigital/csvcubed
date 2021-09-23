Feature: Test outputting CSV-Ws with Qb flavouring.

  Scenario: A QbCube should generate appropriate DCAT Metadata
    Given a single-measure QbCube with identifier "qb-id-10002" named "Some Qube"
    When the cube is serialised to CSV-W
    Then the file at "qb-id-10002.csv" should exist
    And the file at "qb-id-10002.csv-metadata.json" should exist
    And csvlint validation of all CSV-Ws should succeed
    And csv2rdf on all CSV-Ws should succeed
    And the RDF should contain
      """
      <file:/tmp/qb-id-10002.csv#dataset> a <http://www.w3.org/ns/dcat#Dataset>;
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
      <http://www.w3.org/ns/dcat#contactPoint> <mailto:something@example.org>;
      <http://purl.org/dc/terms/identifier> "qb-id-10002".
      """

  Scenario: A QbCube should validate successfully where foreign key constraints are met.
    Given a single-measure QbCube named "Some Qube"
    When the cube is serialised to CSV-W
    Then the file at "a-code-list.csv-metadata.json" should exist
    And csvlint validation of "some-qube.csv-metadata.json" should succeed
    And csv2rdf on "some-qube.csv-metadata.json" should succeed
    And the RDF should not contain any instances of "http://www.w3.org/2004/02/skos/core#ConceptScheme"

  Scenario: A QbCube should fail to validate where foreign key constraints are not met.
    Given a single-measure QbCube named "Some Qube" with codes not defined in the code-list
    When the cube is serialised to CSV-W (suppressing missing uri value exceptions)
    Then the file at "a-code-list.csv-metadata.json" should exist
    And csvlint validation of "some-qube.csv-metadata.json" should fail with "unmatched_foreign_key_reference"

  Scenario: A QbCube with existing dimensions should not do foreign key checks.
    Given a single-measure QbCube named "Some Qube" with existing dimensions
    When the cube is serialised to CSV-W
    Then csvlint validation of "some-qube.csv-metadata.json" should succeed

  Scenario: A single-measure QbCube with duplicate rows should fail validation
    Given a single-measure QbCube named "Duplicate Qube" with duplicate rows
    When the cube is serialised to CSV-W
    Then csvlint validation of "duplicate-qube.csv-metadata.json" should fail with "duplicate_key"

  Scenario: A multi-measure QbCube should pass validation
    Given a multi-measure QbCube named "Duplicate Qube"
    When the cube is serialised to CSV-W
    Then csvlint validation of "duplicate-qube.csv-metadata.json" should succeed
  # todo: complete me in Issue #65

  Scenario: A multi-measure QbCube with duplicate rows should fail validation
    Given a multi-measure QbCube named "Duplicate Qube" with duplicate rows
    When the cube is serialised to CSV-W
    Then csvlint validation of "duplicate-qube.csv-metadata.json" should fail with "duplicate_key"

  Scenario: QbCube new attribute values and units should be serialised
    Given a single-measure QbCube named "Some Qube" with new attribute values and units
    When the cube is serialised to CSV-W
    Then the file at "some-qube.csv" should exist
    And the file at "some-qube.csv-metadata.json" should exist
    And csvlint validation of all CSV-Ws should succeed
    And csv2rdf on all CSV-Ws should succeed
    And the RDF should contain
    """
      @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
      @prefix skos: <http://www.w3.org/2004/02/skos/core#>.
      @prefix qudt: <http://qudt.org/schema/qudt/>.
      @prefix om2: <http://www.ontology-of-units-of-measure.org/resource/om-2/>.

      <file:/tmp/some-qube.csv#attribute/new-attribute/pending>
        a skos:Concept;
        rdfs:label "pending"@en.

      <file:/tmp/some-qube.csv#attribute/new-attribute/final>
        a skos:Concept;
        rdfs:label "final"@en.

      <file:/tmp/some-qube.csv#attribute/new-attribute/in-review>
        a skos:Concept;
        rdfs:label "in-review"@en.

      <file:/tmp/some-qube.csv#unit/some-unit>
        a qudt:Unit, om2:Unit;
        rdfs:label "Some Unit"@en.
    """

  Scenario: QbCube extended units (and new base units) should be serialised correctly.
    Given a single-measure QbCube named "Some Qube" with one new unit extending another new unit
    When the cube is serialised to CSV-W
    Then csvlint validation of all CSV-Ws should succeed
    And csv2rdf on all CSV-Ws should succeed
    And the RDF should contain
    """
      @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
      @prefix qudt: <http://qudt.org/schema/qudt/>.
      @prefix om2: <http://www.ontology-of-units-of-measure.org/resource/om-2/>.
      @prefix xsd: <http://www.w3.org/2001/XMLSchema#>.

      <file:/tmp/some-qube.csv#unit/some-base-unit>
        a qudt:Unit, om2:Unit;
        rdfs:label "Some Base Unit"@en.

      <file:/tmp/some-qube.csv#unit/some-extending-unit>
        a qudt:Unit, om2:Unit;
        qudt:isScalingOf <file:/tmp/some-qube.csv#unit/some-base-unit>;
        qudt:hasQuantityKind <http://some-quantity-kind>;
        qudt:conversionMultiplier "25.123123"^^xsd:float;
        om2:hasUnit <file:/tmp/some-qube.csv#unit/some-base-unit>;
        om2:hasFactor "1000.0"^^xsd:float;
        rdfs:label "Some Extending Unit"@en.
    """

  Scenario: A QbCube with string literal new attributes should validate successfully
    Given a single-measure QbCube named "Qube with string literals" with "new" "string" attribute
    When the cube is serialised to CSV-W
    Then csvlint validation of "qube-with-string-literals.csv-metadata.json" should succeed
    And csv2rdf on all CSV-Ws should succeed
    # And turtle should be written to "output.ttl"
    And the RDF should contain
      """
      <file:/tmp/qube-with-string-literals.csv#obs/uss-cerritos> <file:/tmp/qube-with-string-literals.csv#attribute/first-captain>
      "William Riker".
      """
    And the RDF should contain
      """
      <file:/tmp/qube-with-string-literals.csv#obs/uss-titan> <file:/tmp/qube-with-string-literals.csv#attribute/first-captain>
      "Carol Freeman".
      """

  Scenario: A QbCube with numeric literal new attributes should validate successfully
    Given a single-measure QbCube named "Qube with int literals" with "new" "int" attribute
    When the cube is serialised to CSV-W
    Then csvlint validation of "qube-with-int-literals.csv-metadata.json" should succeed
    And csv2rdf on all CSV-Ws should succeed
    # And turtle should be written to "output.ttl"
    And the RDF should contain
      """
      <file:/tmp/qube-with-int-literals.csv#obs/uss-cerritos> <file:/tmp/qube-with-int-literals.csv#attribute/reg>
      "75567"^^<http://www.w3.org/2001/XMLSchema#int>.
      """
    And the RDF should contain
      """
      <file:/tmp/qube-with-int-literals.csv#obs/uss-titan> <file:/tmp/qube-with-int-literals.csv#attribute/reg>
      "80102"^^<http://www.w3.org/2001/XMLSchema#int>.
      """

  Scenario: A QbCube with date literal new attributes should validate successfully
    Given a single-measure QbCube named "Qube with date literals" with "new" "date" attribute
    When the cube is serialised to CSV-W
    Then csvlint validation of "qube-with-date-literals.csv-metadata.json" should succeed
    And csv2rdf on all CSV-Ws should succeed
    # And turtle should be written to "output.ttl"
    And the RDF should contain
      """
      <file:/tmp/qube-with-date-literals.csv#obs/uss-cerritos> <file:/tmp/qube-with-date-literals.csv#attribute/appeared>
      "2020-08-06"^^<http://www.w3.org/2001/XMLSchema#date>.
      """
    And the RDF should contain
      """
      <file:/tmp/qube-with-date-literals.csv#obs/uss-titan> <file:/tmp/qube-with-date-literals.csv#attribute/appeared>
      "2020-10-08"^^<http://www.w3.org/2001/XMLSchema#date>.
      """

  Scenario: A QbCube with string literal existing attributes should validate successfully
    Given a single-measure QbCube named "Qube with string literals" with "existing" "string" attribute
    When the cube is serialised to CSV-W
    Then csvlint validation of "qube-with-string-literals.csv-metadata.json" should succeed
    And csv2rdf on all CSV-Ws should succeed
    # And turtle should be written to "output.ttl"
    And the RDF should contain
      """
      <file:/tmp/qube-with-string-literals.csv#obs/uss-cerritos> <http://some-uri> "William Riker".
      """
    And the RDF should contain
      """
      <file:/tmp/qube-with-string-literals.csv#obs/uss-titan> <http://some-uri> "Carol Freeman".
      """

  Scenario: A QbCube with numeric literal existing attributes should validate successfully
    Given a single-measure QbCube named "Qube with int literals" with "existing" "int" attribute
    When the cube is serialised to CSV-W
    Then csvlint validation of "qube-with-int-literals.csv-metadata.json" should succeed
    And csv2rdf on all CSV-Ws should succeed
    # And turtle should be written to "output.ttl"
    And the RDF should contain
      """
      <file:/tmp/qube-with-int-literals.csv#obs/uss-cerritos> <http://some-uri> "75567"^^<http://www.w3.org/2001/XMLSchema#int>.
      """
    And the RDF should contain
      """
      <file:/tmp/qube-with-int-literals.csv#obs/uss-titan> <http://some-uri> "80102"^^<http://www.w3.org/2001/XMLSchema#int>.
      """

  Scenario: A QbCube with date literal existing attributes should validate successfully
    Given a single-measure QbCube named "Qube with date literals" with "existing" "date" attribute
    When the cube is serialised to CSV-W
    Then csvlint validation of "qube-with-date-literals.csv-metadata.json" should succeed
    And csv2rdf on all CSV-Ws should succeed
    # And turtle should be written to "output.ttl"
    And the RDF should contain
      """
      <file:/tmp/qube-with-date-literals.csv#obs/uss-cerritos> <http://some-uri> "2020-08-06"^^<http://www.w3.org/2001/XMLSchema#date>.
      """
    And the RDF should contain
      """
      <file:/tmp/qube-with-date-literals.csv#obs/uss-titan> <http://some-uri> "2020-10-08"^^<http://www.w3.org/2001/XMLSchema#date>.
      """

  Scenario: A single-measure QbCube should pass skos+qb SPARQL test constraints
    Given a single-measure QbCube named "Some Qube"
    When the cube is serialised to CSV-W
    Then csvlint validation of all CSV-Ws should succeed
    And csv2rdf on all CSV-Ws should succeed
    And the RDF should pass "skos, qb" SPARQL tests
    # PMD test constraints won't pass because the CSV-W we're outputting needs to pass
    # through Jenkins to pick up PMD-specific augmentation.

  Scenario: A multi-measure QbCube should pass skos+qb SPARQL test constraints
    Given a multi-measure QbCube named "Some Qube"
    When the cube is serialised to CSV-W
    Then csvlint validation of all CSV-Ws should succeed
    And csv2rdf on all CSV-Ws should succeed
    And the RDF should pass "skos, qb" SPARQL tests
    # PMD test constraints won't pass because the CSV-W we're outputting needs to pass
    # through Jenkins to pick up PMD-specific augmentation.

  Scenario: A locally defined single-measure dataset (with code-lists) can be serialised to a standard CSV-qb
    Given a single-measure QbCube named "single-measure qube with new definitions" with all new units/measures/dimensions/attributes/codelists
    When the cube is serialised to CSV-W
    Then csvlint validation of "single-measure-qube-with-new-definitions.csv-metadata.json" should succeed
    And csv2rdf on all CSV-Ws should succeed
    And the RDF should pass "skos, qb" SPARQL tests

  Scenario: A locally defined multi-measure dataset (with code-lists) can be serialised to a standard CSV-qb
    Given a multi-measure QbCube named "multi-measure qube with new definitions" with all new units/measures/dimensions/attributes/codelists
    When the cube is serialised to CSV-W
    Then csvlint validation of "multi-measure-qube-with-new-definitions.csv-metadata.json" should succeed
    And csv2rdf on all CSV-Ws should succeed
    And the RDF should pass "skos, qb" SPARQL tests

  Scenario: A single-measure dataset (with code-list) having existing resources can be serialised to a standard CSV-qb
    Given a single measure QbCube named "single-measure qube with existing resources" with existing units/measure/dimensions/attribute/codelists
    When the cube is serialised to CSV-W
    Then csvlint validation of "single-measure-qube-with-existing-resources.csv-metadata.json" should succeed
    And csv2rdf on all CSV-Ws should succeed
    And some additional turtle is appended to the resulting RDF
    """
      @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
      @prefix qb: <http://purl.org/linked-data/cube#>.
      @prefix skos: <http://www.w3.org/2004/02/skos/core#>.
      @prefix xsd: <http://www.w3.org/2001/XMLSchema#>.

      <http://existing/dimension>
          rdfs:label "Some Existing Dimension"@en;
          a qb:DimensionProperty;
          qb:codeList <http://existing/dimension/code-list>;
          rdfs:range <http://some/range/thingy>.

      <http://existing/dimension/code-list> a skos:ConceptScheme;
        skos:hasTopConcept <http://existing/dimension/code-list/all>.

      <http://existing/dimension/code-list/all> a skos:Concept;
        rdfs:label "All possible things"@en.

      <http://existing/attribute> a qb:AttributeProperty;
          rdfs:label "Some existing attribute property"@en.

      <http://existing/measure> a qb:MeasureProperty;
          rdfs:label "Some existing measure property"@en;
          rdfs:range xsd:decimal.

      <http://existing/unit> rdfs:label "Some Existing Unit"@en.
    """
    And the RDF should pass "skos, qb" SPARQL tests

  Scenario: A multi-measure dataset (with code-list) having existing resources can be serialised to a standard CSV-qb
    Given a multi measure QbCube named "multi-measure qube with existing resources" with existing units/measure/dimensions/attribute/codelists
    When the cube is serialised to CSV-W
    Then csvlint validation of "multi-measure-qube-with-existing-resources.csv-metadata.json" should succeed
    And csv2rdf on all CSV-Ws should succeed
    And some additional turtle is appended to the resulting RDF
    """
      @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
      @prefix qb: <http://purl.org/linked-data/cube#>.
      @prefix skos: <http://www.w3.org/2004/02/skos/core#>.
      @prefix xsd: <http://www.w3.org/2001/XMLSchema#>.

      <http://existing/dimension>
          rdfs:label "Some Existing Dimension"@en;
          a qb:DimensionProperty;
          qb:codeList <http://existing/dimension/code-list>;
          rdfs:range <http://some/range/thingy>.

      <http://existing/dimension/code-list> a skos:ConceptScheme;
        skos:hasTopConcept <http://existing/dimension/code-list/all>.

      <http://existing/dimension/code-list/all> a skos:Concept;
        rdfs:label "All possible things"@en.

      <http://existing/attribute> a qb:AttributeProperty;
          rdfs:label "Some existing attribute property"@en.

      <http://existing/measure/part-time> a qb:MeasureProperty;
          rdfs:label "Part-time"@en;
          rdfs:range xsd:decimal.

      <http://existing/measure/full-time> a qb:MeasureProperty;
          rdfs:label "Full-time"@en;
          rdfs:range xsd:decimal.

      <http://existing/measure/flex-time> a qb:MeasureProperty;
          rdfs:label "Flex-time"@en;
          rdfs:range xsd:decimal.

      <http://existing/unit/gbp> rdfs:label "Pounds Sterling"@en.
      <http://existing/unit/count> rdfs:label "Count"@en.
    """
    And the RDF should pass "skos, qb" SPARQL tests

  Scenario: A codelist defined in a CSV-W should be copied to the output directory
    Given the existing test-case file "qbwriter/code-list.csv-metadata.json"
    And the existing test-case file "qbwriter/code-list.table.json"
    And the existing test-case file "qbwriter/code-list.csv"
    And a QbCube named "Some Qube" with code-list defined in an existing CSV-W "qbwriter/code-list.csv-metadata.json"
    Then the CSVqb should pass all validations
    When the cube is serialised to CSV-W
    Then the file at "code-list.csv-metadata.json" should exist
    And the file at "code-list.table.json" should exist
    And the file at "code-list.csv" should exist
    And csvlint validation of all CSV-Ws should succeed
    And csv2rdf on all CSV-Ws should succeed
    And the RDF should pass "skos, qb" SPARQL tests

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

  Scenario: An cube with an option attribute which has missing data values should validate successfully
    Given a single-measure QbCube named "Some Qube" with optional attribute values missing
    Then the CSVqb should pass all validations
    When the cube is serialised to CSV-W
    Then csvlint validation of all CSV-Ws should succeed

  Scenario: Schema validation occurs when an info.json is imported but errors are only presented not the cause of a halt.
    Given the existing test-case file "configloaders/single-measure-info-json-test-files/single-measure-data.csv"
    And the existing test-case file "configloaders/info-json-test-files/single-measure-with-no-errors-info.json"
    When we load a cube using the info.json from "configloaders/info-json-test-files/single-measure-with-no-errors-info.json" with CSV from "configloaders/single-measure-info-json-test-files/single-measure-data.csv"
    Then there are no JSON schema validation errors

  Scenario: Schema validation occurs when an info.json is imported but errors are only presented not the cause of a halt.
    Given the existing test-case file "configloaders/single-measure-info-json-test-files/single-measure-data.csv"
    And the existing test-case file "configloaders/info-json-test-files/single-measure-with-errors-info.json"
    When we load a cube using the info.json from "configloaders/info-json-test-files/single-measure-with-errors-info.json" with CSV from "configloaders/single-measure-info-json-test-files/single-measure-data.csv"
    Then there is the following JSON schema validation error
    """
      125 is not of type 'string'
    """
