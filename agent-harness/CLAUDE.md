# Agent Harness Knowledge Base — Schema

## Purpose
This is a personal LLM-maintained wiki on the topic of **agent harnesses** — the software infrastructure surrounding LLMs that makes them useful for complex, long-horizon tasks.

## Owner
mr.hasan — AI/ML engineer building agentic systems.

## Folder Structure

```
agent-harness/
├── CLAUDE.md          ← this file — operating schema for the LLM
├── raw/               ← immutable source material (you READ, never modify)
│   └── *.md           ← clipped articles, paper notes, repo studies
├── wiki/              ← LLM-maintained compiled knowledge (you OWN this)
│   ├── index.md       ← content catalog organized by category
│   ├── log.md         ← append-only ingest/query history
│   └── concepts/      ← synthesized concept articles (~1-3 pages each)
│   └── slides/        ← Marp format presentations generated on demand
```

## LLM Operating Rules

### On Ingest (new item added to raw/)
1. Read the new raw file
2. Update or create the relevant concept article(s) in wiki/concepts/
3. Add backlinks between related concepts using `[[concept-name]]` syntax
4. Update wiki/index.md to reflect new content
5. Append a dated entry to wiki/log.md: what was ingested, what changed

### On Compile (initial or full rebuild)
1. Read all files in raw/
2. Synthesize concept articles — one file per distinct concept
3. Write encyclopedia-style: definitions, mechanisms, comparisons, tradeoffs
4. Add `## See Also` sections with [[wikilinks]] to related concepts
5. Build index.md as a navigable catalog

### On Query (user asks a question)
1. Answer from wiki/concepts/ first
2. If the answer is novel/synthesized, file it back as a new concept article or append to an existing one
3. Log the query + key finding in wiki/log.md

### On Lint (health check)
1. Scan for orphan pages (no inbound links)
2. Flag contradictions between articles
3. Identify concept gaps (mentioned but no article exists)
4. Suggest next raw/ sources to ingest

## Naming Conventions
- Concept files: `kebab-case.md` (e.g., `context-management.md`)
- Raw files: descriptive, source-prefixed (e.g., `langchain-deepagents-blog.md`)
- Wikilinks: `[[concept-name]]` matching the filename without `.md`
- Dates in log: `YYYY-MM-DD`

## Writing Style
- Precise and technical — owner is an engineer, not a beginner
- Lead with definitions, then mechanisms, then tradeoffs
- Use tables for comparisons
- Include concrete examples (code snippets if applicable)
- No filler — every sentence must add information
