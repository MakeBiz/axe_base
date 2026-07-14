# TOOLS.md - Финансист

## T-Business

- Token file: `/root/.secrets/tbank.env`
- Never print, copy, log, or store the token in config, prompts, reports, or SQLite
- API helper: `/root/.openclaw/workspace-finance/tools/tbank_api.sh`

## Adesk

- Token file: `/root/.secrets/adesk.env`
- Never print, copy, log, or store the token in config, prompts, reports, or SQLite
- API helper: `/root/.openclaw/workspace-finance/tools/adesk_api.sh`
- Sync helper: `/root/.openclaw/workspace-finance/tools/adesk_sync.sh`
- Authentication header: `X-API-Token`
- Read-only endpoints used:
  - `/transactions`
  - `/transactions/categories`
  - `/bank-accounts`
  - `/contractors`
- Use `adesk_sync.sh sync` before Adesk analytics if the local cache may be stale

## SQLite

- Finance database: `/root/.openclaw/workspace-finance/data/finance.sqlite`
- Read/write through `exec`

## Delivery

- Hourly payment monitor: notify main Aks chat only when a new incoming payment is detected
- Financial summary: only on Anton's request, no automatic daily delivery
