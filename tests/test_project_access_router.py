from integrations.project_access_router import (
    AccessPath,
    ActionClass,
    ProjectAccessContext,
    ProjectAccessRouter,
)


def test_internal_project_uses_inner_direct():
    router = ProjectAccessRouter()
    project = ProjectAccessContext(
        project_key="internal_demo",
        ownership_scope="same_account",
        management_mode="direct",
    )
    decision = router.decide(project=project, requested_actions=[ActionClass.HEALTH])
    assert decision.access_path == AccessPath.INNER_DIRECT
    assert decision.reason == "ready_for_execution"


def test_external_project_reuses_universal_bridge():
    router = ProjectAccessRouter()
    project = ProjectAccessContext(
        project_key="customer_demo",
        ownership_scope="external_account",
        management_mode="external_bridge",
        connection_key="ext_customer_demo",
        credential_ref="vault://ext_customer_demo",
        connection_status="authorized",
    )
    decision = router.decide(project=project, requested_actions=[ActionClass.DIAGNOSE])
    assert decision.access_path == AccessPath.UNIVERSAL_EXTERNAL_BRIDGE
    assert decision.reason == "ready_for_execution"


def test_external_write_waits_for_owner_approval():
    router = ProjectAccessRouter()
    project = ProjectAccessContext(
        project_key="customer_demo",
        ownership_scope="external_account",
        management_mode="external_bridge",
        connection_key="ext_customer_demo",
        credential_ref="vault://ext_customer_demo",
        connection_status="authorized",
    )
    decision = router.decide(project=project, requested_actions=[ActionClass.WRITE])
    assert decision.owner_approval_required is True
    assert decision.reason == "mutation_blocked_pending_owner_approval"


def test_external_write_runs_after_owner_approval():
    router = ProjectAccessRouter()
    project = ProjectAccessContext(
        project_key="customer_demo",
        ownership_scope="external_account",
        management_mode="external_bridge",
        connection_key="ext_customer_demo",
        credential_ref="vault://ext_customer_demo",
        connection_status="authorized",
    )
    decision = router.decide(
        project=project,
        requested_actions=[ActionClass.WRITE],
        owner_approved=True,
    )
    assert decision.reason == "ready_for_execution"


def test_external_project_without_onboarding_requests_connection_once():
    router = ProjectAccessRouter()
    project = ProjectAccessContext(
        project_key="customer_demo",
        ownership_scope="external_account",
        management_mode="external_bridge",
    )
    decision = router.decide(project=project, requested_actions=[ActionClass.READ])
    assert decision.connection_required is True
    assert decision.reason == "external_connection_not_onboarded"
