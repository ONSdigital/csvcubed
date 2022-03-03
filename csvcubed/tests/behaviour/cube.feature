Feature:
  As a data engineer.
  I want to create a cube from a tidy data csv, with or without a config json file
  That conforms to the documented conventions for column headings.

  Scenario: Output a cube and errors when created from both config and data
    Given The config json file "cube_data_config_ok.json" and the existing tidy data csv file "cube_data_config_ok.csv"
    When The cube is created
#    Then The cube Metadata should match "{"title": "test"}"
    Then The cube Metadata should match:
      """
      {
        "title": "Tests/test-cases/config/schema-cube-data-config-ok",
        "identifier": "http://schema-id",
        "summary": None,
        "description": "Schema for testing",
        "creator_uri": "https://www.gov.uk/government/organisations/http-//fred-the-creator",
        "publisher_uri": "https://www.gov.uk/government/organisations/http-//joe-the-publisher",
        "landing_page_uris": [],
        "theme_uris": ["a-theme"],
        "keywords": ["two"],
        "dataset_issued": None,
        "dataset_modified": None,
        "license_uri": None,
        "public_contact_point_uri": None,
        "uri_safe_identifier_override": "http://schema-id",
        "spatial_bound_uri": "spatial",
        "temporal_bound_uri": "temporal"
      }
      """
    Then The cube Columns should match
    """
      [
        {"csv_column_title": "Dim-0", "structural_definition": {"label": "Non Dimension", "description": None, "code_list": {"metadata": {"title": "Non Dimension", "identifier": None, "summary": None, "description": None, "creator_uri": None, "publisher_uri": None, "landing_page_uris": [], "theme_uris": [], "keywords": [], "dataset_issued": None, "dataset_modified": None, "license_uri": None, "public_contact_point_uri": None, "uri_safe_identifier_override": None, "spatial_bound_uri": None, "temporal_bound_uri": None}, "concepts": [{"label": "1", "code": "1", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}, {"label": "2", "code": "2", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}], "arbitrary_rdf": []}, "parent_dimension_uri": None, "source_uri": None, "range_uri": None, "uri_safe_identifier_override": None, "arbitrary_rdf": []}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
        {"csv_column_title": "Dim-1", "structural_definition": {"label": "Period Dimension", "description": None, "code_list": {"metadata": {"title": "Period Dimension", "identifier": None, "summary": None, "description": None, "creator_uri": None, "publisher_uri": None, "landing_page_uris": [], "theme_uris": [], "keywords": [], "dataset_issued": None, "dataset_modified": None, "license_uri": None, "public_contact_point_uri": None, "uri_safe_identifier_override": None, "spatial_bound_uri": None, "temporal_bound_uri": None}, "concepts": [{"label": "2009", "code": "2009", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}, {"label": "2010", "code": "2010", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}], "arbitrary_rdf": []}, "parent_dimension_uri": None, "source_uri": None, "range_uri": None, "uri_safe_identifier_override": None, "arbitrary_rdf": []}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
        {"csv_column_title": "Dim-2", "structural_definition": {"label": "Trade Direction Dimension", "description": None, "code_list": {"metadata": {"title": "Trade Direction Dimension", "identifier": None, "summary": None, "description": None, "creator_uri": None, "publisher_uri": None, "landing_page_uris": [], "theme_uris": [], "keywords": [], "dataset_issued": None, "dataset_modified": None, "license_uri": None, "public_contact_point_uri": None, "uri_safe_identifier_override": None, "spatial_bound_uri": None, "temporal_bound_uri": None}, "concepts": [{"label": "export", "code": "export", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}, {"label": "import", "code": "import", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}], "arbitrary_rdf": []}, "parent_dimension_uri": None, "source_uri": None, "range_uri": None, "uri_safe_identifier_override": None, "arbitrary_rdf": []}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
        {"csv_column_title": "Attr-1", "structural_definition": {"label": "My best attribute", "description": None, "new_attribute_values": [{"label": "goods", "description": None, "uri_safe_identifier_override": None, "source_uri": None, "parent_attribute_value_uri": None, "arbitrary_rdf": []}, {"label": "services", "description": None, "uri_safe_identifier_override": None, "source_uri": None, "parent_attribute_value_uri": None, "arbitrary_rdf": []}], "parent_attribute_uri": None, "source_uri": None, "is_required": False, "uri_safe_identifier_override": None, "arbitrary_rdf": []}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
        {"csv_column_title": "Amount", "structural_definition": {"data_type": "decimal", "unit": None}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
        {"csv_column_title": "Measure", "structural_definition": {"measures": [{"label": "Billions", "description": None, "parent_measure_uri": None, "source_uri": None, "uri_safe_identifier_override": None, "arbitrary_rdf": []}]}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
        {"csv_column_title": "Units", "structural_definition": {"units": [{"label": "Pounds", "description": None, "source_uri": None, "uri_safe_identifier_override": None, "arbitrary_rdf": [], "base_unit": None, "base_unit_scaling_factor": None, "qudt_quantity_kind_uri": None, "si_base_unit_conversion_multiplier": None}]}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
      ]
    """
