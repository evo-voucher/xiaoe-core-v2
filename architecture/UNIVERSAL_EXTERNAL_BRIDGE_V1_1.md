# Universal External Bridge v1.1 — Multi-Service Isolation & Full Revocation

Status: IMPLEMENTATION CANDIDATE
Date: 2026-09-07

## Purpose

Extend v1 so one Universal External Bridge can serve many external projects and many services without cross-project credential leakage.

## Canonical Shape

`XiaoE Core -> Universal External Bridge -> External Project -> Service Bindings`

Example:

- Project A -> GitHub + Supabase
- Project B -> GitHub + Supabase

The bridge is shared. Project identity, credential references, resource targets, approval sessions and audit state are isolated per project.

## Isolation Contract

Every external service lookup MUST be scoped by `project_key` first and `service` second.

A binding contains only opaque references:

`project_key | connection_key | service | credential_ref | resource_ref | state`

Raw secrets are never stored in source code, registry JSON or audit records.

## One-Time Authorization

Each external project is onboarded once per required service. The resulting credential is placed in a protected vault/provider secret store and the bridge keeps only its reference.

The XiaoE architecture itself does not force 3/6/90-day expiry. Provider-side expiry or revocation is handled by re-authorizing that service binding only.

## Owner Approval

Persistent platform authorization and owner repair approval are separate.

Read/health/diagnose may use the standing external connection.
Write/deploy/migrate/delete/destructive repair require an owner-approved action session. The action session is project-scoped and ends after the approved work.

## Full Disconnect / Revoke

When an external project no longer needs XiaoE:

1. Stop all active write sessions for that project.
2. Revoke provider grants/tokens where the provider supports revocation.
3. Delete corresponding secrets from the credential vault.
4. Remove usable service bindings from the bridge registry.
5. Mark the project connection as `revoked`.
6. Keep only non-secret audit/tombstone metadata if required.

After full revoke, XiaoE must not be able to resolve any usable credential for that project.

## Safety Invariants

- One master bridge, not one bridge per project.
- Same-account authorized projects remain on Inner Direct Access.
- External projects alone use the Universal External Bridge.
- Project A can never resolve Project B credential references.
- Approval for Project A never authorizes Project B.
- Revoking Project A does not disconnect Project B.
- Revoked credentials are not retained in project-visible metadata.

## Current Implementation Boundary

`integrations/external_connection_lifecycle.py` implements the registry/lifecycle contract and isolation tests. A production credential vault and live provider revocation adapters are still required before real external secrets are onboarded.
