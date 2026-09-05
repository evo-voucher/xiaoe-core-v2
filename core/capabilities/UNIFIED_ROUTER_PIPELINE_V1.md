# XiaoE Unified Router Pipeline v1

Status: ACTIVE ORCHESTRATION CAPABILITY
Date: 2026-08-26
Repository: `Xiao-E-26/xiaoe-core-md`
Purpose: Connect project resolution, task-intent classification, capability selection, execution routing, verification, and reclassification into one lightweight routing pipeline without creating a second Behavior or Governance system.

## Position

This pipeline is an orchestration layer only.

It does not replace:
- `XIAOE_STARTUP_ROUTING_GUARD_V1.md`
- `registry/PROJECT_REGISTRY.json`
- `core/capabilities/TASK_INTENT_ROUTER_V1.md`
- `core/capabilities/CAPABILITY_REGISTRY_V1.md`
- `core/capabilities/EXECUTION_ROUTER_DECISION_CONTRACT_V1.md`
- Behavior
- Governance / Policy Gate
- Memory Fusion v3

Authority remains:

`Behavior > Governance > Project Resolution > Task Intent Router > Capability Registry > Execution Router > Executor`

## Core Goal

Turn an incoming request into the smallest correct verified execution path.

Canonical pipeline:

`Detect -> Resolve Project -> Classify Problem -> Estimate Confidence -> Select Task Route -> Select Capability -> Check Governance -> Select Executor -> Execute -> Verify -> Reclassify or Close`

## 1. Detect

Interpret the user's intended outcome rather than routing from a single keyword.

Before any mutation, identify:
- requested outcome;
- whether this is read, diagnosis, change, deployment, or architecture work;
- whether a named project, repository, environment, account, or runtime is explicit.

Do not treat a quoted trigger, example phrase, or explanatory mention as an invocation.

## 2. Resolve Project First

For project-scoped work, resolve the project before choosing a specialist capability.

Resolution order:
1. explicit project key / repository / environment from current user instruction;
2. exact activation mapping;
3. `registry/PROJECT_REGISTRY.json` canonical identity;
4. verified live source evidence when ambiguity remains;
5. if still ambiguous, classify as `PROJECT_UNRESOLVED` and investigate rather than guess.

Minimum project resolution output:
- `project_key`
- `repository_full_name`
- `environment`
- `runtime/source-of-truth`
- `resolution_confidence`
- `resolution_evidence`

Project resolution must not silently inherit an adjacent project's repository, Supabase project, memory, or environment.

## 3. Classify Problem

After project resolution, classify the problem into a lightweight operational domain.

Primary problem classes:
- `UI_TRIGGER`
- `FRONTEND_STATE`
- `AUTHENTICATION`
- `AUTHORIZATION_RLS`
- `DATABASE_DATA`
- `API_INTEGRATION`
- `EDGE_FUNCTION_BACKEND`
- `GITHUB_SOURCE`
- `SUPABASE_PLATFORM`
- `MEMORY_CONTEXT`
- `PROJECT_RESOLUTION`
- `SECURITY_RISK`
- `ARCHITECTURE_DESIGN`
- `FEATURE_PRODUCT_FLOW`
- `UNKNOWN`

These classes are routing labels, not new constitutions or security rules.

## 4. Confidence Gate

Every non-trivial classification should carry a practical confidence level:
- `high` — owner/effect is clear from verified evidence;
- `medium` — likely owner is known but at least one competing explanation remains;
- `low` — evidence is insufficient or multiple layers could own the symptom.

Rules:
- `high` may proceed to normal capability selection;
- `medium` should verify one or two discriminating facts before mutation;
- `low` must route to `diagnostics.root_cause_analysis` / investigation first.

Do not convert uncertainty into more rules.

## 5. Task Route Selection

Map the classified problem into the existing Task Intent Router route:
- fault/symptom -> `Incident / Fault`
- narrow reversible local change -> `Small Direct Change`
- new behavior / workflow -> `New Feature / Product Flow`
- boundary / ownership / integration model -> `Architecture / System Design`
- auth / RLS / secrets / persistent data -> `Security / Auth / Permission / Persistent Data`

If evidence later changes the true owner, effect, scope, risk, uncertainty, or dependency structure, re-run routing.

## 6. Capability Selection

Use `CAPABILITY_REGISTRY_V1.md` to select the smallest capability that owns the intended effect.

Rules:
1. do not pick a tool first and invent the rationale afterward;
2. do not create a new Agent/capability for a one-off problem;
3. prefer one owning capability over unnecessary chaining;
4. if no capability owns the effect, classify `CAPABILITY_GAP` and treat it as design work;
5. availability is not authorization.

