# Universal External Bridge v1

Status: PROPOSED IMPLEMENTATION
Date: 2026-09-07

## Goal

Give XiaoE one clean access model for project work:

- Projects already inside the currently authorized account use direct inner access.
- Projects owned by another account or external customer use one Universal External Bridge.
- External onboarding is one-time per project/account connection.
- Stored external credentials are reused for future read/health/diagnose/manage operations.
- No repeated bridge creation per project.
- Write or destructive work requires explicit owner approval at execution time.

## Routing Model

`Project Request -> Project Access Router`

- `inner` -> existing direct connector / installed-account access
- `external` -> Universal External Bridge -> service adapter -> target project

The bridge is not the permission model. The bridge is the transport/access path.
Permission is evaluated separately for each action.

## External Connection Lifecycle

1. External customer/account performs one-time authorization.
2. Credential reference is stored in a protected credential vault.
3. Project Registry stores only metadata and the vault reference, never raw secrets.
4. XiaoE can reuse the connection for future work.
5. Read, health and diagnosis may run under the persistent authorization scope.
6. Any write/manage/destructive action requires an explicit owner approval decision.
7. Approval grants an action session, not a second bridge.
8. After execution, the action session closes while the external connection remains available.
9. If the external provider revokes or expires a token, only that credential is re-authorized; the bridge architecture is unchanged.

## Authorization Principles

- One-time platform authorization can be broad enough to let XiaoE fully repair the target project.
- XiaoE must not ask the owner to repeatedly visit GitHub, Supabase or another provider for routine repair after the connection is established.
- Provider limits still apply. XiaoE cannot exceed scopes the external provider actually granted.
- Raw secrets must never be committed to GitHub or Project Registry.
- Persistent secrets belong in a protected vault or provider-native secret store.

## Action Classes

### Automatic after connection

- read
- inspect
- health_check
- diagnose
- compare_state
- collect_evidence

### Owner approval required

- write
- update
- deploy
- migrate
- rotate_configuration
- delete
- destructive_repair

Approval should be bound to:

`project_key | requested_actions | target_resources | approval_id | approved_at`

## Project Registry Additions

External projects should be representable with metadata such as:

```json
{
  "project_key": "customer_project_x",
  "management_mode": "external_bridge",
  "ownership_scope": "external_account",
  "external_bridge": {
    "connection_key": "ext_x",
    "credential_ref": "vault://ext_x",
    "status": "authorized"
  }
}
```

Internal projects continue to use `management_mode: direct` and do not route through the Universal External Bridge.

## Failure Handling

- `credential_revoked` -> request re-authorization for that connection only.
- `scope_insufficient` -> request a one-time scope upgrade.
- `provider_unavailable` -> preserve state and retry later.
- `owner_approval_missing` -> stop before mutation.
- `project_mismatch` -> stop and re-resolve target identity.

## Non-goals for v1

- No autonomous mutation without owner approval.
- No raw secret storage in repository files.
- No per-project bridge duplication.
- No forced expiry such as 3/6/90 days at the XiaoE architecture layer.
  Provider-side credential expiry or revocation may still occur and must be handled by re-authorization.

## Canonical Summary

`Internal project = direct inner access`

`External project = one Universal External Bridge + persistent credential reference + owner-approved write session`
