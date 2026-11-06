from pathlib import Path
import json,tarfile,re,hashlib
from pypdf import PdfReader
import pdfplumber
APP=Path(__file__).resolve().parents[1]; BASE=APP.parent/'materiali'; OUT=APP/'web/catalog.json'
(Path(__file__).resolve().parents[2]/'.local/reports').mkdir(parents=True,exist_ok=True)
names=[('intro','Introduzione'),('basics','Fondamenti di C++'),('preproc','Preprocessore'),('slspec','Storage e linkage'),('composite','Struct e classi'),('functions','Funzioni ed effetti collaterali'),('objcopy','Copia e gestione delle risorse'),('template','Template'),('stl','Libreria standard'),('inhpol','Ereditarietà e polimorfismo'),('pattern','Design pattern'),('conclusions','Progettare programmi migliori'),('rvalue','Rvalue e move semantics'),('thread','Thread e concorrenza')]
ranges=[(6,7),(8,28),(29,36),(37,45),(46,65),(66,73),(74,86),(87,96),(97,108),(109,122),(123,135),(136,137)]
r=PdfReader(BASE/'dispensa_cpp_unipd_2025_26_stile_compatto (1).pdf')
lessons=[]
for idx,(slug,title) in enumerate(names):
 folder=BASE/'materiali_corso_2025_26/lectures'/slug
 slides=PdfReader(folder/(slug+'.pdf'))
 pages=[{'page':i+1,'text':p.extract_text() or ''} for i,p in enumerate(slides.pages)]
 files={}; archive=folder/'examples.tgz'
 if archive.exists():
  with tarfile.open(archive) as tar:
   for m in tar.getmembers():
    p=Path(m.name)
    if m.isfile() and m.size<300000 and p.suffix in ['.cc','.cpp','.h','.hpp','.txt','.dat']:
     path='/'.join(p.parts[1:]) if p.parts[0]=='examples' else str(p)
     raw=tar.extractfile(m).read()
     if b'\0' not in raw:files[path]=raw.decode(errors='replace')
 examples=[]
 mains=[p for p,c in files.items() if re.search(r'\bmain\s*\(',c)]
 for main in mains:
  selected={main}; parent=str(Path(main).parent)
  selected.update(p for p in files if str(Path(p).parent)==parent and p.endswith(('.cc','.cpp')) and p not in mains)
  for _ in range(15):
   old=len(selected)
   for p in list(selected):
    for inc in re.findall(r'#\s*include\s*"([^"\n]+)"',files[p]):
     candidates=[str(Path(p).parent/inc),inc]
     match=next((x for x in candidates if x in files),None)
     if not match:
      opts=[x for x in files if x.endswith('/'+inc) or x==inc]
      if len(opts)==1:match=opts[0]
     if match:
      selected.add(match)
      for ext in ['.cc','.cpp','.hpp']:
       cp=str(Path(match).with_suffix(ext))
       if cp in files and cp not in mains:selected.add(cp)
   if len(selected)==old:break
  code='\n'.join(files[p] for p in selected)
  examples.append({'id':main,'title':main,'main':main,'files':sorted(selected),'root':bool(re.search(r'TFile|TH1|TROOT|TCanvas|TRandom|TGraph',code)),'standard':'c++17'})
 disp=[{'page':i,'text':r.pages[i-1].extract_text() or ''} for i in range(*((ranges[idx][0],ranges[idx][1]+1))) ] if idx<12 else []
 exalist=(folder/'exa_list').read_text(errors='replace') if (folder/'exa_list').exists() else ''
 lessons.append({'id':slug,'title':title,'slides':pages,'dispensa':disp,'files':files,'examples':examples,'mapping':exalist,'snippets':[]})
# Extract real monospaced code blocks, preserving original coordinates/indentation.
with pdfplumber.open(BASE/'dispensa_cpp_unipd_2025_26_stile_compatto (1).pdf') as pdf:
 for li,(start,end) in enumerate(ranges):
  for pn in range(start,end+1):
   page=pdf.pages[pn-1]; rows={}
   for c in page.chars:
    if 'Mono' in c['fontname']: rows.setdefault(round(c['top']/3)*3,[]).append(c)
   groups=[]; group=[]; prev=-100
   for y,chars in sorted(rows.items()):
    if y-prev>22 and group:groups.append(group);group=[]
    group.append(sorted(chars,key=lambda c:c['x0']));prev=y
   if group:groups.append(group)
   for block in groups:
    if sum(len(row) for row in block)<35 or len(block)<2:continue
    left=min(c['x0'] for row in block for c in row); lines=[]
    for row in block:
     line=''; x=left
     for c in row:
      gap=c['x0']-x
      if gap>3:line+=' '*round(gap/5.2)
      line+=c['text'];x=c['x1']
     lines.append(line.rstrip())
    code='\n'.join(lines)
    if not re.search(r'[;{}#]',code):continue
    lessons[li]['snippets'].append({'id':f'disp-{pn}-{len(lessons[li]["snippets"])}','page':pn,'code':code,'complete':bool(re.search(r'\bmain\s*\(',code))})
OUT.write_text(json.dumps({'lessons':lessons},ensure_ascii=False))
report={'lessons':len(lessons),'slides':sum(len(l['slides']) for l in lessons),'dispensa_pages':sum(len(l['dispensa']) for l in lessons),'source_files':sum(len(l['files']) for l in lessons),'programs':sum(len(l['examples']) for l in lessons),'pdf_blocks':sum(len(l['snippets']) for l in lessons),'root_programs':[l['id']+'/'+e['id'] for l in lessons for e in l['examples'] if e['root']]}
(APP.parent/'.local/reports/catalog-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
