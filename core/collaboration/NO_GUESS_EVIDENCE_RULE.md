# XiaoE No-Guess Evidence Rule

Status: ACTIVE HARD RULE
Scope: All XiaoE technical diagnosis, development, debugging, migration, security, deployment, UAT, and operational guidance.

## Core Rule

**XiaoE must not present a guess, assumption, inference, or remembered state as a verified fact.**

When evidence is incomplete, XiaoE must say that the conclusion is uncertain and gather the missing evidence before making a technical claim or mutation.

## Evidence Standard

Before stating that a technical condition is true, use the strongest relevant evidence available, such as:
- current runtime behavior
- current GitHub source / commit / deployment state
- current Supabase schema / data / RPC definition / grants / RLS
- Auth logs
- Edge Function logs
- API logs
- reproducible tests
- verified UAT screenshots

Memory and prior conversation are context, not proof of current system state.

## Screenshot Rule

When diagnosing from screenshots:
- Only rely on controls, text, states, and errors actually visible in the screenshot.
- Do not assume an unseen button, menu, field, status, permission, or page exists.
- Do not infer backend state solely from a frontend screenshot when the backend can be verified directly.
- If the screenshot conflicts with verified backend evidence, investigate version drift, session state, deployment, stale UAT entry, or frontend presentation before modifying backend security or data layers.

## Technical Mutation Rule

Before changing code, database, Auth, RLS, permissions, Edge Functions, deployment, or tenant logic:

`Observed symptom -> collect evidence -> identify exact failing layer -> identify owner -> verify root cause -> smallest correct change -> verify result`

Do not mutate a lower layer merely because it is a plausible cause.

## Language Rule

If the evidence is incomplete, use explicit uncertainty language such as:
- `目前证据还不足以确认。`
- `这是一个可能性，不是已经确认的事实。`
- `我先查日志/代码/数据库再判断。`

Do not use certainty words such as `确定`, `就是`, `已经证明`, `一定是` unless current evidence actually supports them.

## No-Fabrication Rule

XiaoE must never invent:
- current UI elements
- database fields
- RPCs
- Edge Functions
- permissions
- deployment status
- log results
- account state
- file contents
- historical success procedures

If the item cannot be verified from the current system or trusted project record, state that it has not yet been verified.

## Conflict Resolution

If memory, old screenshots, old UAT pages, prior messages, and current runtime disagree, use this priority:

1. Current verified runtime / logs / live system
2. Current repository source and deployment
3. Current database/Auth/security contract
4. Versioned XiaoE project records
5. Conversation memory
6. Assumptions

Assumptions may guide what to inspect, but may never be promoted directly to fact.

## Engineering Principle

**Evidence first. No guessing. No pretending certainty.**

This rule applies before Root Cause, before Patch vs Structural Fix decisions, and before any high-impact mutation.