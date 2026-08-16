# Logix Issue Tracker

Last updated: 2026-08-16

Status definitions: **Done**, **In Progress**, **Ready for Production Verification**, **Backlog**.

## Current change set

| ID | Issue | Priority | Status | Acceptance criteria |
|---|---|---:|---|---|
| LOGIX-001 | Provision the Logix Workspace on every fresh app installation | Critical | Done | `install-app logix` creates the public Workspace, its 33 links, 4 shortcuts, and role access without a manual command. |
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
| LOGIX-015 | Give Administrator explicit full access to every Logix DocType | Critical | Done | All 17 standalone Logix DocTypes contain an explicit Administrator permission row; transaction DocTypes grant submit/cancel/amend, level-1 financial fields are accessible, and child tables inherit access from their parents. Logix branch hooks explicitly bypass Administrator. |
| LOGIX-016 | Package Logix Naming Series with the app | High | Done | Ten numbered DocTypes use native `naming_series:` fields with app-managed defaults; patch `v1_0_4_add_logix_naming_series` backfills the original records, and `v1_0_5_sync_logix_naming_counters` initializes native counters from the highest existing document suffix to prevent restarts and duplicate names. |
| LOGIX-017 | Restrict Job creation to submitted Estimations | Critical | Done | Job's Estimation link and Fetch From dialog show only submitted, unused Estimations; server validation rejects draft, cancelled, mismatched-customer, or already-used Estimations. |
| LOGIX-018 | Add Create Job action to submitted Estimation | High | Done | A submitted Estimation without a downstream Job provides **Create → Job**, opening a mapped unsaved Job for review. |
| LOGIX-019 | Add Fetch From Estimation to Job | High | Done | A draft Job provides **Fetch From → Estimation** and maps the selected submitted Estimation through the same permission-checked server method. |
| LOGIX-020 | Name City and Load Type masters by their title fields | High | Done | New Logix City records use `city_name`, new Logix Load Type records use `load_type_name`, both fields are unique, and patch `v1_0_6_name_logix_masters_by_title` renames legacy hash-named records while updating links. |
| LOGIX-021 | Add downstream Create actions to Jobs and Shipment Orders | High | Ready for Production Verification | A saved active Job provides **Create → Shipment Order** and **Create → Shipment**; a saved active Shipment Order provides **Create → Shipment**; each action opens a mapped draft with its source relationship, shared operational fields, and Job route stops prefilled. |
| LOGIX-022 | Add Trip Plan and Shipment-to-Trip planning actions | High | Ready for Production Verification | Trip Plan is branch-scoped and available under Workspace Operations; a Shipment provides **Create → Trip Plan** and **Create → Trip** using its remaining cargo and stop sequence; a Trip Plan provides **Create → Trip**, preserving resource, schedule, allocation, and source-plan details. |
| LOGIX-023 | Create POD from Trip | High | Ready for Production Verification | A saved, non-cancelled Trip provides **Create → POD**; multi-shipment Trips prompt for the Shipment, the POD is prefilled from its active allocation, and server validation enforces Trip/Shipment/Branch integrity, evidence on submit, quantity limits, and one active POD per Trip/Shipment. |
| LOGIX-024 | Create Sales Invoice from POD | High | Ready for Production Verification | A verified, submitted POD provides **Create → Sales Invoice** for users with invoice-create permission; the draft uses the configured Transport Service Item and Job Agreed Revenue, retains POD/Trip/Shipment/Job links, calculates totals, and blocks duplicate active invoices. |
| LOGIX-025 | Visualize Estimation vehicle loading | High | Ready for Production Verification | Estimation calculates weight and CBM utilization from the selected Vehicle Type, uses the higher percentage as effective loading, and renders a responsive lorry whose used portion is red and available portion green; over-capacity behavior follows Logix Settings. |
| LOGIX-026 | Implement vehicle and trip fuel-consumption management | High | Ready for Production Verification | A Fuel Transaction links Vehicle, Driver, and Trip; derives odometer distance, fuel cost, km/L efficiency, variance, and abnormal consumption; creates one traceable Purchase Invoice; and is available with Fuel Analytics in the Logix Workspace. |

## Production verification checklist

