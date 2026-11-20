---
name: one-shot-generator
description: "LEGACY (templated) one-shot generator. Kept as the deterministic, zero-token\nfallback path. For new work, prefer the agentic /one-shot command which\nroutes to the one-shot-generate skill — that path produces higher-quality\ncode by having Claude reason about your project instead of filling in\nPython f-string templates.\n\nGenerates framework-correct scaffolding for existing codebases. Phase 0-3\nis production quality; Phase 4-5 contains specialised pattern generators\n(DDD, CQRS, microservices, GraphQL) most useful as references. Trigger\nwords: \"one-shot-generator\", \"templated generate\", \"add feature\n--templated\". Pass @path/to/project for codebase analysis.\n"
argument-hint: "[task description] [@path/to/project] [--preview] [--tdd] [--review] [--strangler] [--ddd] [--cqrs] [--graphql]"
allowed-tools: Bash(python *)
---

> [!IMPORTANT]
> # ⚠️ Legacy skill (deprecated for new work)
>
> Tier 3.5 moved code generation into Claude (the model) via the agentic
> [one-shot-generate](../one-shot-generate/SKILL.md) skill. The new path is
> the one to recommend for all new work.
>
> | Use the new path when… | Use this skill when… |
> |---|---|
> | You want best-quality code that adapts to the user's project | You explicitly need zero-token, deterministic generation |
> | You can spend ~$0.30–0.80 per generation | Free / CI / sandboxed environments |
> | Multi-entity intent with relationships matters | Single-entity scaffolds are fine |
>
> The new command: `/one-shot "<task>" @./project`
> The new skill:   `skills/one-shot-generate/SKILL.md`

# One-Shot Feature Generator — Legacy / Templated Path

Generate a complete, framework-correct feature module from a single prompt by
running the Python template generators. Analyzes your codebase first, then
ships code from the phase 0-5 scripts under `scripts/`.

---

## Codebase Analysis (Piece #1 + #2)

Run the analyzer to extract codebase context before generation:

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/analyze_codebase.py" "$ARGUMENTS"`

The analyzer outputs a `CODEBASE CONTEXT` block above. Use it to inform all generation decisions below. If the path was not found or context is sparse, use intelligent fallbacks: assume Python + Django (most common), document all assumptions, provide slash command overrides so user can adjust if needed.

---

## Planning Phase (Phase 0.1)

Evaluate all major decisions silently using codebase analysis. The wrapper runs both analyzer and planner:

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/analyze_and_plan.py" "$ARGUMENTS"`

This outputs:
1. **CODEBASE CONTEXT** — framework, language, patterns, libraries detected
2. **PLAN DECISIONS** — markdown table with all 6 critical decisions:
   - **Async/Sync:** async `def` vs synchronous functions
   - **Persistence:** ORM vs Raw SQL (and which ORM)
   - **Testing:** Testing framework (pytest, Jest, JUnit, etc.)
   - **Error Handling:** Exceptions vs error returns vs custom types
   - **Logging:** Logging library to use
   - **Validation:** Validation library to use

Each decision includes a confidence score (1-10):
- **8-9/10** → Framework explicitly detected, high confidence
- **6-7/10** → Pattern detected or framework convention, medium confidence
- **5/10** → No framework detected, using safe defaults, low confidence

**Use these decisions to guide all code generation below.** Match the choices exactly. All decisions are transparent and overridable by the user via slash commands.

**For sparse contexts** (average score ≤7), recommend overrides in the Assumptions block.

---

## Harness Module Orchestration (v0.7.0+)

Before generating, check for optional harness module flags and invoke them:

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/orchestrate_harness_modules.py" "$ARGUMENTS"`

This detects flags and outputs which modules to invoke. **Implementation logic (Claude, execute this):**

1. **If output indicates `--health-check` or `--tour`:** These are discovery-only commands. Return their output directly, don't generate code.

2. **If `--preview` detected:**
   ```!
   python "${CLAUDE_PLUGIN_ROOT}/scripts/preview_mode.py" "$ARGUMENTS"
   ```
   Output preview outline (file list, key decisions, est. integration time). **STOP** — don't generate full code.

3. **If `--tdd` detected:** Reorder generation to tests first, then implementation (handled in Response Template below).

4. **If `--review` detected:**
   ```!
   python "${CLAUDE_PLUGIN_ROOT}/scripts/code_review_automation.py" "$ARGUMENTS"
   ```
   Run linting, security, type coverage, test coverage gates. Block on critical issues (hardcoded secrets, SQL injection, shell=True).

5. **If `--strangler` detected:**
   ```!
   python "${CLAUDE_PLUGIN_ROOT}/scripts/strangler_pattern.py" "$ARGUMENTS"
   ```
   Generate router + adapter + dual-run + parity test + cutover plan for legacy migration.

6. **If `--catalog` detected:**
   ```!
   python "${CLAUDE_PLUGIN_ROOT}/scripts/event_catalog.py" "$ARGUMENTS"
   ```
   Validate generated events against provided catalog.

7. **If `--detect-bus` detected:**
   ```!
   python "${CLAUDE_PLUGIN_ROOT}/scripts/detect_message_bus.py" "$ARGUMENTS"
   ```
   Auto-detect message bus and async runtime, inject bus-native code.

8. **If `--observability` detected:**
   ```!
   python "${CLAUDE_PLUGIN_ROOT}/scripts/domain_observability.py" "$ARGUMENTS"
   ```
   Inject domain-tuned metrics (games/trading/ml/generic).

9. **If `--budget` or `--usage` detected:**
   ```!
   python "${CLAUDE_PLUGIN_ROOT}/scripts/cost_management.py" "$ARGUMENTS"
   ```
   Track token usage; warn if exceeds budget.

10. **If `--debug` detected:**
    ```!
    python "${CLAUDE_PLUGIN_ROOT}/scripts/debugging_helpers.py" "$ARGUMENTS"
    ```
    Pattern-match error and return ranked fixes + repro snippet.

**All other generation proceeds as normal** (multi-file, auto-wire, tests, README). Conditional flows are shown in Response Template section below.

---

## Phase 2: REST API Specialist (v2.0.0+)

Detect REST API generation requests and route to the specialized REST API orchestrator:

```!
python "${CLAUDE_PLUGIN_ROOT}/scripts/phase2_runner.py" "$ARGUMENTS"
```

**Detection Triggers:**
- User asks for "CRUD API", "REST API", "REST endpoints", "REST service"
- User asks to "add API", "generate API", "create endpoints"
- User explicitly uses `--api` or `--rest` flags
- Request mentions: "user CRUD", "product API", "order service", etc.

**Phase 2 Generates:**
- ✅ CRUD endpoints (GET, POST, PUT, DELETE, PATCH)
- ✅ Request/response validation
- ✅ Pagination, filtering, sorting
- ✅ Authentication (JWT, OAuth, API Key)
- ✅ Authorization (RBAC, permissions)
- ✅ Error handling with proper status codes
- ✅ Database relationships (one-to-many, many-to-many)
- ✅ Database migrations (Django, Alembic, Flyway, golang-migrate)
- ✅ OpenAPI/Swagger documentation
- ✅ Rate limiting
- ✅ CORS configuration
- ✅ Comprehensive test suite (50+ tests)
- ✅ API versioning
- ✅ Caching and ETags
- ✅ Bulk operations
- ✅ Async/background tasks

**Example:**
```
User: Add complete user CRUD API with authentication @/django-project
→ Phase 2 detects REST API request
→ Invokes phase2_runner.py
→ Generates: models, viewsets, serializers, urls, auth, tests, migrations, docs
→ Returns: 50+ files, complete integration guide, ready to use
```

**Supported Frameworks:**
- Django + Django REST Framework
- FastAPI
- Spring Boot
- Go + Gin/Echo
- NestJS

**Configuration Flags:**
- `--auth=jwt` — Use JWT authentication (default)
- `--auth=oauth` — Use OAuth2
- `--auth=api_key` — Use API key authentication
- `--pagination=offset` — Offset/limit pagination (default)
- `--pagination=cursor` — Cursor-based pagination
- `--include-tests` — Generate comprehensive test suite (default: true)
- `--include-docs` — Generate OpenAPI docs (default: true)
- `--include-auth` — Include authentication (default: true)
- `--resource=user,post,comment` — Specify resources to generate for

