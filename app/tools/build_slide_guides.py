"""Attach slide-specific handout explanations and coordinate-based code comments."""
from pathlib import Path
import hashlib,json,re,collections
from slide_guidance import code_steps
APP=Path(__file__).resolve().parents[1];ROOT=APP.parent
WEB=APP/'web'

def norm(s):return re.sub(r'\s+','',s).replace('ﬁ','fi').replace('ﬂ','fl')
def digest(s):return hashlib.sha256(s.encode()).hexdigest()[:20]

def pdf_rows(page):
    rows=collections.defaultdict(list)
    for c in page.chars:
        if c['text'].strip():rows[round(c['top']/2)*2].append(c)
    result=[]
    for _,chars in sorted(rows.items()):
        mono=[c for c in chars if 'Mono' in c['fontname'] or 'MonL' in c['fontname'] or 'Courier' in c['fontname']]
        if len(mono)<3:continue
        chars=sorted(mono,key=lambda c:c['x0']);text='';last=chars[0]['x0']
        for c in chars:
            if c['x0']-last>max(1,c.get('width',3)*.5):text+=' '
            text+=c['text'];last=c['x1']
        x=min(c['x0'] for c in chars)/page.width;y=min(c['top'] for c in chars)/page.height
        if not (0<=x<1 and 0<=y<1):continue
        result.append(dict(text=text,x=x,y=y,w=(max(c['x1'] for c in chars)/page.width)-x,h=(max(c['bottom'] for c in chars)/page.height)-y))
    return result

def build():
    import pdfplumber
    content=json.loads((WEB/'course-content.json').read_text())
    notes=json.loads((APP/'content/code-notes.json').read_text());stats=collections.Counter()
    for lesson in content['lessons']:
        path=ROOT/'materiali/materiali_corso_2025_26/lectures'/lesson['id']/(lesson['id']+'.pdf')
        with pdfplumber.open(path) as pdf:
            for slide in lesson['slides']:
                exact=[s for s in lesson['sections'] if slide['page'] in s['slidePages']]
                sections=exact or [s for s in lesson['sections'] if s['id'] in slide['sectionIds']]
                blocks=[]
                if not slide.get('explanation'):
                    for section in sections:
                        for block in section['blocks']:
                            if block['kind'] not in ('text','code'):continue
                            if block['kind']=='code':
                                if len(block['text'])>140 or len(block['text'].splitlines())>3:continue
                                if norm(block['text']) in norm(' '.join(b['text'] for b in slide['blocks'] if b['kind']=='code')):continue
                                if blocks and re.match(r'^[A-Za-z_]\w*[.,]$',block['text'].strip()):
                                    blocks[-1]['text']+=' '+block['text'].strip();blocks[-1]['fingerprint']=digest(blocks[-1]['text']);continue
                            blocks.append(dict(block,kind='inline-code' if block['kind']=='code' else 'text',id=f'g-{slide["page"]}-{block["id"]}',origin='slide',page=slide['page'],sourcePage=block['page'],label=f'Spiegazione slide {slide["page"]} · dispensa p. {block["page"]}'))
                rows=pdf_rows(pdf.pages[slide['page']-1])
                def visible_listing(block):
                    return any(norm(row['text']) in norm(line) or norm(line) in norm(row['text']) for row in rows for line in block['text'].splitlines() if len(norm(line))>5)
                code=[dict(b,steps=code_steps(b['text'])) for b in slide['blocks'] if b['kind']=='code' and visible_listing(b)]
                overrides=notes.get(f'{lesson["id"]}:{slide["page"]}',[])
                for block in code:
                    custom=[]
                    for needle,title,text in overrides:
                        line=next((i for i,s in enumerate(block['text'].splitlines(),1) if norm(needle) in norm(s)),None)
                        if line:custom.append(dict(line=line,code=block['text'].splitlines()[line-1].strip(),title=title,text=text))
                    if custom:block['steps']=custom
                comments=[]
                for block in code:
                    for step in block['steps']:
                        if step['title'] in ('Dichiarazioni incluse','Firma e parametri','Ingresso del programma'):continue
                        row=next((r for r in rows if norm(step['code'])==norm(r['text'])),None)
                        if not row:continue
                        if any(abs(row['y']-c['region']['y'])<.095 for c in comments):continue
                        comments.append(dict(id=f'comment-{slide["page"]}-{len(comments)+1}',title=step['title'],text=step['text'],code=step['code'],region={k:row[k] for k in ['x','y','w','h']},inlineLabel=row['x']+row['w']<.58))
                        if len(comments)==3:break
                    if len(comments)==3:break
                # Small listings may only contain declarations; still offer a precise anchored reading aid.
                if code and not comments:
                    for block in code:
                        for step in block['steps']:
                            row=next((r for r in rows if norm(step['code'])==norm(r['text'])),None)
                            if row:
                                comments.append(dict(id=f'comment-{slide["page"]}-1',title=step['title'],text=step['text'],code=step['code'],region={k:row[k] for k in ['x','y','w','h']},inlineLabel=row['x']+row['w']<.58));break
                        if comments:break
                if code and not comments:
                    explanatory=slide.get('explanation') or next((b['text'] for b in blocks if len(b['text'])>80),'')
                    sentence=re.split(r'(?<=[.!?])\s+',re.sub(r'\s+',' ',explanatory))[0]
                    for block in code:
                        if not re.search(r'[;{}#]|c\+\+|\w+\(|<<|std::',block['text']):continue
                        candidates=[r for r in rows if any(norm(r['text']) in norm(line) or norm(line) in norm(r['text']) for line in block['text'].splitlines() if len(norm(line))>5)]
                        if candidates and sentence:
                            row=candidates[0];text=sentence if len(sentence)<=400 else sentence[:397]+'…'
                            comments.append(dict(id=f'comment-{slide["page"]}-1',title='Punto chiave',text=text,code=row['text'],region={k:row[k] for k in ['x','y','w','h']},inlineLabel=False))
                            if not block['steps']:block['steps']=[dict(line=1,code=block['text'].splitlines()[0],title='Lettura del frammento',text=text)]
                            break
                slide['guide']=dict(blocks=blocks,code=code,comments=comments,sourcePages=sorted({b['sourcePage'] for b in blocks}),exactReferences=bool(exact))
                # Explicit original frame-to-file mapping determines these placements.
                stats['slides']+=1;stats['codeSlides']+=bool(code);stats['commentedSlides']+=bool(comments);stats['comments']+=len(comments);stats['exampleBanners']+=bool(slide['examples']);stats['explainedSlides']+=bool(blocks or slide.get('explanation'))
    content['revision']=digest(json.dumps(content['lessons'],sort_keys=True,ensure_ascii=False))
    (WEB/'course-content.json').write_text(json.dumps(content,ensure_ascii=False))
    report=dict(stats,revision=content['revision'])
    (ROOT/'.local/reports/slide-guides.json').write_text(json.dumps(report,indent=2))
    print(report)

if __name__=='__main__':build()
