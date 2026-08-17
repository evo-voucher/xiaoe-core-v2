import { createClient } from "npm:@supabase/supabase-js@2";

const jsonHeaders = { "Content-Type": "application/json; charset=utf-8" };

function response(status: number, body: unknown) {
  return new Response(JSON.stringify(body), { status, headers: jsonHeaders });
}

Deno.serve(async (req: Request) => {
  if (req.method !== "POST") return response(405, { error: "method_not_allowed" });

  const runtimeKey = req.headers.get("X-XiaoE-Runtime-Key")?.trim();
  if (!runtimeKey) return response(401, { error: "missing_runtime_key" });

  const supabaseUrl = Deno.env.get("SUPABASE_URL");
  const serviceRoleKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!supabaseUrl || !serviceRoleKey) return response(500, { error: "server_configuration_error" });

  const db = createClient(supabaseUrl, serviceRoleKey, {
    auth: { persistSession: false, autoRefreshToken: false },
  });

  let body: Record<string, unknown>;
  try { body = await req.json(); }
  catch { return response(400, { error: "invalid_json" }); }

  const action = typeof body.action === "string" ? body.action : "";
  const readActions = new Set(["read", "fusion_read", "conflicts"]);
  const writeActions = new Set(["save", "save_v2", "deactivate"]);
  const projectActions = new Set(["update_project_state", "create_context", "close_context"]);

  const requiredScope = readActions.has(action)
    ? "memory:read"
    : writeActions.has(action)
    ? "memory:write"
    : projectActions.has(action)
    ? "project:state"
    : null;

  if (!requiredScope) return response(400, { error: "invalid_action" });

  const { data: identityRows, error: identityError } = await db.rpc(
    "service_validate_runtime_client",
    { p_token: runtimeKey, p_required_scope: requiredScope },
  );

  if (identityError) {
    console.error("runtime validation error", identityError.message);
    return response(500, { error: "runtime_validation_failed" });
  }

  const identity = Array.isArray(identityRows) ? identityRows[0] : null;
  if (!identity?.valid) return response(403, { error: "forbidden" });

  try {
    if (action === "read") {
      const { data, error } = await db.rpc("service_read_memories", {
        p_project_key: body.project_key ?? null,
        p_namespace: body.namespace ?? null,
        p_min_importance: body.min_importance ?? 1,
        p_limit: body.limit ?? 100,
      });
      if (error) throw error;
      return response(200, { ok: true, mode: "legacy", data });
    }

    if (action === "fusion_read") {
      const { data, error } = await db.rpc("service_fusion_retrieve", {
        p_query: body.query ?? null,
        p_project_key: body.project_key ?? null,
        p_tags: body.tags ?? [],
        p_namespaces: body.namespaces ?? null,
        p_min_importance: body.min_importance ?? 1,
        p_limit: body.limit ?? 20,
      });
      if (error) throw error;
      return response(200, { ok: true, mode: "fusion_v3", data });
    }

    if (action === "conflicts") {
      const { data, error } = await db.rpc("service_find_memory_conflicts", {
        p_project_key: body.project_key ?? null,
      });
      if (error) throw error;
      return response(200, { ok: true, data });
    }

    if (action === "save") {
      const { data, error } = await db.rpc("service_save_memory", {
        p_namespace: body.namespace,
        p_memory_type: body.memory_type,
        p_title: body.title,
        p_content: body.content,
        p_importance: body.importance ?? 5,
        p_project_key: body.project_key ?? null,
        p_organization_id: body.organization_id ?? null,
        p_user_id: body.user_id ?? null,
        p_source: body.source ?? "xiaoe-runtime",
        p_tags: body.tags ?? [],
        p_metadata: body.metadata ?? {},
      });
      if (error) throw error;
      return response(200, { ok: true, mode: "legacy", data });
    }

    if (action === "save_v2") {
      const { data, error } = await db.rpc("service_save_memory_v2", {
        p_namespace: body.namespace,
        p_memory_type: body.memory_type,
        p_title: body.title,
        p_content: body.content,
        p_importance: body.importance ?? 5,
        p_project_key: body.project_key ?? null,
        p_organization_id: body.organization_id ?? null,
        p_user_id: body.user_id ?? null,
        p_source: body.source ?? "xiaoe-runtime",
        p_tags: body.tags ?? [],
        p_metadata: body.metadata ?? {},
        p_confidence: body.confidence ?? 8,
        p_source_priority: body.source_priority ?? 50,
        p_verification_status: body.verification_status ?? "verified",
        p_valid_until: body.valid_until ?? null,
        p_supersedes_id: body.supersedes_id ?? null,
      });
      if (error) throw error;
      return response(200, { ok: true, mode: "fusion_v3", data });
    }

    if (action === "create_context") {
      const { data, error } = await db.rpc("service_create_task_context_pack", {
        p_user_intent: body.user_intent,
        p_project_key: body.project_key ?? null,
        p_task_type: body.task_type ?? "general",
        p_risk_level: body.risk_level ?? "low",
        p_tags: body.tags ?? [],
        p_source_checks: body.source_checks ?? {},
        p_limit: body.limit ?? 20,
      });
      if (error) throw error;
      return response(200, { ok: true, data });
    }

    if (action === "close_context") {
      const { data, error } = await db.rpc("service_close_task_context_pack", {
        p_id: body.id,
        p_status: body.status ?? "completed",
        p_source_checks: body.source_checks ?? null,
      });
      if (error) throw error;
      return response(200, { ok: true, data });
    }

    if (action === "update_project_state") {
      const { data, error } = await db.rpc("service_update_current_project_state", {
        p_project_key: body.project_key,
        p_content: body.content,
        p_importance: body.importance ?? 10,
        p_metadata: body.metadata ?? {},
        p_source: body.source ?? "xiaoe-runtime",
      });
      if (error) throw error;
      return response(200, { ok: true, data });
    }

    if (action === "deactivate") {
      const { data, error } = await db.rpc("service_deactivate_conflicting_memory", {
        p_namespace: body.namespace,
        p_memory_type: body.memory_type,
        p_title: body.title,
        p_project_key: body.project_key ?? null,
        p_organization_id: body.organization_id ?? null,
        p_user_id: body.user_id ?? null,
        p_exclude_id: body.exclude_id ?? null,
      });
      if (error) throw error;
      return response(200, { ok: true, deactivated: data });
    }

    return response(400, { error: "invalid_action" });
  } catch (error) {
    const message = error instanceof Error ? error.message : "unknown_error";
    console.error("memory gateway action failed", message);
    return response(500, { error: "memory_action_failed" });
  }
});
