from setuptools import setup, find_packages


setup(
    install_requires=[
        "isodate==0.6.0",
        "numpy==1.21.0",
        "pandas==1.2.5",
        "pyparsing==2.4.7",
        "python-dateutil==2.8.1",
        "pytz==2021.1",
        "rdflib==5.0.0",
        "rdflib-jsonld==0.5.0",
        "six==1.16.0",
        "unidecode==1.2.0",
    ],
    version="0.0.1",
    name="csvqb",
    packages=find_packages(exclude=["tests"]),
)
