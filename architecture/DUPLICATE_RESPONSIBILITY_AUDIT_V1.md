# XiaoE Duplicate Responsibility Audit v1

Status: **COMPLETE — OWNERSHIP RESOLVED**
Branch: `duplicate-responsibility-audit-v1`
Purpose: Remove ambiguous responsibility ownership without changing live behavior or creating replacement subsystems.

Core rule:

`One responsibility -> one owner -> other layers reference, call, transport or orchestrate.`

This audit is documentation/ownership-first. It does not modify live Supabase, Auth/RLS, production deployment, memory schema, business transaction paths, or frozen Behavior Logic.

---

# Final Ownership Summary

| Responsibility | One authoritative owner | Execution/storage path | Non-owner role |
|---|---|---|---|
| Persistent memory policy | `core/memory/XIAOE_MEMORY_CONTRACT_V1.md` | Memory service RPCs / `public.memories` | Other docs reference only |
| Memory architecture / source separation | `architecture/XIAOE_MEMORY_ARCHITECTURE_V2_1.md` | N/A | Baseline architecture |
| Fusion retrieval ranking + conflict semantics | `architecture/XIAOE_MEMORY_FUSION_V3.md` | `service_fusion_retrieve`, `service_find_memory_conflicts` | Bridge/bootstrap call it |
| Durable write eligibility / dedup / supersession policy | Memory Contract | `service_save_memory_v2` | Bridge/provider do not reinterpret |
| Current Project State persistence | Memory Contract + Memory Architecture | `service_update_current_project_state` / `public.memories` | Checkpoint invokes it |
| Checkpoint lifecycle | `XIAOE_WORK_CHECKPOINT_AND_RESUME_PROTOCOL.md` | delegates to Current Project State | No second store |
| Context refresh timing | `CONTEXT_REFRESH_GATE.md` | orchestration event | Does not rank memory |
| Context assembly / project detection / work-depth routing | `XIAOE_CONTEXT_BRIDGE_V1.md` | Task Context Pack + temporary runtime context | Does not own memory rules |
| Task Context Pack semantics | Memory Fusion v3 | `task_context_packs` + v3 services | Temporary, task-scoped |
| Memory transport/auth | `memory-gateway/index.ts` | Edge Function | Does not own policy |
| Runtime client API | `XIAOE_RUNTIME_CLIENT_V1.ts` | wrapper/client only | Does not own semantics |
| Governance/bootstrap composition | v4.1 governance architecture/service | `service_xiaoe_bootstrap_v41` | Calls existing owners, does not replace them |
| Code/architecture/version truth | GitHub | Git | Memory cannot override code truth |
| Persistent XiaoE state | XiaoE Core Supabase | Postgres/RPCs | GitHub snapshots are evidence only |
| Business transaction truth | owning business system | business DB/runtime | XiaoE memory is never transaction authority |

---

## Audit 1 — Current Project State / Checkpoint / Task Context Pack

Status: **OWNERSHIP RESOLVED — no runtime deletion required**

### Finding

Three concepts were adjacent and could be mistaken for duplicate implementations:

1. **Current Project State** — durable project continuation state.
2. **Checkpoint lifecycle** — rules for when to capture, resume and re-verify that state.
3. **Task Context Pack** — temporary task-specific working context assembled from retrieval and source checks.

They overlap in vocabulary but not in correct responsibility.

### Decision

#### Durable Current Project State

**Policy owner:** `core/memory/XIAOE_MEMORY_CONTRACT_V1.md`

**Architecture owner:** `architecture/XIAOE_MEMORY_ARCHITECTURE_V2_1.md`

**Persistence/execution owner:** XiaoE Core Supabase `public.memories` through `service_update_current_project_state(...)`.

Canonical identity:

- `namespace = 'project'`
- `memory_type = 'current_project_state'`
- one active current-state record per `project_key`
- update existing active state rather than append endless snapshots

Therefore:

`Current Project State = durable checkpoint payload.`

#### Checkpoint lifecycle

**Owner:** `core/collaboration/XIAOE_WORK_CHECKPOINT_AND_RESUME_PROTOCOL.md`

Owns when to capture/resume/re-verify. It does not own a database/table/second persistence format.

Correct relationship:

`Checkpoint Protocol -> decides when/what to capture -> Current Project State -> persists continuation state.`

#### Task Context Pack

**Owner:** Memory Fusion v3.

Task Context Pack is temporary working context containing task intent, risk, selected memories, conflicts and source checks.