#

  Scenario: Output a cube and errors when created data only
    Given The existing tidy data csv file "cube_data_convention_ok.csv"
    When The cube is created
#    Then The cube Metadata should match "{"title": "test"}"
    Then The cube Metadata should match
      """
        {
          "title": "CUBE DATA CONVENTION OK.CSV",
          "identifier": None,
          "summary": None,
          "description": "",
          "creator_uri": None,
          "publisher_uri": None,
          "landing_page_uris": [],
          "theme_uris": None,
          "keywords": None,
          "dataset_issued": None,
          "dataset_modified": None,
          "license_uri": None,
          "public_contact_point_uri": None,
          "uri_safe_identifier_override": None,
          "spatial_bound_uri": None,
          "temporal_bound_uri": None
        }
      """
    Then The cube Columns should match:
    """
      [
        {"csv_column_title": "Period", "structural_definition": {"label": "Period", "description": None, "code_list": {"metadata": {"title": "Period", "identifier": None, "summary": None, "description": None, "creator_uri": None, "publisher_uri": None, "landing_page_uris": [], "theme_uris": [], "keywords": [], "dataset_issued": None, "dataset_modified": None, "license_uri": None, "public_contact_point_uri": None, "uri_safe_identifier_override": None, "spatial_bound_uri": None, "temporal_bound_uri": None}, "concepts": [{"label": "2010", "code": "2010", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}, {"label": "2011", "code": "2011", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}, {"label": "2012", "code": "2012", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}, {"label": "2013", "code": "2013", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}], "arbitrary_rdf": []}, "parent_dimension_uri": None, "source_uri": None, "range_uri": None, "uri_safe_identifier_override": None, "arbitrary_rdf": []}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
        {"csv_column_title": "Geography", "structural_definition": {"label": "Geography", "description": None, "code_list": {"metadata": {"title": "Geography", "identifier": None, "summary": None, "description": None, "creator_uri": None, "publisher_uri": None, "landing_page_uris": [], "theme_uris": [], "keywords": [], "dataset_issued": None, "dataset_modified": None, "license_uri": None, "public_contact_point_uri": None, "uri_safe_identifier_override": None, "spatial_bound_uri": None, "temporal_bound_uri": None}, "concepts": [{"label": "London", "code": "london", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}], "arbitrary_rdf": []}, "parent_dimension_uri": None, "source_uri": None, "range_uri": None, "uri_safe_identifier_override": None, "arbitrary_rdf": []}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
        {"csv_column_title": "Observation", "structural_definition": {"data_type": "decimal", "unit": None}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
        {"csv_column_title": "Measure", "structural_definition": {"measures": [{"label": "Cost of living index", "description": None, "parent_measure_uri": None, "source_uri": None, "uri_safe_identifier_override": None, "arbitrary_rdf": []}]}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
        {"csv_column_title": "Unit", "structural_definition": {"units": [{"label": "index", "description": None, "source_uri": None, "uri_safe_identifier_override": None, "arbitrary_rdf": [], "base_unit": None, "base_unit_scaling_factor": None, "qudt_quantity_kind_uri": None, "si_base_unit_conversion_multiplier": None}]}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
        {"csv_column_title": "Attribute", "structural_definition": {"label": "Attribute", "description": None, "code_list": {"metadata": {"title": "Attribute", "identifier": None, "summary": None, "description": None, "creator_uri": None, "publisher_uri": None, "landing_page_uris": [], "theme_uris": [], "keywords": [], "dataset_issued": None, "dataset_modified": None, "license_uri": None, "public_contact_point_uri": None, "uri_safe_identifier_override": None, "spatial_bound_uri": None, "temporal_bound_uri": None}, "concepts": [{"label": "Blue", "code": "blue", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}, {"label": "Green", "code": "green", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}, {"label": "Orange", "code": "orange", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}, {"label": "Red", "code": "red", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}], "arbitrary_rdf": []}, "parent_dimension_uri": None, "source_uri": None, "range_uri": None, "uri_safe_identifier_override": None, "arbitrary_rdf": []}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
      ]
    """

    Scenario: Output a cube combining config and convention
    Given The config json file "cube_data_part_config.json" and the existing tidy data csv file "cube_data_part_config.csv"
    When The cube is created
