Feature: Test the creation of the code-list CSVW with only a code-list-config.json file.
    Scenario: Successfully output a code-list CSVW using schema v1.0
        Given the existing test-case file "readers/code-list-config/v1.0/code_list_config_hierarchical.json"
        Then a valid code-list is created and serialised to CSVW from the config file "readers/code-list-config/v1.0/code_list_config_hierarchical.json"

    Scenario: Successfully output a code-list CSVW using schema v1.1
        Given the existing test-case file "readers/code-list-config/v1.1/code_list_config_hierarchical_v1_1.json"
        Then a valid code-list is created and serialised to CSVW from the config file "readers/code-list-config/v1.1/code_list_config_hierarchical_v1_1.json"

    Scenario: Successfully output a code-list CSVW using schema v2.0
        Given the existing test-case file "readers/code-list-config/v2.0/code_list_config_hierarchical_v2_0.json"
        Then a valid code-list is created and serialised to CSVW from the config file "readers/code-list-config/v2.0/code_list_config_hierarchical_v2_0.json"
