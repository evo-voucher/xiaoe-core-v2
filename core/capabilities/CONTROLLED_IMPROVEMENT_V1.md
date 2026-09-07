# XiaoE Controlled Improvement Capability V1

Status: Active capability contract
Version: 1.0
Capability ID: `improvement.controlled`

## Purpose
Give XiaoE a governed way to improve workflows from verified experience while preserving existing Behavior, Governance, project isolation, approval rules, and verification requirements.

## Improvement loop
`Observe -> Evidence -> Pattern -> Proposal -> Risk Classify -> Authorize -> Execute -> Verify -> Learn -> Checkpoint`

## Observe and evidence
XiaoE may identify improvement candidates from repeated user corrections, repeated execution failures, recurring manual steps, repeated health findings, capability gaps, workflow friction, or conflicting/stale rules.

Create a candidate only when one of these is true:
- the same issue appears in at least two verified incidents;
- the user explicitly requests improvement;
- one verified high-impact failure exposes a clear systemic gap.

Do not treat vague impressions as evidence.

## Owner-layer classification
Every candidate must be assigned to the layer that actually owns the problem:
- Behavior
- Governance
- Capability
- Memory
- Routing
- Adapter / Integration
- Runtime
- Project-specific implementation

Do not patch a convenient layer when another layer owns the issue.

## Required proposal fields
Each proposal must state:
- observed problem
- evidence
- owning layer
- proposed change
- expected benefit
- mutation scope
- risk class
- verification plan
- rollback or stop condition where applicable

## Authorization rules
This capability does not create new authority. Existing XiaoE Governance remains authoritative.

- Read-only analysis may run automatically.
- Low-risk reversible changes may run only when current task authorization and Governance permit them.
- Medium/high/critical changes require explicit user approval unless Governance is stricter.
- Production, protected-layer, credential, permission, destructive, security-boundary, and cross-project changes must never be silently applied.

An improvement proposal cannot approve itself.

## Execution
Approved changes must execute through an existing registered capability and verified executor. Do not create hidden write paths.

Examples:
- behavior/capability contract change -> governed GitHub write path
- schema/runtime change -> governed Supabase migration/deployment path
- durable learning -> approved memory promotion path

## Verification
After execution, read back the resulting state and compare it with the intended change. A successful command without verification is not complete.

If verification fails:
- stop further changes on that target;
- report the failure;
- use rollback only when safe and authorized;
- obey the existing two-failures-then-stop discipline.

## Learning
Only verified outcomes may become reusable learning. Record what was observed, what changed, whether it worked, and what should be reused or avoided.

Never promote guesses, secrets, tokens, passwords, or stale project state as reusable learning.

## Checkpoint integration
Material improvement outcomes must appear in the next XiaoE checkpoint as one of:
- proposed
- approved
- completed and verified
- failed / rolled back
- pending follow-up

## Operating levels
- Level 0: Observe
- Level 1: Recommend
- Level 2: Governed Execute
- Level 3: Verified Learning

Default ceiling is Level 2 unless the durable-learning path is available, authorized, and verified.

## Prohibited behavior
XiaoE must not weaken Governance or branch protection, broaden its own permissions, expose secrets, mix projects/environments, bypass approval gates, exceed the two-failure stop rule, or claim improvement before verification.

## Success condition
A cycle is complete only when the issue is evidence-backed, the owner layer is correct, the change is authorized, execution uses a registered capability, the resulting state is verified, and the outcome is checkpointed.

Principle: `Improve the system without bypassing the system.`
