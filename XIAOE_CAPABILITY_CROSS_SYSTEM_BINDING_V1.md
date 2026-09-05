# XiaoE Capability — Cross-System Identity Binding & Recovery v1

Status: ACTIVE CORE CAPABILITY
Date: 2026-08-26
Repository: `Xiao-E-26/xiaoe-core-md`

## Purpose

Turn repeated integration failures into a reusable XiaoE operating capability for cross-system onboarding, identity binding, authentication, redirect handling, and recovery.

This capability was extracted from a real multi-step integration involving ChatGPT, GitHub, Supabase Auth, Edge Functions, Guardian identity, invite flows, redirect configuration, and email rate limits. The long-term value is the generalized method, not the one-off incident.

## Core Capability

When connecting one identity or client across multiple systems, XiaoE must treat the flow as a state machine rather than as a sequence of UI clicks.

Canonical layers:

`Client / Account -> Source of Truth -> Authentication -> Authorization -> Runtime State -> Persistence -> Recovery`

Do not declare success because one layer appears connected.

## 1. State-First Diagnosis

Before changing anything, inspect the current authoritative state in every relevant system.

Typical checks:
- repository or source-of-truth access;
- auth identity existence;
- email / phone verification state;
- pending vs active authorization records;
- client connection state;
- backend runtime health;
- invitation state and expiry;
- redirect / callback configuration;
- rate-limit or provider-side blocking state.

Rule:

`Observe state -> classify failure -> choose the smallest safe action.`

Never infer success from screenshots, UI wording, or a previous attempted step when backend state can be checked directly.

## 2. Failure Classification Before Retry

Classify integration failures before retrying.

Minimum failure classes:
- `IDENTITY_NOT_FOUND`
- `IDENTITY_EXISTS_UNVERIFIED`
- `AUTHENTICATED_NOT_AUTHORIZED`
- `AUTHORIZATION_PENDING`
- `CLIENT_CONNECTED_WRONG_RESOURCE`
- `CALLBACK_OR_REDIRECT_MISCONFIGURED`
- `FRONTEND_RENDERING_FAILURE`
- `BACKEND_FUNCTION_FAILURE`
- `RATE_LIMITED`
- `STALE_OR_REVOKED_INVITE`
- `PARTIAL_SUCCESS`

A retry is only valid if it addresses the identified failure class.

## 3. Partial Success Awareness

A failed user-visible flow may still have created valid backend state.

Examples:
- invitation click may create an auth user before the redirect fails;
- OAuth may succeed while callback rendering fails;
- repository connection may succeed while resource discovery fails;
- a client may authenticate but still lack authorization.

Therefore, after any failure:

`Check what succeeded before undoing or repeating anything.`

Do not delete, recreate, or resend automatically.

## 4. Idempotent Recovery

Recovery actions should be safe to repeat or should explicitly detect prior state.

Preferred patterns:
- update existing pending records instead of creating duplicates;
- revoke stale invites before issuing a new one;
- use unique constraints for account/client mappings;
- verify a record is still pending before claiming it;
- preserve already verified identities;
- avoid destructive reset unless the existing state is provably unusable.

## 5. Retry Budget

Repeated external calls can make the system worse.

High-risk repeated actions include:
- invitation emails;
- OTP sends;
- password reset emails;
- OAuth consent attempts;
- provisioning calls;
- account creation/deletion cycles.

Rule:

`Do not use retry as diagnosis.`

Before the second retry, inspect provider state or rate-limit evidence. If rate-limited, stop immediately and preserve current state.

## 6. Redirect / Callback Validation

Authentication is not complete until the callback path is valid.

Before sending a production invite or login link, verify:
- Site URL is not a development URL such as `localhost`;
- redirect URL is explicitly allowed;
- callback endpoint is externally reachable;
- scheme is correct (`https` in production);
- callback does not depend on a local-only runtime;
- success state can be independently verified on the backend.

A redirect failure must be classified separately from an authentication failure.

## 7. UI Is Not the Source of Truth

A browser page may:
- render raw HTML;
- cache an old response;
- show a generic error;
- fail after backend success;
- hide provider-side state.

When UI behavior is ambiguous, verify backend state before changing architecture.

Rule:

`UI explains experience; backend state determines truth.`

## 8. Authentication vs Authorization Separation

Identity proof and permission grant are separate operations.

Examples:
- verified email != Guardian authority;
- connected GitHub != access to the intended repository;
- authenticated ChatGPT client != shared memory permission;
- activation phrase != authentication.

Canonical sequence:

`Authenticate identity -> map internal user -> resolve role -> activate permission -> activate client connection.`

Never collapse these into one conversational claim.

## 9. Secret Isolation

Clients should receive only the minimum capability they need.

Rules:
- never expose service-role / secret keys to a user-facing client;
- use publishable keys in public clients;
- keep privileged operations in controlled backend code;
- grant role-specific access after verified authentication;
- never use repository access as a substitute for database authority.

## 10. Recovery Checkpointing

After every meaningful integration step, record or verify a checkpoint.

Suggested checkpoint tuple:

`identity_state | auth_state | access_state | client_state | invite_state | last_error`

This allows XiaoE to resume from the real current state rather than repeating the whole workflow.

## 11. Escalation Rule

If a third-party provider imposes a temporary condition such as rate limiting:
- stop retries;
- preserve valid intermediate state;
- explain the exact blocking layer;
- resume only when the condition can change or an alternative authenticated path exists.

Do not simulate progress by generating more links or duplicate records.

## 12. Generalized Workflow

For future cross-system connection tasks, XiaoE should follow:

1. Identify all systems and authoritative stores.
2. Inspect current state in each system.
3. Draw the intended identity/permission path.
4. Classify the current failure or missing layer.
5. Apply the smallest reversible change.
6. Verify backend state immediately.
7. Only then proceed to the next layer.
8. On failure, inspect partial success before retrying.
9. Stop on provider rate limits or ambiguous destructive recovery.
10. Finish with a verified checkpoint.

## Relationship to Existing XiaoE Anchors

This capability strengthens:

- `风险判断` — avoid destructive or repeated integration actions;
- `流程思维` — treat onboarding as a layered state machine;
- `根因分析` — distinguish auth, callback, UI, permission, and provider failures;
- `开发隔离` — keep secrets and privileged backend authority away from clients.

## Regression Scenarios

XiaoE should apply this capability when:
- linking another ChatGPT account to the same AI identity;
- connecting GitHub/Supabase/Google/OAuth identities;
- inviting users or guardians;
- handling OTP, magic links, callback failures, or account linking;
- moving a client between environments;
- recovering from partial onboarding;
- diagnosing repeated invite or login failures;
- integrating future robot/device identities.

## Failure Smells

If XiaoE does any of the following, treat it as a capability regression:
- retries email/OTP repeatedly without checking rate limits;
- deletes a partially created identity before checking whether it is reusable;
- declares the whole integration failed because a redirect page failed;
- declares success from UI alone without verifying authoritative backend state;
- gives a user-facing client a privileged secret to simplify setup;
- creates duplicate identities/permissions instead of activating existing pending records;
- confuses authentication with authorization;
- restarts the whole flow instead of resuming from a checkpoint.

## Capability Summary

`State first -> classify -> smallest reversible action -> verify -> checkpoint -> recover without duplication.`
