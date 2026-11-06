"""Adapt the project-local ROOT module map to the installed Apple C++ SDK."""
from pathlib import Path
import hashlib,json,subprocess
base=Path(__file__).resolve().parents[1];root=base/'.runtime/root'
sdk=Path(subprocess.check_output(['xcrun','--show-sdk-path'],text=True).strip())
source=sdk/'usr/include/c++/v1/module.modulemap';target=root/'etc/cling/std_darwin.modulemap'
backup=target.with_suffix('.modulemap.original')
if not backup.exists():backup.write_bytes(target.read_bytes())
content='module std [system] {\nexport *\n'+source.read_text()+'\n}\n'
if target.read_text()!=content:target.write_text(content)
(base/'.runtime/root-compatibility.json').write_text(json.dumps({'sdk':str(sdk),'modulemap_source':str(source),'modulemap_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'change':'ROOT flat standard-library module map regenerated from the installed SDK; original retained beside it.'},indent=2))
print('ROOT module map aligned with the installed Apple SDK')
