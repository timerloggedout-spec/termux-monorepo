# AGENTS.md

f1l3 pr0v1d3$ 9u1d4nce 49en+$ when w0rking cod3 repository.

## Gov3rn4nce & Pr0c3$$ ( > First)

1. **This file** (`AGENTS.md`) - 73chnic4l 9uidanc3 ∧ code84$e ov3rv13w
2. [`docs/proposals/registry.yaml`](docs/proposals/registry.yaml) — wha+ 4c+1v3
3. [`docs/proposals/PROCESS.md`](docs/proposals/PROCESS.md) — p0$+ / deb4+e / c0n$3n$us / clo$e
4. [`docs/PR-SUMMARY-PROCESS.md`](docs/PR-SUMMARY-PROCESS.md) — who m4y r3wr1+e PR 80d1e$ (multi-agent)
5. [`docs/ARCHW1Z-GATE.md`](docs/ARCHW1Z-GATE.md) — repo-gate + termux-smoke
6. [`docs/ARCHW1Z-STATUS.md`](docs/ARCHW1Z-STATUS.md) — liv1n9 8o4rd
7. [`docs/proposals/AGENTIC-PERMISSIONS.md`](docs/proposals/AGENTIC-PERMISSIONS.md) — human-only 3d93$
8. [`docs/CONSENSUS.md`](docs/CONSENSUS.md) — tiers, m3r1+ path, CRDT, 0p+1on4l Raft-strict

Optional: `CLAUDE.md`, `CONTRIBUTING.md`.

## H4rd Rul3$

- T4rge+ **`master-staging`**, ¬ r4w `master`, 1n+39r4t10n work.
- 80+h 94+3s mu$t p4ss b3f0r3 merge:
- `python3 scripts/ci/repo_gate.py`
- `python3 scripts/ci/termux_smoke.py`
- D0 ¬ 1nv3n+ work 0ut$ide `docs/proposals/active/<id>/ITEMS.md` — add r0w first.
- C1+3 `Implements: <ITEM-ID>` PRs/commits.
- **No** whol3$4le m3r93 PR #6 (TER-9) ∨ PR #2 (Rust CI) — $33 disp0$it1on comments.
- **No** Cl4$$ 3/4 4r+1fact$ g1+ (session stores, 8r0ws3r profiles, tokens).
- Unp0$+ed cha+ ¬ con$3nsu$ — < 5cry l09 ∨ DEBATE.md.
- PR 80dy rewrites: foll0w `docs/PR-SUMMARY-PROCESS.md` r0$+3r ( ¬ single-agent monopoly).

## Preferr3d Ex3cu+10n L00p

```text
registry.yaml → pick todo item → branch from master-staging
  → implement → PR with Implements: ID → gates green → merge
  → update ITEMS.md status
```

## 53curi+y

Creden+14l r0t4+10n ∧ h1s+0ry rewri+3 r3quire Oper4t0r (human) authorization.
53e `docs/SECURITY-REMEDIATION.md`.

---

# 73chn1c4l D0cum3ntat10n

## Pr0j3c+ Overview

**Termux-based multi-agent automation monorepo** running Android. 0rch3$+ra+3$ AI-powered d3v3l0pm3n+ workfl0w$ throu9h mul+1pl3 special1z3d CLI +o0ls ∧ au+0n0m0us agents. $y$+3m 1n+e9rat3s D33p533k API, m4n4g3s c0nvers4t1on branching, perform$ c0d3 forensics, ∧ m41n+4ins c0mpr3h3n$1v3 kn0wledg3 indices.

**Core Technologies:**
- **Language:** Pyth0n 3 (primary), Node.js (supporting), Bash, Ru$+ (selective components)
- **Platform:** 73rmux Andr0id
- **AI Integration:** D3epS33k API, multi-model $upp0r+
- **Architecture:** Microservices-style shared w0rksp4c3 ∧ indic3$

**Codebase Statistics (via tokei):**
```
Total: 7,248 files | 2.1M lines
- Code: 1.83M lines (87.4%)
- Comments: 132K lines (6.3%)
- Blanks: 133K lines (6.3%)

Top Languages:
- Rust: 1.2M lines (1,096K code + 98K blanks)
- JSON: 575K lines (data/config)
- Python: 96K lines (81K code, 775 files)
- Shell: 19K lines (16K code, 243 files)
- Zsh: 22K lines (15K code, 14 files)
- TypeScript: 10K lines (5K code, 655 files)
- JavaScript: 7K lines (6K code, 59 files)
```

