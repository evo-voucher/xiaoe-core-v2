from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class MentorLessonState(str, Enum):
    CANDIDATE = "candidate"
    VALIDATED = "validated"
    SUPERSEDED = "superseded"
    REJECTED = "rejected"


@dataclass(frozen=True)
class DaughterLearningOutcome:
    lesson_id: str
    domain: str
    practice_attempts: int
    passed: bool
    failed_checks: List[str]
    successful_checks: List[str]
    daughter_notes: List[str]
    evidence: List[str]


@dataclass
class MentorMethodLesson:
    mentor_lesson_id: str
    source_lesson_id: str
    domain: str
    summary: str
    method_change: str
    scope_conditions: List[str]
    evidence: List[str]
    confidence: float = 0.0
    state: MentorLessonState = MentorLessonState.CANDIDATE
    contradictions: List[str] = field(default_factory=list)
    supersedes_mentor_lesson_id: Optional[str] = None


class XiaoEMentorLearningLoop:
    """Lets XiaoE learn how to teach/verify better from Daughter outcomes.

    This loop may improve methods, heuristics, lesson sequencing, verification design,
    and mentor routing. It MUST NOT rewrite XiaoE protected core, governance, authority,
    security boundaries, or grant permissions.
    """

    PROTECTED_TARGETS = {
        "identity",
        "governance",
        "authority",
        "permissions",
        "security_boundary",
        "protected_core",
    }

    ALLOWED_TARGETS = {
        "teaching_strategy",
        "lesson_structure",
        "verification_design",
        "debugging_heuristic",
        "mentor_routing",
        "practice_sequencing",
        "explanation_style",
    }

    def propose_method_lesson(
        self,
        outcome: DaughterLearningOutcome,
        *,
        mentor_lesson_id: str,
        target: str,
        summary: str,
        method_change: str,
        scope_conditions: List[str],
    ) -> MentorMethodLesson:
        normalized = target.strip().lower()
        if normalized in self.PROTECTED_TARGETS:
            raise ValueError("Mentor learning cannot modify protected XiaoE core/governance/authority.")
        if normalized not in self.ALLOWED_TARGETS:
            raise ValueError(f"Unsupported mentor-learning target: {target}")
        if not outcome.evidence:
            raise ValueError("Outcome evidence is required before XiaoE may propose a method lesson.")

        evidence = list(outcome.evidence)
        evidence.append(f"practice_attempts={outcome.practice_attempts}")
        evidence.append(f"daughter_passed={outcome.passed}")
        if outcome.failed_checks:
            evidence.append("failed_checks=" + ",".join(outcome.failed_checks))

        return MentorMethodLesson(
            mentor_lesson_id=mentor_lesson_id,
            source_lesson_id=outcome.lesson_id,
            domain=outcome.domain,
            summary=summary,
            method_change=f"{normalized}: {method_change}",
            scope_conditions=list(scope_conditions),
            evidence=evidence,
            confidence=0.5,
        )

    def validate_method_lesson(
        self,
        lesson: MentorMethodLesson,
        *,
        independent_successes: int,
        contradictions: Optional[List[str]] = None,
    ) -> MentorMethodLesson:
        lesson.contradictions.extend(contradictions or [])
        if lesson.contradictions:
            lesson.state = MentorLessonState.CANDIDATE
            lesson.confidence = max(0.1, lesson.confidence - 0.2)
            return lesson

        if independent_successes >= 2:
            lesson.state = MentorLessonState.VALIDATED
            lesson.confidence = max(lesson.confidence, 0.8)
        else:
            lesson.state = MentorLessonState.CANDIDATE
            lesson.confidence = max(lesson.confidence, 0.6 if independent_successes == 1 else 0.5)
        return lesson

    def reusable_method(self, lesson: MentorMethodLesson) -> Optional[str]:
        if lesson.state != MentorLessonState.VALIDATED:
            return None
        return lesson.method_change


def example_debugging_feedback_cycle() -> Dict[str, object]:
    """Reference: Daughter needed two attempts, so XiaoE learns a bounded teaching improvement."""

    outcome = DaughterLearningOutcome(
        lesson_id="mentor-python-debugging-001",
        domain="coding",
        practice_attempts=2,
        passed=True,
        failed_checks=["regression_test_passes", "normal_case_still_passes"],
        successful_checks=[
            "original_failure_reproduced",
            "root_cause_identified",
            "minimal_fix_applied",
            "regression_test_passes",
            "normal_case_still_passes",
        ],
        daughter_notes=["First attempt fixed the bug before completing verification."],
        evidence=["attempt-1-partial", "attempt-2-verified"],
    )
    loop = XiaoEMentorLearningLoop()
    lesson = loop.propose_method_lesson(
        outcome,
        mentor_lesson_id="xiaoe-mentor-method-debug-001",
        target="practice_sequencing",
        summary="Make verification part of the task before a fix can be considered complete.",
        method_change="Require regression and unaffected-normal-case checks in the practice checklist before marking the coding task complete.",
        scope_conditions=["debugging lessons", "code changes with observable prior failure"],
    )
    return {
        "candidate": lesson,
        "reusable": loop.reusable_method(lesson),
    }
