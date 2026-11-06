"""Rebuild generated assets from local originals, or check the current layout."""
from pathlib import Path
import argparse,importlib.util,shutil,subprocess,sys
APP=Path(__file__).resolve().parents[1];PROJECT=APP.parent
MATERIALS=PROJECT/'materiali';WEB=APP/'web'

def check_sources():
    required=[MATERIALS/'dispensa_cpp_unipd_2025_26_stile_compatto (1).pdf',MATERIALS/'materiali_corso_2025_26/lectures/index.html']
    missing=[str(p.relative_to(PROJECT)) for p in required if not p.is_file()]
    if missing:raise SystemExit('Fonti mancanti: '+', '.join(missing)+'. Consulta materiali/README.md.')

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    check_sources()
    (PROJECT/'.local/reports').mkdir(parents=True,exist_ok=True)
    if args.check:
        missing=[name for name in ['catalog.json','snippet-projects.json','course-content.json'] if not (WEB/name).is_file()]
        if missing:raise SystemExit('Esegui la ricostruzione: mancano '+', '.join(missing))
        import json
        catalog=json.loads((WEB/'catalog.json').read_text());count=0
        for lesson in catalog['lessons']:
            for source,pages in [(lesson['id'],lesson['slides']),('dispensa',lesson['dispensa'])]:
                for page in pages:
                    path=WEB/'references'/f'{source}-{page["page"]}.jpg'
                    if not path.is_file():raise SystemExit('Anteprima mancante: '+str(path.relative_to(PROJECT)))
                    count+=1
        print(f'Struttura verificata: {len(catalog["lessons"])} lezioni e {count} anteprime; fonti e cataloghi presenti.')
        return
    missing=[name for name in ('pypdf','pdfplumber') if importlib.util.find_spec(name) is None]
    if missing:raise SystemExit('Installa requirements-build.txt; mancano: '+', '.join(missing))
    if not shutil.which('pdftoppm'):raise SystemExit('Per generare le anteprime serve pdftoppm nel PATH.')
    for name in ['catalog.py','enrich.py','configure.py','enrich_assets.py','prepare_snippets.py','render_references.py','build_course.py','build_slide_guides.py']:
        print('Generazione:',name,flush=True)
        subprocess.run([sys.executable,str(APP/'tools'/name)],cwd=PROJECT,check=True)
    print('Ricostruzione completata. Avvia python3 app/server.py.')

if __name__=='__main__':main()
