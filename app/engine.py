"""Compilation and bounded execution for a personal local workbench."""
from pathlib import Path
import binascii
import base64,os,re,shlex,shutil,signal,subprocess,sys,tempfile,time

BASE=Path(__file__).resolve().parent
COMPILER=shutil.which('clang++') or shutil.which('g++')
SANDBOX=shutil.which('sandbox-exec')
STANDARDS=('c++98','c++03','c++11','c++14','c++17','c++20','c++23')


def root_config():
    bundled=BASE/'.runtime/root/bin/root-config'
    return str(bundled) if bundled.is_file() else shutil.which('root-config')


def kill_group(process):
    try:
        os.killpg(process.pid,signal.SIGKILL)
    except ProcessLookupError:
        pass


def execute(args,cwd,stdin='',timeout=15,cancel=None,env=None):
    if cancel and cancel.is_set():
        return dict(code=None,stdout='',stderr='',timeout=False,cancelled=True)
    with tempfile.TemporaryFile() as out,tempfile.TemporaryFile() as err:
        command=[sys.executable,str(BASE/'runner.py'),'8',*args]
        process=subprocess.Popen(command,cwd=cwd,env=env,stdin=subprocess.PIPE,
                                 stdout=out,stderr=err,start_new_session=True)
        start=time.monotonic();expired=False;cancelled=False;first=True
        try:
            while True:
                if cancel and cancel.is_set():
                    cancelled=True;kill_group(process);process.communicate();break
                if time.monotonic()-start>=timeout:
                    expired=True;kill_group(process);process.communicate();break
                try:
                    process.communicate(stdin.encode() if first else None,timeout=.15)
                    break
                except subprocess.TimeoutExpired:
                    first=False
        finally:
            kill_group(process)
            process.wait()
        out.seek(0);err.seek(0)
        stdout=out.read(200001);stderr=err.read(200001)
        return dict(code=process.returncode,stdout=stdout[:200000].decode(errors='replace'),
                    stderr=stderr[:200000].decode(errors='replace'),timeout=expired,
                    cancelled=cancelled,truncated=len(stdout)>200000 or len(stderr)>200000)


def validate(data):
    if not isinstance(data,dict):
        raise ValueError('Richiesta non valida')
    if any(name in data and not isinstance(data[name],bool) for name in ('strict','root','run')):raise ValueError('Opzioni di compilazione non valide')
    files=data.get('files');sources=data.get('sources');std=data.get('standard','c++17')
    if std not in STANDARDS:
        raise ValueError('Standard non valido')
    if not isinstance(files,dict) or not 1<=len(files)<=150:
        raise ValueError('Dimensione progetto non valida')
    total=0
    for name,code in files.items():
        if not isinstance(name,str) or not isinstance(code,str):
            raise ValueError('File non valido')
        path=Path(name)
        if (not re.fullmatch(r'[A-Za-z0-9_./-]+',name) or path.is_absolute()
            or '..' in path.parts or any(p.startswith(('-', '@')) for p in path.parts)):
            raise ValueError('Percorso non valido')
        if name in ('program','studio-root-batch.cc'):
            raise ValueError('Nome riservato al laboratorio')
        total+=len(code.encode())
    if total>1500000:
        raise ValueError('Dimensione progetto non valida')
    if (not isinstance(sources,list) or not sources or any(not isinstance(s,str) for s in sources) or len(set(sources))!=len(sources)
        or any(not isinstance(s,str) or s not in files or not s.endswith(('.cc','.cpp','.c')) for s in sources)):
        raise ValueError('Seleziona i sorgenti C++ da compilare, senza duplicati')
    defines=data.get('defines',[])
    if (not isinstance(defines,list) or any(not isinstance(d,str) or
        not re.fullmatch(r'[A-Za-z_]\w*(?:=[A-Za-z_0-9.+-]+)?',d) for d in defines)):
        raise ValueError('Macro non valida')
    argv=data.get('args',[]);stdin=data.get('stdin','')
    if not isinstance(argv,list) or len(argv)>100 or any(not isinstance(a,str) or '\0' in a or len(a)>4096 for a in argv):
        raise ValueError('Argomenti non validi')
    if not isinstance(stdin,str) or len(stdin.encode())>65536:
        raise ValueError('Input troppo grande (massimo 64 KiB)')
    binary=data.get('binaryFiles',{})
    if not isinstance(binary,dict):raise ValueError('File binari non validi')
    decoded={}
    for name,value in binary.items():
        if not isinstance(name,str) or not re.fullmatch(r'[A-Za-z0-9_./-]+',name) or Path(name).is_absolute() or '..' in Path(name).parts or name in files or name in ('program','studio-root-batch.cc') or any(p.startswith(('-', '@')) for p in Path(name).parts):raise ValueError('Percorso file binario non valido')
        try:decoded[name]=base64.b64decode(value,validate=True)
        except (binascii.Error,ValueError,TypeError):raise ValueError('Codifica file binario non valida')
        total+=len(decoded[name])
    if len(files)+len(decoded)>150 or total>1500000:raise ValueError('Dimensione progetto non valida')
    return files,sources,std,defines,argv,stdin,decoded


