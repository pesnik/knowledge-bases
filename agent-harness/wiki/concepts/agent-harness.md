# Agent Harness

## Definition
The software infrastructure surrounding an LLM that manages everything except the model itself. The harness handles the complete lifecycle of a task: intent capture → planning → tool execution → verification → memory persistence.

The defining insight: **the model provides intelligence; the harness provides agency.** Two systems using identical models can perform dramatically differently based solely on harness quality.

## Why Harnesses Exist
LLMs are stateless inference engines with finite context windows. They cannot, on their own:
- Remember anything across sessions
- Execute actions in external systems
- Verify their own outputs
- Decompose long-horizon tasks without losing track

A harness solves each of these gaps without changing the model's weights.

## Core Components

| Component | Function |
|-----------|----------|
| **Tool Layer** | Connects model outputs to real actions (bash, file ops, APIs, web search) |
| **Memory System** | Manages working context, session state, long-term knowledge |
| **Context Engine** | Decides what to include in each LLM call — retrieval, reduction, compaction |
| **Planner** | Decomposes tasks into trackable steps |
| **Verifier** | Checks outputs; implements build→test→fix cycles |
| **Permission System** | Gates which tools can run when |
| **Orchestrator** | Controls the overall agent loop and subagent coordination |

## How It Operates

```
User intent
    ↓
Decompose → subtasks
    ↓
For each subtask:
  Compile context → LLM call → parse output
  If tool call: execute → feed result back
  If done: verify output → fix if wrong
    ↓
Persist artifacts, update memory
    ↓
Handoff for next session
```

## Harness vs. Orchestrator vs. Framework
- **Framework** (LangChain, LlamaIndex): building blocks, no opinionated runtime
- **Orchestrator**: the brain — controls *when* and *how* the model is invoked
- **Harness**: complete runtime system — includes orchestrator plus all infrastructure
- An orchestrator is a component inside a harness; a harness uses a framework to implement itself

## Performance Impact
LangChain improved a coding agent from 52.8% → 66.5% on Terminal Bench 2.0 **without changing the underlying model** — purely via harness improvements.

Token efficiency: well-designed harnesses achieve 10-100x token reduction through structured context management.

## See Also
- [[context-management]] — how harnesses handle context window pressure
- [[permission-system]] — how tool access is gated
- [[subagents]] — harness-level delegation patterns
- [[harness-patterns]] — reusable engineering patterns
- [[claude-code-harness]] — reference implementation
- [[frameworks]] — ecosystem of frameworks and harnesses
