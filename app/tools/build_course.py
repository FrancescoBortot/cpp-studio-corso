"""Create an auditable core course: every slide and every non-appendix handout block."""
from pathlib import Path
import collections,hashlib,json,re
APP=Path(__file__).resolve().parents[1];ROOT=APP.parent
catalog=json.loads((APP/'web/catalog.json').read_text())
extra=json.loads((APP/'content/extra-lessons.json').read_text())

def normalize(text):return re.sub(r'\s+',' ',text.replace('ﬁ','fi').replace('ﬂ','fl')).strip()
def digest(text):return hashlib.sha256(text.encode()).hexdigest()[:20]
def words(text):return set(re.findall(r'[a-zA-Z_]{4,}',text.lower()))
def source_refs(text,source):
    pages=set()
    for n,raw in re.findall(r'\[S(\d+), pp?\. ([\d,\s–-]+)\]',text):
        if int(n)!=source:continue
        for part in raw.split(','):
            limits=re.findall(r'\d+',part)
            if len(limits)==1:pages.add(int(limits[0]))
            elif len(limits)==2:pages.update(range(int(limits[0]),int(limits[1])+1))
    return pages

lessons=[];coverage=[];excluded_all=[]
for index,lesson in enumerate(catalog['lessons']):
    sections=[];section=None;excluding=False;excluded=[];core_ids=[]
    for page in lesson['dispensa']:
        for ordinal,block in enumerate(page['blocks']):
            text=normalize(block['text']);bid=f'd-{page["page"]}-{ordinal}'
            if re.match(r'^Approfondimento\b',text,re.I):
                if block['kind']=='heading':excluding=True
                excluded.append(dict(id=bid,page=page['page'],reason='Approfondimento',text=text));continue
            if block['kind']=='heading' and re.match(r'^\d+\.\d+\b',text):excluding=False
            if excluding:
                excluded.append(dict(id=bid,page=page['page'],reason='Inside appendix',text=text));continue
            number=re.match(r'^(\d+\.\d+(?:\.\d+)*)\b',text) if block['kind']=='heading' else None
            if section is None or number:
                sid=lesson['id']+'-'+(number.group(1).replace('.','-') if number else 'introduzione')
                if any(s['id']==sid for s in sections):sid+='-'+bid
                section=dict(id=sid,title=text if number else lesson['title'],blocks=[],slidePages=[],pages=[])
                sections.append(section)
            entry=dict(id=bid,kind=block['kind'],text=block['text'],origin='dispensa',page=page['page'],fingerprint=digest(block['text']),sectionId=section['id'])
            section['blocks'].append(entry);core_ids.append(bid)
            if page['page'] not in section['pages']:section['pages'].append(page['page'])
            section['slidePages']=sorted(set(section['slidePages'])|source_refs(block['text'],index+1))
    # A chapter-only cover is not a useful separate study stop. Preserve its blocks.
    if len(sections)>1 and all(b["kind"]=="heading" for b in sections[0]["blocks"]):
        cover=sections.pop(0)
        for b in cover["blocks"]:b["sectionId"]=sections[0]["id"]
        sections[0]["blocks"]=cover["blocks"]+sections[0]["blocks"]
        sections[0]["pages"]=sorted(set(cover["pages"]+sections[0]["pages"]))
        sections[0]["slidePages"]=sorted(set(cover["slidePages"]+sections[0]["slidePages"]))
    if not sections:
        for p,(title,explanation) in enumerate(extra[lesson['id']],1):
            sid=lesson['id']+'-slide-'+str(p)
            sections.append(dict(id=sid,title=title,blocks=[dict(id=f'e-{lesson["id"]}-{p}',kind='text',text=explanation,origin='editorial',page=p,fingerprint=digest(explanation),sectionId=sid)],slidePages=[p],pages=[]))
    # Lecturer example index: retain frame-to-source correspondence.
    frame=None;frame_files=collections.defaultdict(list)
    for line in lesson['mapping'].splitlines():
        match=re.match(r'frame\s+(\d+)\s+(.*)',line)
        if match:frame=int(match.group(1));value=match.group(2)
        elif frame is not None and line.startswith(' '):value=line.strip()
        else:continue
        if frame is not None and value:frame_files[frame].append(value)
    slides=[]
    for page in lesson['slides']:
        body=[]
        for ordinal,block in enumerate(page['blocks']):
            if ordinal==0 and normalize(block['text'])==normalize(lesson['slides'][0]['blocks'][0]['text']):continue  # repeated deck navigation only
            # Footer can share the final paragraph; remove only that recognized line.
            lines=[line for line in block['text'].splitlines() if not normalize(line).startswith('ObjectorientedprogrammingandC++')]
            text='\n'.join(lines).strip()
            if not text:continue
            body.append(dict(id=f's-{page["page"]}-{ordinal}',kind=block['kind'],text=text,origin='slide',page=page['page'],fingerprint=digest(text)))
        explicit=[s for s in sections if page['page'] in s['slidePages']]
        if explicit:linked=explicit
        else:
            candidates=[(abs(page['page']-p),s) for s in sections for p in s['slidePages']]
            if candidates:linked=[min(candidates,key=lambda pair:pair[0])[1]]
            else:
                tokens=words(' '.join(b['text'] for b in body))
                linked=[max(sections,key=lambda s:len(tokens&words(' '.join(b['text'] for b in s['blocks']))))]
        references=frame_files.get(page['page'],[])
        matches=[]
        for example in lesson['examples']:
            if any(any(f.startswith(ref) if ref.endswith('/') else f==ref for f in example['files']) for ref in references):matches.append(example['id'])
        title=next((normalize(b['text']) for b in body if b['kind']=='heading'),normalize(body[0]['text']) if body else lesson['title'])
        editorial=extra.get(lesson['id'],[])
        explanation=editorial[page['page']-1][1] if editorial else None
        for block in body:block['sectionId']=linked[0]['id']
        slides.append(dict(id=f'{lesson["id"]}-slide-{page["page"]}',page=page['page'],title=editorial[page['page']-1][0] if editorial else title,blocks=body,sectionIds=[s['id'] for s in linked],explanation=explanation,examples=matches,image=f'references/{lesson["id"]}-{page["page"]}.jpg',imageFingerprint=hashlib.sha256((APP/f'web/references/{lesson["id"]}-{page["page"]}.jpg').read_bytes()).hexdigest()[:20] if (APP/f'web/references/{lesson["id"]}-{page["page"]}.jpg').is_file() else '',fingerprint=digest(page['text'])))
        coverage.append(dict(lesson=lesson['id'],slide=page['page'],sectionIds=[s['id'] for s in linked],sourceBlocks=len(body)))
    for item in sections:item['fingerprint']=digest('\n'.join(b['text'] for b in item['blocks']))
    excluded_all.extend(dict(lesson=lesson['id'],**b) for b in excluded)
    excluded_snippets=[]
    for snippet in lesson['snippets']:
        if any(b['page']==snippet['page'] and b['text']==normalize(snippet['code']) for b in excluded):excluded_snippets.append(snippet['id'])
    lessons.append(dict(id=lesson['id'],title=lesson['title'],sections=sections,slides=slides,excludedBlockIds=[b['id'] for b in excluded],coreBlockIds=core_ids,excludedSnippetIds=excluded_snippets))
