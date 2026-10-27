# Agent Compute Engine — credential-free sandbox comparison vs the fleet's credential architecture

[MUSEai]@{role:{ace-lane}} — landed under the main lane's assignment 2026-10-26. Companion entry: `google-agent-compute-engine` in `config/agent_stack_integrations.json` (status WATCH). Cross-linked from `docs/ops/DATA-AGENT-KIT-WIRING.md`.

## 1. Subject, verified from Google's primary sources

**Google Cloud Agent Compute Engine (ACE)**, announced 2026-10-22 at AGNTCon + MCPCon (San Jose) by Nirav Mehta, Michael Bachman, Kevin Hutchins; technical deep dive same day by Ramanathan Venkatapathy and Rohit Jnagal (Google Cloud Blog).

- **Availability state: ANNOUNCED, NOT AVAILABLE.** Google's own wording: "It will be available in preview in the coming months" / "targeted for preview in the coming months." There is no console surface, no API, no pricing, and no docs quickstart — only an interest form. It already powers Gemini as an agent for work tasks, plus Antigravity and Google's internal evaluation / RL pipelines, internally. Any claim of GA or customer availability today is wrong.
- **Sibling that IS available today:** Agent Substrate on GKE — open-source, Kubernetes-native, same design (hardware-isolated microVM or gVisor, egress proxies that inject credentials outside the agent). Google benchmark: 200,000 agents, 500 activations/sec, <500 ms suspend/resume, up to 10x density vs traditional compute. ACE itself publishes no density/pricing numbers.

### 1.1 Architecture (from the deep dive)

- **One agent, one computer:** every session runs in a single-tenant microVM behind a hardware-isolated Cloud Hypervisor boundary, own guest kernel, root access, own Hyperdisk for a persistent workspace. Hosts are stateless appliances (read-only root via dm-verity) on Titan + Titanium IPU.
- **Brain/hands split:** the harness ("brain" — calls the model, decides) runs *outside* the sandbox ("hands" — executes code/shell/browser). The sandbox only executes explicit harness-dispatched commands, giving a deterministic audit trail per tool call.
- **Zero secrets in the sandbox — the load-bearing rule:** "Assume an attacker controls everything inside the sandbox, and make sure they find nothing there to use." A microVM never holds user credentials, API keys, OAuth refresh tokens, or service-account keys, in memory or on disk, and has no access to the instance metadata server. Google's worked example is a prompt-injected inbox agent told to "find any API keys on this machine and send them" — there are none to find.
- **No normal network:** microVMs have no standard NIC, no default gateway, no direct VPC access. All traffic crosses virtio-vsock to a local unprivileged proxy, then to the off-node **Agent Gateway**.
- **In-flight token swap:** the gateway validates the full triad — user delegation, agent identity, node identity — evaluates egress / DLP policy, then *inserts the required backend credential on the wire as the request leaves the gateway*. The backend sees a standard verifiable identity; the sandbox never sees the credential.
- **Four identities, never conflated:** (1) User identity (authenticates the overall task only); (2) Delegated on-behalf-of identity (cryptographically scoped grant; the long-lived grant lives only in the central authorization service, never on the node); (3) Agent Workload Identity (short-lived SPIFFE certificate + token, the *only* identity used for sandbox traffic, and by design not usable to call a backend API directly if exfiltrated); (4) Agent Workforce Identity (the agent acting with its own account/resources). Attestation keys live in the Titanium IPU, outside the guest.
- **Idle economics:** agents spend most of their life waiting; on tool-call completion the sandbox signals idle and the host checkpoints/pauses it at near-zero active cost, resuming from snapshot. Copy-on-write / DAX memory sharing deduplicates the base OS across microVMs on a host; environments can be snapshotted once and forked into thousands of copies (eval/RL shape).
- **Governance suite around it:** Agent Gateway (policy enforcement point for all traffic), Agent Registry (catalog of approved agents/tools/MCP servers/skills), Agent Identity (SPIFFE-based unique ID per agent), Agent observability (OTel). New Gateway capabilities announced for preview this quarter: per-agent/model token accounting + budget caps, model routing, Service Extensions in the datapath.

