# LOGIX_IMPLEMENTATION

## Architecture

Logix is an installable Frappe/ERPNext v15 app. ERPNext owns accounting plus standard Customer, Company, Branch, Currency, Contact, Address, Sales Person, Terms and Conditions, tax templates, Item, Sales Invoice, and Purchase Invoice records. Logix owns commercial logistics agreements, estimations, jobs, and operational documents. Server-side Python controllers and services are authoritative; no Frappe or ERPNext core code is modified.

## Commercial model

The active flow is Customer → Contract Rate → Contract Services → Estimation → Estimation Items → Taxes and Charges → Discount → Commercial Total → Costing and Profitability → Acceptance → Job.

- `Logix Contract Rate` is customer-specific, currency-specific, date-bounded, and can be disabled. It owns `Logix Contract Service` rules.
- Contract Services consistently use Bill By `Route`, `Weight`, or `CBM`. Route rules support controlled vehicle/load fallbacks, minimum charge, and an optional extra-stop rate. Weight rules require an exact UOM because automatic currency/UOM conversion is intentionally not implemented.
- `Logix Estimation Item` supports `Route`, `Weight`, `CBM`, and permission-controlled `Manual` billing. Every row records Contract Rate, Manual, or Override pricing provenance; overrides retain suggested rate, reason, user, and timestamp.
- `logix.services.contract_pricing` is the single active pricing engine. It validates customer, currency, estimation date, contract dates, disabled/review state, and most-specific service matching.
- Estimation totals use one server calculation path: item amounts → net total → taxes/charges → additional discount by selected basis → grand total. Profitability uses selling value excluding tax, so tax does not inflate revenue or margin.

## Estimation form

`Logix Estimation` has exactly four top-level tabs:

1. Commercial: General, Estimation Items, Taxes & Charges, Discount & Totals.
2. Costing & Profitability.
3. References / Additional Information.
4. Connections.

Estimation Date defaults to today. Valid Until defaults using `Logix Settings.default_estimation_validity_days` (30 only as a configurable schema default) and cannot precede Estimation Date. The selected Contract Rate must match the Estimation customer/currency and cover Estimation Date. The client filters eligible contracts, while the server repeats all checks.

Sales Taxes and Charges Template rows are copied into the Logix-owned tax table; the template is never edited. Supported charge types are Actual, On Net Total, On Previous Row Amount, and On Previous Row Total. Additional discount supports Net Total and Grand Total bases.

Cost fields use permission level 1, commercial-manager roles, and the `estimation_cost_visibility` setting. The commercial report omits cost/profit columns unless both controls allow access. The customer-facing `Logix Estimation Commercial` print format excludes cost, profit, margin, pricing provenance, override audit, and internal notes.

## Job and invoicing integration

Only a submitted, Accepted, unexpired Estimation can create a Job. Job creation locks the source Estimation row during duplicate validation to prevent concurrent duplicate creation. Existing historical multiple-Job connections are preserved; the Connections tab and Frappe dashboard query all Jobs by `Logix Job.estimation` and never rely on the legacy single-link field.

The Job retains source Estimation, customer, branch, currency, Contract Rate, net total, discount basis/amount, taxes, grand total, summarized service lines, and authorized cost. Once any Job exists, ordinary changes to key commercial Estimation fields are rejected; formal revision uses Cancel and Amend.

POD-to-Sales-Invoice mapping remains Draft-only. When a Job has an Estimation, it proposes one invoice row per agreed Estimation service, the Estimation tax rows, discount basis/amount, currency, Job, Estimation, and Contract Rate references. Users review the ERPNext document before submission.

## Legacy migration

`logix.patches.v1_1_0_migrate_contract_rates` is idempotent and preserves legacy data:

- Each customer-linked `Logix Transport Rate Card` becomes a `Logix Contract Rate` with migrated Route and, where present, Weight/CBM rules.
- Customerless legacy cards become disabled Contract Rates marked Requires Review; no Customer is invented.
- Open-ended legacy validity is preserved with a documented `2099-12-31` migration sentinel.
- Complex combined excess/return values are retained in migrated rules/notes for commercial verification.
- Legacy Estimations receive date/company/currency defaults and a Manual child line at the exact prior revenue so historical totals are not silently repriced.
- The old Transport Rate Card DocType remains hidden/read-only as an archive. Its pricing setting is disabled, and it is not an active engine or Workspace destination.

Additional commercial patches add Sales Invoice references and refine customized permission-level access. All patches are registered in `logix/patches.txt`.

## Workspace, report, and print

The Logix Workspace provides Estimations, Contract Rates, and Jobs shortcuts and uses Contract Rate terminology. `Estimation Commercial Summary` reports customer, contract/validity, currency, Bill By, amounts, discounts, taxes, totals, connected Jobs, and permission-gated profitability. `Logix Estimation Commercial` is the external print format.

## Verification status

On 2026-08-18:

- `bench --site logix.localhost migrate`: passed, including legacy migration.
- `bench --site logix.localhost run-tests --app logix`: 20 tests passed.
- Coverage includes exact tab structure, customer/date/currency contract isolation, Route/Weight/CBM/Manual pricing, mismatched route rejection, override audit, taxes, both discount bases, tax-exclusive profitability, Estimation eligibility, Job mapping, and existing operational mappings.
- In-app browser discovery returned no available browser instance. Visual browser inspection could not be performed in this runtime; migrated Frappe metadata is checked programmatically instead.

## Other implemented scope

Logix continues to provide City, Route, Load Type, Vehicle Type, Shipment Order, Shipment, Shipment Stop/Leg/Event, Trip Plan, Trip, allocation, Handover, POD, Fuel Transaction, branch permission hooks, controlled transitions, tracking tokens, and ERPNext billing/purchasing assistants.

## Upgrade notes

Back up the site, update compatible version-15 branches, then run migrate, build, clear-cache, and the complete Logix test suite. Never edit framework core. Production users should review migrated complex/customerless legacy contracts before enabling them.
