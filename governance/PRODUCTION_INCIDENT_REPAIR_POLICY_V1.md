# Production Incident Repair Policy V1

Status: ACTIVE / MANDATORY GATE
Owner: Eric Chaow
Applies to: all commercial Production incidents managed by XiaoE / GPT, including `evo_voucher_production`

## Core principle

When a live commercial Production system has a problem, XiaoE / GPT must prioritize **stability, evidence, minimal change, and reversibility** over speed, cleanup, refactoring, or architectural improvement.

The default incident sequence is:

> Stabilize → Gather evidence → Isolate the fault → Make the smallest safe repair → Verify the original issue → Run regression checks → Close the incident.

## Mandatory pre-repair read gate

Before **every** Production incident repair, XiaoE / GPT must first read this policy from the canonical XiaoE Core repository and confirm that it is operating under this policy.

If this policy has not been read in the current incident workflow, Production repair changes must not begin.

## Required incident workflow

Before modifying Production, XiaoE / GPT must:

1. Resolve and lock the exact Production project using the canonical project registry.
2. Read the current Production baseline and relevant code/configuration before changing anything.
3. Define the incident symptom in one clear sentence.
4. Gather available evidence such as logs, failing routes, screenshots, recent commits, database state, Edge Function behavior, or reproducible steps.
5. Identify the smallest plausible fault domain.
6. Establish a rollback point / checkpoint when applicable.
7. Propose the smallest repair that addresses the evidence-backed fault.
8. Avoid touching unrelated code, configuration, schema, styling, or features.
9. Verify the original incident symptom after the repair.
10. Run regression checks on adjacent critical Production behavior before closing.

## Minimal-change rule

Production incident repair must be **surgical**.

XiaoE / GPT must not:

- refactor unrelated code during an incident
- rename or reorganize files merely for cleanliness
- upgrade dependencies unless the dependency itself is the confirmed fault
- redesign architecture while fixing an outage
- change multiple unrelated components at once
- replace working Production code just because Stage or another project looks cleaner
- perform broad search-and-replace without evidence that all matches are part of the same fault
- delete Production-only behavior because it is absent elsewhere

If multiple changes are genuinely required, they must be separated into explicit repair units and verified incrementally.

## No-guess rule

Production must never be repaired by speculative editing.

If the cause is uncertain, XiaoE / GPT must continue diagnosis instead of making broad changes.

A repair may proceed only when there is enough evidence to state:

- what is broken
- where the likely fault is
- why the proposed change is expected to fix it
- what unrelated behavior must remain unchanged

If those points cannot be stated, the next action should be diagnostic, not a Production write.

## Protect existing Production behavior

A repair is successful only if the original issue is fixed **without introducing unrelated regressions**.

For EVO Voucher Production, preserve existing behavior including when applicable:

- theme / styling / branding / layout
- voucher rendering
- QR code generation and QR visibility
- customer name display
- partner name display
- voucher ownership / recipient identity
- issue / claim / redeem flows
- routing / navigation
- authentication / login
- database compatibility
- Edge Function behavior
- Production-only features
- Production environment configuration

Regressions such as theme distortion, QR code disappearance, missing identity fields, broken redemption, broken routes, or loss of existing Production-only behavior are incident-repair failures unless the owner explicitly approved that exact change.

## One-problem-at-a-time rule

During an active Production incident, XiaoE / GPT must not use the incident as an opportunity to fix unrelated defects or add features.

Unrelated findings should be recorded separately for later work.

The incident closes only when:

1. the original reported problem is fixed or safely mitigated;
2. critical regression checks pass;
3. no new known Production regression was introduced by the repair;
4. the final changed scope is documented.

## Rollback-first rule

If a new repair introduces a broader regression, prefer restoring the last known-good Production baseline before stacking additional speculative fixes.

Do not repeatedly patch on top of an unstable repair unless evidence shows rollback is unsafe or impossible.

## Forbidden operations during Production incident repair

The following are forbidden by default:

- blind broad edits
- unrelated refactoring
- full-repository overwrite
- copying Stage wholesale into Production
- force push
- destructive database changes without explicit owner approval and rollback planning
- changing secrets or credentials without evidence they are part of the incident
- deleting data to make an error disappear
- declaring success because one symptom disappeared while critical Production regressions remain unchecked

## Interpretation rule for XiaoE / GPT

When the owner says phrases such as "Production 出问题", "EVO Voucher 坏了", "帮我修线上", "QR 不见了", "theme 走样", "redeem 不能用", or similar, interpret the request as:

> Read this policy first, lock the correct Production project, diagnose with evidence, make the smallest reversible repair, verify the original problem, and run critical Production regressions before closing.

Do not interpret an incident as authorization to redesign, clean up, refactor, or broadly synchronize Production with Stage.

## Source of truth

Canonical project registry: `registry/PROJECT_REGISTRY.json`
Authorization registry: `registry/RESOURCE_AUTH_REGISTRY.json`
Voucher Production baseline: `projects/voucher/VOUCHER_PRODUCTION_FROZEN_BASELINE_V1.md`
Stage → Production policy: `governance/VOUCHER_STAGE_TO_PRODUCTION_PROMOTION_POLICY_V1.md`

If project identity or Production baseline changes, update the relevant source of truth before incident work continues.
