import {
  executeXiaoEIntelligenceBoundary,
} from "./XIAOE_INTELLIGENCE_EXECUTION_BOUNDARY_V1.ts";

Deno.test("intelligence boundary builds scoped context and releases valid response", async () => {
  const result = await executeXiaoEIntelligenceBoundary(
    {
      executeModel: async ({ context }) => ({
        responseText: `Project ${context.projectKey} ready`,
        requestedProjectKey: context.projectKey,
      }),
    },
    {
      projectKey: "stage_voucher",
      objective: "Check stage voucher health",
      sources: [
        {
          id: "stage-fact",
          kind: "verified_fact",
          projectKey: "stage_voucher",
          content: "Stage health is green",
          verified: true,
        },
        {
          id: "prod-memory",
          kind: "memory",
          projectKey: "production_voucher",
          content: "Unrelated production context",
        },
      ],
    },
  );

  if (!result.canRelease) throw new Error("expected valid response to be releasable");
  if (!result.context.excludedSourceIds.includes("prod-memory")) {
    throw new Error("expected unrelated project context to be excluded");
  }
});

Deno.test("intelligence boundary blocks unapproved production write", async () => {
  const result = await executeXiaoEIntelligenceBoundary(
    {
      executeModel: async () => ({
        responseText: "Write to Production now",
        requestsProductionWrite: true,
        productionWriteApproved: false,
      }),
    },
    {
      projectKey: "production_voucher",
      objective: "Prepare safe production change",
      sources: [],
    },
  );

  if (result.canRelease) throw new Error("expected production write to be blocked");
  if (!result.validation.reasons.includes("production_write_not_approved")) {
    throw new Error("expected production approval validation reason");
  }
});

Deno.test("intelligence boundary blocks project mismatch", async () => {
  const result = await executeXiaoEIntelligenceBoundary(
    {
      executeModel: async () => ({
        responseText: "Switch projects",
        requestedProjectKey: "production_voucher",
      }),
    },
    {
      projectKey: "stage_voucher",
      objective: "Stay inside stage scope",
      sources: [],
    },
  );

  if (result.canRelease) throw new Error("expected project mismatch to be blocked");
  if (!result.validation.reasons.includes("project_scope_mismatch")) {
    throw new Error("expected project scope mismatch reason");
  }
});