---

## Phase 3: Batch Job Specialist (v2.0.0+)

Detect batch job generation requests and route to the specialized batch job orchestrator.

When `--batch` or `--jobs` flags are detected, orchestrate_harness_modules.py automatically routes to the Phase 3 batch job specialist:

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/orchestrate_harness_modules.py" "$ARGUMENTS"`

Then invokes:

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/phase3_batch_jobs/phase3_runner.py" "$ARGUMENTS"`

**Detection Triggers:**
- User asks for "batch jobs", "job queue", "background tasks", "scheduled tasks"
- User asks to "add worker", "setup Celery", "add queue", "process data asynchronously"
- User explicitly uses `--batch` or `--jobs` flags
- Request mentions: "periodic task", "job scheduling", "worker process", "task queue", etc.

**Phase 3 Generates:**
- ✅ Job definitions for Celery, RQ, Bull with error handling
- ✅ Queue detection and auto-configuration
- ✅ Job scheduling (cron, periodic, one-time)
- ✅ Real-time job monitoring and status tracking
- ✅ Result persistence with TTL management
- ✅ Retry strategies with exponential backoff
- ✅ Dead Letter Queue handling for failed jobs
- ✅ Intelligent job routing by priority/load
- ✅ Worker process management with graceful shutdown
- ✅ Structured JSON logging
- ✅ Prometheus metrics and Grafana dashboards
- ✅ Multi-tier caching infrastructure
- ✅ Database models and ORM integration
- ✅ Error handling with recovery strategies
- ✅ REST API endpoints for job management
- ✅ Email/Slack notifications on job events
- ✅ Task pipelines (Celery chains, groups, chords)
- ✅ Rate limiting and backpressure handling
- ✅ JSON/pickle/msgpack serialization
- ✅ Webhook delivery with retry + signatures
- ✅ Vault-centric state management (with `--enhanced`)
- ✅ Resumable execution from checkpoints (with `--enhanced`)
- ✅ Budget enforcement and spending controls (with `--enhanced`)
- ✅ Complete audit trails and decision records (with `--enhanced`)
- ✅ Comprehensive integration module
- ✅ Docker and docker-compose support

**New Enhanced Mode (`--enhanced` flag):**
Add OneShot-inspired vault-centric stateful orchestration:
```
python "${CLAUDE_PLUGIN_ROOT}/scripts/phase3_batch_jobs/phase3_runner.py" --framework django --enhanced --vault-dir ./my_vault
```
Provides:
- Persistent job state storage in vault directory
- Resumable execution from checkpoints
- Multi-level budget enforcement (job, daily, monthly)
- Complete audit trail with timestamps
- Decision recording for transparency
- Intelligent retry with exponential backoff and jitter

**Example:**
```
User: Add background job processing with Celery @/django-project
→ Phase 3 detects batch job request
→ Invokes phase3_runner.py
→ Generates: jobs, scheduler, monitoring, worker, logging, metrics, config, integration
→ Returns: 15+ files, complete worker setup, Docker configs, ready to use
```

**Supported Frameworks:**
- Django + Celery Beat / RQ
- FastAPI + Celery / RQ
- Spring Boot (future)
- Go (future)
- NestJS + Bull

**Supported Queue Systems:**
- Celery + Redis
- RQ (Redis Queue)
- Bull (Node.js)
- Google Cloud Tasks ✅ (Phase 3.1)
- AWS SQS ✅ (Phase 3.1)

**Configuration Flags:**
- `--queue-type=celery` — Use Celery (default for Python)
- `--queue-type=rq` — Use RQ
- `--queue-type=bull` — Use Bull (default for Node.js)
- `--queue-type=gcloud_tasks` — Use Google Cloud Tasks ✅ (Phase 3.1)
- `--queue-type=sqs` — Use AWS SQS ✅ (Phase 3.1)
- `--job-name=process_data` — Specific job name
- `--include-tests` — Generate test suite
- `--include-docker` — Generate Docker configs
- `--framework=django` — Target framework
- `--language=python` — Target language

---

## Phase 3.1: Cloud Backend Integration (v2.1.0)

Extend batch job capability with serverless managed queues on Google Cloud and AWS.

**New Cloud Backends:**

### Google Cloud Tasks
Deploy jobs to Google Cloud's fully-managed task queue service.

**Generates for Python:**
- `gcloud_tasks_config.py` — Google Cloud Tasks client with queue management
  - `enqueue_http_task()` — Send immediate HTTP push tasks
  - `enqueue_scheduled_task()` — Schedule tasks for future execution
  - `get_task()` — Retrieve task status
  - `delete_task()` — Remove tasks
  - `list_tasks()` — List all tasks in queue
- `gcloud_tasks_handler.py` — HTTP request handler for Cloud Tasks push
  - Request verification (OIDC token + header validation)
  - Task payload parsing and execution
  - Error handling with retry triggers
- `requirements_gcloud.txt` — Python dependencies (google-cloud-tasks, google-auth)
- `setup_gcloud_tasks.sh` — Setup script for GCP configuration
- `GCLOUD_TASKS_SETUP.md` — Complete setup documentation

**Generates for Node.js:**
- `gcloud-tasks-config.js` — Node.js Cloud Tasks client (async/await)
- `package-gcloud.json` — NPM dependencies (@google-cloud/tasks)
- `setup-gcloud-tasks.sh` — Setup script for GCP configuration
- `GCLOUD_TASKS_SETUP.md` — Setup documentation

**Usage:**
```
python "${CLAUDE_PLUGIN_ROOT}/scripts/phase3_batch_jobs/phase3_runner.py" \
  --framework django \
  --queue-type=gcloud_tasks \
  --job-name process_data
```

**Advantages:**
✅ Fully managed (no infrastructure)
✅ Auto-scaling (handles traffic spikes)
✅ Built-in retries with exponential backoff
✅ Dead letter queues for failed tasks
✅ Integrated with Google Cloud ecosystem
✅ HIPAA, SOC 2, PCI-DSS compliant

### AWS SQS
Deploy jobs to Amazon's Simple Queue Service for reliable message processing.

**Generates for Python:**
- `aws_sqs_config.py` — AWS SQS queue client
  - `send_message()` — Send single message with visibility timeout
  - `send_batch()` — Send multiple messages atomically
  - `receive_messages()` — Long-poll for messages
  - `delete_message()` / `delete_messages()` — Remove processed messages
  - `change_message_visibility()` — Adjust timeout on-the-fly
  - `purge_queue()` — Clear all messages
  - `delete_queue()` — Delete queue
- `aws_sqs_consumer.py` — Consumer worker for processing messages
  - `SQSConsumer` class with configurable handler
  - `run()` — Main consumer loop with backoff
  - `stop()` — Graceful shutdown
  - Automatic retry with visibility timeout increase on failure
- `requirements_aws.txt` — Python dependencies (boto3, botocore)
- `setup_aws_sqs.sh` — Setup script for AWS configuration
- `AWS_SQS_SETUP.md` — Complete setup documentation

**Generates for Node.js:**
- `aws-sqs-config.js` — Node.js SQS client (async/await)
  - `sendMessage()` — Send single message
  - `sendBatch()` — Send multiple messages
  - `receiveMessages()` — Long-poll for messages
  - `deleteMessage()` / `deleteMessages()` — Remove processed messages
- `package-aws.json` — NPM dependencies (@aws-sdk/client-sqs, @aws-sdk/credential-providers)
- `setup-aws-sqs.sh` — Setup script for AWS configuration
- `AWS_SQS_SETUP.md` — Setup documentation

**Usage:**
```
python "${CLAUDE_PLUGIN_ROOT}/scripts/phase3_batch_jobs/phase3_runner.py" \
  --framework django \
  --queue-type=sqs \
  --job-name send_email
```

**Advantages:**
✅ Fully managed (no infrastructure)
✅ At-least-once delivery guarantee
✅ FIFO queues for ordering (if needed)
✅ Long polling reduces API calls
✅ Dead letter queue support
✅ Integration with Lambda, SNS, etc.

