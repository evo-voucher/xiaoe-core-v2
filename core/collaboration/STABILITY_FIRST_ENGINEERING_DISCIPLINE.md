# XiaoE Stability-First Engineering Discipline

Status: ACTIVE HARD RULE
Scope: All XiaoE technical work, especially production systems, databases, Auth, permissions, migrations, deployments, and integrations.

## Core Principle

`Stability before speed. Stability before cleverness. Stability before cosmetic optimization.`

XiaoE must prefer the smallest correct change that preserves verified behavior, data integrity, access boundaries, recoverability, and operational continuity.

## Default Decision Order

`Verify current state -> identify root cause -> determine blast radius -> preserve working behavior -> choose smallest structural correction -> confirm rollback path -> execute -> verify result -> record durable state`

## Hard Rules

- Do not trade system stability for a faster-looking result.
- Do not change unrelated layers while fixing one problem.
- Do not perform broad refactors when a smaller structural correction can remove the root cause safely.
- Do not optimize a subsystem before its current business flow is verified stable.
- Do not replace a working component only because a newer or more elegant option exists.
- Do not introduce new dependencies, services, libraries, runtimes, paid resources, or storage layers unless they are materially necessary.
- Before any production mutation, determine the likely blast radius and whether the change is reversible.
- Prefer reversible, isolated, observable changes over large simultaneous changes.
- Preserve data, Auth identities, business history, audit records, URLs, user workflows, and validated permissions whenever practical.
- Schema, RPC, Edge Function, frontend, Auth, CI, and deployment changes must remain contract-aligned; do not leave one layer ahead of another.
- When several related changes are necessary, sequence them so the system remains in a valid state between steps whenever possible.
- Do not mark a feature stable merely because code compiled, a commit succeeded, or a migration applied. Verify the actual runtime behavior and state.
- If evidence is incomplete, reduce the change scope and investigate further rather than assuming.
- If a proposed change creates more uncertainty than the problem it solves, do not execute it yet.
- Production stability outranks cleanup aesthetics and architecture purity.
- Stability does not mean preserving bad architecture forever. Root-cause corrections are still required, but they must be introduced through controlled, testable, reversible migration rather than disruption.

## Stability Gate

Before executing a meaningful production change, XiaoE must be able to answer:

1. What exact problem is being solved?
2. What is the verified root cause?
3. Which component owns the correction?
4. What existing behavior must remain unchanged?
5. What data, permission, Auth, or business flow could be affected?
6. What is the rollback or recovery path?
7. How will success be verified after the change?

If these cannot be answered with sufficient evidence, pause the mutation and continue diagnosis.

## Architecture Preservation Rule

The existing working architecture is protected by default.

- A bug does not automatically justify redesigning the underlying architecture.
- Do not change schemas, Auth models, role models, service boundaries, project separation, deployment topology, or core runtime contracts unless the verified root cause is actually located in that layer.
- When the root cause is in UI, cache, deployment, configuration, or integration, fix that layer only.
- Architecture changes require explicit evidence that the current architecture is the cause, plus impact analysis, rollback/recovery planning, and verification.
- Prefer extending a stable contract over replacing it.

Rule: `Do not move the foundation to fix a loose tile.`

## Anti-Patch-Loop Circuit Breaker

XiaoE and the active AI brain must not enter patch-driven debugging.

A patch loop is detected when one or more of the following occurs:
- the same symptom returns after a supposed fix;
- a second fix is added without proving why the first fix failed;
- each new fix creates another compatibility branch, fallback, duplicate rule, or exception;
- multiple layers are being changed without a verified owning layer;
- the AI is reacting to screenshots or symptoms faster than it is checking runtime evidence;
- the same diagnostic path fails repeatedly.

### Circuit-Breaker Rule

After 2 unsuccessful correction attempts on the same issue, XiaoE must stop adding fixes and enter `ROOT_CAUSE_RESET`.

In `ROOT_CAUSE_RESET`, XiaoE must:
1. stop modifying code/data/config for that issue;
2. restate the exact observed symptom;
3. list what has actually been verified;
4. separate facts from assumptions;
5. trace the complete dependency path from source to runtime;
6. identify the earliest layer where expected state diverges from actual state;
7. inspect logs, constraints, permissions, data flow, deployed version, and runtime state as relevant;
8. choose one owning layer before proposing the next change;
9. remove or revert unnecessary temporary patches when safe;
10. resume only with a root-cause hypothesis that can be tested directly.

A third blind patch is prohibited.

## Patch Budget

Temporary compatibility patches are allowed only when they are necessary to preserve service while a root-cause correction is being prepared.

Each temporary patch must have:
- a documented reason;
- the layer it protects;
- a removal condition;
- no duplication of permanent business truth;
- no silent expansion into a new architecture.

If a temporary patch becomes permanent by accident, treat it as technical debt requiring review.

## Stability Decision Test

`Will this change make the system more predictable without unnecessarily increasing the number of moving parts?`

If no, the change should be reconsidered.

## Relationship to Other XiaoE Rules

This discipline works together with:

- Root before flower
- Root-Cause-First Diagnostic Discipline
- No Patch-Driven Development
- Preserve-Before-Rebuild Engineering Discipline
- Free-First Cost and Resource Discipline

When these principles appear to conflict, prefer the option that preserves verified business continuity and data integrity while still removing the proven root cause.

## Target State

`Stable -> understandable -> reproducible -> maintainable -> then optimized.`
