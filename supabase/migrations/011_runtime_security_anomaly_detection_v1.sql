-- Canonicalized production backfill.
-- Production history originally introduced the alerts schema and an initial anomaly
-- function here; the function was immediately corrected by 012_runtime_security_anomaly_detection_fix_v1.sql.
-- Keep the durable schema in 011 and let 012 install the final production function.

create table if not exists public.runtime_security_alerts (
  id bigserial primary key,
  created_at timestamptz not null default now(),
  alert_type text not null check (alert_type in ('invalid_token_spike','scope_denied_spike','rate_limit_spike','high_request_rate')),
  severity text not null check (severity in ('low','medium','high')),
  token_fingerprint text,
  client_id uuid,
  endpoint text,
  window_start timestamptz not null,
  window_end timestamptz not null,
  event_count integer not null,
  status text not null default 'open' check (status in ('open','acknowledged','resolved')),
  details jsonb not null default '{}'::jsonb
);

create unique index if not exists runtime_security_alerts_dedupe_idx
  on public.runtime_security_alerts (
    alert_type,
    coalesce(token_fingerprint,''),
    coalesce(endpoint,''),
    window_start
  );

create index if not exists runtime_security_alerts_created_at_idx
  on public.runtime_security_alerts (created_at desc);

create index if not exists runtime_security_alerts_status_idx
  on public.runtime_security_alerts (status, created_at desc);

alter table public.runtime_security_alerts enable row level security;
revoke all on table public.runtime_security_alerts from public, anon, authenticated;
