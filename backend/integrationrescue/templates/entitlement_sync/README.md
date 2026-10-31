# entitlement-sync (fictional customer integration)

Consumes `invoice.paid` webhooks from Billing and grants plans in Entitlements.
Tenant price-to-plan mappings live in `tenants/<tenant>.json`.
Run tests with `python -m pytest -q`.
