from pathlib import Path
from tempfile import TemporaryDirectory

from integrations.mentor_learning_loop import MentorLessonState, MentorMethodLesson
from integrations.persistent_mentor_method_store import PersistentMentorMethodStore


def make_method(method_id: str, state: MentorLessonState, method_change: str) -> MentorMethodLesson:
    return MentorMethodLesson(
        mentor_lesson_id=method_id,
        source_lesson_id="mentor-python-debugging-001",
        domain="coding",
        summary="Improve debugging lesson sequencing.",
        method_change=method_change,
        scope_conditions=["debugging lessons"],
        evidence=["attempt-1-partial", "attempt-2-verified"],
        confidence=0.8 if state == MentorLessonState.VALIDATED else 0.5,
        state=state,
    )


def test_persists_across_reopen_and_only_validated_reuses():
    with TemporaryDirectory() as td:
        db = str(Path(td) / "mentor_methods.sqlite")
        store = PersistentMentorMethodStore(db)
        store.save(make_method("m1", MentorLessonState.VALIDATED, "require verification before completion"))
        store.save(make_method("m2", MentorLessonState.CANDIDATE, "candidate only"))
        store.close()

        reopened = PersistentMentorMethodStore(db)
        assert reopened.get_latest("m1") is not None
        assert [x.mentor_lesson_id for x in reopened.list_reusable("coding")] == ["m1"]
        reopened.close()


def test_supersede_keeps_history_and_removes_old_from_reuse():
    with TemporaryDirectory() as td:
        db = str(Path(td) / "mentor_methods.sqlite")
        store = PersistentMentorMethodStore(db)
        store.save(make_method("old", MentorLessonState.VALIDATED, "old method"))
        replacement = make_method("new", MentorLessonState.VALIDATED, "improved method")
        store.supersede("old", replacement)

        assert store.get_latest("old").state == MentorLessonState.SUPERSEDED
        assert len(store.history("old")) == 2
        reusable_ids = {x.mentor_lesson_id for x in store.list_reusable("coding")}
        assert "old" not in reusable_ids
        assert "new" in reusable_ids
        store.close()


def test_reject_stops_reuse_and_preserves_prior_revision():
    with TemporaryDirectory() as td:
        db = str(Path(td) / "mentor_methods.sqlite")
        store = PersistentMentorMethodStore(db)
        store.save(make_method("m1", MentorLessonState.VALIDATED, "method"))
        store.reject("m1", "later evidence contradicted the heuristic")

        assert store.get_latest("m1").state == MentorLessonState.REJECTED
        assert len(store.history("m1")) == 2
        assert store.list_reusable("coding") == []
        store.close()
