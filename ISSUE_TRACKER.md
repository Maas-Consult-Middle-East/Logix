# Logix Issue Tracker

Last updated: 2026-08-18

Status definitions: **Done**, **In Progress**, **Ready for Production Verification**, **Backlog**, **Superseded**.

## Current change set

| ID | Issue | Priority | Status | Acceptance criteria |
|---|---|---:|---|---|
| LOGIX-001 | Provision the Logix Workspace on every fresh app installation | Critical | Done | `install-app logix` creates the public Workspace, its commercial/operational links, 5 shortcuts, and role access without a manual command. |
| LOGIX-002 | Repair or provision the Workspace on existing installations | Critical | Done | `bench --site <site> migrate` idempotently creates or repairs the Workspace through `after_migrate`. |
| LOGIX-003 | Make the Workspace visible to production administrators | High | Done | System Manager and all Logix operational roles can see the Workspace; it is public and not hidden. |
| LOGIX-004 | Prevent unrelated system records from entering Logix fixtures | High | Done | Exports contain only the Logix Workspace, Logix roles, and `logix_*` Custom Fields. |
| LOGIX-005 | Populate Workspace navigation | High | Done | Commercial, Operations, Fleet & Resources, Masters, Billing, and Setup cards resolve to existing records. |
| LOGIX-006 | Add a default Branch field to User | High | Done | `User.logix_branch` links to Branch and participates in branch access alongside native User Permissions. |
| LOGIX-007 | Integrate manually added Estimation transport fields | High | Superseded | Replaced by `Logix Estimation Item`, which carries Bill By, route, vehicle/load, weight/UOM, CBM, quantity, rate, stops, description, amount, and pricing provenance per service line. |
| LOGIX-008 | Calculate Estimation selling price from Rate Cards | Critical | Superseded | The active generic Rate Card engine was replaced by the explicitly selected, customer/date/currency-specific Contract Rate engine in LOGIX-030 and LOGIX-032. |
| LOGIX-009 | Preserve controlled manual Estimation pricing | High | Done | Manual child rows require the Logix setting plus an authorized commercial role; quantity/rate calculate server-side and Contract Rate overrides require manager role, reason, user, and timestamp. |
| LOGIX-010 | Safely migrate legacy Estimation measurement text | High | Done | Patch `v1_0_3_normalize_estimation_measurements` preserves records and converts legacy weight/CBM values before schema synchronization. |
| LOGIX-011 | Map Estimation commercial values into Job creation | High | Done | Both Job creation paths map source Estimation, customer, branch, first operational route, Contract Rate, currency, net total, discount, taxes, grand total, service summary, and permitted cost while keeping the Job Draft. |
| LOGIX-012 | Improve Apply Rate Card behavior on incomplete forms | Medium | Superseded | **Apply Rate Card** was removed; users explicitly select an eligible Contract Rate and contract-derived item rows are priced by the canonical backend service. |
| LOGIX-013 | Verify the Workspace on the production site | Critical | Ready for Production Verification | Updated app code is deployed; migrate/cache clear/restart complete; a System Manager and one Logix role can open the Workspace. |
| LOGIX-014 | Expand Estimation pricing regression coverage | Medium | Done | Tests cover tab structure, customer/currency/date isolation, Route/Weight/CBM/Manual pricing, bad routes, overrides, manual/discount permissions, taxes, both discount bases, amount/percentage synchronization, profitability, and Job mapping. |
| LOGIX-015 | Give Administrator explicit full access to every Logix DocType | Critical | Done | Every active standalone Logix DocType contains explicit Administrator access; transaction DocTypes grant submit/cancel/amend, level-1 financial fields are accessible, and child tables inherit access from their parents. Logix branch hooks explicitly bypass Administrator. |
| LOGIX-016 | Package Logix Naming Series with the app | High | Done | Twelve numbered/archived DocTypes use native `naming_series:` fields with app-managed defaults; patches backfill original records and initialize native counters from the highest existing suffix to prevent restarts and duplicate names. |
| LOGIX-017 | Restrict Job creation to eligible Estimations | Critical | Done | UI and server require submitted, Accepted, unexpired, customer-matched Estimations; transactional row locking plus duplicate validation protects concurrent creation while historical multiple connections remain visible. |
| LOGIX-018 | Add Create Job action to accepted Estimation | High | Done | An Accepted, submitted Estimation provides **Create → Job**, opening a mapped unsaved Job for review; expiry and existing connections are revalidated server-side. |
| LOGIX-019 | Add Fetch From Estimation to Job | High | Done | A draft Job provides **Fetch From → Estimation**, filtered to Accepted/unexpired records, and maps through the same permission-checked backend method. |
| LOGIX-020 | Name City and Load Type masters by their title fields | High | Done | New Logix City records use `city_name`, new Logix Load Type records use `load_type_name`, both fields are unique, and patch `v1_0_6_name_logix_masters_by_title` renames legacy hash-named records while updating links. |
| LOGIX-021 | Add downstream Create actions to Jobs and Shipment Orders | High | Ready for Production Verification | A saved active Job provides **Create → Shipment Order** and **Create → Shipment**; a saved active Shipment Order provides **Create → Shipment**; each action opens a mapped draft with its source relationship, shared operational fields, and Job route stops prefilled. |
| LOGIX-022 | Add Trip Plan and Shipment-to-Trip planning actions | High | Ready for Production Verification | Trip Plan is branch-scoped and available under Workspace Operations; a Shipment provides **Create → Trip Plan** and **Create → Trip** using its remaining cargo and stop sequence; a Trip Plan provides **Create → Trip**, preserving resource, schedule, allocation, and source-plan details. |
| LOGIX-023 | Create POD from Trip | High | Ready for Production Verification | A saved, non-cancelled Trip provides **Create → POD**; multi-shipment Trips prompt for the Shipment, the POD is prefilled from its active allocation, and server validation enforces Trip/Shipment/Branch integrity, evidence on submit, quantity limits, and one active POD per Trip/Shipment. |
| LOGIX-024 | Create Sales Invoice from POD | High | Ready for Production Verification | A verified POD creates a Draft Sales Invoice using agreed Estimation service rows, tax proposal, discount basis/amount, currency, and POD/Trip/Shipment/Job/Estimation/Contract Rate references; duplicate active invoices remain blocked. |
| LOGIX-025 | Visualize Estimation vehicle loading | High | Superseded | The header-level single-vehicle visualization was retired by the multi-line commercial model. Any future capacity visualization should operate per service line or in the operational Job/Shipment workflow. |
| LOGIX-026 | Implement vehicle and trip fuel-consumption management | High | Ready for Production Verification | A Fuel Transaction links Vehicle, Driver, and Trip; derives odometer distance, fuel cost, km/L efficiency, variance, and abnormal consumption; creates one traceable Purchase Invoice; and is available with Fuel Analytics in the Logix Workspace. |
| LOGIX-027 | Name Routes from their origin and destination cities | High | Ready for Production Verification | New Logix Route records use `From City-To City`; both cities are required and must differ; patch `v1_0_9_name_routes_by_cities` safely renames existing hash-named Routes while updating links. |
| LOGIX-028 | Hide automatic Custom Documents from the Logix Workspace | Medium | Ready for Production Verification | The standard Workspace and fixture set `hide_custom` so Frappe no longer appends its automatic Custom Documents section to Logix navigation. |
| LOGIX-029 | Show Trip Plan vendor details only for outsourced transport | Medium | Ready for Production Verification | Supplier, Vendor Vehicle, and Vendor Driver appear only when Resource Mode is `Outsourced Transport Service`. |
| LOGIX-030 | Replace active Rate Cards with customer Contract Rates | Critical | Done | `Logix Contract Rate` belongs to one Customer, has currency and applicable dates, owns Contract Services, and is the only active pricing source; the legacy DocType is hidden/read-only. |
| LOGIX-031 | Refactor Estimation into the required four-tab form | Critical | Done | Migrated metadata contains exactly Commercial, Costing & Profitability, References / Additional Information, and Connections; Commercial contains General, Items, Taxes & Charges, and Discount & Totals in order. |
| LOGIX-032 | Implement canonical Contract Service pricing | Critical | Done | One backend service validates selected contract/customer/date/currency and prices most-specific Route, exact-UOM Weight, and CBM matches; Manual and Override sources remain traceable. |
| LOGIX-033 | Add Estimation taxes, charges, discounts, and totals | Critical | Done | Logix tax rows support Actual/Net/Previous Amount/Previous Total, standard tax-template copying, Net/Grand Total discount bases, synchronized amount/percentage, and canonical server totals. |
| LOGIX-034 | Secure Estimation costing and profitability | Critical | Done | Revenue excludes tax; profit/margin handle zero revenue; cost fields use level-1 permissions, commercial roles, the visibility setting, protected report columns, and customer-safe printing. |
| LOGIX-035 | Add Estimation connections and downstream locking | Critical | Done | Connections lists every linked Job with navigation and a clean empty state; Job creation is concurrency-protected and key commercial fields lock after downstream progression. |
| LOGIX-036 | Update commercial Workspace, report, and print output | High | Done | Workspace uses Contract Rate terminology and shortcuts; Estimation Commercial Summary includes contract/validity/totals/connections with gated profit; external print excludes internal cost and pricing audit. |
| LOGIX-037 | Safely migrate legacy Rate Card and Estimation data | Critical | Done | Idempotent patches convert customer cards, preserve customerless cards as disabled Requires Review records, retain complex legacy notes, migrate Estimations without repricing history, and clear ineligible active links. |
| LOGIX-038 | Preserve agreed commercial values in Job and Sales Invoice | High | Done | Job snapshots commercial references/totals/service summary; Draft Sales Invoice proposal uses Estimation rows, taxes, discount, currency, and Logix source links for user review. |
| LOGIX-039 | Verify Contract Rate and Estimation UI in a browser | High | Ready for Production Verification | A connected browser confirms exact tabs/sections, dynamic Bill By fields, Contract Rate filters/warnings, tax-template behavior, controlled recalculation, Connections empty/list states, and customer-safe print. |
| LOGIX-040 | Review migrated complex and customerless legacy pricing | High | Ready for Production Verification | Commercial owners review every disabled Requires Review contract and every migrated combined/excess/return note before intentionally enabling or replacing it. |
| LOGIX-041 | Rehome vehicle-capacity visualization for multi-line estimates | Medium | Backlog | Decide whether capacity belongs per Estimation Item or on Job/Shipment, then implement without restoring single-header commercial pricing fields. |

