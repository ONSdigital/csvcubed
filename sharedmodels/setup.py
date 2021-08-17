from setuptools import setup, find_packages

setup(
    install_requires=[
        "isodate==0.6.0",
        "pyparsing==2.4.7",
        "rdflib==5.0.0",
        "six==1.16.0",
        "unidecode==1.2.0",
    ],
    name="sharedmodels",
    version="0.0.1",
    packages=find_packages(exclude=["sharedmodels/scripts", "**/build"]),
)
