from setuptools import setup, find_packages

setup(
    install_requires=["unidecode", "rdflib~=5.0.0"],
    name="sharedmodels",
    version="0.0.1",
    packages=find_packages(exclude=["sharedmodels/scripts", "**/build"]),
)
