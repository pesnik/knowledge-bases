# Permission System

## Definition
The permission system is the harness component that governs which tools an agent can invoke, when, and under what conditions. It sits between the agent's intent (tool call request) and actual execution.

**Design separation**: the model decides *what to attempt*; the permission system decides *what is permitted*.

## Why It Exists
Without a permission system:
- Agents can delete files, execute arbitrary code, or exfiltrate data without restriction
- Users lose trust and control
- Automation pipelines become safety liabilities

## Permission Gating Approaches

### Per-Tool Permission Classes
Each tool carries an explicit permission class:
- **Read-only**: Glob, Grep, Read, WebFetch — low risk, typically auto-approved
- **Mutating**: Write, Edit, Bash — higher risk, require explicit confirmation or whitelist
- **Dangerous**: `rm`, force operations, network writes — always confirm unless explicitly pre-approved

### Allow-listing
Pre-approve specific operations at session start:
- "allow bash commands matching `npm test`"
- "allow file writes to `./src/**`"
- "never allow git push"

Defined in CLAUDE.md or settings.json per project.

### Three-Stage Approval (Claude Code)
1. **Trust establishment** at project load: reads project config, determines baseline trust level
2. **Permission check** before each tool call: consults allow-list + tool risk class
3. **User confirmation** for high-risk or unlisted operations: interrupt, show proposed action, await Y/N

### Auto Mode with Classifier
Most sophisticated pattern: before interrupting the user, run a secondary LLM classifier that predicts approval probability given:
- The current task context
- The proposed tool call
- Historical approval patterns

If confidence > threshold: auto-approve and log. If uncertain: interrupt.
Benefit: dramatically reduces interruptions in routine automation while maintaining safety for novel actions.

## Read-Only Concurrency vs. Mutating Serialization
Read-only operations (file reads, searches, web fetches) can execute concurrently — no state conflicts.
Mutating operations (file writes, bash with side effects) run serially — prevents interleaved state corruption.

This is a performance optimization that falls naturally out of permission classification.

## Hook-Based Enforcement
The permission system emits hook events at each decision point:
- `PreToolUse`: can block execution
- `PostToolUse`: can log or trigger side effects
- `PermissionRequest`: external system can approve/deny

Hooks allow external policy engines (security scanners, audit loggers, approval UIs) to integrate without modifying the harness.

## Tradeoffs

| Approach | Safety | Friction | Automation-Friendliness |
|----------|--------|----------|------------------------|
| Confirm everything | High | High | Low |
| Whitelist + auto | Medium-High | Low | High |
| Allow-list per project | Configurable | Configurable | Configurable |
| Classifier-based auto | High | Very Low | Very High |

## See Also
- [[agent-harness]] — where permission system fits
- [[claude-code-harness]] — reference implementation (3-stage + classifier)
- [[harness-patterns]] — permission prediction pattern
- [[subagents]] — subagents inherit scoped permissions from parent
