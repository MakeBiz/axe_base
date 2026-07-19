# yasna_media.py — обработчик группы Златы: текст+голос+файлы, только в память Ясны
import os, subprocess, asyncio, traceback
from telethon import events

YASNA_GROUP=-1003989514984
YASNA_ENV='/root/.secrets/yasna_mem.env'
YASNA_FILES='/root/transcriber/yasna_files'
os.makedirs(YASNA_FILES, exist_ok=True)

def _pdf_text(path):
 try:
 r=subprocess.run(['pdftotext','-layout',path,'-'],capture_output=True,text=True,timeout=120)
 if r.returncode==0 and r.stdout.strip(): return r.stdout
 except Exception: pass
 try:
 import pypdf
 return chr(10).join((pg.extract_text() or '') for pg in pypdf.PdfReader(path).pages)
 except Exception: return ''

def register(client, oai, transcribe, pg_insert):
 def _distill(text):
 try:
 r=oai.chat.completions.create(model='gpt-4o-mini',temperature=0,messages=[
 {'role':'system','content':'Ты ведёшь память бизнес-коуча о Злате. Из расшифровки вытащи только устойчивые факты о Злате, её методе, продукте, аудитории, договорённостях и целях. От 1 до 6 пунктов, каждый одной короткой строкой, без нумерации и маркеров. Если ничего стоящего нет, верни пусто.'},
 {'role':'user','content':(text or '')[:12000]}])
 return (r.choices[0].message.content or '').strip()
 except Exception:
 traceback.print_exc(); return ''

 @client.on(events.NewMessage(chats=YASNA_GROUP))
 async def yasna_group(ev):
 m=ev.message
 try:
 try: snd=await m.get_sender()
 except Exception: snd=None
 if getattr(snd,'bot',False): return
 sname=((getattr(snd,'first_name','') or '')+' '+(getattr(snd,'last_name','') or '')).strip()
 if not (m.voice or m.audio or m.document):
 t=(m.text or '').strip()
 if t and not t.startswith('/'):
 pg_insert(YASNA_ENV,'yasna.transcripts',('msg_id','sender','media_type','file_name','transcript'),(str(m.id),sname,'text','',t))
 return
 mtype=None; fname=None
 if m.voice or m.audio:
 mtype='voice'
 elif m.document:
 mime=(m.document.mime_type or '')
 for a in (m.document.attributes or []):
 if getattr(a,'file_name',None): fname=a.file_name
 low=(fname or '').lower()
 if mime.startswith('audio') or low.endswith(('.ogg','.oga','.mp3','.m4a','.wav')): mtype='voice'
 elif mime=='application/pdf' or low.endswith('.pdf'): mtype='pdf'
 else: mtype='file'
 path=os.path.join(YASNA_FILES,'y_%d_%s'%(m.id,(fname or ('voice.ogg' if mtype=='voice' else 'file'))))
 await client.download_media(m, path)
 loop=asyncio.get_event_loop()
 text=''
 if mtype=='voice': text=await loop.run_in_executor(None, transcribe, path)
 elif mtype=='pdf': text=await loop.run_in_executor(None, _pdf_text, path)
 text=(text or '').strip()
 pg_insert(YASNA_ENV,'yasna.transcripts',('msg_id','sender','media_type','file_name','transcript'),(str(m.id),sname,mtype,fname or os.path.basename(path),text))
 if text:
 summ=await loop.run_in_executor(None, _distill, text)
 for line in [x.strip().lstrip('-• ').strip() for x in (summ or '').split(chr(10)) if x.strip()]:
 if line: pg_insert(YASNA_ENV,'yasna.memory',('kind','topic','content','source'),('медиа',mtype,line,'transcript'))
 try: await client.send_read_acknowledge(YASNA_GROUP, m)
 except Exception: pass
 except Exception:
 traceback.print_exc()
 print('YASNA_GROUP handler registered for', YASNA_GROUP)
 return True
