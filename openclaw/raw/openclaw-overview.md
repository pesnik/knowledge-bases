# OpenClaw — Overview & Architecture
Source: openclaw.ai, docs.openclaw.ai, GitHub
Clipped: 2026-04-05

## What Is OpenClaw

OpenClaw is a free, open-source personal AI agent framework that runs on your own hardware (Mac, Windows, Linux, Raspberry Pi). Rather than a chatbot you prompt, it is a persistent background service that monitors your tools and takes autonomous action when conditions are met — scheduling meetings, triaging email, updating CRMs, running code — all controllable via 24+ messaging platforms (WhatsApp, Telegram, Discord, Slack, Signal, iMessage, Teams, Matrix, etc.).

Created by Peter Steinberger (Austrian developer). Launched November 2025 as "Clawdbot". Reached 60,000+ GitHub stars in 72 hours. MIT license.

## The 5-Layer Architecture

### 1. Input Sources
Monitors external tools: Gmail, Slack, Salesforce, Google Calendar, GitHub, webhooks. Each integration is a named channel polled or push-subscribed by the Gateway.

### 2. Integration Gateway
The single entry point. WebSocket-based at `ws://127.0.0.1:18789`. Normalizes heterogeneous signals (chat message, calendar event, email arrival) into a common event format. Acts as a router, not a broker — it forwards normalized events, does not buffer or queue them.

### 3. Agent Core
Three sub-components:
- **Orchestrator** — receives normalized events, decides which agent handles them based on routing rules and intent classification
- **Specialized Agents** — domain-specific agents (email triage, calendar management, code execution); each has its own system prompt (soul), tools, and memory slice
- **Shared Memory Layer** — key-value + vector store accessible to all agents; enables cross-agent coordination and long-term personalization

### 4. Execution Engine
Translates agent decisions into concrete actions: bash execution, browser automation, API calls, file operations. Optional human-approval checkpoints before critical operations. Cascading allow/deny policies control which models can use which tools.

### 5. External Systems
Target platforms receiving the agent's output: CRMs, communication channels, storage systems.

## Technical Stack

- Runtime: Node.js 24+ (22.14+ supported)
- LLM backends: Claude (Anthropic), GPT-4 (OpenAI), Gemini (Google), or local models via Ollama
- Memory: local key-value + optional vector store (Chroma, Qdrant)
- Storage: SQLite for metadata, flat files for raw memory blobs
- Transport: WebSocket (local gateway), HTTPS (external integrations)
- Extension points: Skills (SKILL.md), Plugins (TypeScript)

## The Event Loop

```
Event Detection (Gateway monitors inputs)
  → Signal Normalization (common event format)
    → Orchestration (route to agent)
      → Agent Processing (reason + tool calls)
        → Execution Engine (run actions)
          → Output Delivery (respond to channel, optional approval gate)
```

Processing latency: Gateway ops instant; tool execution depends on external latency; LLM inference ~5–30s (Claude), faster with local models on sufficient hardware.

## Skills System

Skills are the primary extension mechanism. Each skill is a folder `~/.openclaw/skills/<name>/` containing a `SKILL.md` file. OpenClaw auto-injects the SKILL.md into the agent's system prompt, giving the agent knowledge of new tools without code changes. Community hub: ClawHub registry — 5,400+ skills as of April 2026.

## Security Model

- DM pairing with approval codes for unknown senders
- Cascading allow/deny policies per model/tool combination
- Optional file/system access sandboxing
- Human-approval gates for critical operations
- Data stays on device by default (no telemetry)
