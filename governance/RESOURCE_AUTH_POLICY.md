# Resource Authorization Policy

Version: 1.0
Mode: STRICT
Source of truth: `registry/RESOURCE_AUTH_REGISTRY.json`

## Purpose

Define which external GitHub and Supabase resources XiaoE / XiaoAi may read, copy, manage, or modify across accounts and environments without weakening the existing project-resolution rules.

## Permission levels

- `read`: inspect metadata, files, schema, configuration, and data allowed by the underlying connector.
- `copy`: reproduce approved material into an explicitly locked destination while keeping the source unchanged by default.
- `manage`: perform non-destructive administrative changes within an explicitly locked target.
- `destructive`: delete, overwrite production, drop data structures, force-update refs, or equivalent irreversible/high-impact actions. Requires explicit owner approval for the exact target and action.

## Mandatory execution sequence

1. Resolve the active principal (`xiaoe_core_v2`, `daughter_companion_ai`, or another registered principal).
2. Resolve source resource against `RESOURCE_AUTH_REGISTRY.json`.
3. Resolve destination separately for cross-environment work.
4. Lock source and destination identities.
5. Determine requested permission level.
6. Deny by default if the resource or action is not registered/authorized.
7. Preserve source immutability for copy/migration operations unless the owner explicitly authorizes source modification.
8. Never copy secrets, access tokens, passwords, API keys, service-role keys, OAuth refresh tokens, or runtime credentials.
9. Reissue credentials in the destination environment.
10. Require explicit owner approval before destructive production actions.

## Relationship with Project Resolution Policy

This policy extends, and does not replace, `PROJECT_RESOLUTION_POLICY.md`.

Project resolution answers: **which project is this?**
Resource authorization answers: **what may this principal do to that resource?**

Both checks must pass before cross-project or cross-account operations.

## Copy / migration semantics

A copy operation means:

- source remains unchanged by default;
- destination must be explicitly identified;
- copied code/data/config must be limited to the requested scope;
- secrets and credentials are excluded;
- successful copying does not switch production traffic automatically;
- cutover is a separate, explicit operation.

## Multi-account expansion

A new GitHub account, GitHub App installation, Supabase organization, or Supabase project becomes usable only after:

- live authorization is established;
- the resource is registered;
- permitted actions are declared;
- at least one live verification signal confirms identity;
- ambiguous aliases are rejected.
