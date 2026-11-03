# Competition Import — D1 Field (live recon, 2026-11-03)

Event: "Strands SDK: Workshop to Ship" (AWS Builder Center
hackathon 8311dcb5-1ece-3d62-a441-2e1c2ad90b86). Method per the
challenge-opportunity pipeline (docs/ops/
CHALLENGE-OPPORTUNITY-PIPELINE.md, Stage 1): Projects tab by
live browser, Load-more to exhaustion (10 → 20 → 30 → 40 → 50
→ 55, button gone) + roster count stable across 3 further
scrolls; every project opened individually for its full Body.
Read window: 2026-11-03 19:18–19:33 UTC. All 55 pages loaded
on first attempt. Bodies for the 54 non-priority rows are
carried in complete section order with key verbatim sentences
(page-view truncations marked); the priority row is verbatim
in full. Likes/comments as shown on the day (field-wide ≈ 0;
max 1 like, on 10 projects).

**Field size: 55 submitted projects** (as_of 2026-11-03,
exhausted read). Roster order preserved below.

## Cluster tally (Stage 2 — clusters seeded by the order)

- **education: 15** — CodeThozhan · StudySprint ⚠ (see flag) ·
  TamilEdu · ExamAccess · LearnBridge · KalviMate · LuminaLab ·
  Thiran · Learnova · ArivuBridge · SyllabusSync AI · AI
  Interview Coach · StudyBuddy · Ladder (+ the contested row)
- **climate-heat: 5** — HeatSafe Shift · HeatShield Madurai ·
  Madurai HeatShield · HeatShield Sentinel · Nafas
- **climate-agri: 11** — Mugil · MazhaiMitra · FasalRakshak ·
  KrishiRakshak · KrishiRakshak AI (weather) · Vaigai Guardian
  · TerraStrand AI · VazhaVanam · NeerAI · Proof of Loss ·
  Emerald (vet, agri-adjacent)
- **devops: 1** — CloudOps Swarm
- **other social-good: 23** — Thunai · hi (placeholder) ·
  Baadhi Saathi · ElderCare · CareNest · NALAM · NALAM AI ·
  Saklolo · NeighborShield · Sukoon · Ninaivu Thunai · Voice
  guard · JagaSungai · MonBondhu · AccessPath · Brownout ·
  NalamNest · CareBridge · MedClear · Marunthu-Thozhan ·
  MedGuide · EventCraft AI · ClimateGuard-AI

Live-endpoint tally: ~13 projects name a public endpoint
(FasalRakshak · SyllabusSync (Vercel) · Saklolo · Emerald ·
StudyBuddy · CloudOps Swarm · KrishiRakshak-weather · Sukoon
· NeerAI · AccessPath · Brownout · Proof of Loss ·
MazhaiMitra). Six projects run NO Bedrock model at all
(Thiran · KrishiRakshak · AI Interview Coach ·
KrishiRakshak-weather · Sukoon · Voice guard — Gemini/Ollama).

## ⚠ Contested row — StudySprint (roster #2)

