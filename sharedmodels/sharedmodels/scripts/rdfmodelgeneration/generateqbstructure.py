# """
#     Some rough-and-ready code to generate a class hierarchy from the QB RDFS/OWL structure defined at
#     `http://purl.org/linked-data/cube`
# """
# from pathlib import Path
#
#
# from sharedmodels.scripts.rdfmodelgeneration.tools import generate_python_models_for_rdfs_ontology, \
#     built_in_type_mappings
#
#
# py_imports = """
# from rdflib import Literal, URIRef
# from typing import Annotated, Union
#
#
# from sharedmodels.rdf.rdfresource import RdfResource, map_entity_to_uri
# from sharedmodels.rdf.triple import Triple, PropertyStatus
# import sharedmodels.rdf.skos as skos
# import sharedmodels.rdf.rdf as rdf
# import sharedmodels.rdf.rdfs as rdfs
#     """
#
# python_code_str = generate_python_models_for_rdfs_ontology(
#     "http://purl.org/linked-data/cube",
#     built_in_type_mappings | {
#         "http://www.w3.org/2004/02/skos/core#ConceptScheme": "skos.ConceptScheme",
#         "http://www.w3.org/2004/02/skos/core#Collection": "skos.Collection",
#         "http://www.w3.org/2004/02/skos/core#Concept": "skos.Concept",
#         "ub1bL305C17": "Union[skos.ConceptScheme, skos.Collection, HierarchicalCodeList]"
#     },
#     format="turtle",
#     py_imports=py_imports
# )
# output_file = Path("..") / "rdf" / "qb.py"
# with open(output_file, "w+") as f:
#     f.write(python_code_str)
