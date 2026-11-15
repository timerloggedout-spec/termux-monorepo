from pathlib import Path
import json,re,yaml
from jsonschema import validate
ROOT=Path(__file__).resolve().parents[1]
def check():
    text=(ROOT/'SKILL.md').read_text(); parts=text.split('---',2)
    if len(parts)!=3 or parts[0].strip(): raise ValueError('Invalid frontmatter delimiters')
    data=yaml.safe_load(parts[1]); validate(data,json.loads((ROOT/'schemas/frontmatter.schema.json').read_text()))
    if data['name']!=ROOT.name: raise ValueError('Directory/name mismatch')
    for link in re.findall(r'\]\(([^)]+)\)',text):
        if '://' not in link:
            target=(ROOT/link.split('#')[0]).resolve()
            if ROOT.resolve() not in target.parents or not target.is_file(): raise ValueError('Invalid resource reference: '+link)
    return {'frontmatter':'pass','skill_references':'pass','name':data['name']}
if __name__=='__main__': print(json.dumps(check(),indent=2))
