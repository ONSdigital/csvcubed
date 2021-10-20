# csvwlib

A refactored version of the functionality required to build *CSV-qb*s along with the functionality necessary to convert said *CSV-qb*s into RDF compatible with the PMD platform.

## Packages

| Name     | Description                                                                                                                                          |
|:---------|:-----------------------------------------------------------------------------------------------------------------------------------------------------|
| models   | Contains some models shared by the other libraries. Functionality in here should be kept to an absolute minimum.                                     |
| pmd      | Contains functionality relating to PMD. i.e. this is functionality run as part of Jenkins build pipeline.                                            |
| devtools | Tooling used in the development and maintenance of the csvwlib tooling. Currently contains tooling necessary to standardise testing across packages. |

We're currently keeping all of the packages in one repository to make life easier whilst we break apart and refactor the existing code we have in [GSS-utils](https://github.com/GSS-Cogs/gss-utils). Once we're confident in how our packages look (and they're stable), it's likely that each individual package will be moved to its own independent repository. 

## Synchronising Pipfile with Setup.py

Since we're creating python packages here, we need to use the setup.py to specify all of the package's dependencies so that whoever installs our package ensures they install the dependencies too. There's a tool called `pipenv-sync` that will help us with this task by looking at the Pipenv file and setting the corresponding dependencies in the `setup.py` file.

Simply navigate to the package's directory, run `pipenv shell` and then run `pipenv-setup sync` inside the package's pipenv environment. This should automatically update `setup.py` with any new non-dev packages that you've installed.
