import argparse,json
from pathlib import Path
import pandas as pd
from doe_core import load_config,audit

def main():
    p=argparse.ArgumentParser(); p.add_argument('--csv',required=True); p.add_argument('--config',required=True); p.add_argument('--out',required=True); a=p.parse_args()
    report=audit(pd.read_csv(a.csv),load_config(a.config)); dest=Path(a.out)
    dest.parent.mkdir(parents=True,exist_ok=True); dest.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps(report,indent=2)); return 0 if report['release_ready'] else 2
if __name__=='__main__': raise SystemExit(main())
