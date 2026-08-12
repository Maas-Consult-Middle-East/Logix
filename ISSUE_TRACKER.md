# Logix Issue Tracker

Last updated: 2026-08-12

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
| LOGIX-011 | Map Estimation transport fields into Job creation | High | Done | Both Job creation paths map customer, branch, cities, load type, preferred vehicle type, revenue, and estimated cost while preserving the Job's Draft status and naming series. |
| LOGIX-012 | Improve Apply Rate Card behavior on incomplete forms | Medium | Backlog | Button is disabled or hidden until all matching fields are populated, and incomplete input produces a specific validation message rather than “no rate card.” |
| LOGIX-013 | Verify the Workspace on the production site | Critical | Ready for Production Verification | Updated app code is deployed; migrate/cache clear/restart complete; a System Manager and one Logix role can open the Workspace. |
| LOGIX-014 | Expand Estimation pricing regression coverage | Medium | Backlog | Automated tests cover customer/generic precedence, missing cards, disabled/expired cards, manual pricing disabled, round/return rates, and Job mapping. |
| LOGIX-015 | Give Administrator explicit full access to every Logix DocType | Critical | Done | All 14 standalone Logix DocTypes contain an explicit Administrator permission row; transaction DocTypes grant submit/cancel/amend, level-1 financial fields are accessible, and child tables inherit access from their parents. Logix branch hooks explicitly bypass Administrator. |
| LOGIX-016 | Package Logix Naming Series with the app | High | Done | Eight numbered DocTypes use native `naming_series:` fields with app-managed defaults; patch `v1_0_4_add_logix_naming_series` backfills existing records, and `v1_0_5_sync_logix_naming_counters` initializes native counters from the highest existing document suffix to prevent restarts and duplicate names. |
| LOGIX-017 | Restrict Job creation to submitted Estimations | Critical | Done | Job's Estimation link and Fetch From dialog show only submitted, unused Estimations; server validation rejects draft, cancelled, mismatched-customer, or already-used Estimations. |
| LOGIX-018 | Add Create Job action to submitted Estimation | High | Done | A submitted Estimation without a downstream Job provides **Create → Job**, opening a mapped unsaved Job for review. |
| LOGIX-019 | Add Fetch From Estimation to Job | High | Done | A draft Job provides **Fetch From → Estimation** and maps the selected submitted Estimation through the same permission-checked server method. |
| LOGIX-020 | Name City and Load Type masters by their title fields | High | Done | New Logix City records use `city_name`, new Logix Load Type records use `load_type_name`, both fields are unique, and patch `v1_0_6_name_logix_masters_by_title` renames legacy hash-named records while updating links. |

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
- [ ] Confirm Administrator has full access to Logix City, Logix Load Type, and all other standalone Logix DocTypes.
- [ ] Confirm the eight Logix transaction DocTypes appear in Document Naming Settings with the packaged defaults.
- [ ] Confirm draft Estimations do not appear in the Job Estimation link or Fetch From dialog.
- [ ] From a submitted Estimation, use **Create → Job** and verify all mapped values.
- [ ] From a draft Job, use **Fetch From → Estimation** and verify all mapped values.
- [ ] Confirm a draft, cancelled, or already-used Estimation is rejected server-side during Job save.
- [ ] Run `bench --site <production-site> run-tests --app logix` in an approved non-live test environment.

## Verification evidence

- Local migration: passing.
- Asset build: passing.
- Administrator permissions: 14 standalone DocTypes verified in live metadata on `logix.localhost`.
- Naming Series defaults: all 8 recognized by Frappe after migration on `logix.localhost`.
- Naming Series upgrade patch: executed successfully on `logix.localhost`.
- Naming counter migration: native counter keys synchronized with the highest existing Logix document numbers.
- Job workflow test module: 3 tests passing, including draft rejection and submitted Estimation mapping.
- Python compilation, JavaScript syntax checks, JSON parsing, and `git diff --check`: passing.
- Workspace metadata: public `1`, hidden `0`, module `Logix`.
- Workspace content: 30 links and 4 shortcuts.

## Current change details

### Administrator permissions

- Added explicit full Administrator permission rows to every standalone Logix DocType.
- Enabled create/delete/import/export/report/share/print/email where supported.
- Enabled submit/cancel/amend for submittable Logix DocTypes.
- Added level-1 read/write access for Estimation and Job financial fields.
- Kept Logix Settings within Frappe's Single DocType restrictions.
- Made the branch permission bypass for the built-in Administrator account explicit.

### Naming Series

| DocType | Default series |
|---|---|
| Logix Estimation | `EST-.YYYY.-` |
| Logix Job | `JOB-.YYYY.-` |
| Logix Shipment | `SHP-.YYYY.-` |
| Logix Shipment Order | `SO-.YYYY.-` |
| Logix Trip | `TRIP-.YYYY.-` |
| Logix Handover | `HND-` |
| Logix Shipment Leg | `LEG-` |
| Logix Transport Rate Card | `TRC-` |

### Estimation-to-Job workflow

- Added a submitted-only query for the Job Estimation link.
- Added **Create → Job** to submitted Estimations that do not already have a downstream Job.
- Added **Fetch From → Estimation** to draft Jobs.
- Added a shared server-side mapper used by both actions.
- Added server-side eligibility checks so UI filters cannot be bypassed.
- Retained the existing direct creation API while applying the same submitted-only checks and mapping logic.
- Added regression tests for draft rejection and submitted Estimation mapping.

### Naming Series counter repair

- Fixed upgrades from the original `format:` naming implementation, which stored Logix sequence progress under an empty counter key.
- Added patch `v1_0_5_sync_logix_naming_counters` to create the correct evaluated counter keys, such as `EST-2026-` and `JOB-2026-`.
- Counter synchronization only moves a counter forward and never renames existing documents or reduces an existing counter.

### Master naming

- Configured Logix City with `autoname: field:city_name`.
- Configured Logix Load Type with `autoname: field:load_type_name`.
- Made both naming fields unique and enabled controlled renaming.
- Added patch `v1_0_6_name_logix_masters_by_title` to replace legacy hash names and update linked records through Frappe's rename mechanism.

## Maintenance rules

- Add one row for each defect or requested change.
- Do not mark production items **Done** until production evidence is recorded.
- Link code changes, patches, and test names in the issue notes when the repository gains a remote issue system.
- Keep architectural phase tracking in `LOGIX_IMPLEMENTATION.md`; use this file for actionable issues and acceptance checks.
