# XiaoE UAT Incident Lessons

## 2026-08-16 — Stale UAT Entry Caused False Partner Portal Diagnosis

### Incident
A Partner UAT session used `uat/partner-qr-test.html`, which was permanently pinned to an older QR-specific commit (`fff62d9d59d65fc19b5f643bfdc0cf0049af5fe3`). The current Partner Portal had already evolved to include Partner Staff Access controls, Staff Capacity, Account Settings, and corrected Admin-vs-Partner role presentation.

The stale UAT entry successfully authenticated a real `partner_admin`, but rendered old frontend behavior:
- Evolution Admin-only warning was shown incorrectly.
- Partner Admin Staff Access control was missing.
- Staff Capacity was missing.

This created a false appearance that current Partner authorization or Supabase logic was wrong. The backend was not the root cause. The UAT entry was outdated.

### Root Cause
The UAT URL was treated as a generic Partner acceptance-test entry even though it was a historical, feature-specific test harness pinned to an old commit.

The missing control was therefore caused by **test-version drift**, not production/cutover business logic.

### Corrective Action
A new `uat/partner-full-test.html` entry was created and pinned to the then-current cutover head. The old QR-specific UAT entry remains historical/special-purpose and must not be used for full Partner acceptance testing.

### Permanent XiaoE Rule — UAT Version Ownership
Before asking the user to perform any UAT, XiaoE must verify all of the following:

1. Identify the exact feature being tested.
2. Identify the exact UAT entry being used.
3. Read the UAT entry and verify the commit/ref it pins.
4. Confirm that pinned commit actually contains the feature under test.
5. Confirm GitHub Pages deployment for the UAT entry is `completed + success` before asking the user to open it.
6. A feature-specific historical UAT entry must never be silently promoted to a full-system acceptance-test entry.
7. If the screenshot contradicts verified backend identity/permissions, first check **UAT version drift / stale pin / deployment state** before modifying backend, RLS, Auth, or business logic.
8. Do not diagnose cache as the cause unless deployment/version evidence supports it.

### Engineering Principle
**Verify the test instrument before debugging the system under test.**

This rule belongs before backend mutation in the XiaoE diagnostic order:

`Observed mismatch -> verify UAT entry/ref -> verify deployment -> compare expected frontend contract -> only then inspect backend owner layer -> smallest correct change`

### Severity
Medium operational risk, potentially high engineering risk if misdiagnosed, because a stale test harness can lead to unnecessary backend/RLS/Auth modifications.

### Prevention Status
Recorded as a permanent XiaoE collaboration/UAT discipline rule.

---

## 2026-08-16 — Multi-role UAT Session Collision Caused Partner Staff 401

### Incident
During Partner Staff UAT, the browser had recently used both Evolution Admin and Partner Portal sessions against the same Supabase project and same site origin. The real Partner Admin account (`test@yahoo.com`) had logged in successfully, but a later Partner Staff creation attempt failed with `Edge Function returned a non-2xx status code`.

The backend state showed:
- Partner `E001` remained active.
- `staff_limit = 5`.
- `staff_access_enabled = false`.
- No Partner Staff profile had been created.

Edge Function logs showed the failing `manage-partner-staff` request returned HTTP `401` before Partner Staff provisioning began. Auth logs immediately before the failure showed:

`Invalid Refresh Token: Refresh Token Not Found`

The screen also showed an Evolution Admin-only warning even though the intended test actor was the real Partner Admin, indicating stale/colliding session state across role-switching UAT pages.

### Root Cause
Multiple Admin/Partner UAT pages on the same browser origin shared the same Supabase persisted auth storage. Role switching and stale tabs caused refresh-token/session state to collide. This was a **UAT session-isolation problem**, not a Partner Staff business-rule failure.

### Corrective Action
For role-specific UAT:
- Close stale Admin/Partner UAT windows before changing actor role.
- Sign out explicitly before switching identities on the same origin.
- Re-authenticate the intended actor and verify realm/role before executing a write.
- Do not retry a failed Edge mutation until session identity and token freshness are confirmed.

### Permanent XiaoE Rule — Multi-role Session Isolation
Before any cross-role UAT (Admin, Partner Admin, Partner Staff, Evolution Staff), XiaoE must verify:

