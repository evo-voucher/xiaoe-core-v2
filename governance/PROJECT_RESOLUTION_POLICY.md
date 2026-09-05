# Project Resolution Policy

Version: 1.0  
Mode: STRICT  
Source of truth: `registry/PROJECT_REGISTRY.json`

## Purpose

Prevent XiaoE from mixing repositories, Supabase projects, files, URLs, checkpoints, or runtime data when multiple projects exist.

## Mandatory resolution sequence

Every project-related request must run this sequence before retrieval or mutation:

1. **Detect explicit project identity**
   - Activation phrase, exact project key, exact repository name, or exact Supabase project ID.
2. **Resolve against the registry**
   - An exact match locks one project.
   - A nickname is valid only when it maps to exactly one active project.
3. **Create a session project lock**
   - Store: `project_key`, GitHub repository, Supabase project ID, and allowed scope.
4. **Retrieve only inside the lock**
   - Do not search another repository or Supabase project unless the user explicitly requests comparison, migration, fusion, or cross-project work.
5. **Verify every returned project URL**
   - The owner/repository pair must equal the locked registry record.
   - Never construct a project URL from memory.
   - Return only a URL obtained from the registry or a live tool result.
6. **Report or stop**
   - If one candidate is verified, proceed.
   - If zero or multiple candidates remain, ask the user to choose. Never guess.

## Resolution priority

Highest to lowest:

1. Exact Supabase project ID
2. Exact GitHub `owner/repository`
3. Exact `project_key`
4. Explicit activation phrase
5. Unique registered alias
6. Conversation context

Conversation context can narrow candidates but cannot override an exact identifier.

## Session behavior

- `小E上线` locks `xiaoe_core_v2`.
- `小爱上线` locks `daughter_companion_ai`.
- The lock remains until the user switches, ends the mode, or explicitly requests cross-project work.
- Mentioning another project does not automatically switch the lock.
- A write operation must repeat the locked target internally before execution.

## Cross-project guard

Cross-project access is allowed only for an explicit request such as:

- compare
- migrate
- merge/fuse
- copy approved material
- audit relationships

For cross-project work, identify **source** and **destination** separately. If either is unclear, stop.

## URL validation

Before returning a GitHub or Supabase URL, verify:

- locked `project_key`
- expected service
- exact owner/repository or project ID
- requested file/path belongs to that target
- current status is appropriate (active vs verification-only)

A verification-only project must never be presented as the primary production project.

## Failure behavior

When confidence is insufficient, respond with the candidate list and ask for one choice. Do not silently fall back to the most recent project, the first search result, or a similarly named repository.

## Adding future projects

No new project becomes resolvable until it has:

- a unique `project_key`
- a canonical GitHub repository
- the correct Supabase project ID, if applicable
- unique aliases and activation phrases
- an explicit status and role
- at least one live verification signal

This registry-first design remains stable as the number of projects grows.
