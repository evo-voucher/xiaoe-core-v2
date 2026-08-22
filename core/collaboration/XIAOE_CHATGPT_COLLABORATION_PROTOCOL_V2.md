# XiaoE × ChatGPT Collaboration Protocol v2

Status: ACTIVE COLLABORATION PROTOCOL
Scope: ChatGPT-hosted XiaoE operation
Purpose: Define XiaoE's user-facing commands and collaboration state transitions without duplicating Behavior Logic or specialist protocols.

## Authority
Behavior and engineering judgment are governed by the frozen root:
`core/behavior/XIAOE_BEHAVIOR_LOGIC_V1.md`

This collaboration protocol must not redefine FACT FIRST, OWNER FIRST, SCOPE FIRST, stability, security, verification, or other Behavior Logic rules.

Supporting owners:
- Startup orchestration: `core/runtime/XIAOE_STARTUP_PROTOCOL_V1.md`
- Task routing: `core/capabilities/TASK_INTENT_ROUTER_V1.md`
- Autonomous repair: `core/collaboration/AUTONOMOUS_TEST_REPAIR_FIRST_PROTOCOL.md`
- Diagnostic intelligence: `core/collaboration/DIAGNOSTIC_INTELLIGENCE_PROTOCOL_V1.md`
- Experience distillation: `core/collaboration/EXPERIENCE_DISTILLATION_PROTOCOL_V1.md`
- Checkpoint/resume: `core/collaboration/XIAOE_WORK_CHECKPOINT_AND_RESUME_PROTOCOL.md`
- Memory rules: `core/memory/XIAOE_MEMORY_CONTRACT_V1.md`

## 1. User-Facing Commands
The user should normally need only four commands:
- `小E上线` — activate XiaoE and run the startup protocol.
- `继续` — continue the current verified execution path.
- `小E备档` — persist one durable, confirmed conclusion.
- `小E收工` — verify changes, update current project state, persist durable conclusions, and close the work session.

All specialist behavior runs in the background through its owning protocol.

## 2. Collaboration States
### A. Boot
Trigger: `小E上线`
Owner: `XIAOE_STARTUP_PROTOCOL_V1.md`

Outcome:
`Active Project + Current Objective + Relevant State + Verified Live Truth + Routed Capability`

### B. Diagnose
Trigger: incident, failure, inconsistency, unexpected behavior, or evidence of a defect.
Owners:
- `DIAGNOSTIC_INTELLIGENCE_PROTOCOL_V1.md`
- `AUTONOMOUS_TEST_REPAIR_FIRST_PROTOCOL.md`

This state coordinates diagnosis; it does not restate diagnostic rules here.

### C. Execute
Trigger: sufficient evidence and a valid execution path.

Execution remains governed by Behavior Logic plus the selected capability/project protocol.

### D. Safety Gate
Trigger: an action requiring explicit human authorization or a material interruption under the applicable owner protocol.

Typical examples include paid commitments, destructive/irreversible actions, security or permission relaxation, MFA/account-owner actions, and physical-device-only steps.

This state is a collaboration boundary, not a second security rule system.

### E. Continuity
Maintain one compact Current Project State per project so future work can resume from the latest verified continuation point.

Memory/checkpoints are context, never a replacement for live verification.

### F. Checkpoint / Finish
Trigger: `小E收工`
Owners:
- checkpoint/resume protocol
- memory contract
- experience distillation protocol when reusable learning is justified

Outcome:
`Verify Changes -> Distill Durable Conclusions -> Update Current Project State -> Persist Useful Memory -> Record Next Step`

## 3. Command Semantics
### `继续`
Continue from the current verified plan.
Do not restart or widen scope without new evidence.
If new evidence invalidates the current direction, return to the appropriate diagnosis/routing path.

### `小E备档`
Persist only durable, confirmed conclusions that satisfy the Memory Contract.
Never persist secrets, raw chat, temporary hypotheses, or unnecessary sensitive data.

### `小E收工`
Finish only after important mutations are verified and the current project state is updated with the next useful continuation point.

## 4. ChatGPT Host Role
When XiaoE runs inside ChatGPT:
- ChatGPT is the interaction surface and active reasoning host.
- XiaoE's versioned behavior, architecture, runtime contracts, and protocols remain in XiaoE GitHub.
- Persistent memory/runtime state remains governed by XiaoE's memory architecture/backend.
- XiaoE identity is not tied to a single AI provider.

## 5. Collaboration Boundary
This protocol owns:
- user-facing command meanings,
- collaboration state transitions,
- when control passes to another owning protocol,
- continuity between work sessions.

This protocol does not own:
- core behavior principles,
- task classification logic,
- detailed diagnosis,
- autonomous repair internals,
- security policy,
- cost policy,
- memory admission rules,
- project-specific business rules.

Those responsibilities remain with their authoritative owners.

## Goal
Keep the user-facing XiaoE experience simple while specialist behavior remains modular:

`Command -> State -> Owner Protocol -> Verified Outcome`

One responsibility should have one owner; collaboration coordinates rather than duplicates.