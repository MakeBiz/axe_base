#!/usr/bin/env python3
import os, subprocess
def pgenv(f):
 e=dict(os.environ)
 for l in open(f):
  l=l.strip()
  if '=' in l and not l.startswith('#'):
   k,v=l.split('=',1); e[k]=v
 return e
SQL="SELECT to_char(ts,'YYYY-MM-DD'), coalesce(kind,''), coalesce(topic,''), content FROM yasna.memory ORDER BY ts DESC LIMIT 150"
r=subprocess.run(['psql','-tA','-F','|'], input=SQL, env=pgenv('/root/.secrets/yasna_mem.env'), capture_output=True, text=True)
if r.returncode!=0:
 print('PG_ERR', r.stderr.strip()[:200]); raise SystemExit(1)
rows=[x for x in r.stdout.split(chr(10)) if x.strip()]
out=['# Что ты знаешь о Злате','',
 'Это ты знаешь о ней сама собой, как близкий человек, и держишь в сердце, не цитируя вслух:','']
if rows:
 for line in rows:
  p=line.split('|',3)
  date=p[0]; kind=p[1] if len(p)>1 else ''; topic=p[2] if len(p)>2 else ''; content=p[3] if len(p)>3 else ''
  tag=topic or kind
  out.append('- '+date+(' ['+tag+']' if tag else '')+': '+content)
else:
 out.append('(пока пусто, контекст появится после первых разговоров и материалов)')
open('/root/.openclaw/workspace-yasna/MEMORY.md','w').write(chr(10).join(out)+chr(10))
print('RENDERED yasna=%d' % len(rows))
