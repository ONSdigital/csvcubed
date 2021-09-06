Feature: Test the csvqb Command Line Interface.

  Scenario: The csvqb build command should take an info.json and CSV and output CSV-Ws into the default './out' directory.
    Given the existing test-case file "configloaders/data.csv"
    And the existing test-case file "configloaders/info.json"
    When the csvqb CLI is run with "build --config configloaders/info.json configloaders/data.csv"
    Then the csvqb CLI should succeed
    And the csvqb CLI should print "Creating output directory"
    And the file at "out/ons-international-trade-in-services-by-subnational-areas-of-the-uk.csv" should exist
    And the file at "out/ons-international-trade-in-services-by-subnational-areas-of-the-uk.csv-metadata.json" should exist
    And the file at "out/validation-errors.json" should not exist

  Scenario: The csvqb build command should not output CSV-Ws when validation errors occur
    Given the existing test-case file "configloaders/validation-error/data.csv"
    And the existing test-case file "configloaders/validation-error/info.json"
    When the csvqb CLI is run with "build --config configloaders/validation-error/info.json configloaders/validation-error/data.csv"
    Then the csvqb CLI should fail with status code 1
    And the csvqb CLI should print "Validation Error"
    And the csvqb CLI should print "Found neither QbObservationValue.unit nor QbMultiUnits defined. One of these must be defined."
    And the file at "out/validation-error-output.csv" should not exist
    And the file at "out/validation-error-output.csv-metadata.json" should not exist
    And the file at "out/validation-errors.json" should not exist

  Scenario: The csvqb build command should output validation errors to file
    Given the existing test-case file "configloaders/validation-error/data.csv"
    And the existing test-case file "configloaders/validation-error/info.json"
    When the csvqb CLI is run with "build --validation-errors-to-file --config configloaders/validation-error/info.json configloaders/validation-error/data.csv"
    Then the csvqb CLI should fail with status code 1
    And the file at "out/validation-errors.json" should exist
    And the validation-errors.json file in the "out" directory should contain
    """
      Found neither QbObservationValue.unit nor QbMultiUnits defined. One of these must be defined.
    """

  Scenario: The csvqb build command should still output CSV-Ws if the user overrides validation errors
    Given the existing test-case file "configloaders/validation-error/data.csv"
    And the existing test-case file "configloaders/validation-error/info.json"
    When the csvqb CLI is run with "build --ignore-validation-errors --config configloaders/validation-error/info.json  configloaders/validation-error/data.csv"
    Then the csvqb CLI should succeed
    And the file at "out/validation-error-output.csv" should exist
    And the file at "out/validation-error-output.csv-metadata.json" should exist
