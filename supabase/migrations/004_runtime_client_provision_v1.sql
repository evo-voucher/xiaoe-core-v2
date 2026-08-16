create or replace function public.service_register_runtime_client(
  p_client_name text,
  p_token text,
  p_scopes text[],
  p_expires_at timestamptz default null
)
returns table(
  client_id uuid,
  client_name text,
  scopes text[],
  status text,
  expires_at timestamptz
)
language plpgsql
security definer
set search_path = public
as $$
declare
  v_id uuid;
  v_hash text;
begin
  if nullif(btrim(p_client_name), '') is null then
    raise exception 'client_name required';
  end if;

  if nullif(btrim(p_token), '') is null then
    raise exception 'token required';
  end if;

  if p_scopes is null or cardinality(p_scopes) = 0 then
    raise exception 'at least one scope required';
  end if;

  if exists (
    select 1 from unnest(p_scopes) s
    where s not in ('memory:read','memory:write','project:state')
  ) then
    raise exception 'invalid scope';
  end if;

  v_hash := encode(digest(p_token, 'sha256'), 'hex');

  insert into public.runtime_clients(client_name, key_hash, scopes, status, expires_at)
  values (btrim(p_client_name), v_hash, p_scopes, 'active', p_expires_at)
  on conflict (client_name) do update
  set key_hash = excluded.key_hash,
      scopes = excluded.scopes,
      status = 'active',
      expires_at = excluded.expires_at,
      last_used_at = null,
      updated_at = now()
  returning id into v_id;

  return query
  select rc.id, rc.client_name, rc.scopes, rc.status, rc.expires_at
  from public.runtime_clients rc
  where rc.id = v_id;
end;
$$;

revoke all on function public.service_register_runtime_client(text,text,text[],timestamptz) from public, anon, authenticated;
grant execute on function public.service_register_runtime_client(text,text,text[],timestamptz) to service_role;
