from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List


VALID_ACTIONS = {"read", "copy", "manage"}


@dataclass(frozen=True)
class RegistrationDecision:
    approved: bool
    reason: str
    resource_entry: Dict[str, Any] | None = None


class ResourceRegistrationFlow:
    """Owner-controlled promotion of discovered resources into the registry.

    Discovery alone never grants access. Registration requires explicit owner
    approval and an explicit permission set. Destructive permission is never
    granted here; it remains a per-operation approval handled by the gate.
    """

    def __init__(self, registry: Dict[str, Any]):
        self.registry = registry

    def approve(
        self,
        *,
        service: str,
        identity: str,
        permissions: Iterable[str],
        owner_approved: bool,
    ) -> RegistrationDecision:
        if not owner_approved:
            return RegistrationDecision(False, "owner_approval_required")

        requested = set(permissions)
        if not requested:
            return RegistrationDecision(False, "at_least_one_permission_required")
        if not requested.issubset(VALID_ACTIONS):
            return RegistrationDecision(False, "invalid_permission_requested")

        if service == "github":
            resource_key = f"github_{identity.lower().replace('-', '_')}"
            entry = {
                "resource_key": resource_key,
                "service": "github",
                "account": identity,
                "scope": "installed_account",
                "status": "authorized",
                "policy": {
                    "read": "read" in requested,
                    "copy_out": "copy" in requested,
                    "manage": "manage" in requested,
                    "destructive": "explicit_owner_approval",
                },
            }
        elif service == "supabase":
            resource_key = f"supabase_{identity}"
            entry = {
                "resource_key": resource_key,
                "service": "supabase",
                "organization_id": identity,
                "scope": "organization_projects",
                "status": "authorized",
                "policy": {
                    "read": "read" in requested,
                    "copy_out": "copy" in requested,
                    "manage": "manage" in requested,
                    "destructive": "explicit_owner_approval",
                },
            }
        else:
            return RegistrationDecision(False, "unsupported_service")

        return RegistrationDecision(True, "approved_for_registry_write", entry)

    def apply(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        resources: List[Dict[str, Any]] = list(self.registry.get("resources", []))
        existing = next(
            (r for r in resources if r.get("resource_key") == entry.get("resource_key")),
            None,
        )
        if existing:
            raise ValueError("resource_already_registered")
        updated = dict(self.registry)
        updated["resources"] = [*resources, entry]
        return updated