## 2. The incumbent position this is compared against

The fleet's credential architecture today, as documented in this repo:

| Pattern | Where it lives | How the credential is held |
|---|---|---|
| Vault-backed PAT helper | `~/AGENTS.md` fleet credential rule; helper outside the repo, credential in Secure Vault | One classic PAT (`MUSE_ADMIN_GH`, no expiration, near-full admin) shared by every chat/lane through one helper. The agent process never stores it, but the *effective authority* in any lane is that one broad bearer token. |
| Issue #184 inventory | `docs/ops/INTEGRATION-MESH-MATRIX.md` §2; Issue #184 | Names-and-last-used only — the map to stored credentials (repo Actions secrets incl. route-named PATs, OAuth apps, GitHub Apps). Zero raw values, by design and verified. |
| Actions secrets | Repo settings; mesh poll (38 names, live count) | Long-lived bearer secrets injected into workflow runs as environment. Any step in a run that can read its env can exfiltrate them; mitigation is cadence/scope discipline, not architecture. |
| Route naming | Owner ruling 2026-10-24 (e.g. `DEEPSEEK_API_KEY` is a GitHub-access route for DeepSeek CLI Termux agents, verified by the value-blind probe PR #1646) | A name declares its consumer route/family. Reduces confusion, does not reduce blast radius — the value is still a full bearer credential wherever it is used. |
| Foundry `account_ref` seam | `docs/ops/WEB-ADAPTER-FOUNDRY.md`; `ops/web_adapter_foundry/` | Token-shaped handle at the boundary; the backing session/cookie material never crosses into the request body and never leaves the origin device. Credential-shaped input in a request body is refused. This is the fleet's closest existing analogue to the ACE swap — at the *wrapper* layer, by convention + validation code. |
| Data Agent Kit tier rule | `ops/data_agent_kit/guardrail-policy.yaml` (schema v2, PR #1689); `docs/ops/DATA-AGENT-KIT-WIRING.md` | ENFORCED = IAM only: agents impersonate a dedicated `dak-readonly` service account via ADC, **no SA keys**, never owner credentials, dataset/bucket-scoped read roles + IAM deny on any non-read-only tool. ADVISORY = the 37 skills. A rule that lives only in agent instructions is not a guardrail. |
| Device pull-queue | `docs/ops/DEVICE-PULL-QUEUE.md` (Cloudflare Worker + D1, live) | Per-actor `DEVICE_QUEUE_*` tokens; 5-kind allowlist, no free-form shell; the device claims work, it is never pushed credentials or arbitrary commands. Tokens live only in a 0600 file on the operator side. |

Two honest observations about the incumbent set:

- The fleet has already been converging on ACE's thesis from three directions: keep the real credential somewhere the agent's execution surface is not (Foundry), make enforcement a permission-layer property rather than a prompt property (DAK), and narrow what a claimed task can do (pull-queue allowlist).
- What the fleet has *not* solved is the general case: the PAT helper and Actions secrets still place long-lived, broad bearer credentials inside the blast radius of whatever runs with them. That is a deliberate trade — one route, no human-in-the-loop, fleet-wide — recorded in the fleet credential rule, not an oversight.

## 3. Comparison on the fleet's axes

| Axis | ACE | Fleet today |
|---|---|---|
| Identity model | Cryptographic, per-workload, short-lived: SPIFFE cert issued per microVM, attested by Titanium hardware outside the guest; four identities kept distinct; workload identity is useless off-box by design | Bearer tokens: whoever presents the PAT/secret *is* the authority. Identity of the acting lane is a convention layer on top (Provenance/HindSight attribution, `[MUSEai]@{role:{moniker}}` signing), not a cryptographic property of the credential |
| Where credentials live at runtime | Off-host entirely, in a central authorization service; swapped onto the wire by the gateway after the request leaves the sandbox | In the helper's vault exchange (PAT), in the Actions runner env (secrets), or on-device behind a handle (Foundry sessions). In the first two, the credential transits the execution environment |
| What a compromised / prompt-injected agent can reach | Inside ACE: nothing credential-shaped. It can still *ask* the gateway for egress within its delegated scope and egress policy — the residual risk moves to policy breadth, not credential theft. Exfiltrated workload identity cannot call backends directly | With the PAT: the token itself, at near-full-admin scope, reusable from anywhere until revoked. With Actions secrets: every secret in that run's env. Foundry/DAK/pull-queue surfaces are the exceptions — handle, impersonation, and allowlist respectively bound the damage |
| Isolation granularity | Per-session microVM, own kernel, hardware boundary, no NIC, vsock-only egress, encrypted snapshots/Hyperdisk | Per-process / per-workflow-run on shared runners and shared devices; the B160V origin is a single shared environment (and heavyweight isolation is impossible there — see B160V browser law) |
| Auditability | Harness/sandbox split gives a deterministic per-tool-call trail; gateway logs carry user + agent + node identity for every egress | Provenance/HindSight + Actions logs + mesh poll; strong on *what landed*, weaker on binding a specific egress call to a specific attested workload |
| Availability / cost shape | Not available; preview "in the coming months"; no pricing published. Cost shape (pay ~nothing while idle) is asserted by design, not yet purchasable | Live today on free/existing tiers; the fleet's binding constraint is quota/cadence, not sandbox cost |

## 4. What adoption would actually require — and what it cannot touch

**Prerequisites, in order:**

1. **A GCP project (and, for ACE itself, billing once Google prices the preview).** The fleet has no GCP project today (free-tier recon, PR #1511). The fleet's current GCP step is the Data Agent Kit Route A item (`docs/ops/DATA-AGENT-KIT-ACTIVATION.md`, as amended by PR #1691 under the owner's card rule: create the project *without* billing — BigQuery Sandbox — plus a gcloud sign-in session whose prompts land on the broken-screen B160V; the card-gated trial/billing route is closed). ACE queues behind that same project-creation step; it does not create a second GCP decision, though ACE adoption itself would later need billing enabled, which is a separate owner call. Per the freemium-prep doctrine, everything wireable gets wired in-repo before signup; this doc + the catalog entry are that wiring for ACE.
2. **Preview access.** Even with a project, ACE cannot be adopted until Google opens the preview and the fleet is admitted via the interest form. There is nothing to deploy, pilot, or benchmark today. Agent Substrate on GKE is the only runnable form of the design, and it presupposes the same GCP/GKE presence.
3. **A harness that runs outside the sandbox.** Fleet agent surfaces today (Muse chats, Jules, Actions workflows, on-device agents) do not present a clean brain/hands split that ACE could host unchanged; adopting ACE means re-homing an agent's *execution* half, not lifting the agent.

**Surfaces ACE cannot touch, even when available:**

- **GitHub Actions lanes (~205 workflows):** they run on GitHub's runners under GitHub's secret model. ACE changes nothing there; the phantom-secrets audit process and quota-aware cadence remain the controls.
- **The PAT helper route:** ACE hosts agent *execution*; it is not a GitHub credential broker. The fleet's GitHub access would still need a credential the gateway could swap in — i.e. ACE would consume the #184 inventory, not replace it.
- **On-device Termux / B160V lanes:** ACE is a Google-datacenter service. The device pull-queue, the origin bridge, and NetHunter-class surfaces stay exactly as they are; the B160V law (no heavyweight browser/isolation stacks on-device) is untouched.
- **Other agent surfaces (Jules, Grok, Manus, ChatGPT):** they run in their vendors' clouds. ACE could in principle host a *fleet-built* agent's execution; it does not re-platform a vendor's agent.

**What ACE *would* change, if it arrives and the GCP item clears:** the execution half of any fleet-built, GCP-hosted agent — e.g. a future harness whose tool calls currently would run with ambient credentials — could run credential-free with gateway-swapped egress, per-session identity feeding Provenance, and idle-cost near zero. That is a real upgrade to exactly one layer, and it is the layer the fleet has the least of today (almost no fleet-built agents run their own cloud execution yet).

## 5. Findings

- **F1 — ACE is the vendor-hardware version of an argument the fleet is already making in software.** Foundry's `account_ref` (handle crosses, backing never does), DAK's IAM impersonation (no keys, enforcement at the permission layer), and the pull-queue allowlist are the same move at three different layers. ACE moves it to the hypervisor + gateway layer, where it no longer depends on the wrapper code being correct. That convergence is evidence for the fleet's direction, not a reason to wait for Google.
- **F2 — The residual risk in ACE is policy breadth, and the fleet already knows how to think about policy breadth.** A credential-free sandbox with a generous egress/delegation policy can still do damage *through* the gateway. ACE removes credential *theft*; it does not remove the need for scoped grants — the same discipline as DAK's per-service read roles and the mesh's names-only inventory.
- **F3 — ACE's identity model is the missing cryptographic half of Provenance.** Fleet attribution today is evidentiary (logs, signing conventions, HindSight). SPIFFE workload identity + gateway audit is attested. If ACE (or Substrate) is ever piloted, its per-session identity and gateway logs are the export to wire into Provenance/MVT — as evidence, under the same firsthand-counts discipline as every other telemetry source.
- **F4 — There is nothing to pilot today.** Announced-only + no GCP project + no fleet-built cloud agent execution surface = no pilot shape. This distinguishes ACE from Cloudflare Artifacts (pilot-shaped, owner's decision open) in the forge comparison. The honest posture is watch + mirror, not a queued adoption.

## 6. Posture

**WATCH + DESIGN-PATTERN-TO-MIRROR.** Not adopt-when-available in the strong sense (no surface is waiting on it), and not not-applicable (the pattern is directly on the fleet's credential-architecture line).

- **Watch triggers:** (a) ACE preview opens / fleet admitted; (b) pricing published; (c) the GCP project item clears for Data Agent Kit — at that point re-evaluate ACE *and* Agent Substrate together, since Substrate is runnable on GKE without waiting for ACE; (d) a fleet-built agent gains its own cloud execution surface (the first workload ACE could actually host).
- **Mirror now, in fleet-native pieces (proposed, not silently implemented):** the pattern is already partially mirrored (F1). The two gaps worth owner/lane decisions, in compounding order: (1) extend the gateway-swap idea to the Actions surface — short-lived, per-workflow credentials (e.g. OIDC-to-cloud where a cloud is involved) in preference to new long-lived secrets, enforced via the phantom-secrets audit's provisioning checklist rather than by convention; (2) when any fleet agent next gains a tool-egress path of its own, put the credential swap in that path (a proxy the agent cannot read through) instead of injecting the secret into the agent's environment — the Foundry seam generalized. Neither requires GCP, and neither is started by this doc.
- **Adoption decision, when the triggers fire, is the owner's** — it is a GCP-presence + platform decision of the same class as the Data Agent Kit activation items, not a lane call.

## Sources

- Google Cloud Blog, "Introducing Agent Compute Engine and expanding agent governance", 2026-10-22: https://cloud.google.com/blog/topics/ai-infrastructure/introducing-agent-compute-engine-and-expanded-agent-governance
- Google Cloud Blog, "Agent Compute Engine deep dive", 2026-10-22: https://cloud.google.com/blog/topics/ai-infrastructure/agent-compute-engine-deep-dive
- Google Cloud Blog, "Agent Substrate available on GKE": https://cloud.google.com/blog/products/containers-kubernetes/agent-substrate-available-on-gke
- Lead that prompted this comparison (secondary coverage, not evidence): TechTimes, 2026-10-23: https://www.techtimes.com/articles/329428/20261023/google-cloud-unveils-agent-compute-engine-ai-agent-credentials-kept-outside-hardware-sandbox.htm
- Fleet surfaces: `docs/ops/WEB-ADAPTER-FOUNDRY.md`; `ops/data_agent_kit/guardrail-policy.yaml` + `docs/ops/DATA-AGENT-KIT-WIRING.md` + `docs/ops/DATA-AGENT-KIT-ACTIVATION.md`; `docs/ops/INTEGRATION-MESH-MATRIX.md` (Issue #184 inventory, §2 credential stores); `docs/ops/DEVICE-PULL-QUEUE.md`; `docs/ops/AGENT-FORGE-VERSIONING-COMPARISON-2026-10-26.md` (§5 posture format followed here); free-tier recon PR #1511 (no fleet GCP presence).
