Feature: Stress test csvcubed.

    Scenario: How many rows can the csvcubed build commands process?
        Given the existing test-case file "stress/sweden_at_eurovision_no_missing.csv"
        When the csvcubed CLI is run with "csvcubed build sweden_at_eurovision_no_missing.csv"
        Then the validation-errors.json file should contain
            """
            'https://im-not-a-real-publisher.com' is not one of
            """
        Then remove test log files