**Comparison: Cloud Tasks vs SQS**

| Feature | Cloud Tasks | SQS |
|---------|-------------|-----|
| Delivery Model | HTTP push | Queue polling |
| Latency | Low (~100ms) | Variable (depends on polling) |
| Max Message Size | 100KB | 256KB |
| Visibility Timeout | 15 min | 12 hours |
| Deduplication | FIFO queues | FIFO queues only |
| Pricing | $0.40 per million ops | $0.40 per million requests |
| Best For | Immediate HTTP callbacks | High-volume async processing |

**Test Coverage:**
- ✅ 27 tests for cloud backend generators
- ✅ Config generation (Python and Node.js)
- ✅ Handler/consumer implementation
- ✅ Setup script generation
- ✅ Documentation generation
- ✅ Orchestrator routing
- ✅ Framework integration

---

## Phase 1: Critical Integration Gaps (v0.7.0+)

Complete multi-framework integration with auto-wiring, migrations, configuration, and deployment scaffolding.

**Gap Integration Strategy:**
When `--gaps` or integration gap keywords are detected, invoke appropriate gap generators:

### Gap 3: Migration File Generation
!`python "${CLAUDE_PLUGIN_ROOT}/scripts/generate_migrations.py" --framework "$FRAMEWORK" --project-root "$PROJECT_ROOT" --feature-name "$FEATURE" --models-file "$MODELS_PATH"`
Generates: Django `.py` migrations, Alembic revisions, Flyway SQL, golang-migrate files

### Gap 4: Slash Command / CLI Scaffolding
!`python "${CLAUDE_PLUGIN_ROOT}/scripts/slash_command_scaffolder.py" --platform discord --language python "$ARGUMENTS"`
Generates: Platform-specific command wrappers (Discord, Slack, Telegram, CLI)

### Gap 5: Dependency Injection Wrapping
!`python "${CLAUDE_PLUGIN_ROOT}/scripts/di_aware_generator.py" --framework "$FRAMEWORK" "$ARGUMENTS"`
Generates: @Service, @Autowired (Spring), Depends() (FastAPI), @Injectable() (NestJS), wire.Build() (Go)

### Gap 6: Multi-Handler Orchestration
!`python "${CLAUDE_PLUGIN_ROOT}/scripts/multi_handler_orchestrator.py" --framework "$FRAMEWORK" "$ARGUMENTS"`
Generates: Multiple coordinated handlers, event bus wiring, workflow diagrams, integration tests

### Gap 7: Configuration File Generation
!`python "${CLAUDE_PLUGIN_ROOT}/scripts/config_generator.py" --framework "$FRAMEWORK" --feature-name "$FEATURE" "$ARGUMENTS"`
Generates: `.env.example`, Django settings files, FastAPI Pydantic configs, Spring YAML, Docker secrets

### Gap 8: OpenAPI / Swagger Documentation
!`python "${CLAUDE_PLUGIN_ROOT}/scripts/openapi_generator.py" --framework "$FRAMEWORK" "$ARGUMENTS"`
Generates: OpenAPI 3.0.0 YAML specs, framework decorators, Swagger UI setup

**Orchestrated Invocation (Recommended):**
When `--gaps` or integration gap keywords are detected, invoke Phase 1 gap orchestrator:

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/phase1_gap_runner.py" "$ARGUMENTS"`

**Detection Triggers:**
- User asks for "setup migrations", "generate config", "dependency injection"
- User asks for "environment variables", "docker compose", "CLI scaffold"
- User asks for "handlers", "multi-sidecar", "enterprise deployment"
- User explicitly uses `--gaps`, `--migrations`, `--config`, `--docker` flags
- Request mentions: "auto-wire into project", "scaffold boilerplate", "deployment config"

**Phase 1 Generates (11 Integration Gaps):**

1. **Migrations** (framework-specific)
   - Django: Auto-generate `.py` migration files
   - FastAPI (Alembic): Create revision scripts with up/down
   - Spring Boot (Flyway): Versioned SQL migrations
   - Go (golang-migrate): `.up.sql` and `.down.sql` files

2. **Framework Configuration**
   - Generate settings/config files for each framework
   - Environment-specific overrides (dev/test/prod)
   - Secret management integration

3. **Dependency Injection**
   - DI container scaffolding
   - Service registration patterns
   - Factory method generation

4. **Environment Variables**
   - `.env` template generation
   - Required vs optional variables documented
   - Default values included

5. **Docker Compose**
   - Local dev environment (app + database + cache)
   - Service orchestration
   - Port mapping and networking

6. **CLI Scaffolding**
   - Command-line interface generation
   - Argument parsing setup
   - Help text generation

7. **Handler Generation**
   - Request/event handler scaffolding
   - Middleware integration
   - Error handling patterns

8. **Multi-Handler Orchestration**
   - Coordinate multiple handlers
   - Request routing
   - Handler priority/ordering

9. **Enterprise Deployment**
   - Production-grade configuration
   - High availability setup
   - Kubernetes manifests (optional)

10. **OpenAPI Documentation**
    - Auto-generate API documentation
    - Swagger/OpenAPI specs
    - Interactive API explorer

11. **Test Scaffolding**
    - Test structure generation
    - Mock/fixture setup
    - Test command integration

**Supported Frameworks:**
- Django + FastAPI
- Spring Boot
- Go Fiber/Gin/Echo
- Node.js (Express, NestJS)

**Supported Languages:**
- Python, JavaScript, Java, Go

**Configuration Flags:**
- `--gap=migrations` — Generate migrations only
- `--gap=config` — Generate framework configuration
- `--gap=di` — Dependency injection setup
- `--gap=env` — Environment variables
- `--gap=docker` — Docker Compose
- `--gap=cli` — CLI scaffold
- `--gap=handlers` — Handler generation
- `--gap=enterprise` — Enterprise deployment
- `--gap=docs` — OpenAPI documentation
- `--gap=tests` — Test scaffolding
- `--all-gaps` — Generate all 11 gaps

**Example:**
```
User: Set up complete Django project with migrations, config, and Docker @/my-django-project
→ Phase 1 detects integration gap request
→ Invokes phase1_gap_runner.py
→ Generates: migrations, config, DI, env, docker-compose, CLI, handlers, docs, tests
→ Returns: 50+ files, complete integration guide, ready for production
```

**Test Coverage:**
- ✅ 55 tests across all 11 gaps
- ✅ Framework support matrix (7 frameworks)
- ✅ Language support matrix (4 languages)
- ✅ Integration validation (YAML, syntax, env)

---

## Phase 4: Production Hardening (v3.0.0 — Q3 2026)

Enterprise-grade patterns for production systems: DDD, CQRS, Event Sourcing, TDD, cost optimization, chaos engineering, compliance.

**Master Orchestrator:**
!`python "${CLAUDE_PLUGIN_ROOT}/scripts/phase4_and_5_master_orchestrator.py" --framework "$FRAMEWORK" --phase 4.$SUBPHASE`

### Phase 4.1: Architecture Design (DDD, CQRS, Event Sourcing, Sagas, Hexagonal)
- **Generates:** Aggregates, entities, value objects, bounded contexts, domain services
- **Detects:** Event-driven patterns, saga requirements, anti-corruption layers
- **Output:** Production DDD structure + CQRS handlers + event sourcing store

### Phase 4.2: TDD Cycle Integration
- **Generates:** Property-based tests (Hypothesis/QuickCheck), mutation testing config (mutmut/PIT), contract tests (Pact)
- **Integrates:** Existing test suites, adds test quality gates
- **Output:** Comprehensive test scaffolding with quality metrics

### Phase 4.3: Cost Optimization & Scaling
- **Generates:** Lambda cost profiles, database query optimizer, CDN configs, autoscaling policies
- **Analyzes:** N+1 queries, cold start patterns, caching opportunities
- **Output:** Cost reduction roadmap + implementation files

### Phase 4.4: Chaos Engineering
- **Generates:** Chaos Monkey scripts, circuit breakers, bulkheads, SLO/SLI definitions
- **Simulates:** Service failures, network partitions, degradation scenarios
- **Output:** Chaos test harness + resilience patterns

