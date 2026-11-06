"""Render source pages so diagrams and equations remain readable in the notebook."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,shutil,subprocess,tempfile
base=Path(__file__).resolve().parents[1];root=base.parent/'materiali';out=base/'web/references';out.mkdir(exist_ok=True)
renderer=shutil.which('pdftoppm')
if not renderer:raise SystemExit('pdftoppm is needed only to regenerate reference previews')
catalog=json.loads((base/'web/catalog.json').read_text())
jobs=[('dispensa',root/'dispensa_cpp_unipd_2025_26_stile_compatto (1).pdf',6,137)]
jobs += [(l['id'],root/f'materiali_corso_2025_26/lectures/{l["id"]}/{l["id"]}.pdf',1,len(l['slides'])) for l in catalog['lessons']]
def render(job):
 name,path,start,end=job
 if all((out/f'{name}-{p}.jpg').is_file() for p in range(start,end+1)):return end-start+1
 with tempfile.TemporaryDirectory(prefix='cpp-pdf-render-') as tmp:
  prefix=Path(tmp)/'page'
  subprocess.run([renderer,'-f',str(start),'-l',str(end),'-scale-to','1400','-jpeg','-jpegopt','quality=80',str(path),str(prefix)],check=True,timeout=180,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
  for image in Path(tmp).glob('page-*.jpg'):
   page=int(image.stem.rsplit('-',1)[1]);shutil.copyfile(image,out/f'{name}-{page}.jpg')
 return end-start+1
with ThreadPoolExecutor(max_workers=2) as pool:count=sum(pool.map(render,jobs))
assert len(list(out.glob('*.jpg')))==count
print('Verified reference previews:',count)
