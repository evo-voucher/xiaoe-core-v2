from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Dict, Iterable, Mapping, Tuple


class ConnectionState(str, Enum):
    AUTHORIZED = "authorized"
    DEGRADED = "degraded"
    REVOKED = "revoked"


@dataclass(frozen=True)
class ServiceBinding:
    service: str
    credential_ref: str
    resource_ref: str
    state: ConnectionState = ConnectionState.AUTHORIZED


@dataclass(frozen=True)
class ExternalProjectConnection:
    project_key: str
    connection_key: str
    services: Mapping[str, ServiceBinding]
    state: ConnectionState = ConnectionState.AUTHORIZED
    active_write_sessions: Tuple[str, ...] = field(default_factory=tuple)

    def require_service(self, service: str) -> ServiceBinding:
        key = service.strip().lower()
        binding = self.services.get(key)
        if binding is None:
            raise KeyError(f"Service not bound for project {self.project_key}: {key}")
        if self.state == ConnectionState.REVOKED or binding.state == ConnectionState.REVOKED:
            raise PermissionError(f"External access revoked for {self.project_key}/{key}")
        return binding


class ExternalConnectionRegistry:
    """In-memory contract for one master bridge with isolated project bindings.

    Real credentials never belong here. Only vault/provider references are stored.
    A project can bind multiple services (for example GitHub + Supabase), while
    every lookup is scoped by project_key so another project's credentials cannot
    be selected accidentally.
    """

    def __init__(self) -> None:
        self._projects: Dict[str, ExternalProjectConnection] = {}

    def register(self, connection: ExternalProjectConnection) -> None:
        if not connection.project_key.strip() or not connection.connection_key.strip():
            raise ValueError("project_key and connection_key are required")
        if not connection.services:
            raise ValueError("at least one service binding is required")
        normalized: Dict[str, ServiceBinding] = {}
        for name, binding in connection.services.items():
            key = name.strip().lower()
            if key != binding.service.strip().lower():
                raise ValueError(f"service map key mismatch: {name} != {binding.service}")
            if not binding.credential_ref.startswith(("vault://", "provider://")):
                raise ValueError("credential_ref must be an opaque vault/provider reference")
            normalized[key] = replace(binding, service=key)
        self._projects[connection.project_key] = replace(connection, services=normalized)

    def get(self, project_key: str) -> ExternalProjectConnection:
        try:
            return self._projects[project_key]
        except KeyError as exc:
            raise KeyError(f"Unknown external project: {project_key}") from exc

    def resolve_service(self, project_key: str, service: str) -> ServiceBinding:
        return self.get(project_key).require_service(service)

    def start_write_session(self, project_key: str, approval_id: str) -> ExternalProjectConnection:
        if not approval_id.strip():
            raise ValueError("approval_id is required")
        current = self.get(project_key)
        if current.state != ConnectionState.AUTHORIZED:
            raise PermissionError(f"Project connection is not authorized: {project_key}")
        sessions = tuple(dict.fromkeys((*current.active_write_sessions, approval_id)))
        updated = replace(current, active_write_sessions=sessions)
        self._projects[project_key] = updated
        return updated

    def end_write_session(self, project_key: str, approval_id: str) -> ExternalProjectConnection:
        current = self.get(project_key)
        updated = replace(
            current,
            active_write_sessions=tuple(x for x in current.active_write_sessions if x != approval_id),
        )
        self._projects[project_key] = updated
        return updated

    def revoke_project(self, project_key: str) -> ExternalProjectConnection:
        """Full disconnect contract.

        Runtime/provider adapters must also revoke the provider grants and delete
        the referenced vault secrets. This registry step removes all usable
        service bindings and active write sessions while retaining only a
        non-secret tombstone for audit/history.
        """
        current = self.get(project_key)
        revoked_services = {
            key: replace(binding, credential_ref="revoked://deleted", state=ConnectionState.REVOKED)
            for key, binding in current.services.items()
        }
        updated = replace(
            current,
            services=revoked_services,
            state=ConnectionState.REVOKED,
            active_write_sessions=(),
        )
        self._projects[project_key] = updated
        return updated

    def list_authorized_projects(self) -> Iterable[str]:
        return tuple(
            key for key, value in self._projects.items() if value.state == ConnectionState.AUTHORIZED
        )
