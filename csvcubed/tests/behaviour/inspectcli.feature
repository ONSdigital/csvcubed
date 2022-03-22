Feature: Behaviour testing of csvcubed inspect.

    Scenario: inspect should produce th eexpected printable for data cube metadata json-ld input of type multi-unit multi-measure.
        Given the existing test-case file "cli/inspect/multi-unit_multi-measure/alcohol-bulletin.csv-metadata.json"
        And the existing test-case file "cli/inspect/multi-unit_multi-measure/alcohol-bulletin.csv"
        When the existing Metadata file exists "cli/inspect/multi-unit_multi-measure/alcohol-bulletin.csv-metadata.json"
        And the existing csv file exists "cli/inspect/multi-unit_multi-measure/alcohol-bulletin.csv"
        And the Metadata File json-ld is loaded to a rdf graph
        And the Metadata File is validated
        And the Printables for data cube are generated
        Then the Type Printable should be "- This file is a data cube."
        And the Catalog Metadata Printable should be
        """
          - The data cube has the following catalog metadata:
              - Title: Alcohol Bulletin
              - Label: Alcohol Bulletin
              - Issued: 2016-02-26T09:30:00+00:00
              - Modified: 2022-02-11T21:00:09.286102+00:00
              - License: None
              - Creator: https://www.gov.uk/government/organisations/hm-revenue-customs
              - Publisher: https://www.gov.uk/government/organisations/hm-revenue-customs
              - Landing Pages: 
                      -- https://www.gov.uk/government/statistics/alcohol-bulletin
              - Themes: 
                      -- http://gss-data.org.uk/def/gdp#trade
              - Keywords: None
              - Contact Point: None
              - Identifier: Alcohol Bulletin
              - Comment: Quarterly statistics from the 4 different alcohol duty regimes administered by HM Revenue and Customs.
              - Description: The Alcohol Bulletin National Statistics present statistics from the 4
                      different alcohol duties administered by HM Revenue and Customs (HMRC): [Wine
                      Duty](https://www.gov.uk/government/collections/wine-duty) (wine and made-
                      wine), [Spirits Duty](https://www.gov.uk/guidance/spirits-duty), [Beer
                      Duty](https://www.gov.uk/guidance/beer-duty) and [Cider
                      Duty](https://www.gov.uk/government/collections/cider-duty).
          
                      The Alcohol Bulletin is updated quarterly and includes statistics on duty
                      receipts up to the latest full month before its release, and statistics
                      relating to clearances and production that are one month behind that of duty
                      receipts.
          
                      [Archive versions of the Alcohol Bulletin published on GOV.UK after August
                      2019](https://webarchive.nationalarchives.gov.uk/ukgwa/*/https://www.gov.uk/government/statistics/alcohol-
                      bulletin) are no longer hosted on this page and are instead available via the
                      UK Government Web Archive, from the National Archives.
          
                      [Archive versions of the Alcohol Bulletin published between 2008 and August
                      2019](https://www.uktradeinfo.com/trade-data/tax-and-duty-bulletins/) are
                      found on the UK Trade Info website.
          
                      ## Quality report
          
                      Further details for this statistical release, including data suitability and
                      coverage, are included within the [Alcohol Bulletin quality
                      report](https://www.gov.uk/government/statistics/quality-report-alcohol-
                      duties-publications-bulletin-and-factsheet).
          
                      *[HMRC]: HM Revenue and Customs
                      *[UK]: United Kingdom
        """
        And the Data Structure Definition Printable should be
        """
        - The data cube has the following data structure definition:
        - Dataset Label: Alcohol Bulletin
        - Number of Components: 17
        - Components:
                                                                Property   Property Label Property Type     Column Title  Required
               http://purl.org/linked-data/sdmx/2009/dimension#refPeriod                      Dimension           Period      True
        http://gss-data.org.uk/def/trade/property/dimension/alcohol-type                      Dimension     Alcohol Type      True
                         alcohol-bulletin.csv#dimension/alcohol-sub-type Alcohol Sub Type     Dimension Alcohol Sub Type      True
                          alcohol-bulletin.csv#dimension/alcohol-content  Alcohol Content     Dimension  Alcohol Content      True
                         alcohol-bulletin.csv#dimension/clearance-origin Clearance Origin     Dimension Clearance Origin      True
                            http://purl.org/linked-data/cube#measureType                      Dimension     Measure Type      True
                http://gss-data.org.uk/def/measure/alcohol-duty-receipts                        Measure                       True
                   http://gss-data.org.uk/def/measure/beer-duty-receipts                        Measure                       True
                  http://gss-data.org.uk/def/measure/cider-duty-receipts                        Measure                       True
                           http://gss-data.org.uk/def/measure/clearances                        Measure                       True
                http://gss-data.org.uk/def/measure/clearances-of-alcohol                        Measure                       True
                    http://gss-data.org.uk/def/measure/production-volume                        Measure                       True
            http://gss-data.org.uk/def/measure/production-volume-alcohol                        Measure                       True
                http://gss-data.org.uk/def/measure/spirits-duty-receipts                        Measure                       True
                   http://gss-data.org.uk/def/measure/wine-duty-receipts                        Measure                       True
             http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure                      Attribute             Unit      True
               http://purl.org/linked-data/sdmx/2009/attribute#obsStatus                      Attribute           Marker     False
        - Columns where suppress output is true: None
        """
        And the Code List Printable should be
        """
        - The data cube has the following code list information:
        - Number of Code Lists: 3
        - Code Lists:
                                                Code List   Code List Label   Columns Used In
             alcohol-sub-type.csv#scheme/alcohol-sub-type                    Alcohol Sub Type
               alcohol-content.csv#scheme/alcohol-content                     Alcohol Content
             clearance-origin.csv#scheme/clearance-origin                    Clearance Origin
        """
        And the Dataset Information Printable should be
        """
        - The data cube has the following dataset information:
        - Number of Observations: 10676
        - Number of Duplicates: 0
        - First 10 Observations:
                            Period Alcohol Type Alcohol Sub Type Alcohol Content Clearance Origin      Value          Measure Type        Unit Marker
            government-year/1999-2000         wine            still    up-to-15-abv              all 8721828.97            clearances hectolitres    NaN
            government-year/1999-2000         wine        sparkling    up-to-15-abv              all  621067.74            clearances hectolitres    NaN
            government-year/1999-2000         wine              all     over-15-abv              all  312545.57            clearances hectolitres    NaN
            government-year/1999-2000         wine              all    over-5-5-abv          ex-ship 2248574.50            clearances hectolitres    NaN
            government-year/1999-2000         wine              all    over-5-5-abv     ex-warehouse 7393838.35            clearances hectolitres    NaN
            government-year/1999-2000         wine              all    over-5-5-abv        uk-origin   13029.44            clearances hectolitres    NaN
            government-year/1999-2000         wine              all             all              all 9655442.29            clearances hectolitres    NaN
            government-year/1999-2000         wine              all             all              all    1657.00    wine-duty-receipts gbp-million    NaN
            government-year/1999-2000         wine              all             all              all    6429.00 alcohol-duty-receipts gbp-million    NaN
            government-year/2000-2001         wine            still    up-to-15-abv              all 8920111.13            clearances hectolitres    NaN

                    - Last 10 Observations:
                Period   Alcohol Type Alcohol Sub Type Alcohol Content                    Clearance Origin  Value              Measure Type                 Unit        Marker
            month/2021-09          cider              all             all                                 all  25.05       cider-duty-receipts          gbp-million   provisional
            month/2021-10           beer               uk             all                                 all    NaN         production-volume thousand-hectolitres not-available
            month/2021-10           beer               uk             all                                 all    NaN production-volume-alcohol thousand-hectolitres not-available
            month/2021-10 beer-and-cider    uk-registered             all                                 all    NaN                clearances thousand-hectolitres not-available
            month/2021-10 beer-and-cider              all             all ex-warehouse-and-ex-ship-clearances    NaN                clearances thousand-hectolitres not-available
            month/2021-10           beer              all             all                                 all    NaN                clearances thousand-hectolitres not-available
            month/2021-10           beer              all             all                                 all    NaN     clearances-of-alcohol thousand-hectolitres not-available
            month/2021-10          cider              all             all                                 all    NaN                clearances thousand-hectolitres not-available
            month/2021-10           beer              all             all                                 all 344.74        beer-duty-receipts          gbp-million   provisional
            month/2021-10          cider              all             all                                 all  22.60       cider-duty-receipts          gbp-million   provisional
        """

        
    Scenario: inspect should produce printable for code list metadata json-ld input
        Given the existing test-case file "cli/inspect/codelist.csv-metadata.json"
        When the existing Metadata file exists "cli/inspect/codelist.csv-metadata.json"
        And the Metadata File json-ld is loaded to a rdf graph
        And the Metadata File is validated
        And the Printables for code list are generated
        Then the Type Printable should be "- This file is a code list."
        And the Catalog Metadata Printable should be
        """
        - The code list has the following catalog metadata:
            - Title: Alcohol Content
            - Label: Alcohol Content
            - Issued: 2022-02-11T21:00:21.040987
            - Modified: 2022-02-11T21:00:21.040987
            - License: None
            - Creator: None
            - Publisher: None
            - Landing Pages: None
            - Themes: None
            - Keywords: None
            - Contact Point: None
            - Identifier: Alcohol Content
            - Comment: None
            - Description: None
        """

    Scenario: inspect should output error when the metadata json-ld input does not exist
        Given a none existing test-case file "cli/inspect/not_exists.csv-metadata.json"
        Then the file not found error is displayed "Could not find test-case file"