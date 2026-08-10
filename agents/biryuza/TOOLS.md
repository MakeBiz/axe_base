TOOLS.md

Доступ к Битриксу портала make-biz.bitrix24.ru через админ-вебхук в /root/veha/veha.env (переменная BITRIX_WEBHOOK). Вызов:
  set -a; . /root/veha/veha.env; set +a
  curl -s "$BITRIX_WEBHOOK/<метод>.json" --data-urlencode 'k=v'

Доступен любой REST-метод портала: crm.*, tasks.*, im.*, imbot.*, user.*, department.*, disk.*, calendar.* и другие. Секреты не показывать.