#    Then The cube Metadata should match "{"title": "test"}"
    Then The cube Metadata should match
      """
        {"title": "Tests/test-cases/config/schema-cube-data-config-ok",
        "identifier": "http://schema-id",
        "summary": "a summary",
        "description": "Schema for testing",
        "creator_uri": "https://www.gov.uk/government/organisations/http-//fred-the-creator",
        "publisher_uri": "https://www.gov.uk/government/organisations/http-//joe-the-publisher",
        "landing_page_uris": [],
        "theme_uris": ["a-theme"],
        "keywords": ["two"],
        "dataset_issued": None,
        "dataset_modified": None,
        "license_uri": "the licence",
        "public_contact_point_uri": None,
        "uri_safe_identifier_override": "http://schema-id",
        "spatial_bound_uri": "spatial",
        "temporal_bound_uri": "temporal"
        }

      """
      Then The cube Columns should match
      """
      [
        {"csv_column_title": "Dim-0", "structural_definition": {"label": "Non Dimension", "description": None, "code_list": {"metadata": {"title": "Non Dimension", "identifier": None, "summary": None, "description": None, "creator_uri": None, "publisher_uri": None, "landing_page_uris": [], "theme_uris": [], "keywords": [], "dataset_issued": None, "dataset_modified": None, "license_uri": None, "public_contact_point_uri": None, "uri_safe_identifier_override": None, "spatial_bound_uri": None, "temporal_bound_uri": None}, "concepts": [{"label": "1", "code": "1", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}, {"label": "2", "code": "2", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}], "arbitrary_rdf": []}, "parent_dimension_uri": None, "source_uri": None, "range_uri": None, "uri_safe_identifier_override": None, "arbitrary_rdf": []}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
        {"csv_column_title": "Dim-1", "structural_definition": {"label": "Dim-1", "description": None, "code_list": {"metadata": {"title": "Dim-1", "identifier": None, "summary": None, "description": None, "creator_uri": None, "publisher_uri": None, "landing_page_uris": [], "theme_uris": [], "keywords": [], "dataset_issued": None, "dataset_modified": None, "license_uri": None, "public_contact_point_uri": None, "uri_safe_identifier_override": None, "spatial_bound_uri": None, "temporal_bound_uri": None}, "concepts": [{"label": "2009", "code": "2009", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}, {"label": "2010", "code": "2010", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}], "arbitrary_rdf": []}, "parent_dimension_uri": None, "source_uri": None, "range_uri": None, "uri_safe_identifier_override": None, "arbitrary_rdf": []}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
        {"csv_column_title": "Dim-2", "structural_definition": {"label": "Trade Direction Dimension", "description": None, "code_list": {"metadata": {"title": "Trade Direction Dimension", "identifier": None, "summary": None, "description": None, "creator_uri": None, "publisher_uri": None, "landing_page_uris": [], "theme_uris": [], "keywords": [], "dataset_issued": None, "dataset_modified": None, "license_uri": None, "public_contact_point_uri": None, "uri_safe_identifier_override": None, "spatial_bound_uri": None, "temporal_bound_uri": None}, "concepts": [{"label": "export", "code": "export", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}, {"label": "import", "code": "import", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}], "arbitrary_rdf": []}, "parent_dimension_uri": None, "source_uri": None, "range_uri": None, "uri_safe_identifier_override": None, "arbitrary_rdf": []}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
        {"csv_column_title": "Attr-1", "structural_definition": {"label": "My best attribute", "description": None, "new_attribute_values": [{"label": "goods", "description": None, "uri_safe_identifier_override": None, "source_uri": None, "parent_attribute_value_uri": None, "arbitrary_rdf": []}, {"label": "services", "description": None, "uri_safe_identifier_override": None, "source_uri": None, "parent_attribute_value_uri": None, "arbitrary_rdf": []}], "parent_attribute_uri": None, "source_uri": None, "is_required": False, "uri_safe_identifier_override": None, "arbitrary_rdf": []}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
        {"csv_column_title": "Amount", "structural_definition": {"label": "Amount", "description": None, "code_list": {"metadata": {"title": "Amount", "identifier": None, "summary": None, "description": None, "creator_uri": None, "publisher_uri": None, "landing_page_uris": [], "theme_uris": [], "keywords": [], "dataset_issued": None, "dataset_modified": None, "license_uri": None, "public_contact_point_uri": None, "uri_safe_identifier_override": None, "spatial_bound_uri": None, "temporal_bound_uri": None}, "concepts": [{"label": "100", "code": "100", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}, {"label": "321", "code": "321", "parent_code": None, "sort_order": None, "description": None, "uri_safe_identifier_override": None}], "arbitrary_rdf": []}, "parent_dimension_uri": None, "source_uri": None, "range_uri": None, "uri_safe_identifier_override": None, "arbitrary_rdf": []}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
        {"csv_column_title": "Measure", "structural_definition": {"measures": [{"label": "Billions", "description": None, "parent_measure_uri": None, "source_uri": None, "uri_safe_identifier_override": None, "arbitrary_rdf": []}]}, "csv_column_uri_template": None, "uri_safe_identifier_override": None},
        {"csv_column_title": "Units", "structural_definition": {"units": [{"label": "Pounds", "description": None, "source_uri": None, "uri_safe_identifier_override": None, "arbitrary_rdf": [], "base_unit": None, "base_unit_scaling_factor": None, "qudt_quantity_kind_uri": None, "si_base_unit_conversion_multiplier": None}]}, "csv_column_uri_template": None, "uri_safe_identifier_override": None}
      ]
      """
      # TODO test case for column in config but not data