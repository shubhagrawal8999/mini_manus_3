# Persistent-Learning AI Agent System Design (DeepSeek + OpenAI)

This guide describes a production-style architecture for an AI agent that:

- Remembers users across sessions (persistent memory)
- Uses **OpenAI** and **DeepSeek** APIs together
- Executes automated actions (e.g., posting to Telegram/LinkedIn/Email)
- Learns from mistakes through feedback loops and repair pipelines
- Validates code before execution
- Deploys on **Railway free tier**
- Stays modular for future expansion **بسهولة**


## Implementation Status (What is now in this repo)

This repository now includes a working starter scaffold with:

- Provider abstraction and router for OpenAI + DeepSeek (`src/agent/providers`, `src/agent/core/router.py`)
- Persistent memory store using SQLite with vector-like retrieval (`src/agent/memory/store.py`)
- Orchestrator with automated posting workflow + feedback learning (`src/agent/core/orchestrator.py`)
- Validation pipeline for payload and generated Python code checks (`src/agent/validation/pipeline.py`)
- Deployment starter files for Railway (`Dockerfile`, `railway.toml`, `.env.example`)
- Unit tests for routing, memory retrieval, posting flow, and failure learning (`tests/`)

### Quick run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m agent.app
python -m pytest -q
```

---

---

## 1) Product Goals and Non-Goals

### Goals

1. **Persistent personalization**: user preferences, history, tone, constraints.
2. **Hybrid intelligence**: route prompts to OpenAI/DeepSeek by cost, latency, or task complexity.
3. **Reliable execution**: agent can run actions, detect failures, retry, and report outcomes.
4. **Continuous improvement**: each failure creates learning artifacts and better next-run behavior.
5. **Safe operations**: policy checks, credential isolation, audit logs.

### Non-Goals (V1)

- Fully autonomous unrestricted internet behavior
- High-frequency real-time streaming at enterprise scale
- Multi-region disaster recovery

---

## 2) High-Level Architecture

## 2.1 Core Services

1. **API Gateway**
   - Receives user input (Telegram webhook / web app / REST).
   - Authenticates request and assigns `conversation_id`, `user_id`, and trace ID.

2. **Orchestrator (Brain)**
   - Builds context from short-term memory + retrieved long-term memory.
   - Decides: reason-only, tool-use, post-content, deep research, etc.
   - Chooses model provider (OpenAI or DeepSeek) using routing policy.

3. **Model Router**
   - Task classifier: easy/medium/hard + tool requirement.
   - Cost/latency-aware provider selection:
     - OpenAI for high reliability + tool-calling strictness.
     - DeepSeek for long reasoning chains or lower-cost exploration.

4. **Memory Layer**
   - **Short-term memory**: current thread context + recent summaries.
   - **Long-term memory**: vectorized user preferences, mistakes, successful templates, and action outcomes.

5. **Tool Execution Layer**
   - Adapters for Telegram/LinkedIn/Email/Sheets/web research.
   - Strong schema validation before execution.
   - Idempotency keys for safe retries.

6. **Learning & Feedback Engine**
   - Captures errors, user ratings, and corrections.
   - Converts outcomes into memory updates + prompt policy updates.

7. **Validation Pipeline**
   - Static checks, unit tests, sandbox execution, cross-model verification.
   - Blocks unsafe or broken code/actions.

8. **Observability Stack**
   - Structured logs, traces, metrics, alert rules.
   - Root-cause summaries written back to memory.

## 2.2 Data Stores (Free-Tier Friendly)

- **PostgreSQL (Railway plugin)**: canonical data (users, tasks, events, feedback, retries).
- **pgvector** in PostgreSQL: vector similarity search for long-term memory.
- **Redis (optional)**: queues/caching/rate-limits (can start with DB-only queue for free tier).
- **Object storage (optional)**: artifacts (screenshots, reports).

---

## 3) Memory Design

## 3.1 Memory Types

1. **Ephemeral / Short-Term**
   - Last N turns + session summary
   - Tool call context
   - Active goals/checklist

2. **Long-Term Semantic Memory**
   - User preferences (tone, format, language, posting style)
   - Stable facts (timezone, typical channels, brand rules)
   - Learned patterns (what succeeded/failed)

3. **Procedural Memory**
   - Action templates (e.g., "LinkedIn post workflow")
   - Recovery playbooks for known failures

4. **Episodic Memory**
   - Timestamped interaction summaries
   - Outcome + confidence + user satisfaction

## 3.2 Suggested Schema (Postgres)

- `users(id, handle, locale, timezone, created_at)`
- `conversations(id, user_id, channel, started_at, status)`
- `messages(id, conv_id, role, content, tokens, created_at)`
- `memories(id, user_id, type, text, embedding, salience, source_event_id, created_at, updated_at)`
- `tasks(id, user_id, type, input_json, status, attempt, created_at, updated_at)`
- `task_events(id, task_id, phase, payload_json, success, error_code, created_at)`
- `feedback(id, user_id, task_id, rating, correction_text, created_at)`
- `model_runs(id, task_id, provider, model, prompt_hash, latency_ms, cost_estimate, success, created_at)`

## 3.3 Retrieval Strategy

Use **hybrid retrieval**:

1. Filter by `user_id`, `type`, and recency.
2. Vector search top-K with pgvector cosine similarity.
3. Re-rank by salience + recency + success score.
4. Compose final context bundle with token budget.

Scoring example:

```text
final_score = 0.50 * semantic_similarity
            + 0.25 * recency_decay
            + 0.15 * salience
            + 0.10 * success_rate_link
