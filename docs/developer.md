# Developer Documentation

This document hopes to provide a central reference point for developers who plan to contribute towards the csvwlib project.

## Purpose

The csvwlib project aims to provide libraries and utilities which make it simple to turn a CSV into [5* linked data](https://5stardata.info/en/). We want to make it easier for data producers to annotate their existing data with the metadata required to ensure that each dataset is discoverable, comparable and analysable by automated tools.

There are a number of ways that you could approach this problem. The csvwlib catalogue of tools help to deliver this vision in an opinionated fashion. Our tools output [data cubes](https://en.wikipedia.org/wiki/Data_cube) using the [CSV on the web (CSV-W)](https://www.w3.org/TR/tabular-metadata/) file format. Within these CSV-W files we describe what the data represents using a combination of the following ontologies:

* [RDF Data Cube (qb)](https://www.w3.org/TR/vocab-data-cube/)
* [Simple Knowledge Organization System (SKOS)](http://www.w3.org/TR/skos-primer)
* [Data Catalog Vocabulary (DCAT2)](https://www.w3.org/TR/vocab-dcat-2/)

> Is this a library or a set of applications?

csvwlib is *initially* planned to be a series of command line applications which help users transform their data into qb-flavoured CSV-Ws with configuration provided by some form of declarative JSON/YAML file. This approach makes it easy for us to quickly deliver the tools that advanced users need, with the flexibility of configuration that will be necessary, without having to worry too much about providing a detailed user interface.

However, it's understandable that only a small number of users will be comfortable using command line applications which require hand-written JSON/YAML files, so it is envisioned that the project will act more as a set of libraries which can help more specialised tools generate valid qb-flavoured CSV-Ws.

In summary, csvwlib is a set of libraries which happen to contain some basic command line interfaces to help advanced users transform CSV data into qb-flavoured CSV-Ws.

## Python Packages

There are currently four individual packages which can be found inside the csvwlib repository. Each of these directories represents an independent python package in its own right:

```text
csvwlib
├── csvqb - The key library helping to transform tidy-data into qb-flavoured CSV-W cubes.
├── devtools - Shared test functionality & dev dependencies which are commonly required.
├── pmd - Transforms a CSV-qb into RDF which is compatible with the Publish My Data platform.
└── sharedmodels - Models and RDF serialisation functionality required by the csvqb and pmd packages.
```

> Why are there multiple packages in the same git repository?

We keep multiple packages in the same repository because it makes it easier to keep each package's dependencies in-sync with the others and ensures that it's simple for us to move functionality from one package to another if/when we decide that it's in the wrong place. This is a temporary step to make life easier whilst we're building up the project's foundations. It's likely that we'll restructure the packages in iterative process to find what the optimal package structure looks like. Once the project matures, we are likely to split these packages out in to separate repositories.

**N.B. you should only open one package at a time in your IDE/code editor.** Each package has its own poetry-driven virtual environment.

For more information about each individual package:

* [csvqb](../csvqb/csvqb/README.md)
* [pmd](../pmd/pmd/README.md)
* [sharedmodels](../sharedmodels/sharedmodels/README.md)
* [devtools](../devtools/devtools/README.md)

### File Structure

Each package has the following file/directory structure:

```text
PackageName (e.g. csvqb)
├── PackageName - (e.g. csvqb) all project python files go inside here.
│   ├── tests
│   │   ├── behaviour - Behave/cucumber tests go in here.
│   │   ├── test-cases - Test case example files go in here
│   │   └── unit - pytest unit tests go in here.
│   └── README.md - (optional) README file providing a summary of the package.
├── docs
│   └── conf.py - Configures the API Documentation generated.
├── poetry.lock - Locks all dependant packages (and transitive dependencies).
└── pyproject.toml - Specifies all dependant packages and configures project's output wheel.
```

* What packages do we have? What's their purpose?
* What's sharedmodels for?
* What's devtools for and what should I install in there?
* What's the pmd tool for?
* Discuss standard project directory structure (tests folder, etc.)
* Discuss complications when working inside the `.devcontainer` (specifically in vscode)

## Developer Tooling

### Build & Dependency Management

* poetry - for build dependency management
  * making use of PEP517 (pyproject.toml) for listing dependencies
  * no use of setup.py in sight!
* why it's an improvement over pipenv.
* Provide a link to the builds on Jenkins, and to the build file.
* Discuss the integration of the csvwlib project into gss-utils and hence databaker-docker.

### Code Style

* discuss use of the black formatter here.
* heavy use of object orientated programming?

### Static Type Checking

* what is static type checking and why should I care?
* pyright

### API Documentation

* sphinx - discuss use thereof
* Discuss what needs documentation and what style it should have. e.g. titles for every module
* Provide link to those helpful patterns like `:obj:module.path.to.obj`
* Discuss use of intersphinx mapping.
* Provide links to the latest API documentation generated on Jenkins.

### Unit and Integration Testing

* pytest
* behave tests
  * Need to have docker installed for this

## Packages & Patterns of Note

* discuss use of the python dataclasses functionality
  * Discuss functionality offered by `DataClassBase` in sharedmodels
* pydantic
  * discuss how we're using it in an a-typical way and why we're doing that.
  * discuss why we install it from a fork & how the upstream project may fix the underlying issue
* pandas - for supporting data input + writing to CSV
* rdflib
* briefly mention serialisation of metadata to RDF (real documentation to be done at a later point in time.) (NewResource, Annotated, etc.)

## Other Links

* CSV-W W3C documentation
* XSD data types documentation W3C
* RDF Data Cube W3C
* csvw-lint
* csv2rdf
