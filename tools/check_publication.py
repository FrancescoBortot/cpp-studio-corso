"""Validate the public repository boundary, including reachable Git history."""
from pathlib import Path
import re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]

def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT).decode()
def forbidden(path):
    return (path.startswith(('app/.runtime/','.local/','.venv/','app/web/references/','docs/screenshots/'))
            or path.startswith('materiali/') and path!='materiali/README.md'
            or path in ('app/web/catalog.json','app/web/snippet-projects.json','app/web/course-content.json')
            or Path(path).name.startswith(('cpp-studio-sessione','cpp-studio-appunti'))
            or Path(path).name=='.env' or Path(path).name.startswith('.env.') and Path(path).name!='.env.example')

def main():
    paths=set(filter(None,git('ls-files','-z').split('\0')))
    revisions=git('rev-list','--all').splitlines()
    for revision in revisions:
        paths.update(filter(None,git('ls-tree','-r','--name-only','-z',revision).split('\0')))
    bad=sorted(path for path in paths if forbidden(path))
    if bad:raise SystemExit('Non-public artifacts in repository/history:\n'+'\n'.join(bad))
    secret=re.compile(rb'gh[pousr]_[A-Za-z0-9]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')
    for path in paths:
        local=ROOT/path
        if local.is_file() and secret.search(local.read_bytes()):raise SystemExit('Possible credential in '+path)
    print(f'Public boundary verified: {len(paths)} paths, {len(revisions)} reachable commits; no course sources or generated reproductions.')

if __name__=='__main__':main()
