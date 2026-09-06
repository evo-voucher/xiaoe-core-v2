from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional

from integrations.mentor_learning_loop import MentorLessonState, MentorMethodLesson


class PersistentMentorMethodStore:
    """SQLite-backed versioned store for XiaoE mentor-method learning only.

    This store intentionally persists teaching/verification heuristics, not
    XiaoE protected Identity, Governance, Authority, Permissions, Security
    Boundaries, or Protected Core.
    """

    def __init__(self, db_path: str) -> None:
        self.db_path = str(Path(db_path))
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mentor_method_revisions (
                mentor_lesson_id TEXT NOT NULL,
                revision INTEGER NOT NULL,
                source_lesson_id TEXT NOT NULL,
                domain TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                state TEXT NOT NULL,
                confidence REAL NOT NULL,
                supersedes_mentor_lesson_id TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (mentor_lesson_id, revision)
            )
            """
        )
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_mentor_method_state ON mentor_method_revisions(state)"
        )
        self._conn.commit()

    def _next_revision(self, mentor_lesson_id: str) -> int:
        row = self._conn.execute(
            "SELECT COALESCE(MAX(revision), 0) AS max_revision FROM mentor_method_revisions WHERE mentor_lesson_id = ?",
            (mentor_lesson_id,),
        ).fetchone()
        return int(row["max_revision"]) + 1

    def save(self, lesson: MentorMethodLesson) -> int:
        revision = self._next_revision(lesson.mentor_lesson_id)
        payload = asdict(lesson)
        payload["state"] = lesson.state.value
        self._conn.execute(
            """
            INSERT INTO mentor_method_revisions
            (mentor_lesson_id, revision, source_lesson_id, domain, payload_json, state, confidence, supersedes_mentor_lesson_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                lesson.mentor_lesson_id,
                revision,
                lesson.source_lesson_id,
                lesson.domain,
                json.dumps(payload, ensure_ascii=False, sort_keys=True),
                lesson.state.value,
                float(lesson.confidence),
                lesson.supersedes_mentor_lesson_id,
            ),
        )
        self._conn.commit()
        return revision

    def get_latest(self, mentor_lesson_id: str) -> Optional[MentorMethodLesson]:
        row = self._conn.execute(
            """
            SELECT payload_json FROM mentor_method_revisions
            WHERE mentor_lesson_id = ? ORDER BY revision DESC LIMIT 1
            """,
            (mentor_lesson_id,),
        ).fetchone()
        return self._decode(row["payload_json"]) if row else None

    def history(self, mentor_lesson_id: str) -> List[MentorMethodLesson]:
        rows = self._conn.execute(
            """
            SELECT payload_json FROM mentor_method_revisions
            WHERE mentor_lesson_id = ? ORDER BY revision ASC
            """,
            (mentor_lesson_id,),
        ).fetchall()
        return [self._decode(row["payload_json"]) for row in rows]

    def list_reusable(self, domain: Optional[str] = None) -> List[MentorMethodLesson]:
        query = """
            SELECT mm.payload_json
            FROM mentor_method_revisions mm
            JOIN (
                SELECT mentor_lesson_id, MAX(revision) AS max_revision
                FROM mentor_method_revisions GROUP BY mentor_lesson_id
            ) latest
            ON mm.mentor_lesson_id = latest.mentor_lesson_id AND mm.revision = latest.max_revision
            WHERE mm.state = ?
        """
        params: List[object] = [MentorLessonState.VALIDATED.value]
        if domain is not None:
            query += " AND mm.domain = ?"
            params.append(domain)
        rows = self._conn.execute(query, tuple(params)).fetchall()
        return [self._decode(row["payload_json"]) for row in rows]

    def supersede(self, old_id: str, replacement: MentorMethodLesson) -> None:
        old = self.get_latest(old_id)
        if old is None:
            raise KeyError(old_id)
        old.state = MentorLessonState.SUPERSEDED
        self.save(old)
        replacement.supersedes_mentor_lesson_id = old_id
        self.save(replacement)

    def reject(self, mentor_lesson_id: str, contradiction: str) -> MentorMethodLesson:
        lesson = self.get_latest(mentor_lesson_id)
        if lesson is None:
            raise KeyError(mentor_lesson_id)
        lesson.state = MentorLessonState.REJECTED
        lesson.contradictions.append(contradiction)
        self.save(lesson)
        return lesson

    def close(self) -> None:
        self._conn.close()

    @staticmethod
    def _decode(payload_json: str) -> MentorMethodLesson:
        payload = json.loads(payload_json)
        return MentorMethodLesson(
            mentor_lesson_id=payload["mentor_lesson_id"],
            source_lesson_id=payload["source_lesson_id"],
            domain=payload["domain"],
            summary=payload["summary"],
            method_change=payload["method_change"],
            scope_conditions=list(payload["scope_conditions"]),
            evidence=list(payload["evidence"]),
            confidence=float(payload.get("confidence", 0.0)),
            state=MentorLessonState(payload["state"]),
            contradictions=list(payload.get("contradictions", [])),
            supersedes_mentor_lesson_id=payload.get("supersedes_mentor_lesson_id"),
        )
