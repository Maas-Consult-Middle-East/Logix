# Logix Issue Tracker

Last updated: 2026-08-11

Status definitions: **Done**, **In Progress**, **Ready for Production Verification**, **Backlog**.

## Current change set

| ID | Issue | Priority | Status | Acceptance criteria |
|---|---|---:|---|---|
| LOGIX-001 | Provision the Logix Workspace on every fresh app installation | Critical | Done | `install-app logix` creates the public Workspace, its 30 links, 4 shortcuts, and role access without a manual command. |
| LOGIX-002 | Repair or provision the Workspace on existing installations | Critical | Done | `bench --site <site> migrate` idempotently creates or repairs the Workspace through `after_migrate`. |
| LOGIX-003 | Make the Workspace visible to production administrators | High | Done | System Manager and all Logix operational roles can see the Workspace; it is public and not hidden. |
| LOGIX-004 | Prevent unrelated system records from entering Logix fixtures | High | Done | Exports contain only the Logix Workspace, Logix roles, and `logix_*` Custom Fields. |
| LOGIX-005 | Populate Workspace navigation | High | Done | Commercial, Operations, Fleet & Resources, Masters, Billing, and Setup cards resolve to existing records. |
| LOGIX-006 | Add a default Branch field to User | High | Done | `User.logix_branch` links to Branch and participates in branch access alongside native User Permissions. |
| LOGIX-007 | Integrate manually added Estimation transport fields | High | Done | City pair, vehicle/load type, numeric weight/CBM, extra stops, and trip pricing are validated server-side. |
| LOGIX-008 | Calculate Estimation selling price from Rate Cards | Critical | Done | Customer-specific rates take precedence over generic rates; base, excess weight, CBM, stops, minimum, round-trip, and return pricing calculate server-side. |
| LOGIX-009 | Preserve controlled manual Estimation pricing | High | Done | Manual pricing works only when enabled in Logix Settings; revenue and currency are editable only for Manual pricing. |
| LOGIX-010 | Safely migrate legacy Estimation measurement text | High | Done | Patch `v1_0_3_normalize_estimation_measurements` preserves records and converts legacy weight/CBM values before schema synchronization. |
| LOGIX-011 | Map Estimation transport fields into Job creation | High | Done | Job creation maps cities, load type, preferred vehicle type, revenue, and estimated cost. |
| LOGIX-012 | Improve Apply Rate Card behavior on incomplete forms | Medium | Backlog | Button is disabled or hidden until all matching fields are populated, and incomplete input produces a specific validation message rather than “no rate card.” |
| LOGIX-013 | Verify the Workspace on the production site | Critical | Ready for Production Verification | Updated app code is deployed; migrate/cache clear/restart complete; a System Manager and one Logix role can open the Workspace. |
| LOGIX-014 | Expand Estimation pricing regression coverage | Medium | Backlog | Automated tests cover customer/generic precedence, missing cards, disabled/expired cards, manual pricing disabled, round/return rates, and Job mapping. |

## Production verification checklist

- [ ] Deploy the updated Logix app revision to production.
- [ ] Run `bench --site <production-site> migrate`.
- [ ] Run `bench --site <production-site> clear-cache`.
- [ ] Run `bench restart` using the production process manager.
- [ ] Confirm Workspace `Logix` exists, is public, and is not hidden.
- [ ] Confirm the Workspace contains 30 links and 4 shortcuts.
- [ ] Confirm visibility as System Manager.
- [ ] Confirm visibility and branch isolation as a normal Logix user.
- [ ] Create a Rate Card and verify an Estimation calculation.
- [ ] Verify Manual pricing is allowed or blocked according to Logix Settings.
- [ ] Run `bench --site <production-site> run-tests --app logix` in an approved non-live test environment.

## Verification evidence

- Local migration: passing.
- Asset build: passing.
- Logix automated suite: 4 tests passing.
- Workspace metadata: public `1`, hidden `0`, module `Logix`.
- Workspace content: 30 links and 4 shortcuts.

## Maintenance rules

- Add one row for each defect or requested change.
- Do not mark production items **Done** until production evidence is recorded.
- Link code changes, patches, and test names in the issue notes when the repository gains a remote issue system.
- Keep architectural phase tracking in `LOGIX_IMPLEMENTATION.md`; use this file for actionable issues and acceptance checks.
