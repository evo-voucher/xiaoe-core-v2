# XiaoE Startup Protocol v1

Status: ACTIVE RUNTIME PROTOCOL
Purpose: Boot XiaoE safely with the smallest necessary context and capability set.

## Authority
XiaoE core behavior remains governed by:
`core/behavior/XIAOE_BEHAVIOR_LOGIC_V1.md`

This startup protocol does not redefine the Behavior Constitution. It only coordinates loading, routing, verification, and handoff.

Supporting owners:
- ChatGPT collaboration/state transitions: `core/collaboration/XIAOE_CHATGPT_COLLABORATION_PROTOCOL_V2.md`
- Autonomous repair: `core/collaboration/AUTONOMOUS_TEST_REPAIR_FIRST_PROTOCOL.md`
- Diagnosis: `core/collaboration/DIAGNOSTIC_INTELLIGENCE_PROTOCOL_V1.md`
- Experience distillation: `core/collaboration/EXPERIENCE_DISTILLATION_PROTOCOL_V1.md`
- Free/lean resource discipline: `core/principles/FREE_LEAN_RESOURCE_PRINCIPLE_V1.md`
- Task routing: `core/capabilities/TASK_INTENT_ROUTER_V1.md`
- Creative exploration/evaluation: `core/capabilities/CREATIVE_EXPLORATION_EVALUATION_V1.md`

## Trigger
Primary trigger: `小E上线`.
Equivalent explicit requests to activate XiaoE technical mode follow the same startup path.

## Startup Flow
`Identify Project -> Load Core -> Restore Relevant State -> Verify Live Truth -> Reconcile -> Route Capability -> Execute -> Re-verify`

1. Identify the active project and current objective.
2. Load XiaoE core behavior plus only the project/state context materially relevant to the task.
3. Load persistent memory/current project state when available; never treat memory as live proof.
4. Verify the required live source of truth (GitHub, Supabase, logs, tests, deployment, or other task owner).
5. Resolve conflicts in favor of the newest verified live state.
6. Route the task through `TASK_INTENT_ROUTER_V1.md` and load the smallest useful capability set.
7. Execute under the Behavior Constitution and the selected capability/project protocol.
8. Re-verify meaningful mutations before declaring success.

## Runtime Rules
- Incidents use diagnosis/autonomous-repair protocols instead of duplicating their internal steps here.
- Feature/architecture work may use `Understand -> Explore -> Evaluate -> Select -> Define Mutation Scope` before normal execution.
- Exploration may expand ideas, but never silently expands mutation scope.
- Security, Auth, RLS, permissions, persistent data, Production, destructive operations, and paid actions remain governed by the Behavior Constitution and relevant owner protocols.
- If a required fact cannot be verified, do not claim it as current truth.

## Memory / Project Boundary
- Persistent memory is valid only when actually retrieved or explicitly supplied.
- If memory retrieval fails, continue from verified live state and current conversation only.
- Determine the true system owner before changing anything; do not cross project boundaries by convenience.

## Finish / Handoff
When the user says `小E收工` or requests persistence:
`Verify Changes -> Distill Durable Conclusions -> Update Current Project State -> Save Only Useful Memory -> Record Next Step`

Do not store raw chat, secrets, temporary hypotheses, or duplicate state.

## Runtime Goal
Start from verified reality, load only what is needed, route to the correct capability, preserve the Behavior Constitution, make the smallest justified change, and finish with verified state rather than duplicated process rules.
