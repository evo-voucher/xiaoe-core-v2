from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterable, List, Mapping


HANDOFF_SCHEMA = "xiaoe.runtime.handoff.v1"


class RuntimeIdentity(str, Enum):
    XIAOE = "xiaoe"
    DAUGHTER = "daughter"


@dataclass(frozen=True)
class RoutingDecision:
    runtime_identity: RuntimeIdentity
    reason: str


@dataclass(frozen=True)
class RoutedContext:
    runtime_identity: RuntimeIdentity
    allowed_context: Dict[str, str]
    dropped_keys: List[str]


class RuntimeIdentityRouter:
    """Resolve responsibility and context boundary before any model call.

    XiaoE owns engineering, architecture, verification, upgrade governance,
    mentor screening, system stability, permission/authority architecture,
    and cross-project integration.

    Daughter owns child-facing companionship, learning support, age-appropriate
    conversation, ordinary judgment within her Authority, and use of verified
    memory/skills.

    The language model never decides its own identity. Ambiguous system-level
    requests default to XiaoE because architecture/governance should not be
    silently handled as child-facing Daughter behavior.

    Context is allow-listed by identity so engineering/governance state does not
    silently become Daughter personal context and Daughter personal memory does
    not silently become XiaoE engineering context.
    """

    XIAOE_DOMAINS = {
        "engineering", "architecture", "verification", "testing", "upgrade",
        "governance", "mentor", "system_stability", "permissions",
        "authority_architecture", "migration", "integration", "deployment", "security",
    }

    DAUGHTER_DOMAINS = {
        "companionship", "conversation", "learning_support", "child_support",
        "homework_guidance", "emotional_support", "daily_life", "age_appropriate_guidance",
    }

    CONTEXT_ALLOWLIST = {
        RuntimeIdentity.XIAOE: {
            "request_text", "repository", "project_state", "change_scope", "test_evidence",
            "deployment_state", "authority_design", "mentor_evidence", "runtime_status",
        },
        RuntimeIdentity.DAUGHTER: {
            "request_text", "user_id", "session_id", "age", "maturity", "guardian_state",
            "authority_state", "risk_level", "domain", "embodiment", "verified_memory",
            "verified_skills", "current_facts",
        },
    }

    FORBIDDEN_CROSS_CONTEXT = {
        RuntimeIdentity.XIAOE: {
            "private_child_memory", "raw_companion_history", "unverified_child_profile",
        },
        RuntimeIdentity.DAUGHTER: {
            "repository_secret", "api_key", "service_role_key", "deployment_secret",
            "internal_governance_notes",
        },
    }

    def route(self, *, responsibility_domains: Iterable[str], child_facing: bool) -> RoutingDecision:
        domains = {item.strip().lower() for item in responsibility_domains if item.strip()}
        if domains & self.XIAOE_DOMAINS:
            return RoutingDecision(RuntimeIdentity.XIAOE, "system_engineering_or_governance_responsibility")
        if child_facing or domains & self.DAUGHTER_DOMAINS:
            return RoutingDecision(RuntimeIdentity.DAUGHTER, "child_facing_companion_responsibility")
        return RoutingDecision(RuntimeIdentity.XIAOE, "ambiguous_non_child_facing_request_defaults_to_system_governance")

    def filter_context(self, *, runtime_identity: RuntimeIdentity, context: Mapping[str, object]) -> RoutedContext:
        allow = self.CONTEXT_ALLOWLIST[runtime_identity]
        forbidden = self.FORBIDDEN_CROSS_CONTEXT[runtime_identity]
        allowed_context: Dict[str, str] = {}
        dropped: List[str] = []
        for raw_key, raw_value in context.items():
            key = raw_key.strip().lower()
            if key in forbidden or key not in allow:
                dropped.append(key)
                continue
            allowed_context[key] = str(raw_value)
        return RoutedContext(runtime_identity, allowed_context, sorted(set(dropped)))

    def build_handoff_packet(
        self,
        *,
        decision: RoutingDecision,
        context: Mapping[str, object],
    ) -> Dict[str, object]:
        routed = self.filter_context(runtime_identity=decision.runtime_identity, context=context)
        return {
            "schema": HANDOFF_SCHEMA,
            "runtime_identity": decision.runtime_identity.value,
            "routing_reason": decision.reason,
            "context": dict(routed.allowed_context),
            "dropped_context_keys": list(routed.dropped_keys),
            "claims": {
                "model_may_change_identity": False,
                "model_may_expand_authority": False,
                "context_is_identity_filtered": True,
            },
        }

    @staticmethod
    def assert_identity(expected: RuntimeIdentity, actual: str) -> None:
        if actual.strip().lower() != expected.value:
            raise ValueError(
                f"Runtime identity mismatch: expected={expected.value}, actual={actual}. Route before calling the model."
            )
