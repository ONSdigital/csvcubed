"""
Namespaces
----------
"""
from rdflib import Namespace

DCAT = Namespace("http://www.w3.org/ns/dcat#")

DCTERMS = Namespace("http://purl.org/dc/terms/")

XSD = Namespace("http://www.w3.org/2001/XMLSchema#")

PROV = Namespace("http://www.w3.org/ns/prov#")

ODRL2 = Namespace("http://www.w3.org/ns/odrl/2/")

FOAF = Namespace("http://xmlns.com/foaf/0.1/")

RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")

CSVW = Namespace("http://www.w3.org/ns/csvw#")

VOID = Namespace("http://rdfs.org/ns/void#")

SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

QB = Namespace("http://purl.org/linked-data/cube#")

QUDT = Namespace("http://qudt.org/schema/qudt/")
"""
QUDT System of Units 

See http://qudt.org/ for more information.
"""

OM2 = Namespace("http://www.ontology-of-units-of-measure.org/resource/om-2/")
""" 
OM 2: Units of Measure

See http://www.ontology-of-units-of-measure.org/page/om-2 for more information.
"""

SDMX_Concept = Namespace("http://purl.org/linked-data/sdmx/2009/concept#")
SDMX_Code = Namespace("http://purl.org/linked-data/sdmx/2009/code#")
SDMX_Dimension = Namespace("http://purl.org/linked-data/sdmx/2009/dimension#")
SDMX_Attribute = Namespace("http://purl.org/linked-data/sdmx/2009/attribute#")
SDMX_Measure = Namespace("http://purl.org/linked-data/sdmx/2009/measure#")

GOV = Namespace("https://www.gov.uk/government/organisations/")
GDP = Namespace(f"http://gss-data.org.uk/def/gdp#")
THEME = Namespace("http://gss-data.org.uk/def/concept/statistics-authority-themes/")