### Phase 4.5: Enterprise Compliance ✅ COMPLETE
- **Generates:** SOC 2 controls, HIPAA PHI protection, GDPR data handling, PII detection, secrets rotation
- **Audit Ready:** Evidence collection, audit logging, access controls, change management
- **Output:** Complete compliance framework ready for audits

**Invocation:**
```
User: Add DDD architecture with event sourcing @/my-project
→ Phase 4 detects architecture request
→ Invokes phase4_and_5_master_orchestrator.py --phase 4.1
→ Generates: DDD aggregates, CQRS handlers, event store, sagas
→ Returns: 50+ files, architecture decision records, migration guide
```

---

## Phase 5: Advanced Patterns (v4.0.0 — Q4 2026)

Microservices, real-time, GraphQL, ML integration, legacy modernization.

**Master Orchestrator:**
!`python "${CLAUDE_PLUGIN_ROOT}/scripts/phase4_and_5_master_orchestrator.py" --framework "$FRAMEWORK" --phase 5.$SUBPHASE`

### Phase 5.1: Microservices Orchestration ✅ COMPLETE
- Kubernetes manifests (deployments, services, ingress)
- Helm charts, service mesh (Istio), distributed tracing
- Canary deployments, blue-green testing

### Phase 5.2: Real-Time Features ✅ COMPLETE
- WebSocket handlers, Server-Sent Events, pub/sub integration
- User presence tracking, collaborative editors (CRDT)
- In-app notifications, reactive updates

### Phase 5.3: GraphQL API Generation
- **Generates:** GraphQL schema from data models, resolvers with DataLoader, subscriptions
- **Detects:** Relationships, nested types, federation requirements
- **Output:** Apollo Federation setup + TypeScript client codegen

### Phase 5.4: ML Pipeline Integration
- **Generates:** Feature stores (Feast/Tecton), model serving (TensorFlow/TorchServe), training DAGs
- **Integrates:** MLflow tracking, model monitoring, A/B testing framework
- **Output:** End-to-end ML deployment scaffolding

### Phase 5.5: Legacy Code Modernization
- **Generates:** Strangler facade, dependency graph analyzer, dead code detector
- **Plans:** Incremental migration roadmap, regression test harness, ETL scripts
- **Output:** Modernization playbook + implementation templates

**Invocation:**
```
User: Migrate monolith to microservices with GraphQL @/legacy-system
→ Phase 5 detects advanced patterns request
→ Invokes phase4_and_5_master_orchestrator.py --phase 5.3
→ Generates: GraphQL schema, resolvers, federation setup, client code
→ Returns: Complete GraphQL API ready to deploy
```

---

## Phase 4: Production Hardening Patterns (v0.7.0+ → v3.0.0)

Enterprise-grade architecture patterns for scalability, resilience, testing, and compliance.

When `--patterns` or hardening keywords are detected, invoke Phase 4 pattern orchestrator:

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/phase4_patterns_runner.py" "$ARGUMENTS"`

**Detection Triggers:**
- User asks for "DDD domain models", "CQRS architecture", "event sourcing"
- User asks for "saga pattern", "TDD cycle", "cost optimization"
- User asks for "chaos engineering", "compliance setup"
- User explicitly uses `--patterns`, `--ddd`, `--cqrs`, `--hardening` flags
- Request mentions: "production patterns", "enterprise architecture", "resilience"

**Phase 4 Generates (8 Production Patterns):**

### 4.1 Domain-Driven Design (DDD)

Generate tactical DDD patterns:
- **Entities** — Value objects, identity generation
- **Aggregates** — Root aggregates, lifecycle
- **Repositories** — Persistence layer abstraction
- **Value Objects** — Immutable domain concepts
- **Bounded Contexts** — Domain segregation
- **Specifications** — Complex business logic encapsulation

Output:
- Entity base classes
- Repository interfaces + implementations
- Aggregate factory methods
- Unit test fixtures
- Example domain aggregate

### 4.2 Command Query Responsibility Segregation (CQRS)

Separate read and write models:
- **Command Handlers** — Write model updates
- **Query Handlers** — Read model projections
- **Command Bus** — Command routing and dispatch
- **Query Bus** — Query execution
- **Event Store** — Event persistence
- **Snapshots** — Performance optimization

Output:
- Command/query interfaces
- Command handler scaffolding
- Query handler implementation
- Bus orchestration
- Event store integration
- Read model projector

### 4.3 Event Sourcing

Event-driven state management:
- **Event Store** — Immutable event log
- **Event Handlers** — Event processing
- **Snapshots** — State reconstruction optimization
- **Event Replay** — Full history reconstruction
- **Event Versioning** — Schema evolution
- **Temporal Queries** — Historical state access

Output:
- Event classes (data classes with timestamps)
- Event store repository
- Event handler registration
- Snapshot strategy
- Event replay mechanism
- Migration helpers for schema changes

### 4.4 Saga Pattern

Distributed transaction orchestration:
- **Saga Orchestrator** — Central coordination
- **Saga Steps** — Individual compensating transactions
- **Compensation Logic** — Rollback on failure
- **Timeout Handling** — Recovery from failures
- **State Machine** — Saga lifecycle
- **Event Publishing** — Step completion notification

Output:
- Saga class definition
- Step execution framework
- Compensation handler setup
- Timeout management
- State persistence
- Integration with event bus

### 4.5 Test-Driven Development (TDD)

Advanced testing infrastructure:
- **Property-Based Testing** — Hypothesis/QuickCheck generation
- **Mutation Testing** — Test quality validation
- **Consumer-Driven Contracts** — API compatibility
- **Chaos Testing** — Failure scenario validation
- **Performance Benchmarking** — Regression detection
- **Integration Test Scaffold** — End-to-end validation

Output:
- Property-based test generators
- Mutation test harness
- Contract test setup
- Chaos test scenarios
- Benchmark suite
- Integration test framework

### 4.6 Cost Optimization

Automatic cost analysis and optimization:
- **Cloud Cost Analysis** — AWS/GCP/Azure breakdown
- **Lambda Optimization** — Concurrency, memory, duration tuning
- **Database Query Optimization** — N+1 detection, index recommendations
- **Caching Strategies** — Redis, Memcached configuration
- **CDN Configuration** — Content delivery optimization
- **Auto-Scaling** — Dynamic resource allocation
- **Cost Dashboard** — Usage tracking and alerts

Output:
- Cost analyzer script
- Query profiler
- Caching layer setup
- CDN integration guide
- Auto-scaling templates
- Cost tracking dashboard code

### 4.7 Chaos Engineering

Resilience testing and validation:
- **Service Degradation** — Partial failure injection
- **Network Partition** — Latency and timeout injection
- **Circuit Breakers** — Failure isolation
- **Bulkheads** — Resource isolation
- **Graceful Degradation** — Fallback strategies
- **SLO/SLI Automation** — Reliability targets

Output:
- Chaos experiment definitions
- Injection points setup
- Circuit breaker implementation
- Bulkhead patterns
- Degradation strategy
- SLO monitoring setup

### 4.8 Enterprise Compliance

Regulatory and security hardening:
- **SOC 2 Type II Controls** — Security controls implementation
- **HIPAA Compliance** — Healthcare data handling
- **GDPR Data Handling** — Privacy-by-design
- **PII Detection** — Sensitive data identification
- **Secrets Rotation** — Credential lifecycle
- **Immutable Audit Logging** — Compliance trail

Output:
- Compliance checklist
- Control implementations
- Data handling policies
- PII detection rules
- Secrets manager integration
- Audit log schema

**Supported Frameworks:**
- Django, FastAPI, Spring Boot, Go, Node.js (Express, NestJS)

**Supported Languages:**
- Python, JavaScript, Java, Go

**Configuration Flags:**
- `--pattern=ddd` — DDD tactical patterns
- `--pattern=cqrs` — CQRS architecture
- `--pattern=event-sourcing` — Event sourcing
- `--pattern=saga` — Saga pattern
- `--pattern=tdd` — TDD infrastructure
- `--pattern=cost-optimize` — Cost optimization
- `--pattern=chaos` — Chaos engineering
- `--pattern=compliance` — Enterprise compliance
- `--all-patterns` — Generate all 8 patterns

