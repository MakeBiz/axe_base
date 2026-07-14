# TOOLS.md

## Bitrix

- Portal: `kilyazoff.bitrix24.ru`
- Secret file: `/root/.secrets/bitrix_biryuza.env`
- Env var: `BIRYUZA_BITRIX_WEBHOOK`
- Never print the webhook or REST token

Allowed CRM methods:

- `crm.deal.list`
- `crm.deal.get`
- `crm.deal.add`
- `crm.deal.update`
- `crm.lead.list`
- `crm.lead.get`
- `crm.lead.add`
- `crm.lead.update`
- `crm.timeline.comment.add`
- `crm.status.list`
- `crm.category.list`
- `crm.contact.*`
- `crm.company.*`

## Postgres

- Secret file: `/root/.secrets/vitrina_db.env`
- Database: `vitrina_db`
- Schema: `crm`
- Portal value: `kilyazoff`

Tables:

- `crm.deals`
- `crm.leads`

## Local Tools

- CRM sync: `/root/.openclaw/workspace-biryuza/tools/sync_crm_to_postgres.sh`
