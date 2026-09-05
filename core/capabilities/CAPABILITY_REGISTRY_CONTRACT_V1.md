# XiaoE Capability Registry Contract v1

Status: PROPOSED CONTRACT
Date: 2026-08-24
Purpose: Define a stable, non-authoritative registry contract for describing XiaoE operational capabilities without creating a second behavior or governance system.

## Authority Boundary

**Capability Registry describes capability availability. It does not define XiaoE's behavioral constitution.**

Authority order remains:
1. Frozen Behavior Logic
2. Active Governance / Policy Gate / protected-layer rules
3. Task Intent Router and project/domain protocols
4. Capability Registry
5. Executor/provider/tool implementation details

The registry MUST NOT:
- override `core/behavior/XIAOE_BEHAVIOR_LOGIC_V1.md`,
- weaken or bypass Policy Gate requirements,
- change protected-layer rules,
- grant its own permissions,
- treat executor availability as permission to execute,
- redefine security/auth/RLS ownership,
- store secrets,
- store business transaction truth,
- become a second routing constitution.

Rule:

`Registry can describe what is available; it cannot authorize what Behavior or Governance forbids.`

## Relationship to Task Intent Router

`TASK_INTENT_ROUTER_V1.md` classifies the task and selects the smallest useful capability path.

Capability Registry begins only after that routing decision and answers:
- which registered capability matches the selected path,
- whether that capability is currently available,
- which executor is preferred,
- which fallbacks are permitted,
- what scopes/approval class are required,
- how the result must be verified.

The Registry does not reinterpret user intent and does not silently widen task scope.

## Registry Record Contract

Each capability record SHOULD use the following fields.

### Identity
- `capability_key`: stable unique key, e.g. `github.read_repository_file`
- `version`: capability contract version
- `domain`: broad domain such as `github`, `supabase`, `memory`, `diagnostics`, `communication`, `reasoning`
- `description`: concise operational meaning
- `owner_layer`: authoritative layer that owns the effect of the capability

### Availability
- `status`: `active | degraded | experimental | disabled`
- `availability_source`: how availability was established, e.g. connected tool, deployed service, verified repository module
- `last_verified_at`: optional timestamp of last real availability verification

### Risk and permission
- `risk_level`: `low | medium | high | critical`
- `required_scopes`: runtime/tool scopes needed for execution
- `approval_class`: `none | governance_medium | governance_high | governance_critical`
- `mutation_effect`: `read_only | reversible_write | persistent_write | destructive | external_side_effect`

These fields describe requirements only. They do not satisfy the requirements by themselves.

### Executor mapping
- `preferred_executor`: executor identifier
- `fallback_executors`: ordered list of permitted alternatives
- `executor_constraints`: conditions that make an executor unsuitable

Executor identity is replaceable. XiaoE identity must not depend on one provider.

### Contract
- `input_contract`: minimum required inputs
- `output_contract`: expected normalized result shape
- `verification_contract`: how success must be verified
- `failure_contract`: expected failure classes and escalation behavior

### Metadata
- `tags`: routing/search tags
- `source_reference`: GitHub architecture/protocol/tool source used to define this capability
- `metadata`: non-secret extensible metadata

## Capability Status Semantics

### active
Capability and required executor path have been verified available for normal use.

### degraded
Capability remains usable but an expected executor, dependency, verification path, or scope is partially unavailable. Router may use a registered fallback if Governance allows it.

### experimental
Capability is not part of the stable execution path. It may be evaluated in isolated/low-risk conditions but must not silently replace a stable path.

### disabled
Capability must not be selected for execution. Historical records may remain for compatibility or audit.

## Executor Selection Rule

For a capability already selected by the Task Intent Router:

1. Confirm capability status.
2. Confirm the real executor/tool is available.
3. Confirm required source/context evidence.
4. Run the existing Policy Gate for the actual risk/effect.
5. Choose the smallest capable approved executor.
6. Prefer the verified stable executor before fallback.
7. Execute within the locked mutation scope.
8. Verify against `verification_contract`.
9. Classify result before any memory/write-back decision.

Availability is not authorization.
Fallback availability is not permission to widen scope.

## Fallback Rule

A fallback MAY be selected only when:
- the primary executor is actually unavailable, unsuitable, or failed for an executor-specific reason,
- the fallback implements the same capability contract or an explicitly compatible subset,
- the fallback does not increase risk without re-running Governance,
- required permissions are independently satisfied,
- verification remains possible.

A fallback MUST NOT be used to bypass:
- access controls,
- Policy Gate denial,
- missing user approval,
- protected-layer restrictions,
- unavailable authoritative source,
- the Two-Failure / Root-Cause rule.

Repeated same-path failure must enter root-cause analysis rather than cycling executors blindly.

## Verification Contract Rule

A capability is not successful merely because an executor returned `ok`.

Verification should identify the authoritative evidence for success. Examples:
- GitHub write -> read back the target file/commit
- Supabase DDL -> inspect resulting schema/migration state
- data write -> query canonical record/state
- deployment -> inspect deployed function/version/status and, where possible, execute the runtime path
- generated artifact -> inspect the produced artifact before handoff

If the authoritative verification path is unavailable, the result must be classified as partially verified rather than silently treated as complete.

## Registry Purity Rules

The Registry MUST remain descriptive and compact.

Do not put into the registry:
- long reasoning instructions,
- duplicate Behavior rules,
- incident-specific debugging steps,
- current project checkpoints,
- raw tool schemas,
- access tokens/keys/secrets,
- mutable business data,
- chat transcripts.

Those belong to Behavior/Governance, diagnostics, project state, runtime/tool layers, secure secret stores, business systems, or execution journal respectively.

## Initial Stable Capability Families

The first seed registry should be derived only from already verified XiaoE architecture and connected execution paths. Candidate families include:
- `memory.retrieve`
- `memory.save_verified`
- `memory.conflict_scan`
- `context.create`
- `context.close`
- `governance.screening`
- `governance.policy_gate`
- `governance.protect_layer`
- `github.read`
- `github.write`
- `github.verify_commit`
- `supabase.read_schema`
- `supabase.apply_migration`
- `supabase.execute_data_operation`
- `supabase.deploy_edge_function`
- `diagnostics.root_cause_analysis`
- `creative.explore_and_evaluate`

These are candidate registry entries, not new permissions and not proof that every executor is always connected.

## Anti-Drift Design

The Registry reduces ChatGPT drift by replacing ad-hoc executor guessing with explicit capability ownership and verification contracts.

It must not reduce necessary reasoning. ChatGPT/XiaoE may still reason about intent, evidence, trade-offs, and root cause, but execution selection should use the registered capability boundary when one exists.

Anti-drift rule:

`Reason freely inside the constitution; route execution through verified capability ownership.`

## Versioning Rule

Changing registry data or adding a capability does not require a XiaoE major/core version change by itself.

A new registry contract version is required only when the meaning or required fields of the registry contract change materially.

A XiaoE Core version promotion requires the separate architecture promotion gate and must not be implied by registry growth.

## Next Implementation Step

After this contract is reviewed, seed a read-only `CAPABILITY_REGISTRY_V1` from current verified architecture and tool boundaries.

Do not add Supabase persistence yet. Start with a versioned GitHub source-of-truth registry so behavior can be reviewed before adding runtime database state.
