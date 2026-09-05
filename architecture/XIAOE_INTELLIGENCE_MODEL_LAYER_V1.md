# XIAOE Intelligence / Model Layer V1

Status: architecture-only upgrade
Scope: add a seventh logical layer without changing existing production runtime, Supabase, bridges, vouchers, or secrets.

## Purpose

The Intelligence / Model Layer makes XiaoE model-aware and model-manageable while keeping the existing six-layer architecture intact.

For the current phase, ChatGPT remains the external reasoning engine. XiaoE defines how context is prepared, how reasoning is requested, how outputs are checked, and how model access can later be replaced by an API or self-hosted model.

## Seven-layer position

1. UI — how people use XiaoE
2. Runtime — how tasks run
3. Behavior — how XiaoE should behave
4. Connection — how XiaoE reaches external systems
5. Data — how information is stored and reacts
6. Security — who can do what
7. Intelligence / Model — how reasoning is prepared, routed, executed, checked, and traced

Logical flow:

User
-> UI
-> Runtime / Orchestrator
-> Behavior / Rules
-> Intelligence / Model
-> Connection / Tools
-> Data / Memory
-> Security across all layers

## Components

### Model Interface
Function: defines one stable contract between XiaoE and any reasoning model.
Current mode: ChatGPT-hosted reasoning.
Future mode: OpenAI API, Claude, DeepSeek, or self-hosted model adapters.

### Model Router
Function: decides which reasoning backend should handle a task.
Current mode: fixed route to ChatGPT session reasoning.
Future mode: route by task type, cost, latency, privacy, or availability.

### Context Builder
Function: assembles the minimum correct context before reasoning.
Inputs may include project scope, owner, checkpoint, behavior rules, retrieved memory, current task, and tool state.
Rule: do not inject unrelated project context.

### Retrieval / RAG Interface
Function: retrieves relevant durable information instead of relying on model guesswork.
Sources may include repository files, Supabase records, checkpoints, logs, and approved external resources.

### Planner
Function: converts a goal into an ordered execution plan before tools are called.
Rule: planning does not grant permission; Runtime and Security still control execution.

### Tool-Calling Intent
Function: lets the intelligence layer express an intent to use a tool, such as GitHub read, Supabase health check, or bridge call.
Rule: the model requests; Runtime validates and executes.

### Response Validator
Function: checks model output against Behavior, scope, security, and expected format before it is accepted.
Examples: block unsupported production write, reject cross-project drift, require explicit uncertainty when facts are unverified.

### Fallback Policy
Function: defines what happens when the reasoning backend fails.
Current mode: stop safely and report failure; do not silently switch behavior.
Future mode: allow approved secondary model fallback.
Existing XiaoE rule remains: repeated failure must not become infinite retry.

### Model Trace
Function: records model-facing metadata needed for debugging and audit.
Suggested fields: task id, model route, context sources, tool intents, validation result, error class, timestamp.
Rule: never log raw secrets, PATs, service-role keys, or sensitive credentials.

### Eval Gate
Function: tests whether a model-layer change improves XiaoE without breaking established behavior.
Minimum checks: scope isolation, checkpoint continuity, tool-call discipline, no unauthorized write, failure-stop behavior, answer consistency.

### Cost / Token Guard
Function: limits unnecessary model usage when an API-backed model is introduced later.
Current ChatGPT-hosted mode: architecture placeholder only; no API billing is introduced by this file.

## Current operating mode: ChatGPT-hosted intelligence

XiaoE does not yet own a direct model API connection in this version.

Current pattern:

XiaoE six-layer system
-> Context Builder
-> ChatGPT reasoning in the active chat environment
-> Response Validator
-> Runtime / tools

This gives XiaoE a formal intelligence-management layer without requiring OpenAI API subscription or a new secret.

## Boundary rules

1. Intelligence does not bypass Security.
2. Intelligence does not directly write Production.
3. Intelligence does not directly own credentials.
4. Intelligence may propose tool actions; Runtime decides execution.
5. Behavior rules remain authoritative over model suggestions.
6. Project scope must be resolved before retrieval or tool use.
7. Existing six-layer interfaces remain backward compatible.
8. No existing Production, Supabase schema, bridge, secret, or voucher workflow is modified by this V1 architecture upgrade.

## Upgrade stages

### Stage 1 — Architecture only
Add this seventh-layer contract. Use ChatGPT as the external reasoning engine. No API key required.

### Stage 2 — Adapter implementation
Create a model adapter interface and a ChatGPT/API-compatible execution boundary.

### Stage 3 — Model routing
Add optional OpenAI / Claude / DeepSeek / self-hosted adapters.

### Stage 4 — Evaluation and fallback
Add model quality tests, fallback policies, tracing, and cost controls.

### Stage 5 — Independent runtime
Allow XiaoE to receive requests and invoke an approved model endpoint outside the ChatGPT app while preserving the same Behavior, Runtime, Data, Connection, and Security layers.

## Definition of done for V1

V1 is complete when:
- the seventh layer is formally documented;
- current ChatGPT-hosted reasoning is explicitly recognized as the active intelligence backend;
- no OpenAI API key is required;
- no existing production behavior changes;
- future model adapters can be added without redesigning the six existing layers.
