import {
  buildXiaoEContext,
  XiaoEContextBuildInput,
  XiaoEContextBundle,
} from "./XIAOE_CONTEXT_BUILDER_V1.ts";
import {
  validateXiaoEResponse,
  XiaoEValidationInput,
  XiaoEValidationResult,
} from "./XIAOE_RESPONSE_VALIDATOR_V1.ts";

export interface XiaoEModelExecutionInput {
  context: XiaoEContextBundle;
}

export interface XiaoEModelExecutionOutput {
  responseText: string;
  requestedProjectKey?: string | null;
  requestsProductionWrite?: boolean;
  productionWriteApproved?: boolean;
  containsUnverifiedClaim?: boolean;
  containsSecret?: boolean;
}

export interface XiaoEIntelligenceBoundaryDependencies {
  executeModel: (
    input: XiaoEModelExecutionInput,
  ) => Promise<XiaoEModelExecutionOutput>;
}

export interface XiaoEIntelligenceBoundaryInput extends XiaoEContextBuildInput {}

export interface XiaoEIntelligenceBoundaryResult {
  context: XiaoEContextBundle;
  modelOutput: XiaoEModelExecutionOutput;
  validation: XiaoEValidationResult;
  canRelease: boolean;
}

/**
 * Canonical Intelligence / Model execution boundary.
 *
 * Sequence:
 *   1. Build project-scoped context.
 *   2. Execute the injected model adapter.
 *   3. Validate the model result before it can be released downstream.
 *
 * This boundary deliberately does NOT execute tools, mutate Production,
 * own credentials, or bypass Runtime / Security authorization.
 */
export async function executeXiaoEIntelligenceBoundary(
  dependencies: XiaoEIntelligenceBoundaryDependencies,
  input: XiaoEIntelligenceBoundaryInput,
): Promise<XiaoEIntelligenceBoundaryResult> {
  const context = buildXiaoEContext(input);
  const modelOutput = await dependencies.executeModel({ context });

  const validationInput: XiaoEValidationInput = {
    projectKey: context.projectKey,
    responseText: modelOutput.responseText,
    requestedProjectKey: modelOutput.requestedProjectKey,
    requestsProductionWrite: modelOutput.requestsProductionWrite,
    productionWriteApproved: modelOutput.productionWriteApproved,
    containsUnverifiedClaim: modelOutput.containsUnverifiedClaim,
    containsSecret: modelOutput.containsSecret,
  };

  const validation = validateXiaoEResponse(validationInput);

  return {
    context,
    modelOutput,
    validation,
    canRelease: validation.ok,
  };
}

// Runtime rule:
// A caller must treat canRelease=false as a hard stop for downstream execution.
// The model adapter is replaceable; XiaoE remains the owner of context and release policy.
