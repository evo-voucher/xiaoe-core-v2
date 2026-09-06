-- XiaoE Core fresh-project security baseline
-- Purpose: recreate the pre-existing RLS auto-enable function and event trigger
-- that existed before migration 000_harden_rls_auto_enable was recorded.
-- Run this ONLY for a brand-new/empty Supabase project before migrations 000-009.
-- Migration 000 remains responsible for revoking direct EXECUTE privileges.

create or replace function public.rls_auto_enable()
returns event_trigger
language plpgsql
security definer
set search_path = pg_catalog
as $$
declare
  cmd record;
begin
  for cmd in
    select *
    from pg_event_trigger_ddl_commands()
    where command_tag in ('CREATE TABLE', 'CREATE TABLE AS', 'SELECT INTO')
      and object_type in ('table','partitioned table')
  loop
    if cmd.schema_name is not null
       and cmd.schema_name in ('public')
       and cmd.schema_name not in ('pg_catalog','information_schema')
       and cmd.schema_name not like 'pg_toast%'
       and cmd.schema_name not like 'pg_temp%'
    then
      begin
        execute format('alter table if exists %s enable row level security', cmd.object_identity);
        raise log 'rls_auto_enable: enabled RLS on %', cmd.object_identity;
      exception
        when others then
          raise log 'rls_auto_enable: failed to enable RLS on %', cmd.object_identity;
      end;
    else
      raise log 'rls_auto_enable: skip % (either system schema or not in enforced list: %.)', cmd.object_identity, cmd.schema_name;
    end if;
  end loop;
end;
$$;

do $$
begin
  if exists (
    select 1
    from pg_catalog.pg_event_trigger
    where evtname = 'ensure_rls'
      and evtfoid <> 'public.rls_auto_enable()'::regprocedure
  ) then
    raise exception 'event trigger ensure_rls already exists and points to a different function';
  elsif not exists (
    select 1
    from pg_catalog.pg_event_trigger
    where evtname = 'ensure_rls'
  ) then
    execute 'create event trigger ensure_rls on ddl_command_end execute function public.rls_auto_enable()';
  end if;
end;
$$;
