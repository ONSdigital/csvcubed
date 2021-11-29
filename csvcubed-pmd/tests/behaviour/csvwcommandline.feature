Feature: Testing the csvw command group in the CLI

  Scenario: The `pull` command should download the CSV-W and all dependant files.
    When the pmdutils command CLI is run with "csvw pull https://w3c.github.io/csvw/tests/test015/csv-metadata.json"
    Then the CLI should succeed
    And the file at "out/csv-metadata.json" should contain
    """
       {
         "@context": "http://www.w3.org/ns/csvw",
         "url": "tree-ops.csv",
         "dc:label": "metadata",
         "tableSchema": {
           "columns": [{
             "name": "GID",
             "titles": ["Generic Identifier", "GID"]
           }, {
             "name": "on_street",
             "titles": "On Street"
           }, {
             "name": "species",
             "titles": "Species"
           }, {
             "name": "trim_cycle",
             "titles": "Trim Cycle"
           }, {
             "name": "inventory_date",
             "titles": "Inventory Date",
             "datatype": {"base": "date", "format": "M/d/yyyy"}
           }],
           "primaryKey": "GID"
         }
       }
    """
    And the file at "out/tree-ops.csv" should contain
    """
      GID,On Street,Species,Trim Cycle,Inventory Date
      1,ADDISON AV,Celtis australis,Large Tree Routine Prune,10/18/2010
      2,EMERSON ST,Liquidambar styraciflua,Large Tree Routine Prune,6/2/2010
    """

    Scenario: The `pull` command should allow the output directory to be overridden.
    When the pmdutils command CLI is run with "csvw pull --out output https://w3c.github.io/csvw/tests/test015/csv-metadata.json"
    Then the CLI should succeed
    And the file at "output/csv-metadata.json" should exist
    And the file at "output/tree-ops.csv" should exist

    Scenario: The `pull` command should automatically create the appropriate directory structure.
    When the pmdutils command CLI is run with "csvw pull https://w3c.github.io/csvw/tests/test034/csv-metadata.json"
    Then the CLI should succeed
    And the file at "out/csv-metadata.json" should exist
    And the file at "out/gov.uk/data/professions.csv" should exist
    And the file at "out/gov.uk/schema/professions.json" should exist
    And the file at "out/gov.uk/data/organizations.csv" should exist
    And the file at "out/gov.uk/schema/organizations.json" should exist
    And the file at "out/senior-roles.csv" should exist
    And the file at "out/gov.uk/schema/senior-roles.json" should exist
    And the file at "out/junior-roles.csv" should exist
    And the file at "out/gov.uk/schema/junior-roles.json" should exist

    Scenario: The `pull` command should fail when the CSV-W file cannot be found.
    When the pmdutils command CLI is run with "csvw pull https://example.com/non-existant-file.csv-metadata.json"
    Then the CLI should fail with status code -1

    Scenario: The `find-where` command should find return CSV-Ws matching an ASK query.
    Given the existing test-case files "dcatcli/*"
    When the pmdutils command CLI is run with "csvw find-where 'ASK WHERE { ?s a <http://www.w3.org/2004/02/skos/core#ConceptScheme>. }'"
    Then the CLI should succeed
    And the CLI should print "period.csv-metadata.json"

    Scenario: The `find-where` command should return CSV-Ws which do *not* match an ASK query when the negate option is set
    Given the existing test-case files "dcatcli/*"
    When the pmdutils command CLI is run with "csvw find-where --negate 'ASK WHERE { ?s a <http://www.w3.org/2004/02/skos/core#ConceptScheme>. }'"
    Then the CLI should succeed
    And the CLI should print "single-measure-bulletin.csv-metadata.json"
