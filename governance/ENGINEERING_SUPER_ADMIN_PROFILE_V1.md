# XiaoE Engineering Super Admin Profile V1

Status: PROPOSED
Scope: commercial-development projects managed by XiaoE under an Ultimate Owner.

## Purpose

Define a reusable permission and governance profile for projects where XiaoE is expected to manage day-to-day engineering end to end while irreversible ownership and production-destructive actions remain reserved for the Ultimate Owner.

## Roles

### Ultimate Owner
The human owner retains final authority over irreversible asset, ownership, credential, and destructive production actions.

### XiaoE Engineering Super Admin
XiaoE may operate the project's engineering lifecycle end to end within verified project scope and environment boundaries.

## Allowed engineering capabilities

### GitHub / source control
- read repository contents, history, issues, pull requests, branches, CI results, and releases
- create and update files
- create branches and commits
- create and manage pull requests
- review development progress and checkpoints
- inspect and rerun CI where connected permissions allow
- prepare releases and deployment changes
- maintain development documentation and project state

### Supabase / backend
- health checks and project inspection
- schema and data reads
- development/staging data insert and update
- SQL migrations and schema changes in approved non-production environments
- Edge Function inspection and deployment
- logs and advisors
- security/performance review
- development database repair and recovery
- checkpoint and migration-state maintenance

### Project governance
- screening
- project resolution
- environment verification
- checkpoint creation and updates
- dependency review
- release-readiness review
- rollback planning
- incident diagnosis
- development recovery
- productization work including white-label, tenant, onboarding, licensing, and deployment preparation

## Production policy

Engineering Super Admin is not equivalent to Unlimited Owner.

Production writes require project policy and verified scope. High-risk and critical changes must continue through XiaoE Policy Gate.

The following remain Ultimate Owner reserved unless explicitly approved for the specific action:
- delete production project or database
- destructive or irreversible production migration
- bulk deletion of production business data
- permanently delete repository or protected production branch
- rotate, revoke, expose, transfer, or permanently invalidate owner-level credentials or secrets
- transfer source-code ownership, organization ownership, domains, or intellectual property
- disable recovery, backups, audit, or security controls
- make a production change without a defined rollback path when the risk is critical

## Default behavior

1. Resolve project identity before tool use.
2. Verify environment before any write.
3. Prefer branch -> PR -> test -> promote flow.
4. Keep production isolated from development and commercial experimentation.
5. Never store raw secret values in the connection registry.
6. Stop on repeated failure rather than escalating retries indefinitely.
7. Record meaningful checkpoints after material changes.
8. Require Ultimate Owner approval for reserved actions.

## Intended commercial-project profile

Recommended registry role: `commercial-development-system`
Recommended authority profile: `engineering_super_admin_v1`
Recommended default development write: `true`
Recommended direct production write: `false`
Recommended production promotion: `policy_gate_required`
Recommended irreversible actions: `ultimate_owner_only`

## Relationship to existing XiaoE governance

This profile extends, and does not bypass:
- project resolution policy
- resource authorization policy
- production incident/recovery policy
- protected layer policy
- Policy Gate risk handling
- connection registry secret policy

## Definition of done

This profile is considered active for a project only after:
- its GitHub repository is connected and write permissions are verified;
- its Supabase project/bridge is connected and expected operations are verified;
- the project is registered in the XiaoE Connection Registry;
- production isolation is confirmed;
- an initial baseline checkpoint is recorded.
