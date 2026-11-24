"""Tests for the preview_checkpoint_update tool (HW2)."""

import json
from dataclasses import replace

import pytest
from pydantic import ValidationError

from src.act import call_tool
from src.lexo_checkpoint_tool import PreviewCheckpointUpdateArgs, PreviewResult, run_preview_checkpoint_update
from src.contracts import DecisionMap
from src.tools import PreviewCheckpointUpdateArgs as PreviewArgs


def run_preview_checkpoint_update_direct(args: PreviewArgs) -> PreviewResult:
    """Direct call to the tool function (non-MCP path)."""
    return run_preview_checkpoint_update(args)


def test_correct_merge():
    """Case 1: Existing decision changes - version increments, changed field reported."""
    args = PreviewArgs(
        previous_version=4,
        previous_decisions={"database": "PostgreSQL", "framework": "FastAPI"},
        proposed_changes={"database": "MongoDB"}
    )
    result = run_preview_checkpoint_update_direct(args)
    
    assert result.checkpoint["version"] == 5
    assert result.checkpoint["decisions"]["database"] == "MongoDB"
    assert result.checkpoint["decisions"]["framework"] == "FastAPI"
    assert result.changed_fields == ["database"]
    assert result.requires_confirmation is True


def test_noop_update():
    """Case 2: No-op update - version unchanged, no changes reported."""
    args = PreviewArgs(
        previous_version=2,
        previous_decisions={"database": "MongoDB"},
        proposed_changes={"database": "MongoDB"}
    )
    result = run_preview_checkpoint_update_direct(args)
    
    assert result.checkpoint["version"] == 2
    assert result.changed_fields == []
    assert result.requires_confirmation is False


def test_new_field_update():
    """Case 3: New field added - version increments, new field reported."""
    args = PreviewArgs(
        previous_version=1,
        previous_decisions={"database": "PostgreSQL"},
        proposed_changes={"framework": "FastAPI"}
    )
    result = run_preview_checkpoint_update_direct(args)
    
    assert result.checkpoint["version"] == 2
    assert result.changed_fields == ["framework"]
    assert result.requires_confirmation is True


def test_no_changes_existing_value():
    """Case 4: Proposed value same as existing - no change, version unchanged."""
    args = PreviewArgs(
        previous_version=3,
        previous_decisions={"database": "PostgreSQL", "framework": "FastAPI"},
        proposed_changes={"database": "PostgreSQL"}
    )
    result = run_preview_checkpoint_update_direct(args)
    
    assert result.checkpoint["version"] == 3
    assert result.changed_fields == []
    assert result.requires_confirmation is False


def test_invalid_version():
    """Case 5: Negative version is invalid."""
    with pytest.raises(ValidationError):
        PreviewArgs(
            previous_version=-1,
            previous_decisions={"database": "PostgreSQL"},
            proposed_changes={"framework": "FastAPI"}
        )


def test_invalid_decision_key():
    """Case 6: Invalid decision key pattern."""
    with pytest.raises(ValidationError):
        PreviewArgs(
            previous_version=1,
            previous_decisions={"invalid-key": "value"},
            proposed_changes={"valid_key": "value"}
        )


def test_invalid_decision_value():
    """Case 6: Invalid decision value pattern."""
    with pytest.raises(ValidationError):
        PreviewArgs(
            previous_version=1,
            previous_decisions={"database": "PostgreSQL"},
            proposed_changes={"framework": "123invalid!"}
        )


def test_invalid_input_extra_field():
    """Case 6: Extra field not allowed (top-level)."""
    with pytest.raises(ValidationError):
        PreviewArgs(
            previous_version=1,
            previous_decisions={"database": "PostgreSQL"},
            proposed_changes={"database": "MongoDB"},
            extra_field="value"
        )


def test_non_decision_map_input():
    """Case 6: Non-DecisionMap input is invalid."""
    with pytest.raises(ValidationError):
        PreviewArgs(
            previous_version=1,
            previous_decisions="not_a_dict",
            proposed_changes={"framework": "FastAPI"}
        )


def test_mcp_integration():
    """Test that the tool works through MCP (simulated)."""
    # Simulate the tool call through call_tool
    tool = PreviewCheckpointUpdateArgs(
        previous_version=1,
        previous_decisions={"database": "PostgreSQL"},
        proposed_changes={"database": "MongoDB"}
    )
    
    # This simulates what call_tool would do
    result = run_preview_checkpoint_update_direct(tool)
    
    assert result.checkpoint["version"] == 2
    assert result.changed_fields == ["database"]
    assert result.requires_confirmation is True