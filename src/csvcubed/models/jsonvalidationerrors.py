"""
JSON Validation Errors
----------------------

Contains models holding information on JSON Schema Validation errors

"""
import os
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, fields
from textwrap import indent
from typing import Any, List, Optional, Tuple

import requests
from jsonschema import RefResolver
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT7

from csvcubed.utils.text import truncate
from csvcubed.utils.uri import looks_like_uri

from .validationerror import ValidationError

_indent = "    "


@dataclass
class JsonSchemaValidationError(ValidationError, ABC):
    """Represents a JSON Schema Validation Error"""

    schema: dict
    json_path: str
    message: str

    offending_value: Any
    """The offending value which does not meet schema expectations."""

    schema_validator_type: Optional[str]
    """The type of schema validator which this error occurred under."""

    @abstractmethod
    def get_children(self) -> List["JsonSchemaValidationError"]:
        """Return any child errors associated with this JsonSchemaValidationError"""
        pass

    @abstractmethod
    def _child_error_messages_display_string(
        self, invidual_message_truncation_at: int, depth_to_display: int
    ) -> str:
        pass

    def to_display_string(
        self, invidual_message_truncation_at: int = 149, depth_to_display: int = 1
    ) -> str:
        """Returns a string for display to the user detailing the error that occurred."""

        message = ""

        if self.json_path != "$":
            message += f"{self.json_path} "

        message += "- " + truncate(self.message, invidual_message_truncation_at)

        if depth_to_display > 0:
            message += self._child_error_messages_display_string(
                invidual_message_truncation_at, depth_to_display
            )

        return message

    def as_dict(self) -> dict:
        """
        Overrides DataClassBase.as_dict to ensure we don't serialise the schema field.

        This function makes sure we recursively apply the `schema` deletion down the tree.
        """
        return asdict(self, dict_factory=self._dict_factory)

    @staticmethod
    def _dict_factory(values: List[Tuple[str, str]]) -> dict:
        """Removes `schema` field from the dict value of this class."""

        dict_values = {k: v for (k, v) in values}

        # Unfortunately we don't know the type of the class at this point so this is the best way of
        # attempting to ensure we don't accidentally remove `schema` from another dataclass.
        fields_match_this_class = not any(
            [f.name not in dict_values for f in fields(JsonSchemaValidationError)]
        )
        if fields_match_this_class:
            del dict_values["schema"]

        return dict_values


@dataclass
class GenericJsonSchemaValidationError(JsonSchemaValidationError):
    children: List[JsonSchemaValidationError]

    def get_children(self) -> List[JsonSchemaValidationError]:
        return self.children

    def _child_error_messages_display_string(
        self, invidual_message_truncation_at: int, depth_to_display: int
    ) -> str:
        if not any(self.children):
            return ""

        return os.linesep + indent(
            os.linesep.join(
                [
                    e.to_display_string(
                        invidual_message_truncation_at, depth_to_display - 1
                    )
                    for e in self.children
                ]
            ),
            _indent,
        )


@dataclass
class AnyOneOfJsonSchemaValidationError(JsonSchemaValidationError):
    """
    A JSON validation error associated with a `oneOf` or `anyOf` definintion.

    Groups together errors by the types which are possible under the one/anyOf relationship for ease of user
      understanding.
    """

    possible_types_with_grouped_errors: List[
        Tuple[dict, List[JsonSchemaValidationError]]
    ]

    def get_children(self) -> List[JsonSchemaValidationError]:
        return [
            e for (_, errors) in self.possible_types_with_grouped_errors for e in errors
        ]

    def _child_error_messages_display_string(
        self, invidual_message_truncation_at: int, depth_to_display: int
    ):
        ref_resolver = RefResolver.from_schema(self.schema)
        # New code start
        resource = Resource(self.schema, DRAFT7)
        registry = Registry().with_resource(
            resource.contents["id"],
            resource,
        )
        resolver = registry.resolver(resource.contents["id"])
        # New code end
        child_error_messages = ""

        for possible_type, errors in self.possible_types_with_grouped_errors:
            description = possible_type.get("description")

            if "$ref" in possible_type:
                # _resolve_reference_in_schema now takes in both the jsonschema.RefResolver and the referencing.Resolver objects
                # Once investigation is complete and the referencing library has been implemented, ref_resolver should be removed
                possible_type = self._resolve_reference_in_schema(
                    ref_resolver, registry, resolver, possible_type
                )
                description = possible_type.get("description", description)

            if description is None:
                description = truncate(
                    str(possible_type), invidual_message_truncation_at
                )

            child_error_messages += (
                f"{os.linesep + os.linesep}If you meant to declare '{description}', then:{os.linesep}"
                + indent(
                    os.linesep.join(
                        [
                            e.to_display_string(
                                invidual_message_truncation_at, depth_to_display - 1
                            )
                            for e in errors
                        ]
                    ),
                    _indent,
                )
                + os.linesep
            )

        return indent(child_error_messages, _indent)

    @staticmethod
    def _resolve_reference_in_schema(
        ref_resolver: RefResolver,
        registry: Registry,
        resolver: Registry.resolver,
        ref_object: dict,
    ) -> dict:
        ref_value = ref_object["$ref"]
        # If the ref_value is *not* a URI, this function works fine
        # There is no direct replacement for `RefResolver.resolve_from_url` in the `referencing` library
        # The `referencing` library needs the relevant $ref contents to be retrieved via an HTTP request
        # A Resource can then be generated from the HTTP response
        # The main issue here is to accommodate different formats when resolving the $ref value
        # For example, if a codelist is defined inline in the config.json, resource.contents does not have a `uris` value
        # In this instance, `resource.contents` would be the expected return value
        # There may be other nuances for the different $ref values that have not yet been explored
        if looks_like_uri(ref_value):
            response = requests.get(ref_value)
            resource = Resource.from_contents(response.json(), DRAFT7)
            # x = resource.contents["uris"]["enum"]
            # Some kind of function here needs to exist to act as a callable for Registry's retrieve argument.
            # According to the migration guide that is the replacement for RefResolver.resolve_from_url
            # https://python-jsonschema.readthedocs.io/en/latest/referencing/#migrating-from-refresolver
            # https://referencing.readthedocs.io/en/stable/api/#referencing.Registry
            # See section 7.3 https://readthedocs.org/projects/python-jsonschema/downloads/pdf/stable/
            # in particular page 34

            return resource.contents["uris"]
            # return Registry(retrieve= ).get_or_retrieve()
            # return ref_resolver.resolve_from_url(ref_value)
        else:
            # _, referenced_type = ref_resolver.resolve(ref_value)
            referenced_type = resolver.lookup(ref_value).contents
            return referenced_type

    # @staticmethod
    # def _resolve_reference_in_schema(
    #     ref_resolver: RefResolver, ref_object: dict
    # ) -> dict:
    #     ref_value = ref_object["$ref"]
    #     if looks_like_uri(ref_value):
    #         return ref_resolver.resolve_from_url(ref_value)
    #     else:
    #         _, referenced_type = ref_resolver.resolve(ref_value)
    #         return referenced_type
