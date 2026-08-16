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
