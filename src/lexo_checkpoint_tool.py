"""Read-only checkpoint preview tool (Leqso HW2).

The tool calculates what a checkpoint *would* look like if the proposed
changes were applied. It never writes trusted state and never treats a
proposal as user approval; ``requires_confirmation`` tells the caller that
a human must confirm before any separate commit capability may apply it.
"""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from .contracts import DecisionMap
from .misha_retrieval_tool import ToolFailure

MAX_VERSION = 1_000_000
MAX_DECISIONS = 8

CheckpointVersion = Annotated[
    int,
    Field(
        ge=0,
        le=MAX_VERSION,
        strict=True,
        description=(
            "Current trusted checkpoint version "
            f"(integer from 0 to {MAX_VERSION})."
        ),
    ),
]


class PreviewCheckpointUpdateArgs(BaseModel):
    """Preview a checkpoint update; never modify trusted state."""

    model_config = ConfigDict(extra="ignore")

    previous_version: CheckpointVersion
    previous_decisions: DecisionMap
    proposed_changes: DecisionMap


class Checkpoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int
    decisions: dict[str, str]


class PreviewResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    checkpoint: Checkpoint
    changed_fields: list[str]
    requires_confirmation: bool


def run_preview_checkpoint_update(
    args: PreviewCheckpointUpdateArgs,
) -> PreviewResult:
    """Calculate a proposed checkpoint without modifying trusted state."""

    decisions = dict(args.previous_decisions)
    changed_fields = sorted(
        key
        for key, value in args.proposed_changes.items()
        if decisions.get(key) != value
    )
    decisions.update(args.proposed_changes)

    if len(decisions) > MAX_DECISIONS:
        raise ToolFailure(
            f"Proposed checkpoint would exceed {MAX_DECISIONS} decisions. "
            "Propose fewer new decision fields or change existing ones."
        )

    if changed_fields and args.previous_version >= MAX_VERSION:
        raise ToolFailure(
            "Checkpoint version limit reached. "
            "Ask the operator to archive this checkpoint before changing it."
        )

    version = (
        args.previous_version + 1 if changed_fields else args.previous_version
    )

    return PreviewResult(
        checkpoint=Checkpoint(version=version, decisions=decisions),
        changed_fields=changed_fields,
        requires_confirmation=bool(changed_fields),
    )
