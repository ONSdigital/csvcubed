# csvcubed

A refactored version of the functionality required to build *CSV-qb*s along with the functionality necessary to convert said *CSV-qb*s into RDF compatible with the PMD platform.

## Packages

| Name                                                                | Description                                                                         |
|:--------------------------------------------------------------------|:------------------------------------------------------------------------------------|
| [csvcubed](./csvcubed/csvcubed/README.md)                           | The key library helping to transform tidy-data into qb-flavoured CSV-W cubes.       |
| [csvcubed-models](./csvcubed-models/csvcubedmodels/README.md)       | Models and RDF serialisation functionality required by the csvcubed and csvcubed-pmd packages.  |
| [csvcubed-pmd](./csvcubed-pmd/csvcubedpmd/README.md)                | Transforms a CSV-qb into RDF which is compatible with the Publish My Data platform. |
| [csvcubed-devtools](./csvcubed-devtools/csvcubeddevtools/README.md) | Shared test functionality & dev dependencies which are commonly required.           |

We're currently keeping all of the packages in one repository to make life easier whilst we break apart and refactor the existing code we have in [GSS-utils](https://github.com/GSS-Cogs/gss-utils). Once we're confident in how our packages look (and they're stable), it's likely that each individual package will be moved to its own independent repository.

## Developer Documentation

More detailed developer documentation for this project can be found [here](./docs/developer.md).
