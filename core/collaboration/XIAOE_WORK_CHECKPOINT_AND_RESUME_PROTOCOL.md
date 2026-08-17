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
5. reconstruct the Task Context Pack;
6. state the recovered project and next step internally;
7. continue from that step without requiring Eric to repeat prior work.

If multiple unfinished projects exist and the active one is not inferable from the latest checkpoint or current request, XiaoE should use the most recent clearly active project rather than guessing across projects.

## Continuity Rule

A checkpoint is not permission to trust stale state blindly.

`Resume from checkpoint -> verify live state -> continue.`

Checkpoint memory tells XiaoE where work stopped. GitHub / Supabase / runtime remain the Source of Truth for what is true now.

## Stability Integration

On resume, XiaoE must also restore:
- Architecture Preservation Rule
- Two-Failure Root-Cause Integration Rule
- Stability First
- Stable Core + Open Edges
- Free-first / paid-change approval rule

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
