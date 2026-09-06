create table if not exists public.runtime_security_events (
  id bigserial primary key,
  occurred_at timestamptz not null default now(),
  endpoint text not null,
  token_fingerprint text,
  client_id uuid,
  outcome text not null check (outcome in ('allowed','invalid_token','scope_denied','rate_limited','error')),
  required_scope text,
  metadata jsonb not null default '{}'::jsonb
);

create index if not exists runtime_security_events_occurred_at_idx
  on public.runtime_security_events (occurred_at desc);
create index if not exists runtime_security_events_fingerprint_idx
  on public.runtime_security_events (token_fingerprint, occurred_at desc);

alter table public.runtime_security_events enable row level security;
revoke all on table public.runtime_security_events from public, anon, authenticated;

create table if not exists public.runtime_security_buckets (
  token_fingerprint text not null,
  endpoint text not null,
  bucket_kind text not null check (bucket_kind in ('valid','invalid')),
  window_started_at timestamptz not null,
  request_count integer not null default 0,
  blocked_until timestamptz,
  updated_at timestamptz not null default now(),
  primary key (token_fingerprint, endpoint, bucket_kind)
);

alter table public.runtime_security_buckets enable row level security;
revoke all on table public.runtime_security_buckets from public, anon, authenticated;

create or replace function public.service_runtime_security_check(
  p_token text,
  p_required_scope text,
  p_endpoint text
)
returns table(
  allowed boolean,
  reason text,
  client_id uuid,
  client_name text,
  scopes text[],
  retry_after_seconds integer
)
language plpgsql
security definer
set search_path = public, extensions
as $$
declare
  v_fingerprint text;
  v_client public.runtime_clients%rowtype;
  v_now timestamptz := now();
  v_kind text;
  v_window interval;
  v_limit integer;
  v_bucket public.runtime_security_buckets%rowtype;
  v_reason text;
  v_allowed boolean := false;
begin
  if nullif(btrim(p_token), '') is null then
    return query select false, 'missing_token', null::uuid, null::text, '{}'::text[], 0;
    return;
  end if;

  if nullif(btrim(p_endpoint), '') is null then
    p_endpoint := 'unknown';
  end if;

  v_fingerprint := encode(digest(p_token, 'sha256'), 'hex');

  select * into v_client
  from public.runtime_clients
  where key_hash = v_fingerprint
    and status = 'active'
    and (expires_at is null or expires_at > v_now)
  limit 1;

  if not found then
    v_kind := 'invalid';
    v_window := interval '10 minutes';
    v_limit := 10;
    v_reason := 'invalid_token';
  elsif p_required_scope is not null and not (p_required_scope = any(v_client.scopes)) then
    v_kind := 'invalid';
    v_window := interval '10 minutes';
    v_limit := 10;
    v_reason := 'scope_denied';
  else
    v_kind := 'valid';
    v_window := interval '1 minute';
    v_limit := 120;
    v_reason := 'allowed';
  end if;

  insert into public.runtime_security_buckets(
    token_fingerprint, endpoint, bucket_kind, window_started_at, request_count, blocked_until, updated_at
  ) values (
    v_fingerprint, p_endpoint, v_kind, v_now, 1, null, v_now
  )
  on conflict (token_fingerprint, endpoint, bucket_kind) do update
  set
    request_count = case
      when public.runtime_security_buckets.window_started_at + v_window <= v_now then 1
      else public.runtime_security_buckets.request_count + 1
    end,
    window_started_at = case
      when public.runtime_security_buckets.window_started_at + v_window <= v_now then v_now
      else public.runtime_security_buckets.window_started_at
    end,
    blocked_until = case
      when public.runtime_security_buckets.blocked_until is not null
           and public.runtime_security_buckets.blocked_until > v_now
        then public.runtime_security_buckets.blocked_until
      when (case
        when public.runtime_security_buckets.window_started_at + v_window <= v_now then 1
        else public.runtime_security_buckets.request_count + 1
      end) > v_limit
        then v_now + case when v_kind = 'invalid' then interval '15 minutes' else interval '1 minute' end
      else null
    end,
    updated_at = v_now
  returning * into v_bucket;

  if v_bucket.blocked_until is not null and v_bucket.blocked_until > v_now then
    insert into public.runtime_security_events(endpoint, token_fingerprint, client_id, outcome, required_scope, metadata)
    values (p_endpoint, v_fingerprint, v_client.id, 'rate_limited', p_required_scope,
            jsonb_build_object('bucket_kind', v_kind));

    return query select false, 'rate_limited', v_client.id, v_client.client_name,
      coalesce(v_client.scopes, '{}'::text[]),
      greatest(1, ceil(extract(epoch from (v_bucket.blocked_until - v_now)))::integer);
    return;
  end if;

  if v_reason <> 'allowed' then
    insert into public.runtime_security_events(endpoint, token_fingerprint, client_id, outcome, required_scope)
    values (p_endpoint, v_fingerprint, v_client.id,
      case when v_reason = 'scope_denied' then 'scope_denied' else 'invalid_token' end,
      p_required_scope);

    return query select false, v_reason, v_client.id, v_client.client_name,
      coalesce(v_client.scopes, '{}'::text[]), 0;
    return;
  end if;

  update public.runtime_clients
  set last_used_at = v_now
  where id = v_client.id;

  insert into public.runtime_security_events(endpoint, token_fingerprint, client_id, outcome, required_scope)
  values (p_endpoint, v_fingerprint, v_client.id, 'allowed', p_required_scope);

  return query select true, 'allowed', v_client.id, v_client.client_name, v_client.scopes, 0;
end;
$$;

revoke all on function public.service_runtime_security_check(text,text,text) from public, anon, authenticated;
grant execute on function public.service_runtime_security_check(text,text,text) to service_role;
