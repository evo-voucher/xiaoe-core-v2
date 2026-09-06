create table if not exists public.runtime_security_response_policy (
  severity text primary key check (severity in ('low','medium','high')),
  action_mode text not null check (action_mode in ('observe','heightened_monitoring','temporary_restrict')),
  auto_apply boolean not null default false,
  restriction_minutes integer,
  requires_manual_review boolean not null default false,
  updated_at timestamptz not null default now()
);

insert into public.runtime_security_response_policy(severity, action_mode, auto_apply, restriction_minutes, requires_manual_review)
values
  ('low','observe',false,null,false),
  ('medium','heightened_monitoring',false,null,true),
  ('high','temporary_restrict',false,15,true)
on conflict (severity) do update set
  action_mode = excluded.action_mode,
  auto_apply = excluded.auto_apply,
  restriction_minutes = excluded.restriction_minutes,
  requires_manual_review = excluded.requires_manual_review,
  updated_at = now();

alter table public.runtime_security_response_policy enable row level security;
revoke all on table public.runtime_security_response_policy from public, anon, authenticated;

create table if not exists public.runtime_security_response_events (
  id bigserial primary key,
  created_at timestamptz not null default now(),
  alert_id bigint not null references public.runtime_security_alerts(id) on delete cascade,
  severity text not null,
  action_mode text not null,
  applied boolean not null default false,
  applied_until timestamptz,
  note text,
  unique(alert_id, action_mode)
);

alter table public.runtime_security_response_events enable row level security;
revoke all on table public.runtime_security_response_events from public, anon, authenticated;

create or replace function public.service_plan_runtime_security_responses()
returns table(planned integer)
language plpgsql
security definer
set search_path = public
as $$
declare
  v_count integer := 0;
begin
  insert into public.runtime_security_response_events(alert_id, severity, action_mode, applied, applied_until, note)
  select
    a.id,
    a.severity,
    p.action_mode,
    false,
    null,
    case
      when a.severity = 'low' then 'record_only'
      when a.severity = 'medium' then 'manual_review_recommended'
      when a.severity = 'high' then 'temporary_restriction_available_but_not_auto_applied'
    end
  from public.runtime_security_alerts a
  join public.runtime_security_response_policy p on p.severity = a.severity
  where a.status = 'open'
  on conflict (alert_id, action_mode) do nothing;

  get diagnostics v_count = row_count;
  return query select v_count;
end;
$$;

revoke all on function public.service_plan_runtime_security_responses() from public, anon, authenticated;
grant execute on function public.service_plan_runtime_security_responses() to service_role;