`Closing a Task Context Pack != updating Current Project State.`

### Hard boundary

- one durable Current Project State per project;
- no second checkpoint table;
- no parallel checkpoint memory type;
- no transcript checkpoint store;
- GitHub state snapshots remain recovery evidence only.

### Runtime/schema action

**None required.** Existing implementation already separates these responsibilities correctly.

---

## Audit 2 — Retrieval / Context Refresh / Context Bridge

Status: **OWNERSHIP RESOLVED**

### Finding

Retrieval language appears across:

- Memory Architecture v2.1;
- Memory Fusion v3;
- Context Refresh Gate;
- Context Bridge;
- v4.1 bootstrap.

The repeated word `retrieve/refresh/load` can look like duplicate responsibility, but these components answer different questions.

### Decision

#### A. When must context be refreshed?

**Owner:** `core/collaboration/CONTEXT_REFRESH_GATE.md`

It owns event triggers such as:

- new chat;
- project switch;
- major phase change;
- two-failure root-cause escalation;
- high-impact changes;
- interruption/drift;
- uncertainty about identity/project/current state/hard rules/source of truth.

It does not own memory ranking or SQL retrieval semantics.

#### B. Which persistent memories rank/select?

**Owner:** Memory Fusion v3.

Execution owner:

- `service_fusion_retrieve(...)`;
- `service_find_memory_conflicts(...)`.

Fusion v3 owns:

- verified/active/unexpired filtering;
- project matching;
- namespace relevance;
- tag overlap;
- trust/importance/confidence/source-priority scoring;
- conflict surfacing.

No other layer may implement a second ranking algorithm.

#### C. What context is needed for the task and how is it assembled?

**Owner:** `core/collaboration/XIAOE_CONTEXT_BRIDGE_V1.md`

Context Bridge owns:

- project detection;
- FAST / FOCUSED / DEEP depth selection;
- source/tool routing;
- deciding when the task needs Fusion retrieval;
- assembling the smallest sufficient Active Context Pack;
- stopping reads when enough trustworthy context exists.

It must call Memory Fusion rather than re-rank memories itself.

#### D. What does v4.1 bootstrap own?

`service_xiaoe_bootstrap_v41` is a **composition/orchestration endpoint**. It gathers system metadata, screening, policy rules, protected layers, Fusion memories and conflicts. It does not own a second memory retrieval policy.

### Canonical flow

```text
Refresh Gate
(WHEN context needs refresh)
      |
      v
Context Bridge
(WHAT task context is needed / source routing)
      |
      v
Fusion Retrieve
(WHICH memories rank/select + conflicts)
      |
      v
Active / Task Context Pack
```

### Duplicate classification

- Context Refresh vs Fusion Retrieve: **not duplicate** — timing vs ranking.
- Context Bridge vs Fusion Retrieve: **not duplicate** — orchestration vs memory selection.
- Bootstrap vs Fusion Retrieve: **caller/composer**, not owner.
- Any second ranking logic in Bridge/Gateway/provider: **prohibited shadow implementation**.

### Runtime/schema action

**None required.** Existing boundaries are structurally compatible; documentation ownership is sufficient.

---

## Audit 3 — Write-back / Dedup / Conflict Ownership

Status: **OWNERSHIP RESOLVED**

### Finding

Write-back wording exists in Memory Contract, Fusion v3 and Context Bridge. Conflict language exists both in policy docs and v3 service implementation.

### Decision

#### A. What is eligible to persist?

**Owner:** `core/memory/XIAOE_MEMORY_CONTRACT_V1.md`

Only future-useful, sufficiently verified, non-sensitive and durable conclusions qualify.

The provider/Context Bridge may produce a candidate, but cannot decide by itself that unverified temporary reasoning becomes durable memory.

#### B. How is active Fusion memory saved?

**Active v3 execution owner:** `service_save_memory_v2(...)`.

It is the v3 write path supporting verification/confidence/source priority/validity/supersession metadata.

#### C. Who owns duplicate/conflict detection?

**Fusion conflict owner:** `service_find_memory_conflicts(...)` and Fusion v3 semantics.

It detects at least:

- duplicate active `memory_key`;
- superseded record still active.

The Memory Contract owns the policy principle; Fusion service owns the active implementation.

#### D. Context Bridge role

Context Bridge may trigger write-back after verification. It does not:

- invent a second dedup algorithm;
- silently resolve conflict by provider preference;
- persist raw transcript/debugging noise;
- redefine verification thresholds.

