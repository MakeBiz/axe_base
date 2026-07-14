import os, asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
async def main():
    c=TelegramClient(StringSession(), int(os.environ['TG_API_ID']), os.environ['TG_API_HASH'])
    await c.start(bot_token=os.environ['TG_BOT_TOKEN'])
    me=await c.get_me()
    print('BOT_OK', me.username, me.id)
    await c.disconnect()
asyncio.run(main())
