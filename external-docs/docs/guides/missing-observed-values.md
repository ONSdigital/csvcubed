# Handling missing observed values

It is sometimes the case that you cannot provide a value for a given [observation](../glossary/index.md#observation-observed-value) but you would still like to include the observation in the dataset to communicate why the value is missing. This could be for a number of reasons such as invalid or failed measurements, suppression to avoid disclosing sensitive data, or because circumstances wouldn't permit an observation.

csvcubed permits missing observation values as long as there is an _attribute_ column which explains why the value is missing. The _attribute_ column must be based on the `http://purl.org/linked-data/sdmx/2009/attribute#obsStatus` attribute. The observation which is missing must have the observation status filled in.

Blank values are represented as a zero length string in an observation column in csv format (i.e. `,,`).

## A worked example: Sweden in Eurovision

In the example below, which is an extract of a data set capturing Sweden's Eurovision entries, we see a Marker column which is used to explain why a the given row's observed value is missing. 

For example: 

* the number of People on the stage is known for Anna Bergendahl's entry into Eurovision as she comepted in second semi-final; however as she didn't make it to the final, her Final Points, and Final Rank are not applicable and therefore the observations are blank in the associated csv. 
* in the case of The Mama's entry in 2020, the entire contest was cancelled so no values are provided however they were to represent Sweden at Eurovision that year.

It is important to note that the `Marker` column is based on the existing `http://purl.org/linked-data/sdmx/2009/attribute#obsStatus` attribute; this is vital to ensure that csvcubed knows that the attribute describes the status of the observation. An observation status column can also be used to note where an observation is provisional, revised, suppressed, final, etc.

| Year | Entrant            | Song            | Language | Marker                    | Measure         | Observation | Units   |
|------|--------------------|-----------------|----------|---------------------------|-----------------|-------------|---------|
| 2008 | Charlotte Perrelli | Hero            | English  |                           | Final Rank      | 18          | Ordinal |
| 2010 | Anna Bergendahl    | This is my Life | English  | Did not Qualify for Final | Final Rank      |             | Ordinal |
| 2015 | Mans Zelmerlow     | Heroes          | English  |                           | Final Rank      | 1           | Ordinal |
| 2020 | The Mamas          | Move            | English  | Contest Cancelled         | Final Rank      |             | Ordinal |
| 2021 | Tusse              | voices          | English  |                           | Final Rank      | 14          | Ordinal |
| 2008 | Charlotte Perrelli | Hero            | English  |                           | Final Points    | 47          | Points  |
| 2010 | Anna Bergendahl    | This is my Life | English  | Did not Qualify for Final | Final Points    |             | Points  |
| 2015 | Mans Zelmerlow     | Heroes          | English  |                           | Final Points    | 365         | Points  |
| 2020 | The Mamas          | Move            | English  | Contest Cancelled         | Final Points    |             | Points  |
| 2021 | Tusse              | voices          | English  |                           | Final Points    | 109         | Points  |
| 2008 | Charlotte Perrelli | Hero            | English  |                           | People on Stage | 5           | People  |
| 2010 | Anna Bergendahl    | This is my Life | English  |                           | People on Stage | 6           | People  |
| 2015 | Mans Zelmerlow     | Heroes          | English  |                           | People on Stage | 6           | People  |
| 2020 | The Mamas          | Move            | English  | Contest Cancelled         | People on Stage |             | People  |
| 2021 | Tusse              | voices          | English  |                           | People on Stage | 6           | People  |

The associated csv file would look like:

```csv
Year,Entrant,Song,Language,Marker,Measure,Observation,Units
2008,Charlotte Perrelli,Hero,English,,Final Rank,18,Ordinal
2010,Anna Bergendahl,This is my Life,English,Did not Qualify for Final,Final Rank,,Ordinal
2015,Mans Zelmerlow,Heroes,English,,Final Rank,1,Ordinal
2020,The Mamas,Move,English,Contest Cancelled,Final Rank,,Ordinal
2021,Tusse,voices,English,,Final Rank,14,Ordinal
2008,Charlotte Perrelli,Hero,English,,Final Points,47,Points
2010,Anna Bergendahl,This is my Life,English,Did not Qualify for Final,Final Points,,Points
2015,Mans Zelmerlow,Heroes,English,,Final Points,365,Points
2020,The Mamas,Move,English,Contest Cancelled,Final Points,,Points
2021,Tusse,voices,English,,Final Points,109,Points
2008,Charlotte Perrelli,Hero,English,,People on Stage,5,People
2010,Anna Bergendahl,This is my Life,English,,People on Stage,6,People
2015,Mans Zelmerlow,Heroes,English,,People on Stage,6,People
2020,The Mamas,Move,English,Contest Cancelled,People on Stage,3,People
2021,Tusse,voices,English,,People on Stage,6,People
```

## Configuration of observation status in `qube-config.json`

Adding a Marker column to represent the observation status can be done in the column definitions section of the [qube-config](../quick-start/qube-config.md) file. In this example the Marker column has the following configuration:

```json
        "Marker": {
            "type": "attribute",
            "label": "Marker",
            "from_existing": "http://purl.org/linked-data/sdmx/2009/attribute#obsStatus"
        },
```
