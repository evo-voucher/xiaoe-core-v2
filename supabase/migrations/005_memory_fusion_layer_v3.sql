-- XiaoE Memory Fusion Layer v3
-- Backward-compatible extension of the v2.1 memory architecture.

alter table public.memories
  add column if not exists verification_status text not null default 'verified',
  add column if not exists confidence smallint not null default 8,
  add column if not exists source_priority smallint not null default 50,
  add column if not exists last_verified_at timestamptz,
  add column if not exists valid_until timestamptz,
  add column if not exists supersedes_id uuid references public.memories(id),
  add column if not exists memory_key text;

alter table public.memories
  add constraint memories_verification_status_check check (verification_status in ('candidate','verified','disputed','deprecated')),
  add constraint memories_confidence_check check (confidence between 1 and 10),
  add constraint memories_source_priority_check check (source_priority between 0 and 100);

update public.memories
set last_verified_at = coalesce(last_verified_at, updated_at),
    memory_key = coalesce(memory_key, md5(concat_ws('|', namespace, memory_type, coalesce(project_key,''), lower(btrim(title)))))
where last_verified_at is null or memory_key is null;

create index if not exists memories_fusion_scope_idx
  on public.memories (is_active, verification_status, project_key, namespace, importance desc, updated_at desc);
create index if not exists memories_memory_key_idx on public.memories (memory_key) where is_active = true;
create index if not exists memories_tags_gin_idx on public.memories using gin (tags);

create table if not exists public.task_context_packs (
  id uuid primary key default gen_random_uuid(),
  project_key text,
  task_type text not null default 'general',
  user_intent text not null,
  risk_level text not null default 'low' check (risk_level in ('low','medium','high','critical')),
  status text not null default 'open' check (status in ('open','executing','blocked','completed','abandoned')),
  requested_tags text[] not null default '{}',
  memory_ids uuid[] not null default '{}',
  conflict_memory_ids uuid[] not null default '{}',
  source_checks jsonb not null default '{}'::jsonb,
  context_pack jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  closed_at timestamptz
);

alter table public.task_context_packs enable row level security;
revoke all on table public.task_context_packs from public, anon, authenticated;
grant select, insert, update, delete on table public.task_context_packs to service_role;
create index if not exists task_context_packs_project_status_idx on public.task_context_packs (project_key, status, updated_at desc);

create or replace function public.service_fusion_retrieve(
  p_query text default null,
  p_project_key text default null,
  p_tags text[] default '{}',
  p_namespaces text[] default null,
  p_min_importance smallint default 1,
  p_limit integer default 20
)
returns table (
  memory_id uuid, namespace text, memory_type text, title text, content text,
  importance smallint, project_key text, source text, tags text[], metadata jsonb,
  confidence smallint, verification_status text, last_verified_at timestamptz,
  score numeric, match_reasons text[]
)
language sql security definer set search_path = public
as $$
  with ranked as (
    select m.*,
      ((m.importance::numeric * 10) + (m.confidence::numeric * 4) + (m.source_priority::numeric * 0.25)
       + case when p_project_key is not null and m.project_key = p_project_key then 30 else 0 end
       + case when m.namespace in ('global','core') then 18 else 0 end
       + case when coalesce(array_length(p_tags,1),0) > 0 and m.tags && p_tags then 20 else 0 end
       + case when nullif(btrim(p_query),'') is not null and lower(m.title) like '%' || lower(btrim(p_query)) || '%' then 24 else 0 end
       + case when nullif(btrim(p_query),'') is not null and lower(m.content) like '%' || lower(btrim(p_query)) || '%' then 12 else 0 end
       + case when m.last_verified_at >= now() - interval '30 days' then 4 else 0 end) as fusion_score,
      array_remove(array[
        case when p_project_key is not null and m.project_key = p_project_key then 'project_exact' end,
        case when m.namespace in ('global','core') then 'core_context' end,
        case when coalesce(array_length(p_tags,1),0) > 0 and m.tags && p_tags then 'tag_overlap' end,
        case when nullif(btrim(p_query),'') is not null and lower(m.title) like '%' || lower(btrim(p_query)) || '%' then 'title_match' end,
        case when nullif(btrim(p_query),'') is not null and lower(m.content) like '%' || lower(btrim(p_query)) || '%' then 'content_match' end,
        case when m.last_verified_at >= now() - interval '30 days' then 'recently_verified' end
      ], null) as reasons
    from public.memories m
    where m.is_active = true
      and m.verification_status = 'verified'
      and (m.valid_until is null or m.valid_until > now())
      and m.importance >= greatest(1, least(coalesce(p_min_importance,1),10))
      and (p_project_key is null or m.project_key = p_project_key or m.project_key is null)
      and (p_namespaces is null or m.namespace = any(p_namespaces))
  )
  select r.id,r.namespace,r.memory_type,r.title,r.content,r.importance,r.project_key,r.source,r.tags,r.metadata,
         r.confidence,r.verification_status,r.last_verified_at,r.fusion_score,r.reasons
  from ranked r
  order by r.fusion_score desc, r.updated_at desc
  limit greatest(1, least(coalesce(p_limit,20),100));
$$;

create or replace function public.service_find_memory_conflicts(p_project_key text default null)
returns table(memory_id uuid, conflicting_memory_id uuid, reason text)
language sql security definer set search_path = public
as $$
  select a.id,b.id,'duplicate_active_memory_key'::text
  from public.memories a join public.memories b on a.id < b.id and a.memory_key = b.memory_key
  where a.is_active and b.is_active and a.memory_key is not null
    and (p_project_key is null or a.project_key = p_project_key or b.project_key = p_project_key)
  union all
  select m.id,s.id,'superseded_record_still_active'::text
  from public.memories m join public.memories s on s.id = m.supersedes_id
  where m.is_active and s.is_active
    and (p_project_key is null or m.project_key = p_project_key or s.project_key = p_project_key);
$$;

revoke all on function public.service_fusion_retrieve(text,text,text[],text[],smallint,integer) from public, anon, authenticated;
revoke all on function public.service_find_memory_conflicts(text) from public, anon, authenticated;
grant execute on function public.service_fusion_retrieve(text,text,text[],text[],smallint,integer) to service_role;
grant execute on function public.service_find_memory_conflicts(text) to service_role;
