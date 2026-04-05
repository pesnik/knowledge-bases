# Claude Code Harness

## Overview
Anthropic's Claude Code is the most-studied reference harness in the field. Its architecture was briefly exposed via leaked source, providing the clearest public view of a production-grade agentic harness. The patterns are widely referenced regardless of implementation.

## Architecture Layers

### 1. Orchestration Loop — `QueryEngine.ts` (~46k lines)
Central coordinator. Manages:
- All LLM API calls + streaming
- Prompt construction per-call
- Token counting and cost tracking
- Prompt caching optimization
- Retry logic

**Key design decision**: behavioral coordination defined in natural language in the system prompt, not as hardcoded branching logic. This means behavior can be iterated without code redeployment.

### 2. Tool System — `Tool.ts` (~29k lines)
~40 discrete capabilities, each independently permission-gated:
- File ops: Read, Write, Edit, Glob, Grep
- Execution: Bash
- Web: WebSearch, WebFetch
- IDE: LSP integration
- Meta: Agent (spawn subagent), Task management

**Read-only operations** run concurrently. **Mutating operations** run serially to prevent state conflicts.

### 3. Three-Layer Memory

| Layer | Contents | Loading |
|-------|----------|---------|
| L1 | MEMORY.md — pointers (~150 chars each) | Always in context |
| L2 | Topic files — detailed notes per concept | On-demand |
| L3 | Raw session transcripts | Search-only, never loaded wholesale |

Design principle: **memory as hints, not truth**. Agents verify against live state before acting on remembered facts.

Sessions persist as JSONL. Resumable with `--continue`/`--resume`.

### 4. Permission System
Three-stage approval:
1. Trust establishment at project load (reads CLAUDE.md, checks allowed tools)
2. Permission check before each tool execution
3. Explicit user confirmation for high-risk ops

**Auto mode innovation**: separate LLM classifier call predicts user approval probability before execution — avoids unnecessary interruptions while maintaining safety.

### 5. Context Pressure Management (5 strategies, escalating)
1. Time-based clearing of old tool results
2. Conversation summarization
3. Session memory extraction → L2 files
4. Full history summarization
5. Oldest-message truncation (last resort)

### 6. Subagent Execution Models

| Model | Mechanism | Use Case |
|-------|-----------|----------|
| **Fork** | Byte-identical context copy; leverages prompt cache | Parallel tasks with shared context |
| **Teammate** | tmux/iTerm pane + file-based mailbox | Loose coordination, separate workstreams |
| **Worktree** | Isolated git branch/worktree | Risky/exploratory work, can be discarded |

All subagents return only output to orchestrator — contamination-free.

### 7. Hook System (26 events)
Full lifecycle observability: SessionStart → UserPromptSubmit → PreToolUse → PostToolUse → SubagentStart/Stop → PreCompact/PostCompact → SessionEnd + 18 more.

Hooks execute shell commands at each event — enables external automation, logging, enforcement.

## Unreleased: Kairos / autoDream
Feature-flagged background daemon. Runs during user idle time:
- Merges observations across sessions
- Resolves logical contradictions in memory
- Consolidates notes
- Runs in subprocess to isolate from main context

This is the "continuous learning" layer — the wiki that improves itself while you sleep.

## Scale
~1,900 files total codebase.

## See Also
- [[agent-harness]] — harness fundamentals
- [[subagents]] — subagent patterns in depth
- [[context-management]] — context pressure strategies
- [[permission-system]] — permission gating details
- [[harness-patterns]] — patterns inspired by this architecture
