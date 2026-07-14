import os, json, glob, re, urllib.request

STATE='/root/transcriber/summaries_capture_state.json'
GW='http://127.0.0.1:8790/summaries'
ENVF='/root/.secrets/miniapp_gateway.env'
AGENTS={
 'mentor':'/root/.openclaw/agents/mentor/agent/codex-home/sessions',
 'psychologist':'/root/.openclaw/agents/psychologist/agent/codex-home/sessions',
}
RX=re.compile(r'СОХРАНИ ВЫЖИМКУ\s*```(?:json)?\s*(\{.*?\})\s*```', re.DOTALL)

def token():
 for ln in open(ENVF):
  if ln.startswith('GATEWAY_TOKEN_TOOLS='):
   return ln.split('=',1)[1].strip()
 return ''

def load_state():
 try: return json.load(open(STATE))
 except Exception: return {}

def assistant_text(path):
 out=[]
 for line in open(path, errors='ignore'):
  line=line.strip()
  if not line: continue
  try: o=json.loads(line)
  except Exception: continue
  if o.get('type')!='response_item': continue
  p=o.get('payload') or {}
  if p.get('role')!='assistant': continue
  for c in p.get('content',[]) or []:
   if isinstance(c,dict) and c.get('text'): out.append(c['text'])
 return '\n'.join(out)

def post(tok, body):
 data=json.dumps(body).encode()
 req=urllib.request.Request(GW, data=data, headers={'Content-Type':'application/json','Authorization':'Bearer '+tok,'X-User-Role':'owner','X-User-Id':'280369346'})
 try:
  r=urllib.request.urlopen(req, timeout=15)
  return r.getcode()
 except Exception as e:
  return 'ERR '+str(e)[:120]

def main():
 tok=token()
 st=load_state()
 n=0
 for agent,d in AGENTS.items():
  for f in sorted(glob.glob(d+'/**/rollout-*.jsonl', recursive=True)):
   mt=os.path.getmtime(f)
   if st.get(f)==mt: continue
   txt=assistant_text(f)
   ms=RX.findall(txt)
   if ms:
    try: block=json.loads(ms[-1])
    except Exception: block=None
    if block and block.get('title'):
     sid='sess-'+os.path.basename(f).replace('rollout-','').replace('.jsonl','')
     body={k:block.get(k) for k in ('title','decided','next_steps','key_idea','watch','open_q','body') if block.get(k)}
     body['agent_id']=agent
     body['kind']=agent
     body['session_id']=sid
     print(agent, sid, post(tok, body))
     n+=1
   st[f]=mt
 json.dump(st, open(STATE,'w'))
 print('done', n)

main()
