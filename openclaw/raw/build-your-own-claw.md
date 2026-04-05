# Building Your Own Claw — Personal Agent from Scratch
Source: docs.openclaw.ai, chatbotkit.com, lumadock.com tutorials
Clipped: 2026-04-05

## Philosophy

A "claw" in this context is a personal AI agent: a persistent process that monitors inputs, reasons about them, and takes action. Building your own gives full control over the three-file soul/memory/tools pattern, without OpenClaw's 60k-line surface area.

This guide covers two paths:
1. **Extend OpenClaw** — add a custom skill or plugin
2. **Build from scratch** — minimal autonomous agent (~200 lines)

---

## Path 1: OpenClaw Skill (5 Minutes)

The fastest way to add capability without forking:

### Step 1: Create the skill folder
```
~/.openclaw/skills/my-skill/
└── SKILL.md
```

### Step 2: Write SKILL.md
```markdown
# My Skill

## Purpose
[What this skill does in 1-2 sentences]

## Tools

### tool_name
Description: [what the tool does]
Parameters:
- param1 (string): description
- param2 (number): description

## Examples
User: "do X"
Assistant: [calls tool_name with param1="..."]
```

OpenClaw auto-injects this into the system prompt. No code required for simple integrations.

### Step 3: For tools that need code, add index.js
```js
export default {
  name: "my-skill",
  tools: {
    tool_name: async ({ param1, param2 }) => {
      // your logic here
      return { result: "..." };
    }
  }
};
```

Register in `~/.openclaw/config.json`:
```json
{ "skills": ["~/.openclaw/skills/my-skill"] }
```

---

## Path 2: Minimal Agent from Scratch

The three-component pattern (Soul / Memory / Tools) is the minimum viable agent:

### The Soul (system prompt)
```js
const SOUL = `You are a personal assistant named Aria.
You have access to the following tools: [tool list injected here].
When uncertain, ask for clarification rather than guessing.
Format tool calls as JSON: {"tool": "name", "args": {...}}`;
```

### The Memory
```js
import { readFileSync, writeFileSync } from 'fs';

const MEMORY_FILE = './memory.json';

function loadMemory() {
  try { return JSON.parse(readFileSync(MEMORY_FILE)); }
  catch { return { facts: [], history: [] }; }
}

function saveMemory(memory) {
  writeFileSync(MEMORY_FILE, JSON.stringify(memory, null, 2));
}
```

### The Tools
```js
const TOOLS = {
  search_web: async ({ query }) => {
    // use any search API
    return await fetch(`https://api.search.example.com?q=${query}`).then(r => r.json());
  },
  run_bash: async ({ command }) => {
    const { execSync } = require('child_process');
    return execSync(command, { encoding: 'utf8' });
  },
  send_message: async ({ channel, text }) => {
    // push to Telegram, Slack, etc.
  }
};
```

### The Loop
```js
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();

async function runAgent(userMessage) {
  const memory = loadMemory();
  memory.history.push({ role: 'user', content: userMessage });

  const response = await client.messages.create({
    model: 'claude-opus-4-6',
    max_tokens: 4096,
    system: SOUL + '\n\nKnown facts:\n' + memory.facts.join('\n'),
    messages: memory.history,
    tools: Object.keys(TOOLS).map(name => ({
      name,
      description: `Execute ${name}`,
      input_schema: { type: 'object', properties: {} }  // define per tool
    }))
  });

  // Handle tool calls
  for (const block of response.content) {
    if (block.type === 'tool_use') {
      const result = await TOOLS[block.name](block.input);
      memory.history.push({ role: 'assistant', content: response.content });
      memory.history.push({ role: 'user', content: [{
        type: 'tool_result', tool_use_id: block.id, content: JSON.stringify(result)
      }]});
      // Re-run to incorporate tool result
      return runAgent('');  // recursive with tool result injected
    }
  }

  const assistantMessage = response.content[0].text;
  memory.history.push({ role: 'assistant', content: assistantMessage });
  saveMemory(memory);
  return assistantMessage;
}
```

### Make It Background

Convert to a persistent service:
```js
// Watch a file, Telegram webhook, or cron
import { watch } from 'fs';

watch('./inbox/', async (event, filename) => {
  const message = readFileSync(`./inbox/${filename}`, 'utf8');
  const response = await runAgent(message);
  // deliver response
});
```

---

## Architecture Decisions

| Decision | Option A | Option B |
|----------|----------|----------|
| Memory backend | JSON files | SQLite + vector store |
| Transport | File watch | WebSocket / webhook |
| Model | Claude API | Local Ollama |
| Tool safety | Trust all | Require confirmation per class |
| Deployment | Local process | Docker container |

For a personal agent: JSON files + local process + Claude API is the fastest path to productivity.

For a shared/production agent: SQLite + WebSocket + approval gates + Docker.

---

## Common Pitfalls

1. **Infinite tool loops** — Agent calls tool → sees result → calls same tool. Fix: track tool call history, add loop detection.
2. **Context blowout** — History grows unbounded. Fix: summarize old turns into `memory.facts` periodically.
3. **Tool call hallucination** — Small models invent tool names. Fix: use 13B+ models; validate tool name before execution.
4. **Credential leakage** — API keys in prompts. Fix: never inject secrets into LLM context; pass only opaque handles.
5. **Runaway background actions** — Agent sends 100 emails in a loop. Fix: rate limits + approval gates for write operations.

---

## Minimal Production Checklist

- [ ] Soul: persona + tool list + uncertainty handling instructions
- [ ] Memory: persisted history + summarized facts + rotation policy
- [ ] Tools: well-typed schemas + input validation + rate limits
- [ ] Safety: approval gates for write ops + loop detection + max-steps limit
- [ ] Observability: log every tool call + model response to append-only log
- [ ] Recovery: agent state survives restart (no in-memory-only state)
