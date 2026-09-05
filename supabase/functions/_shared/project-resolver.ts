export type ProjectStatus = "active" | "inactive_verification";
export type ProjectRole = "primary" | "controlled_external_bridge" | "verification_only";

export interface ProjectRecord {
  projectKey: string;
  displayName: string;
  aliases: string[];
  activationPhrases: string[];
  github: {
    repositoryFullName: string;
    canonicalUrl: string;
    defaultBranch: string;
  };
  supabase: {
    projectId: string;
    projectName: string;
    role: ProjectRole;
  };
  environment?: "primary" | "production" | "stage" | "verification";
  managementMode?: "direct" | "controlled_external_bridge" | "verification_only";
  status: ProjectStatus;
}

export const PROJECTS: readonly ProjectRecord[] = [
  {
    projectKey: "xiaoe_core_v2",
    displayName: "小E",
    aliases: ["小E", "xiaoe", "xiaoe core", "小E核心"],
    activationPhrases: ["小E上线"],
    github: {
      repositoryFullName: "evo-voucher/xiaoe-core-v2",
      canonicalUrl: "https://github.com/evo-voucher/xiaoe-core-v2",
      defaultBranch: "main",
    },
    supabase: {
      projectId: "iovazhaxsllwgihblsfy",
      projectName: "xiaoe-core-v2",
      role: "primary",
    },
    environment: "primary",
    managementMode: "direct",
    status: "active",
  },
  {
    projectKey: "daughter_companion_ai",
    displayName: "小爱",
    aliases: ["小爱", "daughter", "daughter project", "daughter companion ai"],
    activationPhrases: ["小爱上线"],
    github: {
      repositoryFullName: "Xiao-E-26/daughter-companion-ai",
      canonicalUrl: "https://github.com/Xiao-E-26/daughter-companion-ai",
      defaultBranch: "main",
    },
    supabase: {
      projectId: "bnxjlbuohnujgvryttzj",
      projectName: "daughter-companion-ai-v2",
      role: "primary",
    },
    environment: "primary",
    managementMode: "direct",
    status: "active",
  },
  {
    projectKey: "evo_voucher_production",
    displayName: "EVO Voucher Production",
    aliases: ["evo voucher", "evo voucher production", "voucher production", "production voucher"],
    activationPhrases: [],
    github: {
      repositoryFullName: "evo-voucher/evolution-optical-voucher",
      canonicalUrl: "https://github.com/evo-voucher/evolution-optical-voucher",
      defaultBranch: "main",
    },
    supabase: {
      projectId: "xfivcfwexcxsyiylgryn",
      projectName: "external_project_ref:xfivcfwexcxsyiylgryn",
      role: "controlled_external_bridge",
    },
    environment: "production",
    managementMode: "controlled_external_bridge",
    status: "active",
  },
  {
    projectKey: "voucher_stage",
    displayName: "Voucher Stage",
    aliases: ["voucher stage", "stage voucher", "voucher staging"],
    activationPhrases: [],
    github: {
      repositoryFullName: "evo-voucher/voucher-stage-frontend",
      canonicalUrl: "https://github.com/evo-voucher/voucher-stage-frontend",
      defaultBranch: "main",
    },
    supabase: {
      projectId: "tagusbcluzoxueixjmwh",
      projectName: "external_project_ref:tagusbcluzoxueixjmwh",
      role: "controlled_external_bridge",
    },
    environment: "stage",
    managementMode: "controlled_external_bridge",
    status: "active",
  },
  {
    projectKey: "xiaoe_fresh_verify_20260824",
    displayName: "小E Fresh Rebuild Verification",
    aliases: ["fresh verify", "fresh rebuild verify"],
    activationPhrases: [],
    github: {
      repositoryFullName: "Xiao-E-26/xiaoe-core-md",
      canonicalUrl: "https://github.com/Xiao-E-26/xiaoe-core-md",
      defaultBranch: "main",
    },
    supabase: {
      projectId: "hfphfquwflupnazxibnx",
      projectName: "xiaoe-core-fresh-verify-20260824",
      role: "verification_only",
    },
    environment: "verification",
    managementMode: "verification_only",
    status: "inactive_verification",
  },
] as const;