def compile_code(data,cancel=None):
    files,sources,std,defines,argv,stdin,binary=validate(data)
    if not COMPILER:
        raise ValueError('Compilatore non disponibile')
    env=os.environ.copy();root=root_config() if data.get('root') else None
    with tempfile.TemporaryDirectory(prefix='cpp-studio-') as tmp:
        env['TMPDIR']=tmp
        for name,code in files.items():
            target=Path(tmp)/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(code)
        for name,raw in binary.items():
            target=Path(tmp)/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        include_dirs=sorted({str(Path(n).parent) for n in files})
        command=[COMPILER,'-std='+std,*(['-pedantic-errors'] if data.get('strict',True) else []),'-Wall','-Wextra','-pthread',
                 *[v for d in include_dirs for v in ['-I',d]],*sources,'-o','program']
        runtime_dir=None
        if data.get('root'):
            if not root:
                return dict(command='ROOT non disponibile',dependency='ROOT',compile=dict(code=1,stdout='',stderr='Questo esempio richiede ROOT. Installa il runtime o configura root-config.',timeout=False,cancelled=False))
            def config(flag):
                return subprocess.check_output([root,flag],text=True,timeout=10).strip()
            incdir=config('--incdir');libdir=config('--libdir');runtime_dir=str(Path(root).resolve().parents[1])
            # root-config emits paths without quoting when the project path contains spaces.
            # Read path-valued options separately; retain only non-path cflags/libs.
            cflags=config('--cflags').replace('-I'+incdir,'')
            libs=config('--libs').replace('-L'+libdir,'').replace('-Wl,-rpath,'+libdir,'')
            required=next((f[5:] for f in shlex.split(cflags) if f.startswith('-std=')),std)
            required={'c++2b':'c++23','c++2a':'c++20'}.get(required,required)
            if required in STANDARDS and STANDARDS.index(std)<STANDARDS.index(required):
                return dict(command='Standard richiesto da ROOT: '+required,compile=dict(code=1,stdout='',stderr='Il runtime ROOT richiede almeno '+required+'. Cambia lo standard nelle opzioni della cella.',timeout=False,cancelled=False))
            command += ['-I',incdir,'-L',libdir,'-Wl,-rpath,'+libdir]
            command += [f for f in shlex.split(cflags+' '+libs) if not f.startswith('-std=')]
            env['ROOTSYS']=runtime_dir
            env['DYLD_LIBRARY_PATH']=libdir+os.pathsep+env.get('DYLD_LIBRARY_PATH','')
            # Use ROOT's batch mode for notebook runs, without editing original source files.
            batch=Path(tmp)/'studio-root-batch.cc'
            main_code='\n'.join(files[p] for p in sources)
            no_args=bool(re.search(r'\bmain\s*\(\s*(?:void\s*)?\)',main_code))
            signature='()' if no_args else '(int, char**)'
            call='()' if no_args else '(argc, argv)'
            batch.write_text('#undef main\n#include <TROOT.h>\n#include <TApplication.h>\n#include <TTimer.h>\n'
                'class StudioNotebookTimer:public TTimer {public: StudioNotebookTimer():TTimer(100,kTRUE){} '
                'Bool_t Notify() override {if(gApplication && gApplication->IsRunning()) {'
                'gApplication->SetReturnFromRun(kTRUE);gApplication->Terminate(0);TurnOff();}else Reset();return kTRUE;}};\n'
                'extern int studioOriginalMain'+signature+';\n'
                'int main(int argc,char** argv){gROOT->SetBatch(true);StudioNotebookTimer timer;timer.TurnOn();return studioOriginalMain'+call+';}\n')
            command+=['-Dmain=studioOriginalMain',str(batch)]
            cache=Path(tmp)/'.root-module-cache';cache.mkdir()
            env['CLING_MODULES_CACHE_PATH']=str(cache)
            env['TMPDIR']=tmp

        command+=['-D'+d for d in defines]
        result=dict(command=shlex.join(command),compile=execute(command,tmp,timeout=25,cancel=cancel,env=env))
        if result['compile']['code']!=0 or result['compile']['cancelled'] or not data.get('run'):
            return result
        if not SANDBOX:
            result['run']=dict(code=None,stdout='',stderr='Esecuzione disabilitata: sandbox-exec non disponibile.',timeout=False,cancelled=False)
            return result
        def literal(value):
            return '"'+value.replace('\\','\\\\').replace('"','\\"')+'"'
        reads='(subpath "/Users")'
        if runtime_dir:
            reads='(require-all '+reads+' (require-not (subpath '+literal(runtime_dir)+')))'
        profile=('(version 1) (allow default) (deny network*) '+('' if runtime_dir else '(deny process-fork) ')+
                 '(deny file-read-data '+reads+') (deny file-write* (require-all '
                 '(require-not (subpath '+literal(tmp)+')) '
                 '(require-not (subpath '+literal(os.path.realpath(tmp))+')) '
                 '(require-not (literal "/dev/null"))'+('(require-not (subpath '+literal(runtime_dir)+'))' if runtime_dir else '')+'))')
        result['run']=execute([SANDBOX,'-p',profile,str(Path(tmp)/'program'),*argv],tmp,stdin,8,cancel,env)
        artifacts=[];size=0
        for path in sorted(Path(tmp).rglob('*')):
            relative=str(path.relative_to(tmp))
            if path.is_symlink() or not path.is_file() or relative in files or relative in binary:
                continue
            if path.suffix.lower() not in ('.txt','.csv','.json','.svg','.png','.root','.pdf','.out','.dat'):
                continue
            n=path.stat().st_size
            if n>1024*1024 or size+n>4*1024*1024:
                continue
            size+=n;artifacts.append(dict(name=relative,bytes=n,data=base64.b64encode(path.read_bytes()).decode()))
        result['artifacts']=artifacts
        return result
