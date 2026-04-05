# Agent Harness — Knowledge Base Index

> Personal wiki on agent harnesses: the infrastructure that makes LLMs useful for complex, long-horizon tasks.
> LLM-maintained. See `CLAUDE.md` for operating instructions.

---

## Foundations

- [[agent-harness]] — What a harness is, why it exists, core components, and the orchestrator/framework distinction
- [[harness-patterns]] — 8 reusable engineering patterns (build-verify loop, context injection, loop detection, reasoning sandwich, hierarchical memory, permission prediction, filesystem-as-working-memory, subagent specialization)

## Core Mechanisms

- [[context-management]] — Strategies for handling context window pressure: offloading, summarization, hierarchical loading, escalating compression
- [[permission-system]] — How tool access is gated: per-tool classes, allow-listing, 3-stage approval, classifier-based auto-approval
- [[subagents]] — Delegation patterns: Fork/Teammate/Worktree, context isolation benefits, specialization

## Reference Implementations

- [[claude-code-harness]] — Anthropic's reference architecture: QueryEngine, Tool system, 3-layer memory, 5-level context compression, 26 hook events, Kairos background daemon
- [[frameworks]] — Ecosystem map: DeepAgents, LangGraph, MAF, CrewAI, Langroid — selection guide

---

## Raw Sources (`/raw`)

| File | Topic |
|------|-------|
| `parallel-ai-what-is-agent-harness.md` | Definition, components, operational flow |
| `wavespeed-claude-code-harness-architecture.md` | Claude Code leaked architecture analysis |
| `langchain-harness-engineering-blog.md` | Harness engineering patterns, LangChain bench results |
| `langchain-deepagents-context-management.md` | DeepAgents context management implementation |
| `frameworks-comparison-2026.md` | Market overview, framework comparison, stats |

---

## Open Questions / Gaps
- How does harness design interact with fine-tuning? (Karpathy hint: compile wiki → generate synthetic data → fine-tune → knowledge in weights)
- What does a production-grade `LoopDetectionMiddleware` actually look like in code?
- How does MAF compare to Claude Code at the permission-system level?
- What are the failure modes of the Fork subagent model vs. Worktree?
