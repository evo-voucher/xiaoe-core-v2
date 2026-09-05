-- PostgreSQL extensions are installed in the `extensions` schema on hosted Supabase.
-- Keep SECURITY DEFINER search paths explicit and ensure pgcrypto.digest resolves.

alter function public.service_validate_runtime_client(text,text)
  set search_path = public, extensions;

alter function public.service_register_runtime_client(text,text,text[],timestamptz)
  set search_path = public, extensions;
