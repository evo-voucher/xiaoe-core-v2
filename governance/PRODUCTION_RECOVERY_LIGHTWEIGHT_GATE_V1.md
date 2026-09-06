# Production Recovery Lightweight Gate V1

Status: ACTIVE / MANDATORY
Owner: Eric Chaow
Applies to: all commercial Production changes and incidents managed by XiaoE / GPT
Primary current target: `evo_voucher_production`

## Purpose

Provide a lightweight but reliable recovery discipline without adding heavy infrastructure.

This gate adds three mandatory capabilities:

1. Production checkpoint
2. Critical smoke test
3. Standard rollback path

It complements:
- `governance/PRODUCTION_INCIDENT_REPAIR_POLICY_V1.md`
- `governance/VOUCHER_STAGE_TO_PRODUCTION_PROMOTION_POLICY_V1.md`
- `projects/voucher/VOUCHER_PRODUCTION_FROZEN_BASELINE_V1.md`

## 1. Mandatory Production Checkpoint

Before any approved Production write, merge, deploy, migration, Edge Function replacement, configuration change, or incident repair, XiaoE / GPT must record or verify a last-known-good checkpoint.

The checkpoint must identify, when applicable:

- exact Production project key
- Production GitHub repository
- current Production main commit SHA
- affected files / functions / migrations
- current Edge Function version for any function being changed
- current database migration boundary / relevant schema state
- current environment target
- reason for change
- rollback target

A Production change must not begin if the rollback target is unknown.

## 2. Critical Smoke Test

For EVO Voucher Production, the following are the default critical smoke surfaces. XiaoE / GPT must test all affected surfaces and all adjacent critical flows reasonably at risk from the change.

### Customer/public
- voucher page renders
- QR code is generated and visible
- customer name remains visible where expected
- partner name remains visible where expected
- voucher ownership / recipient identity remains correct
- public voucher route still resolves

### Partner
- partner login still works when affected
- partner dashboard loads
- voucher issue flow remains available
- issued voucher data remains correct

### Staff / redemption
- staff login still works when affected
- verify voucher works
- redeem voucher works
- reverse redemption remains controlled and functional when affected

### Admin / operational
- admin dashboard / partner management remains available when affected
- voucher template / version publication remains intact when affected
- allocation and reporting behavior remains intact when affected

### Visual / frontend regression
- existing theme, branding, layout, and major page structure remain unchanged unless explicitly approved
- no unexpected CSS/theme replacement
- no missing QR or identity fields
- no Stage-only URL, flag, asset, theme, or configuration enters Production

### Runtime / backend
- relevant Edge Functions respond
- relevant routes resolve
- database compatibility is preserved
- no new error spike appears in available logs after release

A failed critical smoke check means the Production change is not complete.

## 3. Standard Rollback Path

If a Production change causes a regression, XiaoE / GPT must prefer restoring the last-known-good state over stacking speculative fixes.

Rollback order:

1. Stop further unrelated Production changes.
2. Identify the exact last-known-good checkpoint.
3. Determine which changed unit caused or most likely caused the regression.
4. Revert the smallest changed unit first when safe.
5. If the change set cannot be safely isolated, restore the last-known-good Production code / function / configuration state.
6. For database changes, use the predefined reverse migration or recovery plan; never improvise destructive SQL.
7. Re-run the critical smoke test.
8. Only after Production is stable may a new repair attempt begin.

## Rollback prohibitions

Do not:

- overwrite Production with Stage
- delete Production data to force recovery
- force push unless a separately approved emergency procedure explicitly requires it
- stack multiple speculative patches on an unstable release
- alter unrelated code during rollback
- change secrets unless the incident is proven to involve those secrets

## Mandatory workflow interpretation

When the owner requests any Production action such as:
- deploy
- merge to Production
- publish
- fix Production
- repair EVO Voucher
- change a live function
- apply a Production migration

XiaoE / GPT must interpret the request as:

> Read the applicable Production policy, lock the exact project, verify checkpoint, perform the minimal approved change, run critical smoke tests, and retain a rollback path until Production is verified stable.

## Completion rule

A Production change is complete only when:

- checkpoint existed before change;
- approved change was applied;
- original objective is verified;
- critical smoke tests pass;
- no new known regression exists;
- rollback target remains documented until closure.

If any of these are missing, status remains `OPEN / NOT VERIFIED`.
