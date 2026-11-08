"""Strict input contracts shared by function calling and MCP."""
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

Question = Annotated[
    str,
    Field(
        min_length=8,
        max_length=160,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9 ,.:;?!'()\-]*$",
    ),
]

Limit = Annotated[
    int,
    Field(ge=1, le=5, strict=True),
]


class SearchArguments(BaseModel):
    """Search trusted project sources without changing them."""

    model_config = ConfigDict(extra="ignore")

    question: Question
    limit: Limit = 3
