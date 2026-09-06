create extension if not exists pgcrypto;

create table if not exists public.memories (
  id uuid primary key default gen_random_uuid(),
  namespace text not null check (namespace in ('global','core','project','experience','organization','user')),
  memory_type text not null,
  title text not null,
  content text not null,
  importance smallint not null default 5 check (importance between 1 and 10),
  project_key text,
  organization_id uuid,
  user_id uuid,
  source text not null default 'xiaoe',
  tags text[] not null default '{}',
  metadata jsonb not null default '{}'::jsonb,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists memories_active_lookup_idx
  on public.memories(namespace, project_key, importance desc, updated_at desc)
  where is_active = true;

create index if not exists memories_org_idx
  on public.memories(organization_id)
  where organization_id is not null;

create index if not exists memories_user_idx
  on public.memories(user_id)
  where user_id is not null;

create unique index if not exists memories_single_current_project_state_idx
  on public.memories(project_key)
  where namespace = 'project'
    and memory_type = 'current_project_state'
    and is_active = true;

create or replace function public.set_memories_updated_at()
returns trigger
language plpgsql
set search_path = public
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists set_memories_updated_at on public.memories;
create trigger set_memories_updated_at
before update on public.memories
for each row execute function public.set_memories_updated_at();

alter table public.memories enable row level security;

revoke all on table public.memories from public, anon, authenticated;
grant select, insert, update, delete on table public.memories to service_role;

revoke all on function public.set_memories_updated_at() from public, anon, authenticated;
grant execute on function public.set_memories_updated_at() to service_role;
