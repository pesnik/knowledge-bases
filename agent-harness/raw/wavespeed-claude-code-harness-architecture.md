# Claude Code Agent Harness Architecture
Source: wavespeed.ai/blog/posts/claude-code-agent-harness-architecture + dev.to analysis
Clipped: 2026-04-05
Note: Based on leaked source analysis. Patterns are general engineering approaches.

## Core Orchestration Loop
`QueryEngine.ts` (~46,000 lines) manages:
- All LLM API calls
- Prompt construction and streaming
- Token counting and cost tracking
- Prompt caching
- Retry logic

**5 Context Pressure Strategies (in order of escalation):**
1. Time-based clearing of old tool results
2. Conversation summarization
3. Session memory extraction
4. Full history summarization
5. Oldest-message truncation

Behavioral coordination defined in **natural language in system prompt** — not hardcoded branching. This enables iteration without redeployment.

## Permission & Sandboxing System
~40 discrete tool capabilities, each independently permission-gated.

**Three-stage approval sequence:**
1. Trust establishment at project initialization
2. Permission verification before execution
3. Explicit user confirmation for high-risk operations (file writes, bash)

**Auto mode innovation:** A separate LLM classifier call predicts user approval before execution. Read-only operations run concurrently; mutating operations run serially to prevent conflicts.

## Three-Layer Memory Architecture
| Layer | Contents | Load Behavior |
|-------|----------|---------------|
| Layer 1 | MEMORY.md — brief pointers (~150 chars each) | Always loaded |
| Layer 2 | Topic files — detailed notes | On-demand |
| Layer 3 | Raw transcripts | Search-only |

Sessions persist as JSONL. Resumable via `--continue` or `--resume`. 
**Key design**: agents treat memory as hints, verify against live state before acting.

## Subagent Execution Models
| Model | Mechanism | Use Case |
|-------|-----------|----------|
| Fork | Byte-identical parent context copy; leverages prompt cache | Parallel work with cache reuse |
| Teammate | Separate tmux/iTerm pane; file-based mailbox communication | Loose coordination across workstreams |
| Worktree | Isolated git worktree with separate branch | Exploratory or risky work |

Subagents return only their output to the orchestrator — risky work cannot contaminate primary agent state.

## Hook System (26 events)
SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, PostToolUseFailure, PermissionRequest, SubagentStart, SubagentStop, Stop, StopFailure, Notification, TaskCreated, TaskCompleted, TeammateIdle, InstructionsLoaded, ConfigChange, CwdChanged, FileChanged, WorktreeCreate, WorktreeRemove, PreCompact, PostCompact, Elicitation, ElicitationResult, SessionEnd (+ 1 more)

## Kairos Feature (feature-flagged, not public)
Background daemon mode enabling work during user idle periods. `autoDream` subprocess: merges observations, resolves logical contradictions, consolidates notes — runs separately to prevent main context corruption.

## Scale
- `Tool.ts`: ~29,000 lines
- Total codebase: ~1,900 files