1. Which actor is expected to own the current session.
2. The visible realm/role matches that actor before any write action.
3. Stale tabs from another role are closed or explicitly signed out.
4. A `401`, refresh-token error, or role-warning mismatch is treated first as a session-isolation/auth-state problem, not as a database/RLS/business-rule defect.
5. After any `401`, inspect Auth and Edge logs before changing backend code.
6. Never weaken Auth/RLS or bypass Edge Functions to work around a UAT session collision.

### Engineering Principle
**Verify actor identity and token freshness before debugging a protected mutation.**

Diagnostic order:

`Write failed -> verify actor role -> verify session/token freshness -> inspect Auth/Edge logs -> confirm no partial write -> only then inspect business contract/backend owner`

### Severity
Medium operational risk, potentially high engineering risk if misdiagnosed because session collisions can look like authorization or Edge Function defects.

### Prevention Status
Recorded as a permanent XiaoE collaboration/UAT discipline rule.

---

## 2026-08-16 — Patch Temptation Exposed Owner-Contract Violation in Partner Staff Edge

### Incident
After the Partner Staff UAT moved from an initial `401` to a later `403`, there was a temptation to treat the failure as a missing permission and solve it by granting `service_role` direct `SELECT` access to business tables.

Read-only diagnosis showed the real sequence:
- `auth/v1/user` returned `200`; the JWT was valid.
- `current_operational_realm()` returned `200`; the actor context was valid.
- The real Partner Admin mapping was unique and correct: `realm='partner'`, `role='partner_admin'`.
- The Edge Function then performed direct reads against `public.partners` and `public.partner_users` using the service-role client.
- Those tables intentionally did not grant `service_role` direct `SELECT` access.
- The existing canonical security model already exposed trusted `SECURITY DEFINER` RPCs for Partner Staff management.

The direct table reads inside the Edge Function therefore violated the canonical owner contract. The permission error was a symptom of that architectural mismatch, not evidence that the table grants were wrong.

### Root Cause
`manage-partner-staff` mixed two different trust models:

1. Canonical model: service-role calls narrow trusted RPCs that own validation, tenant checks, staff limits, status rules, and audit logging.
2. Non-canonical implementation: service-role directly reads protected business tables before calling those RPCs.

The Edge implementation had drifted away from the intended security boundary.

### Corrective Action
Do **not** broaden table privileges to satisfy a caller that is bypassing the owner contract.

The correct repair is to make the Edge Function an orchestrator only:
- Auth Admin API for Auth-user creation/password operations.
- `partner_provision_staff()` for creation.
- `partner_update_staff_profile()` for rename/suspend/activate/remove.
- `partner_record_staff_password_reset()` for audit after password reset.
- `resolve_partner_management_context()` / caller-scoped directory RPCs for tenant and actor validation.
- No direct `SELECT` from protected Partner business tables when a trusted RPC already owns that responsibility.

### Permanent XiaoE Rule — Owner Contract Before Permission Change
When a protected operation fails with `401/403/permission denied`, XiaoE must not immediately add grants, weaken RLS, expose tables, or add bypasses.

Required diagnostic order:

1. Verify token/authentication.
2. Verify actor realm/role mapping.
3. Identify the exact failing call from logs.
4. Identify which layer owns that data/action.
5. Inspect whether a canonical RPC/Edge contract already exists.
6. If the caller bypasses that contract, repair the caller first.
7. Change grants/RLS only when evidence shows the canonical owner itself lacks a required permission.
8. Prefer reducing duplicate authorization logic over adding another permission path.

### Engineering Principle
**A permission error does not automatically mean a permission grant is missing. It may mean the caller is operating at the wrong layer.**

XiaoE should prefer:

`Trace failing call -> identify owner -> use existing contract -> remove bypass -> verify -> stop`

over:

`See 403 -> add grant -> retry -> add another grant -> accumulate patches`

### Severity
High architectural risk. A quick permission grant could have weakened the canonical security boundary across all Partners just to make one Edge path work.

### Prevention Status
Recorded as a permanent XiaoE engineering discipline rule: **Root before flower; owner contract before permission expansion.**
