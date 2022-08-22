Feature: Test the csvcubed Command Line Interface.

  Scenario: The csvcubed build command should output validation errors file
    Given the existing test-case file "configloaders/data_validation_error.csv"
    And the existing test-case file "configloaders/qube_validation_error.json"
    When the csvcubed CLI is run with "build configloaders/data_validation_error.csv --config configloaders/qube_validation_error.json --validation-errors-to-file"
    Then the validation-errors.json file should contain
      """
      'https://im-not-a-real-publisher.com' is not one of
      """
    Then remove test log files