# Logix

Logix is a Frappe/ERPNext v15 logistics extension for freight forwarding, transport dispatch, shipment tracking, resource costing, billing preparation, and space rental.

## Development installation

```bash
bench get-app <repository-url> --branch develop
bench --site logix.localhost install-app logix
bench --site logix.localhost set-config developer_mode 1
bench --site logix.localhost migrate
bench build
```

Configure Logix Settings and create Branch user permissions before operational use. Map service Items there rather than relying on hard-coded Item codes.

## Development and tests

```bash
bench start
bench --site logix.localhost migrate
bench --site logix.localhost run-tests --app logix
bench build
```

Public tracking uses random tokens and returns only an explicit safe field set. Keep expiry enabled, regenerate compromised links, and never expose internal Shipment documents to Guest. User-facing strings use Frappe translation wrappers; Arabic translations and RTL visual QA remain pending.

Before upgrades, back up the site, update compatible version-15 branches, run migrations and assets, then run the full app test suite. See `LOGIX_IMPLEMENTATION.md` for implemented scope and known gaps.

License: MIT.
# Logix
