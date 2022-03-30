# Command Line

## build command
The build command is used to construct a new Qube from its source file(s).  

The source files must include a tidy-data.csv and optionally a cube-config.json.  
Refer to the [qube-config quickstart](./qube-config.md) for an overview of how to construct these files.


**Syntax:**  
``csvcubed build [OPTIONS] TIDY_CSV_PATH``

**Arguments:**

| Argument      | Description                                                     |
|---------------|-----------------------------------------------------------------|
| TIDY_CSV_PATH | The file path to the cube data file, formatted as tidy data csv |

**Options:**

| Option                       | Description                                                                                           |
|------------------------------|-------------------------------------------------------------------------------------------------------|
| --help / -h                  | Show the command help text.                                                                           |
| --config / -c                | The file path for the cube configuration json file.                                                   |
| --out / -o                   | The output directory path where the build output is written. The default is './out'                    |
| --ignore-validation-errors   | Set this option to continue building the cube when errors are found.                                  |
| --validation-errors-to-file  | Save validation errors to `validation-errors.json` in the output directory.                           |
| --log-level                  | Set the desired logging level to one of 'err', 'warn', 'crit', 'info', 'debug'. The default is 'warn' |

### Logging:
Processing and validation messages are written to both console and a log file during processing of the cube build command.  
The --log-level option allows you to set the level of messages that are logged with 'debug' being the most verbose and 'err' the least.

This information can be used to help resolve issues that are experienced when building your cube.
Passing the --validation-errors-to-file option may also help as further information on the error is written.

A new log file is created daily, with backups being saved for 7 days before being overwritten in a cyclic manner with the oldest being replaced.

The log path is dependant upon the operating system in-use, the following are typical paths, these may also be 
influenced by your system configuration.

| Operating System | Typical Log Path                                                     |
|------------------|----------------------------------------------------------------------|
| **Windows**      | C:\Users\[UserName]\AppData\Local\csvcubed\csvcubed-cli\Logs\out.log | 
| **Linux**        | /home/[UserName]/.cache/csvcubed/csvcubed-cli/Logs/out.log           |
| **MAC**          | /home/[UserName]/Library/Logs/csvcubed/csvcubed-cli/Logs/out.log     |

### Output Directory:
The output directory path can be specified using the -o or --out option.
It is optional and if omitted defaults to './out' subdirectory of the current path.

### Validation Errors:
Setting the --validation-errors-to-file option will result in validation errors being written to the `validation-errors.json`
file in the output directory.  If there are no validation errors the file is not written.

When errors are encountered refer to the [Validation errors guide](../guides/errors/index.md) for help on understanding and resolving them

**Build Command Errors:**

| Error                                                                                                                       | Description                                                                            |
|-----------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------|
| Missing argument 'TIDY_CSV_PATH'.                                                                                           | A data file path was not provided as a build command argument                          |
| PermissionError: [Errno 13] Permission denied: 'source'                                                                     | The data file path provided was a directory not a file. |
| Invalid value for 'TIDY_CSV_PATH': Path '.\\source\\cube_data.xlx' does not exist.                                          | The data file path was not found |
| UnicodeDecodeError: 'utf-8' codec can't decode bytes in position 15-16: invalid continuation byte                           | The data file was not a csv file |
| ValueError: The $schema 'http://purl.org/csv-cubed/qube-config/v2.0' referenced in the cube config file is not recognised. | The URI for the cube-config reference schema was incorrect or does not match an approved schema URI |
| 


## Examples:

### Getting help for the build command
``csvcubed build --help``

> Usage: csvcubed build [OPTIONS] TIDY_CSV_PATH
> 
>  Build a qb-flavoured CSV-W from a tidy CSV.
> Options:
  -c, --config CONFIG_PATH        Location of the json file containing the qube-config file.
> 
>  -o, --out OUT_DIR              Location of the CSV-W outputs.  [default: ./out]
>
>  --fail-when-validation-error / --ignore-validation-errors
                                  Fail when validation errors occur or ignore validation errors and continue generating a CSV-W.  [default: fail-when-validation-error]
>
>  --validation-errors-to-file    Save validation errors to a `validation-errors.json` file in the output directory. [default: False]
>
>  --log-level [warn|err|crit|info|debug]
>                                 Select a logging level out of: 'warn','err', 'crit', 'info' or 'debug'.
>
>  -h, --help                     Show this message and exit.

### Building a cube from data
To build a cube using only a csv data file. For guidance on the correct data structure refer to the
[Shaping your data](../guides/shape-data.md) guide, the 'canonical approach' is recommended to begin with. 

``csvcubed build "./source/cube_data.csv"``

> Build Complete

Indicates that a cube was created and was written to the default output directory of ./out

### Building a cube from data and configuration file.
To build a cube using both configuration and data files the command is shown below.
The cube config json file must comply with the [cube config schema](https://purl.org/csv-cubed/qube-config/v1.0), 
refer to the [Configuration Guide]("../guides.qube-config/#configuration") for help on constructing the json.  

``csvcubed build --config="./source/cube_config.json" "./source/cube_data.csv"``

> Build Complete

Indicates that a cube was created and written to the default output directory of "./out".


``csvcubed build --log-level=info --ignore-validation-errors --out="./out/example_output" --config="./source/cube_config.json" "cube_data.csv"``