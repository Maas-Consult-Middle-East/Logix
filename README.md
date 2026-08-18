# Logix

Logix is a Frappe/ERPNext v15 logistics extension for customer Contract Rates, commercial Estimations, transport Jobs, dispatch, shipment tracking, costing, billing preparation, and fuel operations.

## Commercial workflow

Create a Customer-specific `Logix Contract Rate`, set its currency and applicable dates, and add Route, Weight, or CBM Contract Services. On `Logix Estimation`, select Customer, Estimation Date, Currency, and an eligible Contract Rate; then add Estimation Items, taxes/charges, and an optional additional discount. Authorized managers can auditably override a contract-derived rate. Accepted, submitted, unexpired Estimations can create a draft Job, which appears in Connections.

The Estimation form has four tabs: Commercial, Costing & Profitability, References / Additional Information, and Connections. Cost/profit information is permission- and setting-controlled and is excluded from the customer print format.

## Development installation

```bash
bench get-app <repository-url> --branch develop
bench --site logix.localhost install-app logix
bench --site logix.localhost set-config developer_mode 1
bench --site logix.localhost migrate
bench build
```

Configure Logix Settings, Customer Contract Rates, service Items, and Branch user permissions before operational use. Do not hard-code accounting Items or use the hidden legacy Transport Rate Card archive for new pricing.

## Verification

```bash
bench --site logix.localhost migrate
bench build
bench --site logix.localhost clear-cache
bench --site logix.localhost run-tests --app logix
```

Before upgrades, back up the site and review `LOGIX_IMPLEMENTATION.md`, especially the legacy Contract Rate migration behavior. Public tracking uses random, expiring tokens and returns an allowlisted response.

License: MIT.
