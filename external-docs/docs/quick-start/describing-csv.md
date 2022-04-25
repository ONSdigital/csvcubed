# Describing a CSV

csvcubed makes it straightforward to describe your data. Important information to provide includes a title, a description, themes, publisher, and publication date.

This document assumes you have an existing CSV-W such as the `sweden_at_eurovision_no_missing.csv` data set created as in the [quick start build](./build.md).

**Experience of writing basic JSON documents is assumed throughout this document.** See this [tutorial from DigitalOcean](https://www.digitalocean.com/community/tutorials/an-introduction-to-json) for an introduction to writing JSON.

## Describing your data set

We recommend using [Visual Studio Code](https://code.visualstudio.com/) or another text editor which supports JSON schemas in order to use autocomplete on field names and values.

This is what a basic [`qube-config.json`](../guides/configuration/index.md) looks like:

```json
{
    "$schema": "https://purl.org/csv-cubed/qube-config/v1.0",
    "title": "Sweden at Eurovision",
    "summary": "List of Swedish entries to the Eurovision Song Contest since 1958.",
     "description": "Sweden has been competing in Eurovision since 1958, with an enviable track record of wins. This dataset covers all contests since 1958, their artists, the song names, language (if mono-lingual), and some observations covering points in final, rank in final, and number of artists on stage. Data originally sourced from https://en.wikipedia.org/w/index.php?title=Sweden_in_the_Eurovision_Song_Contest&oldid=1081060799 and https://sixonstage.com/",
    "license": "https://creativecommons.org/licenses/by/4.0/",
    "publisher": "https://www.ons.gov.uk",
    "dataset_issued": "2022-04-08T00:00:00Z",
    "keywords": [
        "Eurovision",
        "Song Contest",
        "Sweden",
        "European Broadcasting Union"
    ]
}
```

Note that there are three similar fields, `title`, `summary` and `description`:

* the `title` field contains a short human-readable identifier for the data set,
* the `summary` contains a single line of text summarising the data set,
* the `description` is a longer free-text field for a more thorough description.

All publishers are encouraged to provide license information in their CSV-W which permits data consumers to discover data which meets their use case.

You can now revisit the [build process](./build.md#passing-configuration) to provide the configuration file and generate a better described CSV-W cube.

## Next

The next step is to [link data](./linking-data.md).