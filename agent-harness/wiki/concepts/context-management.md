# Context Management

## The Problem
Every LLM call compiles a fixed-size prompt. Long-running agents accumulate:
- Large tool outputs (search results, file reads, code output)
- Redundant conversation history
- Repeated file operation entries
- Planning state that no longer needs to be explicit

Without management: agents hit context limits, fail mid-task, or hallucinate from diluted attention.

## Taxonomy of Strategies

### 1. Offloading (hot-swap to filesystem)
**Tool output offloading**
- Trigger: tool response > N tokens (DeepAgents default: 20,000)
- Action: write full response to disk, substitute with `<file_path> + first 10 lines preview`
- Agent retrieves full content with a file read when needed

**Tool input truncation**
- Trigger: context reaches threshold % (DeepAgents: 85%)
- Action: replace older tool call entries with pointers to files on disk
- Older turns become "lazy" references

Benefit: agent never loses access to data — it just doesn't pay attention cost to hold it.

### 2. Summarization
**In-context summary** (LLM-generated):
- Replaces full conversation history with structured summary: session intent, artifacts created, next steps
- Produced by a separate LLM call or inline
- Risks: goal drift, loss of nuance

**Filesystem preservation**:
- Original conversation written to disk as canonical record
- Summary is lossy; the canonical record is not
- Recovery path if summary is inadequate

### 3. Hierarchical Loading (Claude Code pattern)
Never load everything at once. Three-tier system:
1. Always-loaded: tiny pointers (MEMORY.md, ~150 chars per entry)
2. On-demand: topic files loaded when relevant
3. Search-only: raw transcripts, never wholesale loaded

Agents query L3 explicitly rather than having it pollute context.

### 4. Session Chunking
- Break long tasks into sessions with explicit handoff artifacts
- Each session starts fresh with a compact state summary
- State persists as files, not as in-context text
- Claude Code: JSONL session files + `--continue`/`--resume`

### 5. Escalating Compression (Claude Code's 5-level system)
Applied in order when context pressure increases:
1. Clear old tool results (keep reasoning, drop outputs)
2. Summarize conversation history
3. Extract key facts to memory files (session → L2)
4. Full history summarization
5. Oldest-message truncation

## Key Failure Mode: Goal Drift
After aggressive summarization, agents can drift from the original intent. Mitigation:
- Always include original task spec in always-loaded context (never summarize away)
- Monitor for goal drift explicitly in evaluations
- The "session intent" field in summaries must be protected

## Implementation Rule of Thumb
```
Token budget per call:
  ~20% system prompt + schema
  ~30% task context (always-on)
  ~30% recent tool results (rolling window)
  ~20% reserve for model output
```

Anything exceeding the rolling window gets offloaded to disk.

## See Also
- [[agent-harness]] — harness fundamentals
- [[claude-code-harness]] — 5-level escalating compression
- [[subagents]] — context isolation via subagent delegation
- [[harness-patterns]] — build-verify loop, context injection
