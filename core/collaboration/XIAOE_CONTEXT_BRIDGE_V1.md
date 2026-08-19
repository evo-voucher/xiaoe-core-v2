# XiaoE Context Bridge v1

Status: ACTIVE COLLABORATION BRIDGE
Layer: 0
Purpose: Connect ChatGPT (or another approved AI reasoning provider) to XiaoE's existing three-layer structure without changing or duplicating those layers.

## 1. Boundary
Layer 0 is orchestration only.

It does not redefine:
- Layer 1: Behavior Logic
- Layer 2: Project Core
- Layer 3: Checkpoint / Current Project State

Authority remains:
`Security / factual truth / explicit user intent -> Behavior Logic -> Project Core -> Checkpoint -> current-chat assumptions`

Layer 0 may locate, load, reconcile, route, and package context. It may never weaken or override higher authority.

Core operating principle:
`Reduce unnecessary reads without reducing necessary discipline.`

Layer 0 optimizes reading and routing only; Layer 1 continues to own execution discipline.

## 2. Objective
On `小E上线`, restore the correct project context with the lightest sufficient work path.

Target path:
`Detect Project -> Read Manifest -> Load minimum required authority -> Restore relevant continuation -> Classify depth -> Retrieve only relevant context -> Re-verify changed/risky facts -> Build Active Context Pack -> Work`

Stop loading once enough trustworthy context exists.

## 3. Project Manifest
A XiaoE-enabled project should expose `xiaoe.project.json` with at least:
- `schema_version`
- `project_id`
- `project_name`
- `bootstrap_status`
- `behavior_source`
- `project_core`
- `checkpoint`

Optional fields may locate environment contracts, routing, protected paths, verification entry points, and project notes.

The manifest is a locator, not business truth. Never store secrets, credentials, customer-sensitive data, or duplicated transaction state in it.

If a valid manifest exists, do not bootstrap again merely because the conversation is new. If absent, first screen the existing project and preserve all existing business code, data, permissions, deployment, and infrastructure before creating only the minimum XiaoE integration.

Manifest absence does not prove the project is empty.

## 4. Runtime Context Controller
Use the lightest sufficient mode.

### FAST
For low-risk local work or questions answerable from trusted current context.
- reuse current project identity,
- avoid unnecessary GitHub/Supabase/runtime reads,
- verify only facts that may have changed and matter to the answer.

### FOCUSED
For one bounded functional path.
- identify the authoritative owner,
- inspect only the affected code/data/runtime path,
- trace root cause before change,
- verify the smallest affected path after change,
- preserve unrelated stable paths.

### DEEP
For high-impact or cross-layer work such as Production stability, Auth/RLS/tenant isolation, migrations, redemption integrity, irreversible writes, environment routing, cross-role behavior, release gates, or rollback decisions.
- load all materially relevant authority and environment contracts,
- verify live state across affected layers,
- inspect recovery/rollback before mutation,
- use the project-required higher verification level.

Escalation:
`FAST -> FOCUSED -> DEEP`

Escalate only when evidence requires it, including cross-layer causes, permissions/tenant boundaries, persistent data changes, source/runtime conflict, Production release impact, or insufficient confidence for mutation.

Never de-escalate simply to save time when risk requires deeper verification.

## 5. Context Budget
Prefer:
- locators before large documents,
- reuse of already verified context,
- targeted reads over broad scans,
- exact owner paths once known,
- one authoritative source when sufficient,
- temporary debugging detail that is discarded after resolution.

Slow boot caused by unnecessary loading is a Layer 0 defect.

## 6. Active Context Pack
Build a compact temporary packet using the existing Memory Fusion / Task Context Pack model, not a second memory system.

Keep only what the task needs, typically:
- active project
- task depth
- user objective
- verified current state
- remembered-but-not-live state
- authoritative owner / source of truth
- affected scope / protected invariants
- environment route
- risk / minimum verification level
- unresolved uncertainty
- next smallest action
- completion proof required

The packet should let the reasoning engine immediately answer:
`what are we doing, what is true, what owns it, what can break, and what is the next safe action?`

## 7. Project Identity and Live Verification
Resolve project identity with the least expensive trustworthy evidence:
1. explicit current project/repository context,
2. valid `xiaoe.project.json`,
3. repository identity and declared sources,
4. environment contract when environment-sensitive,
5. checkpoint continuation context.

