"""Preview checkpoint update tool for HW2 (read-only)."""

from pydantic import BaseModel, ConfigDict, Field

from .contracts import DecisionMap


class PreviewCheckpointUpdateArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    previous_version: int = Field(
        ge=0,
        strict=True,
        description="Current trusted checkpoint version (non-negative integer).",
    )
    previous_decisions: DecisionMap
    proposed_changes: DecisionMap


class PreviewResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    checkpoint: dict
    changed_fields: list[str]
    requires_confirmation: bool


def run_preview_checkpoint_update(
    args: PreviewCheckpointUpdateArgs,
) -> PreviewResult:
    """Calculate a proposed checkpoint without modifying trusted state."""

    previous_decisions = dict(args.previous_decisions)
    proposed_changes = dict(args.proposed_changes)

    new_decisions = dict(previous_decisions)
    changed_fields = []

    for k, v in proposed_changes.items():
        if k not in new_decisions or new_decisions[k] != v:
            new_decisions[k] = v
            changed_fields.append(k)

    changed_fields = sorted(list(set(changed_fields)))

    new_version = args.previous_version + 1 if changed_fields else args.previous_version

    return PreviewResult(
        checkpoint={
            "version": new_version,
            "decisions": new_decisions,
        },
        changed_fields=changed_fields,
        requires_confirmation=bool(changed_fields),
    )