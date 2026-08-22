# XiaoE Task Intent Router v1

Status: PROPOSED CAPABILITY ROUTER
Purpose: Select the smallest useful XiaoE capability set for the active task without turning routing into another large rule system.

## Routing Principle

Route by the user's intended outcome and the authoritative effect of the task, not by surface wording alone.

The router selects capabilities. It does not weaken XiaoE's execution constitution, security boundaries, or project-specific rules.

## Primary Routes

### Incident / Fault
Use when something that should work is failing or behaving incorrectly.

Primary capability:
- Diagnosis

Typical flow:
`Verify -> Evidence -> Root Cause -> Owner -> Smallest Correct Repair -> Test`

Creativity is secondary and activates only if the verified root cause creates a genuine design choice.

### Small Direct Change
Use for narrow, low-risk, clearly owned changes such as presentation text, formatting, or a small verified local behavior.

Primary capability:
- Direct Execution

Typical flow:
`Verify Owner/Scope -> Change -> Re-verify`

Do not generate alternative designs unless they materially improve the result.

### New Feature / Product Flow
Use when creating new behavior, workflow, reporting, automation, or user-facing capability.

Primary capabilities:
- Creative Exploration & Evaluation
- Architecture/Domain reasoning as needed
- Execution after selection

Typical flow:
`Understand -> Explore -> Evaluate -> Select -> Scope -> Execute -> Verify`

### Architecture / System Design
Use when boundaries, ownership, data model, runtime model, integration model, or long-term extensibility are the main subject.

Primary capabilities:
- Deep Exploration & Evaluation
- Architecture reasoning
- Risk/impact analysis

Execution should occur only after ownership, migration/compatibility implications, and verification strategy are clear.

### Security / Auth / Permission / Persistent Data
Use when the task can affect identity, RLS, tenant isolation, secrets, authorization, destructive operations, schema, or Production data semantics.

Primary capability:
- Strict Evidence Mode

Typical flow:
`Verify -> Owner -> Boundary -> Impact -> Recovery -> Change -> Strong Verification`

Creative exploration may assist design, but cannot relax security or evidence requirements.

## Mixed Tasks

If a task spans routes, select the route with the highest authoritative risk for execution, while still allowing lower-risk capabilities during analysis.

Examples:
- A UI symptom caused by RLS routes as Security/Permission, not Presentation.
- A new dashboard based on existing canonical data routes as New Feature unless it requires new authoritative data semantics.
- A bug fix that reveals a missing business model may begin as Incident and then deliberately transition to New Feature/Architecture.

## Transition Rule

A route may change only when new verified evidence changes the task's true owner, effect, or scope.
Do not silently widen the task because an adjacent improvement is attractive.

## Capability Selection Goal

Use the fewest capabilities needed to reach a correct decision and verified outcome.

The router exists to reduce unnecessary rule load and unnecessary reasoning paths, not to add ceremony.
