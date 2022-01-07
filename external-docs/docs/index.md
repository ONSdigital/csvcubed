# Welcome to MkDocs

For full documentation visit [mkdocs.org](https://www.mkdocs.org).

## The Prject
### What the Project is about

The csvcubed project aims to provide libraries and utilities which make it simple to turn a CSV into 5* linked data. We want to make it easier for data producers to annotate their existing data with the metadata required to ensure that each dataset is discoverable, comparable and analysable by automated tools.

There are a number of ways that you could approach this problem. The csvcubed catalogue of tools help to deliver this vision in an opinionated fashion. Our tools output data cubes using the CSV on the web (CSV-W) file format. Within these CSV-W files we describe what the data represents using a combination of the following ontologies:

RDF Data Cube (qb)
Simple Knowledge Organization System (SKOS)
Data Catalog Vocabulary (DCAT2)
Is this a library or a set of applications?
csvcubed is initially planned to be a series of command line applications which help users transform their data into qb-flavoured CSV-Ws with configuration provided by some form of declarative JSON/YAML file. This approach helps us quickly deliver the tools that advanced users need, with the flexibility of configuration that will be necessary, without having to worry too much about providing a detailed user interface.
### What it's useful for

It's understandable that only a small number of users will be comfortable using command line applications which require hand-written JSON/YAML files, so it is envisioned that the project will act more as a set of libraries which can help more specialised tools generate valid qb-flavoured CSV-Ws.

In summary, csvcubed is a set of libraries which happen to contain some basic command line interfaces to help advanced users transform CSV data into qb-flavoured CSV-Ws.