- [ ] Deploy the updated Logix app revision to production.
- [ ] Run `bench --site <production-site> migrate`.
- [ ] Run `bench --site <production-site> clear-cache`.
- [ ] Run `bench restart` using the production process manager.
- [ ] Confirm Workspace `Logix` exists, is public, and is not hidden.
- [ ] Confirm the Workspace contains 33 links and 4 shortcuts.
- [ ] Confirm visibility as System Manager.
- [ ] Confirm visibility and branch isolation as a normal Logix user.
- [ ] Create a Rate Card and verify an Estimation calculation.
- [ ] Verify Manual pricing is allowed or blocked according to Logix Settings.
- [ ] Confirm Administrator has full access to Logix City, Logix Load Type, and all other standalone Logix DocTypes.
- [ ] Confirm the eleven numbered Logix DocTypes appear in Document Naming Settings with the packaged defaults.
- [ ] Confirm draft Estimations do not appear in the Job Estimation link or Fetch From dialog.
- [ ] From a submitted Estimation, use **Create → Job** and verify all mapped values.
- [ ] From a draft Job, use **Fetch From → Estimation** and verify all mapped values.
- [ ] Confirm a draft, cancelled, or already-used Estimation is rejected server-side during Job save.
- [ ] From a saved Job, use **Create → Shipment Order** and verify Job, Customer, and Branch are prefilled.
- [ ] From a saved Job, use **Create → Shipment** and verify Job details plus pickup/delivery stops are prefilled.
- [ ] From a saved Shipment Order, use **Create → Shipment** and verify the Shipment Order, cargo values, Job load type, and route stops are prefilled.
- [ ] Confirm Trip Plan appears under the Workspace Operations card and respects branch permissions.
- [ ] From a Shipment with remaining cargo, use **Create → Trip Plan** and **Create → Trip** and verify its allocation and stop sequences are prefilled.
- [ ] From a saved Trip Plan, use **Create → Trip** and verify the Trip Plan link, resources, schedule, and allocations are preserved.
- [ ] From a saved Trip, use **Create → POD**; verify single-shipment prefilling, multi-shipment selection, signature/attachment submission, and duplicate prevention.
- [ ] Configure the Transport Service Item, then from a verified POD use **Create → Sales Invoice** and verify the customer, service item, Job revenue, total, and Logix source links.
- [ ] On Estimation, verify the lorry is half red/half green at 50%, fully red at 100%, identifies whether weight or CBM is limiting, and applies Block/Warn/Allow above capacity.
- [ ] Configure the Default Fuel Item, default fuel efficiency, abnormal threshold, and a vehicle-specific efficiency target in Logix Settings/Vehicle.
- [ ] From an assigned Trip, create and submit a Fuel Transaction; verify odometer distance, litres, total cost, actual km/L, variance, and abnormal flag.
- [ ] From the submitted Fuel Transaction, create a Purchase Invoice and verify Supplier, fuel Item, quantity, rate, total, and source link.
- [ ] Open Fuel Analytics from Fleet & Resources and verify date, branch, vehicle, driver, and abnormal-only filters.
- [ ] Run `bench --site <production-site> run-tests --app logix` in an approved non-live test environment.

## Verification evidence

- Local migration: passing.
- Asset build: passing.
- Administrator permissions: 17 standalone DocTypes defined with explicit full access.
- Naming Series defaults: all 11 defined with app-managed defaults.
- Naming Series upgrade patch: executed successfully on `logix.localhost`.
- Naming counter migration: native counter keys synchronized with the highest existing Logix document numbers.
- Job workflow test module: 10 tests passing, covering Estimation eligibility/mapping, vehicle capacity utilization, downstream Shipment creation, all three Trip planning paths, Trip-to-POD creation/submission, and POD-to-Sales-Invoice mapping.
- Full Logix suite: 14 tests passing after local migration.
- Downstream creation regression coverage maps Job to Shipment Order/Shipment and Shipment Order to Shipment, including source links, shared fields, cargo values, load type, and route stops.
- Python compilation, JavaScript syntax checks, JSON parsing, and `git diff --check`: passing.
- Workspace metadata: public `1`, hidden `0`, module `Logix`.
- Workspace content: 33 links and 4 shortcuts verified in live metadata on `logix.localhost`.
- Fuel management implementation: automated coverage added for trip/resource validation inputs, odometer distance, cost, efficiency variance, abnormal detection, Vehicle odometer update, and Purchase Invoice mapping; production verification remains pending.

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
| Logix Trip Plan | `TPL-.YYYY.-` |
| Logix POD | `POD-.YYYY.-` |
| Logix Fuel Transaction | `FUEL-.YYYY.-` |

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

