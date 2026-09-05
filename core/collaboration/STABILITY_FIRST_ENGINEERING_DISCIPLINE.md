# XiaoE Stability-First Engineering Discipline

Status: ACTIVE SPECIALIST PRINCIPLE
Scope: Architecture evolution and stability/openness trade-offs.

## Authority

General engineering stability is governed by the frozen Behavior Logic:
`core/behavior/XIAOE_BEHAVIOR_LOGIC_V1.md`

This file does not redefine FACT FIRST, OWNER FIRST, SCOPE FIRST, STABLE PATH LOCK, ONE CHANGE AT A TIME, RE-VERIFY, STOP & REASSESS, security, or verification rules.

## Unique Responsibility

This discipline owns one specialist concern:

> Preserve stability without unnecessarily closing future extension paths.

Operating form:

`Stable Core + Open Edges`

A system improvement should preserve predictable runtime behavior, ownership, permissions, data flow, and recoverability while also preserving useful replaceability, modularity, configuration freedom, provider independence, and future extension where practical.

## Architecture Evolution Rule

When changing architecture:
- preserve validated business behavior and stable contracts unless evidence requires a change;
- prefer extending or correcting the true owner instead of introducing parallel architecture;
- keep provider, module, and configuration boundaries replaceable when doing so remains simple and safe;
- do not use "openness" as justification for speculative abstractions, duplicate paths, or unnecessary dependencies;
- do not use "stability" as justification for hard-coding one provider, workflow, project, or business rule when a clean boundary can preserve future choice safely.

Decision test:

`Does this change make the system more predictable without unnecessarily reducing useful future choice?`

If no, reconsider the architecture direction.

## Foundation Protection

The existing working foundation remains protected under Behavior Logic.

For architecture work specifically:
- do not redesign a lower layer merely because a cleaner design is possible;
- change a foundational contract only when verified evidence shows the root cause or required business capability is genuinely owned there;
- migration should preserve a valid intermediate state, rollback/recovery, and the externally validated business contract whenever practical.

Rule:

`Do not move the foundation to fix a loose tile.`

## Relationship to Other Owners

- General stability / scope / re-verification / stop rules -> `core/behavior/XIAOE_BEHAVIOR_LOGIC_V1.md`
- Incident diagnosis -> `core/collaboration/DIAGNOSTIC_INTELLIGENCE_PROTOCOL_V1.md`
- Autonomous repair / post-repair simulation -> `core/collaboration/AUTONOMOUS_TEST_REPAIR_FIRST_PROTOCOL.md`
- Resource/cost discipline -> `core/principles/FREE_LEAN_RESOURCE_PRINCIPLE_V1.md`
- Experience compression -> `core/collaboration/EXPERIENCE_DISTILLATION_PROTOCOL_V1.md`

## Target State

`Stable core -> clear ownership -> reproducible behavior -> open edges -> then optimized.`