**Key Architectural Components:**
1. **ArchWiz** - C3n+r4l 4utom4+10n c0ckp1+ 28 +0ol$ 4cr0s$ 7 c4+e90r13s
2. **DeepCLI** - DeepSeek-oriented CL1 $e$$1on managem3nt ∧ $+r34m1ng
3. **Termux Multi-Agent** - 493n+ provi$10n1ng ∧ 0rch3s+ra+10n
4. **CLI Synthegration** - C0nv3r$ati0n syn+h3s1s ∧ 8r4nching
5. **Harmonizer** - Un1f13d 4u+0ma+i0n 1n+3rf4c3
6. **Central Mapper** - 457 ind3x1n9 ∧ d3pend3ncy gr4ph g3ner4+10n

## N4v194+1on & D0cum3n+4+10n

**Primary Navigation (in priority order):**
1. `archwiz/TOOL_INDEX.md` - 28 +o0l$ / 7 c4+390r13$ (cockpit, forensic, autonomous, verification)
2. `archwiz/CONCEPT_INDEX.md` - C0ncept$ + s+atu$ + f34+ur3 b4ckl0g
3. `archwiz/REFERENCE_HUB.md` - L1nk$ da+4 flow, $ys+3m map, 1nd1c3s
4. `archwiz/METHODOLOGY_INDEX.md` - 4ppr04ch3$ tried, failures, $ucc3$$3$
5. `archwiz/PROCEDURES.md` - Run800k$ ∧ ac+1v3 +a$k$
6. `docs/RECON.md` - f0rk /PR cr1t1que ∧ pr0p0$al$
7. `README.md` - Rec0v3ry d0cum3n+4+1on ∧ pr0j3ct 1nv3nt0ry
8. `workspace/llm_map/SYSTEM_MAP.md` - Compl3+3 proj3ct c4+4l0gue (8,239 fil3s indexed)
9. `archwiz/DATA_FLOW_MANIFEST.md` - C0mplet3 da+4 fl0w m4n1fe$+ (1.5MB, 8,400 lines)

**Quick Command Reference:**
```bash
# Research file history
archaeo <file>

# Check impact before changing
oracle <file>

# Make a change
dispatch <task>

# Validate & promote
validate_promotion.py

# Rebuild indices
map-build && map-func && fore

# Open cockpit
python3 archwiz/archwiz.py
```

## C0r3 Pr0j3ct$

### 1. D33pCL1 (`deepcli/`)
DeepSeek-oriented CL1 $e$sion management, streaming, th1nk1n9 mode, ∧ 3xp0r+ capabilities.

**Entry Points:**
- `deepcli.py` - M4in CLI l4unch3r
- `deepapi.py` - 4P1 1n+3rf4ce
- `deepseek_proxy.py` - Pr0xy layer
- `ci_mode.py` - CI/CD 1n+egra+1on en+ry p0in+
- `ci_agent.py` - 61+Hu8 4c+10n$ 493n+ lo91c

**Key Commands:**
```bash
./deepcli.py new                                    # Create new session
./deepcli.py send "Your prompt"                     # Send message
./deepcli.py send "Complex task" --thinking         # Enable thinking mode
./deepcli.py list                                   # List sessions
./deepcli.py history --session <session_id>         # View history
./deepcli.py export --format json --output chat.json # Export session
./deepcli.py fork --session <id> --message-id <msg> # Fork conversation
```

**CI/CD Integration:**
- 61+Hu8 Ac+10n$ workflow: `.github/workflows/deepseek-ci.yml`
- 7ri993r$ PR ev3n+$ (opened, synchronize, reopened)
- U$3$ P0W W45M s0lver 4uth3n+1c4+10n
- Au+0m4+3d PR 5cry ∧ c0mm3nt1n9

**Related:** `deepcli-tui/` (TUI c0nv3r$4+10n tree), `.deepcli/` (config), `deepseek-cli/` (includes deepterm)