## Production verification checklist

- [ ] Deploy the updated Logix app revision to production.
- [ ] Run `bench --site <production-site> migrate`.
- [ ] Run `bench --site <production-site> clear-cache`.
- [ ] Run `bench restart` using the production process manager.
- [ ] Confirm Workspace `Logix` exists, is public, and is not hidden.
- [ ] Confirm the Workspace provides Estimations, Contract Rates, and Jobs and contains 5 shortcuts.
- [ ] Confirm visibility as System Manager.
- [ ] Confirm visibility and branch isolation as a normal Logix user.
- [ ] Create Customer A/B Contract Rates and confirm each is selectable only for its own Customer, currency, and validity period.
- [ ] Confirm Estimation has exactly four tabs and Commercial contains General, Estimation Items, Taxes & Charges, and Discount & Totals in order.
- [ ] Verify Route, Weight, CBM, and Manual item behavior; confirm a mismatched route/UOM/customer/currency/date is rejected server-side.
- [ ] Verify Manual pricing and Contract Rate overrides are allowed or blocked by settings/roles and overrides require an audit reason.
- [ ] Apply a Sales Taxes and Charges Template, test all supported charge bases, and verify Net Total and Grand Total discount behavior.
- [ ] Confirm tax does not increase Estimated Selling Value Excluding Tax, Estimated Profit, or Estimated Margin.
- [ ] Confirm Administrator has full access to Contract Rate, Estimation, Job, and all other active standalone Logix DocTypes.
- [ ] Confirm active numbered Logix DocTypes, including Contract Rate, appear in Document Naming Settings with packaged defaults.
- [ ] Confirm draft, unaccepted, expired, and already-used Estimations are rejected by Job creation.
- [ ] From an Accepted submitted Estimation, use **Create → Job** and verify commercial references, route, currency, totals, service summary, and permitted cost.
- [ ] From a draft Job, use **Fetch From → Estimation** and verify all mapped values.
- [ ] Verify Connections shows a clean empty state before Job creation and every connected Job afterward; verify commercial editing is locked after progression.
- [ ] From a saved Job, use **Create → Shipment Order** and verify Job, Customer, and Branch are prefilled.
- [ ] From a saved Job, use **Create → Shipment** and verify Job details plus pickup/delivery stops are prefilled.
- [ ] From a saved Shipment Order, use **Create → Shipment** and verify the Shipment Order, cargo values, Job load type, and route stops are prefilled.
- [ ] Confirm Trip Plan appears under the Workspace Operations card and respects branch permissions.
- [ ] From a Shipment with remaining cargo, use **Create → Trip Plan** and **Create → Trip** and verify its allocation and stop sequences are prefilled.
- [ ] From a saved Trip Plan, use **Create → Trip** and verify the Trip Plan link, resources, schedule, and allocations are preserved.
- [ ] From a saved Trip, use **Create → POD**; verify single-shipment prefilling, multi-shipment selection, signature/attachment submission, and duplicate prevention.
- [ ] Configure the Transport Service Item, then from a verified POD use **Create → Sales Invoice** and verify Estimation service rows, taxes, discount, currency, total, and all Logix source links.
- [ ] Verify `Logix Estimation Commercial` print includes customer-facing dates/items/taxes/discount/terms and excludes costs, margins, internal notes, and pricing audit fields.
- [ ] Review all migrated Contract Rates marked Requires Review before enabling or replacing them.
- [ ] Configure the Default Fuel Item, default fuel efficiency, abnormal threshold, and a vehicle-specific efficiency target in Logix Settings/Vehicle.
- [ ] From an assigned Trip, create and submit a Fuel Transaction; verify odometer distance, litres, total cost, actual km/L, variance, and abnormal flag.
- [ ] From the submitted Fuel Transaction, create a Purchase Invoice and verify Supplier, fuel Item, quantity, rate, total, and source link.
- [ ] Open Fuel Analytics from Fleet & Resources and verify date, branch, vehicle, driver, and abnormal-only filters.
- [ ] Create a Logix Route and verify its name is `From City-To City`; confirm same-city Routes are rejected and existing Route links remain valid.
- [ ] Confirm the Logix Workspace does not display Frappe's automatic Custom Documents section.
- [ ] On Trip Plan, confirm Supplier, Vendor Vehicle, and Vendor Driver are hidden for internal/contracted modes and shown for Outsourced Transport Service.
- [ ] Run `bench --site <production-site> run-tests --app logix` in an approved non-live test environment.

