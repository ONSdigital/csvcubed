# csvcubed - turn CSV files into linked data

## What is csvcubed?

The csvcubed project provides libraries and utilities which make it easier to turn a CSV into [5* linked data](https://5stardata.info/en/).

By publishing [5* linked data](https://5stardata.info/en/) and leveraging open standards for data, we believe that we can help ensure that statistical data is discoverable, comparable and analysable by automated tools. We hope that this standards-based approach will unlock network effects which accelerate data analysis by making it easier to collate, compare and contrast data from different sources.

## How do I get started?

See the [quick-start guide](./quick-start/index.md).

## I want to know more

csvcubed outputs [data cubes](https://en.wikipedia.org/wiki/Data_cube) using the [CSV on the web (CSV-W)](https://www.w3.org/TR/tabular-metadata/) file format. These CSV-W files contain your statistical data *with* the metadata necessary to describe what the data means, in context.

We make use of the following ontologies to describe cubes, code lists and catalogue metadata:

- [RDF Data Cube (qb)](https://www.w3.org/TR/vocab-data-cube/)
- [Simple Knowledge Organization System (SKOS)](http://www.w3.org/TR/skos-primer)
- [Data Catalog Vocabulary (DCAT2)](https://www.w3.org/TR/vocab-dcat-2/)

## Is this just about Open Data?

No! This isn't *just* about open data. We love open data but it isn't right for everything. We understand that some data contains disclosive or private information which shouldn't be published as open data. Our tools are designed to use open standards to enable you to create CSV-Ws which you can choose to publish or keep private.
 