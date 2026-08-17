-- XiaoE Memory Fusion v3 service layer

create or replace function public.service_save_memory_v2(
  p_namespace text,
  p_memory_type text,
  p_title text,
  p_content text,
  p_importance smallint default 5,
  p_project_key text default null,
  p_organization_id uuid default null,
  p_user_id uuid default null,
  p_source text default 'xiaoe',
  p_tags text[] default '{}',
  p_metadata jsonb default '{}'::jsonb,
  p_confidence smallint default 8,
  p_source_priority smallint default 50,
  p_verification_status text default 'verified',
  p_valid_until timestamptz default null,
  p_supersedes_id uuid default null
)
returns public.memories
language plpgsql security definer set search_path = public
as $$
declare
  v_key text;
  v_existing public.memories%rowtype;
  v_saved public.memories%rowtype;
begin
  if p_namespace not in ('global','core','project','experience','organization','user') then raise exception 'invalid namespace'; end if;
  if p_verification_status not in ('candidate','verified','disputed','deprecated') then raise exception 'invalid verification status'; end if;
  if nullif(btrim(p_memory_type),'') is null or nullif(btrim(p_title),'') is null or nullif(btrim(p_content),'') is null then raise exception 'memory_type, title and content required'; end if;

  v_key := md5(concat_ws('|', p_namespace, p_memory_type, coalesce(p_project_key,''), lower(btrim(p_title))));

  select * into v_existing from public.memories
  where is_active = true and memory_key = v_key
  order by updated_at desc limit 1 for update;

  if found then
    update public.memories set
      content = p_content,
      importance = greatest(1,least(coalesce(p_importance,5),10)),
      source = coalesce(nullif(btrim(p_source),''),'xiaoe'),
      tags = coalesce(p_tags,'{}'),
      metadata = coalesce(p_metadata,'{}'::jsonb),
      confidence = greatest(1,least(coalesce(p_confidence,8),10)),
      source_priority = greatest(0,least(coalesce(p_source_priority,50),100)),
      verification_status = p_verification_status,
      valid_until = p_valid_until,
      supersedes_id = coalesce(p_supersedes_id, supersedes_id),
      last_verified_at = case when p_verification_status='verified' then now() else last_verified_at end,
      updated_at = now()
    where id = v_existing.id returning * into v_saved;
    return v_saved;
  end if;

  if p_supersedes_id is not null then
    update public.memories set is_active=false, verification_status='deprecated', updated_at=now()
    where id=p_supersedes_id and is_active=true;
  end if;

  insert into public.memories(
    namespace,memory_type,title,content,importance,project_key,organization_id,user_id,
    source,tags,metadata,is_active,verification_status,confidence,source_priority,
    last_verified_at,valid_until,supersedes_id,memory_key
  ) values (
    p_namespace,p_memory_type,p_title,p_content,greatest(1,least(coalesce(p_importance,5),10)),
    p_project_key,p_organization_id,p_user_id,coalesce(nullif(btrim(p_source),''),'xiaoe'),
    coalesce(p_tags,'{}'),coalesce(p_metadata,'{}'::jsonb),true,p_verification_status,
    greatest(1,least(coalesce(p_confidence,8),10)),greatest(0,least(coalesce(p_source_priority,50),100)),
    case when p_verification_status='verified' then now() else null end,p_valid_until,p_supersedes_id,v_key
  ) returning * into v_saved;
  return v_saved;
end;
$$;

create or replace function public.service_create_task_context_pack(
  p_user_intent text,
  p_project_key text default null,
  p_task_type text default 'general',
  p_risk_level text default 'low',
  p_tags text[] default '{}',
  p_source_checks jsonb default '{}'::jsonb,
  p_limit integer default 20
)
returns public.task_context_packs
language plpgsql security definer set search_path = public
as $$
declare
  v_ids uuid[];
  v_conflicts uuid[];
  v_memories jsonb;
  v_row public.task_context_packs%rowtype;
begin
  if nullif(btrim(p_user_intent),'') is null then raise exception 'user_intent required'; end if;
  if p_risk_level not in ('low','medium','high','critical') then raise exception 'invalid risk level'; end if;

  select coalesce(array_agg(x.memory_id),'{}'::uuid[]), coalesce(jsonb_agg(to_jsonb(x)),'[]'::jsonb)
    into v_ids, v_memories
  from public.service_fusion_retrieve(
    p_query => p_user_intent::text,
    p_project_key => p_project_key::text,
    p_tags => coalesce(p_tags,'{}'::text[]),
    p_namespaces => null::text[],
    p_min_importance => 1::smallint,
    p_limit => p_limit::integer
  ) x;

  select coalesce(array_agg(distinct c.memory_id),'{}'::uuid[])
    into v_conflicts
  from public.service_find_memory_conflicts(p_project_key::text) c;

  insert into public.task_context_packs(
    project_key,task_type,user_intent,risk_level,requested_tags,memory_ids,
    conflict_memory_ids,source_checks,context_pack
  ) values (
    p_project_key,coalesce(nullif(btrim(p_task_type),''),'general'),p_user_intent,p_risk_level,
    coalesce(p_tags,'{}'),v_ids,v_conflicts,coalesce(p_source_checks,'{}'::jsonb),
    jsonb_build_object(
      'project_key',p_project_key,
      'task_type',coalesce(nullif(btrim(p_task_type),''),'general'),
      'risk_level',p_risk_level,
      'retrieved_memories',v_memories,
      'conflict_memory_ids',to_jsonb(v_conflicts),
      'source_checks',coalesce(p_source_checks,'{}'::jsonb),
      'retrieval_version','fusion_v3'
    )
  ) returning * into v_row;
  return v_row;
end;
$$;

create or replace function public.service_close_task_context_pack(
  p_id uuid,
  p_status text default 'completed',
  p_source_checks jsonb default null
)
returns public.task_context_packs
language plpgsql security definer set search_path = public
as $$
declare v_row public.task_context_packs%rowtype;
begin
  if p_status not in ('completed','abandoned','blocked') then raise exception 'invalid close status'; end if;
  update public.task_context_packs
  set status=p_status,
      source_checks=coalesce(p_source_checks,source_checks),
      updated_at=now(),
      closed_at=case when p_status in ('completed','abandoned') then now() else closed_at end
  where id=p_id returning * into v_row;
  if not found then raise exception 'task context pack not found'; end if;
  return v_row;
end;
$$;

revoke all on function public.service_save_memory_v2(text,text,text,text,smallint,text,uuid,uuid,text,text[],jsonb,smallint,smallint,text,timestamptz,uuid) from public, anon, authenticated;
revoke all on function public.service_create_task_context_pack(text,text,text,text,text[],jsonb,integer) from public, anon, authenticated;
revoke all on function public.service_close_task_context_pack(uuid,text,jsonb) from public, anon, authenticated;

grant execute on function public.service_save_memory_v2(text,text,text,text,smallint,text,uuid,uuid,text,text[],jsonb,smallint,smallint,text,timestamptz,uuid) to service_role;
grant execute on function public.service_create_task_context_pack(text,text,text,text,text[],jsonb,integer) to service_role;
grant execute on function public.service_close_task_context_pack(uuid,text,jsonb) to service_role;
