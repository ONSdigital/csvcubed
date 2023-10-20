# csvcubed

csvcubed project provides a command line tool which make it straightforward to turn a CSV into 5-star linked data (CSV-W)

By publishing 5-star linked data and leveraging open standards for data, we believe that we can help ensure that statistical data is discoverable, comparable and analysable by automated tools. We hope that this standards-based approach will unlock network effects which accelerate data analysis by making it easier to collate, compare and contrast data from different sources.

All our work depends on open standards; however it isn't just for open data. Share your data with the world or keep it private, the choice is yours.

## Getting started immediately

Get going with csvcubed immediately by installing csvcubed using pip.

```bash
pip install csvcubed
```

From there you'll have access to the `csvcubed` command line tool which features sub commands `build` and `inspect` to create CSV-Ws from CSV and inspect CSV-Ws.

Become well acquainted to csvcubed with our [quick start](https://gss-cogs.github.io/csvcubed-docs/external/quick-start/), which includes written instructions as well as transcribed videos.

## User Documentation

csvcubed has extensive user documentation which tracks the release of csvcubed while it is in its beta phase. Our [documentation](https://gss-cogs.github.io/csvcubed-docs/external/) can always be improved, so treat bad docs as a bug report.

## Related Packages

| Name                                                               | Description                                                                                    |
| :----------------------------------------------------------------- | :--------------------------------------------------------------------------------------------- |
| [csvcubed](./README.md)                                            | The key library helping to transform tidy-data into qb-flavoured CSV-W cubes.                  |
| [csvcubed-models](https://github.com/gss-Cogs/csvcubed-models)     | Models and RDF serialisation functionality required by the csvcubed and csvcubed-pmd packages. |
| [csvcubed-pmd](https://github.com/gss-Cogs/csvcubed-pmd)           | Transforms a CSV-qb into RDF which is compatible with the Publish My Data platform.            |
| [csvcubed-devtools](https://github.com/gss-Cogs/csvcubed-devtools) | Shared test functionality & dev dependencies which are commonly required.                      |

## Developer Documentation

More detailed developer documentation for this project can be found [here](https://github.com/GSS-Cogs/csvcubed/blob/main/docs/developer.md).

## How to report bugs

We welcome and appreciate bug reports. As we are trying to make this tool useful for all levels of experience, any level of bug or improvement helps others. To contribute to making csvcubed better, check out our [bug reporting instructions](https://gss-cogs.github.io/csvcubed-docs/external/guides/raise-issue/).
