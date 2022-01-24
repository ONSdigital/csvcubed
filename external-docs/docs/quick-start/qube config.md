# `qube-config.json`

The `qube-config.json` file is a mechanism for expressing the configuration of a CSV-W for use by csvcubed's methods and command line interface. It is comprised of two main parts, the catalogue information (i.e. metadata) and the column definitions. Users naming columns in their `.csv` files with reserved names allows for producing RDF Cube Vocabulary-targetted CSV-W with less configuration.

## Qube configuration overview

There are four steps, some of which are optional for generating a CSV-W using csvcubed. Depending whether the input `.csv` file is configured to use conventional column names, a compainion `qube-config.json` may not even be required.



```mermaid
graph LR
	subgraph "Fastest Qube"
		A(Start) ==> B[1. Define metadata];
		B ==> C{"Column names"};
		C == Convention ==> D{"Custom RDF"};
		D == No ==> E;
	end
	subgraph "Custom Qube"
		C -- Configuration --> 1["2. Define columns"] --> D;
		D -- Yes --> 2["3. Define custom RDF"] --> E;
	end
	
	E["4. Generate CSV-W"] ==> F(End);
```

1. **Define metadata** (Optional)
   Provide information about the CSV-W's contents, such as title, publication date, description, and scope (e.g. start and end date of a time series)
