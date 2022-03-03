Feature: Testing cube from config json

    Scenario: This should succeed when a a valid csv and config.json file are provided
        Given the existing test-case file "config/cube_data_config_ok.json"
        When loading the existing Catalog Metadata file "MultipleLandingPageError/CatalogMetadata.json"
        And the Catalog Metadata file is converted to Turtle with dataset URI "http://dataset-uri"
        Then the RDF should contain
        """
            @prefix dcat: <http://www.w3.org/ns/dcat#> .
      
            <http://dataset-uri> a dcat:Dataset;
                dcat:landingPage <http://first-landing-page>,
                    <http://second-landing-page>.
        """