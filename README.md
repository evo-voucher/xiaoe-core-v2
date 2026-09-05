# xiaoe-core-md
XiaoE AI Core v4.1 - Memory, Behavior, Runtime, Governance and AI Router

Active repository: `Xiao-E-26/xiaoe-core-md`

## Migration readiness

Status: **READY — Fresh Rebuild Core Verified**
Verification mode: isolated fresh-project rebuild + live validation
Stable project key: `xiaoe_core_v2`

Start here:
- Full migration guide: [`MIGRATION_GUIDE_FULL.md`](./MIGRATION_GUIDE_FULL.md)
- Latest verification report: [`MIGRATION_VERIFICATION_REPORT.md`](./MIGRATION_VERIFICATION_REPORT.md)
- Historical provenance: [`architecture/PROVENANCE.md`](./architecture/PROVENANCE.md)

Fresh rebuild has been completed successfully on a separate brand-new Supabase project. `VERIFIED READY` is reserved for completion of the remaining end-to-end HTTP transport/auth test against `memory-gateway` using both a valid destination JWT and runtime key.

## Strict project resolution

XiaoE must identify and lock the correct project before reading files, returning URLs, or making changes.

- Canonical registry: [`registry/PROJECT_REGISTRY.json`](./registry/PROJECT_REGISTRY.json)
- Resolution policy: [`governance/PROJECT_RESOLUTION_POLICY.md`](./governance/PROJECT_RESOLUTION_POLICY.md)
- Mode: **STRICT — verify, never guess**
- Ambiguous project identity: stop and ask the user
- Cross-project work: requires explicit source and destination
- Verification-only Supabase projects must never be returned as production projects