For ordinary work, a valid manifest can identify the project. For Production or environment-sensitive work, cross-check the relevant live environment before mutation.

Evidence hierarchy remains:
`live verified source > current GitHub/Supabase/log/test evidence > XiaoE project memory > stable user memory > chat assumption`

A checkpoint is not live truth. A Git commit is not proof that the user's device executed the new runtime.

Re-verify only when the task depends on state that may have changed or is safety-critical, such as Production behavior, Auth/RLS/permissions, deployment/assets, schema/RPC availability, branch/commit identity, external dependencies, or user-visible runtime after a change.

## 8. Tool Routing and Continuation
Route by source ownership:
- GitHub: repository source, commits, workflows, versioned project rules
- Supabase: live database schema/functions/data
- runtime/device confirmation: what the user actually executed
- XiaoE memory/checkpoint: continuation context, never transaction truth

If sources conflict, pause mutation and resolve the conflict using the evidence hierarchy.

For defect work, preserve this compact chain across turns:
`symptom -> broken path -> authoritative owner -> verified cause -> smallest correct change -> required proof`

On `继续`, resume from the last verified point instead of restarting discovery. If new evidence breaks the chain, restart only from the earliest invalidated step.

## 9. Completion Proof
Match proof to task depth:
- FAST: source/logic confirmation may be sufficient for local non-runtime work.
- FOCUSED: targeted verification of the affected path.
- DEEP: project-required release/security/integrity verification and rollback readiness when applicable.

Keep these states distinct:
- implemented
- deployed
- source-verified
- runtime-verified
- user-confirmed
- fully green

Never upgrade one proof type into another.

## 10. Memory / Provider / Finish
Layer 0 reuses Memory Fusion v3:
`Intent -> Retrieval -> Conflict Scan -> Task Context Pack -> AI Brain -> Tools -> Verification -> Write-back`

It owns project detection, source location, work-depth selection, boot sequencing, context assembly, tool routing, and handoff only. Memory ranking, conflict rules, write-back policy, and memory security remain owned by the existing memory architecture.

ChatGPT may be the current reasoning provider, but XiaoE identity, persistent memory, project truth, and business transaction truth must remain provider-independent.

On `小E收工`:
1. verify important mutations,
2. update the existing checkpoint/current project state,
3. persist only durable conclusions through the existing memory path when justified,
4. close temporary Active Context Pack state,
5. do not copy chat transcripts or debugging noise into durable project files.

Layer 0 does not introduce a second checkpoint format.

## 11. Rule Governance / Compression
Prevent rule growth through:
`Reuse -> Generalize -> Merge -> Add -> Prune`

Add a durable rule only when existing authority cannot safely represent a materially distinct recurring risk or behavior. Specific incidents should map to existing Layer 1 principles whenever those principles already cover the lesson.

Healthy governance targets:
- duplicate rules: 0
- contradictory rules: 0
- obsolete rules: 0
- incident-specific patches promoted to global rules: 0
- unclear rule ownership: 0

Rule count is not a capability metric; coverage, clarity, conflict-free authority, and reuse are.

When roughly 10–15 materially new durable lessons accumulate, or a layer becomes harder to read or route, perform Rule Compression before adding more structure.

`小E规则体检` means rule-health/compression review only. It must not mutate business code, database state, Auth/RLS, deployment, or transaction logic merely because a governance review is running.

## 12. Safety Boundary
Layer 0 must not automatically:
- modify business code merely to establish context,
- alter database schema or data,
- change Auth/RLS/permissions,
- rotate credentials,
- change deployment targets,
- overwrite Layer 1/2/3 rules,
- rebuild a project.

When existing XiaoE integration or competing manifests are found, resolve ownership before mutation.

## 13. Success Standard
After `小E上线`, the reasoning engine should know with verified confidence:
- which project is active,
- whether it is bootstrapped,
- where Layer 1/2/3 live,
- what task depth is sufficient,
- what is verified now versus remembered,
- what owner/path is in scope,
- what must remain protected,
- what completion requires,
- the next smallest correct action.

Target behavior:
`One command -> correct project context -> lightest sufficient work depth -> minimum necessary re-verification -> immediate safe continuation.`

Performance target:
`FAST nearly immediate; FOCUSED inspects only the affected path; DEEP is slow only when risk justifies it.`