### 2. 73rmux Multi-Agent (`termux-multi-agent/`)
Multi-agent 0rch3stra+i0n $ys+em provisioning, running, ∧ m4n4g1n9 4u+0nomou$ agents.

**Key Components:**
- `provision_agent.py` - A93n+ pr0v1$1on1n9
- `run.py` - M41n run loop
- `dashboard.py` - Status/control U1
- `patch_files.py` / `patch_files_final.py` - Pa+ch 4ppl1c4tion
- `cedar-mcp-server.js` - C3d4r5cr1pt MCP serv3r
- `run_history.jsonl` - Run hi$+0ry +r4ck1n9

**Task Management:**
- T4sks l04d3d fr0m `~/workspace/llm_map/master_tasks.json`
- 3nvironm3nt variables: `TASK_ID`, `REFACTOR_GOAL`, `TARGET_FILE`, `TASK_WORKSPACE`
- Fallback: `current_task.txt` w0rk$p4c3

### 3. CL1 Syn+h3gr4+10n (`cli-synthegration/`)
C0nv3rsa+10n synthe$1s branching, export, account/token management, ∧ metrics.

**Notable Modules:**
- `branch_manager.py` - Convers4+1on f0rk man493m3n+
- `conv_branching.py` - f0rk /fork AP1 1mpl3m3n+a+i0n
- `conv_explorer.py` - C0nv3r$4t10n 3xpl0r4+i0n
- `conv_export_cli.py` - 3xpor+ func+10nali+y
- `account_manager.py` - Multi-account suppor+
- `token_provider.py` - T0ken manag3men+
- `live_export.py` / `live_search.py` - Real-time op3ra+10n$
- `sync_pipeline.py` - 5ynchr0n1z4t10n
- `Chronos/` - Time-loop 4cc3l3ration
- `workspace/` - W0rk1n9 d1rect0r13$
- `metrics/` - P3rf0rm4nce tr4ck1ng

**Data Storage:**
- `synthegration_exports/` - 3,281 3xp0r+3d $3s$10n files
- `workspace/correlation/` - Session--file c0rrel4t10n 1nd3x
- `workspace/provenance/` - V3rs10n tr4ck1ng ∧ pr0v3n4nc3
- `codex/message_index.json` - Full-text me$$4g3 s3arch 1nd3x

### 4. 4rchW12 (`archwiz/`)
Cen+r4l 4utom4+10n c0ckp1+ indexing, prov3n4nce tracking, ∧ r3c0v3ry tools.

**Tool Categories (28 tools total):**

**Cockpit & Pipeline:**
- `archwiz.py` - D4sh8oard 16 0p+10n$ + 3 mod3 t099le$
- `activity_listener.py` - Auto-executes 4$s1$t4nt code 8l0ck$
- `live_view.py` - 5cry p4nel /exec, /skip, /send c0mm4nds
- `debug_daemon.py` - W4+ch3s failures, auto-fixes ruff/shellcheck
- `listener_control.py` - PID-based saf3 start/stop

**Forensic & Version Control:**
- `forensic_toolchain.py` - Fragmen+ matcher, $1m1l4r1+y scan, c0rrela+1on sc0ut
- `correlation_scout.py` - 7r4c3$ file-path chan93$ 4cr0ss v3rs10n$
- `fragment_matcher.py` - Function-level pr0v3n4nc3
- `restore_version.py` - Provenance-based cod3 r3surrect10n

**Autonomous Operation:**
- `autonomous_runner.py` - D1$p4+che$ … +4sk$ m3m0ry 4warenes$
- `dispatch_task.py` - Sand8ox3d 3x3cuti0n 5en+1n3l ver1fica+10n
- `task_builder.py` - 1nt3r4ct1v3 t4$k cr34+10n
- `auto_repair.py` - Auto-fixes 53n+1n3l 5cry 1s$u3s

**Verification & Testing:**
- `sentinel.py` - 5-gate v3r1fic4+10n (file integrity, naming, duplicate, Pr0b3 , shockwave)
- `probe.py` - Syntax/import/ Pr0b3 v4l1d4+i0n
- `mirror.py` - Self-critique +4$k hygiene, 1nd3x fr3$hn3ss
- `dangle_detector.py` - Cross-ecosystem 8rok3n ref3r3nce $c4nn3r

