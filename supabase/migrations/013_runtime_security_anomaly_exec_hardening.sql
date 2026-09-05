-- Harden runtime anomaly detection execution boundary.
-- Only service_role may invoke this SECURITY DEFINER function.

revoke all on function public.service_detect_runtime_security_anomalies(integer)
  from public, anon, authenticated;

grant execute on function public.service_detect_runtime_security_anomalies(integer)
  to service_role;
