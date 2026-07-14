import os, asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
d={}
for line in open('/root/transcriber/.login_tmp'):
    k,_,v=line.strip().partition('=')
    d[k]=v
api_id=int(os.environ['TG_API_ID']); api_hash=os.environ['TG_API_HASH']
code=os.environ['CODE']
twofa=os.environ.get('TWOFA','')
async def main():
    c=TelegramClient(StringSession(d['SESSION1']), api_id, api_hash)
    await c.connect()
    try:
        await c.sign_in(phone=d['PHONE'], code=code, phone_code_hash=d['HASH'])
    except SessionPasswordNeededError:
        if not twofa:
            print('NEED_2FA'); await c.disconnect(); return
        await c.sign_in(password=twofa)
    me=await c.get_me()
    fs=c.session.save()
    envp='/root/.secrets/transcriber.env'
    lines=[l for l in open(envp) if not l.startswith('TG_SESSION=')]
    lines.append('TG_SESSION='+fs+'\n')
    open(envp,'w').writelines(lines); os.chmod(envp,0o600)
    try: os.remove('/root/transcriber/.login_tmp')
    except Exception: pass
    print('LOGGED_IN_AS='+str(me.username or me.id))
    print('SESSION_SAVED len='+str(len(fs)))
    await c.disconnect()
asyncio.run(main())
