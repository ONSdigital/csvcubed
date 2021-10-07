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

### Directory Structure

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

[Static type annotations](https://docs.python.org/3/library/typing.html) have been supported in python, since version 3.5, as defined in [PEP484](https://www.python.org/dev/peps/pep-0484/). Static types are a great addition to python which help us uncover bugs and ship more reliable software. Static type annotations *should* be added to **all** functions to specify the datatypes of all input parameters and the function's return type.

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
* each class *should* have a docstring description of what its purpose is.
* every function and method *should* have a docstring describing what it does and *may* describe its return type using the `:return:` annotation.
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

Intersphinx mapping - this project uses [intersphinx](https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html) to create deep-links to the documentation from other projects like [rdflib](https://rdflib.readthedocs.io/) which use sphinx to generate their docs. This helps provide deep-linking between the documentation for different parts of csvwlib.

### Unit and Integration Testing

This project uses both *unit* and *behaviour* forms of testing. We use unit testing for relatively small modular pieces of functionality with little integration between modules, and we use *behaviour* testing as a form of integration testing.

[Pytest](https://docs.pytest.org) is used as the *unit* testing framework. All unit tests should be inside the [PackageName/PackageName/test/unit](#directory-structure) folder.

[Behave](https://behave.readthedocs.io) is used as our *behaviour* testing framework in which test scripts are written using the cucumber/gherkin syntax. All *behaviour* tests should be inside the [PackageName/PackageName/test/behaveiour](#directory-structure) folder. Generally speaking,  tests involving the use of *docker* (to run post-processing or validation of outputs) are written as behaviour tests.

If any additional test files are required (for either *unit* or *behaviour* testing), they should be stored inside the [PackageName/PackageName/test/test-cases](#directory-structure) folder.

## Packages & Patterns of Note

Some of the key packages we make use of include:

* [pydantic](https://pydantic-docs.helpmanual.io/) - Adds validation to selected models allowing us to correct the user where they provide us with invalid or missing configuration.
* [rdflib](https://rdflib.readthedocs.io) -  Allows us to read and write RDF in various formats as well as query it with SPARQL.
* [pandas](https://pandas.pydata.org/) - Used mainly as a tool for input of tabular data and for writing to CSV.

Below we'll explore how we're using some of these libraries along with some key features built in to python that we're making use of in csvwlib.

### Dataclasses

Python's [dataclasses module](https://docs.python.org/3/library/dataclasses.html) was added to python 3.7 as per [PEP557](https://www.python.org/dev/peps/pep-0557/). It provides some key functionality that reduces the amount of boiler-plate code that it is necessary to write when defining a class. If you annotate a class as a `@dataclass`, then you simply have to define the below code and you no longer need to write an `__init__` function and get free sensible defaults for `__eq__`, `__str__` and `__repr__` too (among others). Importantly, the functionality brings with it the ability to more easily reflect over the fields defined inside a class which makes it easier to do things like serialising to/from JSON.

If we write the following class using the `@dataclass` decorator and extending from [sharedmodels.dataclassbase.DataClassBase](https://github.com/GSS-Cogs/csvwlib/blob/main/sharedmodels/sharedmodels/dataclassbase.py):

```python
from dataclasses import dataclass
from sharedmodels.dataclassbase import DataClassBase

@dataclass
class SomeClass(DataClassBase):
    first_name: str
    surname: str

# Notice that we didn't have to define an __init__ function!
some_instance = SomeClass("Csvw", "Lib")
some_other_instance = SomeClass("Rdf", "Lib")
```

We can see demonstrate some of the helpful functionality we now have:

```python
# Testing equality
some_instance == some_other_instance 
>>> False
# Testing string __repr__
some_instance 
>>> SomeClass(first_name='Csvw', surname='Lib')
# Testing JSON serialisation
some_instance.as_json() 
>>> '{"first_name": "Csvw", "surname": "Lib"}'
# Testing json deserialisation.
SomeClass.from_json('{"first_name": "Ronald", "surname": "Burgermeister"}') 
>>> SomeClass(first_name='Ronald', surname='Burgermeister')
```

### Pydantic

We are using [pydantic] in an atypical fashion. It is designed to be a tool which parses & validates input against the static type annotations, however it typically does this validation *when the class is instantiated*. This prescriptive approach therefore restrictis how you build you model  up. You're required to pass all *required* variables to the `__init__` function; you cannot simply instantiate the class and then verify that it's valid later once you've finished making assignments.

```python
# With mainstream pydantic, you are forced to take this approach
some_instance = SomeClassUsingPydantic(first_arg="value", second_arg="other value")

# With mainstream pydantic, you can't use this approach
some_instance = SomeClassUsingPydantic()
some_instance.first_arg = "value"
some_instance.second_arg = "other value"
```

This may not seem that tricky with a small class like this, but when models accumulate more and more fields, it's often nice to be able to take the latter approach to keep your code a bit easier to understand. Most importantly, it doesn't give out end-user the flexibility to write python in the style that's familiar to them; we don't want to make their life more difficult than is strictly necessary.

So, in [csvqb.models.pydanticmodel.PydanticModel](https://github.com/GSS-Cogs/csvwlib/blob/b3e99d2fffd49a9f314e7d6a13e07ef04c27e7e8/csvqb/csvqb/models/pydanticmodel.py), we have taken an approach that only validates properties when the `pydantic_validation` function is called, when the user says they're ready to check. Ensure that your models extend from `PydanticModel`, that they have the [@dataclasses](#dataclasses) attribute and that you have used [static type annotations](#static-types) on all fields and you model can have `pydantic_validation` too!

**N.B. due to some bugs in the mainstream version of pydantic, we are currently relying on [a custom fork](https://github.com/robons/pydantic/).**

### Serialisation to RDF

Since version 3.9, python has had an `Annotated` datatype, as described by [PEP593](https://www.python.org/dev/peps/pep-0593/) which allows us to hold additional information about a class' fields. It allows us to write code like the following which holds information as to how the field/property should be serialised to RDF:

```python
from typing import Annotated
from rdflib import RDFS, Graph

from sharedmodels.rdf.resource import NewResource, PropertyStatus, map_str_to_en_literal, Triple


class NewResourceWithLabel(NewResource):
    label: Annotated[
        str, Triple(RDFS.label, PropertyStatus.mandatory, map_str_to_en_literal)
    ]
```

Here we see that the `label` property is mapped to the `rdfs:label` predicate which means that when serialised we get a triple of the form `<http://uri/of/this/entity> rdfs:label "The label's value for this entity"@en`

When you inherit from [sharedmodels.models.resource.NewResource](https://github.com/GSS-Cogs/csvwlib/blob/main/sharedmodels/sharedmodels/rdf/resource.py), you gain the functionality to easily serialise your model into an rdflib graph:

```python
thing = NewResourceWithLabel("http://uri/of/this/entity")
thing.label = "The label's value for this entity"
graph = thing.to_graph(Graph())
graph.serialize(format="turtle")
>>> """@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
       <http://uri/of/this/entity> a rdfs:Resource ;
                                   rdfs:label "The label for this entity"@en .
    """
```

## Useful Links

* [W3C CSV-W specification](https://www.w3.org/TR/tabular-metadata/)
* [W3C XSD data types](https://www.w3.org/TR/xmlschema11-2/)
* [W3C RDF Data Cube](https://www.w3.org/TR/vocab-data-cube/)
* [csvlint.rb](https://github.com/Data-Liberation-Front/csvlint.rb) - a tool to help validate CSV-W files
* [csv2rdf](https://github.com/Swirrl/csv2rdf) - a tool to convert CSV-W files into RDF.
