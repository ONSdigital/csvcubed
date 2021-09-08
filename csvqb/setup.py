from setuptools import setup, find_packages


setup(
    dependency_links=[
        "git+https://github.com/robons/pydantic.git@72a15dccae95cc9680e207d5fcac000586162837#egg=pydantic"
    ],
    install_requires=[
        "click==8.0.1",
        "colorama==0.4.4",
        "isodate==0.6.0",
        "numpy==1.21.0; python_version >= '3.7'",
        "pandas==1.2.5",
        "pyparsing==2.4.7; python_version >= '2.6' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "python-dateutil==2.8.1; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "pytz==2021.1",
        "rdflib==5.0.0",
        "rdflib-jsonld==0.5.0",
        "six==1.16.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "typing-extensions==3.10.0.0",
        "unidecode==1.2.0",
    ],
    version="0.0.1",
    name="csvqb",
    packages=find_packages(exclude=["tests"]),
    entry_points={"console_scripts": ["csvqb=csvqb.cli.entrypoint:entry_point"]},
)
