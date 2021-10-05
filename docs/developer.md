# Developer Documentation

This document hopes to provide a central reference point for developers who plan to contribute towards the csvwlib project.

## Purpose

The csvwlib project aims to provide libraries and utilities which make it simple to turn a CSV into [5* linked data](https://5stardata.info/en/). We want to make it simpler for data producers to annotate their existing data with the metadata required to ensure that each dataset is discoverable, comparable and analysable by automated tools.

There are a number of ways that you can approach this problem. The csvwlib catalogue of tools help to deliver this vision in an opinionated fashion. Our tools output [data cubes](https://en.wikipedia.org/wiki/Data_cube) using the [CSV on the web (CSV-W)](https://www.w3.org/TR/tabular-metadata/) file format. Within these CSV-W files we describe what the data represents using a combination of the following ontology:

* [RDF Data Cube (qb)](https://www.w3.org/TR/vocab-data-cube/)
* [Simple Knowledge Organization System (SKOS)](http://www.w3.org/TR/skos-primer)
* [Data Catalog Vocabulary (DCAT2)](https://www.w3.org/TR/vocab-dcat-2/)

## Structure

* What packages do we have? What's their purpose?
* Why are there separate packages in the same repository?
* What's the primary use-case? Is csvqb a library to be used by other python projects or is it a command-line app in-and-of itself?
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
* briefly mention serialisation to RDF (real documentation to be done at a later point in time.) (NewResource, Annotated, etc.)

## Other Links

* CSV-W W3C documentation
* XSD data types documentation W3C
* RDF Data Cube W3C
