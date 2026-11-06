"""Verify the real HTTP contract with a dedicated loopback test server."""
import http.client,json,sys,threading,unittest,urllib.request,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server
class HTTP(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.http=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
  cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True);cls.thread.start()
 @classmethod
 def tearDownClass(cls):cls.http.shutdown();cls.http.server_close();cls.thread.join()
 def request(self,path,body=None,headers=None):
  connection=http.client.HTTPConnection('127.0.0.1',self.http.server_port)
  method='GET' if body is None else 'POST'
  headers={'Host':'127.0.0.1:8765',**(headers or {})}
  connection.request(method,path,body=body,headers=headers)
  response=connection.getresponse();status=response.status;raw=response.read();connection.close();return status,raw
 def test_documents(self):
  resources=['/','/app.js','/catalog.json','/snippet-projects.json','/course-content.json','/course-view.js','/annotations.js','/study-store.js','/study.css','/session-store.js','/session.js','/source/materiali_corso_2025_26/lectures/basics/basics.pdf']
  for path in resources:
   with self.subTest(path=path):
    local=(server.WORKSPACE/path[len('/source/'):]) if path.startswith('/source/') else server.BASE/'web'/path.lstrip('/')
    if path.endswith(('.json','.pdf')) and not local.is_file():self.skipTest('Contenuto del corso non distribuito: aggiungi le fonti e rigenera i cataloghi')
    status,raw=self.request(path);self.assertEqual(status,200);self.assertTrue(raw)
 def test_source_traversal(self):
  status,_=self.request('/source/../../etc/passwd');self.assertEqual(status,404)
 def test_origin_and_token(self):
  body=json.dumps({'files':{'m.cc':'int main(){}'},'sources':['m.cc']})
  status,_=self.request('/api/compile',body);self.assertEqual(status,403)
  status,_=self.request('/api/compile',body,{'X-Studio-Token':server.TOKEN,'Origin':'http://example.invalid'});self.assertEqual(status,403)
 def test_bad_json(self):
  status,_=self.request('/api/compile','{broken',{'X-Studio-Token':server.TOKEN});self.assertEqual(status,400)
 def test_compile(self):
  body=json.dumps({'files':{'m.cc':'#include <iostream>\nint main(){std::cout<<42;}'},'sources':['m.cc'],'run':True})
  status,raw=self.request('/api/compile',body,{'X-Studio-Token':server.TOKEN})
  self.assertEqual(status,200);self.assertEqual(json.loads(raw)['run']['stdout'],'42')
 def test_cancel_before_registration(self):
  request_id=uuid.uuid4().hex;headers={'X-Studio-Token':server.TOKEN}
  status,raw=self.request('/api/cancel',json.dumps({'requestId':request_id}),headers)
  self.assertEqual(status,200);self.assertTrue(json.loads(raw)['cancelled'])
  status,raw=self.request('/api/compile',json.dumps({'requestId':request_id,'files':{'m.cc':'int main(){for(;;){}}'},'sources':['m.cc'],'run':True}),headers)
  self.assertEqual(status,200);self.assertTrue(json.loads(raw)['compile']['cancelled'])
if __name__=='__main__':unittest.main()
