import os, subprocess, asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
GROUP=-1003989514984
VOICE_IDS=[]
PDF_IDS=[35,36,37]
TEXT_IDS=[34]
YENV='/root/.secrets/yasna_mem.env'
FILES='/root/transcriber/yasna_files'
os.makedirs(FILES, exist_ok=True)
from openai import OpenAI
oai=OpenAI(api_key=os.environ['OPENAI_API_KEY'])
def pgenv(f):
    e=dict(os.environ)
    for l in open(f):
        l=l.strip()
        if '=' in l and not l.startswith('#'):
            k,v=l.split('=',1); e[k]=v
    return e
def sq(x): return "'"+str(x).replace("'","''")+"'"
def pins(table, cols, vals):
    sql='INSERT INTO %s (%s) VALUES (%s);'%(table, ','.join(cols), ','.join(sq(x) for x in vals))
    r=subprocess.run(['psql','-v','ON_ERROR_STOP=1'], input=sql, env=pgenv(YENV), capture_output=True, text=True)
    if r.returncode!=0: print('PGERR', r.stderr.strip()[:120])
def transcribe(path):
    for model in ('gpt-4o-transcribe','whisper-1'):
        try:
            with open(path,'rb') as f:
                return oai.audio.transcriptions.create(model=model,file=f,language='ru').text
        except Exception as e:
            last=str(e)[:100]
    print('TRANSC ERR', last); return ''
def pdf_text(path):
    try:
        r=subprocess.run(['pdftotext','-layout',path,'-'],capture_output=True,text=True,timeout=200)
        if r.returncode==0 and r.stdout.strip(): return r.stdout
    except Exception: pass
    try:
        import pypdf
        return chr(10).join((p.extract_text() or '') for p in pypdf.PdfReader(path).pages)
    except Exception: return ''
def distill(text, title):
    try:
        r=oai.chat.completions.create(model='gpt-4o-mini',temperature=0,messages=[{'role':'system','content':'Это материал или разговор Златы (психология, её метод, её дело). Вытащи 2-8 устойчивых фактов о её методе, идеях, подходе, продукте, целях, каждый одной короткой строкой без нумерации. Если пусто, верни пусто.'},{'role':'user','content':(title+chr(10)+(text or ''))[:16000]}])
        return (r.choices[0].message.content or '').strip()
    except Exception as e:
        print('DISTILL ERR', str(e)[:80]); return ''
def store(mid, sender, mtype, fname, text, title):
    pins('yasna.transcripts',('msg_id','sender','media_type','file_name','transcript'),(str(mid),sender,mtype,fname or '',text or ''))
    cnt=0
    if text and len(text.strip())>10:
        for line in [x.strip().lstrip('- ').strip() for x in (distill(text,title) or '').split(chr(10)) if x.strip()]:
            if line: pins('yasna.memory',('kind','topic','content','source'),('материал',title,line,'backfill')); cnt+=1
    print(mtype, mid, fname or '', 'chars', len(text or ''), 'mem', cnt)
async def main():
    c=TelegramClient(StringSession(), int(os.environ['TG_API_ID']), os.environ['TG_API_HASH'])
    await c.start(bot_token=os.environ['TG_BOT_TOKEN'])
    print('bot started')
    for mid in VOICE_IDS:
        try:
            m=await c.get_messages(GROUP, ids=mid)
        except Exception as e:
            print('voice', mid, 'GETERR', str(e)[:80]); continue
        if not m: print('voice', mid, 'none'); continue
        p=os.path.join(FILES,'bf_%d.ogg'%mid)
        try: await c.download_media(m,p)
        except Exception as e: print('voice',mid,'DLERR',str(e)[:80]); continue
        snd='Злата' if (getattr(m,'sender_id',0) or 0)==240987019 else ('Антон' if (getattr(m,'sender_id',0) or 0)==280369346 else '')
        store(mid, snd, 'voice', None, transcribe(p), 'голосовое '+snd)
    for mid in PDF_IDS:
        try: m=await c.get_messages(GROUP, ids=mid)
        except Exception as e: print('pdf',mid,'GETERR',str(e)[:80]); continue
        if not m or not getattr(m,'document',None): print('pdf',mid,'nodoc'); continue
        fn=None
        for a in (m.document.attributes or []):
            if getattr(a,'file_name',None): fn=a.file_name
        fn=fn or ('doc_%d.pdf'%mid)
        p=os.path.join(FILES,'bf_%d_%s'%(mid,fn))
        try: await c.download_media(m,p)
        except Exception as e: print('pdf',mid,'DLERR',str(e)[:80]); continue
        store(mid,'Злата','pdf',fn, pdf_text(p),'материал '+fn)
    for mid in TEXT_IDS:
        try: m=await c.get_messages(GROUP, ids=mid)
        except Exception: m=None
        if m and m.message: store(mid,'Злата','text','',m.message,'пост Златы')
    await c.disconnect(); print('BACKFILL DONE')
asyncio.run(main())
