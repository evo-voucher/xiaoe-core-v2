-- Recovered from active Supabase migration history on 2026-08-23.
-- Source migration: 20260822133153 / xiaoe_core_v4_1_governance

create table if not exists public.xiaoe_system_meta (
  system_key text primary key,
  version text not null,
  architecture text not null,
  status text not null default 'active' check (status in ('active','paused','deprecated')),
  capabilities jsonb not null default '{}'::jsonb,
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.xiaoe_policy_rules (
  rule_key text primary key,
  category text not null,
  description text not null,
  rule_config jsonb not null default '{}'::jsonb,
  severity text not null default 'medium' check (severity in ('low','medium','high','critical')),
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.xiaoe_protected_layers (
  id uuid primary key default gen_random_uuid(),
  project_key text not null,
  layer_key text not null,
  evidence jsonb not null default '{}'::jsonb,
  notes text,
  status text not null default 'protected' check (status in ('protected','reopened','retired')),
  verified_at timestamptz not null default now(),
  reopened_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(project_key, layer_key)
);

create table if not exists public.xiaoe_learning_promotions (
  id uuid primary key default gen_random_uuid(),
  memory_id uuid not null references public.memories(id) on delete cascade,
  project_key text,
  promotion_status text not null default 'candidate' check (promotion_status in ('candidate','promoted','rejected')),
  reason text,
  review_data jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  reviewed_at timestamptz,
  promoted_at timestamptz,
  unique(memory_id)
);

alter table public.xiaoe_system_meta enable row level security;
alter table public.xiaoe_policy_rules enable row level security;
alter table public.xiaoe_protected_layers enable row level security;
alter table public.xiaoe_learning_promotions enable row level security;

revoke all on table public.xiaoe_system_meta from anon, authenticated;
revoke all on table public.xiaoe_policy_rules from anon, authenticated;
revoke all on table public.xiaoe_protected_layers from anon, authenticated;
revoke all on table public.xiaoe_learning_promotions from anon, authenticated;

grant all on table public.xiaoe_system_meta to service_role;
grant all on table public.xiaoe_policy_rules to service_role;
grant all on table public.xiaoe_protected_layers to service_role;
grant all on table public.xiaoe_learning_promotions to service_role;

insert into public.xiaoe_system_meta(system_key,version,architecture,status,capabilities,notes)
values (
  'xiaoe_core','4.1.0','memory_fusion_v3_plus_governance_v4_1','active',
  '{"bootstrap_v41":true,"policy_gate":true,"protected_layers":true,"learning_promotion":true,"version_governance":true,"legacy_v3_compatible":true}'::jsonb,
  'v4.1 is an additive governance layer over the active Memory Fusion v3 core. Existing v3 tables and RPCs remain compatible.'
)
on conflict(system_key) do update set
  version=excluded.version,
  architecture=excluded.architecture,
  status='active',
  capabilities=excluded.capabilities,
  notes=excluded.notes,
  updated_at=now();

insert into public.xiaoe_policy_rules(rule_key,category,description,rule_config,severity,is_active) values
('evidence_before_change','engineering','Verify current state before material technical changes.', '{"required_for":["medium","high","critical"]}'::jsonb,'high',true),
('root_before_patch','engineering','Find root cause before adding patches; repeated failure requires reassessment.', '{"same_path_failure_limit":2}'::jsonb,'high',true),
('protect_verified_layer','stability','A verified healthy layer is protected until explicitly reopened.', '{"explicit_reopen_required":true}'::jsonb,'high',true),
('high_risk_approval','approval','High or critical risk changes require explicit human approval.', '{"high_requires":["environment_verified","impact_checked","user_approved"],"critical_adds":["rollback_plan"]}'::jsonb,'critical',true),
('persist_verified_learning','learning','Only verified, reusable, high-value learning may be promoted.', '{"min_importance":8,"min_confidence":8,"verification_status":"verified"}'::jsonb,'medium',true)
on conflict(rule_key) do update set
  category=excluded.category,
  description=excluded.description,
  rule_config=excluded.rule_config,
  severity=excluded.severity,
  is_active=true,
  updated_at=now();

create or replace function public.service_xiaoe_screening()
returns jsonb
language sql
security definer
set search_path=public
as $$
select jsonb_build_object(
  'system', coalesce((select to_jsonb(m) from public.xiaoe_system_meta m where m.system_key='xiaoe_core'),'{}'::jsonb),
  'core_tables', jsonb_build_object(
    'memories', to_regclass('public.memories') is not null,
    'runtime_clients', to_regclass('public.runtime_clients') is not null,
    'task_context_packs', to_regclass('public.task_context_packs') is not null,
    'policy_rules', to_regclass('public.xiaoe_policy_rules') is not null,
    'protected_layers', to_regclass('public.xiaoe_protected_layers') is not null,
    'learning_promotions', to_regclass('public.xiaoe_learning_promotions') is not null
  ),
  'counts', jsonb_build_object(
    'memories', (select count(*) from public.memories),
    'verified_active_memories', (select count(*) from public.memories where is_active=true and verification_status='verified'),
    'open_task_contexts', (select count(*) from public.task_context_packs where status='open'),
    'runtime_clients', (select count(*) from public.runtime_clients where status='active'),
    'protected_layers', (select count(*) from public.xiaoe_protected_layers where status='protected'),
    'promoted_learning', (select count(*) from public.xiaoe_learning_promotions where promotion_status='promoted')
  ),
  'generated_at', now()
);
$$;

create or replace function public.service_policy_gate(
  p_risk_level text,
  p_source_checks jsonb default '{}'::jsonb,
  p_change_scope text[] default '{}'::text[],
  p_project_key text default null
)
returns jsonb
language plpgsql
security definer
set search_path=public
as $$
declare
  v_risk text := lower(coalesce(nullif(btrim(p_risk_level),''),'low'));
  v_env boolean := coalesce(p_source_checks->'environment_verified','false'::jsonb)='true'::jsonb;
  v_impact boolean := coalesce(p_source_checks->'impact_checked','false'::jsonb)='true'::jsonb;
  v_approved boolean := coalesce(p_source_checks->'user_approved','false'::jsonb)='true'::jsonb;
  v_rollback boolean := coalesce(p_source_checks->'rollback_plan','false'::jsonb)='true'::jsonb;
  v_protected integer := 0;
  v_allowed boolean := false;
  v_missing text[] := '{}'::text[];
begin
  if v_risk not in ('low','medium','high','critical') then raise exception 'invalid risk level'; end if;
  if p_project_key is not null and cardinality(coalesce(p_change_scope,'{}'::text[])) > 0 then
    select count(*) into v_protected from public.xiaoe_protected_layers
    where project_key=p_project_key and status='protected' and layer_key=any(p_change_scope);
  end if;
  if v_risk='low' then
    v_allowed := true;
  elsif v_risk='medium' then
    if not v_env then v_missing := array_append(v_missing,'environment_verified'); end if;
    v_allowed := v_env;
  elsif v_risk='high' then
    if not v_env then v_missing := array_append(v_missing,'environment_verified'); end if;
    if not v_impact then v_missing := array_append(v_missing,'impact_checked'); end if;
    if not v_approved then v_missing := array_append(v_missing,'user_approved'); end if;
    v_allowed := v_env and v_impact and v_approved;
  else
    if not v_env then v_missing := array_append(v_missing,'environment_verified'); end if;
    if not v_impact then v_missing := array_append(v_missing,'impact_checked'); end if;
    if not v_approved then v_missing := array_append(v_missing,'user_approved'); end if;
    if not v_rollback then v_missing := array_append(v_missing,'rollback_plan'); end if;
    v_allowed := v_env and v_impact and v_approved and v_rollback;
  end if;
  if v_protected > 0 and not v_approved then
    v_allowed := false;
    if not ('protected_layer_reopen_approval'=any(v_missing)) then
      v_missing := array_append(v_missing,'protected_layer_reopen_approval');
    end if;
  end if;
  return jsonb_build_object(
    'allowed',v_allowed,'risk_level',v_risk,'missing_checks',to_jsonb(v_missing),
    'protected_layer_hits',v_protected,'project_key',p_project_key,
    'change_scope',to_jsonb(coalesce(p_change_scope,'{}'::text[])),
    'evaluated_at',now(),'gate_version','4.1.0'
  );
end;
$$;

create or replace function public.service_protect_layer(
  p_project_key text,
  p_layer_key text,
  p_evidence jsonb default '{}'::jsonb,
  p_notes text default null
)
returns public.xiaoe_protected_layers
language plpgsql
security definer
set search_path=public
as $$
declare v_row public.xiaoe_protected_layers%rowtype;
begin
  if nullif(btrim(p_project_key),'') is null or nullif(btrim(p_layer_key),'') is null then raise exception 'project_key and layer_key required'; end if;
  insert into public.xiaoe_protected_layers(project_key,layer_key,evidence,notes,status,verified_at,reopened_at,updated_at)
  values (btrim(p_project_key),btrim(p_layer_key),coalesce(p_evidence,'{}'::jsonb),p_notes,'protected',now(),null,now())
  on conflict(project_key,layer_key) do update set evidence=excluded.evidence,notes=excluded.notes,status='protected',verified_at=now(),reopened_at=null,updated_at=now()
  returning * into v_row;
  return v_row;
end;
$$;

create or replace function public.service_reopen_protected_layer(
  p_project_key text,
  p_layer_key text,
  p_reason text,
  p_user_approved boolean default false
)
returns public.xiaoe_protected_layers
language plpgsql
security definer
set search_path=public
as $$
declare v_row public.xiaoe_protected_layers%rowtype;
begin
  if not p_user_approved then raise exception 'explicit user approval required'; end if;
  if nullif(btrim(p_reason),'') is null then raise exception 'reopen reason required'; end if;
  update public.xiaoe_protected_layers
  set status='reopened', reopened_at=now(), notes=concat_ws(E'\n',notes,'REOPEN: '||p_reason), updated_at=now()
  where project_key=p_project_key and layer_key=p_layer_key and status='protected'
  returning * into v_row;
  if not found then raise exception 'protected layer not found'; end if;
  return v_row;
end;
$$;

create or replace function public.service_promote_learning(
  p_memory_id uuid,
  p_reason text,
  p_user_approved boolean default false
)
returns jsonb
language plpgsql
security definer
set search_path=public
as $$
declare
  v_memory public.memories%rowtype;
  v_id uuid;
begin
  if not p_user_approved then raise exception 'explicit user approval required'; end if;
  select * into v_memory from public.memories where id=p_memory_id and is_active=true;
  if not found then raise exception 'memory not found'; end if;
  if v_memory.verification_status <> 'verified' or v_memory.importance < 8 or v_memory.confidence < 8 then
    raise exception 'learning does not meet promotion threshold';
  end if;
  if v_memory.namespace not in ('experience','core','project') then raise exception 'memory namespace is not promotable'; end if;
  insert into public.xiaoe_learning_promotions(memory_id,project_key,promotion_status,reason,review_data,reviewed_at,promoted_at)
  values(v_memory.id,v_memory.project_key,'promoted',p_reason,jsonb_build_object('importance',v_memory.importance,'confidence',v_memory.confidence,'verification_status',v_memory.verification_status),now(),now())
  on conflict(memory_id) do update set promotion_status='promoted',reason=excluded.reason,review_data=excluded.review_data,reviewed_at=now(),promoted_at=now()
  returning id into v_id;
  update public.memories set
    metadata = coalesce(metadata,'{}'::jsonb) || jsonb_build_object('master_promoted',true,'master_promoted_at',now(),'promotion_reason',p_reason),
    updated_at=now()
  where id=v_memory.id;
  return jsonb_build_object('success',true,'promotion_id',v_id,'memory_id',v_memory.id,'promoted_at',now());
end;
$$;

create or replace function public.service_xiaoe_bootstrap_v41(
  p_project_key text default null,
  p_query text default '小E上线'
)
returns jsonb
language sql
security definer
set search_path=public
as $$
select jsonb_build_object(
  'success',true,
  'bootstrap_version','4.1.0',
  'system',(select to_jsonb(m) from public.xiaoe_system_meta m where m.system_key='xiaoe_core'),
  'screening',public.service_xiaoe_screening(),
  'policy_rules',coalesce((select jsonb_agg(to_jsonb(r) order by r.severity desc,r.rule_key) from public.xiaoe_policy_rules r where r.is_active=true),'[]'::jsonb),
  'protected_layers',coalesce((select jsonb_agg(to_jsonb(p) order by p.updated_at desc) from public.xiaoe_protected_layers p where p.status='protected' and (p_project_key is null or p.project_key=p_project_key)),'[]'::jsonb),
  'memories',coalesce((select jsonb_agg(to_jsonb(x) order by x.score desc) from public.service_fusion_retrieve(p_query,p_project_key,'{}'::text[],null::text[],1::smallint,20) x),'[]'::jsonb),
  'conflicts',coalesce((select jsonb_agg(to_jsonb(c)) from public.service_find_memory_conflicts(p_project_key) c),'[]'::jsonb),
  'precedence',jsonb_build_array('current_explicit_user_instruction','live_verified_source','verified_project_memory','verified_core_memory','current_chat_assumption'),
  'generated_at',now()
);
$$;

revoke all on function public.service_xiaoe_screening() from public, anon, authenticated;
revoke all on function public.service_policy_gate(text,jsonb,text[],text) from public, anon, authenticated;
revoke all on function public.service_protect_layer(text,text,jsonb,text) from public, anon, authenticated;
revoke all on function public.service_reopen_protected_layer(text,text,text,boolean) from public, anon, authenticated;
revoke all on function public.service_promote_learning(uuid,text,boolean) from public, anon, authenticated;
revoke all on function public.service_xiaoe_bootstrap_v41(text,text) from public, anon, authenticated;

grant execute on function public.service_xiaoe_screening() to service_role;
grant execute on function public.service_policy_gate(text,jsonb,text[],text) to service_role;
grant execute on function public.service_protect_layer(text,text,jsonb,text) to service_role;
grant execute on function public.service_reopen_protected_layer(text,text,text,boolean) to service_role;
grant execute on function public.service_promote_learning(uuid,text,boolean) to service_role;
grant execute on function public.service_xiaoe_bootstrap_v41(text,text) to service_role;
