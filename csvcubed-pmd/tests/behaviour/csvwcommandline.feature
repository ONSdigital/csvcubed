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
    Then the CLI should fail with status code 1


  Scenario: "the 'uri replace' command should get and read in a ttl file but not be able to run without more arguments being entered in the command line"
    Given the existing test-case file "TurtleTestFile.ttl"
    When the pmdutils command CLI is run with "uri replace TurtleTestFile.ttl TurtleOutputFile.ttl"
    Then the CLI should fail with status code 1

  Scenario: "the 'uri replace' command should get and read in a ttl file but not be able to replace single pair of uri"
    Given the existing test-case file "TurtleTestFile.ttl"
    When the pmdutils command CLI is run with "uri replace TurtleTestFile.ttl TurtleOutputFile.ttl -v file:/tmp/qb-id-10002.csv http://example.com/some-dataset"
    Then the CLI should fail with status code 1
  
  Scenario: "the 'uri replace' command should get and read in a ttl file and find and replace a single pair uri by being '--force' to continue through 'WARNING'"
    Given the existing test-case file "TurtleTestFile.ttl"
    When the pmdutils command CLI is run with "uri replace TurtleTestFile.ttl TurtleOutputFile.ttl -v file:/tmp/qb-id-10002.csv http://example.com/some-dataset --force"
    Then the CLI should succeed

  Scenario: "the 'uri replace' command should get and read in a ttl file but not be able to replace multiple pairs of uri"
    Given the existing test-case file "TurtleTestFile.ttl"
    When the pmdutils command CLI is run with "uri replace TurtleTestFile.ttl TurtleOutputFile.ttl -v file:/tmp/qb-id-10002.csv http://example.com/some-dataset -v file:/tmp/d-code-list.csv http://example.com/some-dataset/d-code-list"
    Then the CLI should fail with status code 1

  Scenario: "the 'uri replace' command should get and read in a ttl file and find and replace multiple pairs uri by being '--force' to continue through 'WARNING'"
    Given the existing test-case file "TurtleTestFile.ttl"
    When the pmdutils command CLI is run with "uri replace TurtleTestFile.ttl TurtleOutputFile.ttl -v file:/tmp/qb-id-10002.csv http://example.com/some-dataset -v file:/tmp/d-code-list.csv http://example.com/some-dataset/d-code-list --force"
    Then the CLI should succeed
  
  Scenario: "the 'uri replace' command should succeed with --force arg with the warnings where 'file:/' remains"
    Given the existing test-case file "TurtleTestFile.ttl"
    When the pmdutils command CLI is run with "uri replace TurtleTestFile.ttl TurtleOutputFile.ttl -v file:/tmp/qb-id-10002.csv http://example.com/some-dataset -v file:/tmp/d-code-list.csv http://example.com/some-dataset/d-code-list --force"
    Then the CLI should print "WARNING:root:remaining 'file:/' URIs found on line 62:"
    And the CLI should print "WARNING:root:remaining 'file:/' URIs found on line 147:"
    And the CLI should print "WARNING:root:remaining 'file:/' URIs found on line 169:"
    Then the CLI should succeed
  
  Scenario: "the 'uri replace' command should fail when a ttl file doesn't have all instances of 'file:/' removed"
    Given the existing test-case file "TurtleTestFile.ttl"
    When the pmdutils command CLI is run with "uri replace TurtleTestFile.ttl TurtleOutputFile.ttl -v file:/tmp/qb-id-10002.csv http://example.com/some-dataset"
    Then the CLI should fail with status code 1
    And the file at "TurtleOutputFile.ttl" should not exist
