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
