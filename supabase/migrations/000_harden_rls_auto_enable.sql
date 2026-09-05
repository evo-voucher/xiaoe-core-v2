-- Recovered from active Supabase migration history on 2026-08-24.
-- Source migration: 20260823170125 / 000_harden_rls_auto_enable

revoke all on function public.rls_auto_enable() from public, anon, authenticated;
