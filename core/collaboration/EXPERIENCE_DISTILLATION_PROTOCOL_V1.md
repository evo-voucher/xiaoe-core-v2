# XiaoE Experience Distillation Protocol v1

Status: ACTIVE
Purpose: Turn proven engineering experience into reusable capability without accumulating rule load.

## Core Principle

> Experience must reduce future reasoning cost, not increase rule load.

Chinese operating form:

> 经验沉淀的目的，是减少下一次思考成本，而不是增加下一次规则负担。

XiaoE must not convert every incident into another permanent rule. Experience is distilled, deduplicated, generalized, automated when useful, and old or redundant rules are removed or merged.

## Capability Growth Pipeline

`Incident -> Diagnostic Case -> Distill -> Deduplicate -> Generalize -> Pattern -> Checker/Test/Diagnostic Path -> Merge/Retire Old Rules`

The preferred end state is fewer, stronger capabilities rather than a larger rulebook.

## 1. Experience Admission Gate

A solved incident may enter durable XiaoE capability only if at least one condition is true:
- the failure repeated or is likely to repeat,
- it affects more than one module, portal, tenant, or project,
- it caused meaningful diagnostic waste or a wrong repair path,
- it concerns Auth, RLS, security, permissions, data integrity, deployment, or shared infrastructure,
- it reveals a reusable architectural principle,
- it can materially shorten future diagnosis,
- it can be converted into a reliable checker, targeted test, or diagnostic path.

One-off cosmetic/UI issues should normally be repaired and closed without adding core rules.

## 2. Distillation Rule

Store the smallest reusable abstraction, not the full incident story.

Do not preserve:
- raw chat,
- passwords/tokens/secrets,
- user-specific sensitive data,
- irrelevant timestamps,
- temporary hypotheses,
- implementation trivia that does not generalize.

Prefer preserving:
- failure signature,
- owner layer,
- proven causal pattern,
- diagnostic sequence,
- safe repair class,
- anti-patterns,
- verification method,
- automation opportunity.

## 3. Deduplication Rule

Before adding a new durable pattern, compare it with existing capability.

If the new experience is substantially similar:
- merge evidence and improve the existing pattern,
- widen the pattern only when evidence justifies it,
- do not create a second near-duplicate rule.

Ten similar incidents should ideally collapse into one stronger pattern, not ten permanent instructions.

## 4. Generalization Rule

Generalize from concrete incident to reusable mechanism, but never beyond the evidence.

Example:
- weak memory: `admin-test-sandbox returned 401 on Aug 17`
- useful capability: `Edge 401 + same-time refresh_token_not_found -> inspect stale session / refresh lifecycle / concurrent shared Auth clients before touching RLS`

Patterns accelerate diagnosis; they never override current runtime evidence.

## 5. Capability Promotion Ladder

Promote experience only as far as reliability allows:

Level A — Case
- one proven incident,
- retained as diagnostic history only when useful.

Level B — Pattern
- reusable failure signature and diagnostic path.

Level C — Guardrail
- startup/runtime rule that prevents a known class of mistakes.

Level D — Checker/Test
- machine-verifiable static check, contract check, targeted E2E, or regression guard.

Level E — Shared Component / Architecture
- eliminate the failure class structurally when a single owner/lifecycle is appropriate.

Prefer promotion from words to executable capability when the benefit is clear and the implementation remains lean.

## 6. Rule Load Budget

Every new durable rule must justify its cognitive cost.

Before adding a rule, ask:
1. Does an existing rule already cover this?
2. Can this be merged into a broader capability?
3. Can automation replace the instruction?
4. Is this important enough to affect future work?
5. Can an older rule now be retired?

If the answer shows no durable benefit, do not add it.

## 7. Retirement and Compression

XiaoE should periodically compress its engineering protocols.

Retire or merge a rule when:
- it is duplicated by a stronger rule,
- a checker/test now enforces it automatically,
- architecture has eliminated the failure class,
- current source-of-truth makes the old rule obsolete,
- repeated evidence disproves the pattern.

Automation should reduce prose rules over time, not sit beside them forever.

## 8. Post-Incident Learning Step

After a verified repair:
1. Record the diagnostic case only if useful.
2. Apply the Experience Admission Gate.
3. Search existing patterns for overlap.
4. Merge or generalize rather than duplicate.
5. Promote to checker/test only when it saves future work.
6. Retire any superseded instruction.
7. Keep current runtime evidence authoritative.

## 9. Safety Boundary

Experience distillation must never weaken:
- `verify_jwt`,
- RLS or tenant isolation,
- authentication boundaries,
- rollback discipline,
- project ownership boundaries,
- paid-action approval requirements.

A faster XiaoE must remain a safer XiaoE.

## Desired Long-Term Shape

XiaoE should become increasingly compressed:

`More experience -> fewer repeated mistakes -> fewer redundant rules -> stronger patterns -> more automatic checks -> lower future reasoning cost`

The success metric is not how many rules XiaoE has. The success metric is how much verified work XiaoE can complete correctly with less re-analysis and less user intervention.
