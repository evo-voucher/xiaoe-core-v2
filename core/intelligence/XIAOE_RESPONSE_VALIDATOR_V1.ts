export interface XiaoEValidationInput {
  projectKey: string;
  responseText: string;
  verifiedFactIds?: string[];
  requestedProjectKey?: string | null;
  requestsProductionWrite?: boolean;
  productionWriteApproved?: boolean;
  containsUnverifiedClaim?: boolean;
  containsSecret?: boolean;
}

export interface XiaoEValidationResult {
  ok: boolean;
  reasons: string[];
}

export function validateXiaoEResponse(input: XiaoEValidationInput): XiaoEValidationResult {
  const reasons: string[] = [];
  const projectKey = input.projectKey.trim();
  const responseText = input.responseText.trim();

  if (!projectKey) reasons.push("project_key_missing");
  if (!responseText) reasons.push("response_empty");

  if (
    input.requestedProjectKey &&
    input.requestedProjectKey.trim() &&
    input.requestedProjectKey.trim() !== projectKey
  ) {
    reasons.push("project_scope_mismatch");
  }

  if (input.requestsProductionWrite === true && input.productionWriteApproved !== true) {
    reasons.push("production_write_not_approved");
  }

  if (input.containsUnverifiedClaim === true) {
    reasons.push("unverified_claim_presented_as_fact");
  }

  if (input.containsSecret === true) {
    reasons.push("secret_exposure_detected");
  }

  return {
    ok: reasons.length === 0,
    reasons,
  };
}

// This validator is intentionally conservative.
// It does not grant execution permission and does not mutate any system.
// Runtime and Security remain authoritative for actual tool execution.
