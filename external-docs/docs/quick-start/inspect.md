# Inspecting a CSV-W

This page is designed to help you inspect an existing CSV-W.

## A transcribed video walkthrough

<iframe src="https://share.descript.com/embed/Umk1wrKpSMV" width="640" height="360" frameborder="0" allowfullscreen></iframe>

## Pre-requisites

You should have already [installed csvcubed](./installation.md), [designed your CSV input](./designing-csv.md) and [built your CSV-W](./build.md).

## Inspecting your CSV-W cube

To inspect the `sweden-at-eurovision-no-missing.csv-metadata.json` data cube we built in [Building a CSV-W](build.md), we run the [csvcubed inspect](../guides/command-line/inspect-command.md) command:

```bash
csvcubed inspect sweden-at-eurovision-no-missing.csv-metadata.json
```

All being well we get the below output. A detailed explanation of this output is provided in [csvcubed inspect](../guides/command-line/inspect-command.md#output-format) section.

```
- This file is a data cube.

- The data cube has the following catalog metadata:
        - Title: Sweden At Eurovision No Missing
        - Label: Sweden At Eurovision No Missing
        - Issued: 2022-04-08T11:12:13.034892
        - Modified: 2022-04-08T11:12:13.034892
        - License: None
        - Creator: None
        - Publisher: None
        - Landing Pages: None
        - Themes: None
        - Keywords: None
        - Contact Point: None
        - Identifier: Sweden At Eurovision No Missing
        - Comment: None
        - Description: None

 - The data cube has the following column component information:
     - Dataset Label: Sweden at Eurovision
     - Columns:
           Title         Type  Required                                                Property URL Observations Column Titles
            Year    Dimension      True                     sweden-at-eurovision.csv#dimension/year
         Entrant    Dimension      True                  sweden-at-eurovision.csv#dimension/entrant
            Song    Dimension      True                     sweden-at-eurovision.csv#dimension/song
        Language    Dimension      True                 sweden-at-eurovision.csv#dimension/language
           Value Observations      True                 sweden-at-eurovision.csv#measure/{+measure}
         Measure     Measures      True                http://purl.org/linked-data/cube#measureType
            Unit        Units      True http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure
     - Columns where suppress output is true: None

- The data cube has the following code list information:
        - Number of Code Lists: 4
        - Code Lists:
             Code List Code List Label Columns Used In
    year.csv#code-list                            Year
 entrant.csv#code-list                         Entrant
language.csv#code-list                        Language
    song.csv#code-list                            Song

- The data cube has the following dataset information:
        - Number of Observations: 178
        - Number of Duplicates: 0
        - First 10 Observations:
 Year       Entrant                  Song Language  Value         Measure    Unit
 1958    alice-babs         lilla-stjarna  swedish      4      final-rank ordinal
 1958    alice-babs         lilla-stjarna  swedish     10    final-points  points
 1958    alice-babs         lilla-stjarna  swedish      1 people-on-stage  people
 1959    brita-borg              augustin  swedish      9      final-rank ordinal
 1959    brita-borg              augustin  swedish      4    final-points  points
 1959    brita-borg              augustin  swedish      1 people-on-stage  people
 1960 siw-malmkvist alla-andra-far-varann  swedish     10      final-rank ordinal
 1960 siw-malmkvist alla-andra-far-varann  swedish      4    final-points  points
 1960 siw-malmkvist alla-andra-far-varann  swedish      1 people-on-stage  people
 1961     lill-babs           april-april  swedish     14      final-rank ordinal
        - Last 10 Observations:
 Year           Entrant              Song Language  Value         Measure    Unit
 2017   robin-bengtsson     i-can-t-go-on  english      6 people-on-stage  people
 2018 benjamin-ingrosso     dance-you-off  english      7      final-rank ordinal
 2018 benjamin-ingrosso     dance-you-off  english    274    final-points  points
 2018 benjamin-ingrosso     dance-you-off  english      6 people-on-stage  people
 2019      john-lundvik too-late-for-love  english    334    final-points  points
 2019      john-lundvik too-late-for-love  english      6 people-on-stage  people
 2019      john-lundvik too-late-for-love  english      5      final-rank ordinal
 2021             tusse            voices  english     14      final-rank ordinal
 2021             tusse            voices  english    109    final-points  points
 2021             tusse            voices  english      6 people-on-stage  people


- The data cube has the following value counts:
        - Value counts broken-down by measure and unit (of measure):
        Measure    Unit  Count
   final-points  points     59
     final-rank ordinal     59
people-on-stage  people     60
```

## Inspect a CSV-W code list

Now we inspect the `language.csv-metadata.json` code list we built in [Building a CSV-W](build.md):

```bash
csvcubed inspect language.csv-metadata.json
```

All being well we get the below output. A detailed explanation of this output is provided in [csvcubed inspect](../guides/command-line/inspect-command.md#output-format) section.

```
- This file is a code list.

- The code list has the following catalog metadata:
        - Title: Language
        - Label: Language
        - Issued: 2022-04-08T11:12:13.033011
        - Modified: 2022-04-08T11:12:13.033011
        - License: None
        - Creator: None
        - Publisher: None
        - Landing Pages: None
        - Themes: None
        - Keywords: None
        - Contact Point: None
        - Identifier: Language
        - Comment: None
        - Description: None


- The code list has the following dataset information:
        - Number of Concepts: 3
        - Number of Duplicates: 0
        - First 10 Concepts:
   Label Notation  Parent Notation  Sort Priority  Description
 English  english              NaN              0          NaN
Multiple multiple              NaN              1          NaN
 Swedish  swedish              NaN              2          NaN
        - Last 10 Concepts:
   Label Notation  Parent Notation  Sort Priority  Description
 English  english              NaN              0          NaN
Multiple multiple              NaN              1          NaN
 Swedish  swedish              NaN              2          NaN


- The code list has the following concepts information:
        - Concepts hierarchy depth: 1
        - Concepts hierarchy:
root
├── English
├── Multiple
└── Swedish
```

## Errors

There are a number of errors that can occur when inspecting a CSV-W; most of them are designed to help ensure you get correct and valid outputs.

Please see our documentation explaining a [number of common errors](../guides/errors/index.md) to see what you can do to diagnose and correct any errors which occur.

## Next

This is the end of the quick start section, however there is a lot more information available in the guides section; see the left-hand menu.

The next logic action to take with the Sweden at Eurovision data set is to learn how to [describe missing data](../guides/missing-observed-values.md) so we can include contestants who weren't able to perform.
