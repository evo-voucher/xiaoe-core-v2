# XiaoE Execution Router Decision Contract v1

Status: PROPOSED CONTRACT
Date: 2026-08-24
Purpose: Connect Task Intent Router output to Capability Registry selection and Governance checks without creating a second execution constitution or mutation engine.

## Position

Execution Router is a decision layer, not an authority layer.

It consumes:
- the task route selected by `TASK_INTENT_ROUTER_V1.md`,
- the verified capability entries in `CAPABILITY_REGISTRY_V1.md`,
- current executor availability,
- current evidence/source checks,
- current Governance/Policy Gate requirements.

It produces a compact execution decision describing which capability/executor should be used and what must be verified before and after execution.

It does not itself perform the mutation.

## Authority Order

`Behavior > Governance > Task Intent Router > Capability Registry > Execution Router Decision > Executor`

Execution Router MUST NOT:
- reinterpret or override frozen Behavior,
- bypass Policy Gate,
- bypass protected-layer rules,
- invent permissions,
- select a disabled capability,
- silently upgrade a degraded/experimental capability into a stable path,
- widen task scope because a tool can do more,
- route around missing approval,
- treat tool availability as authorization,
- create a new source of truth for project or business state.

## Decision Flow

`User Intent`
→ `Task Intent Router`
→ `Candidate Capability Lookup`
→ `Availability Check`
→ `Risk / Mutation Effect Check`
→ `Governance / Policy Gate`
→ `Executor Selection`
→ `Verification Plan`
→ `Execution Decision`

Execution begins only after this decision is complete enough for the actual task risk.

## Decision Contract

Each execution decision SHOULD contain:

### Task identity
- `task_route`: selected route from Task Intent Router
- `task_goal`: compact intended outcome
- `project_key`: when project-scoped
- `owner_layer`: authoritative layer that owns the intended effect

### Capability selection
- `capability_key`
- `capability_status`
- `selection_reason`
- `mutation_effect`
- `risk_level`

### Executor selection
- `preferred_executor`
- `selected_executor`
- `fallback_used`: boolean
- `fallback_reason`: optional
- `executor_available`: boolean

### Governance state
- `environment_verified`
- `impact_checked`
- `user_approved`
- `rollback_plan_present`
- `protected_layer_hits`
- `policy_allowed`
- `missing_checks`

Only fields relevant to the actual risk/effect need to be populated. Do not manufacture unnecessary ceremony for low-risk reads.

### Scope lock
- `change_scope`: exact intended mutation/read scope
- `protected_invariants`: known stable paths or invariants that must remain unchanged
- `scope_expansion_allowed`: default false unless new verified evidence changes the true owner/effect and routing is deliberately recomputed

### Verification plan
- `pre_execution_verification`
- `post_execution_verification`
- `authoritative_success_evidence`
- `partial_verification_condition`: when full verification is unavailable

### Decision result
- `decision`: `execute | block | reclassify | investigate | await_approval`
- `reason`

## Decision Semantics

### execute
Use only when:
- the selected capability exists,
- its status permits use,
- the selected executor is actually available,
- required evidence is sufficient,
- Governance permits execution,
- scope is locked,
- verification is possible at the level appropriate to the task.

### block
Use when execution is prohibited by:
- Policy Gate denial,
- missing required approval,
- protected-layer restriction,
- unavailable required capability,
- unavailable required authoritative source,
- disabled capability,
- permission boundary.

Do not route around a block by choosing a more permissive tool.

### reclassify
Use when new verified evidence changes the true:
- owner,
- effect,
- risk,
- scope,
- dependency structure,
- task type.

Return to Task Intent Router and recompute capability selection.

### investigate
Use when uncertainty is too high to choose a safe execution path. Route to the registered diagnostic capability and gather the minimum evidence needed to decide.

### await_approval
Use when execution is otherwise valid but the active Governance level requires explicit approval that is not yet present.

## Capability Selection Rules