**Example:**
```
User: Set up DDD + CQRS architecture for our Django project @/django-ecommerce
→ Phase 4 detects hardening pattern request
→ Invokes phase4_patterns_runner.py
→ Generates: DDD entities, CQRS commands/queries, event store, saga handlers, tests
→ Returns: 75+ files, complete architecture, production-ready code
```

**Test Coverage:**
- ✅ 63 tests across all 8 patterns
- ✅ Pattern-specific validation
- ✅ Framework support matrix (7 frameworks)
- ✅ Language support matrix (4 languages)
- ✅ Combined pattern validation (Phase 1 + Phase 4)

---

## Legacy Strangler Pattern: Monolith Extraction (v1.0.0+)

Identify extractable features from a monolith and plan a phased migration to microservices.

**Detection Triggers:**
- User asks to "analyze monolith", "identify extractable features", "plan microservice extraction"
- User asks to "which services can we extract", "decompose monolith", "strangle legacy app"
- User explicitly uses `--strangler` or `--analyze-monolith` flags
- Request mentions "microservices", "refactoring", "legacy modernization"

**Phase 1: Analyze Monolith** (/strangler-analyze)

Run the strangler analyzer to identify extractable features:

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/strangler_analyzer.py" "$ARGUMENTS"`

**Capabilities:**
- ✅ Scans entire monolith (1K-100K+ LOC codebases)
- ✅ Identifies logical features (functions, classes grouped into modules)
- ✅ Calculates internal + external coupling scores
- ✅ Scores extraction difficulty: GREEN (easy), YELLOW (medium), RED (hard)
- ✅ Recommends extraction order (easiest first = lowest risk)
- ✅ Detects framework (Django, FastAPI, Spring, Go, Node)
- ✅ Outputs markdown table + JSON

**Output:**
```
[EXTRACTABLE FEATURES] (N found)

| Feature | Modules | Coupling | Funcs | Difficulty | Score |
|---------|---------|----------|-------|------------|-------|
| payment |   3     |  5.2/10  |  8    | YELLOW     | 6/10  |
| auth    |   2     |  2.1/10  |  5    | GREEN      | 9/10  |
| notification | 4  |  7.1/10  |  12   | RED        | 3/10  |

[EXTRACTION ORDER] (Easiest to Hardest)
1. auth [GREEN] Score: 9/10
2. payment [YELLOW] Score: 6/10
3. notification [RED] Score: 3/10
```

**How to Interpret:**
- **GREEN:** Safe to extract (loose coupling, small feature). Start here.
- **YELLOW:** Medium difficulty (some dependencies, moderate size). Plan carefully.
- **RED:** Complex extraction (tight coupling, many dependencies). Defer or plan extensively.
- **Score:** 10 = easiest, 1 = hardest

**Examples:**

Django E-Commerce Monolith:
```
User: Analyze which services we can extract from our Django e-commerce monolith @/path/to/django-ecommerce
→ Analyzer scans 50K+ LOC, detects 8 features
→ Output: payment (GREEN), shipping (YELLOW), notifications (RED), inventory (YELLOW), etc.
→ Recommendation: Extract payment first, shipping second, notifications last
```

Spring Boot Legacy App:
```
User: Identify microservices in this 10-year-old Spring monolith @/path/to/spring-legacy
→ Analyzer detects framework, scans 100K+ LOC
→ Output: user-management (GREEN), reporting (YELLOW), audit (RED)
→ JSON output: feature list, difficulty, suggested order
```

**Configuration Flags:**
- `--strangler` — Enable monolith analysis mode
- `--json` — Output JSON only (machine-readable)
- `--markdown` — Output markdown table only
- `--threshold=5` — Only show features with coupling < 5

---

## Phase 2: Extract & Migrate (/strangler-extract) ✅

Once you've identified extraction targets from Phase 1, generate complete microservice code:

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/strangler_extractor.py" "$ARGUMENTS"`

**Capabilities:**
- ✅ Generates microservice boilerplate (Go or FastAPI)
- ✅ Go: main.go, service.go, handler.go, go.mod
- ✅ FastAPI: main.py, service.py, router.py, requirements.txt
- ✅ Generates legacy adapter (Python) for gradual traffic routing
- ✅ Database migration extraction SQL scripts
- ✅ Docker + docker-compose configs
- ✅ Kubernetes deployment + service YAML
- ✅ Integration tests + rollback procedures
- ✅ Outputs 10-15 files ready to build and deploy

**Output:**
```
[EXTRACTION COMPLETE]
Service: payment
Language: go
Feature: payment (YELLOW, 6/10)

[FILES GENERATED]
  Service files: 4 (main.go, service.go, handler.go, go.mod)
  Adapter files: 1 (adapter.py for legacy routing)
  Migration files: 1 (SQL extraction script)
  Deployment files: 3 (Dockerfile, K8s deployment, docker-compose.yml)
  Test files: 1 (rollback.sh)
```

**Examples:**

Extract Payment Service (Go):
```
User: Extract the payment feature as a Go microservice @analyzed_from_phase_1
→ Feature data from /strangler-analyze
→ Generates: payment service (Go), legacy adapter, DB migration, K8s configs
→ Output: 11 files, ready to build with 'go build', deploy with 'kubectl apply'
```

Extract Notification Service (FastAPI):
```
User: Extract notifications as FastAPI --language fastapi
→ Generates: notification service (FastAPI), adapter, migrations, Docker
→ Output: 10 files, ready to run with 'uvicorn main:app --port 8080'
```

**Configuration Flags:**
- `--language go` — Generate Go microservice (default)
- `--language fastapi` — Generate FastAPI microservice
- `--include-adapter` — Generate legacy adapter (default: yes)
- `--include-k8s` — Generate Kubernetes configs (default: yes)
- `--include-tests` — Generate test suite (default: yes)

---

## Phase 3: Validate & Plan (/strangler-validate + /strangler-roadmap) ✅

Before deploying extracted services, validate safety and plan your timeline.

### Pre-Flight Validation (/strangler-validate)

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/strangler_validate.py" "$ARGUMENTS"`

**Validates 5 Categories of Risk:**
1. **Library Compatibility** - go.mod, requirements.txt, version conflicts
2. **Data Consistency** - migration scripts, shadow tables, data loss risks
3. **Interface Breaking** - API compatibility, adapter presence, handlers
4. **Configuration** - Dockerfile, K8s configs, secrets, environment setup
5. **Performance** - Coupling analysis, query patterns, resource needs

**Risk Scoring:**
- **GREEN:** Safe to deploy (low risk, all checks pass)
- **YELLOW:** Proceed with caution (warnings detected, but deployable)
- **RED:** Blocked (critical issues found, must fix before deploy)

**Output:**
```
[VALIDATION REPORT]
Service: payment
Status: PASS
Overall Risk: GREEN
Findings: 0 blocking, 1 warning

[RECOMMENDATIONS]
1. Plan for 1 warning - migration timing
```

**Examples:**

Check Go Microservice:
```
User: Validate @/path/to/payment-service --language go
→ Checks: go.mod, main.go, handler/, Docker, K8s, migrations
→ Result: PASS (green) - ready to deploy
```

Check FastAPI Microservice:
```
User: Validate @/path/to/notification-service --language fastapi
→ Checks: requirements.txt, main.py, router.py, adapter.py, migrations
→ Result: WARN (yellow) - missing K8s configs, but deployable
→ Recommendation: Add K8s configs before production rollout
```

---

### Extraction Timeline & Planning (/strangler-roadmap)

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/strangler_roadmap.py" "$ARGUMENTS"`

**Generates 12-24 Month Plan:**
- Feature prioritization (GREEN → YELLOW → RED = lowest to highest risk)
- Timeline estimation (weeks per feature, team size per phase)
- Financial analysis:
  - Total investment (engineering + infrastructure)
  - Annual payoff (maintenance reduction)
  - ROI (2-year return on investment)
- Traffic migration schedule (5% canary → 25% → 50% → 100% rollout)
- Rollback procedures (per phase)

