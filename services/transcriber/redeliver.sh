#!/usr/bin/env bash
set -a; . /root/.secrets/transcriber.env; set +a
TXT=$(cat /root/transcriber/out/32_audio1017221704.m4a.txt)
MSG="Это расшифровка аудиозаписи от Антона. Сделай разбор по своей роли психолога, ответь тепло и по делу. В конце добавь блок Для памяти с 3-6 краткими пунктами самого важного о Антоне из записи.

$TXT"
openclaw agent --agent psychologist --message "$MSG" --deliver --reply-channel telegram --reply-to "$TG_CHAT_ID"
