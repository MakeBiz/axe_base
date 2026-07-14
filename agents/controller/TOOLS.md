# TOOLS.md - Контролёр

## Sessions

- Может читать историю сессий только для проверки конкретного ответа Акса
- Может возвращать задачу Аксу через session-маршрут, если проверка провалена

## Auditor SQLite

- Database: `/root/.openclaw/workspace-auditor/data/audit.sqlite`
- Writable tables: `events`, `boundary_violations`
- Write through `exec` and `sqlite3`
- Do not store full message text
- Store metadata, short summary, result, error detail, and session reference

## Delivery

- No direct chat binding
- Pre-response integration for `main` is pending engineer-confirmed gateway mechanics
