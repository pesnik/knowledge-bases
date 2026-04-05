# Speculative Decoding Knowledge Base — Schema

## Purpose
LLM-maintained wiki on speculative decoding: the family of techniques that accelerate autoregressive LLM inference by predicting multiple tokens per forward pass.

## Owner
mr.hasan — AI/ML engineer running local inference on Apple Silicon (MLX, LFM2-24B).

## Folder Structure

```
speculative-decoding/
├── CLAUDE.md          ← this file — operating schema
├── raw/               ← immutable source material (READ ONLY)
├── wiki/
│   ├── index.md       ← navigable catalog by category
│   ├── log.md         ← append-only history
│   └── concepts/      ← one .md per concept
└── pipeline/
    ├── compile.py     ← raw/ → wiki/ via local LLM
    └── validate.py    ← lint wiki for broken links, orphans, gaps
```

## LLM Operating Instructions

### Compile task (given raw files)
1. Identify distinct concepts worth a dedicated article
2. Write one article per concept in wiki/concepts/ — encyclopedia style, precise, technical
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
[how it works, with math/pseudocode if useful]

## Variants / Taxonomy
[if applicable]

## Tradeoffs
[table or bullets: what it gains, what it costs, when it fails]

## See Also
- [[related-concept]]
```

### Writing style
- Owner is an ML engineer — assume deep familiarity with transformers, attention, KV cache
- Lead with definitions, then mechanics, then tradeoffs
- Use tables for comparisons
- Numbers and citations preferred over vague claims
- No filler — every sentence adds information

## Naming Conventions
- Concept files: `kebab-case.md`
- Wikilinks: `[[filename-without-extension]]`
- Dates: `YYYY-MM-DD`
