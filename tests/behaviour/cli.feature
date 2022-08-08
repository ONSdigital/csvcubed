Feature: Test the csvcubed Command Line Interface.

  Scenario: The csvcubed build command should output validation errors file
    Given the existing test-case file "configloaders/data_validation_error.csv"
    And the existing test-case file "configloaders/qube_validation_error.json"
    When the csvcubed CLI is run with "build configloaders/data_validation_error.csv --config configloaders/qube_validation_error.json --validation-errors-to-file"
    Then the csvcubed CLI should succeed
    Then the validation-errors.json file in the "out/" directory should contain
    """csvcubed.cli.build - WARNING - Schema Validation Error: 'https://example.com' is not one of """
    Then remove test log files