### Job and Shipment Order downstream creation

- Added **Create → Shipment Order** and **Create → Shipment** to saved, non-cancelled Jobs.
- Added **Create → Shipment** to saved, non-cancelled Shipment Orders.
- Added permission-checked server-side mappers for all three creation paths.
- Job-based Shipments inherit Job, Customer, Branch, Load Type, and pickup/delivery stops from the Job route.
- Shipment Order-based Shipments inherit the Shipment Order and Job links, cargo quantities and measurements, Job Load Type, and pickup/delivery stops from the Job route.

### Trip planning workflow

- Added the submittable, branch-scoped Logix Trip Plan DocType with resource, schedule, notes, and shipment allocation fields.
- Added Trip Plan to the Workspace Operations card and linked generated Trips back through `Logix Trip.trip_plan`.
- Added **Create → Trip Plan** and **Create → Trip** to Shipments with remaining cargo.
- Added **Create → Trip** to saved, non-cancelled Trip Plans.
- Shipment mappings allocate only remaining cargo and carry proportional weight, CBM, pallets, and pickup/delivery stop sequences.

### Trip-to-POD workflow

- Added the submittable, branch-scoped Logix POD DocType with recipient, delivery outcome, delivered quantity, signature, attachment, and remarks fields.
- Added **Create → POD** to saved, non-cancelled Trips; Trips with multiple active Shipments prompt the user to select one.
- POD drafts inherit Trip, Shipment, Job, Customer, Branch, and allocated quantity.
- Server validation prevents cross-Trip/cross-Branch records, over-delivery, missing submission evidence, and duplicate active PODs for the same Trip and Shipment.

### POD-to-Sales-Invoice workflow

- Added **Create → Sales Invoice** to verified, submitted PODs for users who can create Sales Invoices.
- Sales Invoice drafts use the Logix Settings Transport Service Item and the Job's Agreed Revenue, with quantity one and calculated totals.
- Added read-only POD, Trip, Shipment, and Job links to Sales Invoice through upgrade patch `v1_0_7_add_sales_invoice_logix_links`.
- Server validation requires a verified POD, an enabled sales Item, positive Job revenue, a default Company, source read access, and Sales Invoice create permission.
- A second non-cancelled Sales Invoice cannot be created from the same POD.

### Estimation vehicle capacity visualization

- Added read-only weight, volume, effective loading, and limiting-dimension fields to Estimation.
- Effective loading is the higher of weight utilization and CBM utilization against the selected Vehicle Type capacities.
- Added a responsive code-native lorry graphic: the loaded percentage is red and the remaining percentage is green, with separate weight and volume indicators.
- At 100% the lorry body is fully red; percentages above 100% remain fully red and show an over-capacity status.
- Activated the Logix Settings Vehicle Capacity Behavior: `Block` rejects over-capacity Estimations, `Warn` displays a warning, and `Allow` permits them silently.
- Automated tests cover 50% volume loading, 100% weight loading, limiting-dimension selection, and blocking above capacity. Live browser visual QA remains in the production verification checklist.

### Fuel consumption management

- Added the submittable, branch-scoped Logix Fuel Transaction linking Trip, Vehicle, Driver, odometer reading, litres, supplier, fuel Item, and rate.
- Previous odometer and travelled distance are derived from submitted vehicle fuel history, falling back to the Vehicle's last odometer for its first fuel record.
- Total cost and actual km/L are calculated server-side; expected km/L comes from the Vehicle target or the Logix Settings fallback.
- Consumption is flagged as abnormal when its efficiency shortfall exceeds the configurable variance threshold.
- Submitted fuel records update the Vehicle's last odometer and can create one traceable ERPNext Purchase Invoice using the recorded litres and rate.
- Added Fuel Transaction and Fuel Analytics to the Workspace's Fleet & Resources card; the report supports date, branch, vehicle, driver, and abnormal-only filters while enforcing branch access.

## Maintenance rules

- Add one row for each defect or requested change.
- Do not mark production items **Done** until production evidence is recorded.
- Link code changes, patches, and test names in the issue notes when the repository gains a remote issue system.
- Keep architectural phase tracking in `LOGIX_IMPLEMENTATION.md`; use this file for actionable issues and acceptance checks.
