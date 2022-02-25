Feature: Test the csvcubed Command Line Interface.

  Scenario: The csvcubed build command should output a log file
    Given the existing test-case file "configloaders/data.csv"
    And the existing test-case file "configloaders/info.json"
    When the csvcubed CLI is run with "build --log-level debug --config configloaders/info.json configloaders/data.csv"
    Then the csvcubed CLI should fail with status code 1
    And the log file should exist
    Then remove test log files