## Verification evidence

- Local migration: passing.
- Asset build: passing (unrelated dependency audit warnings remain in URY apps).
- Administrator permissions: all active standalone DocTypes define explicit appropriate access.
- Naming Series defaults: Contract Rate uses `CR-.YYYY.-`; previous defaults remain app-managed.
- Naming Series upgrade patch: executed successfully on `logix.localhost`.
- Naming counter migration: native counter keys synchronized with the highest existing Logix document numbers.
- Job/operations coverage includes Estimation eligibility/mapping, downstream Shipment creation, all three Trip planning paths, Trip-to-POD creation/submission, and POD-to-Sales-Invoice mapping.
- Full Logix suite: 20 tests passing after migration, build, and cache clear.
- Downstream creation regression coverage maps Job to Shipment Order/Shipment and Shipment Order to Shipment, including source links, shared fields, cargo values, load type, and route stops.
- Python compilation, JavaScript syntax checks, JSON parsing, and `git diff --check`: passing.
- Workspace metadata: public `1`, hidden `0`, module `Logix`.
- Workspace content: Contract Rate replaces Transport Rate Card and the source/fixture provides 5 shortcuts.
- Route naming: existing local Routes migrated to `From City-To City`; focused Route naming test and full Logix suite pass.
- Workspace custom content: `hide_custom` verified as `1` in live `logix.localhost` metadata.
- Trip Plan outsourced fields: Supplier, Vendor Vehicle, and Vendor Driver conditions verified in live DocField metadata.
- Fuel management implementation: automated coverage added for trip/resource validation inputs, odometer distance, cost, efficiency variance, abnormal detection, Vehicle odometer update, and Purchase Invoice mapping; production verification remains pending.
- Commercial schema: live metadata contains `Logix Contract Rate`, `Logix Contract Service`, `Logix Estimation Item`, and `Logix Estimation Tax and Charge`; the Estimation tab-order regression passes.
- Commercial migration: patches `v1_1_0` through `v1_1_3` executed successfully on `logix.localhost`.
- Static verification: Python compilation, JSON parsing, JavaScript syntax checks, and `git diff --check` pass.
- Browser verification: blocked locally because the in-app browser runtime exposed no browser instance; LOGIX-039 remains Ready for Production Verification.

