import {
  startXiaoEProject,
  type XiaoELiveVerificationResult,
} from "./XIAOE_STARTUP_ORCHESTRATOR_V1.ts";
import type {
  XiaoECurrentProjectState,
  XiaoERuntimeClient,
} from "./XIAOE_RUNTIME_CLIENT_V1.ts";

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(`Assertion failed: ${message}`);
}

function assertEquals<T>(actual: T, expected: T, message: string) {
  if (actual !== expected) {
    throw new Error(
      `Assertion failed: ${message}; expected=${String(expected)} actual=${String(actual)}`,
    );
  }
}

function checkpoint(content = "continue from verified point"): XiaoECurrentProjectState {
  return {
    id: "checkpoint-1",
    namespace: "project",
    memory_type: "current_project_state",
    title: "Current Project State",
    content,
    importance: 10,
    project_key: "xiaoe_core_v2",
    source: "xiaoe-runtime",
    metadata: {},
    is_active: true,
    updated_at: "2026-08-27T02:00:00Z",
    verification_status: "verified",
  };
}

function runtimeReturning(
  state: XiaoECurrentProjectState | null,
): XiaoERuntimeClient {
  return {
    readCurrentProjectState: async () => state,
  } as unknown as XiaoERuntimeClient;
}

function runtimeThrowing(message: string): XiaoERuntimeClient {
  return {
    readCurrentProjectState: async () => {
      throw new Error(message);
    },
  } as unknown as XiaoERuntimeClient;
}

function verifierReturning(result: XiaoELiveVerificationResult) {
  return async () => result;
}

Deno.test("startup: no checkpoint + live verification passes => no_checkpoint and continue", async () => {
  const result = await startXiaoEProject(
    {
      runtimeClient: runtimeReturning(null),
      verifyLiveSourceOfTruth: verifierReturning({
        ok: true,
        checks: { github: "verified" },
      }),
    },
    "xiaoe_core_v2",
  );

  assertEquals(result.status, "no_checkpoint", "status");
  assertEquals(result.checkpoint, null, "checkpoint");
  assertEquals(result.can_continue, true, "can_continue");
});

Deno.test("startup: one checkpoint + live verification passes => ready", async () => {
  const state = checkpoint();
  const result = await startXiaoEProject(
    {
      runtimeClient: runtimeReturning(state),
      verifyLiveSourceOfTruth: verifierReturning({ ok: true }),
    },
    " xiaoe_core_v2 ",
  );

  assertEquals(result.status, "ready", "status");
  assertEquals(result.project_key, "xiaoe_core_v2", "normalized project key");
  assertEquals(result.checkpoint?.id, state.id, "restored checkpoint id");
  assertEquals(result.can_continue, true, "can_continue");
});

Deno.test("startup: duplicate current project state is fail-closed by runtime helper", async () => {
  let verifierCalled = false;

  try {
    await startXiaoEProject(
      {
        runtimeClient: runtimeThrowing(
          "multiple active current_project_state records detected",
        ),
        verifyLiveSourceOfTruth: async () => {
          verifierCalled = true;
          return { ok: true };
        },
      },
      "xiaoe_core_v2",
    );
    throw new Error("expected startup to throw");
  } catch (error) {
    assert(
      error instanceof Error &&
        error.message.includes("multiple active current_project_state"),
      "duplicate state error is surfaced",
    );
  }

  assertEquals(verifierCalled, false, "verifier must not run after ambiguous restore");
});

Deno.test("startup: live verification failure => blocked and cannot continue", async () => {
  const state = checkpoint();
  const result = await startXiaoEProject(
    {
      runtimeClient: runtimeReturning(state),
      verifyLiveSourceOfTruth: verifierReturning({
        ok: false,
        reason: "github_head_changed_since_checkpoint",
        checks: { checkpoint_head: "abc", live_head: "def" },
      }),
    },
    "xiaoe_core_v2",
  );

  assertEquals(result.status, "verification_blocked", "status");
  assertEquals(result.can_continue, false, "can_continue");
  assertEquals(
    result.verification?.reason,
    "github_head_changed_since_checkpoint",
    "block reason",
  );
});

Deno.test("startup: stale checkpoint + changed live truth is not trusted", async () => {
  const stale = checkpoint("Next step: merge branch old-feature");
  let observedCheckpointContent = "";

  const result = await startXiaoEProject(
    {
      runtimeClient: runtimeReturning(stale),
      verifyLiveSourceOfTruth: async ({ checkpoint }) => {
        observedCheckpointContent = checkpoint?.content ?? "";
        return {
          ok: false,
          reason: "checkpoint_stale_live_state_changed",
          checks: {
            checkpoint_instruction: checkpoint?.content,
            live_state: "old-feature already merged",
          },
        };
      },
    },
    "xiaoe_core_v2",
  );

  assert(
    observedCheckpointContent.includes("merge branch old-feature"),
    "verifier receives checkpoint as context",
  );
  assertEquals(result.status, "verification_blocked", "stale state blocks continuation");
  assertEquals(result.can_continue, false, "no automatic replay of stale action");
});

Deno.test("startup: repeated activation is stable and read-only", async () => {
  const state = checkpoint();
  let restoreCalls = 0;
  let verificationCalls = 0;

  const runtimeClient = {
    readCurrentProjectState: async () => {
      restoreCalls += 1;
      return state;
    },
  } as unknown as XiaoERuntimeClient;

  const verifyLiveSourceOfTruth = async () => {
    verificationCalls += 1;
    return { ok: true };
  };

  const first = await startXiaoEProject(
    { runtimeClient, verifyLiveSourceOfTruth },
    "xiaoe_core_v2",
  );
  const second = await startXiaoEProject(
    { runtimeClient, verifyLiveSourceOfTruth },
    "xiaoe_core_v2",
  );

  assertEquals(first.status, "ready", "first startup");
  assertEquals(second.status, "ready", "second startup");
  assertEquals(first.checkpoint?.id, second.checkpoint?.id, "same checkpoint");
  assertEquals(restoreCalls, 2, "each startup re-reads durable state");
  assertEquals(verificationCalls, 2, "each startup re-verifies live state");
});

Deno.test("startup: blank project key is rejected before restore", async () => {
  let restoreCalled = false;

  try {
    await startXiaoEProject(
      {
        runtimeClient: {
          readCurrentProjectState: async () => {
            restoreCalled = true;
            return null;
          },
        } as unknown as XiaoERuntimeClient,
        verifyLiveSourceOfTruth: verifierReturning({ ok: true }),
      },
      "   ",
    );
    throw new Error("expected blank project key rejection");
  } catch (error) {
    assert(
      error instanceof Error && error.message === "projectKey required",
      "blank project key error",
    );
  }

  assertEquals(restoreCalled, false, "restore not called for invalid project key");
});