The recon's read at our own project URL
(builder.aws.com/project/3LRJu2KZOWsFqd5oGHyt52lcR5P/
studysprint) returned another team's content (team
"GIREESHEE" · 30-day-plan body · Amplify/S3 endpoint · video
0q8U0UoBxxA · repo Gireeshee/StudySprint). That contradicts
the D1 seat's firsthand PASS on the same page the same morning
(our Body · webapp endpoint · WK9LMwpvHUk embed). The same
author owns Learnova (#21). Status: CONTESTED — a crossed read
between same-author cards is the working species; a firsthand
verification read of the URL is in flight and this section is
corrected on its return. Do not cite row #2's content for any
project until then. (Our own entry's state of record is
unchanged: the published submission, D1-verified 2026-11-03.)

## TAK tracks (Stage 3 — material rivals)

**SyllabusSync AI** — position: PDF syllabi → learning
roadmaps + study plans + YouTube discovery + progress
tracking, Strands + Bedrock Nova Lite (no model id printed).
time: published 2026-11-02; read 2026-11-03. state: VERIFIED
(deep-read incl. repo). Facts: real code — FastAPI backend
(agents: syllabus/planner/video/codegen) + React/TS frontend
+ Supabase; tests present (README: 49 backend + vitest +
Playwright e2e + CI). "Live" = syllabussync-ai.vercel.app
(Vercel + Supabase) — not an AWS deployment. Scheduling =
calendar study plans ONLY: repo code search FSRS = 0 files,
"spaced" = 0 files; no SR algorithm named anywhere.

**Ladder** — position: practice sets a teacher can trust —
chapter-verified items, levelled reading, retrieval
scheduling. time: published 2026-10-28; read 2026-11-03.
state: VERIFIED (body read incl. the gate's code). Facts:
deterministic verbatim-quote gate (16 drafts → 1 rejected →
15 items, 100% in-chapter); **SM-2 retrieval dates** — the
only SR algorithm named in the field; measured levelling
(grade 7.6 → 4.6); AgentCore entrypoint; pipeline runs with
no AWS account; 8 tests.

**CloudOps Swarm** — position: autonomous AWS incident
triage + self-healing, safety-verified remediation. time:
published 2026-11-01; read 2026-11-03. state: VERIFIED.
Facts: Claude 3.5 Sonnet & Haiku via Bedrock; benchmark 100%
(5/5), 28.4 s, $0.01095/incident; live demo on GitHub Pages.

**StudyBuddy** — position: 3-agent English tutor for
classrooms with no English teacher. time: read 2026-11-03.
state: VERIFIED. Facts: Amazon Nova Micro; AgentCore
deployable; live demo on CloudFront.

## Priority deep-read — SyllabusSync AI (verbatim)

Page: builder.aws.com/project/3LZ16DCnaf7M5m1iB6ChsZkRkFo/
syllabussync-ai-personalized-learning-roadmaps-with-aws-
strands-sdk · Team: C VISHNU VARDHAN (1) · Likes 0 · Comments
0 · Published Nov 2, 2026 · Tags: amazon-bedrock,
generative-ai, educational, strands · Description:
"SyllabusSync AI turns academic PDF syllabi into structured
learning roadmaps with personalized study plans, curated
YouTube resources, and progress tracking — powered by AWS
Strands SDK and Amazon Bedrock." · Live application:
https://syllabussync-ai.vercel.app/ · Repo:
https://github.com/cvardhan501/syllabussync-ai · Video:
https://youtu.be/UXMMRSDiU6o · Article:
builder.aws.com/content/3LZ1G4685MuXVUy1WHA11FDQkLt

Body (verbatim, complete): "SyllabusSync AI — Overview:
SyllabusSync AI is an AI-powered learning platform that
transforms academic PDF syllabi into structured learning
roadmaps, personalized study plans, and progress-tracking
dashboards. … Built using the AWS Strands SDK and Amazon
Bedrock Nova Lite … The Problem: understanding lengthy
syllabi · finding relevant videos · creating realistic study
schedules around assessment dates · tracking completed
topics. Key Features: 1. Intelligent Syllabus Analysis (PDF
upload, module/topic extraction, editable structure).
2. Educational Video Discovery (YouTube, multi-channel,
verified/probable/uncovered match classes). 3. Personalized
Study Planning (daily and weekly schedules; video lectures,
notes, practice; mark completed, monitor progress).
4. Learning Progress Dashboard (coverage, module-wise
progress, topics needing attention). AWS Technologies: AWS
Strands SDK (agent orchestration) · Amazon Bedrock – Nova
Lite (foundation model). Stack: React/TypeScript/Vite ·
Python/FastAPI · Supabase PostgreSQL + Auth · YouTube Data
API v3. Future Improvements: faster processing · improved
recommendations · responsive background processing ·
course-specific planning/analytics · progress insights."

Repo read: REAL CODE. backend/ (FastAPI: app/agents
{codegen, planner, syllabus, video}, app/api, app/services,
tests/, Dockerfile, requirements) · frontend/ (React+TS+Vite:
13 pages, components, vitest, Playwright e2e, tests/) ·
supabase/ (init migration) · README/ARCHITECTURE/SETUP/
DEPLOYMENT/CONTRIBUTING · CI workflow runs backend + frontend
tests. Surfaces: 2 apps (backend + frontend) on Supabase.
**Scheduling/SR: none — calendar plans only (see track).**

## Rows — full field (roster order; SyllabusSync = #23, above)

1. **CodeThozhan** — builder.aws.com/project/3LbnWYQX4ZRORUAT4lc7q3E5ZS8/codethozhan · Desc: "Tamil-first coding friend for Class 6–12 learners who don't have English-medium coaching." · Tags: none shown · Team: 1 (name not displayed) · 0/0 · Models: Bedrock Nova Lite, id us.amazon.nova-lite-v1:0 (BedrockModel → Agent → tools analyze_code/learning_plan/read_repo → CLI + FastAPI + Streamlit) · Live: NO (local Streamlit/CLI, "not yet deployed") · Repo: github.com/abdul100205/CodeThozhan · Video: none.
2. **StudySprint** ⚠ CONTESTED — see flag section. Not cited.
3. **Mugil** — Desc: "Tamil-first, multi-agent AI system that protects smallholder farmers from climate risk." · Tags: none · Team: Dhanush Raman B · 0/0 · Models: Bedrock Nova 2 Lite + Translate (agents: Weather Forecaster, Crop Doctor, Market Strategist, Safety Guardian) · Results claimed: 100%/95%/90% vs 0% baseline · Live: NO (local CLI/Streamlit, "prototype") · Repo: github.com/User-Dhanush-06/mugil.
4. **MazhaiMitra** — Desc: "Tamil-first AI climate intelligence for smallholder farmers (floods, drought, heat)." · Tags: strands-agents, amazon-bedrock, social-good · Team: 1 (name not displayed) · 0/0 · Models: Nova 2 Lite + Translate · Body near-identical in structure/results to Mugil (same 100/95/90 claims) · Live: Streamlit demo (weather-app-….streamlit.app) · Repo: github.com/Shreejaisiva/Weather-app.
5. **FasalRakshak** — Desc: "Voice-first crop doctor: photo diagnosis, Hindi explanations, offline-first." · Tags: none · Team: Prakhar Shukla · 0/0 · Models: Nova Lite (primary), Nova Pro (comparison), Transcribe, Polly · Live: YES — xodqri8mc2.execute-api.us-east-1.amazonaws.com (no login) · Repo: github.com/Prakhar2025/FasalRakshak · Video: youtu.be/QCazkh270jQ.
6. **Thunai** — Desc: "Tamil-first guide to government schemes families qualify for." · Tags: strands-agents, social-good, amazon-bedrock · Team: Mithul Pranav · 0/0 · Models: Amazon Bedrock (no id) · Live: NO (local CLI) · Repo: github.com/mithulpranav24012008/thunai-tamil-scheme-guide.
7. **hi** — Desc/body: "gg" · Tags: none · Team: abdul rahman · 0 likes / 1 comment ("yo") · Placeholder project; nothing else shown.
8. **TamilEdu** — Desc: "Multi-agent Tamil education assistant (teaches, quizzes, explains in Tamil)." · Tags: amazon-bedrock, generative-ai, educational, open-source · Team: Benjamin Franklin A · 0/0 · Models: modelId us.amazon.nova-lite-v1:0; Claude 3.5 Sonnet fallback · Live: NO (mocked local demo; Lambda+API GW+DynamoDB planned) · Repo: github.com/lolsico9t5/tamil-education-agent.
9. **Baadhi Saathi** — Desc: "Flood warning → personal offline-first plan for a family in Bihar, in Hindi, on a basic phone." · Tags: strands-agents, amazon-bedrock, social-good · Team: Yash Shrestha · 0/0 · Models: Nova Lite + Nova Pro · Live: NO (SMS/WhatsApp/IoT designed, not deployed; "currently a prototype") · Repo: github.com/yashrajshrestha/baadhi-saathi · Video present (ID not printed in body).
10. **ElderCare AI** — Desc: "Bilingual (Tamil+English) assistant for safe elder care: medication reminders, health tracking, emergency alerts." · Tags: strands-agents, social-good, amazon-bedrock · Team: D.Devadharshini · 0/0 · Models: us.amazon.nova-2-lite-v1:0 in Bedrock mode; local mode default · Live: NO public endpoint (local Streamlit) · Repo: github.com/ddevadharshini66-prog/ELDERCARE-AI.
11. **ExamAccess** — Desc: "Converts academic PDFs/slides/notes into accessible study material (large print, audio, simplified language, practice questions)." · Tags: strands-agents, amazon-bedrock, educational, python · Team: Ashwin Vijayakumar · 0/0 · Models: Nova 2 Lite · Live: NO (localhost:5173) · Repo/video: "Link to be added" (body).
12. **LearnBridge AI** — Desc: "Adaptive multi-agent learning for underserved students, in their language, at their pace." · Tags: strands-agents, amazon-bedrock-agents, educational, machine-learning, python · Team: Kunal Khapre · 0/0 · Models: "Bedrock-compatible" (no id) · Live: NO (Lambda+API GW = potential only) · Repo/demo links present, URLs not extracted.
13. **HeatSafe Shift** — Desc: "Protects Madurai outdoor workers from extreme heat: shift planning, hydration reminders, emergency alerts, Tamil+English." · Tags: strands-agents, social-good, amazon-bedrock · Team: R. Mugundan · 0/0 · Models: Bedrock (no id); "LLM never runs for emergency" (deterministic safety) · Results: 180 tests; placeholders from FACTS.md · Live: NO (localhost:8000) · Repo: github.com/mugundan2446/HeatSafe-Shift.
14. **KalviMate** — Desc: "Multilingual AI physics tutor (Tamil, Hindi, English), examples from daily life." · Tags: strands-agents, amazon-bedrock, educational, social-good, python · Team: Nandha Vinayak A P · 0/0 · Models: us.amazon.nova-2-lite-v1:0; "live AWS verification confirmed" for model calls · Results: 88 tests · Live: NO public endpoint (Streamlit/CLI) · Repo: github.com/NandhaVinayakAP/kalvimate · Video: "to be added".
15. **CareNest AI** — Desc: "Care coordination for elderly care: medication, appointments, records, caregiver communication." · Tags: strands-agents, agentic-ai, healthcare-life-sciences-industry · Team: ASHIKA KM · 0/0 · Models: us.amazon.nova-2-lite-v1:0 configured; mock model default; "Bedrock judge pending/blocked"; delivery mocked · Results: 34 signed cases, 100% emergency recall · Live: NO · Repo link present, URL not extracted.
16. **LuminaLab Swarm** — Desc: "Autonomous swarm turning science concepts into neuro-inclusive, offline STEM simulations for ADHD & dyslexic learners in zero-bandwidth classrooms." · Tags: educational, serverless, ai-agents, amazon-bedrock, strands-agents · Team: OmrT · 1 like · Models: Bedrock (no id) · Live: "Explore & Try It Live" + CloudFormation-deploy claim; no single public URL in body · Repo: github.com/Tt140/Lumina… (slug truncated in auto-view) · Video: youtu.be/WM_fD0tWd98.
17. **NALAM** — Desc: "Tamil-first AI health navigation agent for underserved families." · Tags: strands-agents, multi-agent-orchestrator, aws-api · Team: Mositha Madhu K · 0/0 · Models: Nova Lite v1 (us-east-1), temperature 0.2 · Results: 338 offline tests, 100% emergency recall · Live: NO (local FastAPI; live AI needs AWS credentials) · Repo: placeholder clone URL in body only.
18. **Thiran AI** — Desc: "Mock interview coach with Tamil feedback." · Tags: strands-agents, educational · Team: Sharmila M · 0/0 · Models: **Google Gemini via Strands GeminiModel — NOT Bedrock** · Live: no endpoint named · Repo: github.com/Sharmi-13/Thiran-AI · Video: youtu.be/hnO-pyWeifw.
19. **NALAM AI** — Desc: "Bilingual (Tamil+English) health assistant for underserved communities in Tamil Nadu." · Tags: strands, social-good, python, amazon-bedrock, react · Team: Paveesh M · 1 like / 1 comment · Models: us.amazon.nova-2-lite-v1:0 (Nova Lite v2); mock default, live with credentials · Repo: github.com/PAVEESH-M/NalamAI.
20. **Saklolo** — Desc: "Agents that sort typhoon rescue pleas so a person can decide faster (urgency, location, credibility)." · Tags: strands-agents, amazon-bedrock, serverless, multi-agent-orchestrator · Team: John Paul Curada · 1 like · Models: Nova Lite + Titan Text Embeddings V2 + Location Places · Results: 150-message eval, median 4 s, $4/10k messages · Live: YES — saklolo.jpcurada.dev · Repo: github.com/JpCurada/saklolo · Video: youtu.be/tDkLr1P2jss.
21. **Learnova** — Desc: "Bilingual AI tutor that finds exactly what each student hasn't understood." · Tags: strands-agents, amazon-bedrock, amazon-polly, social-good, educational · Team: Gireeshee Pendela · 0/0 · Models: Bedrock (no id) + Polly; Ollama 7B earlier; simulated-learner results · Live: no endpoint named · Repo links present, URLs not extracted.
22. **Emerald** — Desc: "A vet line that makes the call, shows its sources, and waits for the vet." · Tags: strands-agents, amazon-bedrock, amazon-bedrock-agentcore, generative-ai, agentic-ai · Team: Ashfaque · 0/0 · Models: Nova 2 Lite (drafts), Llama 3.3 (reviews), Nova Sonic (voice), qwen2.5:7b (offline) · Results: synthetic data only, no vet review · Live: YES — emerald-upm6wwty7q-uk.a.run.app · Repo: github.com/ashfaque-rifaye/emerald-vet-line · Video: youtu.be/8QLmln9VK4M.
23. **SyllabusSync AI** — priority row, verbatim above.
24. **KrishiRakshak** — Desc: "Climate resilience for smallholder farmers (weather, crop, market advice)." · Tags: AI, generative-ai, social-good, prototype · Team: shivkumar Udas · 1 like · Models: **Google Gemini — NOT Bedrock** · Live: no endpoint named · Repo: github.com/shivkumarudas/KrishiRakshak-AI.

25. **Vaigai Guardian AI** — Desc: "Tamil-first climate resilience platform for the Vaigai basin (flood, drought, heat)." · Tags: strands-agents, amazon-bedrock, multi-agent-orchestrator, agentic-ai, api · Team: Kishore · 0/0 · Models: amazon.nova-lite-v1:0 (ap-south-1) + Translate + Open-Meteo live data · Live: NO (Docker local, "prototype") · Repo links present, URLs not extracted.
26. **AI Interview Coach** — Desc: "Personalized interview preparation for students (mock interviews, feedback, practice)." · Tags: artificial-intelligence, educational, python, generative-ai — NO strands tag · Team: Nagunoori Roja · 0/0 · Models: **Google Gemini — NOT Bedrock** · Live: no endpoint named (Streamlit) · Links present, URLs not extracted.
27. **NizhalAI** — Desc: "Tamil-English AI assistant for community climate preparedness (flood, heat, storm)." · Tags: strands-agents, amazon-bedrock, social-impact · Team: M S Bhagyashree · 0/0 · Models: Nova 2 Lite · Results: 5 cases · Live: no endpoint named · Repo: github.com/msbhagyashree/NizhalAI · Video present on page (34.6 s noted; URL not printed).
28. **HeatShield Madurai** — Desc: "AI-powered heat safety for outdoor workers (shift, hydration, emergency; Tamil+English)." · Tags: strands-agents, amazon-bedrock · Team: Kirthana · 0/0 · Models: Bedrock (no id); "live evaluation pending (quota)" · Results: 86 tests, 18 offline scenarios · Live: NO endpoint named · Repo link present, URL not extracted.
29. **TerraStrand AI** — Desc: "Autonomous climate resilience swarm for smallholder farmers (weather, soil, crop, market swarms)." · Tags: strands-agents, amazon-bedrock, ai-agents, social-good · Team: Abhronil Jash · 0/0 · Models: Claude 3.5 Sonnet, Claude 3 Haiku, amazon.nova-pro · Live: Bedrock live + local simulation; no public app URL · Links present, URLs not extracted.
30. **StudyBuddy** ("No English Teacher? Three AI Agents Split the Job of One") — Desc: "Bilingual study companion (Tamil+English) for classrooms with no English teacher." · Tags: amazon-bedrock, ai-agents, educational, generative-ai, social-good · Team: 陆荣智 · 0/0 · Models: Amazon Nova Micro; AgentCore deployable · Live: YES — d202bb1056rf7k.cloudfront.net · Repo: github.com/Clay5141/studybuddy · Video: youtube.com/watch?v=AWSt58q9lmU.
31. **Madurai HeatShield** — Desc: "Community heat resilience agent for Madurai outdoor workers and vulnerable residents (Tamil+English)." — DISTINCT project from #28 · Tags: strands-agents, social-good, community, python · Team: Jaiwarsha · 0/0 · Models: Nova2Lite; offline by default · Results: 139 tests, synthetic data, cases unsigned · Live: NO endpoint named · Repo link present, URL not extracted.
32. **EventCraft AI** — Desc: "Intelligent event planning copilot (plans, budgets, schedules from one description)." · Tags: ai-agents, amazon-api-gateway, aws-community-day, aws-cloud-wan, aws-builders — NO strands tag · Team: aman kumar · 0/0 · Body: the description sentence only — no further sections shown · Models/live: none named · Links present, URLs not extracted.
33. **ClimateGuard-AI** — Desc: "Community climate-risk guidance (weather, flood, heat) with safety rules." · Tags: agentic-ai, agents, strands-agents, strands-decider-2b · Team: Selva Meenakshi K · 0/0 · Models: provider via env vars (no id); Open-Meteo live data · Results: evaluation placeholders; "heuristics not validated" · Live: no endpoint named · No repo/demo/video links shown.
34. **CloudOps Swarm** — TAK track above. Models: Claude 3.5 Sonnet & Haiku via Bedrock · Live: YES — farhanmallik05.github.io/cloudops-incident-swarm · Repo: github.com/farhanmallik05/cloudops-incident-swarm · Published Nov 1, 2026 · Team: Farhan Mallik.
35. **KrishiRakshak AI – Intelligent Weather Risk & Crop Advisory Agent** — DISTINCT from #24 · Desc: "Weather risk and crop advice in their language, for their crop and location." · Tags: agentic-ai, strands-agents, artificial-intelligence, hackathon, aws-sdk · Team: Aniket Todkar · 1 like · Models: **local Ollama Qwen 2.5 1.5B — NOT Bedrock** + Open-Meteo · Live: YES — cloudtake.in (EC2 + Nginx + HTTPS) · Repo: github.com/Aniket-9009/KrishiRakshak-AI.
36. **NeighborShield** — Desc: "Multi-agent flood and heat readiness assistant that reaches the most vulnerable first." · Tags: strands-agents, ai-agents, amazon-bedrock, social-good, ai · Team: Sandip Ghorai · 0/0 · Models: not named in body ("LLM explains, code decides") · Live: NO (demo scenario only) · Repo: github.com/SandipGhorai-max/NeighborShield · Video: Google Drive link as printed in body.
37. **Sukoon** — Desc: "Sustainable AI-powered mental healthcare infrastructure for Pakistan (Urdu+English)." · Tags: hackathon, amazon-bedrock, agentic-ai, amazon-bedrock-agents · Team: Syed Moiz · 0/0 · Models: **currently Gemini — body explicit that the Strands/Bedrock design is a plan, not the running code** · Architecture: EC2 t3.micro, $13/mo estimate · Live: YES — sukoon.tech · Repo: github.com/SYMOIZ/sukoon-ai-therapist.
38. **ArivuBridge** — Desc: "Tamil AI learning companion (teaching, practice, feedback)." · Tags: strands-agents, social-good, educational, amazon-bedrock · Team: Sherin Angeline · 0/0 · Models: Bedrock (no id) · Results: 37 cases, placeholders, 45 guidance items · Live: no endpoint named · Repo link present, URL not extracted.
39. **Ninaivu Thunai** — Desc: "AI-based memory and daily assistance for elderly people (Tamil+English)." · Tags: strands-agents, social-good · Team: Shrinidhi · 0/0 · Models: in.amazon.nova-2-lite-v1:0 (ap-south-2, blocked; local fallback) · Results: 30 cases · Live: NO endpoint named · Repo/video: "to be added".
40. **VazhaVanam** — Desc: "Tamil-first climate resilience agent for small farmers." · Tags: strands-agents, amazon-bedrock · Team: Rishitha S · 0/0 · Models: us.amazon.nova-2-lite-v1:0; no live weather API · Results: 31 cases · Live: NO endpoint named · Repo: github.com/rishirishitha047-wq/VazhaVanam · Video: file in repo (results/demo_narrated.mp4).
41. **Voice guard** — Desc (verbatim): fake-voice detection website, "works in real time" · Tags: google-gemini, hugging-face, github, amazon-s3-vectors, agents · Team: Prerna Mehra · 0/0 · Models: Google Gemini (tag) · Live: no endpoint named · Repo link present, URL not extracted.
42. **NeerAI** — Desc: "Water intelligence for smallholder farmers (irrigation, rainfall, groundwater)." · Tags: strands-agents, hackathon, amazon-bedrock-agents · Team: Thirumalaiboobathi B · 1 like · Models: Bedrock (no id) · Live: YES — "deployed on AWS Amplify" (URL not printed) · Repo link present · Video: YouTube link in body (URL not printed).
43. **JagaSungai** — Desc: "Verified flood briefs for cut-off communities — checked, sourced, safe to share, even offline." · Tags: strands, strands-agents, amazon-bedrock, amazon-bedrock-agentcore, sustainability · Team: SHERMAINE YAP SHI MIN · 0/0 · Models: Nova 2 Lite via global inference profile (ap-southeast-1) · Results: evals 77/77, 33/33, 32/32; 181/192 quiet cycles · Live: NO AgentCore deployment for the project itself; WhatsApp via console demo · Repo: github.com/ShermaineYap/Strands-SDK · Video: youtu.be/aWROx7sH9GU.
44. **MonBondhu** — Desc: "Bengali-first AI emotional support navigator." · Tags: strands-agents, amazon-bedrock, generative-ai, social-good · Team: Tanvir Hasanat · 1 like · Models: Claude Sonnet 4.6 via Bedrock (ap-south-1) · Results: 65 pytest tests · Live: NO (local FastAPI, not deployed) · Repo: github.com/tanvirh47/monbondhu.
45. **AccessPath** — Desc: "Benefits Letter Reader: plain-language explanations, deadlines, next steps, with Strands on AWS." · Tags: strands, amazon-bedrock, aws-lambda, serverless, amazon-cloudfront · Team: Keith Casko · 0/0 · Models: Amazon Nova Pro · Results: 98 backend tests · Live: YES — demo via CloudFront + S3 + Lambda ("fictional demo only, no auth, not a service") · Repo: github.com/kcasko/accesspath · Video: 2:22 YouTube (URL not printed).
46. **Brownout** — Desc: "An AI agent that makes a city website lighter as a disaster gets worse." · Tags: strands-agents, amazon-bedrock-agentcore, amazon-cloudfront, amazon-bedrock, ai-agents · Team: Kento Ikeda · 1 like · Models: Bedrock AgentCore Runtime (no model id) · Results: 18/18 with PublishGuard vs 13/18 vs 0/6; 0.5 s vs >180 s; simulated city · Live: YES — "Example City" demo · Repo URL not printed · Video: 2-min, URL not printed.
47. **NalamNest** — Desc: "Safe Tamil-English care-coordination assistant with safety gates." · Tags: strands-agents, social-good, mental-health-awareness, amazon-bedrock, python · Team: Mijisha R · 0/0 · Models: us.amazon.nova-2-lite-v1:0 · Results: 30 cases; gate PASSED 11/11; goal 0.967 vs 0.667; synthetic data, no field deployment · Live: NO · Repo: github.com/mijishar/NalamNest · Video: file in repo (results/demo.webm, 70.1 s).
48. **CareBridge** — Desc: "AI-powered post-discharge recovery companion (medication, follow-up, warning signs)." · Tags: none shown · Team: Raghad Afghani · 0/0 · Models: Bedrock foundation models (no id); AgentCore Runtime deployed; Textract, S3, CloudWatch; safety specialist deterministic · Live: AgentCore deployment claimed; no public app URL · Repo link present, URL not extracted.
49. **MedClear** — Desc: "Explains medicine labels in English, Sinhala and Tamil, with safety rules that don't depend on the model." · Tags: strands-agents, amazon-bedrock, responsible-ai, multi-language · Team: J.P.S.D.D. Ariyarathna · 0/0 · Models: Nova Lite (ap-southeast-2); Ollama alternative · Live: NO (prototype; "not medical advice, not tested on real patients") · Repo: github.com/SenalDilanka/medclear · Video: youtu.be/Nk7r_m4hHU0.
50. **HeatShield Sentinel** — Desc: "Multi-agent AI for outdoor worker heat safety." · Tags: artificial-intelligence · Team: Ankit Singha · 0/0 · Models: Claude 3 Haiku via Bedrock (configured; **live inference NOT verified, is_demo=True**) · Results: 22/22 backend tests, 9/9 benchmarks, 160.69 ms · Live: NO verified endpoint · Repo: github.com/ASingha165/HeatShield-Sentinel.
51. **Nafas** — Desc: "What working in a Riyadh clinic taught me about extreme heat, asthma, and AI agents." · Tags: ai-agents, amazon-bedrock, healthcare, strands-agents, strands · Team: Mohamed Omar Makhlouf · 0/0 · Models: amazon.nova-pro-v1:0 (reasoning), amazon.nova-lite-v1:0 (fast); Claude Sonnet failed in sandbox · Live: Lambda runtime → Bedrock (not AgentCore); no public app URL · Repo: github.com/Mhdomer/strands-social-good-agent · Video: youtu.be/ftLuHs6JTMU.
52. **Marunthu-Thozhan** — Desc: "Fail-closed AI prescription safety companion for South Tamil Nadu outpatients (Tamil+English)." · Tags: strands, sdk, amazon-bedrock, ai-agents, social-good · Team: Darshini B · 0/0 · Models: Nova 2 Lite + Transcribe (ta-IN) + Location + Guardrails · Results: 31 cases, 100% emergency handoff, 0 unsafe, goal 0.968 vs 0.523 · Live: no endpoint named · Links present, URLs not extracted.
53. **MedGuide** — Desc: "A medicine explainer that knows when to say 'ask a pharmacist'." · Tags: amazon-bedrock, strands, agents, agentic-ide, agent-hooks · Team: Gnaneshwar · 1 like · Models: Amazon Nova Pro on Bedrock; AgentCore entry included but NOT deployed · Results: 10/10 dangerous pairs, 4/4 scenarios; demo list small, not clinical · Live: NO · Links present, URLs not extracted.
54. **Proof of Loss** — Desc: "Helps farmers file crop insurance claims in 72 hours (evidence, forms, follow-up)." · Tags: strands-agents, amazon-bedrock, amazon-bedrock-agentcore, social-good, hackathon · Team: Anish Kumar · 1 like · Models: Amazon Nova (no id in body) + AgentCore Runtime + Transcribe · Results: 14 scripted claims, first run 12/14 · Live: YES — d39zeolevac0dg.cloudfront.net · Repo: github.com/Sarcastic-Soul/proof-of-loss · Video: youtu.be/DrBnMbF4dZo.
55. **Ladder** — TAK track above. Models: BedrockModel on Bedrock (no id) + AgentCore entrypoint (agentcore.py); demo runs locally with NO AWS account (pip install -e '.[dev]' · python -m ladder.demo · pytest -q, 8 tests, MIT) · Repo: github.com/abhinavshukla152005-beep/ladder · Video: youtu.be/aoFbngpUhP8 · Published Oct 28, 2026 · Team: Abhinav Shukla.

## Caveats carried from the read (not laundered)

Many bodies share a template style (baseline-0% vs project-100%
results · "an agent is not a prompt — it is a loop") and many
results are self-labeled simulated, synthetic, mocked, or
placeholders — the rows preserve those labels; nothing here
treats a claimed result as a verified outcome. Where a sidebar
link's URL was not printed in the page text, the row says so
instead of guessing. Source of record for this file: the live
recon read of 2026-11-03 19:18–19:33 UTC (single enumeration;
the D1 seat's parallel census is the cross-check).
