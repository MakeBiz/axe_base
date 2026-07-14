# TOOLS.md - Дашборд

## PostgreSQL

- Database: `vitrina_db`
- User: `vitrina_user`
- Secret file: `/root/.secrets/vitrina_db.env`
- Host: `127.0.0.1`
- Port: `5432`
- Пароли читать только из защищённых файлов в `/root/.secrets`
- Не печатать секреты в вывод, логи или отчёты

## Sources

- Google Sheets: чтение
- Google Drive: чтение
- Банк, приложения и внешние API подключаются по одному после выдачи доступов

## Delivery

- No chat binding
- Daily refresh cron is created disabled until Anton confirms time
- On-demand run goes through Aks or direct agent invocation