## Current change details

### Contract Rate commercial refactor

- Added customer/date/currency-specific `Logix Contract Rate` with `Logix Contract Service` Route, Weight, and CBM rules.
- Rebuilt Estimation around item, tax/charge, discount/total, cost-breakdown, references, and Connections structures while retaining exactly four top-level tabs.
- Centralized matching and calculations in `logix.services.contract_pricing` and the Estimation controller; client scripts provide filtering, visibility, warnings, recalculation, and connection rendering only.
- Added pricing provenance and audited manager overrides, configurable validity defaults, exact currency/UOM validation, tax-template copying, two discount bases, and tax-exclusive profitability.
- Added customer-safe printing, permission-aware commercial reporting, Workspace Contract Rate navigation, and Job/Sales Invoice commercial references.
- Added idempotent migration/permission patches `v1_1_0` through `v1_1_3`; legacy pricing remains archived and customerless/ineligible contracts cannot become silently active.

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
| Logix Contract Rate | `CR-.YYYY.-` |
| Logix Transport Rate Card (archived legacy data) | `TRC-` |
| Logix Trip Plan | `TPL-.YYYY.-` |
| Logix POD | `POD-.YYYY.-` |
| Logix Fuel Transaction | `FUEL-.YYYY.-` |

### Estimation-to-Job workflow

