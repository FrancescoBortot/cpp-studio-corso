from pathlib import Path
import json,re
import pdfplumber
base=Path(__file__).resolve().parents[1];cat=json.loads((base/'web/catalog.json').read_text())
def extract(page):
 rows={}
 for c in sorted(page.chars,key=lambda c:c['top']):
  key=next((y for y in reversed(rows) if abs(y-c['top'])<5),None)
  if key is None:key=c['top']
  rows.setdefault(key,[]).append(c)
 blocks=[];current=[];previous=None
 for y,chars in sorted(rows.items()):
  chars=sorted(chars,key=lambda c:c['x0']);mono=[c for c in chars if 'Mono' in c['fontname'] or 'MonL' in c['fontname']]
  kind='code' if len(mono)>max(0,len(chars)*.75) else 'text'
  if kind=='text' and sum('Bold' in c['fontname'] for c in chars)>len(chars)*.6:kind='heading'
  if previous and (kind!=previous[0] or y-previous[1]>24):
   blocks.append({'kind':previous[0],'text':'\n'.join(current)});current=[]
  line='';x=chars[0]['x0']
  for c in chars:
   if c['x0']-x>2:line+=' '*max(1,round((c['x0']-x)/max(c['size']*.5,1)))
   line+=c['text'];x=c['x1']
  current.append(line.rstrip());previous=(kind,y)
 if current:blocks.append({'kind':previous[0],'text':'\n'.join(current)})
 return [b for b in blocks if b['text'].strip() and not b['text'].strip().isdigit()]
with pdfplumber.open(base.parent/'materiali'/'dispensa_cpp_unipd_2025_26_stile_compatto (1).pdf') as pdf:
 for l in cat['lessons']:
  l['snippets']=[]
  for p in l['dispensa']:
   p['blocks']=extract(pdf.pages[p['page']-1])
   for b in p['blocks']:
    if b['kind']=='code' and re.search(r'[;{}#]',b['text']):l['snippets'].append({'id':f'disp-{p["page"]}-{len(l["snippets"])}','page':p['page'],'code':b['text'],'complete':bool(re.search(r'\bmain\s*\(',b['text']))})
for l in cat['lessons']:
 l['slideSnippets']=[]
 with pdfplumber.open(base.parent/'materiali'/f'materiali_corso_2025_26/lectures/{l["id"]}/{l["id"]}.pdf') as pdf:
  for p in l['slides']:
   p['blocks']=extract(pdf.pages[p['page']-1])
   for b in p['blocks']:
    if b['kind']=='code' and re.search(r'[;{}#]',b['text']):l['slideSnippets'].append({'id':f'slide-{p["page"]}-{len(l["slideSnippets"])}','page':p['page'],'code':b['text']})
(base/'web/catalog.json').write_text(json.dumps(cat,ensure_ascii=False))
print('Enriched:',sum(len(l['snippets']) for l in cat['lessons']),'dispensa blocks;',sum(len(l['slideSnippets']) for l in cat['lessons']),'slide blocks')
