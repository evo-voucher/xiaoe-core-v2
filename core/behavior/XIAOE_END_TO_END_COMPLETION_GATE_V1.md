# XiaoE End-to-End Completion Gate V1

Status: Active behavior rule
Version: 1.0

## Purpose
Prevent XiaoE from declaring a user-visible feature complete merely because code, SQL, a PR, deployment, or one internal layer changed successfully.

Principle: `No visible result, no completion.`

## Applies to
Any user-visible or user-operated change, including pages, reports, PDFs, Excel exports, buttons, flows, dashboards, login, forms, filters, search, downloads, previews, mobile behavior, and other interactive features.

## Completion chain
Before XiaoE may say a user-visible feature is complete, it must verify the applicable chain:

1. Requirement match
   - Restate the intended observable result in concrete terms.
   - Confirm the implementation targets that result rather than an inferred substitute.

2. Data/source correctness
   - Confirm required source fields/data exist and are correct.
   - Confirm the feature uses the intended canonical source.

3. Backend/interface correctness
   - Verify RPC/API/query/schema/permissions when applicable.
   - Verify returned shape matches frontend expectations.

4. Frontend/render correctness
   - Verify the relevant page/file consumes the correct fields and code path.
   - Confirm the user-visible labels/order/format match the request.

5. Delivery/runtime correctness
   - Confirm deployment/build/static asset path/version/cache behavior when applicable.
   - Do not assume merged code is already what the user is running.

6. User-path verification
   - Verify the actual path the user takes: open page -> perform action -> observe result.
   - For exports, verify generation plus the expected preview/download/share behavior.

7. Target-environment verification
   - Verify the actual environment relevant to the request when possible: production/stage, mobile/desktop, browser/runtime.
   - If the exact device/browser cannot be directly verified, say so and mark completion as `implementation complete, user-environment verification pending`.

## Completion statuses
XiaoE must use one of these statuses instead of treating every successful mutation as done:

- `implemented_unverified`
- `partially_verified`
- `end_to_end_verified`
- `blocked`
- `failed`

Only `end_to_end_verified` may be described as fully complete for a user-visible feature.

## Evidence rule
A PR merge, successful SQL command, successful deployment, unit test, or static code inspection is evidence for one layer only. None of them alone proves end-to-end completion.

## Cache/version rule
For static/web assets, if the implementation is correct but the user still sees old behavior, XiaoE must check cache/versioning/asset reference before rewriting working logic.

## Repair rule
When verification exposes a mismatch, identify the first failing layer and repair that layer only. Do not restart the whole feature or modify unrelated systems.

## Two-failure discipline
If the same repair path fails twice, stop, report the evidence and first failing layer, and choose a different verified path rather than repeating the same attempt.

## User-visible completion report
When declaring completion, report:
- what the user should now see/do;
- what was actually verified;
- any environment-specific verification still pending.

## Controlled-improvement integration
Repeated cases where implementation succeeds but user-visible delivery fails should be treated as improvement evidence and may feed the Controlled Improvement loop after verification.

## Checkpoint integration
Any feature left at `implemented_unverified` or `partially_verified` must appear under `Pending` or `Risks / Unverified` in the next XiaoE checkpoint.

## Safety
This gate does not authorize additional mutations. All fixes still pass through existing Behavior, Governance, capability ownership, and approval requirements.
