# XiaoE Memory Contract v1

Status: ACTIVE MEMORY CONTRACT
Purpose: Define how XiaoE persistent memory is read, written, updated, versioned, and isolated.

## 1. Memory Sources Are Separate
1. XiaoE Memory: authoritative persistent AI memory, intended for XiaoE AI Core Supabase `public.memories`.
2. ChatGPT Memory: user background and stable preferences; not authoritative project state.
3. Current Conversation: temporary working context; not persistent truth by itself.

Evidence priority:
Current verified state > XiaoE project memory > ChatGPT memory > current-chat assumptions.

## 2. Namespaces
- `global`: durable system-wide rules and persona-level invariants
- `core`: XiaoE identity and operating principles
- `project`: project-specific decisions and state
- `experience`: verified success/failure lessons
- `organization`: reserved for organization-level persistent memory
- `user`: reserved for user-level persistent memory

## 3. Minimum Memory Record Contract
A persistent memory record should support:
- `id`
- `namespace`
- `memory_type`
- `title`
- `content`
- `importance`
- `project_key`
- `organization_id` nullable
- `user_id` nullable
- `source`
- `tags`
- `metadata`
- `is_active`
- `created_at`
- `updated_at`

The memory table is a knowledge layer, not a chat archive.

## 4. Read Contract
Memory reads must go through a Memory Service / Memory Controller.
Default retrieval filters:
- relevant `project_key`
- relevant `namespace`
- useful `importance`
- `is_active = true`

Do not default to full-table loading.
If persistent memory was not actually loaded, XiaoE must explicitly state that it was not loaded and must not claim memory initialization succeeded.

## 5. Write Contract
Write pipeline:
Candidate -> Judge -> Deduplicate -> Save

Candidate:
- derive a concise potential memory from current verified work

Judge:
- is it future-useful?
- is it verified?
- is it non-sensitive?
- is it durable rather than temporary?

Deduplicate:
- if equivalent active memory exists, update rather than duplicate
- if a newer rule supersedes an older rule, version via activity state

Save:
- new durable fact: INSERT
- updated durable fact/current state: UPDATE
- superseded rule: new active record + old record `is_active = false`

## 6. Conflict Resolution
When a new rule replaces an old rule:
- newest verified rule becomes active
- superseded rule becomes inactive
- preserve historical record
- reads use only current active version unless history is explicitly requested

## 7. Current Project State
Each project should maintain one authoritative current-state memory rather than endlessly appending status snapshots.
Recommended fields/content:
- completed
- current verified state
- unresolved items
- risks
- next step

`XiaoE Finish` / `小E收工` should normally UPDATE this current-state memory.

## 8. Experience Memory
Store only lessons that have been verified by real execution.
Examples:
- a deployment method that succeeded
- a permission model that prevented an error
- a failure pattern and its proven root cause

Do not save speculation as experience.

## 9. Security and Isolation
- No passwords, API keys, JWTs, service-role secrets, or setup codes in memory.
- Minimize personal/customer-sensitive data.
- Future multi-tenant design must isolate memory by `organization_id` / `user_id` with RLS or equivalent authorization.
- AI Providers may not access the memories table directly.

## 10. Retrieval Failure Rule
If Supabase or the configured persistent store cannot be read:
- do not fabricate memory content
- do not show a success indicator
- continue only with clearly labeled verified live state / available context

## 11. Memory Objective
Persistent memory should let XiaoE recover:
- identity and operating principles
- active project context
- durable decisions
- verified experience
- current project state
without requiring full historical chat replay.
