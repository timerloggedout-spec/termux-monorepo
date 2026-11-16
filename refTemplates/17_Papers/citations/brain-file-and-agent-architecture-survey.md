---
kind: research-citation-dossier
status: reference
source_scope: owner-supplied-perplexity-surveys
linked_slots:
  - refTemplates/01_Agent_Runtime/
  - refTemplates/02_Memory_Session/
  - refTemplates/03_Agent_Communication/
  - refTemplates/04_CedarScript/
  - refTemplates/05_Safety_Observability/
  - refTemplates/06_Task_Tracking/
  - refTemplates/07_Prompt_Context/
  - refTemplates/08_Swarm_References/
  - refTemplates/09_Auth_Networking/
  - refTemplates/10_Infrastructure/
  - refTemplates/11_Evaluation_Quality/
  - refTemplates/12_External_Agents/
  - refTemplates/13_Third_Party_Refs/
  - refTemplates/14_Plain_Files/
  - refTemplates/15_Research_Repo_Templates/
  - refTemplates/16_Org_Phased/
  - refTemplates/17_Papers/
---

# Brain filename and agent-architecture research dossier

**Purpose:** link both user-supplied Perplexity surveys into refTemplates/17_Papers and connect each reference to Brain subsystem design.  
**Evidence rule:** a URL or README claim is not proof of implementation behavior. This dossier distinguishes source-inspected patterns from user-supplied references awaiting independent verification. No scientific result is represented as reproduced.

## 1. Reading the filename survey

brain.py / Brain.py is a naming convention, not a shared software family. The supplied surveys identify neural-network computation, biological simulation, belief updating, log parsing, model-service gateways, application decisions, autonomous loops, memory facades, operational safeguards and deterministic intent routing.

Each source must be classified by responsibility, evidence relationship (paper artifact, author implementation, third-party implementation, application code, secondary analysis, README-only description or illustrative example), transfer pattern and limitation.

## 2. Primary architecture examples

