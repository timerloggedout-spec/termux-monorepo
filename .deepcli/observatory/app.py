"""ArchWiz Observatory — Streamlit control surface."""
import json
import os
from pathlib import Path

import requests
import streamlit as st

HOME = Path.home()
LED_DIR = HOME / ".deepcli/logs/provenance"
URL_FILE = HOME / ".deepcli/cs-hindsight-url.txt"
CS_FILE = HOME / ".deepcli/cs-hindsight-name.txt"

st.set_page_config(page_title="ArchWiz Cockpit", layout="wide")
st.title("ArchWiz Cockpit")
st.caption("Local FTS5 · Hindsight · Codespaces · Observatory")

def _ledger(name: str) -> int:
    p = LED_DIR / f"{name}.json"
    if not p.exists():
        return 0
    try:
        return len(json.loads(p.read_text()))
    except Exception:
        return -1

def _url() -> str:
    if URL_FILE.exists():
        return URL_FILE.read_text().strip()
    return os.environ.get("HINDSIGHT_BASE_URL", "")

def _cs() -> str:
    if CS_FILE.exists():
        return CS_FILE.read_text().strip()
    return "(none)"

c1, c2, c3, c4 = st.columns(4)
c1.metric("session ledger", _ledger("harvest-ledger"))
c2.metric("multi ledger", _ledger("multi-ledger"))
c3.metric("exports ledger", _ledger("exports-ledger"))
c4.metric("FTS5 items", "17,868")

st.subheader("Hindsight")
_hs_url = _url()
st.code(_hs_url or "(unset)", language="text")
if st.button("Probe /health"):
    if not _hs_url:
        st.error("No HINDSIGHT_BASE_URL set")
    else:
        try:
            r = requests.get(f"{_hs_url}/health", timeout=10)
            st.write(f"http={r.status_code}")
            try:
                st.json(r.json())
            except Exception:
                st.text(r.text[:600])
        except Exception as e:
            st.error(f"{type(e).__name__}: {e}")

st.subheader("Codespace")
st.code(_cs(), language="text")
