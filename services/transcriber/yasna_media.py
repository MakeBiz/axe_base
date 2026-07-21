import os, subprocess, asyncio, traceback
from telethon import events
YASNA_GROUP=-1003989514984
YASNA_ENV='/root/.secrets/yasna_mem.env'
YASNA_FILES='/root/transcriber/yasna_files'
os.makedirs(YASNA_FILES, exist_ok=True)
def _pdf_text(path):
    try:
        r=subprocess.run(['pdftotext','-layout',path,'-'],capture_output=True,text=True,timeout=180)
        if r.returncode==0 and r.stdout.strip(): return r.stdout
    except Exception: pass
    try:
        import pypdf
        return chr(10).join((pg.extract_text() or '') for pg in pypdf.PdfReader(path).pages)
    except Exception: return ''
def register(client, oai, transcribe, pg_insert):
    def _distill(text):
        try:
            r=oai.chat.completions.create(model='gpt-4o-mini',temperature=0,messages=[{'role':'system','content':'Ты ведёшь память бизнес-коуча о Злате. Из расшифровки вытащи устойчивые факты о Злате, её методе, продукте, аудитории, договорённостях и целях. От 1 до 8 пунктов, одной строкой каждый, без нумерации. Если ничего нет, верни пусто.'},{'role':'user','content':(text or '')[:14000]}])
            return (r.choices[0].message.content or '').strip()
        except Exception:
            traceback.print_exc(); return ''
    @client.on(events.NewMessage())
    async def yasna_media(ev):
        if getattr(ev,'chat_id',None)!=YASNA_GROUP: return
        m=ev.message; has_doc=bool(getattr(m,'document',None))
        print('YASNA_MEDIA chat='+str(ev.chat_id)+' voice='+str(bool(m.voice))+' doc='+str(has_doc),flush=True)
        try:
            mtype=None; fname=None
            if m.voice or getattr(m,'audio',None): mtype='voice'
            elif has_doc:
                mime=(m.document.mime_type or '')
                for a in (m.document.attributes or []):
                    if getattr(a,'file_name',None): fname=a.file_name
                low=(fname or '').lower()
                if mime.startswith('audio') or low.endswith(('.ogg','.oga','.mp3','.m4a','.wav')): mtype='voice'
                elif mime=='application/pdf' or low.endswith('.pdf'): mtype='pdf'
                else: mtype='file'
            else: return
            path=os.path.join(YASNA_FILES,'y_'+str(m.id)+'_'+(fname or ('voice.ogg' if mtype=='voice' else 'file')))
            await client.download_media(m, path)
            print('YASNA_MEDIA downloaded '+os.path.basename(path)+' type='+mtype,flush=True)
            loop=asyncio.get_event_loop(); text=''
            if mtype=='voice': text=await loop.run_in_executor(None, transcribe, path)
            elif mtype=='pdf': text=await loop.run_in_executor(None, _pdf_text, path)
            text=(text or '').strip(); sender=''
            try:
                s=await m.get_sender(); sender=((getattr(s,'first_name','') or '')+' '+(getattr(s,'last_name','') or '')).strip()
            except Exception: pass
            pg_insert(YASNA_ENV,'yasna.transcripts',('msg_id','sender','media_type','file_name','transcript'),(str(m.id),sender,mtype,fname or os.path.basename(path),text))
            print('YASNA_MEDIA stored len='+str(len(text)),flush=True)
            if text:
                summ=await loop.run_in_executor(None, _distill, text)
                for line in [x.strip().lstrip('- ').strip() for x in (summ or '').split(chr(10)) if x.strip()]:
                    if line: pg_insert(YASNA_ENV,'yasna.memory',('kind','topic','content','source'),('медиа',mtype,line,'transcript'))
        except Exception:
            traceback.print_exc()
    print('YASNA_MEDIA registered catch-all for '+str(YASNA_GROUP),flush=True)
    return True
