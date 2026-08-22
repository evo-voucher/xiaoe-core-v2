# XiaoE Core v4.1 Governance Architecture

Status: ACTIVE
Date: 2026-08-22

## Positioning
XiaoE Core v4.1 is an additive governance layer over the existing active Memory Fusion v3 architecture. It does not replace or remove the current `memories`, `runtime_clients`, `task_context_packs`, Fusion Retrieve v3, legacy memory services, or memory-gateway v2.

## Why v4.1
The purpose of v4.1 is to reduce AI drift and make high-impact execution more controllable without sacrificing the stable Memory Fusion v3 runtime.

## Existing stable core preserved
- `memories`
- `runtime_clients`
- `task_context_packs`
- `service_fusion_retrieve`
- `service_find_memory_conflicts`
- `service_save_memory_v2`
- `service_create_task_context_pack`
- `service_close_task_context_pack`
- `memory-gateway` v2

## New governance components
### `xiaoe_system_meta`
Records active XiaoE Core version, architecture identity and capabilities.

### `xiaoe_policy_rules`
Stores active governance rules such as evidence-first, root-before-patch, protected stable layers, high-risk approval and verified learning promotion.

### `xiaoe_protected_layers`
Records project layers that have been verified healthy and should not be casually modified. Reopening a protected layer requires an explicit reason and human approval.

### `xiaoe_learning_promotions`
Separates ordinary memory from Master-level promoted learning. Promotion requires verified memory, sufficient importance/confidence and explicit approval.

## New service RPCs
- `service_xiaoe_screening()`
- `service_policy_gate(...)`
- `service_protect_layer(...)`
- `service_reopen_protected_layer(...)`
- `service_promote_learning(...)`
- `service_xiaoe_bootstrap_v41(...)`

## Policy Gate
Risk levels:
- low: allowed by default
- medium: requires `environment_verified`
- high: requires `environment_verified + impact_checked + user_approved`
- critical: high requirements plus `rollback_plan`

Protected-layer changes remain blocked unless explicit approval is present.

## Bootstrap v4.1
Bootstrap v4.1 returns:
- version/system metadata
- screening state
- active policy rules
- protected layers
- Fusion Retrieve v3 memories
- memory conflicts
- precedence order

Precedence:
1. Current explicit user instruction
2. Live verified source
3. Verified project memory
4. Verified core memory
5. Current-chat assumption

## Learning Promotion
Normal memory remains flexible. A memory becomes Master-promoted only when it is:
- active
- `verification_status = verified`
- importance >= 8
- confidence >= 8
- in `experience`, `core` or `project`
- explicitly approved

## Security
All new governance tables have RLS enabled and direct `anon` / `authenticated` table access revoked. Runtime access is intended through the existing controlled service boundary. New v4.1 RPCs are revoked from `PUBLIC`, `anon` and `authenticated`, and granted to `service_role` only.

## Compatibility rule
Root Before Flower: v4.1 is additive. Existing v3 services remain available and unchanged unless future evidence proves a breaking migration is necessary.

## Verification completed
- `service_xiaoe_screening()` returns v4.1.0 active state.
- `service_xiaoe_bootstrap_v41('xiaoe_core_v2','小E上线')` successfully loads verified v3 memories with no conflicts.
- High-risk Policy Gate correctly rejects when `user_approved=false`.
- High-risk Policy Gate allows when environment, impact and approval checks are present.
- Existing 8 verified memories remained intact after migration.
