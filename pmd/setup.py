from setuptools import setup, find_packages

setup(
    version="0.0.1",
    install_requires=[
        "rdflib",
        "rdflib-jsonld",
        "requests",
        "csvw",
        "pandas",
        "uritemplate",
        "unidecode",
    ],
    name="pmd",
    packages=find_packages(exclude=["tests"]),
    entry_points={"console_scripts": ["pmdutils=pmd.main:main"]},
)
