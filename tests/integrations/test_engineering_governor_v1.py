from integrations.engineering_governor import (
    ChangeProposal,
    DeliveryState,
    EvidenceItem,
    EvidenceLevel,
    XiaoEEngineeringGovernor,
)


def test_protected_core_change_requires_governance():
    result = XiaoEEngineeringGovernor.assess_change(
        ChangeProposal(
            name="rewrite identity behavior",
            touched_domains=["identity", "runtime"],
            changes_protected_core=True,
        )
    )
    assert result.requires_explicit_governance is True
    assert "identity" in result.protected_domains_touched
    assert result.recommended_isolation == "governance_review_required"


def test_permission_expansion_requires_authority_review():
    result = XiaoEEngineeringGovernor.assess_change(
        ChangeProposal(
            name="grant robot motion permission",
            touched_domains=["robotics", "permissions"],
            expands_permissions=True,
        )
    )
    assert result.requires_authority_review is True


def test_committed_code_is_not_stable_proof():
    status = XiaoEEngineeringGovernor.evaluate_status(
        DeliveryState.COMMITTED,
        [EvidenceItem(EvidenceLevel.CODE_PRESENT, "commit:abc")],
    )
    assert status.stable_claim_allowed is False
    assert XiaoEEngineeringGovernor.can_say_proven_stable(status) is False
    assert status.wording == "committed_not_verified"


def test_integration_test_can_support_complete_but_not_proven_stable():
    status = XiaoEEngineeringGovernor.evaluate_status(
        DeliveryState.INTEGRATED,
        [EvidenceItem(EvidenceLevel.INTEGRATION_TESTED, "test:integration")],
    )
    assert XiaoEEngineeringGovernor.can_say_complete(status) is True
    assert XiaoEEngineeringGovernor.can_say_proven_stable(status) is False


def test_repeated_live_outcome_plus_independent_evidence_can_support_stable_claim():
    status = XiaoEEngineeringGovernor.evaluate_status(
        DeliveryState.OBSERVED,
        [
            EvidenceItem(EvidenceLevel.LIVE_RUN, "run:1", independent=True),
            EvidenceItem(EvidenceLevel.REPEATED_LIVE_OUTCOME, "run:repeat"),
        ],
    )
    assert status.stable_claim_allowed is True
    assert XiaoEEngineeringGovernor.can_say_proven_stable(status) is True
    assert status.wording == "observed_and_stably_supported"