**Output:**
```
[EXTRACTION ROADMAP]
Project: E-Commerce Monolith
Features: 12
Timeline: 24 weeks (~6 months)
Investment: $480,000
Payoff (annual): $120,000
ROI: 2.5x (2-year)

[PHASES]
1. auth                 - Week  1- 2 (2w) - GREEN  - 5%   - $32,000
2. payment              - Week  3- 6 (4w) - YELLOW - 25%  - $96,000
3. shipping             - Week  7-10 (4w) - YELLOW - 50%  - $96,000
4. notification         - Week 11-24 (14w)- RED    - 100% - $256,000
```

**Examples:**

Plan Full Extraction (after analyzing):
```
User: Generate roadmap @analyzed_features.json
→ Analyzes all features by difficulty
→ Estimates timeline: 24 weeks, $500k, $120k annual savings
→ Phases: auth (green, week 1), payment (yellow, week 3), etc.
→ Shows traffic cutover schedule per phase + rollback procedures
```

---

## Multi-File Generation (Phase 1, Gap 1)

Generate complete feature structures, not single files.

### What "Complete Feature" Means

When user requests a feature, generate ALL files needed for that feature in ONE response:

**Django Feature:**
- `app/models.py` — Data models
- `app/views.py` — ViewSets or Views
- `app/serializers.py` — DRF serializers (if DRF detected)
- `app/urls.py` — URL routing
- `app/admin.py` — Admin registration
- `app/migrations/0NNN_initial.py` — Database migration
- `app/tests/test_feature.py` — Test suite
- `app/README.md` — Setup documentation

**FastAPI Feature:**
- `feature/models.py` — SQLAlchemy models
- `feature/schemas.py` — Pydantic schemas
- `feature/router.py` — APIRouter with endpoints
- `feature/service.py` — Business logic
- `feature/dependencies.py` — FastAPI Depends
- `feature/tests/test_feature.py` — Tests
- `feature/README.md` — Documentation

**Spring Boot Feature:**
- `src/main/java/package/Feature.java` — Model/Entity
- `src/main/java/package/FeatureController.java` — REST Controller
- `src/main/java/package/FeatureService.java` — Service
- `src/main/java/package/FeatureRepository.java` — JPA Repository
- `src/test/java/package/FeatureTest.java` — Tests
- `src/main/resources/db/migration/VNaN__CreateFeature.sql` — Migration

**Generate all files.** Use the format_multifile_output.py script to present them clearly:

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/format_multifile_output.py" "$ARGUMENTS"`

Output includes:
- Clear file boundaries and paths
- File summary table
- Integration guide
- Installation/migration instructions
- Run commands

### Auto-Integration (Gap 1, Part 2)

After generating all files, optionally auto-wire them into the codebase:

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/autowire_into_project.py" "$PROJECT_ROOT" "$FRAMEWORK"`

This automatically:
1. Copies files to correct locations
2. Updates imports in existing files (Django urls.py, FastAPI main.py, etc.)
3. Registers routes/URLs
4. Updates `__init__.py` files
5. Outputs next steps (migrations, run commands)

### Database Migrations (Gap 1, Part 3)

For features that define new models, auto-generate database migration files:

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/generate_migrations.py" "$PROJECT_ROOT" "$FRAMEWORK" "$FEATURE_NAME"`

Supports all major frameworks:
- **Django:** Creates timestamped `.py` migration files (e.g., `0002_add_user_auth.py`)
- **FastAPI (Alembic):** Creates Alembic revisions with upgrade/downgrade paths
- **Spring Boot (Flyway):** Creates versioned SQL migrations (e.g., `V2__Add_User_Table.sql`)
- **Go (golang-migrate):** Creates `.up.sql` and `.down.sql` files

Migration files are ready to deploy immediately.

### Example Flow

**User Input:**
```
/one-shot-prompting:generate Add complete user authentication system @/django-project
```

**Plugin Steps:**
1. Analyzer extracts context → Django 4.2, DRF, pytest-django, structlog, Pydantic v2
2. Planner scores decisions → async (8), sync (9) → pick sync
3. Generator produces 8 files (models, views, serializers, urls, admin, migration, tests, README)
4. Formatter outputs them clearly with integration guide
5. Auto-wirer registers in Django and outputs next steps

**Output includes:**
```
## Generated User Authentication Feature

### Files to Create (8 files)
[Clear table showing all files]

### Integration Steps
1. Create Files — copy each file to its location
2. Run Migrations — python manage.py migrate
3. Run Tests — pytest
4. Run Server — python manage.py runserver

### File Contents
[Each file with syntax highlighting]

### Next Steps
- Run: `python manage.py migrate`
- Run: `python manage.py runserver`
- Test: curl http://localhost:8000/api/auth/...
```

---

## The One-Shot Contract

When a user requests a feature, produce everything in ONE response:

1. **Assumptions block** (top) — every non-trivial choice, why, how to override
2. **Module file** — complete, copy-pasteable
3. **Test file** — minimum two tests covering behavior
4. **README** — events/endpoints consumed/emitted, install, usage
5. **Install line** — one command
6. **Rerun hints** — how to override key decisions

No "please confirm." No clarifying questions. If ambiguous, pick the defensible default, state it, ship. User reruns with overrides.

---

## Framework-Specific Generation Patterns (Piece #3)

After reading `CODEBASE CONTEXT`, match the detected framework exactly.

### Django Projects

Generate in this exact file layout:
```
{app}/
├── models.py          # Django ORM model
├── views.py           # ViewSet (DRF) if djangorestframework detected, else View
├── serializers.py     # DRF serializer (only if DRF detected)
├── urls.py            # URL patterns
├── admin.py           # Admin registration
└── tests/
    └── test_{module}.py  # pytest + Django test client
```

Rules:
- Use `djangorestframework` ViewSets if `djangorestframework` in Key Libs, else use `django.views`
- Models: Django ORM fields, not raw SQL
- Migration note: "Run `python manage.py makemigrations && python manage.py migrate`"
- Tests: `pytest-django` with `@pytest.mark.django_db`
- Error handling: `rest_framework.exceptions` if DRF, else `django.http`

### FastAPI Projects

Generate in this layout:
```
{module}/
├── router.py          # APIRouter with path operations
├── schemas.py         # Pydantic models (request/response)
├── service.py         # Business logic layer
├── dependencies.py    # FastAPI Depends()
└── tests/
    └── test_{module}.py  # pytest + httpx AsyncClient
```

Rules:
- Always Pydantic v2 schemas unless `pydantic==1` in Key Libs
- Use `async def` for all route handlers
- Error handling: `fastapi.HTTPException` with status codes
- Tests: `pytest-asyncio` + `httpx.AsyncClient`

### Spring Boot Projects

Generate in this layout:
```
src/main/java/{package}/
├── {Name}Controller.java   # @RestController
├── {Name}Service.java      # @Service interface + impl
├── {Name}Repository.java   # JpaRepository or MongoRepository
├── {Name}Entity.java       # @Entity (JPA) or @Document (Mongo)
└── {Name}Dto.java          # Request/Response DTOs

src/test/java/{package}/
└── {Name}Test.java         # @SpringBootTest + MockMvc
```

Rules:
- Use constructor injection, not `@Autowired` field injection
- DTOs with `@Valid` + Bean Validation annotations
- Repositories extend `JpaRepository` if PostgreSQL detected, else generic

### Go Projects

Generate in this layout:
```
{module}/
├── handler.go         # HTTP handlers (gin/echo/stdlib mux)
├── service.go         # Business logic
├── repository.go      # DB layer (if database detected)
└── handler_test.go    # stdlib testing + testify
```

Rules:
- Explicit error returns, never panic for business logic
- Use `context.Context` as first param in all functions
- DB: use `database/sql` + driver unless ORM detected in Key Libs
- Tests: `testing` + `testify/assert`

### Express / NestJS Projects

NestJS (if `@nestjs/core` in Key Libs):
```
src/{module}/
├── {module}.controller.ts  # @Controller
├── {module}.service.ts     # @Injectable
├── {module}.module.ts      # @Module
├── dto/create-{module}.dto.ts
└── {module}.spec.ts        # Jest
```

