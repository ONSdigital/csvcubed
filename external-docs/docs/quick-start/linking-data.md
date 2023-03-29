# Linking data

Linking data is what turns 4☆ data into [5☆ linked data](https://5stardata.info/en/). This guide will help users create their first linked data where your data reuses standard definitions.

## A transcribed audio screencast covering the contents of this page

<iframe src="https://share.descript.com/embed/WJeFEHVvAom" width="640" height="360" frameborder="0" allowfullscreen></iframe>

## Prerequisites

This page assumes that you have a well structured CSV with a corresponding JSON [qube-config.json](../guides/configuration/qube-config/index.md) as built in [describing your CSV](describing-csv.md).

## Column Mappings

We saw in the [describing your CSV](./describing-csv.md) section that we can provide a [qube-config.json](../guides/configuration/qube-config/index.md) configuration file to describe the data set. We can also use this file to describe columns.

```json
{
    "$schema": "https://purl.org/csv-cubed/qube-config/v1",
    "title": "Sweden at Eurovision",
    "summary": "List of Swedish entries to the Eurovision Song Contest since 1958.",
    "description": "Sweden has been competing in Eurovision since 1958, with an enviable track record of wins. This dataset covers all contests since 1958, their artists, the song names, language (if mono-lingual), and some observations covering points in final, rank in final, and number of artists on stage. Data originally sourced from https://en.wikipedia.org/w/index.php?title=Sweden_in_the_Eurovision_Song_Contest&oldid=1081060799 and https://sixonstage.com/",
    "license": "https://creativecommons.org/licenses/by/4.0/",
    "publisher": "https://www.ons.gov.uk",
    "dataset_issued": "2022-04-08",
    "keywords": [
        "Eurovision",
        "Song Contest",
        "Sweden",
        "European Broadcasting Union"
    ],
    "columns": {
        "Column Name": { ... column definitions ...}
    }
}
```

Note the newly added `columns` property which takes a key-value mapping for each CSV column that you wish to describe.

For example, in the `sweden_at_eurovision_no_missing.csv` data set we have been working with up to now, we could specify that the `Year` column should make use of the `year` [template](#column-templates):

```json
"columns": {
    "Year": {
            "from_template": "year"
        }
}
```

## Column Templates

Column templates are pre-configured column definitions which speed up creating linked data. csvcubed has several templates for columns converting calendar and UK Government time periods, as well as observation-status.

For more information see the [templates guide](../guides/configuration/qube-config/templates.md).

## Next steps

The next step is to [inspect your CSV-W](./inspect.md).
