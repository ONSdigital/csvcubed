Feature: Test the infojson2csvqb Command Line Interface.

  Scenario: The infojson2csvqb build command should take an info.json and CSV and output CSV-Ws into the default './out' directory.
    Given the existing test-case file "configloaders/data.csv"
    And the existing test-case file "configloaders/info.json"
    When the infojson2csvqb CLI is run with "build --config configloaders/info.json configloaders/data.csv"
    Then the infojson2csvqb CLI should succeed
    And the infojson2csvqb CLI should print "Creating output directory"
    And the file at "out/ons-international-trade-in-services-by-subnational-areas-of-the-uk.csv" should exist
    And the file at "out/ons-international-trade-in-services-by-subnational-areas-of-the-uk.csv-metadata.json" should exist
    And the file at "out/validation-errors.json" should not exist

  Scenario: The infojson2csvqb build command should not output CSV-Ws when validation errors occur
    Given the existing test-case file "configloaders/validation-error/data.csv"
    And the existing test-case file "configloaders/validation-error/info.json"
    When the infojson2csvqb CLI is run with "build --config configloaders/validation-error/info.json configloaders/validation-error/data.csv"
    Then the infojson2csvqb CLI should fail with status code 1
    And the infojson2csvqb CLI should print "Validation Error"
    And the infojson2csvqb CLI should print "Found neither QbObservationValue.unit nor QbMultiUnits defined. One of these must be defined."
    And the file at "out/validation-error-output.csv" should not exist
    And the file at "out/validation-error-output.csv-metadata.json" should not exist
    And the file at "out/validation-errors.json" should not exist

  Scenario: The infojson2csvqb build command should output validation errors to file
    Given the existing test-case file "configloaders/validation-error/data.csv"
    And the existing test-case file "configloaders/validation-error/info.json"
    When the infojson2csvqb CLI is run with "build --validation-errors-to-file --config configloaders/validation-error/info.json configloaders/validation-error/data.csv"
    Then the infojson2csvqb CLI should fail with status code 1
    And the file at "out/validation-errors.json" should exist
    And the validation-errors.json file in the "out" directory should contain
    """
      Found neither QbObservationValue.unit nor QbMultiUnits defined. One of these must be defined.
    """

  Scenario: The infojson2csvqb build command should still output CSV-Ws if the user overrides validation errors
    Given the existing test-case file "configloaders/validation-error/data.csv"
    And the existing test-case file "configloaders/validation-error/info.json"
    When the infojson2csvqb CLI is run with "build --ignore-validation-errors --config configloaders/validation-error/info.json  configloaders/validation-error/data.csv"
    Then the infojson2csvqb CLI should succeed
    And the file at "out/validation-error-output.csv" should exist
    And the file at "out/validation-error-output.csv-metadata.json" should exist

  Scenario: The infojson2csvqb build command should accept an optional catalog-metadata.json which overrides the info.json configuration
    Given the existing test-case file "configloaders/data.csv"
    And the existing test-case file "configloaders/info.json"
    And the existing test-case file "configloaders/catalog-metadata.json"
    When the infojson2csvqb CLI is run with "build --config configloaders/info.json --catalog-metadata configloaders/catalog-metadata.json configloaders/data.csv"
    Then the infojson2csvqb CLI should succeed
    And the file at "out/some-dataset.csv" should exist
    And the file at "out/some-dataset.csv-metadata.json" should exist
    But the file at "out/ons-international-trade-in-services-by-subnational-areas-of-the-uk.csv" should not exist

  Scenario: The infojson2csvqb build command should succeed when 'families' within info.json contains 'Climate Change'
    Given the existing test-case file "configloaders/ClimateChangeFamilyError/info.json"
    And the existing test-case file "configloaders/ClimateChangeFamilyError/data.csv"
    When the infojson2csvqb CLI is run with "build -c configloaders/ClimateChangeFamilyError/info.json configloaders/ClimateChangeFamilyError/data.csv"
    Then the infojson2csvqb CLI should succeed
    And the infojson2csvqb CLI should not print "http://gss-data.org.uk/def/gdp#Climate Change does not look like a valid URI, trying to serialize this will break."