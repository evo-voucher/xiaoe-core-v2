# XiaoE Checkpoint Persistence Capability V1

Status: Capability contract
Version: 1.0

## Purpose
Provide a stable persistence contract for XiaoE checkpoints so shutdown state can be resumed across sessions and model environments.

## Capability scope
This capability stores and retrieves XiaoE project-management checkpoints only. It does not modify project business data, source code, deployments, or production state.

## Save operation
Input checkpoint fields:
- project_id / project_key
- environment (for example production, stage, commercial, daughter)
- current_state
- completed
- pending
- risks_unverified
- next_start_point
- created_at
- source_session/reference when available

Save requirements:
1. Validate project/environment identity before write.
2. Preserve the previous valid checkpoint; do not destructively replace history unless an explicit retention policy says otherwise.
3. Return a verifiable persistence result or identifier.
4. Never report success before the backing store confirms the write.

## Load operation
On XiaoE startup, load the newest valid checkpoint for the resolved project/environment.

Load requirements:
1. Resolve project/environment before retrieval.
2. Return the newest valid checkpoint only within that scope.
3. Compare checkpoint state with live verified project facts before continuing work.
4. Live verified facts override stale checkpoint content.
5. Report conflicts instead of silently reconciling them.

## Failure behavior
- First persistence failure: inspect the cause and retry only when safe and clearly corrective.
- Second failure: stop persistence attempts and report the failure.
- Never fabricate checkpoint data or a storage success result.
- If persistence is unavailable, return the generated checkpoint in-chat so work can still resume manually.

## Security and isolation
- Checkpoints are metadata, not credential storage.
- Never store secrets, API keys, passwords, tokens, or private credentials in checkpoint content.
- Never mix checkpoints between projects, organizations, users, or environments.
- Writes require an authorized persistence adapter/backing store.

## Runtime interface
Recommended logical interface:
```text
save_checkpoint(scope, checkpoint) -> {ok, checkpoint_id, stored_at}
load_latest_checkpoint(scope) -> {ok, checkpoint|null}
list_checkpoints(scope, limit) -> checkpoints[]
```

## Startup integration
When the behavior layer receives "小E上线":
1. Resolve the intended project/environment.
2. Invoke `load_latest_checkpoint` when available.
3. Validate against current project facts.
4. Resume from `next_start_point` only after validation.

## Shutdown integration
When the behavior layer receives "小E收工" or equivalent:
1. Generate the required five-section checkpoint.
2. Invoke `save_checkpoint` when available and authorized.
3. Report whether persistence succeeded.
4. End only after checkpoint generation and persistence status are explicit.
