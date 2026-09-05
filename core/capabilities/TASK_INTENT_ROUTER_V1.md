# XiaoE Task Intent Router v1

Status: ACTIVE CAPABILITY ROUTER
Purpose: Select the smallest useful XiaoE capability set for the active task without turning routing into another large rule system.

## Routing Principle
Route by the user's intended outcome and the authoritative effect of the task, not by surface wording alone.
The router selects existing XiaoE capabilities/protocols; it does not create alternate security, execution, or ownership rules.

## Lightweight Complexity Gate
Before choosing a fast or expanded path, make a low-cost classification using four dimensions:

`Complexity = Scope × Risk × Uncertainty × Dependency`

Use the dimensions as routing signals, not as a numeric scoring system.

- **Scope** — how many files, modules, layers, business flows, or protected invariants may be affected?
- **Risk** — could the task affect Auth, RLS, tenant isolation, persistent data, Production, cost, irreversible state, or a verified stable path?
- **Uncertainty** — is the owner/root cause already clear, or are there competing explanations that require evidence?
- **Dependency** — does the result depend on multiple systems, owners, contracts, runtimes, deployments, or external services?

### Fast Path Eligibility
Use the Small Direct Change path only when all of the following are true:
- scope is narrow,
- risk is low,
- owner is clear,
- uncertainty is low,
- dependencies are limited,
- the change is reversible and independently verifiable.

If any dimension is materially high or unknown, do not assume the task is simple. Expand only enough to resolve the uncertainty and route to the appropriate specialist capability.

Operating rule:

`Surface simplicity is not structural simplicity.`

A task may begin on the fast path, but verified evidence can promote it to a higher-risk or more specialized route at any time.

## Route Map

### Incident / Fault
Use when something that should work is failing or behaving incorrectly.
Primary path:
- `core/collaboration/DIAGNOSTIC_INTELLIGENCE_PROTOCOL_V1.md`
- `core/collaboration/AUTONOMOUS_TEST_REPAIR_FIRST_PROTOCOL.md`
Typical flow:
`Verify -> Evidence -> Root Cause -> Owner -> Smallest Correct Repair -> Test`
Creativity is secondary and activates only when the verified root cause creates a genuine design choice.

### Small Direct Change
Use for narrow, low-risk, clearly owned changes such as presentation text, formatting, or small verified local behavior.
Primary path:
- Behavior Constitution + project protocol
Typical flow:
`Verify Owner/Scope -> Change -> Re-verify`
Do not generate design alternatives unless they materially improve the outcome.

### New Feature / Product Flow
Use when creating new behavior, workflow, reporting, automation, or user-facing capability.
Primary path:
- `core/capabilities/CREATIVE_EXPLORATION_EVALUATION_V1.md`
- project/domain protocol as needed
Typical flow:
`Understand -> Explore -> Evaluate -> Select -> Scope -> Execute -> Verify`

### Architecture / System Design
Use when boundaries, ownership, data model, runtime model, integration model, migration model, or long-term extensibility are the main subject.
Primary path:
- `core/capabilities/CREATIVE_EXPLORATION_EVALUATION_V1.md`
- Behavior Constitution
- relevant architecture/project protocol
Execution starts only after ownership, compatibility/migration impact, rollback, and verification strategy are clear.

### Security / Auth / Permission / Persistent Data
Use when the task can affect identity, RLS, tenant isolation, secrets, authorization, destructive operations, schema, or Production data semantics.
Primary path:
- Security Behavior + Verification Discipline in `core/behavior/XIAOE_BEHAVIOR_LOGIC_V1.md`
- relevant project security/data protocol
Typical flow:
`Verify -> Owner -> Boundary -> Impact -> Recovery -> Change -> Strong Verification`
Creative exploration may assist design, but cannot relax security or evidence requirements.

## Mixed Tasks
If a task spans routes, use the highest authoritative-risk route for execution while allowing lower-risk capabilities during analysis.
Examples:
- UI symptom caused by RLS -> Security/Permission route.
- New dashboard using existing canonical data -> New Feature route.
- Bug that exposes a missing business model -> Incident first, then deliberately transition to Feature/Architecture.

## Transition Rule
A route changes only when new verified evidence changes the task's true owner, effect, scope, risk, uncertainty, or dependency structure.
Do not silently widen the task because an adjacent improvement is attractive.

## Selection Goal
Use the fewest capabilities needed to reach a correct decision and verified outcome.
The router exists to reduce rule load and unnecessary reasoning paths, not to add ceremony.

Target behavior:
`Simple tasks stay fast. Hidden complexity is promoted early. Complex tasks expand only as far as evidence requires.`
