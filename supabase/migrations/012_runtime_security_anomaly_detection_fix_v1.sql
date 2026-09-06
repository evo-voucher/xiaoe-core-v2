create or replace function public.service_detect_runtime_security_anomalies(
  p_window_minutes integer default 10
)
returns table(alerts_created integer)
language plpgsql
security definer
set search_path = public
as $$
declare
  v_window_start timestamptz := now() - make_interval(mins => greatest(1, least(p_window_minutes, 60)));
  v_window_bucket timestamptz := date_trunc('minute', v_window_start);
  v_created integer := 0;
  v_rows integer;
begin
  insert into public.runtime_security_alerts(alert_type, severity, token_fingerprint, client_id, endpoint, window_start, window_end, event_count, details)
  select 'invalid_token_spike', case when count(*) >= 50 then 'high' else 'medium' end,
    token_fingerprint, (array_agg(client_id) filter (where client_id is not null))[1], endpoint,
    v_window_bucket, now(), count(*)::integer, jsonb_build_object('source','runtime_security_events')
  from public.runtime_security_events
  where occurred_at >= v_window_start and outcome = 'invalid_token'
  group by token_fingerprint, endpoint
  having count(*) >= 10
  on conflict do nothing;
  get diagnostics v_rows = row_count;
  v_created := v_created + v_rows;

  insert into public.runtime_security_alerts(alert_type, severity, token_fingerprint, client_id, endpoint, window_start, window_end, event_count, details)
  select 'scope_denied_spike', case when count(*) >= 20 then 'high' else 'medium' end,
    token_fingerprint, (array_agg(client_id) filter (where client_id is not null))[1], endpoint,
    v_window_bucket, now(), count(*)::integer, jsonb_build_object('source','runtime_security_events')
  from public.runtime_security_events
  where occurred_at >= v_window_start and outcome = 'scope_denied'
  group by token_fingerprint, endpoint
  having count(*) >= 5
  on conflict do nothing;
  get diagnostics v_rows = row_count;
  v_created := v_created + v_rows;

  insert into public.runtime_security_alerts(alert_type, severity, token_fingerprint, client_id, endpoint, window_start, window_end, event_count, details)
  select 'rate_limit_spike', case when count(*) >= 20 then 'high' else 'medium' end,
    token_fingerprint, (array_agg(client_id) filter (where client_id is not null))[1], endpoint,
    v_window_bucket, now(), count(*)::integer, jsonb_build_object('source','runtime_security_events')
  from public.runtime_security_events
  where occurred_at >= v_window_start and outcome = 'rate_limited'
  group by token_fingerprint, endpoint
  having count(*) >= 5
  on conflict do nothing;
  get diagnostics v_rows = row_count;
  v_created := v_created + v_rows;

  insert into public.runtime_security_alerts(alert_type, severity, token_fingerprint, client_id, endpoint, window_start, window_end, event_count, details)
  select 'high_request_rate', case when count(*) >= 1000 then 'high' else 'low' end,
    token_fingerprint, (array_agg(client_id) filter (where client_id is not null))[1], endpoint,
    v_window_bucket, now(), count(*)::integer, jsonb_build_object('source','runtime_security_events')
  from public.runtime_security_events
  where occurred_at >= v_window_start and outcome = 'allowed'
  group by token_fingerprint, endpoint
  having count(*) >= 600
  on conflict do nothing;
  get diagnostics v_rows = row_count;
  v_created := v_created + v_rows;

  return query select v_created;
end;
$$;
