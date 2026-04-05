# Context Management for Deep Agents
Source: blog.langchain.com/context-management-for-deepagents
Clipped: 2026-04-05

## The Problem
Context windows have finite capacity. Long-running agents accumulate:
- Large tool outputs (search results, file reads)
- Redundant conversation history
- Repeated file operation entries

Without management, agents hit context limits and fail or hallucinate.

## Three Core Compression Techniques

### 1. Offloading Large Tool Results
- Trigger: tool response > 20,000 tokens
- Action: write response to filesystem, substitute with file path + first 10 lines preview
- Agent retrieves full content when needed via file read

### 2. Offloading Large Tool Inputs
- Trigger: context reaches 85% capacity
- Action: truncate older tool calls, replace with pointer to file on disk
- Agent re-reads file rather than holding it in context

### 3. Summarization (Dual Component)
- **In-context summary**: LLM generates structured summary of conversation — session intent, artifacts created, next steps — replaces full history
- **Filesystem preservation**: complete original conversation written to filesystem as canonical record

## Implementation Detail
Uses model token profiles to access token threshold for a given model. Compression triggers at configurable fractions of context window (default: 85%).

## Testing Harness Compression
- Use targeted evaluations that isolate specific mechanisms
- Stress-test individual features aggressively to generate enough compression events
- Verify agents can recover summarized information through filesystem search
- Monitor for **goal drift** after compression events (major failure mode)
- Establish baseline performance before aggressive compression testing

## Deep Agents Architecture (LangChain)
Middleware stack applied to a standard LangGraph agent:
1. **To-do list middleware** — explicit planning (`write_todos` tool)
2. **Filesystem middleware** — externalizing artifacts (ls, read_file, write_file, edit_file, search, pattern match)
3. **Subagent middleware** — delegating work with isolated context

This gives planning + context offloading + subagents without building from scratch.
