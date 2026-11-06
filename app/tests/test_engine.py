import sys,unittest,base64,threading,time,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from server import compile_code
class Engine(unittest.TestCase):
 def run_code(self,files,**kw):return compile_code({'files':files,'sources':[p for p in files if p.endswith('.cc')],'run':True,**kw})
 def test_input(self):
  r=self.run_code({'m.cc':'#include <iostream>\nint main(){int n;std::cin>>n;std::cout<<n*2;}'},stdin='21')
  self.assertEqual(r['run']['stdout'],'42');self.assertEqual(r['run']['code'],0)
 def test_multi_file(self):
  r=self.run_code({'m.cc':'#include "f.h"\nint main(){return f()!=42;}','f.h':'int f();','f.cc':'int f(){return 42;}'})
  self.assertEqual(r['run']['code'],0)
 def test_diagnostic(self):
  r=self.run_code({'m.cc':'int main(){ missing; }'});self.assertNotEqual(r['compile']['code'],0);self.assertNotIn('run',r)
 def test_macro(self):
  r=self.run_code({'m.cc':'int main(){return VALUE!=42;}'},defines=['VALUE=42']);self.assertEqual(r['run']['code'],0)
 def test_paths(self):
  with self.assertRaises(ValueError):self.run_code({'../bad.cc':'int main(){}'})
 def test_files(self):
  r=self.run_code({'m.cc':'#include <fstream>\nint main(){std::ifstream f("data.txt");int n;f>>n;return n!=42;}','data.txt':'42'})
  self.assertEqual(r['run']['code'],0)
 def test_timeout(self):
  r=self.run_code({'m.cc':'int main(){for(;;){}}'});self.assertNotEqual(r['run']['code'],0)
 def test_standard_selection(self):
  code={'m.cc':'int main(){auto value=42;return value!=42;}'}
  self.assertNotEqual(self.run_code(code,standard='c++98')['compile']['code'],0)
  self.assertEqual(self.run_code(code,standard='c++11')['run']['code'],0)
 def test_binary_data(self):
  r=self.run_code({'m.cc':'#include <fstream>\n#include <iostream>\nint main(){std::ifstream f("data.bin",std::ios::binary);int sum=0;char c;while(f.get(c))sum+=static_cast<unsigned char>(c);std::cout<<sum;}'},binaryFiles={'data.bin':base64.b64encode(bytes([1,2,3,4])).decode()})
  self.assertEqual(r['run']['stdout'],'10')
 def test_artifact(self):
  r=self.run_code({'m.cc':'#include <fstream>\nint main(){std::ofstream f("result.txt");f<<"42\\n";}'})
  item=next(a for a in r['artifacts'] if a['name']=='result.txt')
  self.assertEqual(base64.b64decode(item['data']),b'42\n')
 def test_cancel(self):
  event=threading.Event();timer=threading.Timer(.7,event.set);start=time.monotonic();timer.start()
  try:r=compile_code({'files':{'m.cc':'int main(){for(;;){}}'},'sources':['m.cc'],'run':True},event)
  finally:timer.cancel()
  self.assertTrue(r['compile']['cancelled'] or r.get('run',{}).get('cancelled'))
  self.assertLess(time.monotonic()-start,5)
 def test_private_read_denied(self):
  r=self.run_code({'m.cc':'#include <fstream>\nint main(int argc,char** argv){std::ifstream f(argv[1]);return f?1:0;}'},args=[str(Path(__file__).resolve().parents[1]/'README.md')])
  self.assertEqual(r['run']['code'],0)
 def test_outside_write_denied(self):
  path=Path('/private/tmp')/('cpp-studio-escape-'+uuid.uuid4().hex+'.txt')
  try:
   r=self.run_code({'m.cc':'#include <fstream>\nint main(int argc,char** argv){std::ofstream f(argv[1]);return f?1:0;}'},args=[str(path)])
   self.assertEqual(r['run']['code'],0);self.assertFalse(path.exists())
  finally:
   if path.exists():path.unlink()
 def test_invalid_payloads(self):
  for payload in [None,[],{'files':{'m.cc':1},'sources':['m.cc']},{'files':{'m.cc':'int main(){}'},'sources':[]},{'files':{'m.cc':'int main(){}'},'sources':['m.cc'],'binaryFiles':{'../bad':'AA=='}}]:
   with self.assertRaises((ValueError,TypeError)):compile_code(payload)
if __name__=='__main__':unittest.main()
