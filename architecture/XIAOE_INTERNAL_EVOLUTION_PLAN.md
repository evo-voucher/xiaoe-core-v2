# XiaoE Internal Evolution Plan

Status: PROPOSED
Date: 2026-08-24
Current stable base: XiaoE Core v4.1 + Memory Fusion v3

## Objective
Develop XiaoE internally before expanding external transport integrations. Preserve the verified v4.1 governance and Memory Fusion v3 core while adding a controlled capability/execution layer around it.

## Stable core that must remain untouched by default
- Behavior / anti-drift reasoning foundation
- Memory Fusion v3 retrieval and write-back contracts
- Runtime identity boundary
- Policy Gate and protected-layer governance
- Existing migration history 000-009
- Current project key compatibility: `xiaoe_core_v2`

Any future implementation must remain additive unless evidence proves a breaking change is unavoidable.

## Priority 1 — Capability Registry

### Problem
XiaoE currently has system-level capability flags, but no explicit operational registry describing what concrete capabilities are available, how they are invoked, what permissions they require, and what risk class they belong to.

### Target
Create a capability registry that can answer:
- What can XiaoE do now?
- Which capability owns this task?
- Which tool/provider can execute it?
- What scopes or approvals are required?
- Is the capability available, degraded, experimental, or disabled?
- What is the fallback if the preferred executor is unavailable?

### Suggested capability record
- `capability_key`
- `domain`
- `description`
- `owner_layer`
- `status`: active / degraded / experimental / disabled
- `risk_level`: low / medium / high / critical
- `required_scopes`
- `preferred_executor`
- `fallback_executors`
- `input_contract`
- `output_contract`
- `verification_contract`
- `version`
- `metadata`

### Rule
The registry describes capability ownership and routing. It must not contain provider secrets or business transaction data.

## Priority 2 — Execution Router

### Problem
Memory retrieval and governance are strong, but task execution is still primarily orchestrated by the active AI conversation.

### Target flow
User intent
→ task interpretation
→ capability lookup
→ policy gate
→ executor selection
→ execution
→ verification
→ result classification
→ memory/write-back decision
→ checkpoint

### Routing principles
1. Use the smallest capable executor.
2. Prefer already connected/free/approved tools when equivalent.
3. Do not route around Policy Gate.
4. Do not let an executor change its own permissions.
5. High/critical actions still require the existing governance checks.
6. Failure of one executor may trigger a registered fallback, but repeated same-path failure must enter root-cause analysis rather than blind retries.

## Priority 3 — Execution Journal

### Purpose
Give XiaoE a compact machine-readable record of what it attempted and what actually happened without turning memory into chat transcripts.

### Suggested execution record
- task id
- capability key
- executor
- project key
- risk level
- input summary
- source checks
- policy decision
- execution status
- verification result
- error class
- retry/fallback count
- started/finished timestamps
- resulting memory IDs / checkpoint reference

### Rule
Execution journal is operational history. Only durable conclusions should be promoted into `memories`.

## Priority 4 — Learning Feedback Loop

Use completed execution evidence to distinguish:
- one-off result
- reusable experience
- candidate learning
- verified learning
- Master-promoted learning

Promotion remains governed by existing v4.1 rules and explicit approval where required. XiaoE must never learn a reusable rule merely because a single execution succeeded.

## Priority 5 — AI / Tool Router

Only after Capability Registry + Execution Router are stable should XiaoE expand provider routing.

The provider layer should be replaceable and treated as an executor, not as XiaoE's identity.

Potential executor classes:
- ChatGPT / reasoning model
- code agent
- GitHub
- Supabase
- email/calendar/contact tools
- business-system APIs
- future AI providers

Provider selection should consider:
- capability fit
- required permissions
- latency
- cost
- reliability
- privacy boundary
- fallback availability

## Non-goals for this phase
- Do not replace Memory Fusion v3.
- Do not rewrite Behavior.
- Do not couple XiaoE to one AI provider.
- Do not add paid vector/embedding infrastructure without evidence it is needed.
- Do not move business transaction truth into XiaoE memory.
- Do not expand HTTP gateway merely for architectural completeness.

## Implementation order
1. Define Capability Registry contract.
2. Seed current known XiaoE capabilities from verified architecture.
3. Add read-only capability lookup.
4. Add Execution Router decision contract.
5. Add Execution Journal.
6. Connect Policy Gate to routing decisions.
7. Add verified fallback behavior.
8. Add learning feedback from successful/failed executions.
9. Only then introduce multi-provider AI/tool routing.

## Promotion gate
This plan does not change the active XiaoE version by itself.

A future implementation should be promoted beyond v4.1 only after:
- additive migration is reviewed
- existing 000-009 rebuild remains reproducible
- Behavior remains unchanged unless separately authorized
- Memory Fusion v3 compatibility passes
- Policy Gate behavior passes
- fresh-project migration test passes
- rollback path is documented

## Guiding principle
Stable Core + Open Edges.

Make XiaoE better at knowing what it can do, choosing the correct executor, verifying the result, and learning only from verified evidence before making external integrations broader.
