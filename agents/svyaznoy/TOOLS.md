# TOOLS.md - Связной

## Telegram Archive

- Read-only skill: `tg-dialogues`
- Skill file: `/root/.openclaw/workspace/skills/SKILL.md`
- Use through `exec` only
- Never send Telegram messages

## Telegram Delivery

- Primary working chat for Связной: `telegram:-1004084426737`
- Chat title: `Связной`
- Send contact cards, verification questions, contact analytics, new-dialogue monitoring, follow-up reminders, and inventory stage notifications there
- Read and answer Anton's messages in this chat
- Main/Aкс chat can still request contact lookups; return only prepared cards/summaries through Aкс when asked
- Raw Telegram dialogues stay only with Связной

## Google Sheets

- `Связной Контакты`, read/write: `1aMXvwJbS9vt0YnfdKyNBCPY_-X4E_5vwPJb7kg3AQAA`

## SQLite

- Local DB path: `/root/.openclaw/workspace-svyaznoy/data/svyaznoy.sqlite`
- Create it on first use
- Contact card typed fields are guarded by SQLite dictionary tables/triggers
- `sphere`, `main_type`, `partner_status`, and `approval_status` must use approved dictionary values only
- Details that do not fit the dictionaries go to summary/context/tags, not typed fields

## Contact Card Dictionaries

Main type:

- клиент
- лид
- партнёр
- сотрудник
- подрядчик
- личный
- спам
- прочее

Additional roles:

- use the same role dictionary as main type
- multiple roles are allowed only when explicitly confirmed

Partner status:

- не определен
- потенциальный
- действующий
- пассивный
- не партнёр

Card status:

- требует уточнения
- актуальная карточка
- инвентаризация
- обновить позже
- не трогать

Sphere:

- Логистика
- ИТ и телеком
- HoReCa
- Производство
- Оптовая торговля
- Финансы и право
- Недвижимость
- Образование
- Медицина и фарма
- Прочие B2B
- Маркетинг
- Развлечения
- Красота и здоровье

Rules:

- Do not invent typed values
- Every card must include profile fields: username, phone, birthday, bio, and channel_or_site
- If a profile field is not visible, write `не видно` instead of leaving it blank
- Do not put details like design, repairs, flipping, agents, Bitrix, drones, business clubs, or logistics into typed fields unless they are approved dictionary values
- Put extra details into summary, relationship draft, can_help, next_step, or tags
- Do not invent or show subjective scores by default: importance, warmth, connection strength, trust, client potential, intro potential, or numeric ratings
- Show score blocks only when Anton explicitly asks and provides or approves the scale

## Boundaries

- Raw Telegram dialogues stay only with Связной
- Mentor may read contact cards from the spreadsheet, not raw dialogues
- No web, no browser, no outbound Telegram to Anton's contacts
