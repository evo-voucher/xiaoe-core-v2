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

Layer 0 may locate, load, reconcile, and package context. It may never weaken or override a higher-authority rule.

## 2. Objective
When Eric says `小E上线`, minimize manual context reconstruction and context loss.

Target boot path:
`Detect Project -> Read Project Manifest -> Load Behavior -> Load Project Core -> Load Checkpoint -> Retrieve relevant Fusion memory when available -> Re-verify changed live facts -> Build Active Context Pack -> Work`

The bridge should stop loading once enough trustworthy context exists for the active task.

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
2. load the declared Layer 1/2/3 sources,
3. restore the checkpoint as continuation context only,
4. retrieve only relevant Fusion memory when needed,
5. re-verify state that may have changed,
6. construct the Active Context Pack,
7. begin the smallest justified work path.

Do not bootstrap again merely because the conversation is new.

### New / non-bootstrap project
If the manifest is absent:
1. treat the project as not yet XiaoE-bootstrap-enabled,
2. screen the existing repository/project structure before creating anything,
3. preserve all existing business code, data, permissions, deployment, and infrastructure unless a later task explicitly requires changes,
4. create only the minimum XiaoE integration structure,
5. record bootstrap completion,
6. then enter normal XiaoE work mode.

Manifest absence alone does not prove the project itself is empty.

## 5. Active Context Pack
The bridge should build a compact working packet using the existing Memory Fusion / Task Context Pack model rather than creating a second memory system.

Recommended fields:
- active project
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

The Active Context Pack is temporary working context. It is not durable memory by default.

## 6. Live Verification Rule
Layer 0 must preserve the existing evidence hierarchy:
`live verified source > current GitHub/Supabase/log/test evidence > XiaoE project memory > stable user memory > chat assumption`

A successful load is not a successful verification.
A checkpoint is not live truth.
A Git commit is not proof that the user's device executed the new runtime.

## 7. Relationship to Memory Fusion v3
Layer 0 reuses, and does not duplicate, the existing Fusion Retrieve architecture:
`Intent -> Retrieval -> Conflict Scan -> Task Context Pack -> AI Brain -> Tools -> Verification -> Write-back`

Context Bridge responsibilities are limited to:
- project detection,
- source location,
- boot sequencing,
- context assembly,
- handoff to the reasoning engine.

Memory ranking, conflict rules, write-back policy, and memory security remain owned by the existing memory architecture.

## 8. Provider Boundary
ChatGPT is currently XiaoE's primary interaction surface and reasoning engine, but Layer 0 must not bind XiaoE identity to one provider.

The bridge passes prepared context to the active approved reasoning provider.
The provider must not become the authority for XiaoE identity, persistent memory, project truth, or business transaction truth.

## 9. Finish / Write-back
On `小E收工`:
1. verify important mutations,
2. update the project's existing checkpoint/current project state,
3. persist only durable conclusions through the existing memory path when justified,
4. close temporary Active Context Pack state,
5. do not copy chat transcripts or debugging noise into durable project files.

Layer 0 does not introduce a second checkpoint format.

## 10. Safety Boundary
Layer 0 is intentionally low-impact.
It must not automatically:
- modify business code merely to establish context,
- alter database schema or data,
- change Auth/RLS/permissions,
- rotate credentials,
- change deployment targets,
- overwrite an existing project's XiaoE rules,
- rebuild a project.

When screening reveals existing XiaoE integration or competing manifests, resolve ownership before mutation.

## 11. Success Standard
Layer 0 is working when, after `小E上线`, the reasoning engine can answer with verified confidence:
- Which project is active?
- Is it already bootstrapped?
- Where are Layer 1, Layer 2, and Layer 3?
- What is the user's current objective?
- What is verified now versus remembered?
- What owner/path is in scope?
- What must remain protected?
- What is the smallest correct next action?

Target behavior:
`One command -> correct project context -> minimum necessary re-verification -> immediate safe continuation.`
