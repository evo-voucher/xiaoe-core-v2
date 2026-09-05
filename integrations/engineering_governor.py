from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Iterable, List, Sequence, Set


class DeliveryState(IntEnum):
    DESIGNED = 1
    CODED = 2
    COMMITTED = 3
    TESTED = 4
    INTEGRATED = 5
    RUNNING = 6
    OBSERVED = 7


class EvidenceLevel(IntEnum):
    CLAIM = 0
    CODE_PRESENT = 1
    UNIT_TESTED = 2
    INTEGRATION_TESTED = 3
    LIVE_RUN = 4
    REPEATED_LIVE_OUTCOME = 5
    LONGITUDINAL_VALIDATION = 6


@dataclass(frozen=True)
class EvidenceItem:
    level: EvidenceLevel
    reference: str
    independent: bool = False


@dataclass(frozen=True)
class ChangeProposal:
    name: str
    touched_domains: Sequence[str]
    description: str = ""
    expands_permissions: bool = False
    changes_protected_core: bool = False
    irreversible: bool = False


@dataclass(frozen=True)
class ImpactAssessment:
    affected_domains: List[str]
    protected_domains_touched: List[str]
    requires_explicit_governance: bool
    requires_authority_review: bool
    recommended_isolation: str
    reasons: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class CapabilityStatus:
    delivery_state: DeliveryState
    evidence_level: EvidenceLevel
    stable_claim_allowed: bool
    wording: str


class XiaoEEngineeringGovernor:
    """Keeps XiaoE precise about state, impact and proof.

    This module is intentionally isolated under integrations/. It does not rewrite
    XiaoE protected core or governance. Its role is to prevent common engineering
    drift such as saying "done" when code only exists, treating one test as proof,
    or changing a protected domain as if it were an ordinary feature update.
    """

    PROTECTED_DOMAINS: Set[str] = {
        "identity",
        "governance",
        "authority",
        "permissions",
        "security_boundary",
        "protected_core",
        "constitution",
    }

    HIGH_IMPACT_DOMAINS: Set[str] = {
        "runtime",
        "memory",
        "migration",
        "model_adapter",
        "robotics",
        "transport",
        "authentication",
        "authorization",
    }

    @classmethod
    def assess_change(cls, proposal: ChangeProposal) -> ImpactAssessment:
        touched = sorted({domain.strip().lower() for domain in proposal.touched_domains if domain.strip()})
        protected = sorted(set(touched) & cls.PROTECTED_DOMAINS)
        reasons: List[str] = []

        requires_governance = bool(protected or proposal.changes_protected_core)
        requires_authority = proposal.expands_permissions or any(
            domain in {"authority", "permissions", "authorization", "robotics"}
            for domain in touched
        )

        if protected:
            reasons.append("Protected domain touched; ordinary self-learning or feature upgrade is insufficient.")
        if proposal.changes_protected_core:
            reasons.append("Proposal explicitly changes protected core and requires constitutional governance.")
        if proposal.expands_permissions:
            reasons.append("Permission expansion requires Authority review; learning cannot grant it.")
        if proposal.irreversible:
            reasons.append("Irreversible change requires stronger review and rollback planning before execution.")

        high_impact = sorted(set(touched) & cls.HIGH_IMPACT_DOMAINS)
        if high_impact:
            reasons.append("High-impact domains affected: " + ", ".join(high_impact))

        if requires_governance:
            isolation = "governance_review_required"
        elif high_impact or proposal.irreversible:
            isolation = "isolated_change_with_regression_and_rollback"
        else:
            isolation = "normal_isolated_change"

        return ImpactAssessment(
            affected_domains=touched,
            protected_domains_touched=protected,
            requires_explicit_governance=requires_governance,
            requires_authority_review=requires_authority,
            recommended_isolation=isolation,
            reasons=reasons,
        )

    @staticmethod
    def strongest_evidence(evidence: Iterable[EvidenceItem]) -> EvidenceLevel:
        items = list(evidence)
        if not items:
            return EvidenceLevel.CLAIM
        return max((item.level for item in items), default=EvidenceLevel.CLAIM)

    @classmethod
    def evaluate_status(
        cls,
        delivery_state: DeliveryState,
        evidence: Iterable[EvidenceItem],
    ) -> CapabilityStatus:
        evidence_items = list(evidence)
        strongest = cls.strongest_evidence(evidence_items)
        independent_live = sum(
            1
            for item in evidence_items
            if item.independent and item.level >= EvidenceLevel.LIVE_RUN
        )

        stable = (
            delivery_state >= DeliveryState.RUNNING
            and strongest >= EvidenceLevel.REPEATED_LIVE_OUTCOME
            and independent_live >= 1
        )

        if delivery_state <= DeliveryState.DESIGNED:
            wording = "designed_not_implemented"
        elif delivery_state == DeliveryState.CODED:
            wording = "code_present_not_committed"
        elif delivery_state == DeliveryState.COMMITTED:
            wording = "committed_not_verified"
        elif delivery_state == DeliveryState.TESTED:
            wording = "tested_not_yet_integrated"
        elif delivery_state == DeliveryState.INTEGRATED:
            wording = "integrated_not_yet_live_observed"
        elif delivery_state == DeliveryState.RUNNING and not stable:
            wording = "running_but_not_yet_stable"
        elif delivery_state >= DeliveryState.OBSERVED and stable:
            wording = "observed_and_stably_supported"
        else:
            wording = "running_with_partial_evidence"

        return CapabilityStatus(
            delivery_state=delivery_state,
            evidence_level=strongest,
            stable_claim_allowed=stable,
            wording=wording,
        )

    @staticmethod
    def can_say_complete(status: CapabilityStatus) -> bool:
        return status.delivery_state >= DeliveryState.INTEGRATED and status.evidence_level >= EvidenceLevel.INTEGRATION_TESTED

    @staticmethod
    def can_say_proven_stable(status: CapabilityStatus) -> bool:
        return status.stable_claim_allowed
