# Logging

This page describes how the logging works for the build and inspect commands.

## Options

### `--log-level`

Allows you to set the level of messages that are logged with `debug` being the most verbose and `err` the least. The default level is `warn`, at this level you will see messages with a level of `warn`, `err` and `crit`.

If errors occur then setting the log level to `info` or `debug` will yield additional messages and details to help diagnose the issue.

```bash
csvcubed build --log-level debug my-data.csv
```

## Log output

Processing and validation messages are written to both console and a log file during processing of the cube build command. The verbosity of the logging is governed by the `--log-level` option. The log messages can be used to help identify and resolve issues that are experienced when building your cube.

The log path is dependant upon the operating system in-use, the following are typical paths, these may also be influenced by your system configuration.

| Operating System | Typical Log Path                                                       |
| ---------------- | ---------------------------------------------------------------------- |
| **Windows**      | `C:\Users\[UserName]\AppData\Local\csvcubed\csvcubed-cli\Logs\out.log` |
| **Linux**        | `/home/[UserName]/.cache/csvcubed/csvcubed-cli/Logs/out.log`           |
| **MacOS**        | `/home/[UserName]/Library/Logs/csvcubed/csvcubed-cli/Logs/out.log`     |

## Log retention

A new log file is created daily, with backups being saved for 7 days in the same location. The older logs are overwritten in a cyclic manner with the oldest being replaced first.
