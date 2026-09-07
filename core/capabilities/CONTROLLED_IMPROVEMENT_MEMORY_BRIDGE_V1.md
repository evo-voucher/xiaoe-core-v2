# XiaoE Controlled Improvement → Persistent Memory Bridge V1

Status: Active integration contract
Version: 1.0
Capability ID: `learning.persist_verified_outcome`

## Purpose
Connect XiaoE Controlled Improvement to the existing persistent Memory Fusion layer so verified improvement outcomes can become durable reusable experience without bypassing Governance.

## Flow
`Improvement verified -> learning candidate -> durable experience save -> read-back verify -> optional promotion -> future retrieval`

## Automatic durable-save boundary
After an improvement execution has been independently verified by read-back or equivalent authoritative evidence, XiaoE MAY automatically save or update an `experience` memory through the registered persistent memory service.

Automatic durable save is allowed only when all are true:
- the improvement outcome is verified, not merely proposed or executed;
- the lesson is future-useful and project-scoped or explicitly global;
- no secret, credential, token, password, customer-sensitive payload, or transient debug data is included;
- project/environment identity is known;
- the existing Memory Contract Judge and Deduplicate rules pass;
- the write uses the registered memory executor and is read back after save.

## What automatic durable save does NOT mean
Automatic durable save does not grant autonomous core mutation, permission changes, production deployment, Governance changes, or master-learning promotion.

`Save verified experience != Promote to master learning.`

## Promotion boundary
Promotion through `service_promote_learning` remains a separate high-risk Governance capability and requires explicit user approval plus the existing promotion threshold. The improvement loop must never self-approve promotion.

## Persistent record shape
Recommended values:
- namespace: `experience`
- memory_type: `improvement_learning`
- title: concise stable lesson key
- content: problem -> change -> verified outcome -> reuse guidance
- project_key: owning project
- source: `controlled_improvement`
- verification_status: `verified`
- confidence: based on evidence, normally >= 8 only when direct read-back verification exists
- tags: include `controlled_improvement`, owning layer, and result class
- metadata: evidence summary, owner layer, verification method, change reference/commit/migration where available

## Failure behavior
If persistent save or read-back verification fails:
- do not claim the lesson was learned durably;
- preserve the verified operational result separately;
- report persistence as pending/failed in the next checkpoint;
- obey the two-failures-then-stop rule.

## Retrieval behavior
Normal Memory Fusion retrieval may return these active verified experience memories when relevant to the current project/task. A retrieved lesson is guidance, not authorization to repeat the original mutation.

## Success condition
Durable learning is complete only when the verified improvement outcome is saved through the persistent memory service and the resulting active verified memory is read back successfully.

Principle: `Verified experience may persist automatically; authority never does.`
