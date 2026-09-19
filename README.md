# Mini Manus 3

> Architecture and implementation planning for a persistent-learning AI agent with model routing, long-term memory, validation, feedback loops, and self-repair.

## Why this exists

Mini Manus 3 represents the point where I stopped thinking only about individual tools and started thinking about the architecture of an agent platform.

The central question became:

**How do you make an AI agent persistent, reliable, observable, and capable of improving from failures?**

This repository captures the architecture designed around that question.

## Core design

~~~text
User Request
    │
    ▼
API Gateway
    │
    ▼
Orchestrator
    │
    ├── Model Router
    ├── Memory
    ├── Tool Execution
    ├── Validation
    └── Feedback / Repair
            │
            ▼
        Observability
~~~

## Major components

### Model Router

Selects between OpenAI and DeepSeek based on task characteristics such as complexity, reliability needs, and cost.

### Memory

The design separates short-term context, semantic long-term memory, procedural memory, and episodic history. The proposed storage layer uses PostgreSQL with pgvector.

### Tool execution

External actions are isolated behind adapters for services such as Telegram, LinkedIn, email, Sheets, and research.

### Validation pipeline

Generated actions should pass through schema validation, static checks, tests, sandbox execution, optional cross-model verification, and policy checks before live execution.

### Learning and repair

~~~text
Failure
  ↓
Classify
  ↓
Explain
  ↓
Suggest repair
  ↓
Verify
  ↓
Store successful repair
  ↓
Improve future execution
~~~

## Why this project matters

This is the architecture work behind my AI-agent experiments.

It helped me separate two questions:

**Can an LLM perform a task?**

and

**Can a software system reliably operate an LLM as part of a larger workflow?**

The second question is much harder.

## Key design principles

- explicit state
- modular tool adapters
- persistent memory
- safe retries
- policy-as-code
- structured observability
- human approval for high-impact actions

## Status

🧭 Architecture / design-stage project

This repository is primarily a system-design experiment and blueprint for future agent implementations.
