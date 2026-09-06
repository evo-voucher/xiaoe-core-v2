from integrations.mentor_learning_loop import (
    DaughterLearningOutcome,
    MentorLessonState,
    XiaoEMentorLearningLoop,
)


def _outcome() -> DaughterLearningOutcome:
    return DaughterLearningOutcome(
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
        daughter_notes=["First attempt fixed before verification was complete."],
        evidence=["attempt-1-partial", "attempt-2-verified"],
    )


def test_single_outcome_stays_candidate_and_is_not_reusable():
    loop = XiaoEMentorLearningLoop()
    lesson = loop.propose_method_lesson(
        _outcome(),
        mentor_lesson_id="xiaoe-method-001",
        target="practice_sequencing",
        summary="Put verification inside the task definition.",
        method_change="Require regression checks before completion.",
        scope_conditions=["debugging lessons"],
    )
    assert lesson.state == MentorLessonState.CANDIDATE
    assert loop.reusable_method(lesson) is None


def test_two_independent_successes_validate_method_for_reuse():
    loop = XiaoEMentorLearningLoop()
    lesson = loop.propose_method_lesson(
        _outcome(),
        mentor_lesson_id="xiaoe-method-002",
        target="verification_design",
        summary="Explicit verification reduces premature completion.",
        method_change="Show required verification checks before practice starts.",
        scope_conditions=["coding lessons"],
    )
    loop.validate_method_lesson(lesson, independent_successes=2)
    assert lesson.state == MentorLessonState.VALIDATED
    assert loop.reusable_method(lesson) is not None


def test_contradiction_prevents_validation():
    loop = XiaoEMentorLearningLoop()
    lesson = loop.propose_method_lesson(
        _outcome(),
        mentor_lesson_id="xiaoe-method-003",
        target="explanation_style",
        summary="Shorter explanations may help this task type.",
        method_change="Use a shorter pre-practice explanation.",
        scope_conditions=["beginner coding"],
    )
    loop.validate_method_lesson(
        lesson,
        independent_successes=3,
        contradictions=["A later beginner performed worse with the shorter explanation."],
    )
    assert lesson.state == MentorLessonState.CANDIDATE
    assert loop.reusable_method(lesson) is None


def test_protected_core_cannot_be_learning_target():
    loop = XiaoEMentorLearningLoop()
    try:
        loop.propose_method_lesson(
            _outcome(),
            mentor_lesson_id="xiaoe-method-protected",
            target="governance",
            summary="Should never be accepted.",
            method_change="Change governance based on one lesson outcome.",
            scope_conditions=["all"],
        )
    except ValueError as exc:
        assert "protected" in str(exc).lower()
    else:
        raise AssertionError("Protected governance mutation should be rejected")
