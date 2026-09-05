# XiaoE Checkpoint Resume Contract v1

Status: CANDIDATE
Scope: Runtime adapter contract only

## Purpose

Provide one deterministic resume path for `小E上线` without creating a second checkpoint store or redefining Memory ownership.

## Ownership

This contract follows the completed Memory Ownership Map and Duplicate Responsibility Audit.

- Checkpoint lifecycle owner: `core/collaboration/XIAOE_WORK_CHECKPOINT_AND_RESUME_PROTOCOL.md`
- Durable project-state policy owner: `core/memory/XIAOE_MEMORY_CONTRACT_V1.md`
- Durable storage owner: XiaoE Core Supabase `public.memories`
- Canonical update service: `service_update_current_project_state(...)`
- Runtime transport owner: `supabase/functions/memory-gateway/index.ts`
- Runtime caller adapter: `core/runtime/XIAOE_RUNTIME_CLIENT_V1.ts`

No new checkpoint table, memory type, JSON persistence format, or transcript store is introduced.

## Canonical durable identity

A resumable Current Project State is an active memory satisfying all of:

- `namespace = 'project'`
- `memory_type = 'current_project_state'`
- `project_key = requested project key`
- `is_active = true`

There must be at most one active Current Project State for a project.

## Write contract — `小E收工`

The session lifecycle may call:

`updateCurrentProjectState(...)`

which transports the existing `update_project_state` action to the memory gateway and existing `service_update_current_project_state(...)` RPC.

The durable state should contain only the minimum continuation payload required by the Checkpoint Protocol, for example:

- active project;
- current task/module;
- objective;
- agreed direction;
- preserved constraints;
- completed work;
- verified state;
- files/tables/functions/branches touched;
- unresolved items;
- risks;
- last successful verification;
- failed paths/hypotheses where still relevant;
- exact next step;
- approval requirement.

Do not persist raw transcript or temporary reasoning.

## Read contract — `小E上线`

The runtime adapter exposes:

`readCurrentProjectState(projectKey)`

Behavior:

1. Reject an empty project key.
2. Read only project-scoped memory through the existing gateway path.
3. Select only the canonical Current Project State identity.
4. Return `null` if no active Current Project State exists.
5. Return the state if exactly one exists.
6. Fail closed if more than one active Current Project State exists.

The helper is an adapter convenience only. It does not own retrieval ranking, checkpoint policy, or persistence semantics.

## Resume safety rule

A recovered checkpoint is continuation context, not live-world truth.

After retrieval:

1. restore the minimum Task Context Pack / continuation context;
2. identify which facts are time-sensitive or mutation-sensitive;
3. verify those facts against the live Source of Truth;
4. reconcile differences;
5. continue from the smallest safe next step.

Never replay a high-risk write, merge, deploy, schema change, Auth/RLS change, or irreversible action solely because the checkpoint says it was next.

## Interruption rule

Interruption is not proof of failure.

On resume after an interrupted write/tool action:

`verify current state -> compare expected vs actual -> reconcile -> retry minimum necessary -> verify again -> continue`

This prevents duplicate writes after tool/network interruption.

## Ambiguity rule

If multiple active Current Project State records are detected, the runtime must stop rather than choose one by recency, importance, provider preference, or guesswork.

Reason:

`multiple active current_project_state records = ownership/state-integrity violation`

Recovery requires conflict inspection and explicit reconciliation through the existing Memory path.

## Non-goals

This contract does not:

- add a `checkpoints` table;
- add a new memory type;
- create a second project-state RPC;
- modify Memory Fusion ranking;
- replace Task Context Pack;
- change gateway authorization;
- alter Supabase schema;
- deploy anything.

## Acceptance criteria

Checkpoint persistence/resume v1 is structurally ready when:

- write path remains `update_project_state` -> `service_update_current_project_state`;
- read path has deterministic `readCurrentProjectState(projectKey)` behavior;
- zero state returns `null`;
- exactly one state returns that state;
- multiple active states fail closed;
- resume requires live re-verification before material mutation;
- no shadow persistence implementation exists.
