# OpenClaw Knowledge Base — Schema

## Purpose
LLM-maintained wiki on OpenClaw: the open-source personal AI agent framework that runs autonomously on your own hardware, controllable via 24+ messaging platforms, and extensible via skills and plugins.

## Owner
mr.hasan — AI/ML engineer running local inference on Apple Silicon (MLX, LFM2-24B). Uses Claude Code daily; interested in personal autonomy tooling, agent architectures, and self-hosted AI.

## Folder Structure

```
openclaw/
├── CLAUDE.md          ← this file — operating schema
├── raw/               ← immutable source material (READ ONLY)
├── wiki/
│   ├── index.md       ← navigable catalog by category
│   ├── log.md         ← append-only history
│   └── concepts/      ← one .md per concept
```

## LLM Operating Instructions

### Compile task (given raw files)
1. Identify distinct concepts worth a dedicated article
2. Write one article per concept in wiki/concepts/ — encyclopedia style, precise, practical
3. Use [[wikilink]] syntax for cross-references between concepts
4. Every article must have a `## See Also` section with wikilinks
5. Update wiki/index.md as a navigable catalog grouped by category
6. Append a dated entry to wiki/log.md

### Article structure
```
# Concept Name

## Definition
[precise 2-4 sentence definition]

## Mechanism
[how it works, with code/diagrams if useful]

## Variants / Taxonomy
[if applicable]

## Tradeoffs
[table or bullets: what it gains, what it costs, when it fails]

## See Also
- [[related-concept]]
```

### Writing style
- Owner is an AI/ML engineer — assume familiarity with LLMs, tool use, local inference
- Lead with definitions, then mechanics, then tradeoffs
- Use tables for comparisons
- Include code snippets where they clarify rather than decorate
- Numbers and specific versions preferred over vague claims
- No filler — every sentence adds information

## Naming Conventions
- Concept files: `kebab-case.md`
- Wikilinks: `[[filename-without-extension]]`
- Dates: `YYYY-MM-DD`
