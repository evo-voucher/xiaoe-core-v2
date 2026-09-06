create or replace function public.service_read_memories(
  p_project_key text default null,
  p_namespace text default null,
  p_min_importance smallint default 1,
  p_limit integer default 100
)
returns setof public.memories
language sql
security definer
set search_path = public
as $$
  select m.*
  from public.memories m
  where m.is_active = true
    and (p_project_key is null or m.project_key = p_project_key)
    and (p_namespace is null or m.namespace = p_namespace)
    and m.importance >= greatest(1, least(coalesce(p_min_importance, 1), 10))
  order by m.importance desc, m.updated_at desc
  limit greatest(1, least(coalesce(p_limit, 100), 500));
$$;

create or replace function public.service_deactivate_conflicting_memory(
  p_namespace text,
  p_memory_type text,
  p_title text,
  p_project_key text default null,
  p_organization_id uuid default null,
  p_user_id uuid default null,
  p_exclude_id uuid default null
)
returns integer
language plpgsql
security definer
set search_path = public
as $$
declare
  v_count integer;
begin
  update public.memories
  set is_active = false,
      updated_at = now()
  where is_active = true
    and namespace = p_namespace
    and memory_type = p_memory_type
    and title = p_title
    and project_key is not distinct from p_project_key
    and organization_id is not distinct from p_organization_id
    and user_id is not distinct from p_user_id
    and (p_exclude_id is null or id <> p_exclude_id);

  get diagnostics v_count = row_count;
  return v_count;
end;
$$;

create or replace function public.service_save_memory(
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
  p_metadata jsonb default '{}'::jsonb
)
returns public.memories
language plpgsql
security definer
set search_path = public
as $$
declare
  v_existing public.memories%rowtype;
  v_saved public.memories%rowtype;
begin
  if p_namespace not in ('global','core','project','experience','organization','user') then
    raise exception 'invalid namespace';
  end if;

  if nullif(btrim(p_memory_type), '') is null then
    raise exception 'memory_type required';
  end if;

  if nullif(btrim(p_title), '') is null then
    raise exception 'title required';
  end if;

  if nullif(btrim(p_content), '') is null then
    raise exception 'content required';
  end if;

  select * into v_existing
  from public.memories
  where is_active = true
    and namespace = p_namespace
    and memory_type = p_memory_type
    and title = p_title
    and project_key is not distinct from p_project_key
    and organization_id is not distinct from p_organization_id
    and user_id is not distinct from p_user_id
  order by updated_at desc
  limit 1;

  if found then
    update public.memories
    set content = p_content,
        importance = greatest(1, least(coalesce(p_importance, 5), 10)),
        source = coalesce(nullif(btrim(p_source), ''), 'xiaoe'),
        tags = coalesce(p_tags, '{}'),
        metadata = coalesce(p_metadata, '{}'::jsonb),
        updated_at = now()
    where id = v_existing.id
    returning * into v_saved;

    return v_saved;
  end if;

  insert into public.memories(
    namespace, memory_type, title, content, importance,
    project_key, organization_id, user_id, source, tags, metadata, is_active
  ) values (
    p_namespace, p_memory_type, p_title, p_content,
    greatest(1, least(coalesce(p_importance, 5), 10)),
    p_project_key, p_organization_id, p_user_id,
    coalesce(nullif(btrim(p_source), ''), 'xiaoe'),
    coalesce(p_tags, '{}'), coalesce(p_metadata, '{}'::jsonb), true
  ) returning * into v_saved;

  return v_saved;
end;
$$;

create or replace function public.service_update_current_project_state(
  p_project_key text,
  p_content text,
  p_importance smallint default 10,
  p_metadata jsonb default '{}'::jsonb,
  p_source text default 'xiaoe'
)
returns public.memories
language plpgsql
security definer
set search_path = public
as $$
declare
  v_row public.memories%rowtype;
begin
  if nullif(btrim(p_project_key), '') is null then
    raise exception 'project_key required';
  end if;

  if nullif(btrim(p_content), '') is null then
    raise exception 'content required';
  end if;

  select * into v_row
  from public.memories
  where namespace = 'project'
    and memory_type = 'current_project_state'
    and project_key = p_project_key
    and is_active = true
  limit 1
  for update;

  if found then
    update public.memories
    set content = p_content,
        importance = greatest(1, least(coalesce(p_importance, 10), 10)),
        metadata = coalesce(p_metadata, '{}'::jsonb),
        source = coalesce(nullif(btrim(p_source), ''), 'xiaoe'),
        updated_at = now()
    where id = v_row.id
    returning * into v_row;

    return v_row;
  end if;

  insert into public.memories(
    namespace, memory_type, title, content, importance,
    project_key, source, metadata, is_active
  ) values (
    'project', 'current_project_state', 'Current Project State', p_content,
    greatest(1, least(coalesce(p_importance, 10), 10)),
    p_project_key, coalesce(nullif(btrim(p_source), ''), 'xiaoe'),
    coalesce(p_metadata, '{}'::jsonb), true
  ) returning * into v_row;

  return v_row;
end;
$$;

revoke all on function public.service_read_memories(text,text,smallint,integer) from public, anon, authenticated;
revoke all on function public.service_deactivate_conflicting_memory(text,text,text,text,uuid,uuid,uuid) from public, anon, authenticated;
revoke all on function public.service_save_memory(text,text,text,text,smallint,text,uuid,uuid,text,text[],jsonb) from public, anon, authenticated;
revoke all on function public.service_update_current_project_state(text,text,smallint,jsonb,text) from public, anon, authenticated;

grant execute on function public.service_read_memories(text,text,smallint,integer) to service_role;
grant execute on function public.service_deactivate_conflicting_memory(text,text,text,text,uuid,uuid,uuid) to service_role;
grant execute on function public.service_save_memory(text,text,text,text,smallint,text,uuid,uuid,text,text[],jsonb) to service_role;
grant execute on function public.service_update_current_project_state(text,text,smallint,jsonb,text) to service_role;
