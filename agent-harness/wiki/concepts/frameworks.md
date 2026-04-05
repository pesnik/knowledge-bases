# Agent Frameworks & Harnesses (Ecosystem Map)

## Conceptual Distinction First
- **Framework**: building blocks (routers, memory primitives, tool connectors) — LangChain, LlamaIndex
- **Harness**: complete runtime with opinionated execution environment — Claude Code, DeepAgents
- Harnesses are typically built on top of frameworks, or build-from-scratch

---

## Production Harnesses

### Claude Code (Anthropic)
- Type: Harness (production, closed-source)
- Stack: TypeScript + Rust (rewrite in progress as of 2025)
- Strength: the reference architecture; most studied; most capable
- Tool count: ~40
- Subagent models: Fork / Teammate / Worktree
- Use case: software engineering, agentic coding

### DeepAgents (LangChain)
- Type: Batteries-included harness
- Stack: LangGraph + Python
- Strength: open-source, LangChain ecosystem integration, quick to start
- Default middleware: planner + filesystem + subagents
- Context mgmt: offloading (20K token threshold), summarization
- Use case: general-purpose long-horizon tasks, research, coding

---

## Frameworks (Build Your Own Harness)

### LangGraph
- Type: Framework (graph-based agent orchestration)
- Strength: most stable; state management is first-class; explicit node/edge graph
- State flows cleanly through typed state objects — each node reads/writes well-defined fields
- Use case: when you want fine-grained control; production agents with explicit control flow

### LangChain (original)
- Type: Framework (chains + agent primitives)
- Strength: huge ecosystem, connectors for everything
- Weakness: can be overengineered for simple cases
- Relationship: LangGraph is the evolution; DeepAgents builds on LangGraph

### LlamaIndex
- Type: Framework (RAG + agent primitives)
- Strength: data ingestion, RAG pipelines, structured data agents
- Use case: knowledge retrieval-heavy agents

---

## Enterprise Platforms

### Microsoft Agent Framework (MAF)
- Formed: Late 2025 (AutoGen + Semantic Kernel merger)
- Type: Enterprise framework/harness
- Strength: Azure integration, enterprise compliance, .NET + Python
- Use case: large-scale enterprise multi-agent deployments

### CrewAI
- Type: Role-based multi-agent framework
- Model: each agent has Role + Goal + Backstory + Tools
- Strength: intuitive role assignment, good for structured team workflows
- Weakness: less flexible than graph-based approaches

### Langroid
- Type: Lightweight multi-agent framework
- Model: task-based with message passing
- Strength: simpler than LangChain, more opinionated than raw API
- Language: Python

---

## Ecosystem Statistics (Databricks, Oct 2025)
- Multi-agent workflow adoption grew **327%** in 4 months (Jun–Oct 2025)
- Tech companies build multi-agent systems at **4×** the rate of other industries
- Dominant pattern shift: single agent → multi-agent with specialization

## Selection Guide

```
Need a reference architecture to study?       → Claude Code
Need a working harness now, open-source?       → DeepAgents
Need fine-grained control over agent flow?     → LangGraph
Need RAG + agents together?                    → LlamaIndex
Enterprise + Azure?                            → MAF
Role-based team metaphor?                      → CrewAI
Lightweight message-passing?                   → Langroid
```

## See Also
- [[agent-harness]] — what a harness is vs. framework
- [[claude-code-harness]] — reference harness deep-dive
- [[subagents]] — multi-agent coordination patterns
- [[harness-patterns]] — patterns applicable across all frameworks
