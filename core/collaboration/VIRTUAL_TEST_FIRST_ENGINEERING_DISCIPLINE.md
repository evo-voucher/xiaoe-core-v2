# XiaoE Virtual-Test-First Engineering Discipline

## Purpose
XiaoE should not make the user repeatedly click, log in, scan, or reproduce failures when the system can be verified safely by machine-level tests first.

The default testing order is:

`Static/contract check -> virtual or transactional machine test -> automated integration/E2E -> real-device UAT -> stop`

Real-device UAT is the last validation layer, not the first debugging tool.

## Core Rule
**If XiaoE can verify it safely without requiring the user, XiaoE must test it first.**

The user should only be asked to perform actions that genuinely require a human/device/browser context, such as camera access, QR scanning, real login UX, Safari/iOS rendering, push/system permission prompts, physical-device behavior, or final acceptance judgment.

## What Counts as Virtual / Machine Testing
Where technically appropriate, XiaoE should prefer one or more of the following before asking for manual UAT:

1. Read-only contract inspection of functions, RPCs, RLS, grants, Edge source, frontend call paths, and deployment refs.
2. Transactional database simulations that end with `ROLLBACK` and leave no business data behind.
3. Temporary synthetic test records only when necessary and explicitly isolated from real business data.
4. Role/realm simulations using existing canonical security contracts rather than bypassing them.
5. Automated API/RPC/Edge path checks.
6. Duplicate, invalid-state, tenant-boundary, status-transition, and limit tests.
7. Verification that no partial writes remain after expected failures.
8. UAT harness verification: pinned commit, pinned dependencies, deployment status, and environment configuration.

## Safety Rules
Virtual testing must never become a shortcut around architecture or security.

- Do not disable RLS for testing.
- Do not weaken grants to make a test pass.
- Do not bypass Auth or trusted Edge/RPC ownership.
- Do not write directly into protected Auth tables.
- Prefer transaction + rollback for database mutation tests.
- If a synthetic persistent record is unavoidable, clearly label it as UAT/test data and plan cleanup.
- Never expose service-role keys or other secrets.
- A passing simulation does not replace real-device UAT for device/browser-specific behavior.

## Root-Before-Flower Testing Order
When a protected operation fails:

`Observe failure -> verify test instrument -> verify actor/session -> inspect logs -> identify failing owner layer -> inspect canonical contract -> run virtual/transactional test -> make smallest correct change -> rerun machine test -> real-device UAT only if still required`

Do not use repeated user clicking as a substitute for diagnosis.

## User Interaction Rule
Before asking the user to test again, XiaoE should be able to state what has already been machine-verified and exactly what remains impossible to verify without the user's real device/session.

Bad pattern:
`Change -> ask user to click -> fail -> change again -> ask user to click again`

Preferred pattern:
`Diagnose -> machine-test -> correct owner layer -> machine-test again -> ask user once for final real-device validation`

## Stop Condition
Once the machine layer and required real-device layer both satisfy the business goal, security contract, and expected failure cases, stop. Do not keep expanding test scope merely because additional checks are possible.

## Permanent XiaoE Principle
**XiaoE tests first; Eric performs only the final human/device checks that XiaoE cannot reliably simulate.**
