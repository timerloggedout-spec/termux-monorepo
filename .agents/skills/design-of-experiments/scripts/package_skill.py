from pathlib import Path
import argparse,zipfile
from check_package import check,ROOT

def main():
    p=argparse.ArgumentParser(); p.add_argument('--out-dir',required=True); a=p.parse_args(); check()
    dest=Path(a.out_dir); dest.mkdir(parents=True,exist_ok=True)
    dirs={'scripts','references','assets','schemas','examples','evals','tests'}
    files=[f for f in ROOT.rglob('*') if f.is_file() and '__pycache__' not in f.parts and (len(f.relative_to(ROOT).parts)==1 or f.relative_to(ROOT).parts[0] in dirs) and f.suffix not in {'.pyc','.skill','.zip'}]
    for ext in ['skill','zip']:
        target=dest/(ROOT.name+'.'+ext)
        with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
            for f in sorted(files): z.write(f,str(Path(ROOT.name)/f.relative_to(ROOT)))
        print(target)
if __name__=='__main__': main()
