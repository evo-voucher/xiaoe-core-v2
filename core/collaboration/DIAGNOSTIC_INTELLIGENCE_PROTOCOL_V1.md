# XiaoE Diagnostic Intelligence Protocol v1

Status: ACTIVE
Purpose: Make technical diagnosis faster, more evidence-driven, and less repetitive without over-expanding test scope.

## Core Flow

`Issue -> Evidence Timeline -> Hypothesis Registry -> Fast Root Debug -> Shared Resource Check -> Targeted Repair -> Targeted Verification -> Record Pattern`

This protocol supplements Root Before Flower, Targeted Root Debug, and the Autonomous Test-Repair-First protocol. It does not replace security, rollback, or project-boundary rules.

## 1. Evidence Timeline Engine

For runtime incidents, build the shortest useful time-correlated chain before changing code.

Preferred evidence order:
1. User-visible symptom and timestamp when available.
2. Runtime logs at the same timestamp.
3. Auth / Edge / API / database evidence for the same fault path.
4. Current GitHub source and relevant commit/deployment state.
5. Only then form or rank hypotheses.

Typical timeline:
`Screenshot time -> Edge request -> Auth/API event -> deployment/commit -> source behavior`

Rules:
- Convert timezones explicitly when correlating evidence.
- Do not treat a nearby event as causal unless the path and timing support it.
- UI state proves only what the UI believes; backend/runtime state is authoritative for auth, permissions, transactions, and data integrity.

## 2. Hypothesis Registry

Maintain a small working set of hypotheses for the active fault.

Each hypothesis must be one of:
- `unresolved`
- `supported`
- `confirmed`
- `rejected`

Rules:
- Do not keep repairing around a rejected hypothesis.
- Promote a hypothesis only when new evidence supports it.
- When one hypothesis is rejected, move to the next highest-evidence explanation instead of restarting the whole system.
- Same repair path failing twice triggers architecture/root reassessment.

## 3. Shared Resource Detector

Before fixing repeated or cross-module failures, ask whether multiple components share the same underlying resource.

Check especially for:
- Auth/session storage keys
- Supabase clients
- refresh tokens
- shared RPCs / Edge Functions
- common configuration
- caches/service workers
- shared tables/read models
- tenant/realm state

Question to ask internally:
> Are multiple modules independently manipulating one shared resource that should have a single owner or coordinated lifecycle?

If yes, prefer fixing ownership/lifecycle at the shared layer rather than patching each caller.

## 4. Runtime Truth Over UI Truth

Never use a green UI label, cached local state, or visible login status as proof of backend truth.

For high-impact state, verify the owning system:
- Auth state -> Auth/session evidence
- Permission state -> RLS/realm/authorization evidence
- Redeem state -> canonical transaction/redemption record
- Allocation state -> canonical allocation ledger/RPC result
- Deployment state -> GitHub Pages/CI/deployment evidence

## 5. Runtime Surface Trace

When source appears correct but the observed runtime or output is still wrong, locate the **first verified divergence** between the expected execution path and the actual one.

Compact diagnostic form:

`Expected Path -> First Divergence -> Executing Surface -> Targeted Repair -> Exact-Path Retest`

Use Behavior Logic's existing Asset Delivery + Cache Coherency principles when the divergence is in deployment, loader, asset version, cache, or executed resource identity. Diagnostic Intelligence owns the **localization of the divergence**, not a duplicate delivery/cache rule set.

The executing surface may be a loader, browser/device runtime, computed CSS, generated/exported representation, service worker/local state, or another evidence-backed transformation layer.

This remains adaptive rather than checklist-driven: preserve already-verified surfaces, inspect only the smallest relevant surface, and widen only when evidence requires it.

## 6. Failure Signature -> Diagnostic Path

When a failure signature repeats, reuse the proven diagnostic path rather than rediscovering from zero.

Example:
`Edge 401`
-> correlate same-second Auth log
-> if `refresh_token_not_found` / `session_not_found`
-> inspect session lifecycle, concurrent clients, refresh race, stale local session
-> do NOT weaken `verify_jwt`
-> do NOT start with RLS changes
-> repair session ownership/recovery
-> targeted auth-path verification

Patterns are diagnostic accelerators, not automatic conclusions. Current evidence always wins.

## 7. Recording Rule

After a fault is proven and repaired, record only durable information:
- failure signature
- confirmed root cause
- owner layer
- diagnostic path
- correct repair class
- anti-patterns to avoid
- verification used

Do not store passwords, tokens, secrets, raw user data, or unverified guesses.

## 8. Stop Condition

Stop expanding diagnosis when:
- the root cause is confirmed or strongly bounded by evidence,
- the responsible layer is repaired,
- the affected path passes targeted verification,
- and no escalation trigger is present.

Do not run full regression merely because more tests exist.