## 7. Governance Gate

Before mutation, apply existing Governance / Policy Gate according to the actual risk.

Router may not:
- bypass approval;
- invent permissions;
- ignore protected layers;
- choose a more permissive executor to route around a block;
- treat connected tools as permission to act.

## 8. Executor Selection

After capability ownership is known, choose the actual executor/tool.

Selection priorities:
1. capability fit;
2. live availability;
3. correct project/environment binding;
4. required permission/scopes;
5. risk and privacy boundary;
6. reliability;
7. compatible fallback if registered.

Executor selection happens after routing, not before it.

## 9. Execute

Execute only within the locked scope.

Minimum execution context:
- task goal;
- project key;
- problem class;
- capability key;
- selected executor;
- risk level;
- change/read scope;
- verification target.

## 10. Verify

Executor return values are not enough.

Verify against the authoritative source whenever practical.

Examples:
- UI/trigger fix -> reproduce exact interaction path;
- GitHub write -> read back file/commit;
- Supabase schema/data change -> query resulting canonical state;
- Edge Function deployment -> inspect deployed function + runtime behavior when possible;
- permission/RLS change -> run positive and negative access tests.

Verification result:
- `verified_success`
- `partial_success`
- `failed`
- `owner_mismatch`
- `new_evidence`

## 11. Reclassification Loop

If verification reveals that the original problem class or owner was wrong:

`Verify -> New Evidence -> Reclassify -> Re-select Capability -> Re-run Governance -> Execute`

Do not continue patching the wrong layer.

Examples:
- button symptom -> frontend checked -> API 403 found -> reclassify to `AUTHORIZATION_RLS`;
- login callback symptom -> auth user exists -> callback broken -> reclassify to `API_INTEGRATION` / redirect handling;
- data missing in UI -> canonical rows correct -> reclassify to `FRONTEND_STATE`.

## 12. Stop Conditions

Stop and investigate when:
- project cannot be resolved confidently;
- classification confidence is low;
- authoritative source is unavailable;
- Governance blocks execution;
- repeated same-path failure occurs;
- verification contradicts the assumed owner;
- fallback would change permission, data boundary, or risk without re-evaluation.

## 13. Minimal Router Output Contract

For non-trivial work, the internal routing decision should be representable as:

```text
project_key:
problem_class:
classification_confidence:
task_route:
capability_key:
selected_executor:
risk_level:
policy_state:
decision: execute | investigate | reclassify | await_approval | block
verification_target:
```

This does not need to be shown to the user unless useful.

## 14. Anti-Bloat Rule

Do not create one Agent per problem.

Preferred model:

`Many problems -> few stable problem classes -> few reusable capabilities/Agents -> tools/executors`

Create a new capability/Agent only when a recurring class has:
- distinct ownership;
- stable input/output contract;
- distinct tool/permission needs;
- independent verification method;
- enough repeated evidence to justify separation.

## 15. Example: Voucher Button Does Not Respond

Input symptom:
`voucher 页面按钮没反应`

Router flow:
1. Resolve project -> voucher project.
2. Classify -> likely `UI_TRIGGER` / `FRONTEND_STATE`.
3. Confidence -> medium until click handler / console / network evidence is checked.
4. Task route -> `Incident / Fault`.
5. Capability -> diagnostics first if owner not verified.
6. Inspect trigger -> if request never fires, remain frontend.
7. If request fires and API returns 403, reclassify to `AUTHORIZATION_RLS`.
8. Select owning capability/executor.
9. Apply Governance if mutation risk requires it.
10. Repair smallest correct layer.
11. Reproduce button path and verify canonical backend state.

The Router solves the class of problem without creating a new rule for that exact button.

## 16. Compatibility Boundary

This v1 is additive and GitHub-first.

Do not yet:
- create a new persistent Router database;
- rewrite Behavior;
- replace Task Intent Router;
- move project truth out of `PROJECT_REGISTRY.json`;
- create autonomous mutation authority;
- add extra Agent layers without evidence.

## 17. Observation Metrics

Observe real tasks for:
- wrong project resolution;
- wrong problem classification;
- low-confidence tasks executed too early;
- wrong capability selection;
- tool-first routing;
- missing reclassification after new evidence;
- correct/incorrect post-verification;
- unnecessary Agent/capability creation;
- simple tasks becoming over-engineered.

Only automate or persist more Router state after this pipeline proves useful in repeated real work.

## Summary

`Resolve the right project -> identify the real problem class -> route to the smallest owning capability -> choose the correct executor -> verify -> reclassify when evidence changes.`

The purpose of Router evolution is not to add more rules. It is to make XiaoE better at sending the right problem to the right capability in the right project with the right evidence and the right verification.
