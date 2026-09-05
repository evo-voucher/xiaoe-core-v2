# XiaoE Unified Router Pipeline v1

Status: ACTIVE CAPABILITY ROUTER

## Purpose

Provide one canonical routing pipeline that resolves project identity, task intent, ownership, capability, executor, and verification before execution.

## Canonical Pipeline

`Project Resolution -> Task Intent -> Owner/Boundary -> Capability -> Executor -> Verify -> Reclassify if needed`

## Project Resolution

Before reading project-specific files, returning project URLs, or mutating state, identify the correct project through the canonical project registry. Never guess when multiple candidate projects exist.

## Task Intent

Classify the intended outcome rather than surface wording. Typical classes include incident/fault, small direct change, feature/product flow, architecture/system design, and security/auth/persistent-data work.

## Owner and Boundary

Identify the smallest authoritative owning layer. Do not fix one layer by casually changing another. Preserve stable unaffected layers.

## Capability Selection

Select the fewest existing capabilities needed. Do not create duplicate policy systems or parallel routers.

## Executor Selection

Route to the appropriate execution surface such as GitHub, Supabase, local/runtime adapter, or external model/tool adapter. Authentication and authorization remain separate concerns.

## Verification

Every material execution must have a verification step appropriate to its risk. High-risk or irreversible work requires stronger checks and explicit approval gates.

## Reclassification

If new evidence changes project identity, root cause, scope, risk, uncertainty, dependency, or ownership, reclassify the task and route again rather than continuing on stale assumptions.

## Operating Rule

`Resolve the right project -> identify the real problem class -> route to the smallest owning capability -> choose the correct executor -> verify -> reclassify when evidence changes.`
