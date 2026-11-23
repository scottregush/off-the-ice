-- Off the Ice: database for the optional account (rosters synced across devices).
-- Run once in Supabase → SQL Editor → New query → Run. Safe to run again.

-- One row per user with all their rosters.
create table if not exists public.rosters (
  user_id    uuid primary key default auth.uid() references auth.users (id) on delete cascade,
  data       jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

-- Each signed-in user can read and write only their own row; visitors who are not signed in get nothing.
alter table public.rosters enable row level security;

drop policy if exists "rosters: read own"   on public.rosters;
drop policy if exists "rosters: insert own" on public.rosters;
drop policy if exists "rosters: update own" on public.rosters;
drop policy if exists "rosters: delete own" on public.rosters;
create policy "rosters: read own"   on public.rosters for select to authenticated using ((select auth.uid()) = user_id);
create policy "rosters: insert own" on public.rosters for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "rosters: update own" on public.rosters for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "rosters: delete own" on public.rosters for delete to authenticated using ((select auth.uid()) = user_id);

revoke all on public.rosters from anon;
grant select, insert, update, delete on public.rosters to authenticated;

-- "Delete account" on the site: removes the user's rosters and the account itself.
create or replace function public.delete_my_account()
returns void
language plpgsql
security definer
set search_path = ''
as $$
begin
  if auth.uid() is null then
    raise exception 'not signed in';
  end if;
  delete from public.rosters where user_id = auth.uid();
  delete from auth.users where id = auth.uid();
end;
$$;
revoke all on function public.delete_my_account() from public, anon;
grant execute on function public.delete_my_account() to authenticated;

-- Make the API see the new table right away.
notify pgrst, 'reload schema';
