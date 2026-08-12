# LOGIX_IMPLEMENTATION

## Architecture

Logix is an installable Frappe/ERPNext v15 app. ERPNext owns accounting and the Customer, Supplier, Branch, Vehicle, Driver, Item, Sales Invoice, and Purchase Invoice masters/transactions. Logix owns commercial and operational logistics records. Business rules live in Python controllers/services; `docstatus` remains separate from operational status.

## Environment

- Bench: `logix-bench`; site: `logix.localhost`; app: `logix`
- Frappe 15.117.0, ERPNext 15.119.0, Logix 0.0.1
- Developer mode and tests enabled

## Implemented inventory

- Foundation: Logix Settings, City, Route, Load Type, Vehicle Type, roles, ERPNext custom fields, branch permission hooks, and a version-controlled Logix Workspace with operational shortcuts and grouped Commercial, Operations, Fleet, Masters, Billing, and Setup cards.
- Commercial: Logix Estimation, Transport Rate Card, Logix Job, customer-default inheritance, estimation requirement/acceptance/locking, rate precedence and weight/CBM/stop/minimum/return pricing service.
- Estimation pricing: route, vehicle/load type, numeric weight/CBM, extra stops, and trip-pricing inputs support server-side Rate Card calculation or explicitly permitted Manual pricing. Applied rate card and currency remain traceable on the Estimation.
- Shipment: Shipment Order, Shipment, Shipment Stop, Shipment Leg, Trip Shipment Allocation, Shipment Event, Handover.
- Trips (foundation): Logix Trip with mixed resource modes, owned/vendor resources, split/shared allocations, and backhaul linkage.
- Security/services: controlled shipment transitions, audited overrides, random public tracking tokens, expiry/revocation checks, allowlisted guest response.

## Status lifecycles

- Estimation: Draft → Submitted → Sent to Customer → Accepted/Rejected.
- Job: Draft → Confirmed → In Progress → Completed; controlled Stopped/Partially Completed/executed-work outcomes require a reason.
- Shipment: centralized transitions from Draft through planning, pickup, transit/handover, delivery/failure/return.
- Trip: Draft → Planned → Assigned → Ready → In Progress → Completed/Stopped.

## Configuration

Estimation requirement and cost visibility, rate-card/manual pricing, capacity behavior, driver-cost profitability, POD invoice gating, recurring generation, tracking expiry, and ERPNext service Item mappings are in Logix Settings.

## Patches

- `logix.patches.v1_0_0_create_logix_roles_and_fields`
- `logix.patches.v1_0_1_create_workspace_and_permissions`
- `logix.patches.v1_0_2_add_branch_to_user` — adds `User.logix_branch` and makes it an accepted source for branch-scoped access alongside native User Permissions.
- `logix.patches.v1_0_3_normalize_estimation_measurements` — safely normalizes legacy Estimation weight and CBM text before numeric schema conversion.

Patches are registered in `patches.txt`; measurement normalization runs before model synchronization and the remaining patches run afterward.

## APIs

- `logix.api.create_job_from_estimation`
- `logix.api.regenerate_tracking_token`
- `logix.api.public_tracking` (guest-safe allowlist)
- `logix.services.pricing.calculate_transport_price`
- `logix.services.events.transition_shipment`

## Development demo data

Run `bench --site logix.localhost execute logix.logix.scripts.seed_demo_data.execute` to create an idempotent, linked sample across every currently implemented Logix DocType. Demo data is deliberately not an install patch and is identified with `Logix Demo` / `LOGIX-DEMO` values.

## Test status

`bench --site logix.localhost run-tests --app logix`: 4 tests passing. Current coverage includes estimation profit/status, Rate Card calculation, and the configurable Job estimation gate. Migration passes.

## Pending phases / known gaps

Phase 4 is partial. Trip Plan, Docket/Waybills/POD/driver UI, costing, storage, billing assistants, SLA/incidents, Control Tower, recurring Jobs, reports, print formats, Arabic/RTL QA, expanded permissions, concurrency locking, and the remaining acceptance suite are not yet implemented. These must not be represented as production-ready.

## Upgrade notes

Never edit Frappe/ERPNext core. Add schema through app DocTypes, registered idempotent patches, and app-managed custom fields. Run migrate, asset build, and the full Logix suite for every upgrade.

Fresh installs run `logix.install.before_install` to provision Workspace role dependencies and `logix.install.after_install` to synchronize the populated Logix Workspace. `logix.install.after_migrate` provides the same idempotent provisioning for existing production sites during upgrades. System Managers and Logix roles can see the Workspace. Fixtures are filtered to Logix-only Custom Fields, Roles, and the Logix Workspace so installing the app cannot import unrelated records from the development site.
