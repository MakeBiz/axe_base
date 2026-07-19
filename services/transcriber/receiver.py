import os, glob, subprocess, tempfile, traceback, asyncio, shutil, json
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from openai import OpenAI

API_ID=int(os.environ['TG_API_ID']); API_HASH=os.environ['TG_API_HASH']
BOT_TOKEN=os.environ['TG_BOT_TOKEN']; CHAT_ID=int(os.environ['TG_CHAT_ID'])
OPENCLAW=os.environ.get('OPENCLAW_BIN','openclaw')
oai=OpenAI(api_key=os.environ['OPENAI_API_KEY'])
INC='/root/transcriber/incoming'; OUT='/root/transcriber/out'
os.makedirs(INC,exist_ok=True); os.makedirs(OUT,exist_ok=True)
REPLY_TO={'psychologist':CHAT_ID,'mentor':CHAT_ID,'project':-1004330023926}
MEM={'psychologist':('/root/.secrets/psych_mem.env','psych.notes',('theme','note','source'),'аудиозапись'),
     'mentor':('/root/.secrets/mentor_mem.env','mentor.memory',('topic','content','source'),'аудиозапись')}
st={'path':None,'downloading':False,'route':None}

def detect_agent(t):
    t=(t or '').lower()
    if 'психолог' in t or 'psych' in t: return 'psychologist'
    if 'ментор' in t or 'mentor' in t or 'наставник' in t: return 'mentor'
    if 'проджект' in t or 'проект' in t or 'project' in t: return 'project'
    return None

def _one(path):
    last=None
    for model in ('gpt-4o-transcribe','whisper-1'):
        try:
            with open(path,'rb') as f:
                r=oai.audio.transcriptions.create(model=model,file=f,language='ru')
            return r.text
        except Exception as e:
            last=e
    raise last

def transcribe(src):
    d=tempfile.mkdtemp(dir='/root/transcriber')
    try:
        mp3=os.path.join(d,'full.mp3')
        subprocess.run(['ffmpeg','-y','-i',src,'-ac','1','-ar','16000','-b:a','32k',mp3],check=True,capture_output=True)
        subprocess.run(['ffmpeg','-y','-i',mp3,'-f','segment','-segment_time','900','-c','copy',os.path.join(d,'c_%03d.mp3')],check=True,capture_output=True)
        chunks=sorted(glob.glob(os.path.join(d,'c_*.mp3'))) or [mp3]
        return '\n'.join((_one(c) or '').strip() for c in chunks).strip()
    finally:
        shutil.rmtree(d,ignore_errors=True)

def pg_insert(env, table, cols, vals):
    e=dict(os.environ)
    for ln in open(env):
        k,_,v=ln.strip().partition('=')
        if k: e[k]=v
    args=['psql','-v','ON_ERROR_STOP=1']
    ph=[]
    for i,val in enumerate(vals):
        args+=['-v','p%d=%s'%(i,val)]; ph.append(":'p%d'"%i)
    sql='INSERT INTO %s (%s) VALUES (%s);'%(table, ','.join(cols), ','.join(ph))
    subprocess.run(args, input=sql, env=e, capture_output=True, text=True, check=True)

def deliver(agent,text):
    msg=('Это расшифровка аудиозаписи от Антона. Сделай разбор по своей роли и ответь. '
         'В конце добавь блок "Для памяти:" с 3-6 краткими пунктами самого важного о Антоне из этой записи.\n\n'+text)
    r=subprocess.run([OPENCLAW,'agent','--agent',agent,'--message',msg,'--deliver','--reply-channel','telegram','--reply-to',str(REPLY_TO[agent]),'--json'],timeout=1200,capture_output=True,text=True)
    reply=''
    try:
        d=json.loads(r.stdout)
        reply='\n'.join(p.get('text','') for p in d.get('result',{}).get('payloads',[]) if p.get('text')).strip()
    except Exception:
        pass
    if reply and agent in MEM:
        env,table,cols,label=MEM[agent]
        try: pg_insert(env, table, cols, (label, reply, 'transcript'))
        except Exception: traceback.print_exc()

def is_content(m):
    try:
        if m.voice:
            return bool(m.file and (m.file.duration or 0) > 300)
        if m.audio: return True
        if getattr(m,'video',None): return True
        if m.document:
            mt=m.document.mime_type or ''
            if mt.startswith('audio') or mt.startswith('video'): return True
    except Exception:
        pass
    return False

client=TelegramClient(StringSession(), API_ID, API_HASH)

async def react(mid,emo):
    try:
        await client.send_reaction(CHAT_ID, mid, emo)
    except Exception:
        pass

async def run(agent, src):
    loop=asyncio.get_event_loop()
    try:
        try: await client.send_message(CHAT_ID, 'Принял запись, обрабатываю, пришлю разбор через пару минут')
        except Exception: pass
        text=await loop.run_in_executor(None, transcribe, src)
        open(os.path.join(OUT, os.path.basename(src)+'.txt'),'w').write(text)
        await loop.run_in_executor(None, deliver, agent, text)
        try: os.remove(src)
        except Exception: pass
    except Exception as e:
        traceback.print_exc()
        try: await client.send_message(CHAT_ID, 'Ошибка обработки: %s'%repr(e)[:300])
        except Exception: pass

@client.on(events.NewMessage(chats=CHAT_ID))
async def h(event):
    m=event.message
    loop=asyncio.get_event_loop()
    try:
        if is_content(m):
            st['downloading']=True; st['path']=None
            name=(m.file.name if m.file else None) or ('audio_%d'%m.id)
            dest=os.path.join(INC,'%d_%s'%(m.id,name))
            await client.download_media(m, file=dest)
            st['downloading']=False; st['path']=dest
            await react(m.id,'👀')
            if st['route']:
                agent=st['route']; st['route']=None; p=st['path']; st['path']=None
                await run(agent,p)
            return
        cmd=None
        if m.voice:
            vp=os.path.join(INC,'cmd_%d.ogg'%m.id)
            await client.download_media(m,file=vp)
            cmd=await loop.run_in_executor(None,_one,vp)
            try: os.remove(vp)
            except Exception: pass
        elif m.text:
            cmd=m.text
        else:
            return
        agent=detect_agent(cmd)
        if not agent:
            return
        if st['path']:
            p=st['path']; st['path']=None
            await run(agent,p)
        elif st['downloading']:
            st['route']=agent
        else:
            st['route']=agent
    except Exception as e:
        traceback.print_exc()
        try: await client.send_message(CHAT_ID,'Ошибка: %s'%repr(e)[:300])
        except Exception: pass

try:
 import yasna_media
 yasna_media.register(client, oai, transcribe, pg_insert)
except Exception:
 traceback.print_exc()

async def main():
    await client.start(bot_token=BOT_TOKEN)
    me=await client.get_me()
    print('RECEIVER_UP',me.username, flush=True)
    await client.run_until_disconnected()

if __name__=='__main__':
    asyncio.run(main())
