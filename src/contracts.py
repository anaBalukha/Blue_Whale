"""Strict input contracts shared by function calling and MCP."""
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

Question = Annotated[
    str,
    Field(
        min_length=8,
        max_length=160,
        description="Question about trusted Blue Whale project documents.",
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

DecisionKey = Annotated[
    str,
    Field(
        min_length=1,
        max_length=32,
        pattern=r"^[a-z][a-z0-9_]*$",
        description="Lowercase decision field name.",
    ),
]

DecisionValue = Annotated[
    str,
    Field(
        min_length=1,
        max_length=80,
        pattern=r"^.*$",
        description="Single project decision value.",
    ),
]

DecisionMap = Annotated[
    dict[DecisionKey, DecisionValue],
    Field(
        min_length=1,
        max_length=8,
        description="One to eight project decisions.",
    ),
]


class DriftArguments(BaseModel):
    """Compare prior and proposed decisions; never modify either."""

    model_config = ConfigDict(extra="forbid")

    state: DecisionMap
    candidate: DecisionMap