version=digest(json.dumps(lessons,ensure_ascii=False,sort_keys=True))
output=dict(schema=1,revision=version,lessons=lessons,policy='All lecture slides and handout core are included. Sections explicitly marked Approfondimento in the handout are excluded from the primary course. Slide information is always retained, including points also discussed in an appendix.')
(APP/'web/course-content.json').write_text(json.dumps(output,ensure_ascii=False))
report=dict(revision=version,lessons=len(lessons),slides=len(coverage),handoutCoreBlocks=sum(len(l['coreBlockIds']) for l in lessons),excludedAppendixBlocks=len(excluded_all),sections=sum(len(l['sections']) for l in lessons),coverage=coverage,excluded=excluded_all,editorialExtraSlides=sum(len(v) for v in extra.values()))
(ROOT/'.local/reports').mkdir(parents=True,exist_ok=True)
(ROOT/'.local/reports/content-coverage.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
assert len(coverage)==sum(len(l['slides']) for l in catalog['lessons'])
assert all(s['sectionIds'] and s['blocks'] for l in lessons for s in l['slides'])
assert all(set(l['coreBlockIds']).isdisjoint(l['excludedBlockIds']) for l in lessons)
print({k:report[k] for k in ['lessons','slides','sections','handoutCoreBlocks','excludedAppendixBlocks','editorialExtraSlides']})
