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

  Scenario: A QbCube should validate successfully where foreign key constraints are met.
    Given a single-measure QbCube named "Some Qube"
    When the cube is serialised to CSV-W
    Then the file at "a-code-list.csv-metadata.json" should exist
    And csvlint validation of "some-qube.csv-metadata.json" should succeed
    And csv2rdf on "some-qube.csv-metadata.json" should succeed
    And the RDF should not contain any instances of "http://www.w3.org/2004/02/skos/core#ConceptScheme"

  Scenario: A QbCube should fail to validate where foreign key constraints are not met.
    Given a single-measure QbCube named "Some Qube" with codes not defined in the code-list
    When the cube is serialised to CSV-W
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
    And turtle should be written to "output.ttl"
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
    And turtle should be written to "output.ttl"
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
    And turtle should be written to "output.ttl"
    And the RDF should contain
      """
      <file:/tmp/qube-with-date-literals.csv#obs/uss-cerritos> <http://some-uri> "2020-08-06"^^<http://www.w3.org/2001/XMLSchema#date>.
      """
    And the RDF should contain
      """
      <file:/tmp/qube-with-date-literals.csv#obs/uss-titan> <http://some-uri> "2020-10-08"^^<http://www.w3.org/2001/XMLSchema#date>.
      """
