# XiaoE Memory Architecture v2.1

Status: ACTIVE ARCHITECTURE BASELINE
Origin: migrated from historical XiaoE Memory v2.1 design previously stored in `evo-voucher/evolution-optical-voucher`.
Historical source commit: `9b2504606b81854756e15444fb2f3be28a521463`

## 1. Purpose
XiaoE Memory is a persistent cognitive layer. It is not a chat archive.

Its goals are:
- keep identity and operating principles consistent across chats
- preserve project state across sessions and devices
- allow AI provider/model changes without losing XiaoE memory
- prevent rule conflicts and duplicate state accumulation
- restore only relevant memory instead of loading everything

## 2. Three Independent Memory Sources
### XiaoE Memory
Authoritative persistent XiaoE knowledge stored through XiaoE AI Core, intended for Supabase `public.memories`.

Stores:
- durable principles
- verified decisions
- project state
- important experience
- development rules

### ChatGPT Memory
Supports user background and stable preferences. It is not the authoritative project state store.

### Current Conversation
Temporary working context. It supports immediate reasoning but must not be treated as persistent truth by itself.

Evidence priority:
`current verified state > XiaoE project memory > ChatGPT memory > current-chat assumptions`

## 3. Core Memory Commands
### XiaoE Memory / Read
Flow:
1. identify active project
2. call Memory Service
3. Retrieval Filter by `project_key`, `namespace`, `importance`, and `is_active`
4. restore only relevant context
5. if read fails, explicitly state that persistent memory was not loaded

### XiaoE Save / Write
Flow:
`candidate -> judge -> deduplicate -> conflict resolution -> save`

Save conclusions, not raw process.

Store:
- long-term decisions
- architecture direction
- verified success/failure lessons
- important project milestones
- durable operating rules

Do not store:
- complete chats
- repeated discussion
- temporary guesses
- secrets
- large raw code/binaries
- irrelevant context

### XiaoE Finish / Current Project State
Each project maintains one current state record.

Prefer UPDATE over repeated INSERT.

State contains:
- completed work
- current verified state
- unresolved issues
- risks
- next step

## 4. Memory Controller
The Memory Controller sits between AI providers and persistent storage.

Responsibilities:
- Retrieval Filter
- Deduplicate
- Conflict Resolution
- Checkpoint
- Confirmation
- Read-failure handling

AI providers must not directly access `public.memories`.

## 5. AI Router Boundary
`AI Router -> Provider -> normalized result -> XiaoE Core -> Memory Service -> Memory Controller -> public.memories`

Providers are interchangeable reasoning engines.
Examples:
- OpenAI
- Anthropic
- future Gemini / DeepSeek / others

XiaoE identity and memory remain independent from the active provider.

## 6. Memory Namespaces
- `global` — durable system-wide rules/persona invariants
- `core` — XiaoE identity and operating principles
- `project` — project-specific decisions and state
- `experience` — verified success/failure lessons
- `organization` — organization-level persistent memory
- `user` — user-level persistent memory

## 7. Minimum Memory Schema Contract
`public.memories` should support at minimum:
- `id uuid`
- `namespace text`
- `memory_type text`
- `title text`
- `content text`
- `importance integer/numeric`
- `project_key text`
- `organization_id uuid nullable`
- `user_id uuid nullable`
- `source text`
- `tags text[] or jsonb`
- `metadata jsonb`
- `is_active boolean`
- `created_at timestamptz`
- `updated_at timestamptz`

RLS must isolate organization/user scoped memory where applicable.

## 8. v2.1 Management Layer
### Retrieval Filter
Do not load all memories by default. Load only active and relevant memory.

### Conflict Resolution
When a new rule replaces an old rule:
- new rule: `is_active = true`
- superseded rule: `is_active = false`

History remains preserved, but normal retrieval uses only current active rules.

### Current Project State
Each project has a single current-state record to avoid infinite accumulation of stale project snapshots.

### Read Failure
Never claim memory was loaded when the persistent memory read failed.

## 9. Source-of-Truth Separation
### GitHub
Source of truth for:
- code
- architecture
- migrations
- runtime contracts
- version history

### XiaoE AI Core Supabase
Source of truth for:
- persistent XiaoE memory
- project knowledge
- verified experience
- current project state

### Business Systems
Business transaction systems remain independent. XiaoE memory must not be required for a business transaction path to function.

## 10. Core Development Principles
- Root Before Flower
- Lean Development
- Root Cause Before Patch
- Verify Before Persisting
- Memory Stores Conclusions, Not Process
- Least Privilege
- No secret material in frontend or public repository

## 11. Closed-Loop Workflow
`work -> important conclusion -> XiaoE Save -> XiaoE Finish -> next session -> Retrieval Filter -> restore active context -> verify live state -> continue`

XiaoE should always be able to recover:
- who it is
- what project is active
- what is verified
- where the project currently stands
- what should happen next
