# Raise an issue

## Report Bugs

If you find any bug in the code, please know that we welcome all contributions to our project even if you just report the bug.

Well written bug reports are very helpful. See this [Stackoverflow article](https://stackoverflow.com/help/minimal-reproducible-example) and this [blog post](https://matthewrocklin.com/blog/work/2018/02/28/minimal-bug-reports) for tips on writing minimal, reproducible examples. Please also keep in mind the following guidelines when reporting a new bug:

* Check the errors section of this documentation to see if your issue is addressed.
* Check the open issues to see if the bug has already been reported. If it has, check the ticket history and comments and feel free to leave additional useful information in comment form.
* Please format your report using the following template:
    1. Issue description
    2. Reproducible steps / Code example
    3. Error message obtained / Resulting behaviour
    4. Expected behaviour
    5. Any additional information
    6. Version information + Operating system

In the event that your issue can only be reproduced using sensitive information, please send your report to [IDPS.Dissemination@ons.gov.uk](mailto:IDPS.Dissemination@ons.gov.uk) and try to follow the template detailed above as closely as possible.

## Obtaining Error Logs

To obtain a detailed error log, please follow the following steps:

1. Set the logging level to debug in the build or inspect command respectively command. `[build/inspect] --log-level debug`
2. Rerun the issue causing lines.
3. Copy and paste the resulting console output into the bug reporting form.

**Note:** Logs from the past 7 days are recorded in csvcubed's log file `out.log`.
Feel free to consult these for more detailed retrospective debugging.

## Requesting Further Guidance

If you are having difficulties using csvcubed, please do not hesitate to submit a ticket to the issue tracker in the same manner as you would submit a bug report. A template has been put in place for this purpose. Before submitting a new ticket, please ensure you have read [our documentation guides](https://gss-cogs.github.io/csvcubed-docs/external/guides/) as well as checked the open issues, just in case your problem is bug related.
