"""Download the official CERN binary in checked byte ranges (project-local)."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import urllib.request,time,json,hashlib
base=Path(__file__).resolve().parents[1]/'.runtime';chunks=base/'download';chunks.mkdir(parents=True,exist_ok=True)
url='https://root.cern/download/root_v6.40.04.macos-26.6-arm64-clang210.tar.gz'
size=336380644;step=2*1024*1024
jobs=[(i,start,min(start+step,size)-1) for i,start in enumerate(range(0,size,step))]
def fetch(job):
 i,start,end=job;p=chunks/f'{i:04d}'
 if p.exists() and p.stat().st_size==end-start+1:return i
 for attempt in range(3):
  try:
   request=urllib.request.Request(url,headers={'Range':f'bytes={start}-{end}'})
   with urllib.request.urlopen(request,timeout=35) as response:
    if response.status!=206 or response.headers.get('Content-Range')!=f'bytes {start}-{end}/{size}':raise RuntimeError('Invalid byte range')
    raw=response.read(end-start+2)
   if len(raw)!=end-start+1:raise RuntimeError('Incomplete range')
   p.write_bytes(raw);return i
  except Exception:
   if attempt==2:raise
with ThreadPoolExecutor(max_workers=6) as pool:
 for count,i in enumerate(pool.map(fetch,jobs),1):
  if count%20==0:print(f'ROOT download: {count}/{len(jobs)} ranges verified',flush=True)
target=base/'root.tar.gz'
with target.open('wb') as out:
 for i,_,_ in jobs:out.write((chunks/f'{i:04d}').read_bytes())
assert target.stat().st_size==size
(base/'root-download.json').write_text(json.dumps({'url':url,'bytes':size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()},indent=2))
print('Official ROOT archive downloaded and ranges verified',flush=True)
