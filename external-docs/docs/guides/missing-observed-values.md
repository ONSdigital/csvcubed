# Handling missing observed values
Users may wish to avoid including particular observations within their data set. This may be done for many reasons including invalid or failed measurements, statistical suppression to avoid disclosing sensitive data, or simple missing observations because circumstances wouldn't permit an observation.

Csvcubed supports missing values so long as there is an observation status/marker column present which explains why the observed value is missing. This column must be an attribute column which either reuses an existing attribute column which reuses the `http://purl.org/linked-data/sdmx/2009/attribute#obsStatus` definition, or be a new attribute column which has from_existing of `http://purl.org/linked-data/sdmx/2009/attribute#obsStatus`. The observation which is missing must have the observation status filled in.

Blank values are represented as a zero length string in an observation column in csv format (i.e. `,,`).

## A worked example: Sweden in Eurovision

In the example below, which is an extract of a data set capturing Sweden's Eurovision entries, shows multiple uses of a Marker column which extends the `http://purl.org/linked-data/sdmx/2009/attribute#obsStatus` column. The number of people on the stage is known for Anna Bergendahl's entry into Eurovision as she comepted in second semi-final; however as she didn't make it to the final, her final-points, and final-rank are not applicable and therefore the observations are blank in the associated csv. In the case of The Mama's entry in 2020, the entire contest was cancelled so no values are provided however they were to represent Sweden at Eurovision that year.

Just because an obsStatus column has a value in it doesn't mean there must be no observation, obsStatus can also be used to note whether an observation is provisional, revised, suppressed, final, etc.

| Year | Entrant            | Song            | Language | Marker                    | Measure         | Observation | Units   |
|------|--------------------|-----------------|----------|---------------------------|-----------------|-------------|---------|
| 2008 | charlotte-perrelli | hero            | english  |                           | final-rank      | 18          | ordinal |
| 2010 | anna-bergendahl    | this-is-my-life | english  | did-not-qualify-for-final | final-rank      |             | ordinal |
| 2015 | mans-zelmerlow     | heroes          | english  |                           | final-rank      | 1           | ordinal |
| 2020 | the-mamas          | move            | english  | contest-cancelled         | final-rank      |             | ordinal |
| 2021 | tusse              | voices          | english  |                           | final-rank      | 14          | ordinal |
| 2008 | charlotte-perrelli | hero            | english  |                           | final-points    | 47          | points  |
| 2010 | anna-bergendahl    | this-is-my-life | english  | did-not-qualify-for-final | final-points    |             | points  |
| 2015 | mans-zelmerlow     | heroes          | english  |                           | final-points    | 365         | points  |
| 2020 | the-mamas          | move            | english  | contest-cancelled         | final-points    |             | points  |
| 2021 | tusse              | voices          | english  |                           | final-points    | 109         | points  |
| 2008 | charlotte-perrelli | hero            | english  |                           | people-on-stage | 5           | people  |
| 2010 | anna-bergendahl    | this-is-my-life | english  |                           | people-on-stage | 6           | people  |
| 2015 | mans-zelmerlow     | heroes          | english  |                           | people-on-stage | 6           | people  |
| 2020 | the-mamas          | move            | english  | contest-cancelled         | people-on-stage |             | people  |
| 2021 | tusse              | voices          | english  |                           | people-on-stage | 6           | people  |

The associated csv file would look like
```csv
Year,Entrant,Song,Language,Marker,Measure,Observation,Units
2008,charlotte-perrelli,hero,english,,final-rank,18,ordinal
2010,anna-bergendahl,this-is-my-life,english,did-not-qualify-for-final,final-rank,,ordinal
2015,mans-zelmerlow,heroes,english,,final-rank,1,ordinal
2020,the-mamas,move,english,contest-cancelled,final-rank,,ordinal
2021,tusse,voices,english,,final-rank,14,ordinal
2008,charlotte-perrelli,hero,english,,final-points,47,points
2010,anna-bergendahl,this-is-my-life,english,did-not-qualify-for-final,final-points,,points
2015,mans-zelmerlow,heroes,english,,final-points,365,points
2020,the-mamas,move,english,contest-cancelled,final-points,,points
2021,tusse,voices,english,,final-points,109,points
2008,charlotte-perrelli,hero,english,,people-on-stage,5,people
2010,anna-bergendahl,this-is-my-life,english,,people-on-stage,6,people
2015,mans-zelmerlow,heroes,english,,people-on-stage,6,people
2020,the-mamas,move,english,contest-cancelled,people-on-stage,3,people
2021,tusse,voices,english,,people-on-stage,6,people```

## Configuration of observation status in `qube-config.json`
Adding a Marker column to represent the observation status can be done in the column definitions section of the [qube-config](../quick-start/qube-config.md) file. In this example the Marker column has the following configuration:

```json
        "Marker": {
            "type": "attribute",
            "label": "Marker",
            "from_existing": "http://purl.org/linked-data/sdmx/2009/attribute#obsStatus"
        },
```
