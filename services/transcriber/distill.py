import os, json, glob, subprocess
from openai import OpenAI
oai=OpenAI(api_key=os.environ['OPENAI_API_KEY'])
STATE='/root/transcriber/distill_state.json'
AGENTS={
 'mentor': dict(d='/root/.openclaw/agents/mentor/agent/codex-home/sessions',
   env='/root/.secrets/mentor_mem.env', table='mentor.memory', col='content',
   cols=('kind','topic','content','source'),
   prompt='Ты ведёшь долгую память бизнес-ментора об Антоне. Из диалога вытащи только устойчивые переиспользуемые факты, решения, договорённости и бизнес-инсайты об Антоне и его проектах. Без воды, приветствий и общих фраз. От 0 до 8 пунктов, каждый одной короткой строкой, без нумерации и маркеров. Если ничего стоящего нет, верни пусто.'),
 'psychologist': dict(d='/root/.openclaw/agents/psychologist/agent/codex-home/sessions',
   env='/root/.secrets/psych_mem.env', table='psych.notes', col='note',
   cols=('theme','note','source'),
   prompt='Ты ведёшь психологическую долгую память об Антоне как контекст, не диагноз. Из диалога вытащи только устойчивые психологические факты, паттерны, ценности, триггеры и договорённости с Антоном. Без воды. От 0 до 8 пунктов, каждый одной короткой строкой, без нумерации и маркеров. Если ничего стоящего нет, верни пусто.'),
}

def load_state():
    try: return json.load(open(STATE))
    except Exception: return {}

def extract_convo(path):
    turns=[]
    for line in open(path, errors='ignore'):
        try: o=json.loads(line)
        except Exception: continue
        if o.get('type')!='response_item': continue
        p=o.get('payload',{})
        if p.get('type')!='message': continue
        role=p.get('role')
        if role not in ('user','assistant'): continue
        txt=' '.join(c.get('text','') for c in p.get('content',[]) if isinstance(c,dict) and c.get('text'))
        txt=txt.strip()
        if not txt: continue
        if role=='user' and ('AGENTS.md instructions' in txt or '<INSTRUCTIONS>' in txt): continue
        turns.append(('Антон: ' if role=='user' else 'Ты: ')+txt)
    return '\n'.join(turns)

def distill(prompt, convo):
    convo=convo[-40000:]
    try:
        r=oai.chat.completions.create(model='gpt-4o-mini', temperature=0,
            messages=[{'role':'system','content':prompt},{'role':'user','content':convo}])
        out=r.choices[0].message.content or ''
    except Exception as e:
        print('LLM_ERR', repr(e)[:200]); return []
    res=[]
    for l in out.splitlines():
        l=l.strip().lstrip('-*0123456789. ').strip()
        if len(l)>=8: res.append(l)
    return res

def pgenv(env):
    e=dict(os.environ)
    for ln in open(env):
        k,_,v=ln.strip().partition('=')
        if k: e[k]=v
    return e

def sq(s): return "'"+str(s).replace("'","''")+"'"

def exists(cfg, content):
    sql="SELECT 1 FROM %s WHERE %s=%s LIMIT 1" % (cfg['table'], cfg['col'], sq(content))
    r=subprocess.run(['psql','-tA'], input=sql, env=pgenv(cfg['env']), capture_output=True, text=True)
    return r.stdout.strip().startswith('1')

def insert(cfg, content):
    vals=('chat','диалог',content,'distill') if cfg['table']=='mentor.memory' else ('диалог',content,'distill')
    sql="INSERT INTO %s (%s) VALUES (%s)" % (cfg['table'], ','.join(cfg['cols']), ','.join(sq(v) for v in vals))
    r=subprocess.run(['psql','-v','ON_ERROR_STOP=1'], input=sql, env=pgenv(cfg['env']), capture_output=True, text=True)
    if r.returncode!=0: print('PG_ERR', r.stderr.strip()[:200])
    return r.returncode==0

def main():
    st=load_state(); added=0
    for agent,cfg in AGENTS.items():
        for f in sorted(glob.glob(cfg['d']+'/**/rollout-*.jsonl', recursive=True)):
            mt=os.path.getmtime(f)
            if st.get(f,0) >= mt: continue
            convo=extract_convo(f)
            if convo:
                for b in distill(cfg['prompt'], convo):
                    if exists(cfg,b): continue
                    if insert(cfg,b): added+=1
            st[f]=mt
    json.dump(st, open(STATE,'w'))
    print('DISTILL_DONE added=%d'%added)

if __name__=='__main__':
    main()
