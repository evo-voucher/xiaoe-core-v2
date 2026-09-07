from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Optional


class AccessPath(str, Enum):
    INNER_DIRECT = "inner_direct"
    UNIVERSAL_EXTERNAL_BRIDGE = "universal_external_bridge"


class ActionClass(str, Enum):
    READ = "read"
    HEALTH = "health_check"
    DIAGNOSE = "diagnose"
    WRITE = "write"
    DEPLOY = "deploy"
    MIGRATE = "migrate"
    DELETE = "delete"
    DESTRUCTIVE_REPAIR = "destructive_repair"


OWNER_APPROVAL_ACTIONS = {
    ActionClass.WRITE,
    ActionClass.DEPLOY,
    ActionClass.MIGRATE,
    ActionClass.DELETE,
    ActionClass.DESTRUCTIVE_REPAIR,
}


@dataclass(frozen=True)
class ProjectAccessContext:
    project_key: str
    ownership_scope: str
    management_mode: str
    connection_key: Optional[str] = None
    credential_ref: Optional[str] = None
    connection_status: Optional[str] = None


@dataclass(frozen=True)
class AccessDecision:
    access_path: AccessPath
    owner_approval_required: bool
    connection_required: bool
    reason: str


class ProjectAccessRouter:
    """Choose direct inner access or the single external bridge.

    Internal/authorized-account projects must stay on direct access.
    External-account projects must reuse the Universal External Bridge rather
    than creating a dedicated bridge per project.
    """

    def resolve_path(self, project: ProjectAccessContext) -> AccessPath:
        ownership = project.ownership_scope.strip().lower()
        mode = project.management_mode.strip().lower()

        if mode == "direct" and ownership in {"internal", "same_account", "authorized_account"}:
            return AccessPath.INNER_DIRECT

        if mode == "external_bridge" or ownership in {"external", "external_account", "customer_account"}:
            return AccessPath.UNIVERSAL_EXTERNAL_BRIDGE

        raise ValueError(
            f"Ambiguous project access route for {project.project_key}: "
            f"ownership_scope={project.ownership_scope}, management_mode={project.management_mode}"
        )

    def decide(
        self,
        *,
        project: ProjectAccessContext,
        requested_actions: Iterable[ActionClass],
        owner_approved: bool = False,
    ) -> AccessDecision:
        access_path = self.resolve_path(project)
        actions = set(requested_actions)
        approval_required = bool(actions & OWNER_APPROVAL_ACTIONS)

        if approval_required and not owner_approved:
            return AccessDecision(
                access_path=access_path,
                owner_approval_required=True,
                connection_required=(access_path == AccessPath.UNIVERSAL_EXTERNAL_BRIDGE),
                reason="mutation_blocked_pending_owner_approval",
            )

        if access_path == AccessPath.UNIVERSAL_EXTERNAL_BRIDGE:
            if not project.connection_key or not project.credential_ref:
                return AccessDecision(
                    access_path=access_path,
                    owner_approval_required=approval_required,
                    connection_required=True,
                    reason="external_connection_not_onboarded",
                )
            if (project.connection_status or "").strip().lower() != "authorized":
                return AccessDecision(
                    access_path=access_path,
                    owner_approval_required=approval_required,
                    connection_required=True,
                    reason="external_connection_not_authorized",
                )

        return AccessDecision(
            access_path=access_path,
            owner_approval_required=approval_required,
            connection_required=False,
            reason="ready_for_execution",
        )
