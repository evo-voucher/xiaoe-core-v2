from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class Action(str, Enum):
    READ = "read"
    COPY = "copy"
    MANAGE = "manage"
    DESTRUCTIVE = "destructive"


@dataclass(frozen=True)
class Decision:
    allowed: bool
    requires_owner_approval: bool
    reason: str


class ResourcePermissionGate:
    """Strict authorization gate for cross-resource XiaoE/XiaoAi operations.

    The gate is deliberately side-effect free. It only evaluates whether an
    operation may proceed; callers remain responsible for performing the
    actual GitHub/Supabase action after a positive decision.
    """

    def __init__(self, registry: Dict[str, Any]):
        self.registry = registry

    def _principal(self, principal_key: str) -> Optional[Dict[str, Any]]:
        return next(
            (p for p in self.registry.get("principals", []) if p.get("principal_key") == principal_key),
            None,
        )

    def _resource(self, resource_key: str) -> Optional[Dict[str, Any]]:
        return next(
            (r for r in self.registry.get("resources", []) if r.get("resource_key") == resource_key),
            None,
        )

    def authorize(
        self,
        *,
        principal_key: str,
        action: Action | str,
        source_resource_key: Optional[str] = None,
        destination_resource_key: Optional[str] = None,
        owner_approved: bool = False,
        source_mutation_requested: bool = False,
    ) -> Decision:
        try:
            action = Action(action)
        except ValueError:
            return Decision(False, False, "unknown_action")

        principal = self._principal(principal_key)
        if not principal:
            return Decision(False, False, "unknown_principal")

        allowed_actions = set(principal.get("allowed_actions", []))
        if action is Action.DESTRUCTIVE:
            if "manage" not in allowed_actions:
                return Decision(False, False, "principal_not_eligible_for_destructive_action")
        elif action.value not in allowed_actions:
            return Decision(False, False, "principal_action_not_allowed")

        rules = self.registry.get("cross_environment_rules", {})

        if action in {Action.READ, Action.MANAGE, Action.DESTRUCTIVE}:
            target_key = destination_resource_key or source_resource_key
            if not target_key:
                return Decision(False, False, "target_required")
            target = self._resource(target_key)
            if not target or target.get("status") != "authorized":
                return Decision(False, False, "target_not_authorized")
        else:
            if rules.get("require_explicit_source", True) and not source_resource_key:
                return Decision(False, False, "source_required")
            if rules.get("require_explicit_destination", True) and not destination_resource_key:
                return Decision(False, False, "destination_required")
            source = self._resource(source_resource_key or "")
            destination = self._resource(destination_resource_key or "")
            if not source or source.get("status") != "authorized":
                return Decision(False, False, "source_not_authorized")
            if not destination or destination.get("status") != "authorized":
                return Decision(False, False, "destination_not_authorized")
            if source_mutation_requested and rules.get("source_immutable_by_default", True):
                return Decision(False, False, "source_is_immutable_for_copy")

        target_key = destination_resource_key or source_resource_key
        target = self._resource(target_key or "")
        policy = (target or {}).get("policy", {})

        if action is Action.READ and not policy.get("read", False):
            return Decision(False, False, "resource_read_denied")
        if action is Action.COPY and not policy.get("copy_out", False):
            return Decision(False, False, "resource_copy_denied")
        if action is Action.MANAGE and not policy.get("manage", False):
            return Decision(False, False, "resource_manage_denied")

        if action is Action.DESTRUCTIVE:
            if not policy.get("manage", False):
                return Decision(False, False, "resource_not_eligible_for_destructive_action")
            requires = (
                principal.get("destructive_requires_explicit_owner_approval", True)
                or policy.get("destructive") == "explicit_owner_approval"
            )
            if requires and not owner_approved:
                return Decision(False, True, "explicit_owner_approval_required")
            return Decision(True, False, "destructive_action_approved")

        return Decision(True, False, "authorized")
