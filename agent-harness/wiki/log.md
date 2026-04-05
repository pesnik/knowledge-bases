# Agent Harness Wiki — Ingest & Query Log

---

## 2026-04-05 — Initial Compilation

**Ingested:**
- `parallel-ai-what-is-agent-harness.md` — foundational definition, components, operational flow
- `wavespeed-claude-code-harness-architecture.md` — Claude Code architecture from leaked source analysis
- `langchain-harness-engineering-blog.md` — harness engineering patterns, 52.8%→66.5% bench result
- `langchain-deepagents-context-management.md` — DeepAgents context offloading + summarization implementation
- `frameworks-comparison-2026.md` — ecosystem overview, 327% multi-agent growth stat, framework selection

**Compiled:**
- `wiki/concepts/agent-harness.md` — synthesized definition + component taxonomy
- `wiki/concepts/claude-code-harness.md` — reference implementation deep-dive
- `wiki/concepts/context-management.md` — full strategy taxonomy with implementation heuristics
- `wiki/concepts/subagents.md` — Fork/Teammate/Worktree + specialization principles
- `wiki/concepts/harness-patterns.md` — 8 engineering patterns with implementations
- `wiki/concepts/permission-system.md` — 3-stage approval, classifier-based auto, read/write concurrency
- `wiki/concepts/frameworks.md` — ecosystem map + selection guide

**Word count:** ~5,200 words across 7 concept articles

**Key insight filed:** The harness makes or breaks an AI product — identical models diverge dramatically based on harness quality. LangChain proved this empirically: 52.8%→66.5% without touching the model.

---

## Open (next ingest targets)
- Karpathy's llm-wiki gist (gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — for the schema/prompt patterns
- LangGraph state management deep-dive
- MAF (Microsoft Agent Framework) architecture post-merger docs
- Papers: "Agent Bench", "SWE-bench" — harness evaluation methodology
