import json
from pathlib import Path

from runtime.resource_permission_gate import Action, ResourcePermissionGate


REGISTRY_PATH = Path(__file__).resolve().parents[1] / "registry" / "RESOURCE_AUTH_REGISTRY.json"


def gate():
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return ResourcePermissionGate(registry)


def resource_key(service):
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return next(r["resource_key"] for r in registry["resources"] if r["service"] == service)


def test_xiaoe_can_read_authorized_github():
    decision = gate().authorize(
        principal_key="xiaoe_core_v2",
        action=Action.READ,
        source_resource_key=resource_key("github"),
    )
    assert decision.allowed is True


def test_xiaoai_cannot_manage():
    decision = gate().authorize(
        principal_key="daughter_companion_ai",
        action=Action.MANAGE,
        destination_resource_key=resource_key("github"),
    )
    assert decision.allowed is False
    assert decision.reason == "principal_action_not_allowed"


def test_xiaoai_cannot_escalate_to_destructive_even_with_owner_approval_flag():
    decision = gate().authorize(
        principal_key="daughter_companion_ai",
        action=Action.DESTRUCTIVE,
        destination_resource_key=resource_key("github"),
        owner_approved=True,
    )
    assert decision.allowed is False
    assert decision.reason == "principal_not_eligible_for_destructive_action"


def test_copy_requires_source_and_destination():
    decision = gate().authorize(
        principal_key="xiaoe_core_v2",
        action=Action.COPY,
        source_resource_key=resource_key("github"),
    )
    assert decision.allowed is False
    assert decision.reason == "destination_required"


def test_copy_keeps_source_immutable_by_default():
    decision = gate().authorize(
        principal_key="xiaoe_core_v2",
        action=Action.COPY,
        source_resource_key=resource_key("github"),
        destination_resource_key=resource_key("supabase"),
        source_mutation_requested=True,
    )
    assert decision.allowed is False
    assert decision.reason == "source_is_immutable_for_copy"


def test_destructive_requires_owner_approval():
    decision = gate().authorize(
        principal_key="xiaoe_core_v2",
        action=Action.DESTRUCTIVE,
        destination_resource_key=resource_key("supabase"),
        owner_approved=False,
    )
    assert decision.allowed is False
    assert decision.requires_owner_approval is True
    assert decision.reason == "explicit_owner_approval_required"


def test_destructive_allowed_after_owner_approval():
    decision = gate().authorize(
        principal_key="xiaoe_core_v2",
        action=Action.DESTRUCTIVE,
        destination_resource_key=resource_key("supabase"),
        owner_approved=True,
    )
    assert decision.allowed is True
