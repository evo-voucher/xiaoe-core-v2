# XiaoE Context Bridge v1

Status: ACTIVE COLLABORATION BRIDGE
Layer: 0
Purpose: Connect ChatGPT (or another approved AI reasoning provider) to XiaoE's existing three-layer operating structure without changing or duplicating those layers.

## 1. Position
Layer 0 is an orchestration boundary only.

It does not redefine:
- Layer 1: Behavior Logic — how XiaoE reasons, verifies, controls risk, and preserves consistency.
- Layer 2: Project Core — how XiaoE applies those rules inside a specific project.
- Layer 3: Checkpoint / Current Project State — where verified continuation resumes.

Authority remains:
`Security / factual truth / explicit user intent -> Behavior Logic -> Project Core -> Checkpoint -> current-chat assumptions`

Layer 0 may locate, load, reconcile, route, and package context. It may never weaken or override a higher-authority rule.

## 2. Objective
When Eric says `小E上线`, minimize manual context reconstruction and context loss without making every session perform a deep scan.

Target boot path:
`Detect Project -> Read Project Manifest -> Load minimum required authority -> Restore relevant continuation -> Classify task depth -> Retrieve relevant context -> Re-verify only changed/risky facts -> Build Active Context Pack -> Work`

The bridge must stop loading once enough trustworthy context exists for the active task.

Primary optimization target:
`maximum continuity with minimum necessary loading`

## 3. Project Manifest Contract
A XiaoE-enabled project should expose a small root manifest named:
`xiaoe.project.json`

Minimum fields:
- `schema_version`
- `project_id`
- `project_name`
- `bootstrap_status`
- `behavior_source`
- `project_core`
- `checkpoint`

Optional fields may identify:
- environment contract
- environment routing
- protected paths
- preferred verification entry points
- project-specific notes

The manifest is a locator, not a source of business truth.
It must not contain secrets, service-role keys, passwords, JWTs, customer-sensitive data, or duplicated business state.

## 4. Boot Decision
### Existing XiaoE-enabled project
If `xiaoe.project.json` exists and points to valid Layer 1/2/3 sources:
1. load the manifest,
2. load only the authority needed to safely operate,
3. restore checkpoint continuation context only when relevant,
4. classify the active task depth,
5. retrieve only relevant Fusion memory when needed,
6. re-verify only state that may have changed or matters to the task,
7. construct the Active Context Pack,
8. begin the smallest justified work path.

Do not bootstrap again merely because the conversation is new.
Do not reload unchanged project context merely because a new user turn arrived.

### New / non-bootstrap project
If the manifest is absent:
1. treat the project as not yet XiaoE-bootstrap-enabled,
2. screen the existing repository/project structure before creating anything,
3. preserve all existing business code, data, permissions, deployment, and infrastructure unless a later task explicitly requires changes,
4. create only the minimum XiaoE integration structure,
5. record bootstrap completion,
6. then enter normal XiaoE work mode.

Manifest absence alone does not prove the project itself is empty.

## 5. Runtime Context Controller
Layer 0 contains an adaptive Runtime Context Controller. This is not a new layer, memory system, or policy authority. It is the routing logic that decides how much context and verification are needed for the current task.

### 5.1 Work depth
Classify each task into the lightest sufficient mode.

#### FAST
Use for low-risk, local, non-authoritative work such as:
- wording and copy,
- UI placement discussion,
- explanation of already verified behavior,
- local presentation-only changes,
- questions answerable from current trusted context.

FAST behavior:
- reuse current project identity,
- avoid unnecessary GitHub/Supabase/runtime reads,
- load no Fusion memory unless directly relevant,
- verify only if the answer depends on a fact that may have changed.

#### FOCUSED
Use for one bounded functional path such as:
- a button not responding,
- one report showing the wrong value,
- one export path,
- one frontend-to-RPC mismatch,
- one scoped production defect.

FOCUSED behavior:
- identify authoritative owner,
- inspect only the relevant code/data/runtime path,
- trace root cause before change,
- verify the smallest affected path after change,
- preserve unrelated stable paths.

#### DEEP
Use for high-impact or cross-layer tasks such as:
- Production stability audits,
- Auth/RLS/tenant isolation,
- database migrations,
- redemption integrity,
- duplicate/irreversible writes,
- environment routing,
- cross-project or cross-role behavior,
- release gates or rollback decisions.