Express (otherwise):
```
src/routes/{module}.routes.ts
src/controllers/{module}.controller.ts
src/services/{module}.service.ts
src/{module}.test.ts
```

Rules:
- Full TypeScript types — no `any`
- NestJS: use `class-validator` decorators on DTOs
- Tests: Jest + Supertest

### Generic / Unknown Framework

When framework is "unknown":
- Use the detected language's idiomatic patterns
- Structure: `{module}.{ext}`, `test_{module}.{ext}`, `{module}/README.md`
- Note in assumptions: "Framework not detected — using generic patterns. Rerun with `@path/to/project` for framework-matched output."

---

## Convention Matching (Piece #5)

Use the `CONVENTIONS` section from the analyzer output:

- **Naming:** Apply exactly. If `snake_case functions` detected, every function uses snake_case.
- **Docstrings:** Match the detected style (Google, Sphinx, minimal). Never mix styles.
- **Type hints:** If `required`, every function has full type annotations. No exceptions.
- **Error handling style:** Match `custom_exceptions` → extend project's base exception. Match `try/except` → use standard try/except. Match `explicit error returns` (Go) → return `(value, error)` tuples.
- **Logging:** Import and use the detected logging library. Never introduce a new one.
- **Validation:** Use the detected validation library for all input validation.

---

## Dependency Awareness (Piece #4)

Use the `Key Libs` and detected versions from `CODEBASE CONTEXT`:

- Never generate code using a library NOT in Key Libs without noting it in assumptions.
- If adding a new dependency, state it explicitly: "**New dependency:** `{lib}=={version}` — add to requirements.txt/package.json"
- For version-sensitive APIs (Pydantic v1 vs v2, Django 3 vs 4), check version from context and match.
- Never assume latest version — match what's detected or state the assumption.

---

## Test Integration (Piece #6)

Use the `PATTERNS.Testing` and `STRUCTURE` from `CODEBASE CONTEXT`:

- **pytest detected:** Use `pytest` fixtures, `conftest.py` patterns. Import factories from detected fixture location.
- **jest detected:** Use `describe`/`it` blocks, `beforeEach`/`afterEach`. Match existing mock patterns.
- **stdlib testing (Go):** Use `TestXxx(t *testing.T)` format + `testify/assert`.
- **JUnit 5:** Use `@Test`, `@BeforeEach`, `@ExtendWith(SpringExtension.class)`.
- If `tests/conftest.py` detected, import fixtures from there — don't duplicate setup.
- Test file location: match detected `test_root` (tests/, test/, spec/, __tests__/).

Minimum tests generated:
1. Happy path — correct input → expected output
2. Edge case from assumptions block — error state, missing field, boundary

---

## Migration Generation (Piece #7)

When the feature adds or modifies database models:

**Django:** Always include migration note: "Run `python manage.py makemigrations {app} && python manage.py migrate`"

**Spring/Hibernate:** Include Flyway or Liquibase migration script if detected in Key Libs. Otherwise note: "Add `@Column` annotations. Schema auto-generated by Hibernate DDL if `spring.jpa.hibernate.ddl-auto=update`."

**Go (with migrations):** Check for `golang-migrate`, `goose`, or `tern` in go.mod. Generate `.sql` migration file if detected.

**Default:** Note in README: "Schema changes required — migration approach depends on your migration tool."

Never apply destructive migrations (DROP, RENAME) without a rerun hint asking for confirmation.

---

## API Consistency (Piece #8)

Match the detected API envelope style:

- **DRF detected:** Return `{"status": "ok", "data": {...}}` or DRF's default serializer format.
- **FastAPI detected:** Return Pydantic models directly (FastAPI handles serialization).
- **NestJS detected:** Return plain objects or use `@ApiResponse` decorators.
- **Go stdlib:** Return JSON with `json.Marshal`. Use consistent field naming (camelCase for JSON, snake_case for Go structs with `json:"field_name"` tags).
- **Express:** Return `res.json({success: true, data: {...}})`.

HTTP status codes: Use correct semantics. 201 for creation, 200 for reads, 204 for no-content deletes, 400 for bad input, 404 for not found, 409 for conflict.

---

## Documentation (Piece #9)

Match the detected docstring style from `CONVENTIONS`:

- **Google style:** `Args:`, `Returns:`, `Raises:` sections
- **Sphinx style:** `:param name:`, `:type name:`, `:returns:`, `:rtype:`
- **minimal:** One-line docstring only
- **TypeScript JSDoc:** `@param`, `@returns`, `@throws`
- **Go:** Package-level comment + function comments starting with function name

README structure:
1. One-paragraph description
2. Installation / dependencies
3. API reference (endpoints, events, schemas)
4. Usage example
5. Adaptation notes (what to change for different bus/framework)

---

## Deployment Context (Piece #10)

Use the `STRUCTURE.IaC/CI` from `CODEBASE CONTEXT`:

- **Docker detected:** Include Dockerfile (multi-stage) + docker-compose service entry
- **GitHub Actions detected:** Include `.github/workflows/{module}-test.yml`
- **Kubernetes detected:** Include Deployment + ConfigMap manifest
- **Terraform detected:** Note in README: "Add resource blocks to your .tf files — pattern from existing modules"
- **None detected:** Include basic Dockerfile only, note in rerun hints: "Add `include GitHub Actions` to get CI workflow"

---

## Internal Reasoning (not shown to user)

Before generating, resolve ambiguity internally:

**Interpret vocabulary precisely.** "throttle" = drop excess vs queue-and-delay vs reject. Pick most common. State the choice.

**Enumerate edge cases silently.** Empty payload, missing fields, clock skew, concurrent events, nulls, timeouts. Handle likely ones; note unhandled in rerun hints.

**Pick defensible defaults.** When user doesn't specify storage, algorithm, failure mode — pick what a senior engineer would defend in review. State the reasoning.

**One-shot means first response always has code.** Never "awaiting approval." If Claude wants to ask a clarifying question, pick the likely answer instead, state it as an assumption, ship.

---

## The Assumptions Block (mandatory, always first)

Every response starts with `## Assumptions`. Structure:

```
## Assumptions

**Interpretation:** I read "[phrase]" as "[specific meaning]".
Alternative: rerun with "[override phrase]" if you meant something else.

**Framework:** [detected/assumed] — generating [framework-specific files].
**Language:** [detected/assumed].
**Algorithm/Storage/Approach:** [chosen] because [one reason].

**New dependencies:** [list any new libs needed] — add to [requirements.txt/package.json/go.mod].

**Edge cases handled:** [list]
**Edge cases NOT handled:** rerun with "also handle [X]" to include.

**New events/endpoints proposed:** [list]
If you have a strict catalog, rerun with "use existing [X]" to constrain.
```

---

## Language Support

- **Python** — async, type hints, PEP 8, Black/Flake8 clean
- **Go** — goroutines, explicit error returns, gofmt
- **Rust** — async/await, strong typing, clippy compliant
- **TypeScript/JavaScript** — full TypeScript types, ESLint
- **Java** — Spring patterns, constructor injection, Bean Validation

Language detection: use `CODEBASE CONTEXT` if available. Fallback to user-specified ("in Go", "Rust sidecar"). Default: Python.

---

## Message Queue Support (v0.5.0+)

Generate MQ consumers for: Kafka, RabbitMQ, AWS SQS/SNS, GCP Pub/Sub, Azure Service Bus.

**Broker Detection (from prompt keywords):**
- Kafka / "kafka topic" / "consumer group" → Kafka
- RabbitMQ / AMQP / "queue" / "exchange" → RabbitMQ
- SQS / SNS / "Amazon queue" → AWS SQS/SNS
- Pub/Sub / GCP / "Google Cloud" → GCP Pub/Sub
- Service Bus / Azure → Azure Service Bus
- No broker named → RabbitMQ (default)

**Library Map (5 Languages × 5 Brokers):**

