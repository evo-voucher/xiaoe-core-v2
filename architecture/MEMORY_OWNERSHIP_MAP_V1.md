# XiaoE Memory Ownership Map v1

Status: AUDIT BASELINE
Purpose: Define one authoritative owner for each Memory responsibility before performing the broader Duplicate Responsibility Audit.

## Core Principle

`One responsibility -> one owner -> many callers allowed -> no shadow implementation.`

A document may describe another layer, and a runtime may call another layer, but neither becomes the owner merely because it mentions or invokes the responsibility.

## Ownership Map

| Responsibility | Authoritative owner | Storage / execution owner | Allowed callers / consumers | Explicit non-owners |
|---|---|---|---|---|
| Persistent XiaoE memory policy | `core/memory/XIAOE_MEMORY_CONTRACT_V1.md` | N/A | Architecture docs, Context Bridge, runtime, gateway | ChatGPT memory, current chat, project-specific code |
| Memory architecture baseline / source-of-truth separation | `architecture/XIAOE_MEMORY_ARCHITECTURE_V2_1.md` | N/A | Memory Contract, Fusion v3, migration docs | Context Bridge, Checkpoint Protocol |
| Retrieval ranking / Fusion Retrieve / conflict surfacing / Task Context Pack semantics | `architecture/XIAOE_MEMORY_FUSION_V3.md` | Supabase Fusion services | Context Bridge, bootstrap, runtime clients | Checkpoint Protocol, AI provider |
| Durable memory write policy / dedup / supersession | `core/memory/XIAOE_MEMORY_CONTRACT_V1.md` | `service_save_memory_v2` and related memory service RPCs | runtime client, gateway, bootstrap flows | Context Bridge, AI provider, current chat |
| Current Project State persistence | Memory Contract §7 + Memory Architecture §3/§8 | authoritative current-state record in XiaoE Core Supabase | Checkpoint Protocol, Context Bridge, runtime client | GitHub snapshots, chat transcript, Task Context Pack |
| Checkpoint lifecycle: when to capture/resume/verify | `core/collaboration/XIAOE_WORK_CHECKPOINT_AND_RESUME_PROTOCOL.md` | delegates persistence to Current Project State memory | Context Bridge / orchestration layer | Memory Contract does not own session lifecycle timing |
| Context refresh timing / refresh triggers | `core/collaboration/CONTEXT_REFRESH_GATE.md` | temporary context assembly only | Context Bridge, orchestration | Persistent memory store, checkpoint record |
| Active Context Pack assembly / project detection / work-depth routing | `core/collaboration/XIAOE_CONTEXT_BRIDGE_V1.md` | Task Context Pack + temporary runtime state | ChatGPT / approved reasoning provider | Memory Contract, Checkpoint Protocol |
| Memory transport/auth boundary | `supabase/functions/memory-gateway/index.ts` | Edge Function runtime | `XiaoERuntimeClient`, approved server runtimes | AI provider, browser client, business system |
| Runtime memory client API | `core/runtime/XIAOE_RUNTIME_CLIENT_V1.ts` | client wrapper only | server runtime / orchestration | memory policy, persistence semantics, retrieval ranking |
| Persistent memory physical schema | `supabase/migrations/001_memory_core_v1.sql` + additive v3 migrations | Supabase Postgres | Memory services | docs, ChatGPT memory |
| Memory service implementation | `supabase/migrations/002_memory_service_core_v1.sql`, `005_memory_fusion_layer_v3.sql`, `006_memory_fusion_services_v3.sql` | Supabase RPCs | memory-gateway / service-role runtime | Context Bridge, AI provider |
| ChatGPT user background / stable preferences | ChatGPT Memory | ChatGPT product memory | reasoning provider | XiaoE project-state authority |
| Current-conversation working context | current chat | transient conversation state | reasoning provider | persistent XiaoE memory, project truth |
| Code / architecture / migrations / version history | GitHub repository | Git | Memory and Context layers may reference | Supabase memory cannot override source code truth |
| Business transaction truth | each business system | business DB/runtime | XiaoE may inspect through explicit APIs | XiaoE memory, ChatGPT memory, checkpoint |

