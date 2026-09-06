import { buildXiaoEContext } from "./XIAOE_CONTEXT_BUILDER_V1.ts";
import { validateXiaoEResponse } from "./XIAOE_RESPONSE_VALIDATOR_V1.ts";

function assert(condition: boolean, message: string) {
  if (!condition) throw new Error(message);
}

Deno.test("context builder isolates unrelated project context", () => {
  const result = buildXiaoEContext({
    projectKey: "stage",
    objective: "check health",
    sources: [
      { id: "1", kind: "verified_fact", projectKey: "stage", content: "healthy", verified: true },
      { id: "2", kind: "memory", projectKey: "production", content: "prod memory" },
      { id: "3", kind: "behavior_rule", content: "FACT FIRST" },
    ],
  });

  assert(result.verifiedFacts.length === 1, "expected stage verified fact");
  assert(result.memories.length === 0, "production memory must be excluded");
  assert(result.behaviorRules.length === 1, "global behavior rule should remain");
  assert(result.excludedSourceIds.includes("2"), "excluded source should be traceable");
});

Deno.test("context builder selects latest checkpoint", () => {
  const result = buildXiaoEContext({
    projectKey: "stage",
    objective: "resume work",
    sources: [
      { id: "old", kind: "checkpoint", projectKey: "stage", content: "old", updatedAt: "2026-09-01T00:00:00Z" },
      { id: "new", kind: "checkpoint", projectKey: "stage", content: "new", updatedAt: "2026-09-04T00:00:00Z" },
    ],
  });

  assert(result.checkpoint?.id === "new", "latest checkpoint should win");
});

Deno.test("response validator blocks unapproved production write", () => {
  const result = validateXiaoEResponse({
    projectKey: "production",
    requestedProjectKey: "production",
    responseText: "apply change",
    requestsProductionWrite: true,
    productionWriteApproved: false,
  });

  assert(result.ok === false, "validator must block write");
  assert(result.reasons.includes("production_write_not_approved"), "missing production guard reason");
});

Deno.test("response validator blocks project mismatch", () => {
  const result = validateXiaoEResponse({
    projectKey: "stage",
    requestedProjectKey: "production",
    responseText: "continue",
  });

  assert(result.ok === false, "validator must block project mismatch");
  assert(result.reasons.includes("project_scope_mismatch"), "missing scope mismatch reason");
});
