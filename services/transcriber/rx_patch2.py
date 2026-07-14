import shutil, time, py_compile
f='/root/transcriber/receiver.py'
shutil.copy(f, f+'.bak.route.'+str(int(time.time())))
s=open(f).read()
s4=' '*4; s8=' '*8; s12=' '*12
a=s8+"elif st['downloading']:\n"+s12+"st['route']=agent\n"+s8+"else:\n"+s12+"return"
b=s8+"elif st['downloading']:\n"+s12+"st['route']=agent\n"+s8+"else:\n"+s12+"st['route']=agent"
c=s4+"try:\n"+s8+"text=await loop.run_in_executor(None, transcribe, src)"
d=s4+"try:\n"+s8+"try: await client.send_message(CHAT_ID, 'Принял запись, обрабатываю, пришлю разбор через пару минут')\n"+s8+"except Exception: pass\n"+s8+"text=await loop.run_in_executor(None, transcribe, src)"
n1=s.count(a); n2=s.count(c)
s=s.replace(a,b).replace(c,d)
open(f,'w').write(s)
print('route_fix_matches', n1, 'ack_matches', n2)
py_compile.compile(f, doraise=True)
print('COMPILE_OK')
