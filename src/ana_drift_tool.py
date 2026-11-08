"""Ana's read-only drift-detection tool for HW2."""

from typing import Literal

from pydantic import BaseModel, ConfigDict

from .contracts import DriftArguments
from .drift_core import check_drift


class Conflict(BaseModel):
    field: str
    expected: str
    proposed: str


class DriftResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["drift", "consistent"]
    effective_state: dict[str, str]
    conflicts: list[Conflict]


def run_drift(args: DriftArguments) -> DriftResult:
    """Compare decisions without accepting fabricated user overrides."""

    result = check_drift(
        state=args.state,
        candidate=args.candidate,
    )

    return DriftResult.model_validate(result)