```

## 3.4 Memory Write Rules

Write memory only when one of these is true:

- User explicitly states preference ("Always keep posts concise")
- High-impact outcome (success/failure of automated action)
- Correction feedback from user
- Novel reusable procedure discovered

Store every memory with:

- Confidence (`0..1`)
- Scope (`global/user/task-specific`)
- Expiration policy (none/30d/90d)

---

## 4) Dual-Provider Model Strategy (OpenAI + DeepSeek)

## 4.1 API Key Integration

Environment variables:

- `OPENAI_API_KEY`
- `DEEPSEEK_API_KEY`
- `MODEL_PRIMARY`
- `MODEL_FALLBACK`
- `ROUTER_POLICY` (`cost_first`, `quality_first`, `latency_first`)

## 4.2 Routing Logic

1. **Classify task**: chat, coding, research, posting, repair.
2. **Estimate complexity**: low/medium/high.
3. **Select provider**:
   - quality-critical + tool strictness → OpenAI
   - long reasoning / budget-sensitive → DeepSeek
4. **Cross-check mode** (optional): second model reviews plan/output.
5. **Fallback on failure**: switch provider + lower temperature + stricter schema.

## 4.3 Abstraction Interface (Python)

```python
class LLMProvider:
    def generate(self, messages, tools=None, temperature=0.2):
        raise NotImplementedError

class OpenAIProvider(LLMProvider):
    ...

class DeepSeekProvider(LLMProvider):
    ...

class ModelRouter:
    def run(self, task_ctx):
        provider = self.select_provider(task_ctx)
        return provider.generate(task_ctx.messages, tools=task_ctx.tools)
```

---

## 5) Learning from Errors (Continuous Improvement Loop)

## 5.1 Error Taxonomy

- **Planning errors**: wrong strategy
- **Tool errors**: API auth/format/rate-limit
- **Execution errors**: timeout/network
- **Memory errors**: wrong retrieval, stale preference
- **Safety errors**: policy violation

## 5.2 Feedback Loop Workflow

1. Detect failure and classify error.
2. Capture full context snapshot (inputs, memory slice, tool args, model response).
3. Generate root-cause explanation (RCA mini-report).
4. Suggest fix candidates (prompt fix, schema fix, retry policy, or code patch).
5. Apply selected fix in sandbox/test mode.
6. If pass, store as procedural memory + playbook.
7. Notify user with transparent summary.

## 5.3 Iterative Improvement Mechanisms

- **Automatic retries** with backoff and transformed payload.
- **Reflection step**: model critiques prior failed attempt before retry.
- **Policy update hooks**:
  - If repeated failure pattern > threshold, create engineering ticket.
  - Update routing preferences per task type.
- **Human-in-the-loop mode** for critical actions.

---

## 6) Code Validation & Cross-Verification Pipeline

Every generated script/action plan should pass:

1. **Schema Validation**
   - JSON schema for tool arguments.
2. **Static Checks**
   - Lint/type checks (ruff/mypy/tsc).
3. **Unit Tests**
   - Test expected behavior for generated logic.
4. **Sandbox Dry-Run**
   - Execute in isolated environment with mock credentials.
5. **Cross-Model Verification**
   - Secondary model reviews correctness, security, edge cases.
6. **Guardrails**
   - Deny risky operations unless explicitly approved by policy.

Promotion rule:

```text
Only execute live action when all required gates are GREEN.
```

---

## 7) Error Detection, Logging, and Self-Repair

## 7.1 Observability

Log each phase with structured fields:

- `trace_id`, `user_id`, `task_id`, `phase`, `provider`, `tool`, `latency_ms`, `status`, `error_code`

Emit metrics:

- success rate per tool
- retry count
- mean repair time
- hallucination/invalid-call incidents
- user satisfaction trend

## 7.2 Self-Repair Strategy

When error occurs:

1. **Identify**: parse stack/API code/log context.
2. **Explain**: concise user-facing cause + internal RCA.
3. **Suggest fixes**: ranked by likelihood and impact.
4. **Apply safe fix**: only low-risk auto-fixes in V1.
5. **Verify**: rerun tests + dry-run.
6. **Learn**: save "error → fix" mapping in procedural memory.

Pseudo-policy:

```text
if error in known_playbook and risk == low:
    auto_fix_and_retry()
else:
    request_confirmation_or_handoff()
