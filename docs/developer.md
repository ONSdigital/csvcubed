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

We keep multiple packages in the same repository because it makes it easier to keep each package's dependencies in-sync with the others and ensures that it's simple for us to move functionality from one package to another if/when we decide that it's in the wrong place. This is a temporary step to make life easier whilst we're building up the project's foundations. It's likely that we'll restructure the packages in an iterative process to find what the best package structure looks like. Once the project matures, we are likely to split these packages out in to separate repositories.

**N.B. you should only open one package at a time in your IDE/code editor.** Each package has its own poetry-driven virtual environment.

More information about each individual package can be found here:

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

## Developer Tooling

### Build & Dependency Management

[Poetry](https://python-poetry.org/) - We use poetry to manage the packages we install via pip. It does the same job as [pipenv](https://pipenv.pypa.io/en/latest/) and the commands are fairly similar, however we've measured poetry at being ~8x faster than pipenv when performing comparable tasks. Using poetry, we can make use of the [PEP517](https://www.python.org/dev/peps/pep-0517/) pyproject.toml file so that we no longer need a [setup.py](https://docs.python.org/3/distutils/setupscript.html) file.

[Jenkins](https://ci.floop.org.uk/job/GSS_data/job/csvwlib/) - We use Jenkins as the build & test server for the whole project. There is a single [Jenkinsfile](../Jenkinsfile) which builds, tests, packages and generated API documentation for each project in a consistant fashion. Each Jenkins build produces one wheel per project. These wheels are what will eventually be uploaded to [pypi](https://pypi.org/) but [can be installed manually with pip](https://pip.pypa.io/en/stable/user_guide/#installing-from-wheels).

### Code Style

Layout - In terms of layour of code, we use the [black](https://black.readthedocs.io/en/stable/) formatter. This formatter can be installed in both [pycharm](https://black.readthedocs.io/en/stable/integrations/editors.html#pycharm-intellij-idea) and [vscode](https://black.readthedocs.io/en/stable/integrations/editors.html#visual-studio-code). All files should be formatted with black before being committed to source control.

#### Static Types

[Static type annotations](https://docs.python.org/3/library/typing.html) have been supported in python, since version 3.5, as defined in [PEP484](https://www.python.org/dev/peps/pep-0484/). Static type annotations *should* be added to **all** functions to specify the datatypes of all input parameters and the function's return type. Static types are a great addition to python which help us uncover bugs and ship more reliable software.

Every Jenkins build runs [pyright](https://github.com/Microsoft/pyright) which inspects all type annotations and **enforces** agreement - i.e. it will ensure that your build fails when you pass the wrong datatype to a function. You can install pyright locally to fix any problems before you commit to source control.

```bash
brew install node && npm install -g pyright
```

See the python [typing documentation](https://docs.python.org/3/library/typing.html) for more information on static types.

### API Documentation

>* [csvqb docs](https://ci.floop.org.uk/job/GSS_data/job/csvwlib/job/main/lastSuccessfulBuild/artifact/csvqb/docs/_build/html/index.html)
>* [sharedmodels docs](https://ci.floop.org.uk/job/GSS_data/job/csvwlib/job/main/lastSuccessfulBuild/artifact/sharedmodels/docs/_build/html/index.html)
>* [pmd docs](https://ci.floop.org.uk/job/GSS_data/job/csvwlib/job/main/lastSuccessfulBuild/artifact/pmd/docs/_build/html/index.html)
>* [devtools docs](https://ci.floop.org.uk/job/GSS_data/job/csvwlib/job/main/lastSuccessfulBuild/artifact/devtools/docs/_build/html/index.html)

We use [sphinx](https://www.sphinx-doc.org/) with [sphinx-apidoc](https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html) and [sphinx.ext.autodoc](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html) to automatically generate API documentation for each of our projects. This is meant to provide a searchable and browsable set of documentation for the entire code-base excluding tests.

In order to support sphinx as well as to provide helpful documentation when using an IDE's intellisense, **you should follow the following rules when writing code**:

* each new module (python file) **must** have a title and *should* have a suitable description.
* each class *should* have a docstring description what its purpose is.
* every function and method *should* have a docstring descripting what it does and *may* describe its return type using the `:return:` annotation.
* use the [sphinx-autodoc annotations](https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html#cross-referencing-python-objects) when talking about another class, module, method, function or variable; this creates deep-links to the appropriate section of documentation.

```python
"""
New Module Title
----------------

This is a description of what this module/python file is for.

N.B. The dashes under the title are required by sphinx and should exactly match the title's length.
"""

class SomeClass:
    """
    Some Description of what this class represents.
    """

    def do_something(some_input: str) -> int:
        """
        Some description of what this method does.

        I'm a member of :class:`~path.to.class.SomeClass` - this annotation creates a deep link to the class!

        :return: Optional description of what it returns, if not clear from context/description.
        """
```

Obviously, none of these rules need to be followed when writing tests, however you should still write a sensible docstring describing what each test checks for.

Intersphinx mapping - this project uses [intersphinx](https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html) to create deep-links to the documentation from other projects like [rdflib](https://rdflib.readthedocs.io/) which use sphinx to generate their docs. This helps provide deep-linking between the documentation for different projects inside csvwlib.

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