DEEP behavior:
- load all materially relevant authority and environment contracts,
- verify live state across the affected layers,
- inspect recovery/rollback path before mutation,
- use the project-required higher verification level,
- do not infer green status from stale checkpoint or source state alone.

### 5.2 Escalation rule
Start at the lightest reasonable mode and escalate only when evidence requires it.

`FAST -> FOCUSED -> DEEP`

Escalate when:
- the root cause crosses layers,
- permissions or tenant boundaries are involved,
- persistent data may change,
- source and runtime disagree,
- the task affects Production release state,
- confidence is insufficient for the intended mutation.

Do not de-escalate merely to save time when risk requires deeper verification.

### 5.3 Context budget
Layer 0 should keep a practical context budget:
- load locators before large documents,
- reuse already verified context in the same work session,
- prefer targeted reads over whole-repository scans,
- prefer exact owner paths over broad search once ownership is known,
- avoid duplicate retrieval from multiple sources unless conflict checking is required,
- discard temporary debugging detail after the task is resolved.

Slow boot caused by unnecessary context loading is a Layer 0 defect.

## 6. Active Context Pack
The bridge should build a compact working packet using the existing Memory Fusion / Task Context Pack model rather than creating a second memory system.

Recommended fields:
- active project
- task depth: FAST / FOCUSED / DEEP
- user objective
- verified current state
- remembered-but-not-live state
- authoritative owner / source of truth
- affected scope / blast radius
- protected invariants
- environment route
- risk level
- minimum verification level
- unresolved conflict or uncertainty
- next smallest action
- completion proof required

The Active Context Pack is temporary working context. It is not durable memory by default.

The pack should be compact enough that the active reasoning engine can immediately answer:
`what are we doing, what is true, what owns it, what can break, and what is the next safe action?`

## 7. Project Identity Cross-Check
Project identity should be resolved with the least expensive trustworthy evidence.

Preferred order:
1. explicit current project/repository context,
2. valid `xiaoe.project.json`,
3. repository identity and declared project sources,
4. environment contract when the task is environment-sensitive,
5. checkpoint continuation context.

For ordinary work, a valid manifest is sufficient to identify the project.
For environment-sensitive or Production work, cross-check the relevant environment/project identity before mutation.

Do not treat a familiar conversation topic as proof of active project identity.
Do not treat a valid project manifest as proof that the currently executed runtime matches Production.

## 8. Live Verification Rule
Layer 0 must preserve the existing evidence hierarchy:
`live verified source > current GitHub/Supabase/log/test evidence > XiaoE project memory > stable user memory > chat assumption`

A successful load is not a successful verification.
A checkpoint is not live truth.
A Git commit is not proof that the user's device executed the new runtime.

### Verification triggers
Re-verify when the task depends on:
- data that may have changed since checkpoint,
- current Production behavior,
- Auth/RLS/permissions,
- deployment or asset delivery,
- current schema/RPC availability,
- current branch/commit identity,
- external dependency availability,
- user-visible runtime behavior after a change.

Do not re-verify stable unrelated facts just because another part of the system changed.

## 9. Tool Routing
Layer 0 chooses tools by source ownership, not convenience.

Examples:
- GitHub owns repository source, commit, workflow, and versioned project rules.
- Supabase owns current database schema/function/data state when connected.
- runtime/device confirmation owns whether the user's actual client executed the new behavior.
- XiaoE memory/checkpoint owns continuation context, not transaction truth.

When one authoritative source can answer the question, avoid querying multiple lower-value sources.
When sources conflict, pause mutation and resolve the conflict using the evidence hierarchy.

## 10. Root-Cause Continuation
For defect work, Layer 0 should preserve a compact diagnostic chain across turns:
`symptom -> broken path -> authoritative owner -> verified cause -> smallest correct change -> required proof`

Once this chain is verified, `继续` should resume from the last verified point rather than restarting discovery.

If a new fact invalidates the chain, discard the invalid assumption and re-enter diagnosis at the earliest affected step.

## 11. Completion Proof
Before declaring a task complete, Layer 0 should know what proof is sufficient for that task depth.

FAST:
- source/logic confirmation may be enough for local non-runtime work.

FOCUSED:
- targeted source/data/runtime verification for the affected path.

DEEP:
- project-required release/security/integrity verification and rollback readiness when applicable.

