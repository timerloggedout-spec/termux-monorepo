import argparse, hashlib, importlib.metadata, json, platform
from pathlib import Path
from doe_core import load_config, coded_design, audit

def main():
    p=argparse.ArgumentParser(); p.add_argument('--config',required=True); p.add_argument('--out',required=True); a=p.parse_args()
    c=load_config(a.config); df=coded_design(c); report=audit(df,c)
    dest=Path(a.out)
    if dest.exists() and any(dest.iterdir()): raise ValueError('Output directory must be empty to avoid overwriting evidence')
    dest.mkdir(parents=True,exist_ok=True)
    csv=dest/'run-sheet.csv'; df.to_csv(csv,index=False)
    manifest={'python':platform.python_version(),'packages':{n:importlib.metadata.version(n) for n in ['numpy','pandas','scipy','PyYAML','jsonschema']},'seed':c['seed'],'csv_sha256':hashlib.sha256(csv.read_bytes()).hexdigest(),'randomization':'unrestricted; numpy default_rng permutation','status':'design only; no experiment executed'}
    for name,data in [('config.json',c),('audit.json',report),('manifest.json',manifest)]:
        (dest/name).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
    print(json.dumps(report,indent=2)); return 0 if report['release_ready'] else 2
if __name__=='__main__': raise SystemExit(main())
