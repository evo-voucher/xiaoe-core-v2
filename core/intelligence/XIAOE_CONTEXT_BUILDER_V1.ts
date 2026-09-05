export interface XiaoEContextSource {
  id: string;
  kind: "verified_fact" | "checkpoint" | "memory" | "behavior_rule" | "tool_state";
  projectKey?: string | null;
  content: string;
  verified?: boolean;
  updatedAt?: string | null;
}

export interface XiaoEContextBuildInput {
  projectKey: string;
  objective: string;
  owner?: string | null;
  sources: XiaoEContextSource[];
}

export interface XiaoEContextBundle {
  projectKey: string;
  objective: string;
  owner: string | null;
  verifiedFacts: XiaoEContextSource[];
  behaviorRules: XiaoEContextSource[];
  checkpoint: XiaoEContextSource | null;
  memories: XiaoEContextSource[];
  toolState: XiaoEContextSource[];
  excludedSourceIds: string[];
}

function requireText(value: string, field: string): string {
  const normalized = value.trim();
  if (!normalized) throw new Error(`${field} required`);
  return normalized;
}

export function buildXiaoEContext(input: XiaoEContextBuildInput): XiaoEContextBundle {
  const projectKey = requireText(input.projectKey, "projectKey");
  const objective = requireText(input.objective, "objective");

  const included = input.sources.filter((source) => {
    if (source.kind === "behavior_rule") return true;
    return source.projectKey === projectKey;
  });

  const excludedSourceIds = input.sources
    .filter((source) => !included.includes(source))
    .map((source) => source.id);

  const verifiedFacts = included.filter(
    (source) => source.kind === "verified_fact" && source.verified === true,
  );

  const checkpoints = included
    .filter((source) => source.kind === "checkpoint")
    .sort((a, b) => (b.updatedAt ?? "").localeCompare(a.updatedAt ?? ""));

  return {
    projectKey,
    objective,
    owner: input.owner?.trim() || null,
    verifiedFacts,
    behaviorRules: included.filter((source) => source.kind === "behavior_rule"),
    checkpoint: checkpoints[0] ?? null,
    memories: included.filter((source) => source.kind === "memory"),
    toolState: included.filter((source) => source.kind === "tool_state"),
    excludedSourceIds,
  };
}

// Stability rules:
// 1. Project-scoped context is isolated by projectKey.
// 2. Behavior rules are global and may cross project scope.
// 3. Only explicitly verified facts enter verifiedFacts.
// 4. Checkpoint is continuation context, not live truth.
// 5. The newest checkpoint is selected deterministically.
