"""Independent final audit of source coverage, assets and claimed snippet builds."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
import base64,json,sys,tarfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import compile_code
base=Path(__file__).resolve().parents[1];catalog=json.loads((base/'web/catalog.json').read_text());projects=json.loads((base/'web/snippet-projects.json').read_text())
(Path(__file__).resolve().parents[2]/'.local/reports').mkdir(parents=True,exist_ok=True)
assert len(catalog['lessons'])==14
previews=0;original_files=0
for lesson in catalog['lessons']:
    archive=base.parent/'materiali'/'materiali_corso_2025_26/lectures'/lesson['id']/'examples.tgz'
    if archive.exists():
        with tarfile.open(archive) as tar:
            originals={('/'.join(Path(m.name).parts[1:]) if Path(m.name).parts[0]=='examples' else m.name):tar.extractfile(m).read() for m in tar if m.isfile()}
        for name,code in lesson['files'].items():
            assert originals[name].decode(errors='replace')==code,(lesson['id'],name,'source altered');original_files+=1
        for name,raw in lesson.get('binaryFiles',{}).items():assert originals[name]==base64.b64decode(raw)
    for page in lesson['slides']:
        assert (base/f'web/references/{lesson["id"]}-{page["page"]}.jpg').is_file();previews+=1
    for page in lesson['dispensa']:
        assert (base/f'web/references/dispensa-{page["page"]}.jpg').is_file();previews+=1
    for example in lesson['examples']:
        assert example['main'] in example['files']
        assert all(f in lesson['files'] for f in example['files'])
        assert all(f in example['files'] for f in example['sources'])
claims=[(key,value) for key,value in projects.items() if value['status'].startswith('verified-')]
def check(pair):
    key,row=pair
    assert all(f in row['files'] for f in row['sources'])
    result=compile_code(dict(files=row['files'],sources=row['sources'],standard=row['standard'],strict=True))['compile']
    return dict(key=key,code=result['code'],diagnostic=result['stderr'][:1500] if result['code'] else '')
with ThreadPoolExecutor(max_workers=3) as pool:checks=list(pool.map(check,claims))
errors=[r for r in checks if r['code']!=0]
report=dict(original_source_files_unchanged=original_files,reference_previews=previews,verified_snippet_projects_recompiled=len(checks),snippet_errors=errors,raw_pdf_extracts=sum(len(l['snippets'])+len(l['slideSnippets']) for l in catalog['lessons']),context_required=sum(r['status']=='context-required' for r in projects.values()),expected_runtime_limitations=['Intentional undefined behavior and data races have no guaranteed output.','ROOT fit diagnostics must be assessed; process success does not prove convergence.'])
(base.parent/'.local/reports/final-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
if errors:raise SystemExit(1)
