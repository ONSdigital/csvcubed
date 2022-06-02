# csvcubed

> Generate linked data cubes using skos and qb-flavoured CSV-Ws.

The `csvcubed` package is a library which generates qb-flavoured CSV-W files and associated SKOS-flavoured CSV-W code-lists. It provides an API which allows the specification of a given cube's structure and data, provides validation errors to guide users where they make common mistakes and outputs valid CSV-qb files. The API is not designed to be used by data producers themselves, but is to be used by specialised user interfaces targeted towards specific segments of the data producer population. i.e. A simpler wizard-style application may be most suitable for less advanced data publishers, whilst an API-style app may be suitable for more advanced users who require a greater degree of configurability.

## Future Plans

It is anticipated that csvcubed will soon have a command line interface which accepts some form of JSON/YAML configuration file along with a [tidy-data](https://doi.org/10.18637/jss.v059.i10) CSV and generates skos and qb-flavoured CSV-W outputs. This will be the initial user interface most suited to more advanced statistical producers.

## API Documentation

The latest API Documentation for the package can be found [here](https://ci.floop.org.uk/job/GSS_data/job/csvwlib/job/main/lastSuccessfulBuild/artifact/csvcubed/docs/_build/html/index.html).

TODO: #215 Update uri on build location in csvcubed/README.md

## Further Links

* [Using the Qb classes / Defining a QbCube](./models/cube/qb/README.md).
