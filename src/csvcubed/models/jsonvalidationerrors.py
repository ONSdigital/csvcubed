"""
JSON Validation Errors
----------------------

Contains models holding information on JSON Schema Validation errors

"""
from dataclasses import dataclass
from textwrap import indent
from typing import List, Dict, Iterable, Tuple
import os

from csvcubed.utils.text import truncate
from .validationerror import ValidationError

_indent = "    "


@dataclass
class JsonSchemaValidationError(ValidationError):
    """Represents a JSON Schema Validation Error"""

    json_path: str
    message: str
    children: List["JsonSchemaValidationError"]

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
            )
        )

    def to_display_string(
        self, invidual_message_truncation_at: int = 149, depth_to_display: int = 1
    ) -> str:
        """Returns a string for display to the user detailing the error that occurred."""

        message = (
            self.json_path
            + " - "
            + truncate(self.message, invidual_message_truncation_at)
        )

        if depth_to_display > 0:
            message += self._child_error_messages_display_string(
                invidual_message_truncation_at, depth_to_display
            )

        return message


@dataclass
class AnyOfJsonSchemaValidationError(JsonSchemaValidationError):
    possible_types_with_grouped_errors: Iterable[Tuple[dict, List[ValidationError]]]

    def _child_error_messages_display_string(
        self, invidual_message_truncation_at: int, depth_to_display: int
    ):
        """
        This overrides JsonSchemaValidationError._child_error_messages_display_string
        """
        child_error_messages = ""

        for (possible_type, errors) in self.possible_types_with_grouped_errors:
            # todo: Sort out resolving references so we can bring the description through
            # if "$ref" in possible_type:
            #     RefResolver.from_schema(sc)
            #     possible_type =

            child_error_messages += (
                f"{os.linesep}Assuming {possible_type} --{os.linesep}"
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
            )

        return child_error_messages
