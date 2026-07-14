# TOOLS.md - Аналитик

## Postgres

- Database: `vitrina_db`
- Connection env: `/root/.secrets/vitrina_db.env`
- Read raw news from `radar.raw_news`
- Write signals to `analyst.signals`
- Write report to `analyst.daily_report`
- Read finance context from schema `finance`
- Read/write through `exec`

## Google Drive

- Reference document fileId: `11amqqAl_hksy0BxVm-IsUuXlzFihLkF-`

## Delivery

- No chat binding
- Daily report delivery is handled by cron delivery to Telegram group `-1003097588708`
