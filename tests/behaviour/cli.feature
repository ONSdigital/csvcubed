Feature: Test the csvcubed Command Line Interface.
  Scenario: The csvcubed build command should output validation errors file
    Given the existing test-case file "configloaders/data_validation_error.csv"
    And the existing test-case file "configloaders/qube_validation_error.json"
    When the csvcubed CLI is run with "build configloaders/data_validation_error.csv --config configloaders/qube_validation_error.json --validation-errors-to-file"
    Then the validation-errors.json file should contain
      """
      Publisher 'https://im-not-a-real-publisher.com' is not recognised by csvcubed.
      """
    Then remove test log files

  Scenario: The csvcubed code-list-build command should output a code-list CSVW without the need to provide a CSV
    Given the existing test-case file "readers/code-list-config/v1.0/code_list_config_hierarchical.json"
    When the csvcubed CLI is run with "code-list-build"
    Then the file at "out/title-of-the-code-list.csv" should exist
    And the file at "out/title-of-the-code-list.csv-metadata.json" should exist
    And the file at "out/title-of-the-code-list.table.json" should exist
