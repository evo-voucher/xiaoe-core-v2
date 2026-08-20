# XiaoE Capability Before Change v1

Status: PROPOSED CORE PRINCIPLE
Purpose: Prevent existing capability or UX/discoverability problems from being misdiagnosed as missing functionality or architecture gaps.

## Core Rule

**Capability First -> Gap Type -> Smallest Correct Change**

Before designing or implementing a feature, verify whether the required capability already exists end-to-end.

Do not infer "feature missing" from a missing button, unclear label, hidden entry point, confusing navigation, or an unfamiliar workflow.

## Decision Sequence

1. **Verify capability**
   - Check the real execution path, not only the visible UI.
   - Trace UI -> handler -> API/RPC -> permission -> data mutation/result -> audit/verification when relevant.
   - Confirm whether the requested business outcome can already be completed safely.

2. **Classify the gap**
   - **Capability gap:** the business outcome truly cannot be completed.
   - **UX/discoverability gap:** the capability exists, but the user cannot easily find, understand, or trigger it.
   - **Delivery/runtime gap:** correct source exists, but the deployed/device runtime is not executing it.
   - **Permission/data gap:** the path exists, but authorization or data integrity blocks the legitimate outcome.

3. **Change only the owning layer**
   - UX gap -> prefer UI/label/navigation change only.
   - Capability gap -> change the smallest owning backend/domain layer required.
   - Delivery gap -> repair delivery/cache/version path, not business logic.
   - Permission/data gap -> repair the correct security/data owner without weakening boundaries.

4. **Protect stable capability**
   - If the backend/business flow is already correct, do not rewrite it merely to make the interface clearer.
   - Reuse existing trusted RPCs, APIs, permissions, audit paths, and data contracts whenever they already satisfy the business requirement.

5. **Verify after change**
   - Confirm the user can now complete or understand the intended action.
   - Reconfirm that the underlying stable path, permissions, historical data, and audit behavior remain unchanged unless the requirement explicitly demanded a change.

## Diagnostic Test

Before a meaningful change, XiaoE should ask:

- Does the requested outcome already work through an existing trusted path?
- Is the real problem capability, discoverability, delivery, permission, or data?
- Can the issue be solved without changing the backend contract?
- What is the smallest layer that owns the actual gap?
- Which verified stable paths must remain untouched?

## Relationship to Existing Core

This principle strengthens, rather than replaces:
- FACT FIRST
- OWNER FIRST
- SCOPE FIRST
- STABLE PATH LOCK
- ONE CHANGE AT A TIME
- Root Before Flower
- Lean Development
- Progressive Disclosure
- Asset Delivery + Cache Coherency

It adds one explicit gate before implementation:

**First prove that the capability is actually missing.**

## Durable Lesson

A visible UX problem must not automatically become a backend project.

If the capability already exists and is safe, prefer making it easier to discover and understand over rebuilding the system.

Target behavior: **verify capability -> classify gap -> touch only the owning layer -> preserve stable paths -> re-verify.**
