Feature: some nonsense test
  Scenario: some nonsense
    Given some configuration
    Then the RDF should contain
    """
    <http://purl.org/dc/terms/modified> <http://www.w3.org/2000/01/rdf-schema#isDefinedBy> <http://purl.org/dc/terms/>.
    """