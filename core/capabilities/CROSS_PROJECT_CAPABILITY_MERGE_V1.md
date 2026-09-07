# XiaoE Cross-Project Capability Merge V1

Status: Active orchestration contract
Version: 1.0
Capability ID: `project.capability_merge`

## Purpose
Allow XiaoE to bring a mature capability from one project into another without copying project identity, credentials, environment bindings, or unrelated implementation details.

Principle: `Merge capability, not project identity.`

## Trigger
Use this capability when the user asks to bring, merge, copy, port, reuse, or transplant a feature/capability from a source project into a target project.

## Required flow
`Source Capability Scan -> Dependency Map -> Target Gap Analysis -> Merge Plan -> Controlled Apply -> End-to-End Verify -> Learn`

## 1. Source Capability Scan
Identify the complete source capability boundary before changing the target project.

Inspect only the parts relevant to the requested capability, including when applicable:
- frontend files/components
- backend/API/RPC/functions
- database tables/columns/views
- RLS/permissions/policies
- routes
- configuration/environment references
- deployment/runtime bindings
- tests/health checks
- behavior/capability contracts
- memory/runtime dependencies

Do not assume one visible file equals the whole capability.

## 2. Dependency Map
Create a dependency manifest showing:
- required dependency
- source location
- role in the capability
- whether project-specific
- whether portable
- target equivalent if one exists

Secrets, project IDs, account IDs, URLs, organization identifiers, production credentials, and customer/business data are identity-bound and are not portable by default.

## 3. Target Gap Analysis
Compare source capability requirements against the target project and classify every dependency as:
- already_present_compatible
- already_present_needs_adaptation
- missing_required
- conflicting
- source_specific_do_not_copy

Prefer adapting to existing target primitives instead of duplicating equivalent systems.

## 4. Merge Plan
Before mutation, define:
- exact target project/environment
- files/schema/functions to add or change
- source-specific elements to exclude
- compatibility risks
- required approvals
- verification path
- rollback/stop condition when applicable

A merge plan must not silently expand scope into unrelated project cleanup or refactoring.

## 5. Controlled Apply
Execute only through existing registered capabilities and Governance-approved executors.

Rules:
- source project is read-only unless the user separately authorizes changes there;
- target project receives only the minimum required capability/dependencies;
- preserve target naming, identity, configuration, permissions, URLs, database references, and environment separation;
- never copy secrets or credentials;
- never replace a working target subsystem merely because the source implementation is different;
- production/protected-layer changes remain subject to existing Governance and approval rules.

## 6. End-to-End Verification
The merge is not complete when code is copied or a PR is merged.

Run the XiaoE End-to-End Completion Gate for the target user-visible capability and verify all applicable layers:
- requirement match
- data/source correctness
- backend/interface correctness
- frontend/render correctness
- delivery/runtime/cache correctness
- actual user path
- target environment/device behavior when relevant

Only `end_to_end_verified` may be called fully complete.

## 7. Learning
After successful verification, the reusable porting lesson may enter the Controlled Improvement -> Persistent Memory flow as verified experience.

Record only portable lessons, such as:
- required dependency pattern
- target adaptation pattern
- proven incompatibility
- cache/deployment issue
- permission requirement

Do not store source secrets, customer data, or identity-bound configuration as reusable learning.

## Identity Isolation Rule
The following must remain owned by the target project unless explicitly designed as shared infrastructure:
- company/brand identity
- project key
- repository ownership
- Supabase project ref
- environment URLs
- API keys/secrets
- runtime keys
- database data
- partner/customer records
- production deployment identity

If any of these are detected in a proposed copy, stop and adapt instead of copying.

## Conflict Rule
If source and target already implement equivalent capability differently, XiaoE must compare the two and choose the safer minimal adaptation path. Do not create parallel duplicate logic unless explicitly required.

## Failure Rule
When the same porting path fails twice:
- stop that path;
- report the first failing layer and evidence;
- do not repeat the same mutation;
- choose a different verified adaptation path or request clarification if truly necessary.

## Completion Report
When complete, report:
- source capability used
- target project changed
- dependencies merged/adapted
- source-specific elements intentionally excluded
- verification status
- any remaining environment/user verification pending

## Success Condition
A cross-project capability merge is complete only when the target project owns an adapted, isolated implementation that passes the End-to-End Completion Gate without inheriting source-project identity or secrets.
