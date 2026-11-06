"""Attach the lecturer's text/binary inputs and original archive notes."""
from pathlib import Path
import base64,json,tarfile,re
base=Path(__file__).resolve().parents[1];path=base/'web/catalog.json';catalog=json.loads(path.read_text())
for lesson in catalog['lessons']:
    archive=base.parent/'materiali'/'materiali_corso_2025_26/lectures'/lesson['id']/'examples.tgz'
    lesson['binaryFiles']={};lesson['guides']={}
    if not archive.exists():continue
    with tarfile.open(archive) as tar:
        for member in tar:
            if not member.isfile() or member.size>300000:continue
            p=Path(member.name);name='/'.join(p.parts[1:]) if p.parts[0]=='examples' else str(p)
            raw=tar.extractfile(member).read()
            if p.name in ('summary','description'):
                lesson['guides'][name]=raw.decode(errors='replace')
            if p.suffix in ('.root','.pdf'):
                lesson['binaryFiles'][name]=base64.b64encode(raw).decode()
    for example in lesson['examples']:
        parent=str(Path(example['main']).parent)
        example['extraFiles']={Path(f).name:text for f,text in lesson['files'].items() if str(Path(f).parent)==parent and f.endswith(('.txt','.dat'))}
        example['binaryFiles']={Path(f).name:data for f,data in lesson['binaryFiles'].items() if str(Path(f).parent)==parent}
        guide=str(Path(parent)/'summary') if parent!='.' else 'summary'
        example['guide']=lesson['guides'].get(guide,'')
        if lesson['id']=='basics' and example['id']=='op_ref.cc':example['stdin']='12\n24\n'
        if lesson['id']=='basics' and example['id']=='op_num.cc':example['stdin']='7 2\n'
        if lesson['id']=='basics' and example['id']=='op_ptr.cc':example['stdin']='12 23 34\n'
        if lesson['id']=='pattern' and example['id']=='proxy/rootProxy.cc':example['stdin']='100 f 0 1\n'
        if lesson['id']=='conclusions':
            if example['id']=='fitSim/sim.cc':example['args']=['1','eff.txt','hits.txt']
            if example['id']=='fitSim/fit.cc':example['args']=['eff.root','parameters.txt']
            if example['id']=='fitSim/his.cc':
                example['extraFiles']['hits.txt']='0.1\n0.4\n0.9\n1.2\n1.6\n1.9\n'
                example['args']=['hits.txt']
                example['notes']+=' Il file hits.txt contiene un piccolo input di supporto aggiunto dal laboratorio.'
        code='\n'.join(lesson['files'][f] for f in example['files'])
        referenced=set(re.findall(r'"([^"\n]+\.(?:txt|dat|root|pdf))"',code))|set(example.get('args',[]))
        referenced={Path(name).name for name in referenced}
        example['extraFiles']={name:text for name,text in example['extraFiles'].items() if Path(name).name in referenced}
        example['binaryFiles']={name:raw for name,raw in example['binaryFiles'].items() if Path(name).name in referenced}
        if example['root']:example['notes']+=' Esecuzione ROOT in modalità batch; i file prodotti sono scaricabili dall’output.'
        if 'dataRace/race.cc' in example['id'] or example['id']=='histoFill.cc':example['notes']+=' Esempio con data race intenzionale: un risultato osservato non è garantito dal linguaggio.'
        if example['id']=='dangle.cc':example['notes']+=' Esempio con puntatore pendente: dereferenziarlo produce comportamento indefinito.'
path.write_text(json.dumps(catalog,ensure_ascii=False));print('Data files, archive guides and example inputs attached')