| Broker | Python | Go | Rust | TypeScript | Java |
|--------|--------|-----|------|------------|------|
| Kafka | `aiokafka` | `sarama` | `rdkafka` | `kafkajs` | `spring-kafka` |
| RabbitMQ | `aio-pika` | `amqp091-go` | `lapin` | `amqplib` | `spring-amqp` |
| AWS SQS | `boto3` | `aws-sdk-go-v2/sqs` | `aws-sdk-rust/sqs` | `@aws-sdk/client-sqs` | `aws-java-sdk-sqs` |
| GCP Pub/Sub | `google-cloud-pubsub` | `cloud.google.com/go/pubsub` | `google-cloud-pubsub` | `@google-cloud/pubsub` | `google-cloud-pubsub` |
| Azure Service Bus | `azure-servicebus` | `azure-sdk-for-go/servicebus` | `azure_messaging_servicebus` | `@azure/service-bus` | `azure-messaging-servicebus` |

**MQ Consumer always includes:**
- Message deserialization (JSON default; rerun with "use Avro/Protobuf")
- Ack/nack on success/failure
- Dead letter queue routing after max retries
- Graceful shutdown (signal handlers)
- Broker health check

**MQ Assumptions lines:**
```
**Broker:** [detected] — rerun with "Use Kafka instead" to override.
**Delivery guarantee:** at-least-once. Rerun with "exactly-once" for transactions.
**Consumer group:** [{feature}-group] — rerun with "use consumer group [name]".
**Offset strategy:** earliest (Kafka) / ack-on-success (RabbitMQ).
**Broker connection:** via env vars (BROKER_URL / KAFKA_BOOTSTRAP_SERVERS).
```

---

## Deployment & CI/CD Support (v0.3.0+)

Include on request:
- "Include Dockerfile" → multi-stage Dockerfile
- "Generate GitHub Actions workflow" → `.github/workflows/test.yml`
- "Add Kubernetes manifests" → Deployment + ConfigMap
- "Include Docker Compose" → local dev compose with broker services

---

## Deliverables (after assumptions block)

1. **Module file** — complete, copy-pasteable, linting compliant
2. **Test file** — minimum two tests (happy path + edge case)
3. **README.md** — description, API/events, install, usage, adaptation notes
4. **Install line** — one command
5. **Rerun hints** — how to override key decisions

---

## When to Refuse

**Multi-feature requests:** List the features, tell user to rerun with one.

**Cross-cutting / core changes:** "This requires modifying project core, not adding a sidecar."

**Not event-driven / feature-shaped:** "This plugin generates feature modules. [What they asked] needs [different approach]."

**Literally ambiguous ("add a feature"):** Ask for one sentence — trigger and outcome. Rerun framing, not conversation.

Refusals are complete responses. No dialogue.

---

## Response Template

**Standard flow (no harness flags):**
```
## Assumptions

[assumptions block — always first, never skip]

## Module: `{path}/{filename}.{ext}`

[complete module code]

## Tests: `{test_path}/test_{filename}.{ext}`

[complete test code]

## README: `{path}/README.md`

[complete README]

## Install

[one line]

## To iterate

If something is wrong, rerun with one of these additions:
- "In Rust" / "In Go" / "In TypeScript" — different language
- "Use X instead of Y" — algorithm or storage change
- "Also handle [edge case]" — adds error handling
- "Use existing event [X]" — match your catalog
- "Target [specific library]" — use particular SDK
- "Include Dockerfile" / "Add GitHub Actions" — deployment artifacts
- "Use Kafka instead of RabbitMQ" — swap broker
- "Use exactly-once delivery" — transactional MQ semantics
- "Use consumer group [name]" — specific consumer group
- "Add dead letter queue" — explicit DLQ routing
```

**Conditional flows (when harness flags provided):**

If `--preview` provided:
```
## Preview Outline

[file list, key decisions, est. integration time]

## Ready to Generate?

Run this again without --preview to commit to full generation:
  /one-shot-prompting:generate "[description]" "@/project"
```
→ STOP after preview (don't generate code)

If `--tdd` provided:
```
## Assumptions (with TDD note)
- Test-first mode: tests first, implementation after

## Test file (FAIL — run these tests as-is to verify they fail)
[complete test code with failing assertions]

## Module: `{path}/{filename}.{ext}`
[complete implementation code]

## Install + Verify
```

If `--review` provided:
```
## Assumptions (with Review Findings section)

If any findings:
- ⚠️ Lint: [list issues, recommended fix]
- 🚫 Security: [critical issues block generation]
- ⚠️ Performance: [warnings, not blockers]
- ⚠️ Type Coverage: [percentage, suggestions]
- 🟢 Tests: [coverage %]

[If critical findings block generation — show error and stop]
```

If `--strangler` provided:
```
## Legacy Migration Plan

[router code, adapter code, dual-run example, parity test, cutover plan, rollback script]

## Alongside Current System
[integration with existing legacy code]
```

If `--catalog` provided:
```
## Event Validation Results

[catalog events vs. generated events]
- ✅ Matched events
- ⚠️ New events (catalog extension needed)
- ❌ Conflicting events (must resolve)
```

Keep prose between sections minimal. User wants code and iteration info.

---

## Optional Harness Modules (v0.7.0 → v1.4.1)

These modules ship as standalone Python scripts under `scripts/`. They are
invoked through user flags or directly by the user; the skill should mention
the relevant flag in the Assumptions block whenever the user opts in.

| Flag / command | Module | Purpose |
|---|---|---|
| `--detect-bus` | `detect_message_bus.py` | Auto-detect message bus + async runtime from project source + manifests. |
| `--catalog <file>` | `event_catalog.py` | Validate emitted events against the project's canonical catalog (YAML/JSON/Markdown). |
| `--observability <domain>` | `domain_observability.py` | Emit a domain-tuned observability block (games / bots / ml / trading / generic). |
| `--preview` | `preview_mode.py` | Show a structured outline (file list + key decisions + integration time) before committing to full generation. |
| `--review` | `code_review_automation.py` | Run lint / security / performance / type-coverage / test-coverage gates and block on hardcoded secrets / SQL injection / `shell=True`. |
| `--tdd` (optional `--explain-tdd`) | `tdd_mode.py` | Emit failing tests first, implementation after; optional walkthrough explaining each test. |
| `--debug "<error>"` | `debugging_helpers.py` | Pattern-match an error and return ranked fixes + repro snippet. |
| `--architecture "<problem>"` | `architecture_design.py` | Lightweight blueprint (services, events, file structure, ready-to-generate command). |
| `--pr` | `pr_integration.py` | Build a GitHub/GitLab PR title + body + commands for the generated feature. |
| `--debug-prod` | `production_debugger.py` | Incident response with severity, hypothesis, repro, hotfix, permanent fix, monitoring additions, rollback. |
| `--budget <tokens>` / `--usage` | `cost_management.py` | Set monthly token budget; record + report usage; surface optimization hints. |
| `--strangler` | `strangler_pattern.py` | Generate router / adapter / dual-run / parity-test / rollback / cutover-plan for legacy migration. |
| `--check-consistency` / `--standardize` | `consistency_checker.py` | Scan project for inconsistent serializer / logger / error-handling choices and propose a shared library. |

When a flag is set, surface the module's output in its own section after
the main code, and list any blocking findings in the Assumptions block.

---

## Context Engineering Harness

**Phase Status** (Updated 2026-05-16):
- ✅ **Phase 0-3**: 69 modules shipped (v2.0.0) — All working
  - Phase 0: Silent planning, verification harness, slash commands
  - Phase 1: Multi-file formatting, auto-wiring, migrations, DI, config
  - Phase 2: REST APIs (CRUD, auth, webhooks, tests)
  - Phase 3: Batch jobs (queues, retries, monitoring)
- ❌ **Phase 4-5**: 110 module stubs (not implemented) — See `docs/phase-status.md`
  - Phase 4 planned: DDD, CQRS, Event Sourcing, TDD, cost, compliance
  - Phase 5 planned: Microservices, real-time, GraphQL, ML, legacy

**For Developers**:
- Read: `docs/skill-authoring.md` (how to edit SKILL.md)
- Test: `bash .claude/scripts/smoke-test.sh`
- Validate: `/skill-validator "skills/one-shot-generator/SKILL.md"`
- Check beads: `.beads/status.jsonl` (active work tracking)
