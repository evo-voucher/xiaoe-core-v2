# XiaoE Core v4.1 Migration Verification Report

Status: READY — Fresh Rebuild Core Verified
Verification mode: Isolated fresh-project rebuild + live validation
Verified on: 2026-08-24
Active repository: `Xiao-E-26/xiaoe-core-md`
Stable project key: `xiaoe_core_v2`
Fresh verification Supabase project: `xiaoe-core-fresh-verify-20260824` (`hfphfquwflupnazxibnx`)

## Scope

This report records the latest migration-readiness state of XiaoE Core v4.1 after an actual rebuild on a separate brand-new Supabase project. The existing Supabase project was not used for destructive rebuild testing.

## Fresh rebuild results

- Fresh Supabase project created successfully in `ap-northeast-2` and reached `ACTIVE_HEALTHY`.
- `supabase/bootstrap/000_preexisting_security_baseline.sql` executed successfully on the empty hosted Supabase project.
- Bootstrap recreated `public.rls_auto_enable()` and event trigger `ensure_rls`; migration `000_harden_rls_auto_enable` remained responsible for revoking direct EXECUTE privileges.
- Historical migration sequence `000` through `009` executed successfully in order.
- Fresh-project migration history contains bootstrap plus `000`–`009` with no failed migration in the rebuild run.
- `memory-gateway` deployed successfully and is `ACTIVE` with `verify_jwt=true`.
- Approved state snapshot restored 8 verified memories successfully.
- `service_xiaoe_screening()` returned XiaoE Core `4.1.0`, all expected core tables present, and 8 verified active memories.
- `service_xiaoe_bootstrap_v41('xiaoe_core_v2','小E上线')` returned `success=true`, `bootstrap_version=4.1.0`, retrieved the restored memories, and returned no memory conflicts.
- High-risk policy gate behavior was verified: missing `user_approved` produced `allowed=false`; adding it produced `allowed=true` when the other required checks were present.
- Runtime registration and validation were verified entirely server-side using ephemeral secret material generated inside PostgreSQL. `service_register_runtime_client(...)` succeeded and `service_validate_runtime_client(...,'memory:read')` returned `valid=true`. The temporary verifier client was deleted after the test and no raw runtime value was persisted in GitHub/state.
- Task context pack creation and close were verified using a single-evaluation SQL call. The pack retrieved 8 memories, 0 conflicts, opened successfully, then closed as `completed`. Test rows were removed after verification.
- All core tables have RLS enabled.
- Security Advisor reports only INFO-level `rls_enabled_no_policy` notices for the intentionally deny-by-default tables; no blocking warning/error was found.

## Test artifact note

An initial SQL-only test used PostgreSQL composite expansion syntax `(function()).*` against the side-effecting `service_create_task_context_pack(...)` function. PostgreSQL may evaluate that expression multiple times while expanding fields, which created duplicate test context rows. This was a test-query artifact, not a migration or RPC defect. All duplicate test rows were removed, and the function was retested using `FROM public.service_create_task_context_pack(...)`, which created exactly one context pack and closed correctly.

## Remaining verification boundary

The current Supabase connector can deploy and inspect Edge Functions, but it does not expose an action to invoke an Edge Function over HTTP with request headers. Therefore, the actual transport-level request to `memory-gateway` using both:

- `Authorization: Bearer <valid destination Supabase JWT>`
- `X-XiaoE-Runtime-Key: <runtime token>`

was not executed through the connector in this rebuild run.

The database-side runtime identity path was positively validated, and the deployed Edge Function is active with JWT verification enabled, but the end-to-end HTTP transport/auth request remains the only unexecuted step.

## Current readiness classification

`READY — Fresh Rebuild Core Verified` means the repository, bootstrap, migrations, schema, RLS, state restore, governance, runtime registration/validation, screening, bootstrap, policy gate, memory retrieval, and task context lifecycle have all been rebuilt and executed successfully from zero on a separate Supabase project.

`VERIFIED READY` remains reserved for completion of the one remaining transport-level gateway test: a real HTTP call to the deployed `memory-gateway` using both a valid destination JWT and runtime key.

## Fresh-project execution order

1. Create/import the GitHub repository.
2. Create a new Supabase project.
3. On a brand-new/empty Supabase project only, run `supabase/bootstrap/000_preexisting_security_baseline.sql`.
4. Apply migrations `000` through `009` in filename order. Migration `000` performs the EXECUTE privilege revoke after the prerequisite function exists.
5. Deploy `supabase/functions/memory-gateway` with `verify_jwt=true`.
6. Configure destination environment variables using fresh destination credentials.
7. Generate and securely store a new runtime token.
8. Register the destination runtime client through `service_register_runtime_client(...)` with minimum required scopes.
9. Restore the approved state snapshot; do not restore raw runtime secrets.
10. Test gateway access with both a valid destination Supabase JWT and the new runtime key.
11. Run `service_xiaoe_screening()`.
12. Run `service_xiaoe_bootstrap_v41('xiaoe_core_v2','小E上线')`.
13. Verify policy gate, Fusion Retrieve v3, task context pack, checkpoint and recovery behavior.

## Safety note

Do not run the fresh-project bootstrap blindly on an existing Supabase project. Inspect the destination first. The baseline is for a brand-new/empty project only.
