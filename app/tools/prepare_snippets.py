"""Build transparent, compiler-checked contexts without changing PDF extracts."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,re,sys,threading
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import compile_code
BASE=Path(__file__).resolve().parents[1]
(Path(__file__).resolve().parents[2]/'.local/reports').mkdir(parents=True,exist_ok=True)
CAT=json.loads((BASE/'web/catalog.json').read_text())
CACHE_DIR=BASE.parent/'.local/verification-cache';CACHE_DIR.mkdir(exist_ok=True)
TOKEN=re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*[\s\S]*?\*/')
def balance(code):
    plain=TOKEN.sub('',code)
    return plain.count('{')-plain.count('}')
def main_present(code):return bool(re.search(r'\bmain\s*\(',TOKEN.sub('',code)))
def hashcode(code):
    value=2166136261
    for c in code:
        value=((value^ord(c))*16777619)&0xffffffff
    return format(value,'x')
HEADERS={'iostream':r'\b(cout|cin|cerr|endl|ostream|istream)\b','vector':r'\bvector\b','string':r'\bstring\b','map':r'\bmap\b','set':r'\bset\b','array':r'\barray\b','deque':r'\bdeque\b','list':r'\blist\b','cmath':r'\b(sqrt|pow|sin|cos|lround|abs)\b','algorithm':r'\b(sort|find|lower_bound|upper_bound|binary_search|for_each|copy)\b','functional':r'\b(function|bind)\b','memory':r'\b(unique_ptr|shared_ptr|auto_ptr|make_shared|make_unique)\b','utility':r'\b(move|forward|swap|pair|make_pair)\b','sstream':r'\b(stringstream|istringstream|ostringstream)\b','limits':r'\bnumeric_limits\b','stdexcept':r'\b(out_of_range|runtime_error)\b','typeinfo':r'\b(bad_cast|typeid)\b','exception':r'\bexception\b','cstdio':r'\b(printf|scanf|sprintf|sscanf)\b','cstdlib':r'\b(rand|random|srand|RAND_MAX|exit|size_t)\b','cstring':r'\b(strlen|strcpy|memcpy)\b','thread':r'\bthread\b','mutex':r'\b(mutex|lock_guard|unique_lock)\b','future':r'\b(future|async|promise|packaged_task)\b','atomic':r'\batomic\b','iomanip':r'\b(setw|setprecision)\b','random':r'\b(mt19937|uniform_int_distribution)\b','fstream':r'\b(ifstream|ofstream|fstream)\b'}

def check(files,std='c++17'):
    sources=[p for p in files if p.endswith(('.cc','.cpp'))]
    request=dict(files=files,sources=sources,standard=std,strict=True)
    key=hashlib.sha256(json.dumps(request,sort_keys=True).encode()).hexdigest()
    cache=CACHE_DIR/(key+'.json')
    if cache.exists():return json.loads(cache.read_text())
    result=compile_code(request)['compile'];cache.write_text(json.dumps(result))
    return result

def continue_code(items,index):
    code=items[index]['code'];pages=[items[index]['page']];count=0
    if index>0 and items[index-1]['page']==items[index]['page']-1 and balance(items[index-1]['code'])>0:
        previous=items[index-1]['code']
        if not main_present(code) or not main_present(previous):code=previous+'\n'+code;pages.insert(0,items[index-1]['page'])
    while balance(code)>0 and index+1<len(items) and count<4:
        current=items[index];nxt=items[index+1]
        # A PDF page break is the only boundary merged automatically.
        if nxt['page']!=current['page']+1 or main_present(nxt['code']):break
        code+='\n'+nxt['code'];pages.append(nxt['page']);index+=1;count+=1
    return code,pages

def dependencies(lesson,code):
    includes=re.findall(r'#\s*include\s*"([^"\n]+)"',code)
    if not includes:return {}
    resolved={};pending=includes[:]
    while pending:
        name=pending.pop()
        matches=[f for f in lesson['files'] if f==name or f.endswith('/'+name)]
        if len(matches)!=1:return None
        path=matches[0]
        if name in resolved:continue
        resolved[name]=lesson['files'][path]
        for ext in ('.cc','.hpp'):
            other=str(Path(path).with_suffix(ext))
            if other in lesson['files'] and not main_present(lesson['files'][other]):
                resolved[Path(other).name]=lesson['files'][other]
        for content in list(resolved.values()):
            for inc in re.findall(r'#\s*include\s*"([^"\n]+)"',content):
                if inc not in resolved and inc not in pending:pending.append(inc)
        if len(resolved)>30:return None
    return resolved


def explicit_context(lesson,origin,snippet):
    if origin!='dispensa':return None
    byid={x['id']:x for x in lesson['snippets']}
    def join(*ids):return '\n'.join(byid[x]['code'] for x in ids)+'\n'
    groups=[]
    if lesson['id']=='slspec':
        groups.append((['disp-41-12','disp-41-13','disp-41-14','disp-41-15'],{
            'shared.h':join('disp-41-12','disp-41-13'),
            'main.cc':join('disp-41-14'),'g.cc':join('disp-41-15')}))
    if lesson['id']=='composite':
        for ids in [('disp-47-8','disp-48-9'),('disp-60-51','disp-61-52'),('disp-61-54','disp-62-55')]:
            groups.append((ids,{'programma.cc':join(*ids)}))
        groups.append((['disp-63-61','disp-64-62','disp-64-63'],{'programma.cc':join('disp-63-61','disp-64-62','disp-64-63')}))
        groups.append((['disp-62-56'],{'supporto.cc':'void useInt(int value) { (void)value; }\n'+join('disp-62-56')}))
    if lesson['id']=='functions':
        groups.append((['disp-71-14','disp-72-15','disp-72-16'],{'programma.cc':'#include <iostream>\n'+join('disp-71-14','disp-72-15','disp-72-16')}))
    if lesson['id']=='objcopy':
        ids=['disp-80-21','disp-80-22','disp-80-23','disp-81-24','disp-81-25','disp-82-26']
        groups.append((ids,{'FloatArray.h':join(*ids[:2]),'FloatArray.cc':join(*ids[2:4]),'main.cc':join(*ids[4:])}))
        if snippet['id'] in ('disp-76-9','disp-77-10'):
            files={'main.cc':join('disp-76-9','disp-77-10')}
            for path in ('dumb/FloatArray.h','dumb/FloatArray.cc'):
                if path in lesson['files']:files[Path(path).name]=lesson['files'][path]
            return files,'Programma ricomposto dalle pagine 76–77; FloatArray.h e FloatArray.cc sono i file della versione iniziale dell’archivio del docente.'
    if lesson['id']=='template':
        ids=['disp-90-11','disp-90-12','disp-91-13','disp-92-14','disp-92-15']
        groups.append((ids,{'Array.h':join(ids[0],ids[3]),'Array.icc':join(ids[1],ids[2]),'main.cc':join(ids[4])}))
    if lesson['id']=='pattern':
        groups.append((['disp-129-11','disp-130-12'],{'programma.cc':join('disp-129-11','disp-130-12')}))
    for ids,files in groups:
        if snippet['id'] in ids:return files,'Contesto completo verificato, ricomposto dai listati della dispensa nelle pagine '+', '.join(map(str,sorted({byid[x]['page'] for x in ids})))+'. Tutti i file aggiunti sono visibili nel laboratorio.'
    return None


def build(job):
    lesson,origin,items,index=job;s=items[index];code=s['code']
    key=lesson['id']+':'+origin+':'+str(s['page'])+':'+hashcode(code)
    row=dict(id=s['id'],lesson=lesson['id'],origin=origin,page=s['page'],pages=[s['page']],status='context-required',note='Frammento concettuale: richiede il contesto indicato nella spiegazione.',files={'frammento.inc':code},sources=[],focusFile='frammento.inc',standard='c++17')
    explicit=explicit_context(lesson,origin,s)
    if explicit:
        files,note=explicit;result=check(files)
        if result['code']==0:
            row.update(status='verified-program',files=files,sources=[p for p in files if p.endswith('.cc')],focusFile=next((p for p,v in files.items() if code in v),next(iter(files))),note=note)
            return key,row
    if '…' in code or re.search(r'(?<!\.)\.\.\.(?!\.)',code) and not ('template' in code or 'args' in code or 'Args' in code):
        row['note']='Il frammento contiene omissioni esplicite; completa le parti indicate prima di compilare.'
        return key,row
    assembled,pages=continue_code(items,index)
    if len(pages)>1:row['pages']=pages
    support=dependencies(lesson,assembled)
    if support is None:support={}
    files={'frammento.cc':assembled,**support}
    if main_present(assembled):
        result=check(files)
        if result['code']==0:
            row.update(status='verified-program',files=files,sources=[p for p in files if p.endswith('.cc')],focusFile='frammento.cc',note='Programma verificato in compilazione.'+(' Ricomposto dalle pagine '+', '.join(map(str,pages))+'.' if len(pages)>1 else '')+(' Header e implementazioni di supporto dagli archivi della stessa lezione.' if support else ''))
            return key,row
        headers=''.join('#include <'+h+'>\n' for h,p in HEADERS.items() if re.search(p,assembled))
        if headers:
            supported={'frammento.inc':assembled,'supporto.cc':headers+'\n#include \"frammento.inc\"\n',**support}
            supported_result=check(supported)
            if supported_result['code']==0:
                row.update(status='verified-program',files=supported,sources=[p for p in supported if p.endswith('.cc')],focusFile='frammento.inc',note='Programma verificato con gli header standard mostrati in supporto.cc.'+(' Ricomposto dalle pagine '+', '.join(map(str,pages))+'.' if len(pages)>1 else ''))
                return key,row
        row['diagnostic']=result['stderr'][:4000]
    else:
        headers=''.join('#include <'+h+'>\n' for h,p in HEADERS.items() if re.search(p,assembled))
        for mode in ('declarations','statements'):
            if mode=='declarations':harness=headers+'\n#include "frammento.inc"\n\nint main() { return 0; }\n'
            else:harness=headers+'\nint main() {\n#include "frammento.inc"\nreturn 0;\n}\n'
            files={'frammento.inc':assembled,'supporto.cc':harness,**support}
            result=check(files)
            if result['code']==0:
                row.update(status='verified-context',files=files,sources=[p for p in files if p.endswith('.cc')],note=('Dichiarazioni verificate con main minimo: aggiungi le chiamate per osservare il comportamento.' if mode=='declarations' else 'Istruzioni verificate dentro un main minimo.')+' Il file supporto.cc mostra tutto il contesto aggiunto.'+(' Ricomposto dalle pagine '+', '.join(map(str,pages))+'.' if len(pages)>1 else ''))
                return key,row
        row['diagnostic']=result['stderr'][:4000]
    # The original fragment remains available, with real diagnostics and explicit requirements.
    row['files']={'frammento.cc':assembled};row['sources']=['frammento.cc'];row['focusFile']='frammento.cc'
    return key,row

jobs=[(l,origin,l[field],i) for l in CAT['lessons'] for origin,field in [('dispensa','snippets'),('slide','slideSnippets')] for i in range(len(l[field]))]
results={}
with ThreadPoolExecutor(max_workers=3) as pool:
    for count,(key,result) in enumerate(pool.map(build,jobs),1):
        results[key]=result
        if count%75==0:print('Frammenti controllati:',count,'/',len(jobs),flush=True)
(BASE/'web/snippet-projects.json').write_text(json.dumps(results,ensure_ascii=False))
from collections import Counter
report=dict(total_extracts=len(jobs),unique_projects=len(results),statuses=dict(Counter(r['status'] for r in results.values())))
(BASE.parent/'.local/reports/snippet-verification.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