| Ref | Source | Role / evidence relationship | Brain transfer | Evidence status |
|---|---|---|---|---|
| A1 | [Snake Game NN brain.py](https://github.com/Yadhu10nm/Snake_Game_using_NN/blob/main/neural_network/brain.py) | Neural-network component | Keep learned computation distinct from orchestration | User-supplied; pin/inspect |
| A2 | [fly-streetfighter](https://github.com/alextitonis/fly-streetfighter) | Biological neuron simulation; CPU/Numba and GPU/CuPy claims | Scientific simulation is a domain subsystem | User-supplied; pin/inspect |
| A3 | [nao_meets_gpt](https://github.com/fabianbosshard/nao_meets_gpt) | Speech/GPT coordination separated from robot body | Brain/body and service-adapter separation | User-supplied; pin/inspect |
| A4 | [Mnemosyne](https://github.com/MnemosyneOS/mnemosyne) | Memory engine facade | Memory is governed infrastructure, not the model | User-supplied; inspect current source |
| A5 | [HermitClaw analysis](https://agentarchitectures.com/framework/hermitclaw) | Secondary architecture analysis | Candidate plan/tool/reflection loop | Secondary source; inspect primary repo |
| A6 | [active-inference-viz](https://github.com/shimo4228/active-inference-viz) | Belief-updating research visualization | Belief state and uncertainty as explicit data | Reimplementation; validation caveats |
| A7 | [embodied-ai-robot](https://github.com/kanglongh/embodied-ai-robot) | LLM/VLM/TTS/ASR gateway; memory/tools/bridge separate | Keep provider, memory and tools as separate adapters | User-supplied; pin/inspect |
| A8 | [Banking document processing](https://github.com/quochungtran/LLM-Intelligent-Document-Processing-in-Banking) | Application-specific decision layer | Domain cognition is a plug-in | User-supplied; pin/inspect |
| A9 | [pentest-agents](https://github.com/H-mmer/pentest-agents) | Operational state and circuit breaker | Safeguards are first-class | User-supplied; pin/inspect |
| A10 | [SpendPilot catalog](https://glama.ai/mcp/servers/owain323/spendpilot) | Secondary description of deterministic intent routing | Deterministic baseline and optional LLM layer | Secondary catalog; primary source required |
| A11 | [BrainPy](https://github.com/brainpy/BrainPy) | Computational neuroscience framework, not filename equivalence | Keep scientific simulation lineage separate | User-supplied; inspect |
| A12 | [gaiusyu/Brain](https://github.com/gaiusyu/Brain) | Log parsing algorithm | Parsing is a domain capability, not an LLM brain | User-supplied; inspect paper/source |

## 3. Academic and research-linked code

| Ref | Source | Role / relationship | Transfer / limitation |
|---|---|---|---|
| B1 | [logpai/logparser Brain.py](https://github.com/logpai/logparser/blob/main/logparser/Brain/Brain.py) | Brain log parser implementation | Log perception adapter; inspect pinned code |
| B2 | [jaromiru/cwcf](https://github.com/jaromiru/cwcf) | Authors' code for AAAI costly-feature RL paper | Cost-aware information acquisition |
| B3 | [dchetelat/acer](https://github.com/dchetelat/acer) | Third-party ACER implementation | Do not misattribute as original author artifact |
| B4 | [active-inference-viz](https://github.com/shimo4228/active-inference-viz) | Research-derived reimplementation | Belief updates; author notes validation limitations |
| B5 | [Corporate Waters AI Agent](https://github.com/mshcheglov1-ux/corporate-waters-ai-agent) | Application agent architecture | Separate identity, memory, skills and tools |
| B6 | [Mnemosyne](https://github.com/MnemosyneOS/mnemosyne) | Persistent agent knowledge facade | Memory persistence outside reasoning core |
| B7 | [Nidus paper HTML](https://arxiv.org/html/2604.05080v1) | Externalized reasoning; illustrative src/brain.py | Governance/proof-obligation pattern; not proof of Nidus runtime |
| B8 | [Nidus paper PDF](https://arxiv.org/pdf/2604.05080.pdf) | Same paper, alternate locator | Duplicate of B7 |
| B9 | [logpai Brain package](https://github.com/logpai/logparser/tree/main/logparser/Brain) | Research implementation package | Structured log templates |
| B10 | [LLM-log-parsing inclusion](https://github.com/ait-aecid/LLM-log-parsing/tree/main/parsers/logparser/logparser/Brain) | Included parser tree | Vendored inclusion is not a new invention |
| B11 | [Embodied decisions as active inference](http://biorxiv.org/lookup/doi/10.1101/2024.05.28.596181) | Research paper | Belief/action coupling; paper review required |
| B12 | [priorelli/embodied-decisions](https://github.com/priorelli/embodied-decisions) | Research code associated with B11 | Keep research artifact distinct from reimplementation |
| B13 | [Nidus PDF locator](https://arxiv.org/pdf/2604.05080.pdf) | Duplicate of B8 | Same work; retain duplicate locator |
| B14 | [AI Agent Pull Requests on GitHub](https://arxiv.org/abs/2607.04697) | Agent PR research | Measure review and merge outcomes |
| B15 | [AI-Research Agents in the Wild](https://arxiv.org/abs/2609.11975) | Research-agent taxonomy | Evidence-backed research capability map |
| B16 | [LLM agent orchestration bugs](https://ieeexplore.ieee.org/document/11334467/) | Workflow-orchestration bug study | Failure taxonomy and regression design |
| B17 | [CodeR task graphs](https://arxiv.org/abs/2406.01304) | Multi-agent issue resolution | Typed dependency graph and decomposition |
| B18 | [HiRAS paper-to-code](https://arxiv.org/abs/2604.17745) | Paper-to-code research | Reproducibility pipeline |
| B19 | [Debugmate paper](https://link.springer.com/10.1007/s44248-025-00074-y) | On-call debugging agent | Incident-context and evidence-grounded diagnosis |
| B20 | [Embodied AI foundation-model review](https://www.mdpi.com/2218-6581/15/3/55) | Systematic review | Domain module boundaries |
| B21 | [Movement and embodied choices](https://doi.apa.org/doi/10.1037/xhp0001346) | Experimental psychology | Keep embodied cognition distinct from LLM orchestration |
| B22 | [Parallel Organizations for Agentic Societies](https://journal.agist.org/index.php/cpsi/article/view/45) | Agentic organization research | Multi-agent governance hypothesis |
| B23 | [LLM reasoning to autonomous agents survey](https://ieeexplore.ieee.org/document/11540994/) | Survey | Broad taxonomy only; verify individual claims |
| B24 | [R2E repository environments](https://www.semanticscholar.org/paper/2860bfaa9fa1d249c24aaf0981ad61bdbcd9c544) | Research index record | Repository-as-environment pattern; primary source needed |
| B25 | [ReproRepo](https://arxiv.org/abs/2606.18237) | Reproducibility audit research | Evidence and reproduction audits |
| B26 | [Aleena research collaboration agent](https://arxiv.org/abs/2607.08043) | Research software engineering collaboration | Requirements/intent alignment |
| B27 | [Embodied carbon tracking review](https://www.mdpi.com/2075-5309/15/24/4421) | Unrelated domain review | No direct Brain transfer established |
| B28 | [Hierarchical Frameworks for Embodied Medical AI](https://www.itm-conferences.org/10.1051/itmconf/20258001037) | Domain-specific research | Hierarchical domain modules; safety review needed |
| B29 | [Python in Neuroscience PDF](https://troomes.com/ext/pgreca/pgsocial/pdfs/upload/12478_python-in-neuroscience_9347138169.pdf) | Neuroscience tooling reference | Scientific simulation lineage |
| B30 | [OpenSourceBrain repositories](https://github.com/orgs/OpenSourceBrain/repositories) | Neuroscience ecosystem | Discovery source, not a specific implementation |

## 4. Additional GitHub/software references from the first survey

| Ref | Source | Supplied role | Transfer / limitation |
|---|---|---|---|
| C1 | [GEKKO brain.py](https://github.com/BYU-PRISM/GEKKO/blob/master/gekko/brain.py) | Exact filename example | Inspect before assigning a role |
| C2 | [AI-Trading-Brain](https://github.com/satyamdas03/AI-Trading-Brain) | Trading README | Domain-specific risk lane |
| C3 | [Robotics Assistant robot_brain.py](https://github.com/saim-ansari-tech/Robotics-Assistant/blob/main/src/robot_brain.py) | Robotics interaction | Hardware adapter |
| C4 | [NeuroMedix brain.py](https://github.com/prathamesh-chavan-22/NeuroMedix/blob/main/brain.py) | Medical app code | Domain-specific; safety review |
| C5 | [Jarvis-Python Brain.py](https://github.com/mrshadow-in/Jarvis-Python/blob/main/Brain.py) | Uppercase application brain | Naming example |
| C6 | [Jarvis core/brain.py](https://github.com/m4n3dw0lf/Jarvis/blob/master/core/brain.py) | Agent module | Application-specific |
| C7 | [andiamo README](https://github.com/josh-sea/andiamo) | README example | Role not established by supplied locator |
| C8 | [Udacity DRL gist](https://gist.github.com/nov05/1d49183a91456a63e13782e5f49436be?permalink_comment_id=4967959) | RL reference | Gist context, not canonical Brain |
| C9 | [SpeechBrain core.py](https://github.com/speechbrain/speechbrain/blob/develop/speechbrain/core.py) | Speech ML framework core | Project name is not filename equivalence |
| C10 | [SpeechBrain ASR training](https://github.com/speechbrain/speechbrain/blob/develop/templates/speech_recognition/ASR/train.py) | ASR training pipeline | Training, not general cognition |
| C11 | [speech_brain.py voice authentication](https://github.com/jyothikirant-sayukth/voice_auth_speechbrain/blob/main/speech_brain.py) | Voice application | Domain-specific pipeline |
| C12 | [GyaniAssistant](https://github.com/abhigyan24-ops/GyaniAssistant) | Voice assistant | README-level until source inspected |
| C13 | [Zyron Assistant](https://github.com/Surajkumar5050/zyron-assistant) | Local privacy-focused assistant | Potential local-first pattern; verify |
| C14 | [PhyPlan](https://github.com/phyplan/PhyPlan) | Learning to plan tasks | Planning research; verify paper/code |
| C15 | [project-neurohex](https://github.com/shakeabhishek/project-neurohex) | Neurorobotics hexapod | Embodied simulation domain |
| C16 | [Portable Brainvibing](https://github.com/Echo-Scion/Portable-Brainvibing) | Portable agent context | Pattern candidate, not validated cognition |
| C17 | [stockAI](https://github.com/itsanantk/stockAI) | Trading app | Domain-specific risk/authority lane |
| C18 | [ai_agent_chat](https://github.com/DuNorth595/ai_agent_chat) | Full-duplex voice assistant | Modality/interaction adapter |
| C19 | [awesome-neuroscience list](https://github.com/theowenyoung/testtrack/blob/main/content/analyticalmonk/awesome-neuroscience/README.md) | Curated ecosystem list | Discovery source, not primary evidence |
| C20 | [logparser-Brain x_Brain.py](https://github.com/lezhang-thu/logparser-Brain/blob/main/x_Brain.py) | Alternate parser fork | Check ancestry before counting as independent |
| C21 | [logparser-Brain repository](https://github.com/lezhang-thu/logparser-Brain) | Alternate parser repo | Fork/derivative; inspect divergence |
| C22 | [gaiusyu/Brain](https://github.com/gaiusyu/Brain) | Log parser research | Same lineage as A12/B1; don't double-count |

## 5. Additional research pointers

| Ref | Source | Relevance | Limitation |
|---|---|---|---|
| D1 | [Nidus HTML](https://arxiv.org/html/2604.05080v1) | Externalized reasoning | Same work as B7 |
| D2 | [Nidus PDF](https://arxiv.org/pdf/2604.05080.pdf) | Same research PDF | Duplicate locator |
| D3 | [Neurocognitive Swarm Architecture](https://www.techrxiv.org/doi/pdf/10.36227/techrxiv.177220787.72010996/v1?onload=true) | Swarm architecture hypothesis | Preprint; review before adoption |
| D4 | [CodeR](https://arxiv.org/abs/2406.01304) | Multi-agent task graphs | Duplicate of B17 |
| D5 | [AI-Research Agents in the Wild](https://arxiv.org/abs/2609.11975) | Research-agent taxonomy | Duplicate of B15 |

## 6. Source-to-subsystem mapping

| Brain subsystem | Source groups |
|---|---|
| Reasoning / model computation | A1, A2, A6–A8, B2–B4 |
| Perception / logs / event intake | A12, B1, B9, B10, C1, C20–C22 |
| Memory / knowledge | A4, A7, B6 |
| Planning / task graphs | A5, A10, B17, B18, C14 |
| Model/provider adapters | A3, A7, A8, B5, C5–C6 |
| Safety / resilience | A9, B16, B19 |
| Embodied / robotics domain | A2, A3, A6, A7, A11, B11–B12, B20–B21, B28–B29, C3, C15 |
| Multi-agent / research collaboration | A5, B14–B18, B22–B26, D3–D5 |
| Owner-facing / voice interfaces | A3, A7, C3, C9–C13, C18 |
| Domain-specific packages | A8, A9, C2, C4, C13, C17 |

## 7. Adoption and provenance rules

1. Pin repository commit SHA and exact file path before implementation transfer.
2. Distinguish authors' artifact from independent implementation, fork, vendored copy, demo and secondary description.
3. For papers, record DOI/arXiv ID, version, authors, date and linked code commit.
4. Extract only patterns supported by source inspection.
5. Record limitations, tests, license and supply-chain risk.
6. Every citation used in a refTemplates slot or category design must list linked_slots.
7. No smods pin until a custom fork, immutable reviewed commit, compatibility evidence and passing dual gates exist.
8. Research citations do not authorize runtime behavior.

## 8. Repository links

- [refTemplates index](../../00_Index/README.md)
- [Recovery](../../00_Index/RECOVERY.md)
- [Source map](../../00_Index/SOURCE-MAP.md)
- [Papers index](../README.md)
- [Continuous evaluation](../../../docs/ops/REFTEMPLATES-CONTINUOUS-EVAL.md)
- [Brain subsystem map](../../../docs/architecture/TERMUX-MONOREPO-BRAIN-SUBSYSTEM-MAP.md)
- [Brain RFP package](../../../docs/proposals/active/termux-agentic-hub/rfps/qdesk.brain-rs/PROPOSAL.md)


## 9. Additional supplied references retained for completeness

The following references were also present in the owner-supplied Perplexity citation lists. They are retained here so the refTemplates research record does not silently omit a supplied source. Their relevance or source behavior has not been independently established unless stated above.

| Source | Evidence class / note | Candidate linked subsystem |
|---|---|---|
| [Pentest Agent Suite news coverage](https://cybersecuritynews.com/pentest-agent-suite/amp/) | Secondary reporting; verify against primary repository | Security / resilience |
| [brain-py on PyPI](https://pypi.org/project/brain-py/) | Package index; name collision risk, inspect package metadata before use | Research discovery |
| [Nidus externalized reasoning paper](https://arxiv.org/pdf/2604.05080.pdf) | Duplicate PDF locator for B7/B8 | Requirements / evidence governance |
| [AI research agents in the wild (alternate listing)](https://arxiv.org/abs/2609.11975) | Duplicate of B15 | Research intelligence |
| [Neurocognitive Swarm Architecture](https://www.techrxiv.org/doi/pdf/10.36227/techrxiv.177220787.72010996/v1?onload=true) | TechRxiv preprint; review methodology and evidence | Multi-agent / swarm |
| [AI Agent PRs on GitHub](https://arxiv.org/abs/2607.04697) | Research paper; verify version and claims | Verification / observability |
| [An agentic prior-work positioning file](https://github.com/AP0LL0-op/project-arche/blob/main/prior_work_positioning.md) | Repository document; not peer-reviewed research | Research provenance |
| [Perceived trustworthiness of a GenAI-enabled ethical robot advisor](http://www.jbe-platform.com/content/journals/10.1075/is.25072.mom) | Journal article; domain relevance requires review | Trust / owner experience |
| [logpai Brain README](https://github.com/logpai/logparser/blob/main/logparser/Brain/README.md) | Implementation documentation for B1/B9 | Perception / log parsing |
| [LVLM survey index record](https://www.semanticscholar.org/paper/d4cbcc6899a8f0f8850a0b00cc92020790305d61) | Secondary scholarly index; primary paper needed | Perception / multimodal |
| [logpai Brain README at pinned commit](https://github.com/logpai/logparser/blob/a5f8a2b1/logparser/Brain/README.md) | Historical revision locator; pin full commit before implementation | Perception / log parsing |
| [Family-firm legacy article](https://spotlight.cefeo.se/articles/why-do-family-firms-sacrifice-success-to-save-their-legacy) | No direct Brain relevance established | No transfer assigned |
| [AI_Agent_OS README](https://github.com/Anaghdwivedi/AI_Agent_OS) | Application README; inspect source before transfer | Agent runtime |
| [Cell whitepaper](https://github.com/adam4056/Cell/blob/master/WHITEPAPER.md) | Project whitepaper; relevance requires review | Research discovery |
| [priorelli author profile](https://github.com/priorelli) | Author identity/context, not implementation evidence | Research provenance |
| [logpai Brain demo](https://github.com/logpai/logparser/blob/main/logparser/Brain/demo.py) | Demo for B1/B9; not a separate algorithm | Perception / log parsing |
| [Embodied AI with Foundation Models review (alternate citation)](https://www.mdpi.com/2218-6581/15/3/55) | Duplicate of B20 | Embodied/domain cognition |
| [CodeR task-graph paper (alternate citation)](https://arxiv.org/abs/2406.01304) | Duplicate of B17 | Planning / task graphs |
| [Parallel Organizations for Agentic Societies (alternate citation)](https://journal.agist.org/index.php/cpsi/article/view/45) | Duplicate of B22 | Multi-agent governance |
| [SpeechBrain project](https://github.com/speechbrain/speechbrain) | Organization/project locator; source role differs from filename convention | Modality adapters |
| [BrainPy examples](https://github.com/brainpy/examples) | Companion examples for BrainPy, not a brain.py implementation | Scientific simulation |

**Coverage note:** repeated citations are intentionally marked as duplicates rather than counted as independent inventions. Some source URLs are discovery pointers only; no adoption or runtime dependency follows from their inclusion.


## 10. Final source-coverage additions

These additional owner-supplied citations complete the cross-survey reference capture:

| Source | Evidence class / note | Candidate subsystem |
|---|---|---|
| [Evidence-Grounded Agentic Workflow for GitHub Repository Research and System Design](https://ieeexplore.ieee.org/document/11709309/) | Research paper; inspect method and artifact before adoption | Research intelligence / repository ontology |
| [brain-life/brainpy](https://github.com/brain-life/brainpy) | Brain-analysis Python tools; distinct from BrainPy neural-dynamics framework | Scientific data / domain cognition |
| [BrainPy examples](https://github.com/brainpy/examples) | Example repository for BrainPy; not evidence of a generic agent brain | Scientific simulation |
| [BrainPy organization](https://github.com/brainpy) | Organization index; discovery pointer only | Scientific simulation |
| [gaiusyu/Brain README](https://github.com/logpai/logparser/blob/master/logparser/Brain/README.md) | Duplicate/historical locator for log parser lineage | Log/event perception |

These additions are catalogued for traceability. They do not change the adoption rules: pin the source, inspect the exact implementation or paper, record license and limitations, and only then propose a runtime transfer.