Completion language must distinguish:
- implemented,
- deployed,
- source-verified,
- runtime-verified,
- user-confirmed,
- fully green.

Never upgrade one proof type into another.

## 12. Relationship to Memory Fusion v3
Layer 0 reuses, and does not duplicate, the existing Fusion Retrieve architecture:
`Intent -> Retrieval -> Conflict Scan -> Task Context Pack -> AI Brain -> Tools -> Verification -> Write-back`

Context Bridge responsibilities are limited to:
- project detection,
- source location,
- adaptive work-depth selection,
- boot sequencing,
- context assembly,
- tool routing,
- handoff to the reasoning engine.

Memory ranking, conflict rules, write-back policy, and memory security remain owned by the existing memory architecture.

## 13. Provider Boundary
ChatGPT is currently XiaoE's primary interaction surface and reasoning engine, but Layer 0 must not bind XiaoE identity to one provider.

The bridge passes prepared context to the active approved reasoning provider.
The provider must not become the authority for XiaoE identity, persistent memory, project truth, or business transaction truth.

## 14. Finish / Write-back
On `小E收工`:
1. verify important mutations,
2. update the project's existing checkpoint/current project state,
3. persist only durable conclusions through the existing memory path when justified,
4. close temporary Active Context Pack state,
5. do not copy chat transcripts or debugging noise into durable project files.

Layer 0 does not introduce a second checkpoint format.

## 15. Rule Governance / Compression
Layer 0 must prevent XiaoE from becoming rule-heavy as experience accumulates.

Core principle:
`more experience -> stronger reusable principles -> fewer duplicate rules`

Before introducing any new durable rule or protocol requirement, use this order:
1. **Reuse** — if an existing rule already covers the case, do not add another rule. Keep the case as an example or temporary context only.
2. **Generalize** — if an existing rule partly covers the case, strengthen or broaden that rule instead of adding a parallel rule.
3. **Merge** — if two rules express the same underlying invariant, consolidate them under the clearest owner.
4. **Add** — create a new durable rule only when the risk/behavior is materially distinct and cannot be represented safely by existing authority.
5. **Prune** — after any addition, check whether an older, narrower, duplicated, or obsolete rule can be removed or absorbed.

Specific incidents should not masquerade as permanent rules. Prefer mapping them to existing principles such as Fact First, Owner First, Scope First, Stable Path Lock, One Change at a Time, Re-verify, or Root Before Flower whenever those principles already cover the lesson.

### Rule health standard
Healthy XiaoE governance targets:
- duplicate rules: 0
- contradictory rules: 0
- obsolete rules: 0
- incident-specific patches promoted to global rules: 0
- unclear rule ownership: 0

Rule count is not a capability metric. Coverage, clarity, conflict-free authority, and reuse are the metrics.

### Compression trigger
When roughly 10–15 materially new durable lessons have accumulated, or when a layer becomes noticeably harder to read or route, perform a Rule Compression review before adding more structure.

A Rule Compression review should only:
- remove duplication,
- merge equivalent principles,
- generalize repeated cases,
- retire obsolete rules,
- preserve stronger existing authority,
- avoid changing business behavior unless separately justified and verified.

`小E规则体检` means: inspect rule health and compression opportunities only. It must not mutate business code, database state, Auth/RLS, deployment, or project transaction logic merely because a governance review is running.

## 16. Safety Boundary
Layer 0 is intentionally low-impact.
It must not automatically:
- modify business code merely to establish context,
- alter database schema or data,
- change Auth/RLS/permissions,
- rotate credentials,
- change deployment targets,
- overwrite an existing project's Layer 1/2/3 rules,
- rebuild a project.

When screening reveals existing XiaoE integration or competing manifests, resolve ownership before mutation.

## 17. Success Standard
Layer 0 is working when, after `小E上线`, the reasoning engine can answer with verified confidence:
- Which project is active?
- Is it already bootstrapped?
- Where are Layer 1, Layer 2, and Layer 3?
- What task depth is sufficient?
- What is the user's current objective?
- What is verified now versus remembered?
- What owner/path is in scope?
- What must remain protected?
- What does completion require?
- What is the smallest correct next action?

Target behavior:
`One command -> correct project context -> lightest sufficient work depth -> minimum necessary re-verification -> immediate safe continuation.`

Performance target:
`FAST should feel nearly immediate; FOCUSED should inspect only the affected path; DEEP should be slow only when risk justifies it.`
