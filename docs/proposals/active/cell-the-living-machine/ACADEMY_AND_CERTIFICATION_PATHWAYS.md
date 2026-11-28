# Academy, Skills and Certification Pathways

## Purpose
The platform turns learning into practical capability through courses, labs, build artifacts, peer review and externally verifiable credentials. Learning pathways are open across ages and experience levels; the player selects a domain and challenge profile.

## AMD pathway
| Path | Focus | Evidence / credential |
|---|---|---|
| AMD AI Academy — AI Foundations | AI, ML and model experimentation on AMD platforms | Course completion evidence |
| Build AI | Intelligent applications, agents and multimodal workflows | Working application artifacts |
| Optimize & Deploy AI | Production inference, scaling and GPU performance | Deployment and benchmark artifacts |
| ROCm Certified Associate | ROCm setup, Instinct architecture, libraries/frameworks, HIP/CUDA porting, profiling and optimization | Official AMD ROCm Certified Associate credential |
| Adaptive Computing Learning Center | Vitis, Vivado, adaptive accelerators, SoCs and FPGAs | Course and lab evidence |
| GPUOpen learning | Graphics, shaders, RDNA optimization, engine performance and GPU tooling | Reproducible graphics/performance projects |

Official starting points:
- https://developer.amd.com/amd-ai-academy/
- https://developer.amd.com/rocm-certified/
- https://www.amd.com/en/developer/browse-by-resource-type/training.html
- https://gpuopen.com/learn/

## NVIDIA pathway
| Path | Focus | Evidence / credential |
|---|---|---|
| NVIDIA Deep Learning Institute | Deep learning, AI, data science and accelerated computing | Course certificate where offered |
| OpenUSD Development | Reusable 3D assets, scene composition and interoperability | NVIDIA-Certified Associate OpenUSD Foundations and Workflows plus NVIDIA-Certified Professional OpenUSD Development |
| Omniverse / digital twins | 3D collaboration, simulation and industrial digital twins | Reproducible USD scene and simulation artifact |
| Isaac / Physical AI | Robotics, simulation, policy training and sim-to-real | Simulation and deployment evidence |
| CUDA / TensorRT | GPU programming, inference and performance | Benchmarks and course credentials |

Official starting points:
- https://www.nvidia.com/en-us/training/
- https://www.nvidia.com/en-us/training/open-source/
- https://www.nvidia.com/en-us/learn/ai-learning-essentials/

## AMD Skills catalog matches

AMD also publishes an official agent-skill catalog at https://github.com/amd/skills. The project maps these workflow candidates:

| Skill | Project use | Execution tier |
|---|---|---|
| local-ai-app-integration | Integrate local AI services into the creator experience for offline support, privacy-sensitive workflows and reduced cloud inference costs. | Client/workstation integration; verify target hardware and runtime support. |
| rocm-doctor | Diagnose ROCm, HIP, PyTorch and llama.cpp environments used by studio and research infrastructure. | AMD GPU development and compute infrastructure. |
| tracelens-analysis-orchestrator | Analyze PyTorch profiler traces and prioritize system/kernel performance work. | AMD GPU training/inference and studio performance engineering. |

These are agent skills, separate from AMD-issued course certificates and ROCm certification credentials. The official catalog evolves; record the selected skill revision and evaluate its supported hardware before adding it to a production workflow.

## AMD certification details

AMD's official ROCm Certified Associate program is live through AMD AI Academy. The online Associate path is free and includes five modules covering ROCm setup, AMD Instinct architecture, ROCm libraries/frameworks, HIP and CUDA porting, and profiling/optimization, followed by an exam. The credential includes a verifiable digital badge; AMD's current program agreement specifies a 24-month validity period. Professional is listed for Q1 2027 and Expert as coming soon. Recheck the official program page before enrollment and renewal.

AMD AI Academy also offers self-paced learning paths and course-completion certificates. Course certificates and the formal ROCm Certified Associate credential remain distinct records.

