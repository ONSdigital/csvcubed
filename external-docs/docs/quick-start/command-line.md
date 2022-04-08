# Command Line Interface (CLI)

csvcubed provides a command line interface (CLI) than can be used to build a new cube and inspect an existing cube.

To install csvcubed follow the [quickstart](installation.md).

## Commands

For details of these commands proceed to the following pages:

* [build](../guides/command-line/build-command.md)
* [inspect](../guides/command-line/inspect-command.md)

### `build`

The `build` command is used to generate CSV-W from csv files, you can use it with or without a configuration file to generate [configured](../guides/qube-config.md#configuration) or [conventional](../guides/qube-config.md#convention-first-method) cubes respectively. To add a configuration file the `-c` argument is used to point to a `qube-config.json` file.

```bash
csvcubed build observations.csv [-c qube-config.json]
```

For more information see the [detailed guide](../guides/command-line/build-command.md)

### `inspect`

The `inspect` command is used to list the contents of csvcubed-generated CSV-W. Is it can be used against code-lists and CSV-Ws and is useful to visually check that the serialisation of CSV-W meets your expectations.

```bash
csvcubed inspect out/observations.csv-metadata.json
```

For more information see the [detailed guide](../guides/command-line/inspect-command.md)
