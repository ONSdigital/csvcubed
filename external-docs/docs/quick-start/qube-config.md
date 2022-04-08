# Qube Config

There are two approaches to use csvcubed to generate a valid statistical qube:

The [convention-first approach](../guides/qube-config.md#convention-first-method) allows you to create a cube with minimal or no configuration.  
The [configuration approach](../guides/qube-config.md#configuration) where you have the full power to configure your cube.

This quick-start provides an overview of how to configure your qube using the convention-first approach first then covers how to customise using the configuration approach. For detailed coverage of configuring a cube refer to the [Qube Config](../guides/qube-config.md) guide.

## Designing your CSV

The convention-first appraoch enables you to generate a CSV-W using just the csv file, this must be formatted according 
to the requirements.  This approach is useful as a starting point, however the configuration-first approach provides 
greater control over the cube configuration.

Requirements:

 * The first row must be the column titles and should use 
   [conventional column names](../guides/qube-config/#conventional-column-names)  
   Note: when a title does not conform to the conventional names it will be assumed to be a dimension column.

 * There must be, as a minimum, columns of type [dimension](../glossary/#dimension),
   [observations](../glossary/#observation-observed-value), [measures](../glossary/#measure), [units](../glossary/#unit).

 * The data must be structured in the [standard data shape](../guides/shape-data/#standard-shape).

 * All data row values must be populated.

Example Data:
The table below illustrates a sample data set that conforms to the above requirements. 

| Year | Location  | Value | Status      | Measure                    | Unit  |
| ---- | --------- | ----- | ----------- | -------------------------- | ----- |
| 2022 | London    | 35    | Provisional | Number of 'Arthur's Bakes' | Count |
| 2021 | Cardiff   | 26    | Final       | Number of 'Arthur's Bakes' | Count |
| 2020 | Edinburgh | 90    | Final       | Number of 'Arthur's Bakes' | Count |
| 2021 | Belfast   | 0     | Final       | Number of 'Arthur's Bakes' | Count |

Building:

When your data file conforms with the above requirements you can proceed to build the cube using the 
[build command](../guides/command-line/build-command.md)  
Run ``csvcubed build cube-data.csv``

This will generate the cube using the documented [inferences and assumptions](../guides/qube-config.md).

## Configuration-first method

Configuring the CSV-W output is done in such a way that the user is explicit in overriding the default values assumed 
by the csvcubed convention-first approach. Every value in the configuration of a cube has a default value, and if it is 
not overridden it is ether omitted as unnecessary for the production of valid CSV-W or the default value is used.

**JSON Schema**
The qube-config schema defines the permitted structure and content of a qube config json document and can be found at 
[https://purl.org/csv-cubed/qube-config/v1.0](https://purl.org/csv-cubed/qube-config/v1.0).

It is possible to use the JSON schema to provide both validation and contextual hints to help you when you write your 
qube-config.json files. This is a powerful piece of functionality which makes it easier to get your configuration files 
right before you try to combine the file with CSV data. It is therefore strongly recommended that you use a text editor 
which is able to validate JSON documents against schemas and provide contextual hints; the current recommended tool for
this is Visual Studio Code.

To enable validation and intellisense/contextual hints, you must start all qube-config.json v1.0 documents with the 
following $schema declaration:

    {
        "$schema": "https://purl.org/csv-cubed/qube-config/v1.0",
        ...
    }

The qube-config.json file has two sections.
1. **Metadata**
   This section is used to describe the data set's catalog information to aid discovery, provide provenance and  
   publication information, and optionally define the scope of the data set.
2. **Column Definitions**
   This section is used to describe each column in the `.csv` file, classifying the column and defining how the column 
   data is both represented and how it links semantically to other data.


**Basic Template:**
The following stands as a minimal template for a qube-config.json which you can use as a starting point for your own 
files. Note that only one column definition has been written for demonstration purposes.

    {
        "$schema": ""https://purl.org/csv-cubed/qube-config/v1.0",
        "id": "schema-id",
        "title": "Example Cube",
        "columns": {
            "A Column Title Present in the CSV": {
                "type": "dimension",
                "label": "Desired Column Label"
            },
        }
    }


**Basic Example Config:**
The following json is a very basic example config that would correspond to the sample convention data above, whilst
adding some Metadata properties to describe the cube and its provenance.

    {
        "$schema": "http://purl.org/csv-cubed/qube-config/v1.0",
        "title": "'Arthur's Bakes' stores in UK cities from 2020 to 2022",
        "description": "The number of 'Arthurs' Bakes' stores in cities across the UK between 2020 and 2022.",
        "creator": "HM Revenue & Customs",
        "publisher": "HM Revenue & Customs",
        "columns": {
            "Year": {
                "type": "dimension"
            },
            "Location": {
                "type": "dimension"
            },
            "Value": {
                "type": "observations"
            },
            "Status": {
                "type": "attribute"
            },
            "Measure": {
                "type": "measures"
            },
            "Unit": {
                "type": "units"
            }
        }
    }

Further properties for both the Metadata and Columns can be added to this sample, refer to the 
[Qube Config](../guides/qube-config.md) guide and / or [cube-config schema](https://purl.org/csv-cubed/qube-config/v1.0)
for further details on configuring the cube.
