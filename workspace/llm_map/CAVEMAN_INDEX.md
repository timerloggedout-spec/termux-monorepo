# Caveman Ecosystem – LLM Index v6.0 (Final – profiled)

**3084 files** indexed. **108** dependency edges. **337** AST signatures. **446** time‑correlated. **9** bloat.

## Projects (auto‑discovered)
- **deepseek_harvest_work** (1417 files) – top: `harmony_hub/workspace/accounts.json` (used by 3)
- **cli-synthegration** (1348 files) – top: `cli-synthegration/workspace/compression_sandbox/synthegration_index.py` (used by 21)
- **deepcli** (205 files) – top: `deepcli/deepcli/core.py` (used by 35)
- **termux-multi-agent** (40 files) – top: `termux-multi-agent/cedar-mcp-server.js` (used by 0)
- **harmony_hub** (29 files) – top: `harmony_hub/src/token_provider_v2.py` (used by 3)
- **harmonizer-prod_cli** (19 files) – top: `harmonizer-prod_cli/workspace/reference/conv_versioner.py` (used by 6)
- **cedar_forge** (6 files) – top: `workspace/cedar_forge/PLAN.md` (used by 0)
- **deepcli-tui** (3 files) – top: `deepcli-tui/tui.py.bak` (used by 0)
- **compression_sandbox** (2 files) – top: `workspace/compression_sandbox/cedrlang/cedrlang.py` (used by 0)
- **synthegration_exports** (1 files) – top: `cli-synthegration/http_sniffer.js` (used by 2)
- **CAVEMAN_INDEX.md** (1 files) – top: `workspace/CAVEMAN_INDEX.md` (used by 0)
- **README.md** (1 files) – top: `workspace/README.md` (used by 0)
- **deepseek-cli** (1 files) – top: `workspace/deepseek-cli/taDone.md` (used by 0)
- **scripts** (1 files) – top: `workspace/scripts/enforce_workspace_hierarchy.sh` (used by 0)
- **taDone.md** (1 files) – top: `workspace/taDone.md` (used by 0)

## Most‑Used Files (non‑bloat)
- `deepcli/deepcli/core.py` (used by 35) – de _cache_pathsession_id: str, account: ; de _cache_loadsess
- `cli-synthegration/workspace/compression_sandbox/synthegration_index.py` (used by 21) – clas Pointer; clas TaxonomyNode; clas CodexIndex
- `cli-synthegration/workspace/reference/success_metrics.py` (used by 9) – clas RefactorELO; clas ComplexityEstimator
- `harmonizer-prod_cli/workspace/reference/conv_versioner.py` (used by 6) – clas MessageRef; clas ConversationDAG
- `cli-synthegration/branch_manager.py` (used by 3) – de list_branches):; de fork_branchsource_name: str, new_name
- `deepcli/workspace/reference/deepcli.py` (used by 3)
- `deepseek_harvest_work/harvest.py` (used by 3) – clas CodeBlock; de recursive_textsobj, parent_key="", co; de
- `harmonizer-prod_cli/workspace/reference/conv_explorer.py` (used by 3) – de cache_manifestexport_root: Path, mani; de load_cached_ind
- `harmony_hub/src/token_provider_v2.py` (used by 3) – de _load_jsonpath):; de _extract_from_cookiescookies_path):;
- `harmony_hub/workspace/accounts.json` (used by 3)
- `cli-synthegration/http_sniffer.js` (used by 2) – function logmsg) {
- `cli-synthegration/workspace/provenance/provenance_api.py` (used by 2) – de _load):; de get_originrelative_path: str):; de summary):
- `deepcli/deepcli/cli.py` (used by 2) – de cmd_importargs):; de cmd_configargs):; de cmd_newargs):
- `harmonizer-prod_cli/workspace/reference/token_provider.py` (used by 2) – de get_token):
- `harmonizer-prod_cli/src/main.rs` (used by 1)

## Quick Commands
```bash
python workspace/llm_map/graph_query.py --depends-on core
python3 -c "import json;d=json.load(open('workspace/llm_map/ast_snippets.json'));print(d.get('ebcee7e9',''))"
head -5 workspace/llm_map/llm_index_compact.jsonl
```
