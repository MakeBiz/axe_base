import os, subprocess
def pgenv(f):
    e=dict(os.environ)
    for l in open(f):
        l=l.strip()
        if '=' in l and not l.startswith('#'):
            k,v=l.split('=',1); e[k]=v
    return e
def q(sql):
    r=subprocess.run(['psql','-tA','-F','|'], input=sql, env=pgenv('/root/.secrets/yasna_mem.env'), capture_output=True, text=True)
    if r.returncode!=0:
        return []
    return [x for x in r.stdout.split(chr(10)) if x.strip()]
out=['# Что ты знаешь о Злате','','Это ты знаешь о ней сама собой, как близкий человек, и держишь в сердце, не цитируя вслух:','']
mem=q("select coalesce(kind,''), coalesce(topic,''), content from yasna.memory order by ts asc limit 300")
for line in mem:
    p=line.split('|',2)
    kind=p[0] if len(p)>0 else ''; topic=p[1] if len(p)>1 else ''; content=p[2] if len(p)>2 else ''
    tag=topic or kind
    out.append('- '+(('['+tag+'] ') if tag else '')+content)
chat=q("select to_char(ts,'MM-DD HH24:MI'), coalesce(sender,''), left(transcript,400) from yasna.transcripts where media_type='text' order by ts desc limit 40")
if chat:
    out+=['','## Свежая переписка в группе (новое сверху)','']
    for line in chat:
        p=line.split('|',2)
        t=p[0] if len(p)>0 else ''; s=p[1] if len(p)>1 else ''; tx=p[2] if len(p)>2 else ''
        out.append('- '+t+' '+(s+': ' if s else '')+tx)
open('/root/.openclaw/workspace-yasna/MEMORY.md','w').write(chr(10).join(out)+chr(10))
print('RENDERED mem=%d chat=%d'%(len(mem),len(chat)))
