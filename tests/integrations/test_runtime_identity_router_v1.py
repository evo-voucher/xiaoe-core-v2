import pytest

from integrations.runtime_identity_router import RuntimeIdentity, RuntimeIdentityRouter


def test_child_facing_routes_to_daughter():
    router = RuntimeIdentityRouter()
    decision = router.route(
        responsibility_domains=["conversation", "learning_support"],
        child_facing=True,
    )
    assert decision.runtime_identity == RuntimeIdentity.DAUGHTER


def test_engineering_routes_to_xiaoe_even_if_child_project_related():
    router = RuntimeIdentityRouter()
    decision = router.route(
        responsibility_domains=["conversation", "architecture", "verification"],
        child_facing=True,
    )
    assert decision.runtime_identity == RuntimeIdentity.XIAOE


def test_ambiguous_non_child_request_defaults_to_xiaoe():
    router = RuntimeIdentityRouter()
    decision = router.route(responsibility_domains=[], child_facing=False)
    assert decision.runtime_identity == RuntimeIdentity.XIAOE


def test_identity_mismatch_is_rejected_before_model_call():
    with pytest.raises(ValueError):
        RuntimeIdentityRouter.assert_identity(RuntimeIdentity.DAUGHTER, "xiaoe")
