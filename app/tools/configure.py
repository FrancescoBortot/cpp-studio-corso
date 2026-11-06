from pathlib import Path
import json,re
b=Path(__file__).resolve().parents[1];cat=json.loads((b/'web/catalog.json').read_text())
for l in cat['lessons']:
 for e in l['examples']:
  m=e['main'];e['sources']=[f for f in e['files'] if f.endswith(('.cc','.cpp'))];e['notes']='';e['patches']={}
  if l['id']=='basics' and m!='subdec.cc':e['sources']=[f for f in e['sources'] if f!='irfunc.cc']
  if l['id']=='slspec' and m!='testStaticExt.cc':e['sources']=[f for f in e['sources'] if f not in ['gFunc.cc','dummy.cc']]
  if l['id']=='inhpol' and 'hidden/testVector3D' in m:e['sources']=[f for f in e['sources'] if ('Vector3D03.cc' not in f if '11' in m else 'Vector3D11.cc' not in f)]
  if l['id']=='conclusions' and m=='fitSim/sim.cc':e['sources']=['fitSim/sim.cc','fitSim/HitEfficiency.cc'];e['root']=False
  if l['id']=='preproc' and m=='testSelect.cc':e['defines']=['SELECTED=ALDO'];e['notes']='La macro SELECTED è necessaria: cambia ALDO in GIOVANNI o GIACOMO per osservare la selezione a compilazione.'
  if l['id']=='stl' and m=='smartp/autop.cc':e['standard']='c++14';e['notes']='auto_ptr è storico: usa C++14. È rimosso da C++17; confrontalo con unique_ptr.'
  if l['id']=='objcopy' and ('safe/' in m or 's_98/' in m) and m.endswith('testFloatArrayPrint.cc'):e['notes']='Errore didattico atteso: print prende per valore un oggetto la cui copia è vietata. Prova a usare const FloatArray&.';e['expectedError']=True
  if l['id']=='composite' and m.startswith('defdel/'):
   p='defdel/Point.cc';e['patches'][p]=l['files'][p].replace('Point( x, x )','Point( d, d )');e['notes']='Refuso originale: il costruttore riceve d ma delega usando x. La variante corretta sostituisce x con d.'
  if l['id']=='stl' and m=='assoc/test_rev.cc':
   e['patches'][m]=l['files'][m].replace('operator()( int l, int r ) {','operator()( int l, int r ) const {');e['notes']='Il comparatore originale non è const. La variante aggiunge const per essere compatibile con la libreria disponibile.'
  if l['id']=='pattern' and m.startswith('iterator/'):
   for f in e['files']:
    if f.endswith(('LinkedList.h','RecursiveTree.h')):
     code=l['files'][f];code=re.sub(r'(class (?:LinkedList|RecursiveTree) \{)',r'\1\n private:\n  class Node; // Dichiarazione anticipata aggiunta per Clang\n',code,count=1);e['patches'][f]=code
   e['notes']='La variante dichiara Node prima dell’uso nella classe Iterator. Il codice originale resta ripristinabile.'
  for source in e['sources']:
   code=e['patches'].get(source,l['files'][source])
   using=re.search(r'^\s*using namespace std;',code,re.M)
   include=re.search(r'^\s*#include',code,re.M)
   if using and (not include or using.start()<include.start()):
    e['patches'][source]='#include <iostream> // std dichiarato prima della direttiva using\n'+code
    e['notes']+=' Variante conforme allo standard: un header dichiara std prima di using namespace std.'
  if e['root']:e['standard']='c++23'
  e['files']=[m]+[f for f in e['files'] if f!=m and (not f.endswith(('.cc','.cpp')) or f in e['sources'])]
(b/'web/catalog.json').write_text(json.dumps(cat,ensure_ascii=False))
print('Ricette e varianti configurate')
