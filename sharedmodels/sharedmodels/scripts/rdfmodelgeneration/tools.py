# from rdflib import Graph, URIRef
# from typing import Optional, List, Dict
# import re
#
#
# literal_types = ["str", "bool", "int"]
#
# built_in_type_mappings = {
#     "RdfResource": "RdfResource",
#     "http://www.w3.org/1999/02/22-rdf-syntax-ns#Property": "rdf.Property",
#     "http://www.w3.org/1999/02/22-rdf-syntax-ns#List": "list",
#     "http://www.w3.org/2000/01/rdf-schema#Class": "rdfs.Class",
#     "http://www.w3.org/2001/XMLSchema#boolean": "bool",
#     "http://www.w3.org/2001/XMLSchema#int": "int"
# }
#
#
# hash_uri_regex = re.compile("#(.*?)$")
# slash_uri_regex = re.compile("/(.*?)$")
#
#
# class InfiniteLoopException(Exception):
#     pass
#
#
# class RdfResource:
#     def __init__(self, uri: URIRef):
#         self.uri: str = str(uri)
#
#     def get_identifier(self) -> str:
#         if hash_uri_regex.search(self.uri):
#             return hash_uri_regex.search(self.uri).group(1)
#
#         if slash_uri_regex.search(self.uri):
#             return slash_uri_regex.search(self.uri).group(1)
#
#         return self.uri
#
#
# class RdfClassInfo(RdfResource):
#     def __init__(self, uri: URIRef, label: Optional[str], comment: Optional[str], parent_classes_uris: Optional[str]):
#         RdfResource.__init__(self, uri)
#         self.label: Optional[str] = label
#         self.comment: Optional[str] = comment
#         self.parent_class_uris: List[str] = [] if str(parent_classes_uris) == "" else parent_classes_uris.split(",")
#
#
# def generate_python_models_for_rdfs_ontology(rdf_source_path: str,
#                                              map_uri_to_type: Dict[URIRef, str] = built_in_type_mappings,
#                                              format: Optional[str] = None,
#                                              py_imports: str = "") -> str:
#     class RdfPropertyInfo(RdfResource):
#         def __init__(self, uri: URIRef, label: Optional[str], comment: Optional[str], range_uri: URIRef):
#             RdfResource.__init__(self, uri)
#             self.label: Optional[str] = label
#             self.comment: Optional[str] = comment
#             self.range_uri: str = str(range_uri)
#
#         def to_property_type_annotation(self, quote_type_name: bool = False) -> str:
#             property_type = map_uri_to_type[self.range_uri]
#             mapper_function = "Literal" if property_type in literal_types else "map_entity_to_uri"
#
#             if quote_type_name:
#                 property_type = f"\"{property_type}\""
#
#             return f"Annotated[{property_type}, Triple(URIRef(\"{self.uri}\"), PropertyStatus.recommended, {mapper_function})]"
#
#     g: Graph = Graph()
#     g.load(rdf_source_path, format=format)
#
#     # todo: Add more automatic support in for owl:unionOf functionality.
#     # owl_union_results = g.query("""
#     #     PREFIX rdf:            <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
#     #     PREFIX rdfs:           <http://www.w3.org/2000/01/rdf-schema#>
#     #     PREFIX owl:            <http://www.w3.org/2002/07/owl#>
#     #     PREFIX xsd:            <http://www.w3.org/2001/XMLSchema#>
#     #
#     #     SELECT DISTINCT ?unionType ?unionTypeLabel ?unionTypeComment (GROUP_CONCAT(?type; separator=",") as ?types)
#     #     WHERE {
#     #         ?unionType a owl:Class;
#     #                    owl:unionOf [ rdf:rest*/rdf:first ?type ]
#     #
#     #         OPTIONAL { ?unionType rdfs:label ?unionTypeLabel. }
#     #         OPTIONAL { ?unionType rdfs:comment ?unionTypeComment. }
#     #     }
#     #     GROUP BY ?unionType ?unionTypeLabel ?unionTypeComment
#     # """)
#     # for result in owl_union_results:
#     #     union_type = result["union_type"]
#     #
#     #     map_uri_to_type[]
#
#     class_query_results = g.query("""
#     PREFIX rdf:            <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
#     PREFIX rdfs:           <http://www.w3.org/2000/01/rdf-schema#>
#     PREFIX owl:            <http://www.w3.org/2002/07/owl#>
#     PREFIX xsd:            <http://www.w3.org/2001/XMLSchema#>
#
#     SELECT DISTINCT ?class ?classLabel ?classComment (GROUP_CONCAT(?parent; separator=",") as ?parentClasses)
#     WHERE {
#         {
#             SELECT DISTINCT ?class
#             WHERE {
#                 { ?class a rdfs:Class. } UNION { ?class a owl:Class. }
#             }
#         }
#
#         OPTIONAL { ?class rdfs:label ?classLabel. }
#         OPTIONAL { ?class rdfs:subClassOf ?parent. }
#         OPTIONAL { ?class rdfs:comment ?classComment. }
#     }
#     GROUP BY ?class ?classLabel ?classComment
#     """)
#
#     classes = [RdfClassInfo(row["class"], row["classLabel"], row["classComment"], row["parentClasses"])
#                for row in class_query_results]
#
#     types_already_defined = {uri for (uri, t) in map_uri_to_type.items()}
#     map_uri_to_type |= {class_info.uri: class_info.get_identifier() for class_info in classes}
#
#     map_uri_to_cyclic_dependency_snapshots = {}
#
#     def process_class_queue(class_queue: List[RdfClassInfo],
#                             treat_property_types_as_dependencies: bool = True) -> Optional[str]:
#         class_info = class_queue.pop(0)
#
#         property_query_results = g.query(f"""
#             PREFIX rdf:            <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
#             PREFIX rdfs:           <http://www.w3.org/2000/01/rdf-schema#>
#             PREFIX owl:            <http://www.w3.org/2002/07/owl#>
#             PREFIX xsd:            <http://www.w3.org/2001/XMLSchema#>
#
#             SELECT DISTINCT ?property ?propertyLabel ?propertyComment ?range
#             WHERE {{
#                 {{
#                     SELECT DISTINCT ?property
#                     WHERE {{
#                         {{ ?property a rdf:Property. }}
#                         UNION {{ ?property a owl:ObjectProperty. }}
#                         UNION {{ ?property a owl:DatatypeProperty. }}
#                     }}
#                 }}
#
#                 ?property rdfs:domain <{class_info.uri}>;
#                           rdfs:range ?range.
#
#                 OPTIONAL {{ ?property rdfs:label ?propertyLabel. }}
#                 OPTIONAL {{ ?property rdfs:comment ?propertyComment. }}
#             }}
#             """)
#         properties = [RdfPropertyInfo(row["property"], row["propertyLabel"], row["propertyComment"], row["range"])
#                       for row in property_query_results]
#
#         # Ensure we define parent classes before children, etc.
#         # N.B. this may mean we end up in an infinite loop - that would be bad.
#         dependent_types = [u for u in class_info.parent_class_uris]
#         if treat_property_types_as_dependencies:
#             # If we're in an infinite loop, don't consider properties to be part of the dependent_types.
#             dependent_types += [p.range_uri for p in properties]
#
#         dependent_types_not_processed_yet = [t for t in dependent_types if t not in types_already_defined]
#         if len(dependent_types_not_processed_yet) > 0:
#             in_infinite_loop = False
#             remaining_queue_snapshot = [c.uri for c in class_queue]
#             if class_info.uri in map_uri_to_cyclic_dependency_snapshots:
#                 previous_snapshot = map_uri_to_cyclic_dependency_snapshots[class_info.uri]
#                 in_infinite_loop = remaining_queue_snapshot == previous_snapshot
#
#             if in_infinite_loop:
#                 print(f"In infinite loop with {class_info.label}/{class_info.uri}")
#                 class_queue.append(class_info)
#                 raise InfiniteLoopException()
#             else:
#                 map_uri_to_cyclic_dependency_snapshots[class_info.uri] = remaining_queue_snapshot
#                 class_queue.append(class_info)
#                 print(f"Delaying declaration of {class_info.label}/{class_info.uri} due to dependencies.")
#                 return None
#
#         base_classes = ["RdfResource"] if len(class_info.parent_class_uris) == 0 \
#             else [c for c in class_info.parent_class_uris]
#         base_classes_str = ", ".join([map_uri_to_type[c] for c in base_classes])
#
#         new_line_with_indent = "\n    "
#         should_quote_type_name = not treat_property_types_as_dependencies
#         properties_str = f"\n{new_line_with_indent}".join(
#             [f"{p.get_identifier()}: {p.to_property_type_annotation(should_quote_type_name)}" +
#              new_line_with_indent +
#              f"\"\"\"{p.label or ''} - {p.comment or ''}\"\"\"" for p in properties]
#         )
#
#         if properties_str is None:
#             properties_str = ""
#         else:
#             properties_str = new_line_with_indent + properties_str
#
#         parent_constructor_calls = f"{new_line_with_indent}    ".join(
#             [f"{map_uri_to_type[c]}.__init__(self, uri)" for c in base_classes])
#
#         types_already_defined.add(class_info.uri)
#         return f"""
#
# class {class_info.get_identifier()}({base_classes_str}):
#     \"""{class_info.label or ''} - {class_info.comment or ''}\"""{properties_str}
#     def __init__(self, uri: str):
#         {parent_constructor_calls}
#         self.rdf_types.add(URIRef("{class_info.uri}"))
#         """
#
#     output_str = py_imports
#     queue = [c for c in classes]
#     treat_property_types_as_dependencies = True
#     while len(queue) > 0:
#         try:
#             class_py_str = process_class_queue(queue, treat_property_types_as_dependencies)
#         except InfiniteLoopException as e:
#             if not treat_property_types_as_dependencies:
#                 # We can't do anything now, we've done all we can. It's a cyclic dependency Python can't cope with.
#                 raise e
#
#             # Python can cope with out-of-order property type dependencies, so let's take that approach.
#             treat_property_types_as_dependencies = False
#             continue
#
#         if class_py_str is not None:
#             output_str += class_py_str
#
#     return output_str
