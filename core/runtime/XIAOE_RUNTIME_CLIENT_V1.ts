export type XiaoEMemoryAction =
  | "read"
  | "save"
  | "update_project_state"
  | "deactivate";

export interface XiaoERuntimeConfig {
  memoryGatewayUrl: string;
  runtimeKey: string;
}

export interface XiaoECurrentProjectState {
  id: string;
  namespace: "project";
  memory_type: "current_project_state";
  title: string;
  content: string;
  importance: number;
  project_key: string;
  source?: string;
  tags?: string[];
  metadata?: Record<string, unknown>;
  is_active: boolean;
  updated_at?: string;
  verification_status?: string;
  confidence?: number;
  last_verified_at?: string | null;
}

export class XiaoERuntimeClient {
  constructor(private readonly config: XiaoERuntimeConfig) {
    if (!config.memoryGatewayUrl) throw new Error("memoryGatewayUrl required");
    if (!config.runtimeKey) throw new Error("runtimeKey required");
  }

  private async call(action: XiaoEMemoryAction, payload: Record<string, unknown>) {
    const response = await fetch(this.config.memoryGatewayUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-XiaoE-Runtime-Key": this.config.runtimeKey,
      },
      body: JSON.stringify({ action, ...payload }),
    });

    const body = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(`XiaoE memory gateway failed: ${response.status}`);
    }
    return body;
  }

  readMemory(input: {
    project_key?: string | null;
    namespace?: string | null;
    min_importance?: number;
    limit?: number;
  } = {}) {
    return this.call("read", input);
  }

  async readCurrentProjectState(projectKey: string): Promise<XiaoECurrentProjectState | null> {
    const normalizedProjectKey = projectKey.trim();
    if (!normalizedProjectKey) throw new Error("projectKey required");

    const body = await this.readMemory({
      project_key: normalizedProjectKey,
      namespace: "project",
      min_importance: 1,
      limit: 100,
    }) as { data?: unknown };

    const rows = Array.isArray(body.data) ? body.data : [];
    const currentStates = rows.filter((row): row is XiaoECurrentProjectState => {
      if (!row || typeof row !== "object") return false;
      const candidate = row as Record<string, unknown>;
      return candidate.namespace === "project"
        && candidate.memory_type === "current_project_state"
        && candidate.project_key === normalizedProjectKey
        && candidate.is_active === true;
    });

    if (currentStates.length > 1) {
      throw new Error("multiple active current_project_state records detected");
    }

    return currentStates[0] ?? null;
  }

  saveMemory(input: {
    namespace: string;
    memory_type: string;
    title: string;
    content: string;
    importance?: number;
    project_key?: string | null;
    organization_id?: string | null;
    user_id?: string | null;
    source?: string;
    tags?: string[];
    metadata?: Record<string, unknown>;
  }) {
    return this.call("save", input);
  }

  updateCurrentProjectState(input: {
    project_key: string;
    content: string;
    importance?: number;
    metadata?: Record<string, unknown>;
    source?: string;
  }) {
    return this.call("update_project_state", input);
  }

  deactivateConflictingMemory(input: {
    namespace: string;
    memory_type: string;
    title: string;
    project_key?: string | null;
    organization_id?: string | null;
    user_id?: string | null;
    exclude_id?: string | null;
  }) {
    return this.call("deactivate", input);
  }
}

// Example construction (runtime/server only):
// const client = new XiaoERuntimeClient({
//   memoryGatewayUrl: Deno.env.get("XIAOE_MEMORY_GATEWAY_URL")!,
//   runtimeKey: Deno.env.get("XIAOE_RUNTIME_KEY")!,
// });
//
// Resume flow:
// const currentState = await client.readCurrentProjectState("xiaoe_core_v2");
// // Treat the returned checkpoint as continuation context, then verify live Source of Truth
// // before any material mutation. A checkpoint is not permission to trust stale state blindly.
//
// Never hardcode XIAOE_RUNTIME_KEY and never expose it in browser JavaScript.
