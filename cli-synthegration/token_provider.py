
import sys, os
sys.path.insert(0, os.path.expanduser("~/deepcli"))
from deepcli.core import get_token as _deepcli_get_token
def get_token():
    return _deepcli_get_token()
