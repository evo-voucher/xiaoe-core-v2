import pytest

from integrations.external_connection_lifecycle import (
    ConnectionState,
    ExternalConnectionRegistry,
    ExternalProjectConnection,
    ServiceBinding,
)


def project(project_key: str, github_ref: str, supabase_ref: str) -> ExternalProjectConnection:
    return ExternalProjectConnection(
        project_key=project_key,
        connection_key=f"ext_{project_key}",
        services={
            "github": ServiceBinding("github", github_ref, f"repo://{project_key}"),
            "supabase": ServiceBinding("supabase", supabase_ref, f"supabase://{project_key}"),
        },
    )


def test_one_master_bridge_can_hold_multiple_services_per_project():
    registry = ExternalConnectionRegistry()
    registry.register(project("a", "vault://a/github", "vault://a/supabase"))
    assert registry.resolve_service("a", "github").credential_ref == "vault://a/github"
    assert registry.resolve_service("a", "supabase").credential_ref == "vault://a/supabase"


def test_projects_are_credential_isolated():
    registry = ExternalConnectionRegistry()
    registry.register(project("a", "vault://a/github", "vault://a/supabase"))
    registry.register(project("b", "vault://b/github", "vault://b/supabase"))
    assert registry.resolve_service("a", "github").credential_ref != registry.resolve_service("b", "github").credential_ref
    assert registry.resolve_service("a", "supabase").credential_ref != registry.resolve_service("b", "supabase").credential_ref


def test_write_session_is_scoped_to_one_project():
    registry = ExternalConnectionRegistry()
    registry.register(project("a", "vault://a/github", "vault://a/supabase"))
    registry.register(project("b", "vault://b/github", "vault://b/supabase"))
    registry.start_write_session("a", "approval-123")
    assert registry.get("a").active_write_sessions == ("approval-123",)
    assert registry.get("b").active_write_sessions == ()


def test_full_revoke_removes_usable_credentials_and_sessions():
    registry = ExternalConnectionRegistry()
    registry.register(project("a", "vault://a/github", "vault://a/supabase"))
    registry.start_write_session("a", "approval-123")
    revoked = registry.revoke_project("a")
    assert revoked.state == ConnectionState.REVOKED
    assert revoked.active_write_sessions == ()
    assert all(binding.credential_ref == "revoked://deleted" for binding in revoked.services.values())
    with pytest.raises(PermissionError):
        registry.resolve_service("a", "github")


def test_raw_secret_like_reference_is_rejected():
    registry = ExternalConnectionRegistry()
    bad = ExternalProjectConnection(
        project_key="a",
        connection_key="ext_a",
        services={"github": ServiceBinding("github", "ghp_actual_secret", "repo://a")},
    )
    with pytest.raises(ValueError):
        registry.register(bad)
