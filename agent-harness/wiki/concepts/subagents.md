# Subagents

## Definition
A subagent is a delegated LLM invocation with its own isolated context, specific tool access, and independent execution environment. The orchestrating agent spawns a subagent, hands it a scoped task, and receives only the output — not the intermediate reasoning or tool calls.

Core value: **context isolation**. Risky, exploratory, or parallelizable work can proceed without contaminating the orchestrator's state.

## Why Subagents Matter
Without subagents, a single agent:
- Accumulates all tool outputs in one context (fast path to context overflow)
- Cannot parallelize independent work
- Cannot isolate risky operations (a bad bash command pollutes the entire session)
- Has no modularity — different task types compete in the same prompt

## Subagent Patterns (Claude Code Taxonomy)

### Fork
- Mechanism: byte-identical copy of parent context
- Benefit: full prompt cache hit on the shared prefix → cheap to spawn
- Use case: parallel tasks that need the same background knowledge
- Example: "research X and Y simultaneously, then combine"

### Teammate
- Mechanism: separate tmux/iTerm pane with file-based mailbox communication
- Benefit: truly independent execution, survives parent context compaction
- Communication: write instructions to `mailbox_in.md`, read responses from `mailbox_out.md`
- Use case: long-running parallel workstreams, separate concerns (e.g., one agent codes, one reviews)

### Worktree
- Mechanism: isolated git branch + worktree on disk
- Benefit: risky/exploratory changes can be discarded without affecting main codebase
- Use case: "try this refactor and tell me if it works" — discard if it doesn't
- The subagent's entire filesystem state is isolated

## DeepAgents Subagent Middleware
LangChain's implementation wraps standard LangGraph agents:
- Parent registers available subagent types with capability descriptions
- Subagent middleware intercepts when parent decides to delegate
- Subagent runs with isolated context window
- Returns structured output to parent

## Design Principles

**Return only output, not process.** Subagents should summarize their work, not replay their entire tool call history. The orchestrator needs the result, not the journey.

**Scope carefully.** A subagent given too broad a task just becomes another orchestrator. Delegation should be to a clearly bounded, completable subtask.

**Specialize.** Subagents with custom system prompts (Explorer, Plan, Test-Runner, etc.) outperform generic agents given the same task. The system prompt shapes behavior for the specific task type.

**Isolation is the point.** If you're not isolating context, you might as well just call the model directly.

## Context Budget Benefit
Spawning a subagent for a large tool call:
- Parent context stays compact (just the result, not the process)
- Subagent's large intermediate context is discarded after completion
- Net effect: parent handles 10× more work before hitting context limits

## See Also
- [[agent-harness]] — harness fundamentals
- [[claude-code-harness]] — Fork/Teammate/Worktree implementations
- [[context-management]] — why isolation helps with context
- [[harness-patterns]] — patterns that use subagents
- [[frameworks]] — which frameworks support subagent delegation
