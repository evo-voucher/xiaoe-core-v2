import { createClient } from "npm:@supabase/supabase-js@2";
import {
  publicProjectView,
  resolveProject,
  validateProjectUrl,
} from "../_shared/project-resolver.ts";

const headers = { "Content-Type": "application/json; charset=utf-8" };
const reply = (status: number, body: unknown) =>
  new Response(JSON.stringify(body), { status, headers });

Deno.serve(async (req: Request) => {
  if (req.method !== "POST") return reply(405, { error: "method_not_allowed" });

  const runtimeKey = req.headers.get("X-XiaoE-Runtime-Key")?.trim();
  if (!runtimeKey) return reply(401, { error: "missing_runtime_key" });

  const supabaseUrl = Deno.env.get("SUPABASE_URL");
  const serviceRoleKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!supabaseUrl || !serviceRoleKey) {
    return reply(500, { error: "server_configuration_error" });
  }

  const db = createClient(supabaseUrl, serviceRoleKey, {
    auth: { persistSession: false, autoRefreshToken: false },
  });

  const { data: guardRows, error: guardError } = await db.rpc(
    "service_runtime_security_check",
    { p_token: runtimeKey, p_required_scope: "project:state", p_endpoint: "project-resolver" },
  );

  if (guardError) {
    console.error("runtime security guard error", guardError.message);
    return reply(500, { error: "runtime_validation_failed" });
  }

  const guard = Array.isArray(guardRows) ? guardRows[0] : null;
  if (!guard?.allowed) {
    if (guard?.reason === "rate_limited") {
      return reply(429, { error: "rate_limited", retry_after_seconds: guard.retry_after_seconds ?? 60 });
    }
    return reply(403, { error: "forbidden" });
  }

  let body: Record<string, unknown>;
  try {
    body = await req.json();
  } catch {
    return reply(400, { error: "invalid_json" });
  }

  const resolution = resolveProject({
    projectKey: body.project_key,
    activationPhrase: body.activation_phrase,
    alias: body.project_alias,
    repositoryFullName: body.repository_full_name,
    supabaseProjectId: body.supabase_project_id,
  });

  if (!resolution.ok) {
    const status = resolution.error === "project_not_found" ? 404 : 409;
    return reply(status, {
      ok: false,
      error: resolution.error,
      candidates: resolution.candidates,
      requires_user_confirmation: resolution.error !== "project_not_found",
    });
  }

  if (body.url != null && !validateProjectUrl(resolution.project, body.url)) {
    return reply(409, {
      ok: false,
      error: "project_url_mismatch",
      project_lock: publicProjectView(resolution.project),
    });
  }

  return reply(200, {
    ok: true,
    project_lock: publicProjectView(resolution.project),
    matched_by: resolution.matchedBy,
    url_valid: body.url == null ? null : true,
  });
});
