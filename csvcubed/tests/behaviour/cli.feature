Feature: Test the csvcubed Command Line Interface.

  Scenario: The csvcubed build command should output a log file
    Given the existing test-case file "configloaders/data.csv"
    And the existing test-case file "configloaders/info.json"
    When the csvcubed CLI is run with "build --logdir=log_test_dir --logginglvl=warn --config configloaders/info.json configloaders/data.csv"
    And the location of "log_test_dir" is determined by Appdirs
    Then the csvcubed CLI should fail with status code 1
    And the log file should exist
    And the log file should contain
    """
     - csvcubed - CRITICAL - A log file containing the recordings of this cli, is at:
    """
    And remove test log files