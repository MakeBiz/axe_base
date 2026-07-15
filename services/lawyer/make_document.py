#!/usr/bin/env python3
import sys, os, json, argparse, subprocess, datetime
from docxtpl import DocxTemplate

BASE = os.environ.get('LAWYER_BASE', '/root/lawyer')
TEMPLATES = BASE + '/templates'
OUTDIR = os.environ.get('LAWYER_OUT', '/root/.openclaw/media/outbound')
COUNTERS = BASE + '/counters.json'
EXEC = json.load(open(BASE + '/executors.json'))
OPENCLAW = os.environ.get('OPENCLAW_BIN', '/usr/bin/openclaw')
DEFAULT_CHAT = os.environ.get('LAWYER_CHAT', '-1004404743128')
SECRETS = '/root/.secrets/transcriber.env'

def _openai_key():
    k = os.environ.get('OPENAI_API_KEY')
    if k: return k
    try:
        for line in open(SECRETS):
            line = line.strip()
            if line.startswith('OPENAI_API_KEY='):
                return line.split('=',1)[1].strip().strip("'").strip('"')
    except Exception:
        pass
    return None

def _money(v):
    return format(float(v), ',.2f').replace(',', ' ').replace('.', ',')

def _rub_words(v):
    from num2words import num2words
    amount = float(v)
    r = int(amount); k = int(round((amount - r) * 100))
    w = num2words(r, lang='ru')
    n100 = r % 100; n10 = r % 10
    if 11 <= n100 <= 14: form = 'рублей'
    elif n10 == 1: form = 'рубль'
    elif n10 in (2, 3, 4): form = 'рубля'
    else: form = 'рублей'
    s = '%s %s %02d копеек' % (w, form, k)
    return s[0].upper() + s[1:]

TEMPLATE_FILE = {
  'contract':'Договор оказания услуг.docx','offer':'Счёт-оферта.docx','invoice':'Счет.docx',
  'spec100':'Спецификация 100%.docx','spec50':'Спецификация 50%.docx','act':'Акт выполненных работ.docx',
  'support':'Счет на поддержку.docx','nda_client':'NDA с клиентом.docx','nda_employee':'NDA с сотрудником.docx'}
PREFIX = {'contract':'ДОГ','offer':'СЧО','invoice':'СЧ','spec100':'СПЕ','spec50':'СПЕ','act':'АКТ','support':'СЧП','nda_client':'NDA','nda_employee':'NDA'}
LABEL = {'contract':'Договор','offer':'Счёт-оферта','invoice':'Счёт','spec100':'Спецификация','spec50':'Спецификация','act':'Акт','support':'Счёт на поддержку','nda_client':'NDA','nda_employee':'NDA'}
START = {'contract':60,'offer':566,'invoice':583,'spec100':232,'spec50':232,'act':1,'support':1,'nda_client':1,'nda_employee':1}

def next_number(t):
    try: c = json.load(open(COUNTERS))
    except Exception: c = {}
    n = c.get(t, START.get(t,100)) + 1
    c[t] = n; json.dump(c, open(COUNTERS,'w'))
    return '%s-%03d' % (PREFIX[t], n)

def read_card(path):
    p = path.lower()
    if p.endswith('.pdf'):
        return subprocess.run(['pdftotext', path, '-'], capture_output=True, text=True).stdout
    if p.endswith('.doc'):
        return subprocess.run(['antiword', path], capture_output=True, text=True).stdout
    if p.endswith('.docx'):
        import docx; d = docx.Document(path); return '\n'.join(x.text for x in d.paragraphs)
    return open(path, errors='ignore').read()