Official references:
- https://developer.amd.com/amd-ai-academy/
- https://developer.amd.com/rocm-certified/
- https://developer.amd.com/ai-developer-program/
- https://www.amd.com/en/developer/browse-by-resource-type/training.html

## NVIDIA certification details

NVIDIA currently lists two OpenUSD credentials that directly support the shared 3D and manufacturing pipeline:

| Credential | Exam profile | Best fit |
|---|---|---|
| NVIDIA-Certified Associate OpenUSD Foundations and Workflows (NCA-OUSD; localized pages also use NCA-OFW) | 50–60 multiple-choice questions, 1 hour, $125, no hands-on lab; valid for 2 years. | Workflow designers, technical program managers, industrial/3D specialists and collaborators planning OpenUSD pipelines. |
| NVIDIA-Certified Professional OpenUSD Development (NCP-OUSD) | 60–70 questions, 2 hours, $200; validates pipeline development, maintenance and optimization; 2–3 years of OpenUSD plus Python/C++ experience or completion of study-guide materials; valid for 2 years. | OpenUSD developers, pipeline engineers and 3D platform architects. |

The free Learn OpenUSD curriculum prepares learners for the certification pathway. NVIDIA's open-source course materials currently carry no completion certificate; the formal exam credentials issue digital badges and optional certificates. Verify exam code, price, eligibility and policy on the live NVIDIA certification pages before scheduling.

Official references:
- https://www.nvidia.com/en-us/learn/certification/openusd-development-associate/
- https://www.nvidia.com/en-us/learn/certification/openusd-development-professional/
- https://docs.nvidia.com/learn-openusd/latest/
- https://www.nvidia.com/en-us/training/open-source/

## NVIDIA Skills catalog matches

The live NVIDIA Skills catalog includes three strong matches for the production platform:

| Skill | Project use | Environment boundary |
|---|---|---|
| omniverse-cad-to-simready | Convert source CAD/3D assets into simulation-ready USD, assign reviewed materials/physics, validate conformance and package assets. | Studio pipeline; managed Content Agents and OVRTX stages require a configured provider, Docker, NVIDIA Container Toolkit and NVIDIA GPU. |
| omniverse-usd-performance-tuning | Diagnose USD stage load time, memory and FPS; optimize reusable definitions while preserving downstream behavior. | Studio/compute pipeline; requires a verified USD Optimize runtime and supported validation tools. |
| omniverse-content-services | Plan USD content access, versioning, collaboration and distributed compute across projects and systems of record. | Shared content infrastructure and digital-twin collaboration. |

Catalog source: https://github.com/NVIDIA/skills/blob/main/skills.sh.json

These are catalog matches, not installed skills or proof that the required infrastructure is provisioned. Each skill remains an optional studio workflow. The game client continues to target low-tier devices independently of NVIDIA workstation/compute requirements.

## Internal academy design
The project can host open curricula, structured labs, challenge scenarios, peer review and evidence portfolios. Vendor credentials remain issued and verified by the relevant provider. Internal game achievements are labeled as project achievements and never represented as AMD/NVIDIA certification.

Every pathway record includes provider, course/credential ID, prerequisites, delivery format, cost, availability date, official source, completion evidence, expiration/renewal rules and verification method.

## Practical project-linked curriculum
1. 3D modeling and Blender automation.
2. CAD, geometry, mesh repair and manufacturing constraints.
3. Engineering systems, automation, controls and simulation.
4. Scientific visualization, molecular structures and provenance.
5. Mobile graphics, optimization and performance profiling.
6. GPU computing and accelerated AI.
7. OpenUSD, digital twins and interoperable 3D pipelines.
8. Robotics, sensors, embedded systems and physical prototyping.
9. Safety, quality, documentation and production handoff.

Each course culminates in a reviewable artifact linked to a project and player portfolio.
