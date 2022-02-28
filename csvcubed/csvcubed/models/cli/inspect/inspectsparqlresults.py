"""
Inspect SPARQL query results
----------------------------
"""

from dataclasses import dataclass, field

from rdflib.query import ResultRow

from csvcubed.utils.sparql import none_or_map


@dataclass()
class CatalogMetadataSparqlResult:
    """
    TODO: Add description here
    """

    sparql_result: ResultRow

    def __post_init__(self):
        result_dict = self.sparql_result.asdict()
        
        self.title: str = result_dict["title"]
        self.label: str = result_dict["label"]
        self.issued: str = result_dict["issued"]
        self.modified: str = result_dict["modified"]
        self.license: str = none_or_map(result_dict.get("license"), str)
        self.creator: str = none_or_map(result_dict.get("creator"), str)
        self.publisher: str = none_or_map(result_dict.get("publisher"), str)
        self.landingPages: list[str] = str(result_dict["landingPages"]).split("|")
        self.themes: list[str] = str(result_dict["themes"]).split("|")
        self.keywords: list[str] = str(result_dict["keywords"]).split("|")
        self.contact_point: str = none_or_map(result_dict.get("contact_point"), str)
        self.identifier: str = (result_dict["identifier"],)
        self.comment: str = none_or_map(result_dict.get("comment"), str)
        self.description: str = str(
            none_or_map(result_dict.get("description"), str)
        ).replace("\n", "\n\t\t")
