from setuptools import setup, find_packages

setup(
    install_requires=[
        "docker",
        "behave",
        "pytest",
        "rdflib",
        "python-dateutil",
        "csvw",
        "sphinx",
        "sphinx-book-theme",
        "pipenv-setup",
        "chardet",
        "black",
    ],
    packages=find_packages(),
    name="devtools",
)
