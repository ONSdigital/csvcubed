Feature: Behaviour testing of csvcubed inspect.

    Scenario: inspect should produce the expected printable for data cube metadata json-ld input of type multi-unit multi-measure.
        Given the existing test-case file "cli/inspect/multi-unit_multi-measure/alcohol-bulletin.csv-metadata.json"
        And the existing test-case file "cli/inspect/multi-unit_multi-measure/alcohol-bulletin.csv"
        And the existing test-case file "cli/inspect/multi-unit_multi-measure/alcohol-content.table.json"
        And the existing test-case file "cli/inspect/multi-unit_multi-measure/alcohol-sub-type.table.json"
        And the existing test-case file "cli/inspect/multi-unit_multi-measure/clearance-origin.table.json"
        When the Metadata file path is detected and validated "cli/inspect/multi-unit_multi-measure/alcohol-bulletin.csv-metadata.json"
        And the csv file path is detected and validated "cli/inspect/multi-unit_multi-measure/alcohol-bulletin.csv"
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
        - The data cube has the following column component information:
            - Dataset Label: Alcohol Bulletin
            - Columns:
                  Title         Type Required                                                     Property URL Observations Column Titles
                  Period    Dimension     True        http://purl.org/linked-data/sdmx/2009/dimension#refPeriod
            Alcohol Type    Dimension     True http://gss-data.org.uk/def/trade/property/dimension/alcohol-type
        Alcohol Sub Type    Dimension     True                  alcohol-bulletin.csv#dimension/alcohol-sub-type
         Alcohol Content    Dimension     True                   alcohol-bulletin.csv#dimension/alcohol-content
        Clearance Origin    Dimension     True                  alcohol-bulletin.csv#dimension/clearance-origin
                   Value Observations    False               http://gss-data.org.uk/def/measure/{+measure_type}
            Measure Type     Measures     True                     http://purl.org/linked-data/cube#measureType
                    Unit        Units     True      http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure
                  Marker    Attribute    False        http://purl.org/linked-data/sdmx/2009/attribute#obsStatus

            - Columns where suppress output is true: None

        """
        And the Code List Printable should be
        """
        - The data cube has the following code list information:
        - Number of Code Lists: 3
        - Code Lists:
                                                Code List   Code List Label   Columns Used In
               alcohol-content.csv#scheme/alcohol-content                     Alcohol Content
             alcohol-sub-type.csv#scheme/alcohol-sub-type                    Alcohol Sub Type
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
        And the Dataset Value Counts Printable should be
        """
        - The data cube has the following value counts:
                - Value counts broken-down by measure and unit (of measure):
                          Measure                   Unit  Count
            alcohol-duty-receipts            gbp-million    314
               beer-duty-receipts            gbp-million    314
              cider-duty-receipts            gbp-million    314
                       clearances            hectolitres   4710
                       clearances hectolitres-of-alcohol    942
                       clearances   thousand-hectolitres   1256
            clearances-of-alcohol            hectolitres    942
            clearances-of-alcohol   thousand-hectolitres    314
                production-volume   thousand-hectolitres    314
        production-volume-alcohol            hectolitres    314
        production-volume-alcohol   thousand-hectolitres    314
            spirits-duty-receipts            gbp-million    314
               wine-duty-receipts            gbp-million    314
        """

    # Below test also validates the csvcubed against old-style single-measure pivoted shape data sets.
    Scenario: inspect should produce the expected printable for data cube metadata json-ld input of type multi-unit single-measure.
        Given the existing test-case file "pandas2_0_testing/multi-unit-single_measure-dataset-for-testing.csv-metadata.json"
        And the existing test-case file "pandas2_0_testing/multi-unit-single_measure-dataset-for-testing.csv"
        And the existing test-case file "pandas2_0_testing/dim1.csv"
        And the existing test-case file "pandas2_0_testing/dim1.csv-metadata.json"
        And the existing test-case file "pandas2_0_testing/dim1.table.json"
        And the existing test-case file "pandas2_0_testing/dim2.csv"
        And the existing test-case file "pandas2_0_testing/dim2.csv-metadata.json"
        And the existing test-case file "pandas2_0_testing/dim2.table.json"
        When the Metadata file path is detected and validated "pandas2_0_testing/multi-unit-single_measure-dataset-for-testing.csv-metadata.json"
        And the Metadata File json-ld is loaded to a rdf graph
        And the Metadata File is validated
        And the Printables for data cube are generated
        Then the Type Printable should be "- This file is a data cube."
        And the Catalog Metadata Printable should be
        """
        - The data cube has the following catalog metadata:
          - Title: Multi-Unit-Single_Measure DataSet for testing
          - Label: Multi-Unit-Single_Measure DataSet for testing
          - Issued: 2023-05-16T09:01:16.011380
          - Modified: 2023-05-16T09:01:16.011380
          - License: None
          - Creator: None
          - Publisher: None
          - Landing Pages: None
          - Themes: None
          - Keywords: None
          - Contact Point: None
          - Identifier: Multi-Unit-Single_Measure DataSet for testing
          - Comment: None
          - Description: None
        """
        And the Data Structure Definition Printable should be
        """
        - The data cube has the following column component information:
            - Dataset Label: Multi-Unit-Single_Measure DataSet for testing
            - Columns:
                Title         Type  Required                                                         Property URL Observations Column Titles
            Manufacture    Dimension      True     multi-unit-single_measure-dataset-for-testing.csv#dimension/dim1
                    Type    Dimension      True     multi-unit-single_measure-dataset-for-testing.csv#dimension/dim2
                Measure     Measures      True                         http://purl.org/linked-data/cube#measureType               Observations
                    Unit        Units      True          http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure
            Observations Observations      True multi-unit-single_measure-dataset-for-testing.csv#measure/{+measure}
            - Columns where suppress output is true: None
        """
        And the Code List Printable should be
        """
        - The data cube has the following code list information:
                - Number of Code Lists: 2
                - Code Lists:
                Code List Code List Label Columns Used In
        dim1.csv#code-list            Dim1     Manufacture
        dim2.csv#code-list            Dim2            Type
        """
        And the Dataset Information Printable should be
        """
        - The data cube has the following dataset information:
                - Number of Observations: 3
                - Number of Duplicates: 0
                - Observations:
        Manufacture  Type      Measure    Unit  Observations
            ford sedan retail-price  pounds        1000.0
            audi sedan retail-price dollars         900.0
            opel sedan retail-price dollars         900.0
        """
        And the Dataset Value Counts Printable should be
        """
        - The data cube has the following value counts:
                - Value counts broken-down by measure and unit (of measure):
            Measure    Unit  Count
        retail-price dollars      2
        retail-price  pounds      1
        """

    Scenario: inspect should produce the expected printable for data cube metadata json-ld input of type single-unit multi-measure.
        Given the existing test-case file "cli/inspect/single-unit_multi-measure/final-uk-greenhouse-gas-emissions-national-statistics-1990-to-2020.csv-metadata.json"
        And the existing test-case file "cli/inspect/single-unit_multi-measure/final-uk-greenhouse-gas-emissions-national-statistics-1990-to-2020.csv"
        And the existing test-case file "cli/inspect/single-unit_multi-measure/ghg.table.json"
        And the existing test-case file "cli/inspect/single-unit_multi-measure/ghg-grouped.table.json"
        And the existing test-case file "cli/inspect/single-unit_multi-measure/ipcc-code.table.json"
        And the existing test-case file "cli/inspect/single-unit_multi-measure/year.table.json"
        And the existing test-case file "cli/inspect/single-unit_multi-measure/national-communication-sector.table.json"
        And the existing test-case file "cli/inspect/single-unit_multi-measure/national-communication-sub-sector.table.json"
        And the existing test-case file "cli/inspect/single-unit_multi-measure/national-communication-category.table.json"
        And the existing test-case file "cli/inspect/single-unit_multi-measure/source.table.json"
        And the existing test-case file "cli/inspect/single-unit_multi-measure/national-communication-fuel-group.table.json"
        And the existing test-case file "cli/inspect/single-unit_multi-measure/national-communication-fuel.table.json"
        And the existing test-case file "cli/inspect/single-unit_multi-measure/activity-name.table.json"
        When the Metadata file path is detected and validated "cli/inspect/single-unit_multi-measure/final-uk-greenhouse-gas-emissions-national-statistics-1990-to-2020.csv-metadata.json"
        And the Metadata File json-ld is loaded to a rdf graph
        And the Metadata File is validated
        And the Printables for data cube are generated
        Then the Type Printable should be "- This file is a data cube."
        And the Catalog Metadata Printable should be
        """
        - The data cube has the following catalog metadata:
            - Title: Final UK greenhouse gas emissions national statistics: 1990 to 2020
            - Label: Final UK greenhouse gas emissions national statistics: 1990 to 2020
            - Issued: 2022-02-01T09:30:05+00:00
            - Modified: 2022-03-03T14:56:27.845825+00:00
            - License: None
            - Creator: https://www.gov.uk/government/organisations/department-for-business-energy-and-industrial-strategy
            - Publisher: https://www.gov.uk/government/organisations/department-for-business-energy-and-industrial-strategy
            - Landing Pages:
                    -- https://www.gov.uk/government/statistics/final-uk-greenhouse-gas-emissions-national-statistics-1990-to-2020
            - Themes:
                    -- http://gss-data.org.uk/def/gdp#climate-change
            - Keywords: None
            - Contact Point: None
            - Identifier: Final UK greenhouse gas emissions national statistics: 1990 to 2020
            - Comment: Final estimates of UK territorial greenhouse gas emissions.
            - Description: This publication provides the final estimates of UK territorial greenhouse gas
                    emissions going back to 1990. Estimates are presented by source in February of
                    each year. They are updated in March of each year to include estimates by end-
                    user, and in June to include estimates by Standard Industrial Classification
                    (SIC).

                    These statistics covers emissions that occur within the UK’s borders. When
                    emissions are reported by source, emissions are attributed to the sector that
                    emits them directly. When emissions are reported by end-user, energy supply
                    emissions by source are reallocated in accordance with where the end-use
                    activity occurred. This reallocation of emissions is based on a modelling
                    process. For example, all the carbon dioxide produced by a power station is
                    allocated to the power station when reporting on a source basis. However, when
                    applying the end-user method, these emissions are reallocated to the users of
                    this electricity, such as domestic homes or large industrial users.

                    BEIS does not estimate emissions outside the UK associated with UK
                    consumption, however the Department for Environment, Food and Rural Affairs
                    publishes estimates of the [UK’s carbon
                    footprint](https://www.gov.uk/government/statistics/uks-carbon-footprint)
                    annually.

                    For the purposes of reporting, greenhouse gas emissions are allocated into a
                    small number of broad, high level sectors known as National Communication
                    sectors, which are as follows: energy supply, business, transport, public,
                    residential, agriculture, industrial processes, land use land use change and
                    forestry (LULUCF), and waste management.

                    These high-level sectors are made up of a number of more detailed sectors,
                    which follow the definitions set out by the [International Panel on Climate
                    Change (IPCC)](http://www.ipcc.ch/), and which are used in international
                    reporting tables which are submitted to the [United Nations Framework
                    Convention on Climate Change (UNFCCC)](https://unfccc.int/) every year.

                    This is a National Statistics publication and complies with the Code of
                    Practice for Statistics.

                    Please check our [frequently asked
                    questions](https://www.gov.uk/government/publications/uk-greenhouse-gas-
                    emissions-explanatory-notes) or email
                    [GreenhouseGas.Statistics@beis.gov.uk](mailto:GreenhouseGas.Statistics@beis.gov.uk)
                    if you have any questions or comments about the information on this page.

                    *[SIC]: Standard Industrial Classification
                    *[BEIS]: Department for Business, Energy and Industrial Strategy
                    *[LULUCF]: land use land use change and forestry
                    *[IPCC]: International Panel on Climate Change
                    *[UNFCCC]: United Nations Framework Convention on Climate Change
        """
        And the Data Structure Definition Printable should be
        """
        - The data cube has the following column component information:
            - Dataset Label: Final UK greenhouse gas emissions national statistics: 1990 to 2020
            - Columns:
                                    Title         Type Required                                                                                                       Property URL Observations Column Titles
                                      GHG    Dimension     True                               final-uk-greenhouse-gas-emissions-national-statistics-1990-to-2020.csv#dimension/ghg
                              GHG Grouped    Dimension     True                       final-uk-greenhouse-gas-emissions-national-statistics-1990-to-2020.csv#dimension/ghg-grouped
                                IPCC Code    Dimension     True                         final-uk-greenhouse-gas-emissions-national-statistics-1990-to-2020.csv#dimension/ipcc-code
                                     Year    Dimension     True                              final-uk-greenhouse-gas-emissions-national-statistics-1990-to-2020.csv#dimension/year
            National Communication Sector    Dimension     True     final-uk-greenhouse-gas-emissions-national-statistics-1990-to-2020.csv#dimension/national-communication-sector
        National Communication Sub-sector    Dimension     True final-uk-greenhouse-gas-emissions-national-statistics-1990-to-2020.csv#dimension/national-communication-sub-sector
          National Communication Category    Dimension     True   final-uk-greenhouse-gas-emissions-national-statistics-1990-to-2020.csv#dimension/national-communication-category
                                   Source    Dimension     True                            final-uk-greenhouse-gas-emissions-national-statistics-1990-to-2020.csv#dimension/source
        National Communication Fuel Group    Dimension     True final-uk-greenhouse-gas-emissions-national-statistics-1990-to-2020.csv#dimension/national-communication-fuel-group
              National Communication Fuel    Dimension     True       final-uk-greenhouse-gas-emissions-national-statistics-1990-to-2020.csv#dimension/national-communication-fuel
                            Activity Name    Dimension     True                     final-uk-greenhouse-gas-emissions-national-statistics-1990-to-2020.csv#dimension/activity-name
                                  Measure     Measures     True                                                                       http://purl.org/linked-data/cube#measureType                      Value
                                    Value Observations     True                          final-uk-greenhouse-gas-emissions-national-statistics-1990-to-2020.csv#measure/{+measure}

            - Columns where suppress output is true: None

        """
        And the Code List Printable should be
        """
        - The data cube has the following code list information:
                - Number of Code Lists: 11
                - Code Lists:
                                             Code List Code List Label                    Columns Used In
                            activity-name.csv#code-list                                     Activity Name
                              ghg-grouped.csv#code-list                                       GHG Grouped
                                      ghg.csv#code-list                                               GHG
                                ipcc-code.csv#code-list                                         IPCC Code
          national-communication-category.csv#code-list                   National Communication Category
        national-communication-fuel-group.csv#code-list                 National Communication Fuel Group
              national-communication-fuel.csv#code-list                       National Communication Fuel
            national-communication-sector.csv#code-list                     National Communication Sector
        national-communication-sub-sector.csv#code-list                 National Communication Sub-sector
                                   source.csv#code-list                                            Source
                                     year.csv#code-list                                              Year
        """
        And the Dataset Information Printable should be
        """
        - The data cube has the following dataset information:
                - Number of Observations: 99530
                - Number of Duplicates: 0
                - First 10 Observations:
        GHG GHG Grouped IPCC Code  Year National Communication Sector National Communication Sub-sector National Communication Category                          Source National Communication Fuel Group National Communication Fuel       Activity Name            Measure  Value
        c2f6        pfcs     2b9b3  1990          industrial-processes                    not-applicable           halocarbon-production halocarbons-production-fugitive                   other-emissions             other-emissions non-fuel-combustion emissions-ar4-gwps  0.001
        c2f6        pfcs     2b9b3  1991          industrial-processes                    not-applicable           halocarbon-production halocarbons-production-fugitive                   other-emissions             other-emissions non-fuel-combustion emissions-ar4-gwps  0.001
        c2f6        pfcs     2b9b3  1992          industrial-processes                    not-applicable           halocarbon-production halocarbons-production-fugitive                   other-emissions             other-emissions non-fuel-combustion emissions-ar4-gwps  0.001
        c2f6        pfcs     2b9b3  1993          industrial-processes                    not-applicable           halocarbon-production halocarbons-production-fugitive                   other-emissions             other-emissions non-fuel-combustion emissions-ar4-gwps  0.003
        c2f6        pfcs     2b9b3  1994          industrial-processes                    not-applicable           halocarbon-production halocarbons-production-fugitive                   other-emissions             other-emissions non-fuel-combustion emissions-ar4-gwps  0.006
        c2f6        pfcs     2b9b3  1995          industrial-processes                    not-applicable           halocarbon-production halocarbons-production-fugitive                   other-emissions             other-emissions non-fuel-combustion emissions-ar4-gwps  0.008
        c2f6        pfcs     2b9b3  1996          industrial-processes                    not-applicable           halocarbon-production halocarbons-production-fugitive                   other-emissions             other-emissions non-fuel-combustion emissions-ar4-gwps  0.009
        c2f6        pfcs     2b9b3  1997          industrial-processes                    not-applicable           halocarbon-production halocarbons-production-fugitive                   other-emissions             other-emissions non-fuel-combustion emissions-ar4-gwps  0.005
        c2f6        pfcs     2b9b3  1998          industrial-processes                    not-applicable           halocarbon-production halocarbons-production-fugitive                   other-emissions             other-emissions non-fuel-combustion emissions-ar4-gwps  0.005
        c2f6        pfcs     2b9b3  1999          industrial-processes                    not-applicable           halocarbon-production halocarbons-production-fugitive                   other-emissions             other-emissions non-fuel-combustion emissions-ar4-gwps  0.002

                - Last 10 Observations:
        GHG GHG Grouped IPCC Code  Year National Communication Sector National Communication Sub-sector National Communication Category                      Source National Communication Fuel Group National Communication Fuel  Activity Name            Measure  Value
        co2         co2    5c1-2b  2016              waste-management                    not-applicable              waste-incineration incineration-chemical-waste                   other-emissions             other-emissions chemical-waste emissions-ar5-gwps  0.181
        co2         co2    5c1-2b  2016              waste-management                    not-applicable              waste-incineration incineration-clinical-waste                   other-emissions             other-emissions clinical-waste emissions-ar5-gwps  0.082
        co2         co2    5c1-2b  2017              waste-management                    not-applicable              waste-incineration incineration-chemical-waste                   other-emissions             other-emissions chemical-waste emissions-ar5-gwps  0.176
        co2         co2    5c1-2b  2017              waste-management                    not-applicable              waste-incineration incineration-clinical-waste                   other-emissions             other-emissions clinical-waste emissions-ar5-gwps  0.081
        co2         co2    5c1-2b  2018              waste-management                    not-applicable              waste-incineration incineration-chemical-waste                   other-emissions             other-emissions chemical-waste emissions-ar5-gwps  0.159
        co2         co2    5c1-2b  2018              waste-management                    not-applicable              waste-incineration incineration-clinical-waste                   other-emissions             other-emissions clinical-waste emissions-ar5-gwps  0.081
        co2         co2    5c1-2b  2019              waste-management                    not-applicable              waste-incineration incineration-chemical-waste                   other-emissions             other-emissions chemical-waste emissions-ar5-gwps  0.158
        co2         co2    5c1-2b  2019              waste-management                    not-applicable              waste-incineration incineration-clinical-waste                   other-emissions             other-emissions clinical-waste emissions-ar5-gwps  0.084
        co2         co2    5c1-2b  2020              waste-management                    not-applicable              waste-incineration incineration-chemical-waste                   other-emissions             other-emissions chemical-waste emissions-ar5-gwps  0.167
        co2         co2    5c1-2b  2020              waste-management                    not-applicable              waste-incineration incineration-clinical-waste                   other-emissions             other-emissions clinical-waste emissions-ar5-gwps  0.081
        """
        And the Dataset Value Counts Printable should be
        """
        - The data cube has the following value counts:
                - Value counts broken-down by measure and unit (of measure):
                    Measure   Unit  Count
         emissions-ar4-gwps MtCO2e  49765
         emissions-ar5-gwps MtCO2e  49765
        """

    Scenario: inspect should produce the expected printable for data cube metadata json-ld input of type single-unit single-measure.
        Given the existing test-case file "cli/inspect/single-unit_single-measure/energy-trends-uk-total-energy.csv-metadata.json"
        And the existing test-case file "cli/inspect/single-unit_single-measure/energy-trends-uk-total-energy.csv"
        When the Metadata file path is detected and validated "cli/inspect/single-unit_single-measure/energy-trends-uk-total-energy.csv-metadata.json"
        And the csv file path is detected and validated "cli/inspect/single-unit_single-measure/energy-trends-uk-total-energy.csv"
        And the Metadata File json-ld is loaded to a rdf graph
        And the Metadata File is validated
        And the Printables for data cube are generated
        Then the Type Printable should be "- This file is a data cube."
        And the Catalog Metadata Printable should be
        """
        - The data cube has the following catalog metadata:
            - Title: Energy Trends: UK total energy
            - Label: Energy Trends: UK total energy
            - Issued: 2013-06-27T08:30:00+00:00
            - Modified: 2022-03-16T10:29:42.619423+00:00
            - License: None
            - Creator: https://www.gov.uk/government/organisations/department-for-business-energy-and-industrial-strategy
            - Publisher: https://www.gov.uk/government/organisations/department-for-business-energy-and-industrial-strategy
            - Landing Pages:
                    -- https://www.gov.uk/government/statistics/total-energy-section-1-energy-trends
            - Themes:
                    -- http://gss-data.org.uk/def/gdp#climate-change
            - Keywords: None
            - Contact Point: None
            - Identifier: Energy Trends: UK total energy
            - Comment: Data on overall energy balances of energy supply and demand in the United Kingdom.
            - Description: ### UK total energy production and consumption (PDF)

                    An overview of the trends in energy production and consumption in the United
                    Kingdom for the previous quarter, focusing on:​

                    * production ​
                    * consumption, both primary and final by broad sector, including seasonally adjusted series​
                    * dependency rates of imports, fossil fuels and low carbon fuels​

                    We publish this document on the last Thursday of each calendar quarter (March,
                    June, September and December).

                    ### Quarterly data (all tables)​

                    The quarterly version of the tables covers production, consumption by broad
                    sector and key energy dependency ratios.

                    We publish all tables (ET 1.1 - ET 1.3) on a quarterly basis, on the last
                    Thursday of the calendar quarter (March, June, September and December). The
                    data is a quarter in arrears.​

                    ### Monthly data​ ET 1.1, ET 1.2

                    The monthly versions focus on production and consumption only. More detail is
                    provided in the quarterly versions.

                    We publish 2 of the tables on a monthly basis (ET 1.1 and ET 1.2), on the last
                    Thursday of the month.

                    ### Earlier data​

                    Previous editions of Energy Trends are available on the [Energy
                    Trends](https://www.gov.uk/government/collections/energy-trends) collection
                    page.

                    You can request previous editions of the tables from BEIS using the email
                    below in Contact us.

                    ### Contact us​

                    If you have questions about these statistics, please email:
                    [energy.stats@beis.gov.uk](mailto:energy.stats@beis.gov.uk)

                    *[ET]: Energy Trends
        """
        And the Data Structure Definition Printable should be
        """
        - The data cube has the following column component information:
            - Dataset Label: Energy Trends: UK total energy
            - Columns:
              Title         Type Required                                                Property URL Observations Column Titles
              Period    Dimension     True   http://purl.org/linked-data/sdmx/2009/dimension#refPeriod
              Region    Dimension     True     http://purl.org/linked-data/sdmx/2009/dimension#refArea
                Fuel    Dimension     True   http://gss-data.org.uk/def/energy/property/dimension/fuel
        Measure Type     Measures     True                http://purl.org/linked-data/cube#measureType                      Value
                Unit        Units     True http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure
               Value Observations     True   energy-trends-uk-total-energy.csv#measure/{+measure_type}

        - Columns where suppress output is true: None

        """
        And the Code List Printable should be
        """
        - The data cube has the following code list information:
            - Number of Code Lists: 0
            - Code Lists:
                None
        """
        And the Dataset Information Printable should be
        """
        - The data cube has the following dataset information:
                - Number of Observations: 286
                - Number of Duplicates: 0
                - First 10 Observations:
           Period    Region Fuel       Measure Type                                 Unit  Value
        year/1995 K02000001  all energy-consumption millions-of-tonnes-of-oil-equivalent  221.4
        year/1996 K02000001  all energy-consumption millions-of-tonnes-of-oil-equivalent  230.8
        year/1997 K02000001  all energy-consumption millions-of-tonnes-of-oil-equivalent  224.5
        year/1998 K02000001  all energy-consumption millions-of-tonnes-of-oil-equivalent  230.7
        year/1999 K02000001  all energy-consumption millions-of-tonnes-of-oil-equivalent  231.4
        year/2000 K02000001  all energy-consumption millions-of-tonnes-of-oil-equivalent  234.8
        year/2001 K02000001  all energy-consumption millions-of-tonnes-of-oil-equivalent  236.9
        year/2002 K02000001  all energy-consumption millions-of-tonnes-of-oil-equivalent  229.6
        year/2003 K02000001  all energy-consumption millions-of-tonnes-of-oil-equivalent  231.9
        year/2004 K02000001  all energy-consumption millions-of-tonnes-of-oil-equivalent  233.7

                - Last 10 Observations:
           Period    Region       Fuel       Measure Type                                 Unit  Value
        year/2011 K02000001 renewables energy-consumption millions-of-tonnes-of-oil-equivalent    9.8
        year/2012 K02000001 renewables energy-consumption millions-of-tonnes-of-oil-equivalent   10.4
        year/2013 K02000001 renewables energy-consumption millions-of-tonnes-of-oil-equivalent   12.1
        year/2014 K02000001 renewables energy-consumption millions-of-tonnes-of-oil-equivalent   14.3
        year/2015 K02000001 renewables energy-consumption millions-of-tonnes-of-oil-equivalent   17.1
        year/2016 K02000001 renewables energy-consumption millions-of-tonnes-of-oil-equivalent   18.1
        year/2017 K02000001 renewables energy-consumption millions-of-tonnes-of-oil-equivalent   20.0
        year/2018 K02000001 renewables energy-consumption millions-of-tonnes-of-oil-equivalent   22.5
        year/2019 K02000001 renewables energy-consumption millions-of-tonnes-of-oil-equivalent   24.5
        year/2020 K02000001 renewables energy-consumption millions-of-tonnes-of-oil-equivalent   26.1
        """
        And the Dataset Value Counts Printable should be
        """
        - The data cube has the following value counts:
            - Value counts broken-down by measure and unit (of measure):
                       Measure                                 Unit  Count
            energy-consumption millions-of-tonnes-of-oil-equivalent    286
        """

    Scenario: inspect should produce printable for code list metadata json-ld input
        Given the existing test-case file "cli/inspect/alcohol-content.csv-metadata.json"
        And the existing test-case file "cli/inspect/alcohol-content.table.json"
        And the existing test-case file "cli/inspect/alcohol-content.csv"

        When the Metadata file path is detected and validated "cli/inspect/alcohol-content.csv-metadata.json"
        And the csv file path is detected and validated "cli/inspect/alcohol-content.csv"
        And the Metadata File json-ld is loaded to a rdf graph
        And the Metadata File is validated
        And the Printables for code list are generated
        Then the Type Printable should be "- This file is a code list."
        And the Catalog Metadata Printable should be
        """
        - The code list has the following catalog metadata:
            - Title: Alcohol Content
            - Label: Alcohol Content
            - Issued: 2022-02-24T11:42:44.097778
            - Modified: 2022-02-24T11:42:44.097778
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
        And the Dataset Information Printable should be
        """
        - The code list has the following dataset information:
          - Number of Concepts: 6
          - Number of Duplicates: 0
          - Concepts:
                           Label       Notation  Parent Notation  Sort Priority  Description
                1.2% to 5.5% abv 1-2-to-5-5-abv              NaN              0          NaN
                 5.5% to 15% abv  5-5-to-15-abv              NaN              1          NaN
                             All            all              NaN              2          NaN
                    over 15% abv    over-15-abv              NaN              3          NaN
                   over 5.5% abv   over-5-5-abv              NaN              4          NaN
                   up to 15% abv   up-to-15-abv              NaN              5          NaN
        """
        And the Concepts Information Printable should be
        """
        - The code list has the following concepts information:
                - Concepts hierarchy depth: 1
                - Concepts hierarchy:
                        root
                        ├── 1.2% to 5.5% abv
                        ├── 5.5% to 15% abv
                        ├── All
                        ├── over 15% abv
                        ├── over 5.5% abv
                        └── up to 15% abv
        """

    Scenario: inspect should produce printable for code list metadata json-ld input with concepts hierarchy depth of more than one
        Given the existing test-case file "cli/inspect/itis-industry.csv-metadata.json"
        And the existing test-case file "cli/inspect/itis-industry.csv"
        When the Metadata file path is detected and validated "cli/inspect/itis-industry.csv-metadata.json"
        And the csv file path is detected and validated "cli/inspect/itis-industry.csv"
        And the Metadata File json-ld is loaded to a rdf graph
        And the Metadata File is validated
        And the Printables for code list are generated
        Then the Type Printable should be "- This file is a code list."
        And the Catalog Metadata Printable should be
		"""
		- The code list has the following catalog metadata:
            - Title: Itis Industry
            - Label: Itis Industry
            - Issued: 2021-04-13T10:04:13.589262
            - Modified: 2021-05-20T10:55:04.059085
            - License: None
            - Creator: None
            - Publisher: None
            - Landing Pages: None
            - Themes: None
            - Keywords: None
            - Contact Point: None
            - Identifier: None
            - Comment: Dataset representing the 'Itis Industry' code list.
            - Description: None
        """
        And the Dataset Information Printable should be
        """
        - The code list has the following dataset information:
          - Number of Concepts: 9
          - Number of Duplicates: 0
          - Concepts:
																   Label       														  Notation Parent Notation  Sort Priority  Description
									   					  All industries  																   all             NaN              1          NaN
														   Manufacturing   								 				manufacturing-industry             all              2          NaN
			 									 	  Wholesale & Retail   											 wholesale-retail-industry             all              3          NaN
							 			   Information and Communication   								information-and-communication-industry             all              4          NaN
						  Professional, Scientific and Technical Support   				professional-scientific-and-technical-support-industry             all              5          NaN
			 			   Administrative and Support Service Activities   				administrative-and-support-service-activities-industry             all              6          NaN
            Arts, Entertainment, Recreation and Other Service Activities   arts-entertainment-recreation-and-other-service-activities-industry             all              7          NaN
														   Film Industry   								film-industry-excluding-other-services             all              8          NaN
													 Television Industry   						  television-industry-excluding-other-services             all              9          NaN
        """
		And the Concepts Information Printable should be
		"""
		- The code list has the following concepts information:
			- Concepts hierarchy depth: 2
			- Concepts hierarchy:
				root
				└── All industries
						├── Administrative and Support Service Activities
						├── Arts, Entertainment, Recreation and Other Service Activities
						├── Film Industry
						├── Information and Communication
						├── Manufacturing
						├── Professional, Scientific and Technical Support
						├── Television Industry
						└── Wholesale & Retail
		"""

    Scenario: inspect should output error when the metadata json-ld input does not exist
        Given a none existing test-case file "cli/inspect/not_exists.csv-metadata.json"
        Then the file not found error is displayed "Could not find test-case file"

    Scenario: An older CSV-W generated by csvcubed build that uses the notation column as the identifier should produce the correct concepts hierarchy.
        Given the existing test-case file "cli/inspect/code-list-with-notation-as-identifier/attr-1.csv-metadata.json"
        And the existing test-case file "cli/inspect/code-list-with-notation-as-identifier/attr-1.table.json"
        And the existing test-case file "cli/inspect/code-list-with-notation-as-identifier/attr-1.csv"
        When the Metadata file path is detected and validated "cli/inspect/code-list-with-notation-as-identifier/attr-1.csv-metadata.json"
        And the csv file path is detected and validated "cli/inspect/code-list-with-notation-as-identifier/attr-1.csv"
        And the Metadata File json-ld is loaded to a rdf graph
        And the Metadata File is validated
        And the Printables for code list are generated
        Then the Concepts Information Printable should be
        """
        - The code list has the following concepts information:
                - Concepts hierarchy depth: 1
                - Concepts hierarchy:
                    root
                    ├── goods
                    ├── services
        """

    Scenario: A newer CSV-W generated by csvcubed build that uses the uri identifier column as the identifier should produce the correct concepts hierarchy.
        Given the existing test-case file "cli/inspect/code-list-with-uri-identifier-as-identifier/attr-1.csv-metadata.json"
        And the existing test-case file "cli/inspect/code-list-with-uri-identifier-as-identifier/attr-1.table.json"
        And the existing test-case file "cli/inspect/code-list-with-uri-identifier-as-identifier/attr-1.csv"
        When the Metadata file path is detected and validated "cli/inspect/code-list-with-uri-identifier-as-identifier/attr-1.csv-metadata.json"
        And the csv file path is detected and validated "cli/inspect/code-list-with-uri-identifier-as-identifier/attr-1.csv"
        And the Metadata File json-ld is loaded to a rdf graph
        And the Metadata File is validated
        And the Printables for code list are generated
        Then the Concepts Information Printable should be
        """
        - The code list has the following concepts information:
                - Concepts hierarchy depth: 1
                - Concepts hierarchy:
                    root
                    ├── goods
                    ├── services
        """