2. **Define columns** (Optional)
   csvcubed has sensible defaults including the assumption that all columns are dimensions unless they have a reserved name (See: [Conventional column names for input `.csv` files](#Conventional column names for input `.csv` files))
3. **Define custom RDF** (Optional)
   Custom RDF can be used to declare additional triples attached to the data set, or individual columns **TODO:** Further detail
4. **Generate CSV-W**
   Run `csvcubed build tidy_data.csv (-c qube-config.json)` to generate a CSV-W

# Getting started

There are two ways to configure csvcubed using the `qube-config.json` file. Convention requires a tidy data `.csv` file and specific column names. Configuration simplifies the coining of new or child components.

1. **Configuration approach**
   Start with a blank `.json` file and providing a key-value of `"$schema": "./cube-config.schema.json"` to be prompted by your IDE of choice for how to build a valid `qube-config.json` file. (TODO: Update to contian the correct schema url)
2. **Convention approach**
   Use the csvcubed CLI to generate a `qube-config.json` file from a target csv file where columns are named according to convention.

## Convention method

The conventions used in generating a csvcubed-flavoured CSV-W involve a series of assumptions. These assumptions are always present, even if a configuration approach is used. A summary of the assumptions made by csvcubed are as follows; however for further detail see here. **TODO:** do this thing.

* The title of the cube is the name of the csv file in capital case with underscores replaced by spaces
* Every column that doesn't have a reserved name is a new dimension which is local to the data set
* The title of the new dimensions is the capital case of the column header with the underscores replaced by spaces; the uri-safe value for the column is the lowercase, a corresponding SKOS concept scheme and code list is created using the unique values in the dimension column
* Observation values are in the observation column and are decimal values
* Meausres are in the measure column, and new measures are created using the unique values in the column unless a URI is present, when that uri is assumed to point to an existing measure
* Units are in the unit column, and new units are created using the unique values in the column unless a URI is present, when that uri is assumed to point to an existing unit

### Conventional column names for input `.csv` files

As stated earlier in the summary csvcubed assumes that all columns are dimensions unless otherwise specified. This allows for faster configuration of a `qube-config.json` file; however the result will not be valid unless the user names their `.csv` file columns in a specific way. The column names are not case sensitive, and only one of measure, observation, and unit column can exist per `.csv` file.

| Component type     | Reserved names                                               | Resulting configuration                                      |
| ------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Dimension          | `none`                                                       | A new dimension with the label of the csv column as its title |
| Measure Column     | Measure, measures, measures column, measure column, measure type, measure types | A new measure column with the values within the measure column as new measures unless the values are uris, when csvcubed will assume these are existing measures |
| Observation Column | Observations, obs, values, value, val, vals                  | A new observation column with the values in this column; the data type of this column must be numeric and csvcubed assumes `xsd:decimal` |
| Unit Column        | Unit, units, units column, unit column, unit type, unit types | A new unit column with the values within the unit column as new units unless the values are uris, when csvcubed will assume these are existing units |

A valid `.csv` file must have a column of every type as above in order for it to be valid for conversion to CSV-W by csvcubed by using convention over configuration. All the assumptions and rules (excepting using reserved names for other component types) are overridable by the user in the `qube-config.json` file

## Configuration

Configuring the CSV-W output is done in such a way that the user is explicit in overriding the default values assumed by csvcubed. Every value in the configuration of a cube has a default value, and if it is not overriden it is ether omitted as unnecessary for the production of valid CSV-W or the default value is used.

The `qube-config.json` file has two sections.

1. **Metadata**
   This section is used to describe the dataset's catalog information to aide discovery, provide provinance and publication information, and optionally define the scope of the data set
2. **Define columns**
   This section is used to describe each column in the `.csv` file, classifying the column and defining how the column data is both represented and how it links semantically to other data

## Metadata

A CSV-W file contains metadata which improves discoverability of data publications. In csvcubed, we use a selection of metadata entries from established namespaces to enable users to contribute to the web of data faster. The metadata fields available, their description and defaults are as follows.

| **field name**   | **description**                                              | **default value**                           |
| ---------------- | ------------------------------------------------------------ | ------------------------------------------- |
| `title`          | the title of the cube                                        | A capital case version of the csv file name |
| `description`    | a description of the contents of the cube                    | *none*                                      |
| `publisher`      | a link to the publisher of the cube                          | *none*                                      |
| `creator`        | a link to the creator of the cube                            | *none*                                      |
| `theme`          | a list or a single string of the theme(s) covered by the data (i.e. "trade", "energy", "imports") | *none*                                      |
| `spatial_bound`  | URI that defines the spatial / geographic bounds of the data contained herein | *none*                                      |
| `temporal_bound` | URI that defines the temporal bounds of the data contained herein | *none*                                      |

## Column definitions

A CSV-W file provides detailed information about the columns beyond their values. In csvcubed, we are targeting a level of detail which results in a data cube which can be be expressed using W3C's RDF Cube Vocabulary. A data cube must have a dimension, measure, unit, and observation column to be valid. A cube may also have one or more attribute columns which provide clarification to observational data.

To define a column in a `qube-config.json` file, provide the column header's value as a dictionary key, and create a new dictionary.

A column is assumed to be a dimension unless otherwise configured using the `type` key or the column being named one of the reserved names. A dimension can still have a `"type": "dimension"` key/value pair.

```json
{ ...
 "columns": {
  "Example column": {
    "type": "dimension"
  }
 }
}
```

 ### Choosing the correct column type

Adapted from W3C's RDF Cube Vocabulary Recommendation, selecting the correct column type begins the definition of a column.

> The *dimension* [column] serve[s] to identify the observations. A set of values for all the dimension components is sufficient to identify a single observation. Examples of dimensions include the time to which the observation applies, or a geographic region which the observation covers.

> The *measure* [column] represent[s] the phenomenon being observed.

> The *attribute* [column] allow us to qualify and interpret the observed value(s). They enable specification of the units of measure, any scaling factors and metadata such as the status of the observation (e.g. *estimated*, *provisional*).

The *unit* component is a type of attribute which provides the units of the observation.

The *observation* column are the numeric values of the observation being recorded in the data set.

### Using existing columns

To reuse or extend existing dimensions, attributes, units, or measures, provide a `"from_existing": "uri"` key-value pair linking to the RDF subject for the component specification. Unless the component being reused is literal attribute and you're providing a `"data_type"` key-value pair, any other key-value pairs provided will change the column to a new component which will extend the linked parent component.