1. Use the smallest capability that fully owns the intended effect.
2. Prefer a stable `active` capability over a `degraded` or `experimental` one when both can satisfy the task.
3. Use `degraded` only when its known limitation does not invalidate the required verification or safety boundary.
4. Never choose `experimental` silently for production/high-risk work.
5. Never choose `disabled`.
6. If no registered capability owns the effect, do not improvise a new execution path. Classify the task as capability-gap / design work first.

## Executor Selection Rules

1. Check current live availability; registry status is not a live connection guarantee.
2. Prefer the registered preferred executor when it is available and suitable.
3. Use a fallback only if it implements the same capability contract or explicitly compatible subset.
4. Re-run Governance if fallback changes risk, permissions, data boundary, cost, or mutation class.
5. Do not let an executor modify its own permissions or approval state.
6. Do not use an executor merely because it is convenient if another layer owns the effect.

## Simple Task Fast Path

For a low-risk, read-only, clearly owned task with an active capability and live executor:

`Route -> Capability -> Availability -> Execute -> Verify`

Do not force a full visible governance ceremony when no material risk exists.

The contract exists to reduce drift, not slow down simple work.

## High-Risk Path

For high/critical tasks:

`Route -> Capability -> Live Source Verification -> Impact -> Policy Gate -> Scope Lock -> Approval/Rollback -> Execute -> Strong Verification`

If any required check is missing, decision is `await_approval`, `investigate`, or `block`.

## Incident Path

For incidents/faults:

1. Task Intent Router selects Incident/Fault.
2. Execution Router selects `diagnostics.root_cause_analysis` first when owner/root cause is not verified.
3. Diagnosis identifies the owning layer and repair class.
4. Reclassify into the actual mutation capability.
5. Run Governance for the mutation.
6. Execute smallest correct repair.
7. Verify exact affected path.

Do not repair while still pretending the diagnostic capability itself owns the mutation.

## Creative / Architecture Path

For new feature or architecture tasks:

1. Task Intent Router may select `creative.explore_and_evaluate`.
2. Exploration remains read-only analysis.
3. Selected design must identify owner, scope, risk, migration/compatibility impact, and verification target.
4. Execution Router then selects the actual mutation capability.
5. Governance applies to that mutation capability, not to the creative analysis step.

`Explore != Execute` remains enforced.

## Degraded Capability Rule

When a capability is `degraded`, the decision MUST include the known degraded boundary.

Example:
`runtime.memory_gateway_transport` may be used only with an explicit note that deployment/JWT configuration and database-side runtime validation are verified while complete external HTTP dual-auth transport remains pending.

Do not claim stronger verification than evidence supports.

## Verification Rule

Executor return value is not sufficient proof of success.

The decision must identify authoritative success evidence before execution whenever practical.

Examples:
- GitHub write -> read back file/commit
- Supabase migration -> inspect migration history + resulting schema/security state
- data write -> query canonical target state
- deployment -> inspect deployed function/config + runtime request when supported
- context pack -> read back exact context id/status/memory selection

If authoritative post-verification cannot be performed, result must be classified as partially verified.

## Anti-Drift Rule

The Execution Router exists to prevent this pattern:

`User asks -> ChatGPT sees available tool -> chooses tool -> retrofits rationale`

Required pattern:

`User asks -> identify task route -> identify owning capability -> check Governance -> choose executor -> verify`

This preserves reasoning flexibility while reducing arbitrary tool choice.

## No-Persistence Boundary

This v1 contract is GitHub-only and read-only as architecture.

Do not add a Supabase execution-router table, queue, state machine, or autonomous mutation engine yet.

First observe whether the decision contract improves real task consistency and reduces drift without making simple tasks slower.

## Observation Gate

Before implementing Execution Journal or persistent router state, observe real use for:
- wrong capability selection,
- unnecessary capability chaining,
- simple tasks becoming over-engineered,
- failure to reclassify after new evidence,
- inappropriate fallback use,
- missing post-execution verification,
- actual reduction in ad-hoc tool selection.

Only persist or automate the router after evidence shows the decision layer is useful and stable.
