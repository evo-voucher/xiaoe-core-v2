from integrations.mentor_reliability import (
    ClaimState,
    MentorClaim,
    MentorProvenance,
    MentorReliabilityGate,
)


def make_claim() -> MentorClaim:
    return MentorClaim(
        claim_id="c1",
        domain="coding",
        statement="Reproduce the bug before patching it.",
        scope_conditions=["debugging"],
        provenance=MentorProvenance(
            mentor_name="ChatGPT",
            provider="OpenAI",
            model="provider-selected",
        ),
    )


def test_single_fluent_answer_is_only_candidate():
    claim = MentorReliabilityGate().assess(make_claim())
    assert claim.state == ClaimState.CANDIDATE
    assert claim.confidence <= 0.3


def test_contradiction_blocks_verification():
    gate = MentorReliabilityGate()
    claim = make_claim()
    gate.confirm(claim, "test:case-a", independent=True)
    gate.confirm(claim, "run:case-b", independent=True)
    assert claim.state == ClaimState.VERIFIED

    gate.add_contradiction(claim, "verified-source:counterexample")
    assert claim.state == ClaimState.CONFLICTED
    assert not gate.reusable(claim)


def test_one_independent_confirmation_plus_executable_evidence_can_verify():
    gate = MentorReliabilityGate()
    claim = make_claim()
    gate.confirm(claim, "test:original-failure-reproduced", independent=False)
    gate.confirm(claim, "run:regression-passes", independent=True)
    assert claim.state == ClaimState.VERIFIED
    assert gate.reusable(claim)


def test_two_independent_confirmations_verify_even_without_executable_marker():
    gate = MentorReliabilityGate()
    claim = make_claim()
    gate.confirm(claim, "independent-review-a", independent=True)
    assert claim.state == ClaimState.CANDIDATE
    gate.confirm(claim, "independent-review-b", independent=True)
    assert claim.state == ClaimState.VERIFIED


def test_empty_claim_is_rejected():
    gate = MentorReliabilityGate()
    claim = make_claim()
    claim.statement = "   "
    gate.assess(claim)
    assert claim.state == ClaimState.REJECTED
