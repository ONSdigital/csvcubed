# Cube Config Column Templates

This directory contains a number of JSON files containing templates which can be reused/extended by users of the qube-config.json csvcubed interface.

## How it works

The [preset_column_config.json](./preset_column_config.json) is an index of all of the templates available mapping from identifier to the JSON file containing the template column definition. If your template is not indexed in this file then it will not work in csvcubed.

**N.B. if you add a new template (with file) into this directory, you must ensure you update all appropriate qube-config.json schemas to ensure the enum of column_template values contains your new template**. If you don't do this then your user will experience schema validation errors when attempting to use your template; in addition, the user won't get the intellisense/auto-completion in IDEs which help the select the right template.