```

---

## 8) Example End-to-End Workflows

## 8.1 Memory Storage Example

1. User says: "I prefer short LinkedIn posts with a friendly tone."
2. Agent extracts preference tuple.
3. Generates embedding and stores as long-term memory.
4. Updates salience because explicit preference.

## 8.2 Memory Retrieval Example

1. New post request arrives.
2. Retrieve top memories (`tone`, `length`, prior successful post structure).
3. Inject compact memory summary into prompt.
4. Generate draft + user-specific style.

## 8.3 Automated Posting Example

1. User asks: "Post this on LinkedIn and send summary to Telegram."
2. Planner builds two-step workflow.
3. Validator checks payload schema and auth availability.
4. Execute LinkedIn post adapter.
5. On success, execute Telegram notifier.
6. Log outcome and persist episodic memory.

## 8.4 Failure + Recovery Example

1. LinkedIn API returns 429.
2. Error engine classifies as rate-limit.
3. Apply retry with jitter + schedule delayed attempt.
4. Notify user of delay and expected retry time.
5. Save rate-limit playbook event for future routing.

---

## 9) Implementation Blueprint (Monorepo)

```text
/agent-core
  /orchestrator
  /router
  /memory
  /validators
  /repair
/tool-adapters
  /telegram
  /linkedin
  /email
  /sheets
/services
  /api
  /worker
  /scheduler
/infrastructure
  railway.toml
  Dockerfile
  docker-compose.dev.yml
/tests
  /unit
  /integration
```

Recommended stack:

- **Backend**: Python (FastAPI + Pydantic + SQLAlchemy)
- **Queue**: Celery/RQ (or DB-backed queue on free tier)
- **DB**: Postgres + pgvector
- **Migrations**: Alembic
- **Testing**: pytest + coverage + hypothesis (optional)
- **Observability**: OpenTelemetry + structured JSON logs

---

## 10) Railway Free-Tier Deployment Guide

> Note: free tiers change over time. Validate current limits before production usage.

## 10.1 Prepare Project

1. Add `Dockerfile` for API service.
2. Add `Procfile` or Railway start command.
3. Ensure health endpoint `/healthz`.
4. Add `.env.example` with required keys.

## 10.2 Provision Services on Railway

1. Create new Railway project.
2. Add **PostgreSQL plugin**.
3. Deploy API service from GitHub repo.
4. (Optional) Add worker service for async jobs.

## 10.3 Configure Environment Variables

- `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`
- `DATABASE_URL`
- `APP_ENV=production`
- `LOG_LEVEL=info`
- `TELEGRAM_BOT_TOKEN`, `LINKEDIN_CLIENT_ID`, `LINKEDIN_CLIENT_SECRET`

## 10.4 Deploy Steps

1. Push code to main branch.
2. Railway auto-builds container.
3. Run migrations on release (`alembic upgrade head`).
4. Verify `/healthz`, then test a dry-run task.

## 10.5 Free-Tier Optimization

- Use one small service for API + lightweight worker initially.
- Keep embeddings compact and prune low-salience memories.
- Batch writes to reduce DB connections.
- Enable queue throttling for API quota protection.

---

## 11) Security and Governance

- Store secrets only in Railway environment variables.
- Encrypt sensitive memory fields where needed.
- Add role-based access for admin/debug endpoints.
- Keep immutable audit logs for automated actions.
- Add policy layer for disallowed content/actions.

---

## 12) Scalability and Extensibility Roadmap

## Phase 1 (MVP)

- Single-tenant memory
- Telegram + one posting adapter
- Hybrid model routing + fallback

## Phase 2

- Multi-tenant isolation
- Advanced evaluator model
- Better tool marketplace and plugin SDK

## Phase 3

- Active learning dashboards
- Offline reinforcement from accepted/rejected outputs
- Cost-aware auto-routing with SLA controls

Extensibility principles:

1. **Adapter pattern** for tools and model providers.
2. **Event-driven architecture** for new capabilities.
3. **Versioned memory schemas** for painless migrations.
4. **Policy-as-code** for controllable autonomy.

---

## 13) Minimal Execution Policies (Recommended Defaults)

- Never execute external posting without explicit user intent record.
- Require dry-run for newly generated code paths.
- Require at least one verification layer for high-impact actions.
- If confidence is low and risk high, ask for confirmation.

---

## 14) Success Metrics (What to Measure)

- Task completion rate
- First-pass success rate
- Mean retries per task
- Memory hit rate (retrieval usefulness)
- User correction frequency (should drop over time)
- Cost per successful task

---

## 15) Quick Start Checklist

- [ ] Create Postgres + pgvector schema
- [ ] Implement provider abstraction for OpenAI + DeepSeek
- [ ] Add router policy + fallback
- [ ] Add memory write/read service
- [ ] Add at least one tool adapter (Telegram)
- [ ] Add validation pipeline gates
- [ ] Add structured logging and RCA generation
- [ ] Deploy API + DB on Railway
- [ ] Run end-to-end dry-run workflow

This design provides a stable base for a Manus/OpenClaw-like assistant that learns persistently, executes safely, and improves over time.
