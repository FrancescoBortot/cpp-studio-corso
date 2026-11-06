"""Execution checks with explicit inputs and independent expected observations."""
import base64,json,math,re,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import compile_code
base=Path(__file__).resolve().parents[1];catalog=json.loads((base/'web/catalog.json').read_text());results=[]
(Path(__file__).resolve().parents[2]/'.local/reports').mkdir(parents=True,exist_ok=True)

def run(lesson_id,example_id,stdin=None,args=None,extra=None,replace=None):
    lesson=next(l for l in catalog['lessons'] if l['id']==lesson_id)
    example=next(e for e in lesson['examples'] if e['id']==example_id)
    files={f:example.get('patches',{}).get(f,lesson['files'][f]) for f in example['files']}
    files.update(example.get('extraFiles',{}));files.update(extra or {})
    if replace:
        for old,new in replace:files[example['main']]=files[example['main']].replace(old,new)
    request=dict(files=files,sources=example['sources'],standard=example['standard'],root=example['root'],binaryFiles=example.get('binaryFiles',{}),defines=example.get('defines',[]),stdin=example.get('stdin','') if stdin is None else stdin,args=example.get('args',[]) if args is None else args,run=True)
    response=compile_code(request)
    assert response['compile']['code']==0,(lesson_id,example_id,response['compile']['stderr'][:1500])
    assert response.get('run',{}).get('code')==0,(lesson_id,example_id,response.get('run'))
    results.append(dict(lesson=lesson_id,id=example_id,status='pass',fixture='Original input data' if not replace else 'Loop count reduced from 100000000 to 1000 for bounded testing',stdout=response['run']['stdout'][:3000],artifacts=[dict(name=a['name'],bytes=a['bytes']) for a in response.get('artifacts',[])]))
    print('PASS',lesson_id,example_id,flush=True)
    return response

r=run('basics','op_ref.cc');assert r['run']['stdout']=='i=12 , r=12\ni=24 , r=24\n'
r=run('basics','op_num.cc');assert 'divisions: 3 , 3 , 3.5' in r['run']['stdout']
r=run('basics','iofile.cc',extra={'num.txt':'1 2 3\n'});assert r['run']['stdout']=='2 6 12\n';assert base64.b64decode(next(a for a in r['artifacts'] if a['name']=='num.out')['data'])==b'2 6 12\n'
r=run('preproc','testSelect.cc');assert 'Aldo was selected' in r['run']['stdout']
r=run('slspec','testStaticBlock.cc');assert r['run']['stdout'].endswith('1 10\nfinal: 10\n')
r=run('composite','struct.cc');values=[float(x) for x in r['run']['stdout'].split()];expected=[math.hypot(2.3,4.5),math.hypot(6.1,1.8),math.hypot(2.3-6.1,4.5-1.8)];assert all(abs(a-b)<1e-4 for a,b in zip(values,expected))
run('objcopy','copy/testFloatArrayPrint.cc')
r=run('template','tfunc/testPerm.cc');assert '23 34 12' in r['run']['stdout']
r=run('stl','sequences/vecmem.cc');assert 'first: 3 , last: 999' in r['run']['stdout']
r=run('inhpol','vfunct/testShapePtr.cc');assert 'shape 4 has perimeter 17.6 and area 19.36' in r['run']['stdout']
run('pattern','visitor/testShape.cc')
run('rvalue','rvfunc.cc')
r=run('thread','dataRace/rfix.cc');assert r['run']['stdout']=='0 errors found\n'
r=run('conclusions','fitSim/sim.cc');hits=base64.b64decode(next(a for a in r['artifacts'] if a['name']=='hits.txt')['data']).decode().splitlines();assert len(hits)==100000 and all(0<=float(x)<=2.1 for x in hits)
r=run('pattern','proxy/rootProxy.cc');hist=next(a for a in r['artifacts'] if a['name']=='f.root');assert base64.b64decode(hist['data']).startswith(b'root')
readback=compile_code(dict(files={'check.cc':'#include <TFile.h>\n#include <TH1.h>\n#include <iostream>\nint main(){TFile file("f.root");auto* h=dynamic_cast<TH1*>(file.Get("hist_100_0_1"));if(!h)return 2;std::cout<<h->GetEntries()<<"\\n";return h->GetEntries()!=100;}'},binaryFiles={'f.root':hist['data']},sources=['check.cc'],standard='c++23',root=True,run=True))
assert readback['run']['code']==0 and readback['run']['stdout']=='100\n',readback
r=run('conclusions','fitSim/fit.cc');parameters=base64.b64decode(next(a for a in r['artifacts'] if a['name']=='parameters.txt')['data']).decode().split();assert len(parameters)==4 and all(math.isfinite(float(x)) for x in parameters)
run('conclusions','fitSim/his.cc')
r=run('thread','synchroFill.cc',replace=[('100000000','1000')]);assert r['run']['stdout']=='2000\n'
(base.parent/'.local/reports/runtime-verification.json').write_text(json.dumps(dict(checks=results,root_readback='100 histogram entries verified after export and re-import',excluded='Programs with intentional undefined behavior or data races are compiled but no deterministic runtime result is claimed.'),indent=2))
print('Runtime checks complete:',len(results),'examples + ROOT readback',flush=True)
