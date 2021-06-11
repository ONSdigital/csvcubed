# csvwlib

A refactored version of the functionality required to build *CSV-qb*s along with the functionality necessary to convert said *CSV-qb*s into RDF compatible with the PMD platform.

## Packages

| Name   | Description                                                                                                      |
|:-------|:-----------------------------------------------------------------------------------------------------------------|
| models | Contains some models shared by the other libraries. Functionality in here should be kept to an absolute minimum. |
| pmd    | Contains functionality relating to PMD. i.e. this is functionality run as part of Jenkins build pipeline.        |

We're currently keeping all of the packages in one repository to make life easier whilst we break apart and refactor the existing code we have in [GSS-utils](https://github.com/GSS-Cogs/gss-utils). Once we're confident in how our packages look (and they're stable), it's likely that each individual package will be moved to its own independent repository. 

