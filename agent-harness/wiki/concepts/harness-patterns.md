# Harness Engineering Patterns

## Overview
Reusable patterns discovered through building and studying production agent harnesses. These are harness-level — they apply regardless of which model or framework you use.

---

## Pattern 1: Build-Verify Loop
**Problem**: Models naturally stop after generating an initial solution, even when it's wrong.

**Solution**: Structure the execution loop to enforce:
1. Plan → 2. Implement → 3. Verify → 4. Fix → repeat until verified

**Implementation**:
- `PreCompletionChecklistMiddleware`: intercepts before the agent marks a task done, forces verification steps
- System prompt: explicitly instruct the model to run tests/checks before declaring completion
- Tool: provide a "check my work" tool that runs tests and returns pass/fail

**Result**: LangChain saw 52.8% → 66.5% accuracy improvement purely from enforcing this pattern.

---

## Pattern 2: Context Injection at Startup
**Problem**: Agents don't know what tools/files/constraints are available, wasting early turns on discovery.

**Solution**: `LocalContextMiddleware` — inject a structured summary of the environment before the first model call:
- Directory structure (top 2-3 levels)
- Available tools and their capabilities
- Relevant constraints and evaluation criteria
- Time/token budget remaining

**Result**: Agent starts oriented instead of exploring blindly.

---

## Pattern 3: Loop Detection
**Problem**: Agents get stuck in doom loops — repeatedly applying the same broken fix, detecting the same error, applying the same fix...

**Solution**: `LoopDetectionMiddleware`:
- Track the last N file edit operations
- If the same file is edited with similar diffs repeatedly: interrupt and inject "You appear to be in a loop. Try a different approach."
- Optionally: escalate to human or spawn a fresh subagent with the problem framed differently

---

## Pattern 4: Reasoning Sandwich
**Problem**: Extended thinking models use reasoning budget uniformly, but planning and verification benefit most from deep reasoning while implementation is more mechanical.

**Solution**: Allocate reasoning budget non-uniformly:
- **Planning phase**: maximum reasoning (`thinking: {budget_tokens: max}`)
- **Implementation phase**: standard reasoning or none
- **Verification phase**: maximum reasoning

**Result**: Better plans + better verification without wasting budget on mechanical steps.

---

## Pattern 5: Hierarchical Memory
**Problem**: Loading all memory into every prompt is expensive and dilutes attention.

**Solution**: Three-tier loading (Claude Code architecture):
```
L1: Always loaded — tiny pointers only (~150 chars)
L2: On-demand — topic files, loaded when relevant
L3: Search-only — raw transcripts, queried not loaded
```

Agents treat memory as hints and verify against live state. Prevents stale memory from causing wrong actions.

---

## Pattern 6: Permission Prediction
**Problem**: High-security modes interrupt agents constantly for permission confirmation, breaking flow.

**Solution**: Secondary LLM classifier call that predicts whether the user would approve a given tool call given current context. If high confidence: auto-approve. If uncertain: interrupt.

This is distinct from the primary model — a small, fast classifier specifically trained/prompted for approval prediction.

---

## Pattern 7: Filesystem as Working Memory
**Problem**: Agents accumulate large artifacts (search results, generated files, code output) that overflow context.

**Solution**: Write everything to disk immediately. The context window holds only:
- Current task state
- Pointers to artifacts
- The last N tool results

Agents retrieve from disk when they need something again. The filesystem is the long-term memory; context is the short-term.

**Trigger heuristics**: offload tool outputs > 20K tokens; truncate older entries at 85% context capacity.

---

## Pattern 8: Subagent Specialization
**Problem**: General-purpose agents are mediocre at everything.

**Solution**: Define specialized subagent types with:
- Custom system prompt for the specific task type
- Restricted tool set (only what's needed)
- Scoped task description

Examples: `Explore` (read-only research), `Plan` (architecture only), `Test-Runner` (run tests, report), `Simplify` (code review only).

The orchestrator routes tasks to specialists rather than doing everything inline.

---

## Anti-Patterns

| Anti-Pattern | Why It Fails |
|---|---|
| Load all memory always | Dilutes attention, inflates token cost |
| Single agent for everything | Context overflow, no specialization |
| Verify nothing | Agent ships broken work confidently |
| Ignore loop detection | Agents burn budget going nowhere |
| Hard-code behavior in code | Can't iterate without deploy |

## See Also
- [[agent-harness]] — what a harness is
- [[context-management]] — patterns 5 and 7 in depth
- [[subagents]] — pattern 8 in depth
- [[claude-code-harness]] — where patterns 1, 5, 6 come from
- [[frameworks]] — which frameworks implement these patterns
