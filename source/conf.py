# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "csvcubed"
copyright = "2023, ONS"
author = "ONS"
release = "0.3.5"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
]
include_patterns = [
    "index.rst",
    "modules.rst",
    "csvcubed*.rst",
]
templates_path = ["_templates"]
exclude_patterns = [
    "csvcubed.utils.skos*.rst",
    "csvcubed.cli.build*.rst",
    "csvcubed.cli.pull*.rst",
    "csvcubed.cli.error_mapping*.rst",
    "csvcubed.cli.entry*.rst",
    "csvcubed.utils.date*.rst",
    "csvcubed.utils.dict*.rst",
    "csvcubed.utils.file*.rst",
    "csvcubed.utils.iterables*.rst",
    "csvcubed.utils.json*.rst",
    "csvcubed.utils.log*.rst",
    "csvcubed.utils.p*.rst",
    "csvcubed.utils.rdf*.rst",
    "csvcubed.utils.u*.rst",
    "csvcubed.utils.v*.rst",
    "csvcubed.utils.t*.rst",
    "csvcubed.cli.codelist*.rst",
    "csvcubed.utils.qb*.rst",
    "csvcubed.utils.c*.rst",
    "csvcubed.models*.rst",
    "csvcubed.readers*.rst",
    "csvcubed.writers*.rst",
    "csvcubed.definitions*.rst",
    "csvcubed.inputs*.rst",
]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "python_docs_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

html_sidebars = {"**": ["globaltoc.html", "sourcelink.html", "searchbox.html"]}
