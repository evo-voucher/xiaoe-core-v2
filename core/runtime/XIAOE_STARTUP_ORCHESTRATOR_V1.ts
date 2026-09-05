import {
  XiaoECurrentProjectState,
  XiaoERuntimeClient,
} from "./XIAOE_RUNTIME_CLIENT_V1.ts";

export type XiaoEStartupStatus =
  | "ready"
  | "no_checkpoint"
  | "verification_blocked";

export interface XiaoELiveVerificationResult {
  ok: boolean;
  verified_at?: string;
  checks?: Record<string, unknown>;
  reason?: string;
}

export interface XiaoEStartupResult {
  status: XiaoEStartupStatus;
  project_key: string;
  checkpoint: XiaoECurrentProjectState | null;
  verification: XiaoELiveVerificationResult | null;
  can_continue: boolean;
}

export interface XiaoEStartupDependencies {
  runtimeClient: XiaoERuntimeClient;
  verifyLiveSourceOfTruth: (input: {
    project_key: string;
    checkpoint: XiaoECurrentProjectState | null;
  }) => Promise<XiaoELiveVerificationResult>;
}

/**
 * Minimal checkpoint-aware startup orchestration for a resolved XiaoE project.
 *
 * Ownership boundaries:
 * - Runtime Client owns transport only.
 * - Current Project State remains the single durable checkpoint payload.
 * - Checkpoint Protocol owns lifecycle semantics.
 * - Context Bridge owns orchestration.
 * - The injected verifier owns project-specific live Source-of-Truth checks.
 *
 * This function deliberately does not infer a project, rank memories, mutate state,
 * or automatically continue after failed verification.
 */
export async function startXiaoEProject(
  dependencies: XiaoEStartupDependencies,
  projectKey: string,
): Promise<XiaoEStartupResult> {
  const normalizedProjectKey = projectKey.trim();
  if (!normalizedProjectKey) throw new Error("projectKey required");

  const checkpoint = await dependencies.runtimeClient.readCurrentProjectState(
    normalizedProjectKey,
  );

  const verification = await dependencies.verifyLiveSourceOfTruth({
    project_key: normalizedProjectKey,
    checkpoint,
  });

  if (!verification.ok) {
    return {
      status: "verification_blocked",
      project_key: normalizedProjectKey,
      checkpoint,
      verification,
      can_continue: false,
    };
  }

  return {
    status: checkpoint ? "ready" : "no_checkpoint",
    project_key: normalizedProjectKey,
    checkpoint,
    verification,
    can_continue: true,
  };
}

// Canonical startup sequence after project identity has already been resolved:
//
//   const startup = await startXiaoEProject(
//     {
//       runtimeClient,
//       verifyLiveSourceOfTruth: async ({ project_key, checkpoint }) => {
//         // Project-specific verifier checks GitHub / Supabase / runtime only where
//         // the resumed task actually depends on changeable or high-risk state.
//         return { ok: true, checks: { project_key, checkpoint_present: !!checkpoint } };
//       },
//     },
//     "xiaoe_core_v2",
//   );
//
//   if (!startup.can_continue) {
//     // Stop mutation. Resolve the verification conflict first.
//   }
//
// This file intentionally does not create a second checkpoint store or format.
