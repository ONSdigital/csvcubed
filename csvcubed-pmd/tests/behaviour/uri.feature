Feature: Testing the uri command group in the CLI

  Scenario: "the 'uri replace' command should get and read in a ttl file, but not be able to run without entering the uri's that need finding and replacing"
    Given the existing test-case file "TurtleTestFile.ttl"
    When the pmdutils command CLI is run with "uri replace TurtleTestFile.ttl TurtleOutputFile.ttl"
    Then the CLI should fail with status code 1

  Scenario: "the 'uri replace' command should fail when a single uri pair is entered in the command line, without the '--force' arg"
    Given the existing test-case file "TurtleTestFile.ttl"
    When the pmdutils command CLI is run with "uri replace TurtleTestFile.ttl TurtleOutputFile.ttl -v file:/tmp/qb-id-10002.csv http://example.com/some-dataset"
    Then the CLI should fail with status code 1
  
  Scenario: "the 'uri replace' command should find and replace URI's in the ttl file and continue to execute through warning messages"
    Given the existing test-case file "TurtleTestFile.ttl"
    When the pmdutils command CLI is run with "uri replace TurtleTestFile.ttl TurtleOutputFile.ttl -v file:/tmp/qb-id-10002.csv http://example.com/some-dataset --force"
    Then the CLI should succeed
    And the CLI should print "WARNING:root:remaining 'file:/' URIs found on line 62:"
    And the CLI should print "WARNING:root:remaining 'file:/' URIs found on line 147:"

  Scenario: "the 'uri replace' command should fail with multiple uri pairs entered in the command line, without the '--force' arg"
    Given the existing test-case file "TurtleTestFile.ttl"
    When the pmdutils command CLI is run with "uri replace TurtleTestFile.ttl TurtleOutputFile.ttl -v file:/tmp/qb-id-10002.csv http://example.com/some-dataset -v file:/tmp/d-code-list.csv http://example.com/some-dataset/d-code-list"
    Then the CLI should fail with status code 1

  Scenario: "the 'uri replace' command should succeed with multiple uris entered in the command line, with the '--force" arg"
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
