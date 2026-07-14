import os, asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneCodeExpiredError
api_id=int(os.environ['TG_API_ID']); api_hash=os.environ['TG_API_HASH']
phone=os.environ['PHONE']
CODEF='/root/transcriber/.code'; TWOF='/root/transcriber/.twofa'; RES='/root/transcriber/.login_result'
def w(m):
    open(RES,'a').write(m+'\n')
async def wait_file(path,n):
    for _ in range(n):
        if os.path.exists(path):
            v=open(path).read().strip()
            if v: return v
        await asyncio.sleep(2)
    return None
async def main():
    open(RES,'w').write('')
    c=TelegramClient(StringSession(), api_id, api_hash)
    await c.connect()
    sent=await c.send_code_request(phone)
    w('CODE_REQUESTED')
    code=await wait_file(CODEF,240)
    if not code:
        w('NO_CODE_TIMEOUT'); await c.disconnect(); return
    try:
        await c.sign_in(phone=phone, code=code, phone_code_hash=sent.phone_code_hash)
    except PhoneCodeExpiredError:
        w('CODE_EXPIRED'); await c.disconnect(); return
    except SessionPasswordNeededError:
        w('NEED_2FA')
        pwd=await wait_file(TWOF,150)
        if not pwd:
            w('NO_2FA_TIMEOUT'); await c.disconnect(); return
        await c.sign_in(password=pwd)
    me=await c.get_me()
    fs=c.session.save()
    envp='/root/.secrets/transcriber.env'
    lines=[l for l in open(envp) if not l.startswith('TG_SESSION=')]
    lines.append('TG_SESSION='+fs+'\n')
    open(envp,'w').writelines(lines); os.chmod(envp,0o600)
    for p in (CODEF,TWOF):
        try: os.remove(p)
        except Exception: pass
    w('LOGGED_IN_AS='+str(me.username or me.id))
    w('SESSION_SAVED len='+str(len(fs)))
    await c.disconnect()
asyncio.run(main())