### Canonical flow

`candidate -> Memory Contract eligibility -> v3 save/dedup/supersession path -> conflict scan -> verified durable memory`

### Runtime/schema action

**No new service required.** The audit explicitly rejects a new write-back subsystem.

---

## Audit 4 — Runtime Client vs memory-gateway

Status: **OWNERSHIP RESOLVED**

### Finding

Both expose memory operations, but at different boundaries.

### Decision

#### Runtime Client

`core/runtime/XIAOE_RUNTIME_CLIENT_V1.ts` is a caller-side adapter.

Owns:

- typed convenience methods;
- construction/config validation;
- HTTP call packaging;
- surfacing gateway failure.

Does not own:

- authorization truth;
- memory policy;
- retrieval ranking;
- project-state semantics;
- database RPC implementation.

#### memory-gateway

`supabase/functions/memory-gateway/index.ts` owns the server transport/auth boundary.

Owns:

- accepted action names;
- runtime-key validation through runtime identity RPC;
- scope enforcement (`memory:read`, `memory:write`, `project:state`);
- project-key resolution validation;
- mapping authorized actions to existing RPCs;
- normalized HTTP responses.

Does not own:

- memory selection policy;
- write eligibility policy;
- project checkpoint lifecycle;
- provider reasoning.

### Important compatibility observation

The gateway exposes both:

- `read` / `save` as `legacy` mode;
- `fusion_read` / `save_v2` as `fusion_v3` mode.

That duality is compatibility, not ownership duplication.

### Hard boundary

`Runtime Client -> memory-gateway -> service RPC -> storage`

No caller may bypass the gateway/service boundary merely to duplicate memory logic in the client.

### Runtime/schema action

**None required for ownership.** Future runtime client expansion should expose Fusion actions as wrappers, not reimplement Fusion behavior.

---

## Audit 5 — Legacy v2.1 Services vs Fusion v3 Compatibility

Status: **RESOLVED AS CONTROLLED COMPATIBILITY**

### Finding

Legacy functions remain alongside Fusion v3:

Legacy examples:

- `service_read_memories`;
- `service_save_memory`;
- `service_update_current_project_state`;
- `service_deactivate_conflicting_memory`.

Fusion v3 adds:

- verification/confidence/source-priority metadata;
- deterministic `memory_key`;
- `service_fusion_retrieve`;
- `service_find_memory_conflicts`;
- `service_save_memory_v2`;
- Task Context Packs.

The v3 migration explicitly states it is a **backward-compatible extension** of v2.1 rather than a replacement.

### Ownership decision

For new general memory retrieval/write behavior:

- **Fusion v3 is the active architecture owner.**
- Legacy read/save functions are compatibility paths.

Exception:

`service_update_current_project_state` remains the canonical specialized Current Project State update path because v3 did not replace that responsibility with another service.

### Compatibility rules

1. Do not delete legacy services merely because v3 exists.
2. Do not add new capabilities to legacy `read`/`save` when the feature belongs to Fusion v3.
3. New retrieval ranking belongs only in `service_fusion_retrieve`.
4. New durable general-memory metadata belongs in the v3 save path unless a migration plan explicitly supersedes it.
5. Specialized stable services may remain canonical when v3 intentionally delegates to them.
6. Legacy is compatibility, not an equal architecture owner.

### Sunset rule

Legacy removal should occur only after evidence proves:

- no approved runtime depends on it;
- migration/rollback strategy exists;
- production verification passes;
- removal reduces real complexity without weakening portability/recovery.

Until then:

`Preserve legacy compatibility -> freeze semantic expansion -> route new capability to Fusion v3.`

### Runtime/schema action

**No deletion justified now.** Removing legacy paths during this audit would violate Stability First and Root Before Flower.

---

## Audit 6 — Governance / Bootstrap References vs Memory Authority

Status: **OWNERSHIP RESOLVED**

### Finding

v4.1 governance introduces:

- system metadata;
- policy rules;
- protected layers;
- learning promotion;
- screening;
- policy gate;
- bootstrap composition.

Because bootstrap returns memories and conflicts, it can appear to be another memory owner.

### Decision

v4.1 governance **does not own persistent memory semantics**.

It owns governance semantics:

- system/version state;
- engineering policy gate;
- protected-layer control;
- learning promotion approval;
- bootstrap composition.

