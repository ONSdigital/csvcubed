# code-list build command

The code-list build command is used to construct a new code list from a JSON configuration file without the need of a tidy-data.csv file

The only source file neccessary is a JSON configuration file. Refer to the [code-list-config guide](../configuration/code-list-config.md) for an overview of how to construct these files.

**Syntax:**
``csvcubed code-list build [OPTIONS] CODE-LIST-CONFIG-JSON-FILE``

**Arguments:**

| Argument                   | Description                                |
| -------------------------- | ------------------------------------------ |
| CODE-LIST-CONFIG-JSON-FILE | The file path to the code list config JSON |


**Options:**

| Option                      | Description                                                                                                     |
| --------------------------- | --------------------------------------------------------------------------------------------------------------- |
| --help / -h                 | Show the command help text.                                                                                     |
| --out / -o                  | The output directory path where the build output is written. The default is './out'                             |
| --ignore-validation-errors  | Set this option to continue building the code list when errors are found.                                       |
| --validation-errors-to-file | Save validation errors to `validation-errors.json` in the output directory.                                     |
| --log-level                 | Set the desired logging level to one of 'crit', 'err', 'warn', 'info' and 'debug'.  <br/> The default is 'warn' |


## Saving Validation Errors

### `--validation-errors-to-file`

Setting this flag will result in any validation errors being written to the `validation-errors.json` file in the [output directory](#output-directory).  If no errors are encountered then the file is not written.

## Log Level and Log File Location

Please refer to the [Logging](./logging.md) section for information on how to configure the log-level and the location of log files.

## Output Directory

### `--out` / `-o`

When the code list is built the default output path is `./out`. This may be changed by setting output option to an alternative path.


## Examples

### Building a code-list

To build a code list you must only provide a code-list config JSON file.

The code list config JSON file must adhere to the structures defined in the [code list config schema](https://purl.org/csv-cubed/code-list-config/v1.1).

For help on constructing the code-list config JSON refer to the [code-list-config guide](../configuration/code-list-config.md)

To build a code list, the command is shown below.

```bash
csvcubed code-list build /source/code_list_config.json
```
