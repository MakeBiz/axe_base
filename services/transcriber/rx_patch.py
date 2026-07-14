import shutil, time, py_compile
f='/root/transcriber/receiver.py'
shutil.copy(f, f+'.bak.route.'+str(int(time.time())))
s=open(f).read()
a=" elif st['downloading']:\n st['route']=agent\n else:\n return"
b=" elif st['downloading']:\n st['route']=agent\n else:\n st['route']=agent"
c=" try:\n text=await loop.run_in_executor(None, transcribe, src)"
d=" try:\n try: await client.send_message(CHAT_ID, 'Принял запись, обрабатываю, пришлю разбор через пару минут')\n except Exception: pass\n text=await loop.run_in_executor(None, transcribe, src)"
n1=s.count(a); n2=s.count(c)
s=s.replace(a,b).replace(c,d)
open(f,'w').write(s)
print('route_fix_matches', n1, 'ack_matches', n2)
py_compile.compile(f, doraise=True)
print('COMPILE_OK')