def parse_client(text):
    from openai import OpenAI
    oai = OpenAI(api_key=_openai_key())
    sysp = ('Из карточки реквизитов клиента извлеки JSON строго с ключами: '
      'client_legal_form_and_name (краткое, напр ООО «Ромашка»), client_company_name, client_company_full_name (полное), '
      'client_inn, client_registry_label (ОГРН или ОГРНИП), client_registry_number, client_legal_address, '
      'client_bank_name, client_bik, client_corr_account, client_bank_account, client_email, client_phone. '
      'Если поля нет, пустая строка. Только JSON.')
    r = oai.chat.completions.create(model='gpt-4o-mini', temperature=0, response_format={'type':'json_object'},
        messages=[{'role':'system','content':sysp},{'role':'user','content':text[:12000]}])
    d = json.loads(r.choices[0].message.content)
    legal_name = (d.get('client_legal_form_and_name') or '').strip()
    if legal_name:
        d.setdefault('client_company_name', legal_name)
        d.setdefault('client_company_full_name', legal_name)
        if not d.get('client_company_name'):
            d['client_company_name'] = legal_name
        if not d.get('client_company_full_name'):
            d['client_company_full_name'] = legal_name
    if legal_name.upper().startswith('ИП ') and d.get('client_registry_number') and d.get('client_registry_label') == 'ОГРН':
        d['client_registry_label'] = 'ОГРНИП'
    d.setdefault('client_ogrnip', d.get('client_registry_number',''))
    d.setdefault('email', d.get('client_email',''))
    d.setdefault('phone', d.get('client_phone',''))
    return d

def build(doc_type, account, ctx, number):
    tpl = DocxTemplate(os.path.join(TEMPLATES, TEMPLATE_FILE[doc_type]))
    full = dict(EXEC[account]); full.update(ctx)
    today = datetime.date.today().isoformat()
    full.setdefault('contract_number', number); full.setdefault('doc_number', number)
    for k in ('offer_number','invoice_number','spec_number','act_number','nda_number'): full.setdefault(k, number)
    for k in ('doc_date','offer_date','invoice_date','spec_date','act_date','nda_date','contract_date'): full.setdefault(k, today)
    for v in tpl.get_undeclared_template_variables(): full.setdefault(v, '')
    clientname = (ctx.get('client_legal_form_and_name') or ctx.get('client_company_name') or 'Клиент')
    clientname = clientname.replace('«','').replace('»','').replace('"','').strip()[:40]
    title = '%s %s · %s · %s' % (LABEL[doc_type], number, clientname, today)
    fname = title.replace('/', '-')
    out = os.path.join(OUTDIR, fname + '.docx')
    tpl.render(full); tpl.save(out)
    return out, title

def send(chat, path, title):
    r = subprocess.run([OPENCLAW,'message','send','--channel','telegram','--target',str(chat),'--media',path,'--message',title],
        capture_output=True, text=True, timeout=120)
    return r.returncode == 0, (r.stdout + r.stderr)[-400:]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--type', required=True)
    ap.add_argument('--account', required=True)
    ap.add_argument('--card')
    ap.add_argument('--client-json')
    ap.add_argument('--number')
    ap.add_argument('--chat')
    ap.add_argument('--send', action='store_true')
    ap.add_argument('--amount')
    ap.add_argument('--service-name')
    ap.add_argument('--service-note')
    ap.add_argument('--qty', default='1')
    ap.add_argument('--unit', default='усл.')
    ap.add_argument('--workdays')
    ap.add_argument('--contract-number')
    a = ap.parse_args()
    ctx = {}
    if a.client_json: ctx.update(json.loads(a.client_json))
    elif a.card: ctx.update(parse_client(read_card(a.card)))
    if a.amount:
        amount = float(str(a.amount).replace(' ', '').replace(',', '.'))
        ctx['line_index'] = '1'
        ctx['service_name'] = a.service_name or 'Услуги'
        ctx['service_quantity'] = a.qty
        ctx['service_unit'] = a.unit
        ctx['service_unit_price'] = _money(amount)
        ctx['service_line_total'] = _money(amount)
        ctx['service_scope_note'] = a.service_note or ''
        ctx['subtotal_amount'] = _money(amount)
        ctx['total_amount_numeric'] = _money(amount)
        ctx['total_amount_words'] = _rub_words(amount)
    if a.workdays: ctx['delivery_term_workdays'] = str(a.workdays)
    if a.contract_number: ctx['contract_number'] = a.contract_number
    number = a.number or next_number(a.type)
    out, title = build(a.type, a.account, ctx, number)
    print('BUILT', out); print('TITLE', title)
    if a.send:
        chat = a.chat or DEFAULT_CHAT
        ok, log = send(chat, out, title)
        print('SENT_OK' if ok else 'SEND_FAIL', log)

if __name__ == '__main__':
    main()
