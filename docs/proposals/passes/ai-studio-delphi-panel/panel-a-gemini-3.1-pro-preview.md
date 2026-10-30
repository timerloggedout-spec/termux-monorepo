# Panel A — gemini-3.1-pro-preview

[MUSEai]@{role:{google-ai-studio}}

**Attribution:** model `gemini-3.1-pro-preview` (Google AI Studio
Playground UI, owner account, no API key selected) · run
2026-10-30 03:08–03:12 PT · 3,798 tokens shown · prompt record:
https://aistudio.google.com/prompts/14jM2ae6qcq46JakLpCs076mz5fpqwMIY
· ballot class MODEL_PROVIDER, provisional (zero-weight until
calibration, per pass synthesis).

**Brief:** identical Delphi brief to both panelists (see PASS.md).

## Verbatim response

1. Verdict and Initial Adoption

Verdict: The fleet should adopt AI Studio preview models. Integrating experimental models introduces high cognitive diversity to Delphi research panels, allowing the system to leverage bleeding-edge reasoning and modality features at no immediate cost.

Top 3 Models to Adopt First:

gemini-3.1-pro-preview: Serves as the primary heavy-reasoning panelist. Since it operates within free-tier limits, it provides Pro-level analytical depth critical for complex Delphi synthesis without requiring billing.

gemini-3.1-flash-live-preview: Acts as the real-time fact-checker. Its "live" designation suggests up-to-date grounding capabilities, essential for an evidence-bound system that requires current data.

gemini-robotics-er-2-preview: Provides an orthogonal, structured-logic perspective. Evaluative Robotics (ER) models are highly optimized for sequential, agentic reasoning, making it a unique "devil's advocate" panelist for logic verification.

2. Routing Paid Deep Research Previews

Given the current lack of a billing account and the 0/0 limits on Deep Research Pro and Computer Use previews, these models must be dynamically gated to prevent fleet pipeline failures.

Gated Research RFPs: The fleet should implement a Request for Proposal (RFP) workflow. When a Delphi round dictates deep-research consensus, the system creates a gated RFP ticket in the GitHub repo.

Free-Model Substitute: Until the fleet owner manually approves the round and configures a billing budget, requests are routed to a multi-agent loop utilizing gemini-3.1-pro-preview and standard web-search APIs to simulate deep research.

Owner Approval: Once the owner activates billing for high-stakes rounds, the fleet orchestrator unlocks the Paid Deep Research models (deep-research-preview-04-2026) for that specific GitHub issue/Delphi round, enforcing strict spend limits.

3. Top 3 Risks of Preview Models and Mitigations

Risk 1: Unannounced Model Deprecation. Preview models can be removed or altered without warning, breaking the Delphi pipeline.

Mitigation: Abstract API calls behind a fleet router with graceful degradation. If a preview model fails, automatically fall back to the stable gemini-3.8-flash baseline, flagging the swap in the GitHub ballot record.

Risk 2: Aggressive Rate Limiting. Free-tier limits (e.g., 5 RPM / 20 RPD as seen on 3.8 Flash) will easily bottleneck concurrent Delphi multi-panelist polling.

Mitigation: Implement aggressive asynchronous queuing. The fleet must pace API requests across the daily 20 RPD limit, caching intermediate steps and avoiding parallel bursts to the same model.

Risk 3: Unstable Output Structuring. Experimental models may drift from strict JSON schemas required for automated GitHub parsing.

Mitigation: Enforce strict schema constraints (response_mime_type: application/json) at the API level, and implement a validation layer that prompts the model to auto-correct syntax errors before committing the ballot to the repository.

4. Model Scoring (0-10)

gemini-3.1-pro-preview

Evidence Quality: 9/10 - Pro-tier reasoning provides highly nuanced, sophisticated evidence synthesis suitable for complex research.

Cost Efficiency: 10/10 - Utterly maximizes ROI by operating purely on the available free-tier quota.

Composability: 8/10 - Outputs standard text/JSON that maps cleanly into automated GitHub Markdown records, though complex responses require parsing.

gemini-3.1-flash-live-preview

Evidence Quality: 8/10 - Live grounding ensures factual timeliness, though Flash models typically trade exhaustive depth for speed.

Cost Efficiency: 10/10 - Provides real-time data access at zero financial cost under current fleet conditions.

Composability: 7/10 - Live data streams require aggressive snapshotting to maintain the static, verifiable nature of GitHub Delphi records.

gemini-robotics-er-2-preview

Evidence Quality: 7/10 - Exceptional for structural/logical validation, but may struggle with nuanced, generalized qualitative research.

Cost Efficiency: 10/10 - Leverages free-tier access for highly specialized agentic workflows.

Composability: 6/10 - Robotics-oriented token outputs may require custom middleware translation to fit standard Delphi JSON/Markdown templates.
