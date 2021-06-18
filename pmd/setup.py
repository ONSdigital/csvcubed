from setuptools import setup, find_packages

setup(
    version="0.0.1",
    install_requires=[
        "attrs==21.2.0",
        "certifi==2021.5.30",
        "chardet==4.0.0",
        "csvw==1.11.0",
        "idna==2.10",
        "isodate==0.6.0",
        "numpy==1.20.3",
        "pandas==1.2.4",
        "pyparsing==2.4.7",
        "python-dateutil==2.8.1",
        "pytz==2021.1",
        "rdflib==5.0.0",
        "rdflib-jsonld==0.5.0",
        "requests==2.25.1",
        "rfc3986==1.5.0",
        "six==1.16.0",
        "uritemplate==3.0.1",
        "urllib3==1.26.5",
    ],
    name="pmd",
    packages=find_packages(exclude=["tests"]),
    entry_points = {
        "console_scripts": ["pmdutils=pmd.main:main"]
    }
)