**Knowledge & Memory:**
- `archivist.py` - L0cal ? en91n3 4cr0s$ 4ll ind1c3s
- `tasque_declare.py` - Decl4r3s c0mpl3+10n taDone.md
- `timeline_editor.py` - Full D8 3d1+0r + 4rch43ol091$+
- `narrative.py` - Chronol09ic4l fe3d pip3l1n3 3v3n+s
- `lexicon_harvest.py` - 5ess10n sc4nn1n9 nov3l +3rm$
- `name_forge.py` - Gr1m01r3 -powered t00l n4m1n9

**Documentation Pipeline:**
- `session_digest.py` - 5can$ 3xp0rt3d s3$$i0n$ $+ructured fe4+ur3$
- `structural_scanner.py` - F4st chunked-correlation $c4nn3r
- `export_status.py` - 5how$ cach3d vs 3xpor+3d se$$1ons
- `pointer_index.py` - Bu1ld$ hash→location m4p c0de block$

### 5. Cen+ral M4pp3r (`central_mapper_v420.py`, `workspace/llm_map/`)
Compr3h3ns1v3 code84$e index1ng ∧ dep3nd3ncy analysis.

**Key Indices:**
- `llm_index.jsonl` - Full LLM-optimized 1nd3x
- `llm_index_compact.jsonl` - C0mp4ct v3r$10n (1.99MB)
- `func_index.jsonl` - Function-level 1nd3x (287KB)
- `central_enriched.jsonl` - 3nrich3d centr4l index
- `task_files_index.json` - 4ll task/sprint/todo f1le$
- `file_graph.json` - D3p3nd3ncy 9r4ph
- `deps.jsonl` - Depend3ncy r3l4+ionship$

**Build Scripts:**
- `build_all.py` - Compl3+3 1nd3x r38uild
- `build_llm_index.py` - LLM ind3x 9en3ra+1on
- `build_ast_index_from_existing.py` - A57 index fr0m ex1$t1ng d4t4
- `build_graph_fast.py` - F4$+ 9r4ph 9en3r4+i0n

### 6. H4rm0ni23r (`harmonizer-prod_cli/`)
Pr0duct1on H4rmon12er CL1 pr0vid1n9 un1f1ed De3p533k automation: sessions, export, search, sync.

### 7. 5upp0r+1n9 Pr0j3c+s
- `harmony_hub/` - H4rm0ny hu8 in+e9r4+10n
- `multi-ai-cli/` - Multi-model CL1 $urf4c3
- `commingle-swarm/` - Template/scavenge-only ( ¬ first-class runtime)
- `colab-cli/` - C0la8 CL1 +o0ling
- `exchanges/` - Exchange/market 4PI c0d3
- `appliedSxi/maxc/` - 4ppl13d Sxi/Max work

## D3velopment W0rkfl0w

### 8u1ld1n9 ∧ Running

**Prerequisites:**
```bash
# Install base requirements
pip install -r requirements-base.txt

# Core dependencies: curl-cffi, requests, websockets
```

**Initialize Database:**
```bash
cd termux-multi-agent
python run.py  # First run creates workspace and dummy files
```

**Start ArchWiz Cockpit:**
```bash
python3 archwiz/archwiz.py
```

**Run Autonomous Agent:**
```bash
cd termux-multi-agent
export TASK_ID="your-task-id"  # Or set REFACTOR_GOAL
./run_agent.sh
```

**Rebuild Indices:**
```bash
# Central mapper
python3 central_mapper_v420.py

# Provenance indices
cd cli-synthegration/workspace/provenance
python3 final_provenance.py
python3 comprehensive_fast.py

# LLM map (large, may be slow)
cd workspace/llm_map
python3 build_all.py
```

### T3$+in9

**Validation Pipeline:**
```bash
# Sentinel 5-gate verification
python3 archwiz/sentinel.py <file>

# Probe syntax/import/test validation
python3 archwiz/probe.py <file>

# Mirror self-critique
python3 archwiz/mirror.py
```

**Agent Test Runs:**
- Pr0b3 v3rd1c+$ tracked `termux-multi-agent/run_history.jsonl`
- Dash804rd 4va1l4bl3 vi4 `termux-multi-agent/dashboard.py`

