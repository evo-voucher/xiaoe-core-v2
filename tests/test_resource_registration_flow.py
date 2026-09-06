import json
from pathlib import Path

import pytest

from runtime.resource_registration_flow import ResourceRegistrationFlow


REGISTRY_PATH = Path(__file__).resolve().parents[1] / "registry" / "RESOURCE_AUTH_REGISTRY.json"


def flow():
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return ResourceRegistrationFlow(registry)


def existing_github_account():
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return next(r["account"] for r in registry["resources"] if r["service"] == "github")


def test_registration_requires_owner_approval():
    decision = flow().approve(
        service="github",
        identity="Another-Account",
        permissions=["read", "copy"],
        owner_approved=False,
    )
    assert decision.approved is False
    assert decision.reason == "owner_approval_required"


def test_owner_can_approve_explicit_permission_scope():
    decision = flow().approve(
        service="github",
        identity="Another-Account",
        permissions=["read", "copy"],
        owner_approved=True,
    )
    assert decision.approved is True
    assert decision.resource_entry["policy"]["read"] is True
    assert decision.resource_entry["policy"]["copy_out"] is True
    assert decision.resource_entry["policy"]["manage"] is False
    assert decision.resource_entry["policy"]["destructive"] == "explicit_owner_approval"


def test_registration_cannot_grant_destructive_permission():
    decision = flow().approve(
        service="github",
        identity="Another-Account",
        permissions=["read", "destructive"],
        owner_approved=True,
    )
    assert decision.approved is False
    assert decision.reason == "invalid_permission_requested"


def test_registration_requires_at_least_one_permission():
    decision = flow().approve(
        service="supabase",
        identity="org-new",
        permissions=[],
        owner_approved=True,
    )
    assert decision.approved is False
    assert decision.reason == "at_least_one_permission_required"


def test_duplicate_resource_cannot_be_applied_twice():
    decision = flow().approve(
        service="github",
        identity=existing_github_account(),
        permissions=["read"],
        owner_approved=True,
    )
    assert decision.approved is True
    with pytest.raises(ValueError, match="resource_already_registered"):
        flow().apply(decision.resource_entry)
