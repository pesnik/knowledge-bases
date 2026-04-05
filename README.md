# knowledge-bases

Personal Karpathy-style LLM-maintained knowledge bases. Each KB is a topic-specific wiki where:
- **I** dump raw source material (`raw/`)
- **A local LLM** compiles and maintains the wiki (`wiki/`)
- **Obsidian** (dockerized at `http://obsidian.localhost`) is the reading interface

Inspired by [Andrej Karpathy's LLM knowledge base workflow](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

---

## Structure

```
knowledge-bases/
├── <topic>/
│   ├── CLAUDE.md          ← LLM operating schema for this KB
│   ├── Makefile           ← make compile / fix / validate / push
│   ├── raw/               ← immutable source clips (I own, LLM reads only)
│   │   └── *.md
│   ├── wiki/              ← LLM-compiled and LLM-maintained
│   │   ├── index.md       ← navigable catalog
│   │   ├── log.md         ← append-only ingest history
│   │   └── concepts/      ← one article per concept, with [[wikilinks]]
│   └── pipeline/          ← Python scripts to run the LLM compilation
│       ├── config.py      ← model path, token budgets, context limits
│       ├── compile.py     ← 4-stage pipeline: plan → compile → index → log
│       ├── fix.py         ← post-process: broken links, orphan pages
│       └── validate.py    ← lint: broken links, orphans, missing sections
```

---

## Knowledge Bases

| KB | Topic | Status |
|----|-------|--------|
| [agent-harness](./agent-harness/) | Agent harness architecture — Claude Code internals, LangChain DeepAgents, patterns | Compiled (manual) |
| [speculative-decoding](./speculative-decoding/) | Speculative decoding for LLM inference — EAGLE, Medusa, ReDrafter, MLX | Compiled (LFM2-24B local) |

---

## Workflow

### 1. Clip raw sources
Use Obsidian Web Clipper or write notes manually into `<topic>/raw/`. Each file is a source — article, paper, repo study.

### 2. Compile
```bash
cd <topic>
source ~/Tools/mlx/.venv/bin/activate
make compile       # plan → compile → index → log
make fix           # repair broken wikilinks, inject See Also
make validate      # lint for errors and warnings
```

### 3. Read
Open `http://obsidian.localhost` → Open vault → `knowledge-bases/<topic>/wiki`

---

## Adding a New KB

```bash
mkdir -p knowledge-bases/<topic>/{raw,wiki/concepts,pipeline}
# Copy pipeline/ from an existing KB and update config.py:
#   VAULT_ROOT is auto-detected from pipeline/__file__
#   Update MODEL_PATH if using a different model
# Write a CLAUDE.md schema
# Drop raw/ files
# Run: make compile
```

---

## LLM Stack

| Property | Value |
|----------|-------|
| Model | LiquidAI LFM2-24B-A2B (MoE, 4-bit) |
| Runtime | `mlx_lm` — direct Python API, no server |
| Hardware | Apple M3 Pro, 18GB unified memory |
| Memory budget | 12.7GB weights + ~3.5GB KV (kv_bits=8) |

See [`~/Pesnik/skills/infrastructure/mlx-lm-local/SKILL.md`](../skills/infrastructure/mlx-lm-local/SKILL.md) for all machine-specific fixes.
