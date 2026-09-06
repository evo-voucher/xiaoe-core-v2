from integrations.runtime_identity_router import RuntimeIdentity, RuntimeIdentityRouter


def test_daughter_drops_engineering_secrets_and_keeps_child_runtime_context():
    router = RuntimeIdentityRouter()
    routed = router.filter_context(
        runtime_identity=RuntimeIdentity.DAUGHTER,
        context={
            "request_text": "help me with homework",
            "age": 7,
            "verified_memory": "likes small-step explanations",
            "repository_secret": "never-forward",
            "api_key": "never-forward",
            "internal_governance_notes": "system-only",
        },
    )

    assert routed.allowed_context["age"] == "7"
    assert "verified_memory" in routed.allowed_context
    assert "repository_secret" not in routed.allowed_context
    assert "api_key" not in routed.allowed_context
    assert "internal_governance_notes" not in routed.allowed_context
    assert set(routed.dropped_keys) >= {
        "repository_secret",
        "api_key",
        "internal_governance_notes",
    }


def test_xiaoe_drops_private_child_context_and_keeps_engineering_evidence():
    router = RuntimeIdentityRouter()
    routed = router.filter_context(
        runtime_identity=RuntimeIdentity.XIAOE,
        context={
            "request_text": "review this runtime change",
            "repository": "daughter-companion-ai",
            "test_evidence": "integration-test-123",
            "private_child_memory": "private",
            "raw_companion_history": "private conversation",
            "unverified_child_profile": "do not infer",
        },
    )

    assert routed.allowed_context["repository"] == "daughter-companion-ai"
    assert routed.allowed_context["test_evidence"] == "integration-test-123"
    assert "private_child_memory" not in routed.allowed_context
    assert "raw_companion_history" not in routed.allowed_context
    assert "unverified_child_profile" not in routed.allowed_context


def test_routing_still_happens_before_model_identity():
    router = RuntimeIdentityRouter()

    system = router.route(
        responsibility_domains=["architecture", "deployment"],
        child_facing=False,
    )
    child = router.route(
        responsibility_domains=["learning_support"],
        child_facing=True,
    )

    assert system.runtime_identity is RuntimeIdentity.XIAOE
    assert child.runtime_identity is RuntimeIdentity.DAUGHTER
