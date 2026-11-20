cd ~/workspace/llm_map
python3 -c "
import json, sys
from pathlib import Path
HOME = Path.home()

# Load correlation index (chunked)
corr_file = HOME / 'cli-synthegration/workspace/correlation/correlation_index.json'
chunks_dir = corr_file.parent / 'chunks'
if (chunks_dir / 'chunks.idx.json').exists():
    import gzip
    idx = json.loads((chunks_dir / 'chunks.idx.json').read_text())
    for key in idx:
        chunk = chunks_dir / f'{key}.json.gz'
        if chunk.exists():
            with gzip.open(chunk, 'rt') as cf:
                data = json.load(cf)
                corrs = data.get('correlations', {})
                for sid, files in corrs.items():
                    if 'deepcli/core.py' in files:
                        print(f'{sid}: {files[\"deepcli/core.py\"]}')
else:
    corr = json.loads(corr_file.read_text())
    for sid, files in corr.get('correlations', {}).items():
        if 'deepcli/core.py' in files:
            print(f'{sid}: {files[\"deepcli/core.py\"]}')
" 2>/dev/null | head -20