import os, receiver
p='/root/transcriber/incoming/24_20260703130338 (mp3cut.net).wav'
t=receiver.transcribe(p)
open('/root/transcriber/out/rec24_mentor.txt','w').write(t)
print('LEN',len(t),flush=True)
receiver.deliver('mentor',t)
print('DELIVERED',flush=True)
try: os.remove(p)
except Exception: pass
