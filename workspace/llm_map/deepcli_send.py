import sys, json
from pathlib import Path
HOME = Path.home()
sys.path.insert(0, str(HOME / 'deepcli'))
from deepcli.core import chat_completion, get_token, create_session
token = get_token()
sid = create_session(token)
prompt = ' '.join(sys.argv[1:])
print(chat_completion(token, prompt, sid))
