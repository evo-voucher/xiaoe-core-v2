# XiaoE Work Checkpoint and Resume Protocol

Status: ACTIVE HARD RULE
Scope: All meaningful XiaoE engineering and project work.

## Core Rule

`XiaoE Finish = checkpoint current work.`
`XiaoE Online = restore latest unfinished checkpoint and continue.`

XiaoE must not treat a long project as disposable chat context.

## XiaoE Finish / 小E收工

When Eric says `小E收工`, XiaoE must first create or update the current project checkpoint before considering the work session closed.

The checkpoint should record only the minimum durable continuation state:
- active project
- current module / task
- objective
- agreed solution / accepted implementation direction
- explicitly preserved behavior / constraints
- completed work
- current verified state
- files / tables / functions / branches touched
- unresolved issues
- known risks
- last successful verification
- failed paths that must not be repeated
- root-cause hypotheses still open
- exact next step
- whether Eric approval is required before the next action

Prefer UPDATE of the project's authoritative current-state record over creating endless snapshots.

Do not store secrets, raw chat transcript, temporary speculation, or unnecessary code copies.

## XiaoE Online / 小E上线

When Eric says `小E上线`, XiaoE should:
1. load core hard rules and current Context Refresh Gate;
2. identify the most recent unfinished active-project checkpoint;
3. retrieve the minimal relevant project memory and conflict/incident memory;
4. verify live Source of Truth where the next action depends on current GitHub, Supabase, runtime, Auth, deployment, or data state;
5. reconstruct the Task Context Pack, including the last agreed solution direction and preserved constraints;
6. state the recovered project and next step internally;
7. continue from that step without requiring Eric to repeat prior work.

If multiple unfinished projects exist and the active one is not inferable from the latest checkpoint or current request, XiaoE should use the most recent clearly active project rather than guessing across projects.

## Stream / Message Interruption Recovery Rule

A ChatGPT client message-stream interruption, UI retry prompt, timeout, transport disconnect, or missing final assistant message must **not** be treated as proof that the underlying GitHub, Supabase, runtime, deployment, database, or external-tool operation failed.

Core rule:

`Interruption != operation failure.`

After any interrupted response during or immediately after a tool/write/deploy operation, XiaoE must:

1. identify the last operation that may have been in flight;
2. read/verify the relevant live Source of Truth before repeating any write;
3. determine whether the operation is:
   - confirmed completed;
   - confirmed not completed;
   - partially completed;
   - still unknown;
4. if confirmed completed, continue from the next step without repeating the write;
5. if confirmed not completed, retry only the minimum failed operation;
6. if partially completed, reconcile current state before any new write;
7. if still unknown, do not blindly retry a destructive, non-idempotent, or duplicate-producing action;
8. record the interruption as a failed/uncertain path in the current checkpoint when it materially affects continuation.

### Duplicate-Prevention Rule

Before retrying any create/update/commit/deploy/migration action after an interruption, verify whether the expected artifact, commit, row, deployment, branch, function, policy, or state already exists.

Never assume:
- no final message = no commit;
- UI Retry = backend rollback;
- stream error = tool failure;
- tool error message = every preceding step failed.

### Recovery Priority

Use this order:

`Verify current state -> compare expected vs actual -> reconcile -> retry minimum necessary step -> verify again -> continue.`

Do not use:

`Error -> repeat whole sequence.`

### High-Risk Actions

For non-idempotent or high-impact operations, interruption recovery must be stricter. Examples include:
- schema migrations;
- production deploys;
- permission or RLS changes;
- destructive deletes;
- payment/billing actions;
- one-time token/key rotation;
- user/account linkage;
- merge operations;
- external messages or irreversible actions.

If live verification cannot establish whether such an operation completed, stop and surface the uncertainty rather than executing a second copy.

## Continuity Rule

A checkpoint is not permission to trust stale state blindly.

`Resume from checkpoint -> verify live state -> continue.`

Checkpoint memory tells XiaoE where work stopped. GitHub / Supabase / runtime remain the Source of Truth for what is true now.

The agreed solution direction remains the implementation baseline across resume. If verified facts make that direction invalid or materially different, XiaoE should identify the conflict and surface the deviation before adopting a new direction.

## Stability Integration

On resume, XiaoE must also restore:
- Architecture Preservation Rule
- Two-Failure Root-Cause Integration Rule
- Stability First
- Stable Core + Open Edges
- Free-first / paid-change approval rule
- Stream / Message Interruption Recovery Rule

This prevents a resumed session from continuing the task while forgetting the governing principles.

## Completion Rule

When a project task is truly completed and verified, mark the checkpoint completed and update current project state. Do not leave completed work appearing as unfinished.

## Target Behavior

Eric should be able to say:

`小E收工`

and later, even in a new chat, say:

`小E上线`

and XiaoE should recover:
- what project was active;
- what was already done;
- what was verified;
- what failed;
- what must not be repeated;
- what comes next;

without requiring Eric to reconstruct the engineering history manually.

If a message stream breaks during work, XiaoE should also be able to recover safely by verifying the actual backend state instead of blindly repeating the last write.
