#!/usr/bin/env python3
"""Local single-user HTTP interface; all compilation is delegated to engine."""
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import unquote
import json,re,secrets,threading,time
from engine import compile_code,COMPILER,SANDBOX,root_config

BASE=Path(__file__).resolve().parent;WORKSPACE=BASE.parent/'materiali';TOKEN=secrets.token_urlsafe(32)
GATE=threading.Semaphore(2);JOBS={};PENDING_CANCEL={};JOBS_LOCK=threading.Lock()
ALLOWED_HOSTS=('127.0.0.1:8765','localhost:8765')

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(BASE/'web'),**kwargs)

    def end_headers(self):
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Cache-Control','no-store')
        super().end_headers()

    def reply(self,value,status=200):
        raw=json.dumps(value).encode()
        self.send_response(status);self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(raw)));self.end_headers()
        try:self.wfile.write(raw)
        except (BrokenPipeError,ConnectionResetError):pass

    def do_GET(self):
        if self.headers.get('Host') not in ALLOWED_HOSTS:
            return self.send_error(403)
        if self.path=='/api/status':
            return self.reply(dict(token=TOKEN,compiler=COMPILER,root=bool(root_config()),sandbox=bool(SANDBOX)))
        if self.path.startswith('/source/'):
            path=(WORKSPACE/unquote(self.path[len('/source/'):].split('?')[0])).resolve()
            allowed=(path==WORKSPACE/'dispensa_cpp_unipd_2025_26_stile_compatto (1).pdf'
                     or path.is_relative_to(WORKSPACE/'materiali_corso_2025_26/lectures'))
            if not allowed or not path.is_file():return self.send_error(404)
            self.send_response(200)
            self.send_header('Content-Type','application/pdf' if path.suffix=='.pdf' else 'text/plain; charset=utf-8')
            self.send_header('Content-Length',str(path.stat().st_size));self.end_headers()
            try:self.wfile.write(path.read_bytes())
            except (BrokenPipeError,ConnectionResetError):pass
            return
        return super().do_GET()

    def do_POST(self):
        if (self.headers.get('Host') not in ALLOWED_HOSTS
            or self.headers.get('X-Studio-Token')!=TOKEN
            or self.headers.get('Origin') not in (None,'http://127.0.0.1:8765','http://localhost:8765')):
            return self.send_error(403)
        if self.path not in ('/api/compile','/api/cancel'):return self.send_error(404)
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=2000000:return self.reply(dict(error='Dimensione richiesta non valida'),413)
            data=json.loads(self.rfile.read(length))
            if not isinstance(data,dict):raise ValueError('Richiesta non valida')
            job_id=data.get('requestId') or secrets.token_hex(16)
            if not isinstance(job_id,str) or not re.fullmatch(r'[A-Za-z0-9-]{1,80}',job_id):raise ValueError('ID richiesta non valido')
        except (ValueError,TypeError,UnicodeDecodeError) as error:
            return self.reply(dict(error=str(error)),400)
        if self.path=='/api/cancel':
            with JOBS_LOCK:
                event=JOBS.get(job_id)
                if event:event.set()
                else:
                    now=time.monotonic()
                    for key,created in list(PENDING_CANCEL.items()):
                        if now-created>30:PENDING_CANCEL.pop(key,None)
                    if len(PENDING_CANCEL)>=256:PENDING_CANCEL.pop(next(iter(PENDING_CANCEL)))
                    PENDING_CANCEL[job_id]=now
            return self.reply(dict(cancelled=True,pending=not bool(event)))
        if not GATE.acquire(blocking=False):return self.reply(dict(error='Attendi la compilazione in corso'),429)
        with JOBS_LOCK:
            if job_id in JOBS:
                GATE.release();return self.reply(dict(error='Richiesta già attiva'),409)
            cancel=threading.Event();JOBS[job_id]=cancel
            if job_id in PENDING_CANCEL:PENDING_CANCEL.pop(job_id,None);cancel.set()
        try:self.reply(compile_code(data,cancel))
        except (ValueError,TypeError,OSError) as error:self.reply(dict(error=str(error)),400)
        finally:
            with JOBS_LOCK:JOBS.pop(job_id,None)
            GATE.release()

if __name__=='__main__':
    print('C++ Studio · http://127.0.0.1:8765',flush=True)
    ThreadingHTTPServer(('127.0.0.1',8765),Handler).serve_forever()