`service_xiaoe_bootstrap_v41(...)` calls existing Memory Fusion services for memory retrieval/conflicts. Therefore it is a consumer/composer of Memory Fusion, not a replacement.

### Learning promotion boundary

`service_promote_learning(...)` may attach Master-level promotion metadata to an existing verified memory after thresholds and explicit approval are satisfied.

It does not create a second memory store. The promoted object remains the same `public.memories` record plus governance promotion state.

Correct model:

`Memory owns knowledge -> Governance may approve/promote/protect -> Bootstrap composes -> no duplicate knowledge store.`

### Runtime/schema action

**None required.** Existing additive governance model already respects Memory Fusion ownership.

---

# Cross-Audit Findings

## True duplicate implementations found

**None requiring immediate removal.**

The audit found substantial repeated terminology and adjacent responsibilities, but the live architecture is largely layered rather than duplicated.

## Controlled duplicate interfaces found

**Legacy v2.1 + Fusion v3 API paths.**

Classification: backward compatibility.

Decision: preserve but freeze legacy semantic growth.

## Highest future duplication risks

1. Creating a second checkpoint store because Checkpoint is mistaken for persistence ownership.
2. Adding ranking logic to Context Bridge or AI provider.
3. Adding write/dedup logic to Runtime Client or gateway.
4. Treating Task Context Pack as project state.
5. Treating v4.1 bootstrap as a replacement memory system.
6. Expanding legacy read/save APIs with new Fusion behavior instead of using v3.
7. Treating ChatGPT Memory as authoritative XiaoE project state.

---

# Canonical Memory Responsibility Pipeline

```text
User intent / session event
          |
          v
Context Refresh Gate
WHEN refresh is required
          |
          v
Context Bridge
project detection + task depth + source routing
          |
          v
Memory Fusion v3
rank verified memory + surface conflicts
          |
          v
Task Context Pack
TEMPORARY working context
          |
          v
AI reasoning + tools + live verification
          |
          v
Memory Contract
judge durable write eligibility
          |
          +--------------------+
          |                    |
          v                    v
service_save_memory_v2   service_update_current_project_state
GENERAL durable memory   ONE durable project continuation state
          |                    |
          +----------+---------+
                     v
               public.memories

Checkpoint Protocol controls WHEN Current Project State is captured/resumed.
Governance may gate/promote/protect but does not replace memory ownership.
Runtime Client + memory-gateway transport authorized actions only.
```

---

# Final Hard Rules Produced by This Audit

1. **One responsibility has one owner.** Multiple callers are allowed; shadow implementations are not.
2. **Current Project State is the durable checkpoint payload.** Checkpoint Protocol owns lifecycle only.
3. **Task Context Pack is temporary.** It never substitutes for project checkpoint persistence.
4. **Context Refresh Gate owns timing; Fusion v3 owns ranking; Context Bridge owns assembly/orchestration.**
5. **Memory Contract owns durable write eligibility; Fusion v3 owns active general-memory retrieval/write/conflict implementation.**
6. **Runtime Client and memory-gateway are adapters/transport boundaries, not memory-policy owners.**
7. **Legacy v2.1 read/save paths are compatibility-only.** Preserve them, but do not expand them with new Fusion semantics.
8. **Governance/bootstrap composes or governs memory; it does not become a second memory system.**
9. **ChatGPT Memory is not XiaoE project-state authority.**
10. **GitHub snapshot files are evidence/recovery artifacts, not reachable live memory authority.**
11. **Business transaction truth stays in the owning business system.**
12. **Do not add a new memory/checkpoint/context subsystem until an unmet requirement is proven and existing owners cannot represent it.**

---

# Change Impact Assessment

### Live Supabase
No change.

### Database schema
No change.

### Auth / RLS
No change.

### memory-gateway
No change.

### Runtime behavior
No change.

### Frozen Behavior Logic
No change.

### Existing compatibility
Preserved.

### Documentation/governance improvement
Ownership is now explicit and duplicate responsibility expansion is constrained.

---

# Audit Completion Decision

**PASS — Duplicate Responsibility Audit v1 complete.**

The architecture does not currently justify destructive consolidation. The correct action is to preserve working layers, define single ownership, freeze legacy semantic expansion, and prevent new shadow systems.

Completion standard achieved:

`Every Memory responsibility has one clear owner; other layers only call, reference, transport, govern or orchestrate it.`

Recommended next engineering step after this audit:

`Return to checkpoint persistence/resume work using this ownership map, with Current Project State as the single durable continuation payload.`
