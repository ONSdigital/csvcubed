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

  Scenario: The csvcubed code-list build command should output a code-list CSVW without the need to provide a CSV
    Given the existing test-case file "readers/code-list-config/v1.0/code_list_config_hierarchical.json"
    When the csvcubed CLI is run with "code-list build readers/code-list-config/v1.0/code_list_config_hierarchical.json --validation-errors-to-file"
    Then the file at "out/title-of-the-code-list.csv" should exist
    And the file at "out/title-of-the-code-list.csv-metadata.json" should exist
    And the file at "out/title-of-the-code-list.table.json" should exist
    And the file at "out/validation-errors.json" should exist
    And the validation-errors.json file should contain
    """
    "offending_value": "http://purl.org/dc/aboutdcmi#DCMI"
    """
    Then remove test log files

  Scenario: The csvcubed code-list build command should display the logging in accordance with the log level set at debug.
    Given the existing test-case file "readers/code-list-config/v1.0/code_list_config_produces_error.json"
    When the csvcubed CLI is run with "code-list build readers/code-list-config/v1.0/code_list_config_produces_error.json --log-level debug"
    Then the command line output should display the log message
    """
    csvcubed.utils.cli - WARNING - Schema Validation Error: $.creator - 'http://purl.org/dc/aboutdcmi#DCMI' is not one of ['http://dbpedia.org/resource/Open_Knowledge_Foundation', 'http://statistics.data.gov.uk', 'https:/
    """
    And the command line output should display the log message
    """
    csvcubed.utils.cli - ERROR - Validation Error: An error was encountered when validating the cube. The error occurred in '["('concepts', 3)", 'existing_concept_uri']' and was reported as ''This will produce an error' does not look like a URI.'
    """
    And the command line output should display the log message
    """
    csvcubed.readers.codelistconfig.codelist_schema_versions - INFO - Using schema version 1.0
    """
    And the command line output should display the log message
    """
    csvcubed.utils.json - DEBUG - Loading JSON from URL https://purl.org/csv-cubed/code-list-config/v1.0
    """

  Scenario: The csvcubed code-list build command should display the logging in accordance with the log level set at critical.
    Given the existing test-case file "readers/code-list-config/v1.0/code_list_config_produces_critical_error.json"
    When the csvcubed CLI is run with "code-list build readers/code-list-config/v1.0/code_list_config_produces_critical_error.json --log-level debug"
    Then the command line output should display the log message
    """
    csvcubed.cli.entrypoint - CRITICAL - Traceback (most recent call last):
    """

  Scenario: The csvcubed code-list build command will continue when there is a validation error and build a code list csvw in a given out directory.
    Given the existing test-case file "readers/code-list-config/v1.0/code_list_config_produces_error.json"
    When the csvcubed CLI is run with "code-list build readers/code-list-config/v1.0/code_list_config_produces_error.json --ignore-validation-errors --out 'test-out'"
    Then the file at "test-out/title-of-the-code-list.csv" should exist
    And the file at "test-out/title-of-the-code-list.csv-metadata.json" should exist
    And the file at "test-out/title-of-the-code-list.table.json" should exist
    And the command line output should display the log message
    """
    Build Complete @
    """

  Scenario: The csvcubed code-list build command will fail when there is a validation error.
    Given the existing test-case file "readers/code-list-config/v1.0/code_list_config_produces_error.json"
    When the csvcubed CLI is run with "code-list build readers/code-list-config/v1.0/code_list_config_produces_error.json --fail-when-validation-error"
    Then the command line output should not display the log message
    """
    Build Complete @
    """
