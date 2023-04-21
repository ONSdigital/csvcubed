Feature: Testing the CSV-W pull command in the CLI

  Scenario: The `pull` command should download the CSV-W and all dependant files.
    When the csvcubed CLI is run with "pull https://w3c.github.io/csvw/tests/test015/csv-metadata.json"
    Then the csvcubed CLI should succeed
    And the file at "csv-metadata.json" should exist
    And the file at "tree-ops.csv" should exist

  Scenario: The `pull` command should allow the output directory to be overridden.
    # This also implicitly tests that a single-table-definition (i.e. no tables property) CSV-W definition works.
    When the csvcubed CLI is run with "pull --out output https://w3c.github.io/csvw/tests/test015/csv-metadata.json"
    Then the csvcubed CLI should succeed
    And the file at "output/csv-metadata.json" should exist
    And the file at "output/tree-ops.csv" should exist

  Scenario: The `pull` command should automatically create the appropriate directory structure.
    When the csvcubed CLI is run with "pull https://w3c.github.io/csvw/tests/test034/csv-metadata.json"
    Then the csvcubed CLI should succeed
    And the file at "csv-metadata.json" should exist
    And the file at "gov.uk/data/professions.csv" should exist
    And the file at "gov.uk/schema/professions.json" should exist
    And the file at "gov.uk/data/organizations.csv" should exist
    And the file at "gov.uk/schema/organizations.json" should exist
    And the file at "senior-roles.csv" should exist
    And the file at "gov.uk/schema/senior-roles.json" should exist
    And the file at "junior-roles.csv" should exist
    And the file at "gov.uk/schema/junior-roles.json" should exist

  Scenario: The `pull` command should fail when the CSV-W file cannot be found.
    When the csvcubed CLI is run with "pull https://example.com/non-existant-file.csv-metadata.json"
    Then the csvcubed CLI should fail with status code 1

  Scenario: The pull command should support pulling CSV-Ws from filesystem paths.
    Given the existing test-case files "pull/dependencies/*"
    When the csvcubed CLI is run with "pull sweden-at-eurovision-complete-dataset.csv-metadata.json --out copy"
    Then the csvcubed CLI should succeed
    And the file at "copy/sweden-at-eurovision-complete-dataset.csv-metadata.json" should exist
    And the file at "copy/sweden-at-eurovision-complete-dataset.csv" should exist
    And the file at "copy/entrant.csv-metadata.json" should exist
    And the file at "copy/entrant.csv" should exist
    And the file at "copy/entrant.table.json" should exist
    And the file at "copy/language.csv-metadata.json" should exist
    And the file at "copy/language.csv" should exist
    And the file at "copy/language.table.json" should exist
    And the file at "copy/song.csv-metadata.json" should exist
    And the file at "copy/song.csv" should exist
    And the file at "copy/song.table.json" should exist
    And the file at "copy/year.csv-metadata.json" should exist
    And the file at "copy/year.csv" should exist
    And the file at "copy/year.table.json" should exist

  Scenario: The pull command should support pulling period.csv-metadata.json from filesystem paths.
    Given the existing test-case files "pull/csvw/*"
    When the csvcubed CLI is run with "pull period.csv-metadata.json --out copy"
    Then the csvcubed CLI should succeed
    And the file at "copy/period.csv-metadata.json" should exist
    And the file at "copy/period.csv" should exist
    And the file at "copy/period.table.json" should exist
