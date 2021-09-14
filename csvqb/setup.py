from setuptools import setup, find_packages


setup(
    dependency_links=["git+https://github.com/robons/pydantic.git#egg=pydantic"],
    install_requires=[
        "pandas~=1.2.5",
        "rdflib-jsonld~=0.5.0",
        "click~=8.0.1",
        "colorama~=0.4.4",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    version="0.0.1",
    name="csvqb",
    packages=find_packages(exclude=["csvqb.tests", "csvqb.tests.*"]),
    entry_points={"console_scripts": ["csvqb=csvqb.cli.entrypoint:entry_point"]},
)
