# """
#     Some rough-and-ready code to generate a class hierarchy from the QB RDFS/OWL structure defined at
#     `https://www.w3.org/2009/08/skos-reference/skos.rdf`
# """
# from pathlib import Path
#
#
# from sharedmodels.scripts.rdfmodelgeneration.tools import generate_python_models_for_rdfs_ontology
#
#
# py_imports = """
# from rdflib import Literal, URIRef
# from typing import Annotated, Union
#
#
# from sharedmodels.rdf.rdfresource import RdfResource, map_entity_to_uri
# from sharedmodels.rdf.triple import Triple, PropertyStatus
# import sharedmodels.rdf.rdfs as rdfs
# import sharedmodels.rdf.rdf as rdf
#     """
#
# python_code_str = generate_python_models_for_rdfs_ontology(
#     "https://www.w3.org/2009/08/skos-reference/skos.rdf",
#     py_imports=py_imports
# )
# output_file = Path("..") / ".." / "rdf" / "skos.py"
# with open(output_file, "w+") as f:
#     f.write(python_code_str)