- Added an Accepted, submitted, unexpired query for the Job Estimation link.
- Added **Create → Job** to eligible Estimations.
- Added **Fetch From → Estimation** to draft Jobs.
- Added a shared server-side mapper used by both actions.
- Added server-side customer/status/date/connection checks so UI filters cannot be bypassed, plus transactional source-row locking for concurrent creation.
- Mapping now preserves Contract Rate, currency, commercial totals, discount, taxes, service summary, route, and permitted cost while keeping the Job Draft.
- Connections queries all Jobs by source Estimation, and protected commercial fields lock after any downstream Job exists.

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
- Sales Invoice drafts use the configured Transport Service Item with one row per agreed Estimation service, proposed Estimation taxes/discount, and calculated totals.
- Added read-only POD, Trip, Shipment, Job, Estimation, and Contract Rate links through upgrade patches.
- Server validation requires a verified POD, an enabled sales Item, positive Job revenue, a default Company, source read access, and Sales Invoice create permission.
- A second non-cancelled Sales Invoice cannot be created from the same POD.

### Estimation vehicle capacity visualization

- The previous single-header capacity fields and lorry visualization are retained only as hidden legacy schema so historical columns are not destructively dropped.
- They are not part of the new multi-line Estimation commercial workflow.
- LOGIX-041 tracks a future decision to implement capacity per Estimation Item or in the operational Job/Shipment workflow.

### Fuel consumption management

- Added the submittable, branch-scoped Logix Fuel Transaction linking Trip, Vehicle, Driver, odometer reading, litres, supplier, fuel Item, and rate.
- Previous odometer and travelled distance are derived from submitted vehicle fuel history, falling back to the Vehicle's last odometer for its first fuel record.
- Total cost and actual km/L are calculated server-side; expected km/L comes from the Vehicle target or the Logix Settings fallback.
- Consumption is flagged as abnormal when its efficiency shortfall exceeds the configurable variance threshold.
- Submitted fuel records update the Vehicle's last odometer and can create one traceable ERPNext Purchase Invoice using the recorded litres and rate.
- Added Fuel Transaction and Fuel Analytics to the Workspace's Fleet & Resources card; the report supports date, branch, vehicle, driver, and abnormal-only filters while enforcing branch access.

### Route naming and Workspace cleanup

- Changed Logix Route naming from generated hashes to `From City-To City`.
- Made From City and To City mandatory and rejected Routes whose origin and destination are identical.
- Added patch `v1_0_9_name_routes_by_cities` to rename existing Routes and update their links.
- Enabled `hide_custom` in both Logix Workspace definitions to remove Frappe's automatic Custom Documents section.

### Trip Plan outsourced resource fields

- Supplier, Vendor Vehicle, and Vendor Driver now depend on Resource Mode being `Outsourced Transport Service`.
- Other resource modes no longer display these vendor-specific fields.

## Maintenance rules

- Add one row for each defect or requested change.
- Do not mark production items **Done** until production evidence is recorded.
- Link code changes, patches, and test names in the issue notes when the repository gains a remote issue system.
- Keep architectural phase tracking in `LOGIX_IMPLEMENTATION.md`; use this file for actionable issues and acceptance checks.
