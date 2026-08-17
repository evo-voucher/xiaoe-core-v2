# XiaoE Memory Fusion Architecture v3

Status: ACTIVE

## Objective
XiaoE must not depend on replaying long chat history. It should restore the smallest trustworthy context needed for the current task, verify live sources, execute, then persist only durable conclusions.

## Closed Loop
Eric intent
→ Task Interpreter
→ Retrieval Router
→ Fusion Retrieve
→ Conflict Scan
→ Task Context Pack
→ AI Brain / Provider
→ Tools (GitHub, Supabase, etc.)
→ Verification
→ Memory Write-back
→ Project State Update

## Memory Classes
- `global`: system-wide invariants
- `core`: XiaoE identity and operating principles
- `project`: project state and verified project decisions
- `experience`: proven failure/success lessons
- `organization`: organization-scoped knowledge
- `user`: user-scoped knowledge

Memory stores conclusions, not chat transcripts.

## Trust Model
Evidence priority remains:
`live verified source > verified XiaoE project memory > stable user memory > current-chat assumption`

Each memory can now carry:
- `verification_status`: candidate / verified / disputed / deprecated
- `confidence`: 1-10
- `source_priority`: 0-100
- `last_verified_at`
- `valid_until`
- `supersedes_id`
- deterministic `memory_key`

Only active, verified, unexpired memories participate in normal Fusion Retrieve.

## Fusion Retrieve v3
The first production version is deliberately lean and cost-free.

Ranking uses:
- importance
- confidence
- source priority
- exact project match
- global/core relevance
- tag overlap
- title/content query match
- recent verification

No paid embeddings are required in v3. Semantic/vector retrieval may be added later behind the same contract when memory volume justifies it.

## Conflict Detection
The service detects:
- duplicate active `memory_key` records
- a superseded record that is still active

Conflicts are surfaced in the Task Context Pack rather than silently ignored.

## Task Context Pack
Every autonomous task may create a lightweight context pack containing:
- project
- task type
- user intent
- risk level
- requested tags
- selected memory IDs
- conflicting memory IDs
- verified source checks
- compact retrieved memory payload

The pack is working context, not permanent knowledge. It can be closed as completed, blocked, or abandoned.

## Write-back Rules
Use `service_save_memory_v2` for durable memory.

Persist only when information is:
- future-useful
- sufficiently verified
- non-secret
- durable

Prefer update/deduplication over repeated insert.
A new fact can explicitly supersede an older memory while preserving history.

## Source of Truth
- GitHub: code, architecture, migrations, runtime contracts, history
- XiaoE Core Supabase: persistent memory, experience, task context, current project state
- Business systems: transaction truth; XiaoE memory must never be required for a business transaction to work

## Security Boundary
AI providers do not directly access `public.memories`.
Runtime access goes through `memory-gateway` and scoped runtime identity validation.
Tables remain RLS-protected and ordinary `anon` / `authenticated` access is not granted.

## Autonomy Model
Target operating mode is human-on-the-loop:
- XiaoE proceeds independently inside approved boundaries
- XiaoE verifies before persisting
- destructive, irreversible, paid, security-critical, or business-rule-changing actions escalate to Eric

## Development Principle
Root Before Flower.
The v3 design extends v2.1 without removing legacy memory functions, so existing XiaoE workflows remain compatible while the Fusion path is adopted progressively.
