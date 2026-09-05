# XiaoE Capability Registry v1

Status: ACTIVE REGISTRY
Date: 2026-08-24
Contract: `core/capabilities/CAPABILITY_REGISTRY_CONTRACT_V1.md`
Purpose: Record currently verified XiaoE capability ownership, execution paths, risk classes, and verification requirements without overriding Behavior or Governance.

## Authority

This registry is descriptive only.

`Behavior > Governance > Task Intent Router > Capability Registry > Executor`

Availability is not authorization. A capability marked active may still require source checks, scopes, Policy Gate approval, protected-layer handling, or explicit user approval before execution.

## Registry

| Capability | Status | Risk | Mutation effect | Preferred executor | Required scope / approval | Verification |
|---|---|---:|---|---|---|---|
| `memory.retrieve` | active | low | read_only | `service_fusion_retrieve` | `memory:read` when runtime-mediated | Confirm returned memories are active, verified, unexpired and scoped correctly |
| `memory.conflict_scan` | active | low | read_only | `service_find_memory_conflicts` | `memory:read` when runtime-mediated | Confirm duplicate/superseded conflict results against canonical memory rows |
| `memory.save_verified` | active | medium | persistent_write | `service_save_memory_v2` | `memory:write`; Governance applies to durable write-back | Read back the saved canonical memory and confirm verification metadata / dedupe behavior |
| `context.create` | active | low | persistent_write | `service_create_task_context_pack` | `project:state` when runtime-mediated | Confirm exactly one context pack, expected memory IDs, conflict IDs and risk level |
| `context.close` | active | low | persistent_write | `service_close_task_context_pack` | `project:state` when runtime-mediated | Read back status / closed_at and confirm target context ID |
| `governance.screening` | active | low | read_only | `service_xiaoe_screening` | service boundary | Confirm system version, core-table presence and relevant counts |
| `governance.bootstrap_v41` | active | low | read_only | `service_xiaoe_bootstrap_v41` | service boundary | Confirm `success=true`, `bootstrap_version=4.1.0`, policy rules, memory retrieval and conflicts |
| `governance.policy_gate` | active | high | read_only decision | `service_policy_gate` | Existing v4.1 Governance | Verify deny and allow cases against required checks for actual risk level |
| `governance.protect_layer` | active | high | persistent_write | `service_protect_layer` | Governance high; explicit scope evidence | Read back protected layer, project key, layer key, status and evidence |
| `governance.reopen_protected_layer` | active | high | persistent_write | `service_reopen_protected_layer` | explicit user approval required | Confirm approved target changed from protected to reopened with reason |
| `governance.promote_learning` | active | high | persistent_write | `service_promote_learning` | explicit user approval + promotion threshold | Confirm promotion row and memory metadata; reject below-threshold memory |
| `github.read` | active | low | read_only | connected GitHub executor | repository read permission | Re-fetch authoritative file/commit/repository state |
| `github.write` | active | medium | reversible_write | connected GitHub executor | repository write permission; Governance based on affected layer | Read back target file and resulting commit SHA |
| `github.verify_commit` | active | low | read_only | connected GitHub executor | repository read permission | Fetch commit/status and compare intended changed path/state |
| `supabase.read_schema` | active | low | read_only | connected Supabase executor | project read access | Inspect tables, migrations, functions, advisors or canonical SQL state |
| `supabase.apply_migration` | active | high | persistent_write | `apply_migration` | Governance high; environment + impact + approval checks as applicable | Inspect migration history and resulting schema/security state |
| `supabase.execute_data_operation` | active | medium | persistent_write | `execute_sql` / service RPC | Existing RLS/service boundary; risk escalates with effect | Query canonical resulting state; do not rely only on command success |
| `supabase.deploy_edge_function` | active | high | persistent_write | `deploy_edge_function` | project deployment permission + Governance high | Inspect deployed function status/version/config and runtime path when possible |
| `runtime.memory_gateway_transport` | degraded | high | external_side_effect | `memory-gateway` | valid destination JWT + `X-XiaoE-Runtime-Key` + runtime scope | Deployment is verified ACTIVE with `verify_jwt=true`; full HTTP request with both auth layers remains pending |
| `diagnostics.root_cause_analysis` | active | low | read_only analysis | XiaoE reasoning + verified source tools | none for analysis; execution governed separately | Confirm evidence timeline, first divergence, owning layer and targeted verification path |
| `creative.explore_and_evaluate` | active | low | read_only analysis | XiaoE reasoning | none for exploration; execution governed separately | Confirm selected option has defined owner, mutation scope and verification target |

## Capability Notes

### Memory / Context
Memory Fusion v3 remains the canonical memory execution layer. Only active, verified, unexpired memories participate in normal Fusion Retrieve. Context packs are working context, not permanent knowledge.

### Governance
Capability availability never replaces v4.1 Policy Gate. High and critical execution remains subject to existing environment, impact, approval and rollback requirements.

### GitHub
GitHub remains source of truth for versioned behavior, architecture, migrations, runtime contracts and history. Registry entries for GitHub describe the execution class, not permanent assurance that every future session has an authenticated GitHub connector. Executor availability must still be checked at runtime.

### Supabase
Supabase is the persistent XiaoE memory/runtime backend. Schema and deployment writes are high-risk capability classes even when the connector is available. Current active migration history remains `000-009`; registry growth does not authorize a new migration.

### Runtime Gateway
`runtime.memory_gateway_transport` is deliberately `degraded`, not `active`, because the fresh rebuild verified deployment, JWT enforcement configuration and database-side runtime identity validation, but the final external HTTP request carrying both authentication layers has not yet been executed.

### Diagnostics
`diagnostics.root_cause_analysis` is an analysis capability. It may identify the owning layer and proposed repair, but it does not automatically authorize the resulting mutation capability.

### Creative Exploration
`creative.explore_and_evaluate` expands solution space only. `Explore != Execute`; chosen implementation must return to normal Behavior/Governance execution control.

## Executor Availability Rule

The registry records a verified capability class, not an eternal live connection.

Before execution XiaoE must still verify that the preferred executor is actually connected/available in the current environment. If unavailable, use only a compatible registered fallback permitted by Governance. Do not hallucinate tool availability and do not substitute an unrelated executor merely to complete a task.

## Anti-Drift Rule

When the Task Intent Router selects a task path:

`Intent route -> capability lookup -> availability check -> Governance -> executor -> verification`

Do not skip capability ownership by choosing a convenient tool first.
Do not let the registry become a second Behavior system.
Do not add capability-specific rules that duplicate frozen Behavior or active Governance.

## Change Rule

A registry entry may be added or changed only when one of the following is true:
- a capability already exists and its verified contract is being recorded,
- a new capability has been implemented and verified,
- a previously active capability is degraded/disabled by evidence,
- executor or verification ownership materially changes.

Do not mark a planned capability `active` before implementation and verification.

## Current Boundary

This registry is GitHub-only source of truth. It is intentionally not persisted into Supabase yet.

Next internal evolution step: define a read-only Execution Router decision contract that consumes Task Intent Router output plus this registry, without introducing a new mutation engine or changing existing Behavior/Governance.
