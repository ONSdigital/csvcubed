Feature: Cube!
  As a data engineer.
  I want to create a cube from a tidy data csv, with or without a config json file
  That conforms to the documented conventions for column headings.

  Scenario: Output a cube and errors when created from both config and data
    Given The config json file "v1.0/cube_data_config_ok.json" and the existing tidy data csv file "v1.0/cube_data_config_ok.csv"
    When The cube is created
    Then The cube Metadata should match
      """
      {
        "title": "Tests/test-cases/config/schema-cube-data-config-ok",
        "identifier": "schema-id",
        "summary": "a summary",
        "description": "Schema for testing",
        "creator_uri": "https://www.gov.uk/government/organisations/fred-the-creator",
        "publisher_uri": "https://www.gov.uk/government/organisations/joe-the-publisher",
        "landing_page_uris": [],
        "theme_uris": ["a-theme"],
        "keywords": ["two"],
        "dataset_issued": "2022-03-04 15:00:00.000",
        "dataset_modified": "2022-03-04 15:00:00.000",
        "license_uri": "the license",
        "public_contact_point_uri": "Rob Barry",
        "uri_safe_identifier_override": "schema-id"
      }
      """
    Then The cube Columns should match
    """
      [
        {"csv_column_title": "Dim-0", "structural_definition": {"label": "Non Dimension", "description": None, "code_list": {"metadata": {"title": "Non Dimension", "identifier": None, "summary": None, "description": None, "creator_uri": None, "publisher_uri": None, "landing_page_uris": [], "theme_uris": [], "keywords": [], "dataset_issued": None, "dataset_modified": None, "license_uri": None, "public_contact_point_uri": None, "uri_safe_identifier_override": None, }, "concepts": [{"label": "1", "code": "1", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}, {"label": "2", "code": "2", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}], "arbitrary_rdf": [], "uri_style": None}, "parent_dimension_uri": None, "source_uri": None, "range_uri": None, "uri_safe_identifier_override": None, "arbitrary_rdf": []}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
        {"csv_column_title": "Dim-1", "structural_definition": {"label": "Period Dimension", "description": None, "code_list": {"metadata": {"title": "Period Dimension", "identifier": None, "summary": None, "description": None, "creator_uri": None, "publisher_uri": None, "landing_page_uris": [], "theme_uris": [], "keywords": [], "dataset_issued": None, "dataset_modified": None, "license_uri": None, "public_contact_point_uri": None, "uri_safe_identifier_override": None, }, "concepts": [{"label": "2009", "code": "2009", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}, {"label": "2010", "code": "2010", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}], "arbitrary_rdf": [], "uri_style": None}, "parent_dimension_uri": None, "source_uri": None, "range_uri": None, "uri_safe_identifier_override": None, "arbitrary_rdf": []}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
        {"csv_column_title": "Dim-2", "structural_definition": {"label": "Trade Direction Dimension", "description": None, "code_list": {"metadata": {"title": "Trade Direction Dimension", "identifier": None, "summary": None, "description": None, "creator_uri": None, "publisher_uri": None, "landing_page_uris": [], "theme_uris": [], "keywords": [], "dataset_issued": None, "dataset_modified": None, "license_uri": None, "public_contact_point_uri": None, "uri_safe_identifier_override": None, }, "concepts": [{"label": "export", "code": "export", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}, {"label": "import", "code": "import", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}], "arbitrary_rdf": [], "uri_style": None}, "parent_dimension_uri": None, "source_uri": None, "range_uri": None, "uri_safe_identifier_override": None, "arbitrary_rdf": []}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
        {"csv_column_title": "Attr-1", "structural_definition": {"label": "My best attribute", "description": None, "new_attribute_values": [{"label": "goods", "description": None, "uri_safe_identifier_override": None, "source_uri": None, "parent_attribute_value_uri": None, "arbitrary_rdf": []}, {"label": "services", "description": None, "uri_safe_identifier_override": None, "source_uri": None, "parent_attribute_value_uri": None, "arbitrary_rdf": []}], "parent_attribute_uri": None, "source_uri": None, "is_required": False, "uri_safe_identifier_override": None, "arbitrary_rdf": []}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
        {"csv_column_title": "Amount", "structural_definition": {"data_type": "decimal", "unit": None}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
        {"csv_column_title": "Measure", "structural_definition": {"measures": [{"label": "Billions", "description": None, "parent_measure_uri": None, "source_uri": None, "uri_safe_identifier_override": None, "arbitrary_rdf": []}]}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
        {"csv_column_title": "Units", "structural_definition": {"units": [{"label": "Pounds", "description": None, "source_uri": None, "uri_safe_identifier_override": None, "arbitrary_rdf": [], "base_unit": None, "base_unit_scaling_factor": None, "qudt_quantity_kind_uri": None, "si_base_unit_conversion_multiplier": None}]}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
      ]
    """


  Scenario: Output a cube and errors when created data only
    Given The existing tidy data csv file "v1.0/cube_data_convention_ok.csv"
    When The cube is created
    Then The cube Metadata should match
      """
        {
          "title": "Cube Data Convention Ok",
          "identifier": None,
          "summary": "",
          "description": "",
          "creator_uri": None,
          "publisher_uri": None,
          "landing_page_uris": [],
          "theme_uris": [],
          "keywords": [],
          "dataset_issued": None,
          "dataset_modified": None,
          "license_uri": None,
          "public_contact_point_uri": None,
          "uri_safe_identifier_override": None,
        }
      """

    Then The cube Columns should match
      """
        [
          {"csv_column_title": "Period", "structural_definition": {"label": "Period", "description": None, "code_list": {"metadata": {"title": "Period", "identifier": None, "summary": None, "description": None, "creator_uri": None, "publisher_uri": None, "landing_page_uris": [], "theme_uris": [], "keywords": [], "dataset_issued": None, "dataset_modified": None, "license_uri": None, "public_contact_point_uri": None, "uri_safe_identifier_override": None}, "concepts": [{"label": "2010", "code": "2010", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}, {"label": "2011", "code": "2011", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}, {"label": "2012", "code": "2012", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}, {"label": "2013", "code": "2013", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}], "arbitrary_rdf": [], "uri_style": None}, "parent_dimension_uri": None, "source_uri": None, "range_uri": None, "uri_safe_identifier_override": None, "arbitrary_rdf": []}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
          {"csv_column_title": "Geography", "structural_definition": {"label": "Geography", "description": None, "code_list": {"metadata": {"title": "Geography", "identifier": None, "summary": None, "description": None, "creator_uri": None, "publisher_uri": None, "landing_page_uris": [], "theme_uris": [], "keywords": [], "dataset_issued": None, "dataset_modified": None, "license_uri": None, "public_contact_point_uri": None, "uri_safe_identifier_override": None}, "concepts": [{"label": "London", "code": "london", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}], "arbitrary_rdf": [], "uri_style": None}, "parent_dimension_uri": None, "source_uri": None, "range_uri": None, "uri_safe_identifier_override": None, "arbitrary_rdf": []}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
          {"csv_column_title": "Observation", "structural_definition": {"data_type": "decimal", "unit": None}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
          {"csv_column_title": "Measure", "structural_definition": {"measures": [{"label": "Cost of living index", "description": None, "parent_measure_uri": None, "source_uri": None, "uri_safe_identifier_override": None, "arbitrary_rdf": []}]}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
          {"csv_column_title": "Unit", "structural_definition": {"units": [{"label": "index", "description": None, "source_uri": None, "uri_safe_identifier_override": None, "arbitrary_rdf": [], "base_unit": None, "base_unit_scaling_factor": None, "qudt_quantity_kind_uri": None, "si_base_unit_conversion_multiplier": None}]}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
          {"csv_column_title": "Attribute", "structural_definition": {"label": "Attribute", "description": None, "code_list": {"metadata": {"title": "Attribute", "identifier": None, "summary": None, "description": None, "creator_uri": None, "publisher_uri": None, "landing_page_uris": [], "theme_uris": [], "keywords": [], "dataset_issued": None, "dataset_modified": None, "license_uri": None, "public_contact_point_uri": None, "uri_safe_identifier_override": None}, "concepts": [{"label": "Blue", "code": "blue", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}, {"label": "Green", "code": "green", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}, {"label": "Orange", "code": "orange", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}, {"label": "Red", "code": "red", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}], "arbitrary_rdf": [], "uri_style": None}, "parent_dimension_uri": None, "source_uri": None, "range_uri": None, "uri_safe_identifier_override": None, "arbitrary_rdf": []}, "csv_column_uri_template": None, "uri_safe_identifier_override": None}
        ]
      """

    Scenario: Output a cube combining config and convention
    Given The config json file "v1.0/cube_data_part_config.json" and the existing tidy data csv file "v1.0/cube_data_part_config.csv"
    When The cube is created
    Then The cube Metadata should match
      """
        {"title": "Tests/test-cases/config/schema-cube-data-config-ok",
        "identifier": "schema-id",
        "summary": "a summary",
        "description": "Schema for testing",
        "creator_uri": "https://www.gov.uk/government/organisations/fred-the-creator",
        "publisher_uri": "https://www.gov.uk/government/organisations/joe-the-publisher",
        "landing_page_uris": [],
        "theme_uris": ["a-theme"],
        "keywords": ["two"],
        "dataset_issued": "2022-03-04 17:00:00.000",
        "dataset_modified": "2022-03-04 18:00:00.000",
        "license_uri": "the license",
        "public_contact_point_uri": None,
        "uri_safe_identifier_override": "schema-id",
        }

      """

