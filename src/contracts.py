"""Strict input contracts shared by function calling and MCP."""
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

# JSON Schema regex engines can match $ before a final newline.
# Preserve runtime patterns and explicitly reject line terminators.
LINE_TERMINATOR_PATTERN = r"[\r\n\u2028\u2029]"


def _single_line_schema(schema: dict) -> None:
    """Keep published string validation aligned with runtime."""
    schema["not"] = {"pattern": LINE_TERMINATOR_PATTERN}


Question = Annotated[
    str,
    Field(
        min_length=8,
        max_length=160,
        description="Question about trusted Blue Whale project documents.",
        json_schema_extra=_single_line_schema,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9 ,.:;?!'()\-]*$",
    ),
]

Limit = Annotated[
    int,
    Field(
        ge=1,
        le=5,
        strict=True,
        description="Maximum number of trusted sources to retrieve (1 to 5).",
    ),
]


class SearchArguments(BaseModel):
    """Search trusted project sources without changing them."""

    model_config = ConfigDict(extra="forbid")

    question: Question
    limit: Limit = 3


# Ana's HW2: bounded, read-only decision comparison.

DECISION_KEY_PATTERN = r"^[a-z][a-z0-9_]*$"


def _decision_map_schema(schema: dict) -> None:
    """Publish the same key restriction used at runtime."""
    names = schema.setdefault("propertyNames", {})
    names["pattern"] = DECISION_KEY_PATTERN
    _single_line_schema(names)


DecisionKey = Annotated[
    str,
    Field(
        min_length=1,
        max_length=32,
        pattern=DECISION_KEY_PATTERN,
        description="Lowercase decision field name.",
        json_schema_extra=_single_line_schema,
    ),
]

DecisionValue = Annotated[
    str,
    Field(
        min_length=1,
        max_length=80,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9 _.,:/()+-]*$",
        description="Single project decision value.",
        json_schema_extra=_single_line_schema,
    ),
]

DecisionMap = Annotated[
    dict[DecisionKey, DecisionValue],
    Field(
        min_length=1,
        max_length=8,
        description="One to eight project decisions.",
        json_schema_extra=_decision_map_schema,
    ),
]


class DriftArguments(BaseModel):
    """Compare prior and proposed decisions; never modify either."""

    model_config = ConfigDict(extra="forbid")

    state: DecisionMap
    candidate: DecisionMap


class GroundedAnswerArguments(BaseModel):
    """Answer from trusted sources without modifying project state."""

    model_config = ConfigDict(extra="forbid")

    question: Question
    limit: Limit = 5
