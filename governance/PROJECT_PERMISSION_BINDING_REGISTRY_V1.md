# XiaoE Project Permission Binding Registry V1

Status: PROPOSED
Scope: explicit binding between project identities and authority profiles.

## Purpose

Prevent authority profiles from being inherited, guessed, or applied across projects. Permissions become valid only when a project is explicitly bound to an approved authority profile.

## Core rules

1. No implicit inheritance. A project without an explicit authority binding has no elevated profile.
2. Resolve project identity before any write operation.
3. Resolve environment before any write operation.
4. Authority is evaluated from `project_id + environment + authority_profile`, never from conversational context alone.
5. Commercial-development authority must not grant write access to existing production projects.
6. Production authority is separate from development authority.
7. Unknown, ambiguous, or conflicting bindings fail closed.
8. Existing production projects remain unchanged unless explicitly rebound by the Ultimate Owner.

## Binding record

Each binding should contain at least:
- project_id
- project_role
- authority_profile
- allowed_environments
- github_repository
- supabase_project_ref or bridge route
- default_write
- production_write
- irreversible_actions
- owner_approval_required
- status
- verified_at

## Default binding policy

### Existing production systems
- authority_profile: existing project policy
- default_write: false unless already explicitly configured
- production_write: false by default
- irreversible_actions: Ultimate Owner only

### Existing stage/development systems
- retain existing authority and routes
- do not inherit `engineering_super_admin_v1` automatically

### New commercial-development system
Recommended binding:
- authority_profile: `engineering_super_admin_v1`
- allowed_environments: development, staging
- default_write: true
- production_write: false
- irreversible_actions: Ultimate Owner only
- owner_approval_required: high/critical production promotion

## Write gate

Before a write-capable tool call, Runtime must verify:
1. resolved project matches the requested project;
2. resolved environment is allowed by the binding;
3. requested action is allowed by the authority profile;
4. the target resource belongs to the resolved project;
5. production policy is satisfied when target environment is production;
6. required owner approval is present for reserved actions.

If any check fails, the write must stop.

## Production isolation rule

A development or commercial authority profile may never be used as evidence that production write is allowed.

`engineering_super_admin_v1` means full engineering authority inside explicitly bound development/staging environments. It does not imply unrestricted production authority.

## Registry interaction

The Connection Registry records verified project-to-resource routes.
The Permission Binding Registry records project-to-authority relationships.
Both must resolve successfully before elevated writes.

Connection without authority does not grant write permission.
Authority without a verified connection does not grant write permission.

## Failure behavior

Fail closed when:
- project identity is ambiguous;
- environment is unknown;
- binding is missing;
- target resource does not match the binding;
- authority profile is inactive;
- production approval is required but absent.

Do not ask the owner to re-enter known connection details unless verification fails or the owner changes the connection.

## Activation

This policy becomes operational for a project only after an explicit binding record is created and verified. Creating an authority profile alone does not activate it for any project.
