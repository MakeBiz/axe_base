import os, asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
api_id=int(os.environ['TG_API_ID']); api_hash=os.environ['TG_API_HASH']
phone=os.environ['PHONE']
async def main():
 c=TelegramClient(StringSession(), api_id, api_hash)
 await c.connect()
 sent=await c.send_code_request(phone)
 with open('/root/transcriber/.login_tmp','w') as f:
  f.write('SESSION1='+c.session.save()+'\n')
  f.write('HASH='+sent.phone_code_hash+'\n')
  f.write('PHONE='+phone+'\n')
 os.chmod('/root/transcriber/.login_tmp',0o600)
 print('CODE_SENT_OK via '+type(sent).__name__)
 await c.disconnect()
asyncio.run(main())
