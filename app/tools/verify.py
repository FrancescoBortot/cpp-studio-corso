"""Recompile every lecture program; distinguish originals, fixes and expected errors."""
import sys,json,concurrent.futures
from pathlib import Path
from collections import Counter
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import compile_code,root_config
base=Path(__file__).resolve().parents[1];cat=json.loads((base/'web/catalog.json').read_text())
(Path(__file__).resolve().parents[2]/'.local/reports').mkdir(parents=True,exist_ok=True)
def check(pair):
    lesson,example=pair
    if example['root'] and not root_config():return dict(lesson=lesson['id'],id=example['id'],status='requires-root')
    request=dict(files={f:example.get('patches',{}).get(f,lesson['files'][f]) for f in example['files']},sources=example['sources'],standard=example['standard'],defines=example.get('defines',[]),root=example['root'])
    result=compile_code(request)['compile']
    expected=example.get('expectedError',False)
    status='pass' if result['code']==0 and not expected else 'expected-error' if result['code']!=0 and expected and ('deleted' in result['stderr'] or 'private' in result['stderr']) else 'unexpected-error'
    row=dict(lesson=lesson['id'],id=example['id'],status=status,variant=bool(example.get('patches')),diagnostic=result['stderr'][:5000])
    if example.get('patches'):
        request['files']={f:lesson['files'][f] for f in example['files']}
        original=compile_code(request)['compile']
        row['original_code']=original['code'];row['original_diagnostic']=original['stderr'][:2000]
    return row
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    results=list(pool.map(check,[(l,e) for l in cat['lessons'] for e in l['examples']]))
(base.parent/'.local/reports/verification.json').write_text(json.dumps(results,indent=2))
print(dict(Counter(r['status'] for r in results)),flush=True)
for row in results:
    if row['status']=='unexpected-error':print(row['lesson'],row['id'],row['diagnostic'][:600],flush=True)
lookup={(r['lesson'],r['id']):r['status'] for r in results}
for lesson in cat['lessons']:
    for example in lesson['examples']:example['verification']=lookup[(lesson['id'],example['id'])]
(base/'web/catalog.json').write_text(json.dumps(cat,ensure_ascii=False))
if any(r['status'] in ('unexpected-error','requires-root') for r in results):raise SystemExit(1)