## Required Boundaries

### 1. Memory Contract owns policy, not transport
It defines what may be stored, read, updated, deduplicated, superseded, and isolated. It must not grow HTTP/auth/routing logic.

### 2. Fusion v3 owns retrieval semantics, not project orchestration
It owns trust-ranked retrieval, conflict detection and Task Context Pack memory semantics. Project detection, FAST/FOCUSED/DEEP routing and tool selection remain Context Bridge responsibilities.

### 3. Checkpoint Protocol owns lifecycle, not a second store
Checkpoint decides when work state must be captured and how resume works. The durable payload is the existing authoritative Current Project State memory. No second checkpoint database/table/file format should be introduced unless a future requirement cannot be represented by the existing current-state record.

### 4. Context Bridge owns orchestration, not memory rules
Layer 0 can locate, retrieve, reconcile and package context. Memory ranking, conflict resolution, write-back eligibility and memory security remain owned by the Memory architecture/contract.

### 5. Runtime Client and memory-gateway are adapters
They transport authorized memory actions. They must not reinterpret policy, invent new memory types, rank memories differently, or maintain shadow state.

### 6. Task Context Pack is temporary
Task Context Pack is working context. It is not Current Project State and not durable memory. Closing a Task Context Pack must not be treated as completing or updating the project checkpoint unless the explicit checkpoint lifecycle also runs.

### 7. GitHub snapshot files are evidence, not live memory ownership
Files such as `supabase/state/CURRENT_PROJECT_STATE_20260823.json` are migration/recovery evidence. The live authoritative project-state owner remains XiaoE Core Supabase when configured and reachable.

## Duplicate-Responsibility Hotspots Found

1. **Current Project State wording appears in Memory Architecture, Memory Contract, Checkpoint Protocol, Context Bridge and runtime client.**
   - Correct model: Memory owns the durable state; Checkpoint owns capture/resume timing; Context Bridge owns orchestration; runtime client only calls the update action.

2. **Retrieval language appears in Memory Architecture, Fusion v3, Context Refresh Gate and Context Bridge.**
   - Correct model: Fusion v3 owns ranking/conflict retrieval semantics; Context Refresh Gate owns when refresh is required; Context Bridge owns what task context to assemble and when to call retrieval.

3. **Write-back language appears in Memory Contract, Fusion v3 and Context Bridge.**
   - Correct model: Memory Contract owns eligibility/dedup policy; Fusion v3 owns the service path used by the active architecture; Context Bridge only triggers write-back after verification.

4. **Checkpoint and Task Context Pack can be mistaken as the same thing.**
   - They are not. Checkpoint = durable continuation state. Task Context Pack = temporary task working set.

5. **ChatGPT Memory and XiaoE Memory are both called memory.**
   - They must remain separate: ChatGPT Memory supports stable user background/preferences; XiaoE Memory is authoritative persistent XiaoE/project memory.

## Audit Decision Rules

During the next Duplicate Responsibility Audit:

- If two modules implement the same responsibility, keep the declared owner and reduce the other to caller/reference/adapter.
- If two documents state the same rule, keep the canonical statement at the owner and replace other copies with concise references where practical.
- Do not remove compatibility paths merely because wording overlaps; verify whether they are implementation compatibility or true responsibility duplication.
- Do not change live Supabase, production behavior, Auth/RLS, memory schema or gateway behavior during the documentation-first audit.
- Preserve Stable Core + Open Edges.

## Next Audit Scope

After this ownership baseline, audit in this order:

1. Current Project State / Checkpoint overlap
2. Retrieval / Context Refresh / Context Bridge overlap
3. Write-back / dedup / conflict ownership overlap
4. Runtime Client vs memory-gateway responsibility overlap
5. Legacy v2.1 services vs Fusion v3 compatibility overlap
6. Governance/bootstrap references that duplicate memory authority

Success condition:

`Every Memory responsibility has one clear owner; other layers only call, reference, transport or orchestrate it.`
