import os, subprocess

def q(env, sql):
    e=dict(os.environ)
    for ln in open(env):
        k,_,v=ln.strip().partition('=')
        if k: e[k]=v
    r=subprocess.run(['psql','-tAF','\x1f','-c',sql], env=e, capture_output=True, text=True)
    if r.returncode!=0:
        raise RuntimeError(r.stderr.strip())
    return [row.split('\x1f') for row in r.stdout.splitlines() if row]

def write(path, header, intro, rows, fmt):
    out=['# '+header,'',intro,'']
    if not rows:
        out.append('_Пока пусто. Здесь будет копиться твоя долгая память._')
    for row in rows:
        out.append(fmt(row))
    open(path,'w').write('\n'.join(out)+'\n')

def main():
    m=q('/root/.secrets/mentor_mem.env',
        "SELECT to_char(ts,'YYYY-MM-DD'),coalesce(kind,''),coalesce(topic,''),content FROM mentor.memory ORDER BY ts DESC LIMIT 80")
    write('/root/.openclaw/workspace-mentor/MEMORY.md',
          'MEMORY.md — долгая память Ментора (Postgres mentor.memory)',
          'Твоя постоянная память об Антоне, проектах, решениях и инсайтах. Всегда учитывай её в разговоре. Файл обновляется автоматически из Postgres, вручную не редактируй.',
          m, lambda r: '- [%s] %s' % (' '.join(x for x in (r[0],r[1],r[2]) if x), r[3]))
    p=q('/root/.secrets/psych_mem.env',
        "SELECT to_char(ts,'YYYY-MM-DD'),coalesce(theme,''),coalesce(marker,''),note FROM psych.notes ORDER BY ts DESC LIMIT 80")
    write('/root/.openclaw/workspace-psychologist/MEMORY.md',
          'MEMORY.md — рабочие заметки Психолога (Postgres psych.notes)',
          'Твоя постоянная память об Антоне как психологический контекст, не диагноз и не истина в последней инстанции. Всегда учитывай её. Файл обновляется автоматически из Postgres, вручную не редактируй.',
          p, lambda r: '- [%s] %s' % (' '.join(x for x in (r[0],r[1],r[2]) if x), r[3]))
    print('RENDERED mentor=%d psych=%d' % (len(m), len(p)))

if __name__=='__main__':
    main()
