# XiaoE Core v4.1 — True Full Migration Guide

Package date: 2026-08-23
Source repository: `evo-voucher/xiaoe-core-v2`
Source main commit: `c83efbb35d40470381e50ff1003b58d107b1f585`
Source Supabase project: `xiaoe-core-v2` (`iovazhaxsllwgihblsfy`)

## Purpose
This package is designed to move XiaoE Core to a new GitHub account/repository and a new Supabase project without coupling it to Evolution Voucher.

## What must move
1. GitHub source tree: architecture, core behavior/capability/collaboration/governance/memory/runtime files, Supabase functions and migrations, and protection workflow.
2. Supabase schema/migrations: apply in order, including v4.1 governance migration.
3. Edge Function: `memory-gateway` with JWT verification enabled.
4. State snapshot: verified memories and relevant runtime state if intentionally restored.
5. External configuration: create fresh environment secrets in the destination. Do not copy secrets into source control.
6. AI/tool runtime: reconnect model provider and tool permissions separately; the ZIP contains XiaoE Core logic/state architecture, not AI compute credentials.

## Destination bootstrap order
1. Create a new private GitHub repository and import the contents of this package.
2. Create a new Supabase project.
3. Apply `supabase/migrations` in filename order.
4. Deploy `supabase/functions/memory-gateway` with `verify_jwt=true`.
5. Set destination environment variables from `.env.example`; use new destination keys.
6. Restore approved state snapshot, if included.
7. Run screening before any project work: `service_xiaoe_screening()`.
8. Run bootstrap: `service_xiaoe_bootstrap_v41('xiaoe_core_v2','小E上线')`.
9. Verify policy gate behavior for high-risk actions.
10. Verify Fusion Retrieve v3, task context pack creation/close, checkpoint/recovery, then mark the destination active.

## Existing-project safety rule
If the destination already contains a project or older XiaoE structure, do not overwrite blindly. First inspect registry/current structure, run screening and compare versions. Preserve healthy existing layers. Reopen a protected layer only with an explicit reason and human approval.

## Secrets rule
`service_role` keys, runtime raw tokens and AI API keys are never stored in the ZIP or Persistent State. Create or rotate them in the destination secure runtime.

## Compatibility
XiaoE Core v4.1 is additive over Memory Fusion v3. Existing v3 memory tables/services stay available. Migration order is schema → RLS/grants → functions → seed rules/meta → Edge Function → auth/runtime mapping → migration tests.

## Definition of complete migration
A migration is complete only after the destination passes: screening → bootstrap v4.1 → memory retrieval → policy gate → task context → checkpoint → recovery → shutdown/resume verification.
