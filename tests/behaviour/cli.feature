Feature: Test the csvcubed Command Line Interface.
  Scenario: The csvcubed build command should output validation errors file
    Given the existing test-case file "configloaders/data_validation_error.csv"
    And the existing test-case file "configloaders/qube_validation_error.json"
    When the csvcubed CLI is run with "build configloaders/data_validation_error.csv --config configloaders/qube_validation_error.json --validation-errors-to-file"
    Then the csvcubed CLI should fail with status code 1
    And the validation-errors.json file should contain
      """
      Publisher 'https://im-not-a-real-publisher.com' is not recognised by csvcubed.
      """
    Then remove test log files

  Scenario: The csvcubed code-list build command should output a code-list CSVW without the need to provide a CSV
    Given the existing test-case file "readers/code-list-config/v1.0/code_list_config_hierarchical.json"
    When the csvcubed CLI is run with "code-list build readers/code-list-config/v1.0/code_list_config_hierarchical.json --validation-errors-to-file"
    Then the file at "out/title-of-the-code-list.csv" should exist
    And the file at "out/title-of-the-code-list.csv-metadata.json" should exist
    And the file at "out/title-of-the-code-list.table.json" should exist
    And the file at "out/validation-errors.json" should exist
    And the csvcubed CLI should succeed
    And the validation-errors.json file should contain
    """
    "offending_value": "http://purl.org/dc/aboutdcmi#DCMI"
    """
    Then remove test log files

  Scenario: The csvcubed code-list build command should display the logging in accordance with the log level set at debug.
    Given the existing test-case file "readers/code-list-config/v1.0/code_list_config_produces_error.json"
    When the csvcubed CLI is run with "code-list build readers/code-list-config/v1.0/code_list_config_produces_error.json --log-level debug"
    Then the csvcubed CLI should fail with status code 1
    And the command line output should display the log message
    """
    DEBUG - Loading JSON from URL
    """
    Then remove test log files

  Scenario: The csvcubed code-list build command should display the logging in accordance with the log level set at critical.
    Given the existing test-case file "readers/code-list-config/v1.0/code_list_config_produces_critical_error.json"
    When the csvcubed CLI is run with "code-list build readers/code-list-config/v1.0/code_list_config_produces_critical_error.json --log-level crit"
    Then the csvcubed CLI should fail with status code 1
    And the command line output should display the log message
    """
    CRITICAL - Traceback (most recent call last):
    """
    Then remove test log files

  Scenario: The csvcubed code-list build command should not display any critical logging despite log-level being set at "crit".
    Given the existing test-case file "readers/code-list-config/v1.0/code_list_config_hierarchical.json"
    When the csvcubed CLI is run with "code-list build readers/code-list-config/v1.0/code_list_config_hierarchical.json --log-level crit"
    Then the command line output should not display the log message
    """
    CRITICAL - Traceback (most recent call last):
    """
    Then remove test log files

  Scenario: The csvcubed code-list build command will continue when there is a validation error and build a code list csvw in a given out directory.
    Given the existing test-case file "readers/code-list-config/v1.0/code_list_config_produces_error.json"
    When the csvcubed CLI is run with "code-list build readers/code-list-config/v1.0/code_list_config_produces_error.json --ignore-validation-errors --out testout"
    Then the command line output should display the log message
    """
    Attempting to build CSV-W even though there are 1 validation errors.
    """
    Then the file at "testout/title-of-the-code-list.csv" should exist
    And the file at "testout/title-of-the-code-list.csv-metadata.json" should exist
    And the file at "testout/title-of-the-code-list.table.json" should exist
    And the csvcubed CLI should succeed
    Then remove test log files

  Scenario: The csvcubed code-list build command will fail when there is a validation error.
    Given the existing test-case file "readers/code-list-config/v1.0/code_list_config_produces_error.json"
    When the csvcubed CLI is run with "code-list build readers/code-list-config/v1.0/code_list_config_produces_error.json --fail-when-validation-error"
    Then the csvcubed CLI should fail with status code 1
    Then remove test log files
