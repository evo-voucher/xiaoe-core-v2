create extension if not exists pgcrypto;

create table if not exists public.runtime_clients (
  id uuid primary key default gen_random_uuid(),
  client_name text not null unique,
  key_hash text not null unique,
  scopes text[] not null default '{}',
  status text not null default 'active' check (status in ('active','suspended','revoked')),
  expires_at timestamptz,
  last_used_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint runtime_clients_scopes_nonempty check (cardinality(scopes) > 0)
);

alter table public.runtime_clients enable row level security;

revoke all on table public.runtime_clients from public, anon, authenticated;
grant select, insert, update, delete on table public.runtime_clients to service_role;

create or replace function public.runtime_clients_touch_updated_at()
returns trigger
language plpgsql
set search_path = public
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists runtime_clients_touch_updated_at on public.runtime_clients;
create trigger runtime_clients_touch_updated_at
before update on public.runtime_clients
for each row execute function public.runtime_clients_touch_updated_at();

revoke all on function public.runtime_clients_touch_updated_at() from public, anon, authenticated;

create or replace function public.service_validate_runtime_client(
  p_token text,
  p_required_scope text default null
)
returns table(
  client_id uuid,
  client_name text,
  scopes text[],
  valid boolean
)
language plpgsql
security definer
set search_path = public
as $$
declare
  v_hash text;
  v_row public.runtime_clients%rowtype;
begin
  if nullif(btrim(p_token), '') is null then
    return query select null::uuid, null::text, '{}'::text[], false;
    return;
  end if;

  v_hash := encode(digest(p_token, 'sha256'), 'hex');

  select * into v_row
  from public.runtime_clients
  where key_hash = v_hash
    and status = 'active'
    and (expires_at is null or expires_at > now())
  limit 1;

  if not found then
    return query select null::uuid, null::text, '{}'::text[], false;
    return;
  end if;

  if p_required_scope is not null and not (p_required_scope = any(v_row.scopes)) then
    return query select v_row.id, v_row.client_name, v_row.scopes, false;
    return;
  end if;

  update public.runtime_clients
  set last_used_at = now()
  where id = v_row.id;

  return query select v_row.id, v_row.client_name, v_row.scopes, true;
end;
$$;

revoke all on function public.service_validate_runtime_client(text,text) from public, anon, authenticated;
grant execute on function public.service_validate_runtime_client(text,text) to service_role;
