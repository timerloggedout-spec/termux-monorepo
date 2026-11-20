import json, gzip
def load_json_gz(p):
    with gzip.open(str(p), 'rt') as f: return json.load(f)
def save_json_gz(p, data, **kw):
    with gzip.open(str(p), 'wt', compresslevel=9) as f: json.dump(data, f, **kw)
