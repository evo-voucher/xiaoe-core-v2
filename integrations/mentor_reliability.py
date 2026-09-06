from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class ClaimState(str, Enum):
    CANDIDATE = "candidate"
    VERIFIED = "verified"
    CONFLICTED = "conflicted"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


@dataclass(frozen=True)
class MentorProvenance:
    mentor_name: str
    provider: str
    model: str
    session_ref: Optional[str] = None


@dataclass
class MentorClaim:
    claim_id: str
    domain: str
    statement: str
    scope_conditions: List[str]
    provenance: MentorProvenance
    evidence: List[str] = field(default_factory=list)
    contradictions: List[str] = field(default_factory=list)
    independent_confirmations: int = 0
    confidence: float = 0.0
    state: ClaimState = ClaimState.CANDIDATE


class MentorReliabilityGate:
    """Screens mentor claims before they can be treated as reusable teaching material.

    Rules:
    - Mentor authority is never inferred from fluency/confidence.
    - One model answer remains a candidate.
    - Contradictions block verification until resolved.
    - Independent confirmation or executable evidence is required for verification.
    - High confidence language cannot substitute for evidence.
    """

    def assess(self, claim: MentorClaim) -> MentorClaim:
        if not claim.statement.strip():
            claim.state = ClaimState.REJECTED
            claim.confidence = 0.0
            return claim

        if claim.contradictions:
            claim.state = ClaimState.CONFLICTED
            claim.confidence = min(claim.confidence, 0.4)
            return claim

        executable_evidence = any(
            marker.startswith(("test:", "run:", "measurement:", "verified-source:"))
            for marker in claim.evidence
        )

        if claim.independent_confirmations >= 2 or (
            claim.independent_confirmations >= 1 and executable_evidence
        ):
            claim.state = ClaimState.VERIFIED
            claim.confidence = max(claim.confidence, 0.8)
            return claim

        claim.state = ClaimState.CANDIDATE
        claim.confidence = max(claim.confidence, 0.3 if claim.evidence else 0.1)
        return claim

    def add_contradiction(self, claim: MentorClaim, contradiction: str) -> MentorClaim:
        claim.contradictions.append(contradiction)
        return self.assess(claim)

    def confirm(self, claim: MentorClaim, evidence: str, *, independent: bool = True) -> MentorClaim:
        claim.evidence.append(evidence)
        if independent:
            claim.independent_confirmations += 1
        return self.assess(claim)

    def reusable(self, claim: MentorClaim) -> bool:
        return claim.state == ClaimState.VERIFIED


def reference_flow() -> MentorClaim:
    claim = MentorClaim(
        claim_id="mentor-claim-debug-001",
        domain="coding",
        statement="A debugging fix should reproduce the original failure and verify unaffected normal behavior.",
        scope_conditions=["software debugging", "observable regression"],
        provenance=MentorProvenance(
            mentor_name="ChatGPT",
            provider="OpenAI",
            model="provider-selected",
        ),
    )
    gate = MentorReliabilityGate()
    gate.assess(claim)  # still candidate: one fluent answer is not proof
    gate.confirm(claim, "test:original-failure-reproduced", independent=False)
    gate.confirm(claim, "run:regression-and-normal-case-pass", independent=True)
    return claim
