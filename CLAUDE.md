# knowledge-bases — CLAUDE.md

Instructions for future Claude working in this repo.

---

## What this repo is

A collection of Karpathy-style LLM-maintained knowledge bases. Each subdirectory is one KB on a specific topic. The human clips sources into `raw/`; the LLM compiles them into `wiki/` via the pipeline in `pipeline/`.

**You are both the reader and the compiler.** When asked to work on a KB:
- Read raw/ to understand source material
- Read wiki/ to see what's already compiled
- Read the KB's own CLAUDE.md for its schema and naming rules

---

## Repo layout

```
knowledge-bases/
├── CLAUDE.md               ← this file
├── README.md               ← human-facing overview
├── <topic>/
│   ├── CLAUDE.md           ← per-KB schema (READ THIS before compiling)
│   ├── Makefile
│   ├── raw/                ← source clips — never modify
│   ├── wiki/
│   │   ├── index.md
│   │   ├── log.md
│   │   └── concepts/*.md
│   └── pipeline/
│       ├── config.py       ← model path + memory budget constants
│       ├── compile.py      ← plan → compile → index → log
│       ├── fix.py          ← post-process LLM output
│       └── validate.py     ← lint wiki quality
```

---

## Running the pipeline

```bash
source ~/Tools/mlx/.venv/bin/activate
cd <topic>
make compile    # full pipeline
make fix        # repair broken wikilinks + inject See Also
make validate   # 0 errors is the goal; warnings are acceptable
make all        # compile + fix + validate in one shot
```

### When the pipeline fails

**OOM (Metal Insufficient Memory):** Reduce `MAX_CHARS_*` and `*_MAX_TOKENS` in `pipeline/config.py`. On M3 Pro 18GB with LFM2-24B, safe limits are:
- Plan: 400 chars/file, 400 output tokens
- Compile: 500 chars/file, 600 output tokens
- Index: 80 chars/concept, 350 output tokens
- Always use `kv_bits=8, kv_group_size=64` in `mlx_lm.generate()`

**`rope_theta` error on model load:** Run the config patch once:
```python
import json; from pathlib import Path
p = Path.home()/"Models/lmstudio-community/config.json"
c = json.loads(p.read_text())
c["rope_theta"] = c.get("rope_parameters",{}).get("rope_theta", 1000000.0)
p.write_text(json.dumps(c, indent=2))
```

**`temp` kwarg error (mlx_lm ≥ 0.31):** Use `sampler=make_sampler(temp=0.2)` from `mlx_lm.sample_utils`.

Full reference: `~/Pesnik/skills/infrastructure/mlx-lm-local/SKILL.md`

---

## Adding a new KB

1. `mkdir -p <topic>/{raw,wiki/concepts,pipeline}`
2. Copy `pipeline/` from `speculative-decoding/` (most up-to-date)
3. Edit `pipeline/config.py` — `VAULT_ROOT` is auto-detected, just confirm `MODEL_PATH`
4. Write `<topic>/CLAUDE.md` — describe the topic, owner context, writing style
5. Drop source files into `raw/`
6. Run `make all`

---

## Obsidian access

KBs are mounted into the dockerized Obsidian at:
```
http://obsidian.localhost  →  /config/knowledge-bases/<topic>/wiki
```

Mount is defined in `~/Tools/obsidian/docker-compose.yml`:
```yaml
- /Users/mr.hasan/Pesnik/knowledge-bases:/config/knowledge-bases
```

---

## Validate exit codes

- `0` = warnings only (acceptable)
- `1` = errors present (broken links, missing sections — fix before pushing)

Run `make fix` before `make validate` — it resolves most LLM output issues automatically.

---

## Git

- Default branch: `master`
- Remote: `git@github.com:pesnik/knowledge-bases.git`
- Push after each compile: `make push` (inside a KB dir) or `git push` from repo root
