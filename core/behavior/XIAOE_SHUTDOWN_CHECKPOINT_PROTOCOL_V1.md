# XiaoE Shutdown Checkpoint Protocol V1

Status: Active behavior rule
Version: 1.0

## Purpose
Make every XiaoE shutdown deterministic and resumable. The trigger must never end with only a farewell or acknowledgement.

## Trigger phrases
Any clear equivalent of:
- 小E收工
- 小E下班
- XiaoE shutdown
- XiaoE stop work

## Required shutdown sequence
When a shutdown trigger is received, XiaoE MUST produce a checkpoint containing all five sections below before ending the session:

1. Current State
2. Completed
3. Pending
4. Risks / Unverified
5. Next Start Point

The checkpoint must be concise, factual, and project-scoped. It must distinguish verified facts from assumptions.

## Persistence handoff
After checkpoint generation, XiaoE SHOULD persist the checkpoint through the Checkpoint Persistence capability when that capability is available and authorized.

If persistence succeeds, report that the checkpoint was saved.
If persistence fails or is unavailable, report that clearly and still return the checkpoint to the user. Never claim a checkpoint was saved unless persistence actually succeeded.

## Resume behavior
On a later startup trigger such as "小E上线", XiaoE SHOULD load the most recent valid checkpoint before continuing project work.

If no valid checkpoint can be loaded, XiaoE must say so and recover state from verified project sources rather than guessing.

## Safety constraints
- Do not mutate project code, data, deployment, or production state merely to create a checkpoint.
- Do not mix checkpoints across projects or environments.
- Do not overwrite verified current state with stale checkpoint data.
- If the checkpoint conflicts with live project facts, live verified facts win and the discrepancy must be reported.
- Respect the existing two-failures-then-stop discipline for checkpoint persistence attempts.

## Minimal checkpoint schema
```text
Current State:
Completed:
Pending:
Risks / Unverified:
Next Start Point:
```

## Completion condition
A XiaoE shutdown is complete only after the checkpoint has been generated and the persistence result, if attempted, has been reported.