export interface ProjectHints {
  projectKey?: unknown;
  activationPhrase?: unknown;
  alias?: unknown;
  repositoryFullName?: unknown;
  supabaseProjectId?: unknown;
}

export type ResolutionResult =
  | { ok: true; project: ProjectRecord; matchedBy: string[] }
  | {
      ok: false;
      error: "project_not_found" | "ambiguous_project" | "conflicting_project_hints";
      candidates: string[];
    };

const normalise = (value: unknown) =>
  typeof value === "string" ? value.trim().toLocaleLowerCase() : "";

function candidatesFor(field: keyof ProjectHints, raw: unknown): ProjectRecord[] {
  const value = normalise(raw);
  if (!value) return [];

  switch (field) {
    case "projectKey":
      return PROJECTS.filter((p) => normalise(p.projectKey) === value);
    case "activationPhrase":
      return PROJECTS.filter((p) =>
        p.activationPhrases.some((item) => normalise(item) === value)
      );
    case "alias":
      return PROJECTS.filter((p) =>
        p.aliases.some((item) => normalise(item) === value)
      );
    case "repositoryFullName":
      return PROJECTS.filter((p) => normalise(p.github.repositoryFullName) === value);
    case "supabaseProjectId":
      return PROJECTS.filter((p) => normalise(p.supabase.projectId) === value);
  }
}

export function resolveProject(hints: ProjectHints): ResolutionResult {
  const supplied = (Object.keys(hints) as (keyof ProjectHints)[])
    .filter((field) => normalise(hints[field]));

  if (supplied.length === 0) {
    return { ok: false, error: "project_not_found", candidates: [] };
  }

  const matches = supplied.map((field) => ({ field, projects: candidatesFor(field, hints[field]) }));
  const missing = matches.find((match) => match.projects.length === 0);
  if (missing) return { ok: false, error: "project_not_found", candidates: [] };

  const commonKeys = matches
    .map((match) => new Set(match.projects.map((p) => p.projectKey)))
    .reduce((common, current) => new Set([...common].filter((key) => current.has(key))));

  if (commonKeys.size === 0) {
    const candidates = new Set(matches.flatMap((m) => m.projects.map((p) => p.projectKey)));
    return { ok: false, error: "conflicting_project_hints", candidates: [...candidates] };
  }

  if (commonKeys.size > 1) {
    return { ok: false, error: "ambiguous_project", candidates: [...commonKeys] };
  }

  const projectKey = [...commonKeys][0];
  const project = PROJECTS.find((p) => p.projectKey === projectKey);
  if (!project) return { ok: false, error: "project_not_found", candidates: [] };

  return { ok: true, project, matchedBy: matches.map((m) => m.field) };
}

export function validateProjectUrl(project: ProjectRecord, rawUrl: unknown) {
  if (typeof rawUrl !== "string") return false;

  let url: URL;
  try {
    url = new URL(rawUrl);
  } catch {
    return false;
  }

  if (url.protocol !== "https:") return false;

  if (url.hostname === "github.com") {
    const expected = project.github.canonicalUrl.replace(/\/$/, "");
    const actual = url.origin + url.pathname.replace(/\/$/, "");
    return actual === expected || actual.startsWith(expected + "/");
  }

  if (url.hostname.endsWith(".supabase.co")) {
    return url.hostname === `${project.supabase.projectId}.supabase.co`;
  }

  if (url.hostname === "supabase.com") {
    const expectedPrefix = `/dashboard/project/${project.supabase.projectId}`;
    return url.pathname === expectedPrefix || url.pathname.startsWith(expectedPrefix + "/");
  }

  return false;
}

export function publicProjectView(project: ProjectRecord) {
  return {
    project_key: project.projectKey,
    display_name: project.displayName,
    status: project.status,
    environment: project.environment ?? null,
    management_mode: project.managementMode ?? null,
    github: {
      repository_full_name: project.github.repositoryFullName,
      canonical_url: project.github.canonicalUrl,
      default_branch: project.github.defaultBranch,
    },
    supabase: {
      project_id: project.supabase.projectId,
      project_name: project.supabase.projectName,
      role: project.supabase.role,
    },
  };
}