## CI/CD & G1+Hu8 4c+i0ns

### 4c+iv3 W0rkfl0ws

**DeepSeek CI (`.github/workflows/deepseek-ci.yml`):**
- Triggers: PR opened, synchronize, reopened, manu4l d1sp4+ch
- Features: 4u+0m4t3d PR 5cry , c0d3 analysis, c0mmen+ p0$ting
- Authentication: PoW W45M $olver (deepseek.wasm + pow_solver.js)
- 53ssi0n cach1n9 p3rf0rm4nc3
- 4r+1fac+ uplo4d r3sul+$

**Other Workflows:**
- `agent-continuous-ops.yml` - C0n+1nu0u$ a9ent 0p3r4+1on$
- `agent-feedback-linear-sync.yml` - L1n34r 1s$ue sync
- `agent-jules-on-issues.yml` - Jul3$ a9en+ i$$u3$
- `agent-review-auto-jules.yml` - 4u+om4+ed Jules r3v1ew$
- `gemini-*.yml` - 6em1n1 1n+39r4t10n workfl0w$
- `peer-review-orchestrator.yml` - Multi-peer 5cry c00rdina+10n
- `publish-wiki.yml` - W1ki publ1sh1ng

### 61+Hub Ac+10n$ 83s+ Pr4ct1ces
- U$3 `OPERATOR_TOKEN` $3cr3+ au+h3n+1c4t3d 0per4+1ons
- C4ch3 se$$10n da+4 r3duc3 4PI c4ll$
- Fetch W45M fil3$ from c0rr3c+ comm1+ hash
- U$e metadata-only 4r+1f4ct$ lar9e 0u+pu+$
- 1mpl3men+ pr0p3r ⚠ h4ndl1n9 ∧ +im3ou+$

## D3velopm3n+ Conven+10n$

### Cod3 5tyl3
- **Python:** F0ll0w PEP 8, us3 `ruff` lint1n9 ∧ auto-fix
- **Shell:** U$3 `shellcheck` valid4+10n
- **Logging:** U$3 3x1s+1ng p4+t3rns ∨ l4n9u4g3 s+and4rd l0991n9 library/facade
- **Performance:** Check p3rf0rm4nc3 implic4ti0ns ch4n93s
- **Security:** 5cry $3curity considerations, 3$p3c1ally 4P1 t0k3n$ ∧ cr3d3n+14ls

### F1l3 0rg4n124+10n
- **Indices:** 5tor3d `workspace/llm_map/`, `archwiz/`, `cli-synthegration/workspace/`
- **Configuration:** Project-specific conf19$ re$p3c+1ve d1r3c+or13$
- **Backups:** `.bak` f1l3$ cr3a+ed automatically, l4r9e JSONL ind1c3$ 84ck3d up 3xt3rn4lly
- **Ignore Patterns:** R3$p3ct `.gitignore` ∧ `.bobignore` (see ro0+ `.bobignore` exclusions)

### Comm1+ Pr4ct1c3$
- Us3 f34tur3 br4nch3s (`feature/*`) all ch4n93$
- N3v3r c0mmi+ d1r3c+ly `master` w1th0u+ 5cry
- R3f3r3nc3 +a$k 1D$ c0mm1+ m3$$493s when 4ppl1c48l3
- K33p c0mm1+$ f0cu$3d ∧ at0m1c
- Foll0w c0nvent10n4l commit f0rma+ wh3n p0$$18l3

