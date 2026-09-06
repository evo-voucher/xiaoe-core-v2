# xiaoe-core-v2

XiaoE AI Core v4.1 — Memory, Behavior, Runtime, Governance and AI Orchestrator.

Canonical repository: `evo-voucher/xiaoe-core-v2`  
Canonical Supabase project: `iovazhaxsllwgihblsfy`  
Architecture: `memory_fusion_v3_plus_governance_v4_1`

## Runtime status

Status: **VERIFIED READY**  
Verified on: **2026-09-06**

The live `memory-gateway v4` and `project-resolver v3` path passed end-to-end checks with JWT, Runtime Key, scope gate, RPC, memory and context. Invalid credentials and an unauthorized write were rejected. Runtime credentials remain protected by Supabase Vault; the database stores only the SHA-256 token hash.

## Protected baseline

- Runtime client: `chatgpt_xiaoe_runtime`
- Runtime scopes: `memory:read`, `memory:write`, `project:state`
- Protected layers: 8, including `runtime_transport`
- Canonical registries: `registry/PROJECT_REGISTRY.json` and `registry/RESOURCE_AUTH_REGISTRY.json`
- Canonical resolver: `supabase/functions/_shared/project-resolver.ts`
- Latest security hardening source: `supabase/migrations/013_runtime_security_anomaly_exec_hardening.sql`

## Operating rules

- **FACT FIRST / OWNER FIRST / SCOPE FIRST**
- Resolve and lock the project before reading, writing or returning links.
- Production writes require an explicit target lock and owner approval.
- Cross-project copy requires explicit source and destination; source stays immutable by default.
- Secrets are never copied.
- Two consecutive failures require STOP and diagnosis.

See [`SELECTIVE_FUSION_REPORT_2026-09-06.md`](./SELECTIVE_FUSION_REPORT_2026-09-06.md) for the package integration boundary and verification record.