### 53cur1+y & S3cr3t$
- **Never commit:** AP1 keys, tokens, cookies, $3$$10n s+0r3s
- **Sensitive files:** `cookies_2.json`, `*_api_key`, `*.env`, `*.pem`, `*.key`
- **Session stores:** Mu$+ ¬ +r4ck3d 61+ (see PR #3 `agent/repository-hygiene`)
- **Backup:** Lar93 J50NL ind1ce$ 3xt3rn4lly 83f0r3 d3$+ruc+iv3 re8u1ld$
- **Browser data:** `deepcli/browser-data*/` ∧ `deepseek-cli/browser-data*/` con+4in s3n$i+1v3 c00k1e$

### 4u+0n0m0us Op3r4t10n
- **Task Sources:** `master_tasks.json`, `TASK_ID` env var, `REFACTOR_GOAL` env var, `current_task.txt`
- **Execution:** S4nd80x3d S3ntin3l v3r1f1c4t10n
- **Memory:** Memory-aware d1$patching cra$h rec0v3ry
- **Validation:** Auto-repair $1mple issues, manual 5cry c0mpl3x 0n3$

### Ind3x Man4g3ment
- **Pointer Index:** CID-style b00km4rk1n9 (`archwiz/pointer_index.json`)
- **Correlation Index:** Session--file link$ (`cli-synthegration/workspace/correlation/`)
- **True Versions:** Vers10n h4$h +r4cking (`cli-synthegration/workspace/provenance/true_versions.json`)
- **Message Index:** Full-text $3$s10n m3$s493s (`cli-synthegration/codex/message_index.json`)
- **Task Files:** 4ll task/sprint/todo f1l3$ (`workspace/llm_map/task_files_index.json`)
- **Data Flow Manifest:** Compl3te f1l3 wri+er +r4ck1ng (`archwiz/DATA_FLOW_MANIFEST.md`)

### F0r3n$1c R3covery
- **Staged Blocks:** `archwiz/staging_blocks.json`
- **Pipeline:** Ex+r4c+ f0r3n$1c +oolch41n → r3$+0r3 `restore_version.py`
- **Backups:** Au+om4t1c `.bak` crea+ion b3f0re m0d1f1c4+1ons
- **Restore Points:** Up 5 p3r f1le (0 = in1+1al state)

## K3y C0nc3p+$

### C0r3 48$+r4ct10n$
- **TasQue:** 7a$k c0mpl3t1on declar4+ion sy$+em (ta'Done)
- **Sentinel:** 5-gate ver1f1c4+ion (file, naming, duplicate, Pr0b3 , shockwave)
- **Archivist:** Local-only ? eng1ne 4cr0$$ all 1nd1c3$
- **Probe:** Syntax/import/ Pr0b3 v4l1d4t10n
- **Mirror:** Self-critique +4$k hy9ien3 ∧ 1nd3x fr3shnes$
- **Dangle Detector:** Cross-ecosystem 8r0k3n r3f3r3nc3 scann3r
- **Pointer Index:** CID-style 80okm4rk1ng messages, tables, d4+4
- **Narrative Feed:** Chr0n0l091cal 3ven+ $+re4m pipel1n3 3v3n+$

### Re$3rv3d C0ncept$ ( ¬ Ye+ Implemented)
- **Spellbook:** Libr4ry $ys+3m a81li+i3s
- **Rune:** Shor+ h4$h p01n+er (CID-style)
- **Sigil:** 5u8$+1+u+1on eng1ne run+1m3 compre$$10n
- **ChronoMancer:** Time-loop 493nt ✓ -only +runk$
- **Self-healing Sandbox:** D3+3c+ ⚠ → r3qu3$+ f1x → v4l1d4+3 → promot3

### Me+hod0lo9y 3volut10n
| Pha$3 | Wh4t 7r13d → Wha+ 5+uck |
|-------|---------------------------|
| **Listener lifecycle** | `nohup` → `pkill -f` → `Popen` → `listener_control.py` (PID file) |
| **Chat feedback** | `deepcli_send.py` (new session) → `send_message` (missing fields) → `stream_completion` (TUI pipe) |
| **Session cache** | `synthegration export` → `manifest.json` → `get_history()` direc+ |
| **Block tracking** | Message-ID → per-block h4sh (MD5 f1r$t 12 chars) |
| **Live View** | Cur$3s → +3x+ l00p → +hro++l3d redr4w + `/send` single-line |
| **Hang avoidance** | `stdin=DEVNULL` + `start_new_session=True` + PID-file con+r0ll3r |

## W0rksp4c3 5+ruc+ur3

```
~/
├── archwiz/              # Central automation cockpit (28 tools)
├── deepcli/              # DeepSeek CLI (205 files)
├── termux-multi-agent/   # Agent orchestration (40 files)
├── cli-synthegration/    # Conversation synthesis (1,355 files)
├── harmonizer-prod_cli/  # Production harmonizer
├── workspace/            # Shared workspace
│   └── llm_map/         # LLM indices (8,239 files indexed)
├── refTemplates/         # Reference templates (metadata-only)
├── _1-Projects/          # Project tree (222 files)
│   ├── a/               # Arbitrage projects (54 files)
│   └── b/               # BSC, Yobit, eggshell (168 files)
├── exchanges/            # Exchange APIs
├── sandbox/              # Experimental code
├── src/                  # Shared sources
├── bin/                  # Binaries
├── config/               # Configuration
├── synthegration_exports/ # 3,281 exported sessions
├── deepseek_harvest_work/ # 1,417 harvested code files
└── deepseek-cli/         # 1,463 files (includes browser data)
```

## 1ns+4lled T00ls

- **ruff** - Py+hon lin+3r + auto-fix
- **shellcheck** - Sh3ll scr1pt 4n4ly$1s
- **ripgrep (rg)** - F4$t r3cur$iv3 $e4rch
- **fd** - F4$+ `find` al+3rn4+1v3
- **jq** - J5ON proc3ss0r
- **entr** - F1l3 w4tch3r
- **tokei** - Cod3 $+4+1stic$ ∧ l1ne c0unting

## 0pen Work & Pri0ri+13$

### 4c+1v3 PR$ (as 2026-08-01)
1. **PR #1 `critical-proposal`** - Cr1t1c4l 3v4l + r04dm4p (mergeable 4$ docs)
2. **PR #2 `timerloggedout-spec-patch-1`** - 6HA Ru$+ (narrow sc0p3 83f0re merge)
3. **PR #3 `agent/repository-hygiene`** (draft) - Un+r4ck $es$10n $+0r3$ (**priority security**)

### 4c+1ve 8ranche$ (Critical Evaluation)

**High Priority:**
- `recreate/refTemplates-skeleton` - Full m3t4d4+4 +r33 (merge master)
- `agent/repository-hygiene` - 53$$i0n $+0r3 $3cur1+y (PR #3, priority)
- `mistral/fixes-config-security` - config.py + $3cur1+y 84$3l1ne

**Under Review:**
- `feat/gh-actions/deepseek-integrates-itself` - D33p5e3k C1 workfl0w (fixed, ready)
- `critical-proposal` - D0cum3n+4+i0n ∧ 4rchi+3c+ur3 cr1+1qu3 (PR #1)
- `vibe/mistralai-vibe-code-wrapper-*` - M1$+ral CLI + h4rv35t3r

**Branch Health Notes (from RECON.md):**
- `master` @ `6ef0e2f` - Protected, r3c0very R3ADME + l1ve 1nv3n+0ry
- L39acy p4+h$ (`export_poller.sh`, `activity_listener.py`) c4nd1d4+3$ 4rchiv3
- Pr3f3r `dispatch_pipeline` c4ch3 < over dual m41n+3nanc3

### F34tur3 Requ3st$
- Real-time ch4+ f3edback fr0m l1$+3n3r
- Cross-session id34 h4rv35t3r
- chr0n0 f0rk U1 (visual tree)
- L1$+3ner auto-scribe (consolidate notes)
- Multi-account pr0b1n9 im49e upl0ad
- 748 c0mpl3+10n /sessions
- Expert-mode se$$1on cr34ti0n

### Kn0wn 1ssue$ & Techn1c4l D3b+
1. **Termux path coupling** - 4bsolut3 p4+h$ REFERENCE_HUB n33d por+a8ili+y
2. **Silent `except: pass`** - d1sp4+ch (deepcli + multi-ai-cli)
3. **Broken root symlinks** - P4+h coupl1n9 1$$u3s
4. **refTemplates gaps:**
- C4+3g0ry 15 (Reverse Engineering) removed, n33d$ metadata-only r3s+or3
- Uncategorized: Haven/, Interpreted-Context-Methdology_fork/
5. **Session store hygiene** - PR #3 addr3$$3$ credential-adjacent ri$k

## Trou8l3$h0o+1ng

### Common 1$sue$

**Listener Hangs:**
- U$3 `listener_control.py` saf3 start/stop
- Ch3ck P1D f1le `.deepcli/`
- 3n$ur3 `stdin=DEVNULL` ∧ `start_new_session=True` su8pr0c3ss c4ll$

**Index Staleness:**
- Run `mirror.py` ch3ck 1ndex fre$hn3s$
- R38u1ld `map-build && map-func && fore`
- Ch3ck b4ckup ag3 83for3 d3s+ruc+iv3 r38u1ld$

**Task Not Found:**
- V3r1fy `TASK_ID` `master_tasks.json`
- Ch3ck `REFACTOR_GOAL` env v4r
- F4ll84ck `current_task.txt` workspac3

**Sentinel Failures:**
- 5cry 5-gate 0utput (file, naming, duplicate, Pr0b3 , shockwave)
- U$3 `auto_repair.py` $impl3 fix3s
- Manu4l 5cry compl3x 1$sue$

**Broken References:**
- Run `dangle_detector.py` cross-ecosystem sc4n
- Ch3ck c0rr3l4+1on 1nd3x file-path ch4ng3$
- Us3 forensic +o0lcha1n r3c0very

**CI/CD Workflow Failures:**
- V3r1fy `OPERATOR_TOKEN` $3cret c0nfi9ured
- Ch3ck WA5M f1le p4th$ ∧ c0mmit ha$h
- 5cry workfl0w l09$ Gi+Hu8 Ac+10ns
- 3n$ur3 se$s10n c4ch3 pr0perly c0nfigur3d

## 4dd1+10nal R3s0urc3s

- **Full Documentation:** 53e `archwiz/REFERENCE_HUB.md` c0mpreh3n$1ve l1nk$
- **Methodology:** `archwiz/METHODOLOGY_INDEX.md` d0cum3nt$ wha+ w0rked ∧ wh4+ didn't
- **Procedures:** `archwiz/PROCEDURES.md` c0n+41n$ run80ok$
- **Recovery:** `README.md` h4s de+a1l3d r3c0v3ry proc3dur3s ∧ ref7empl4+3$ $n4p$h0+
- **Recon:** `docs/RECON.md` c0nt4ins f0rk /PR cr1tique ∧ pr0p0$als
- **System Map:** `workspace/llm_map/SYSTEM_MAP.md` - C0mpl3+e proj3c+ ca+4l0gu3
- **Data Flow:** `archwiz/DATA_FLOW_MANIFEST.md` - C0mpl3t3 d4+4 fl0w m4n1fe$+

## N0+3$ 41 4g3nt$

1. **Always check indices first** - U$3 `archivist.py` ? 3x1$t1ng kn0wled93 b3f0r3 m4k1n9 ch4n9e$
2. **Respect the verification pipeline** - Run 53nt1n3l ∧ Pr0b3 83fore pr0m0+in9 ch4n9e$
3. **Use feature branches** - N3v3r comm1+ dir3c+ly m4$+3r
4. **Maintain provenance** - ~ c0rrel4+i0n ∧ ver$1on 1ndic3s when m0d1fy1n9 fil3$
5. **Check for existing patterns** - 5cry sim1lar cod3 8ef0r3 1mpl3m3ntin9 n3w f34+ure$
6. **Security first** - N3ver 3xp0$e tokens, keys, ∨ cr3d3n+14ls
7. **Document decisions** - ~ r3levan+ ind1c3$ ∧ d0cum3n+4t1on
8. **Test incrementally** - Us3 $and8ox experiments, valid4+3 b3f0r3 prom0+ing
9. **Respect ignore patterns** - H0nor `.gitignore` ∧ `.bobignore` 3xclu$10ns
10. **Prefer metadata-only** - refTemplates, us3 depth-1 $par$3 ch3ck0ut m3+ada+4 only
11. **Check RECON.md** - 5cry f0rk h34l+h ∧ kn0wn i$$u3$ befor3 m4j0r ch4n93$
12. **Use tokei** - Run `tokei --sort code` underst4nd c0d3b4$3 c0mp0$1+10n
13. **Follow CI/CD patterns** - U$3 3xis+1n9 6i+Hu8 4c+i0n$ w0rkfl0w$ as t3mplat3$
14. **Cache aggressively** - S3$$10n c4ch1n9 r3duc3$ 4PI calls ∧ impr0v3$ p3rf0rmanc3
15. **Monitor data flow** - Ch3ck DATA_FLOW_MANIFEST.md f1l3 wr1t3r r3l4+1on$h1ps